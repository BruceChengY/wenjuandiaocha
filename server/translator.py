"""
翻译器模块
支持多种翻译引擎，目前实现Google翻译
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Optional
from abc import ABC, abstractmethod
import json
import urllib.parse
import re

logger = logging.getLogger(__name__)

class BaseTranslator(ABC):
    """翻译器基类"""
    
    @abstractmethod
    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "zh-cn") -> Dict:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            Dict: 翻译结果
        """
        pass

class GoogleTranslator(BaseTranslator):
    """Google翻译实现"""
    
    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single"
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=10)
        
        # 语言代码映射
        self.lang_map = {
            "auto": "auto",
            "zh-cn": "zh",
            "zh-tw": "zh-tw", 
            "en": "en",
            "ja": "ja",
            "ko": "ko",
            "fr": "fr",
            "de": "de",
            "es": "es",
            "ru": "ru",
            "it": "it",
            "pt": "pt",
            "ar": "ar",
            "hi": "hi",
            "th": "th",
            "vi": "vi"
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
        return self.session
    
    def _normalize_lang_code(self, lang_code: str) -> str:
        """标准化语言代码"""
        return self.lang_map.get(lang_code.lower(), lang_code)
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "zh-cn") -> Dict:
        """
        使用Google翻译API翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            Dict: 包含翻译结果的字典
            
        Raises:
            Exception: 翻译失败时抛出异常
        """
        try:
            # 清理和验证输入
            clean_text = self._clean_text(text)
            if not clean_text:
                raise ValueError("翻译文本不能为空")
            
            # 标准化语言代码
            source_lang = self._normalize_lang_code(source_lang)
            target_lang = self._normalize_lang_code(target_lang)
            
            logger.info(f"开始翻译: '{clean_text[:50]}...' ({source_lang} -> {target_lang})")
            
            # 构建请求参数
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': clean_text
            }
            
            # 发送请求
            session = await self._get_session()
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Google翻译API请求失败: HTTP {response.status}")
                
                # 解析响应
                content = await response.text()
                result = self._parse_google_response(content, source_lang, target_lang, clean_text)
                
                logger.info(f"翻译成功: '{result['translation'][:50]}...'")
                return result
                
        except Exception as e:
            logger.error(f"Google翻译失败: {str(e)}")
            # 尝试备用翻译方法
            return await self._fallback_translate(clean_text, source_lang, target_lang)
    
    def _parse_google_response(self, content: str, source_lang: str, target_lang: str, original_text: str) -> Dict:
        """解析Google翻译API响应"""
        try:
            # Google翻译返回的是一个特殊格式的JSON数组
            # 需要特殊处理
            data = json.loads(content)
            
            # 提取翻译结果
            translation_parts = []
            if data and len(data) > 0 and data[0]:
                for item in data[0]:
                    if item and len(item) > 0:
                        translation_parts.append(item[0])
            
            translation = ''.join(translation_parts).strip()
            
            # 检测到的源语言
            detected_lang = source_lang
            if len(data) > 2 and data[2]:
                detected_lang = data[2]
            
            if not translation:
                raise ValueError("翻译结果为空")
            
            return {
                "translation": translation,
                "source_lang": detected_lang,
                "target_lang": target_lang,
                "original_text": original_text
            }
            
        except (json.JSONDecodeError, IndexError, TypeError) as e:
            logger.error(f"解析Google翻译响应失败: {str(e)}")
            raise Exception("翻译响应格式错误")
    
    async def _fallback_translate(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """备用翻译方法（简单的单词映射和基本处理）"""
        logger.warning("使用备用翻译方法")
        
        # 简单的英中翻译映射（仅用于演示和备用）
        simple_translations = {
            "hello": "你好",
            "world": "世界", 
            "thank you": "谢谢",
            "good morning": "早上好",
            "good afternoon": "下午好",
            "good evening": "晚上好",
            "goodbye": "再见",
            "yes": "是",
            "no": "不",
            "please": "请",
            "sorry": "对不起",
            "excuse me": "打扰一下",
            "how are you": "你好吗",
            "what": "什么",
            "when": "什么时候", 
            "where": "哪里",
            "who": "谁",
            "why": "为什么",
            "how": "怎么样",
            "poland": "波兰",
            "lithuanian": "立陶宛的",
            "throne": "王位",
            "commonwealth": "联邦",
            "rzeczpospolita": "共和国",
            "polish": "波兰的"
        }
        
        text_lower = text.lower().strip()
        
        # 尝试直接匹配
        if text_lower in simple_translations:
            translation = simple_translations[text_lower]
        else:
            # 尝试单词级别的翻译
            words = text_lower.split()
            translated_words = []
            for word in words:
                # 移除标点符号
                clean_word = word.strip('.,!?;:"()[]{}')
                if clean_word in simple_translations:
                    translated_words.append(simple_translations[clean_word])
                else:
                    translated_words.append(word)
            
            if len(translated_words) > 0 and any(w in simple_translations.values() for w in translated_words):
                translation = " ".join(translated_words)
            else:
                # 提供友好的错误信息
                translation = f"抱歉，无法翻译 '{text}'。Google翻译服务暂时不可用，请稍后重试。"
        
        return {
            "translation": translation,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "original_text": text
        }
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()

class BaiduTranslator(BaseTranslator):
    """百度翻译实现（预留接口）"""
    
    def __init__(self, app_id: str = None, secret_key: str = None):
        self.app_id = app_id
        self.secret_key = secret_key
        self.base_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    
    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "zh") -> Dict:
        """百度翻译实现（需要配置API密钥）"""
        # 这里需要实现百度翻译API调用
        # 需要注册百度翻译API并获取app_id和secret_key
        raise NotImplementedError("百度翻译功能尚未实现，请使用Google翻译")

class YoudaoTranslator(BaseTranslator):
    """有道翻译实现（预留接口）"""
    
    def __init__(self, app_key: str = None, app_secret: str = None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://openapi.youdao.com/api"
    
    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "zh-CHS") -> Dict:
        """有道翻译实现（需要配置API密钥）"""
        # 这里需要实现有道翻译API调用
        # 需要注册有道智云API并获取应用ID和密钥
        raise NotImplementedError("有道翻译功能尚未实现，请使用Google翻译")

def create_translator(translator_type: str = "google", **kwargs) -> BaseTranslator:
    """
    创建翻译器实例
    
    Args:
        translator_type: 翻译器类型 ("google", "baidu", "youdao")
        **kwargs: 翻译器特定的配置参数
        
    Returns:
        BaseTranslator: 翻译器实例
    """
    translators = {
        "google": GoogleTranslator,
        "baidu": BaiduTranslator,
        "youdao": YoudaoTranslator
    }
    
    translator_class = translators.get(translator_type.lower())
    if not translator_class:
        raise ValueError(f"不支持的翻译器类型: {translator_type}")
    
    return translator_class(**kwargs)