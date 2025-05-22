#!/usr/bin/env python3
"""
配置模块，包含所有脚本的默认参数和常量。
"""

# 默认API地址
DEFAULT_API_URL = "http://localhost:8000"

# 支持的图片格式
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

# 上传错误重试次数
MAX_RETRIES = 3

# 默认分页参数
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 100

# 默认下载缓冲区大小 (8KB)
DOWNLOAD_CHUNK_SIZE = 8192
