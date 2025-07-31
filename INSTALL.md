# 安装部署指南

本文档提供Chrome翻译插件的详细安装和部署步骤。

## 📋 系统要求

### 最低要求
- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 或更高版本
- **Chrome浏览器**: 版本 88 或更高版本
- **内存**: 至少 512MB 可用内存
- **存储**: 至少 100MB 可用磁盘空间

### 推荐配置
- **Python**: 3.10+ 
- **内存**: 1GB+ 可用内存
- **网络**: 稳定的互联网连接

## 🚀 快速安装

### 方法一：使用启动脚本（推荐）

#### Windows用户
```cmd
# 1. 进入server目录
cd E:\translate-extension\server

# 2. 运行启动脚本
start.bat
```

#### Linux/Mac用户
```bash
# 1. 进入server目录
cd /path/to/translate-extension/server

# 2. 给脚本执行权限
chmod +x start.sh

# 3. 运行启动脚本
./start.sh
```

### 方法二：手动安装

#### 1. 安装Python依赖

```bash
# 进入项目目录
cd translate-extension/server

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 启动后端服务

```bash
# 直接运行
python app.py

# 或使用uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 验证服务运行

打开浏览器访问：`http://localhost:8000/health`

如果看到以下响应，说明服务运行正常：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

## 🔧 Chrome插件安装

### 1. 开启开发者模式

1. 打开Chrome浏览器
2. 在地址栏输入：`chrome://extensions/`
3. 在页面右上角开启"开发者模式"开关

### 2. 加载插件

1. 点击"加载已解压的扩展程序"按钮
2. 选择项目中的 `extension` 文件夹
3. 点击"选择文件夹"

### 3. 确认安装

- 插件安装成功后，Chrome工具栏会出现翻译插件图标
- 可以在扩展程序页面看到"智能翻译助手"

### 4. 测试功能

1. 访问任意包含英文的网页
2. 选中一段英文文本
3. 应该自动弹出翻译结果

## 🐳 Docker部署

### 1. 使用Docker Compose（推荐）

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  translator-api:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_ENABLED=true
      - REDIS_HOST=redis
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

启动服务：
```bash
docker-compose up -d
```

### 2. 单独Docker部署

```bash
# 构建镜像
docker build -t translator-api ./server

# 运行容器
docker run -d \
  --name translator-service \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  translator-api
```

## ⚙️ 高级配置

### 1. 环境变量配置

创建 `.env` 文件（复制自 `.env.example`）：

```bash
# 基本配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# 翻译配置
MAX_TEXT_LENGTH=5000
TRANSLATOR_TYPE=google

# Redis缓存（可选）
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

# 性能调优
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30
```

### 2. 反向代理配置

#### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. HTTPS配置

使用Let's Encrypt获取SSL证书：

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

## 🔧 故障排除

### 常见问题解决

#### 1. Python依赖安装失败

**问题**: `pip install` 命令失败

**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或使用conda
conda install --file requirements.txt
```

#### 2. 端口被占用

**问题**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# 终止进程或使用其他端口
export API_PORT=8001
python app.py
```

#### 3. Chrome插件无法连接

**问题**: 插件无法连接到后端服务

**解决方案**:
1. 确认后端服务正在运行（访问 http://localhost:8000/health）
2. 检查插件的 `manifest.json` 中的 `host_permissions`
3. 检查Chrome控制台是否有错误信息
4. 尝试禁用其他可能冲突的扩展

#### 4. 翻译响应慢

**问题**: 翻译速度很慢

**解决方案**:
1. 启用Redis缓存：设置 `REDIS_ENABLED=true`
2. 检查网络连接
3. 考虑使用CDN或更近的服务器
4. 调整并发数：`MAX_CONCURRENT_REQUESTS=50`

#### 5. Google翻译API限制

**问题**: Google翻译请求被限制

**解决方案**:
1. 添加请求间隔
2. 使用代理服务器
3. 考虑申请Google翻译API密钥
4. 切换到其他翻译服务（百度、有道等）

## 🔄 更新升级

### 更新插件

1. 下载最新版本代码
2. 在Chrome扩展程序页面点击"重新加载"
3. 测试新功能是否正常

### 更新后端服务

```bash
# 停止服务
# 如果使用Docker:
docker-compose down

# 更新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 重启服务
# 如果使用Docker:
docker-compose up -d
```

## 📊 性能监控

### 1. 查看服务状态

```bash
# 健康检查
curl http://localhost:8000/health

# 查看统计信息
curl http://localhost:8000/stats
```

### 2. 日志监控

```bash
# 查看应用日志
tail -f translator.log

# 如果使用Docker:
docker logs -f translator-service
```

### 3. 性能指标

- **响应时间**: 正常情况下应小于2秒
- **缓存命中率**: 建议保持在60%以上
- **内存使用**: 通常应小于100MB
- **CPU使用率**: 正常负载下应小于10%

## 🛡️ 安全配置

### 生产环境建议

1. **使用HTTPS**: 避免明文传输
2. **设置防火墙**: 只开放必要端口
3. **API限流**: 防止滥用
4. **日志审计**: 记录关键操作
5. **定期备份**: 备份配置和数据

### 隐私保护

1. **不记录敏感内容**: 避免在日志中记录用户输入
2. **数据加密**: 敏感配置使用加密存储
3. **访问控制**: 限制API访问权限
4. **数据清理**: 定期清理临时数据

## 📞 技术支持

如遇到安装问题，可以：

1. 查看项目 [Issues](https://github.com/your-repo/issues)
2. 阅读完整的 [README.md](README.md)
3. 联系项目维护者

## 🎉 安装完成

恭喜！如果您已成功完成上述步骤，Chrome翻译插件现在应该可以正常工作了。

**快速测试**:
1. 访问任意英文网页
2. 选中一段文本
3. 查看是否自动弹出翻译结果

享受便捷的翻译体验！🌟