#!/usr/bin/env python3

from fastapi import APIRouter

router = APIRouter(prefix="/tags", tags=["标签管理"])

# 你可以在这里添加标签相关的API端点
