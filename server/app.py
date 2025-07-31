"""
FastAPI 翻译服务主应用
提供翻译API接口，支持多种翻译源和缓存机制
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import asyncio
import logging
from datetime import datetime

from translator import GoogleTranslator
from utils.cache import CacheManager
from config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="智能翻译API",
    description="Chrome插件翻译服务后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 初始化翻译器和缓存管理器
translator = GoogleTranslator()
cache_manager = CacheManager()

# 请求模型
class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="要翻译的文本")
    source_lang: str = Field(default="auto", description="源语言代码")
    target_lang: str = Field(default="zh-cn", description="目标语言代码")

class TranslateResponse(BaseModel):
    translation: str = Field(..., description="翻译结果")
    source_lang: str = Field(..., description="检测到的源语言")
    target_lang: str = Field(..., description="目标语言")
    original_text: str = Field(..., description="原始文本")
    cached: bool = Field(default=False, description="是否来自缓存")

class HealthResponse(BaseModel):
    status: str = Field(..., description="服务状态")
    timestamp: str = Field(..., description="检查时间")
    version: str = Field(..., description="服务版本")

# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "内部服务器错误", "status_code": 500}
    )

# API路由
@app.get("/", response_model=dict)
async def root():
    """根路径 - API信息"""
    return {
        "message": "智能翻译API服务",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    翻译文本接口
    
    Args:
        request: 翻译请求，包含文本和语言参数
        
    Returns:
        TranslateResponse: 翻译结果
        
    Raises:
        HTTPException: 翻译失败时抛出异常
    """
    try:
        # 参数验证
        if request.source_lang == request.target_lang and request.source_lang != "auto":
            raise HTTPException(
                status_code=400,
                detail="源语言和目标语言不能相同"
            )
        
        # 检查文本长度
        if len(request.text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="翻译文本不能为空"
            )
        
        if len(request.text) > settings.max_text_length:
            raise HTTPException(
                status_code=400,
                detail=f"文本长度不能超过{settings.max_text_length}个字符"
            )
        
        logger.info(f"翻译请求: {request.source_lang} -> {request.target_lang}, 文本长度: {len(request.text)}")
        
        # 生成缓存键
        cache_key = cache_manager.generate_cache_key(
            request.text, 
            request.source_lang, 
            request.target_lang
        )
        
        # 尝试从缓存获取结果
        cached_result = await cache_manager.get_cached_translation(cache_key)
        if cached_result:
            logger.info(f"缓存命中: {cache_key}")
            return TranslateResponse(
                translation=cached_result["translation"],
                source_lang=cached_result["source_lang"],
                target_lang=cached_result["target_lang"],
                original_text=request.text,
                cached=True
            )
        
        # 执行翻译
        result = await translator.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        
        # 缓存翻译结果
        await cache_manager.cache_translation(cache_key, result)
        
        logger.info(f"翻译完成: {request.source_lang} -> {request.target_lang}")
        
        return TranslateResponse(
            translation=result["translation"],
            source_lang=result["source_lang"],
            target_lang=result["target_lang"],
            original_text=request.text,
            cached=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"翻译失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"翻译服务暂时不可用: {str(e)}"
        )

@app.get("/languages")
async def get_supported_languages():
    """获取支持的语言列表"""
    return {
        "languages": {
            "auto": "自动检测",
            "en": "英语",
            "zh-cn": "中文(简体)",
            "zh-tw": "中文(繁体)",
            "ja": "日语",
            "ko": "韩语",
            "fr": "法语",
            "de": "德语",
            "es": "西班牙语",
            "ru": "俄语",
            "it": "意大利语",
            "pt": "葡萄牙语",
            "ar": "阿拉伯语",
            "hi": "印地语",
            "th": "泰语",
            "vi": "越南语"
        }
    }

@app.get("/stats")
async def get_translation_stats():
    """获取翻译统计信息（需要实现缓存统计）"""
    return {
        "total_translations": 0,
        "cache_hits": 0,
        "cache_miss": 0,
        "cache_hit_rate": "0%"
    }

@app.delete("/cache")
async def clear_cache():
    """清空翻译缓存"""
    try:
        await cache_manager.clear_cache()
        return {"message": "缓存已清空"}
    except Exception as e:
        logger.error(f"清空缓存失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="清空缓存失败"
        )

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("翻译服务启动中...")
    try:
        # 初始化缓存管理器
        await cache_manager.initialize()
        logger.info("缓存管理器初始化完成")
        
        # 测试翻译器
        test_result = await translator.translate("Hello", "en", "zh-cn")
        logger.info(f"翻译器测试成功: {test_result}")
        
        logger.info("翻译服务启动完成")
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("翻译服务关闭中...")
    try:
        await cache_manager.close()
        logger.info("缓存连接已关闭")
    except Exception as e:
        logger.error(f"服务关闭异常: {str(e)}")

# 主函数
def main():
    """启动服务器"""
    logger.info(f"启动翻译服务: {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )

if __name__ == "__main__":
    main()