# Chrome翻译插件项目

🌐 一个功能强大的Chrome浏览器翻译插件，支持快速翻译网页中选中的文本。

## 🚀 功能特性

- **快速翻译**：选中文本后自动弹出翻译结果
- **右键菜单**：支持右键菜单翻译选中文本  
- **弹窗翻译**：插件弹窗支持手动输入文本翻译
- **智能缓存**：相同文本避免重复翻译，提高响应速度
- **优雅界面**：简洁美观的翻译结果展示
- **多语言支持**：支持多种主流语言互译
- **离线缓存**：本地存储翻译历史，提升用户体验

## 🛠️ 技术栈

### 前端（Chrome插件）
- Chrome Extension Manifest V3
- JavaScript (ES6+)
- HTML5 + CSS3
- Chrome Extension APIs

### 后端（Python服务）
- **FastAPI** - 高性能异步Web框架
- **Google翻译API** - 翻译服务
- **Redis** - 缓存服务（可选）
- **Uvicorn** - ASGI服务器
- **aiohttp** - 异步HTTP客户端

## 📁 项目结构

```
translate-extension/
├── extension/                 # Chrome插件前端
│   ├── manifest.json         # 插件配置文件
│   ├── background.js         # 后台脚本
│   ├── content.js           # 内容脚本
│   ├── popup.html           # 插件弹窗界面
│   ├── popup.js             # 弹窗逻辑
│   ├── popup.css            # 弹窗样式
│   ├── styles.css           # 内容脚本样式
│   └── icons/               # 插件图标
│
├── server/                   # Python翻译服务
│   ├── app.py               # FastAPI主应用
│   ├── translator.py        # 翻译逻辑模块
│   ├── config.py            # 配置文件
│   ├── requirements.txt     # Python依赖
│   ├── Dockerfile           # Docker配置
│   ├── .env.example         # 环境变量示例
│   └── utils/              # 工具模块
│       └── cache.py        # 缓存管理
│
└── README.md               # 项目说明
```

## 🚀 快速开始

### 1. 后端服务部署

#### 环境要求
- Python 3.8+
- pip 包管理器

#### 安装依赖
```bash
cd server
pip install -r requirements.txt
```

#### 配置环境（可选）
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
notepad .env  # Windows
# 或
nano .env     # Linux/Mac
```

#### 启动服务
```bash
# 开发模式
python app.py

# 或使用uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

服务将在 `http://localhost:8000` 启动

#### 使用Docker部署（推荐）
```bash
# 构建镜像
docker build -t translator-api ./server

# 运行容器
docker run -d -p 8000:8000 --name translator-service translator-api

# 查看日志
docker logs translator-service
```

### 2. Chrome插件安装

1. **打开Chrome扩展程序管理页面**
   - 在地址栏输入：`chrome://extensions/`
   - 或通过菜单：更多工具 → 扩展程序

2. **启用开发者模式**
   - 在页面右上角开启"开发者模式"开关

3. **加载插件**
   - 点击"加载已解压的扩展程序"
   - 选择项目中的 `extension` 文件夹

4. **确认安装**
   - 插件安装完成后，可以在Chrome工具栏看到插件图标

## 📖 使用指南

### 方式一：选中文本自动翻译
1. 在任意网页中用鼠标选中英文文本
2. 翻译结果会自动显示在选中文本下方的弹窗中
3. 点击关闭按钮或点击页面其他位置关闭翻译弹窗

### 方式二：右键菜单翻译
1. 选中要翻译的文本
2. 右键点击，选择"翻译选中文本"
3. 翻译结果显示在弹窗中

### 方式三：插件弹窗翻译
1. 点击浏览器工具栏的插件图标
2. 在输入框中输入要翻译的文本
3. 选择源语言和目标语言（可选）
4. 点击"翻译"按钮或按Ctrl+Enter
5. 翻译结果显示在下方，支持复制和朗读

## 🔧 API接口文档

### 翻译接口

**请求地址**：`POST /translate`

**请求参数**：
```json
{
  "text": "Hello world",
  "source_lang": "en",
  "target_lang": "zh-cn"
}
```

**响应示例**：
```json
{
  "translation": "你好世界",
  "source_lang": "en", 
  "target_lang": "zh-cn",
  "original_text": "Hello world",
  "cached": false
}
```

### 健康检查

**请求地址**：`GET /health`

**响应示例**：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

### 支持的语言

**请求地址**：`GET /languages`

**响应示例**：
```json
{
  "languages": {
    "auto": "自动检测",
    "en": "英语",
    "zh-cn": "中文(简体)",
    "ja": "日语",
    "ko": "韩语",
    "fr": "法语",
    "de": "德语",
    "es": "西班牙语",
    "ru": "俄语"
  }
}
```

## ⚙️ 配置说明

### 后端配置

主要配置项在 `server/config.py` 文件中：

```python
class Settings:
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # 缓存配置  
    cache_ttl: int = 86400  # 24小时
    max_cache_size: int = 10000
    
    # 翻译配置
    max_text_length: int = 5000
    default_source_lang: str = "en" 
    default_target_lang: str = "zh-cn"
    
    # Redis配置（可选）
    redis_enabled: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
```

### 前端配置

在 `extension/manifest.json` 中配置后端API地址：
```json
{
  "host_permissions": [
    "http://localhost:8000/*"
  ]
}
```

如果后端部署在其他地址，需要相应修改此配置。

## 🔨 开发指南

### 添加新的翻译源

1. **在 `translator.py` 中实现新的翻译类**：
```python
class BaiduTranslator(BaseTranslator):
    async def translate(self, text, source, target):
        # 实现百度翻译API调用
        pass
```

2. **在配置中添加翻译源选择**：
```python
translator_type: str = "baidu"  # google, baidu, youdao
```

### 添加新功能

1. **翻译历史记录**
   - 在后端添加数据库模型
   - 在前端添加历史记录查看界面

2. **批量翻译**
   - 支持一次翻译多段文本
   - 优化API接口性能

3. **自定义快捷键**
   - 添加快捷键配置
   - 实现键盘快捷翻译

### 本地开发环境

1. **克隆项目**
```bash
git clone <repository-url>
cd translate-extension
```

2. **启动后端服务**
```bash
cd server
pip install -r requirements.txt
python app.py
```

3. **加载Chrome插件**
   - 按照上述插件安装步骤加载extension文件夹

4. **测试功能**
   - 在任意网页选中文本测试翻译功能

## ❓ 常见问题

### Q: 插件无法连接到翻译服务
**A**: 请检查以下几点：
- 确保Python后端服务正在运行(`http://localhost:8000`)
- 检查防火墙是否阻止了8000端口
- 确认 `manifest.json` 中的 `host_permissions` 配置正确
- 检查Chrome控制台是否有错误信息

### Q: 翻译速度很慢
**A**: 可能的解决方案：
- 检查网络连接是否稳定
- 启用Redis缓存来提高响应速度
- 考虑更换翻译源（百度、有道等）
- 检查是否有防火墙或代理影响

### Q: 选中文本没有自动翻译
**A**: 请检查：
- 插件是否已正确加载并启用
- 浏览器控制台是否有JavaScript错误
- 确保选中的是纯文本内容（而非图片或其他元素）
- 检查选中文本长度是否在合理范围内

### Q: 翻译结果不准确
**A**: 建议：
- Google翻译对于常见语言对准确性较高
- 可以尝试调整源语言设置（不使用自动检测）
- 对于专业术语，可以考虑集成专业翻译API

## 🔒 安全注意事项

### 生产环境部署
1. **HTTPS配置**：生产环境建议使用HTTPS协议
2. **API认证**：添加API密钥或JWT认证机制  
3. **CORS限制**：限制允许的域名范围
4. **请求限流**：防止API滥用

### 隐私保护
1. **数据处理**：不记录用户敏感翻译内容
2. **缓存策略**：仅缓存通用翻译结果
3. **日志管理**：避免在日志中记录用户输入内容
4. **合规要求**：遵守相关数据保护法规

## 🚀 性能优化

### 缓存策略
- **内存缓存**：快速访问常用翻译
- **Redis缓存**：分布式环境下的持久化缓存
- **LRU算法**：自动清理最少使用的缓存项

### 并发处理
- **异步IO**：使用FastAPI和aiohttp的异步特性
- **连接池**：复用HTTP连接减少开销
- **请求限流**：防止服务过载

### 前端优化
- **防抖处理**：避免频繁的翻译请求
- **本地存储**：离线缓存提升用户体验
- **懒加载**：按需加载翻译功能

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 提交PR前请确保：
- 代码符合项目风格规范
- 添加必要的单元测试
- 更新相关文档
- 测试所有功能正常工作

### 开发流程：
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 联系方式

如有问题或建议，请：
- 提交 [GitHub Issue](../../issues)
- 发送邮件至项目维护者
- 查看项目 [Wiki](../../wiki) 获取更多信息

## 🙏 致谢

感谢以下开源项目：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [Chrome Extensions](https://developer.chrome.com/docs/extensions/) - Chrome扩展开发平台
- [Google Translate](https://translate.google.com/) - 翻译服务

---

**享受翻译的便利！** 🌟