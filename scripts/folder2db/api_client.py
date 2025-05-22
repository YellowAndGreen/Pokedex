#!/usr/bin/env python3
"""
API客户端模块，提供与后端API交互的功能。
"""

import os
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin

from .config import MAX_RETRIES

# 配置日志
logger = logging.getLogger(__name__)


class APIClient:
    """
    API客户端类，封装与后端API的所有交互。
    """

    def __init__(self, base_url: str):
        """
        初始化API客户端。

        参数:
            base_url (str): API基础URL
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Folder2DB-Tool/1.0",
            }
        )

    def create_category(
        self, name: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建新的类别。

        参数:
            name (str): 类别名称
            description (Optional[str]): 类别描述

        返回:
            Dict[str, Any]: 创建的类别信息

        异常:
            requests.HTTPError: 请求失败时抛出
        """
        url = f"{self.base_url}/api/categories/"
        data = {"name": name}
        if description:
            data["description"] = description

        logger.debug(f"创建类别: {name}")
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def upload_image(
        self,
        image_path: str,
        category_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        set_as_thumbnail: bool = False,
    ) -> Dict[str, Any]:
        """
        上传图片到指定类别。

        参数:
            image_path (str): 图片文件路径
            category_id (str): 目标类别ID
            title (Optional[str]): 图片标题
            description (Optional[str]): 图片描述
            tags (Optional[str]): 图片标签（逗号分隔）
            set_as_thumbnail (bool): 是否设置为类别缩略图

        返回:
            Dict[str, Any]: 上传的图片信息

        异常:
            requests.HTTPError: 请求失败时抛出
            FileNotFoundError: 图片文件不存在时抛出
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        url = f"{self.base_url}/api/images/upload/"

        # 准备表单数据
        data = {
            "category_id": category_id,
            "set_as_category_thumbnail": "true" if set_as_thumbnail else "false",
        }

        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags

        # 准备文件数据
        filename = os.path.basename(image_path)
        logger.debug(f"上传图片: {filename} 到类别ID: {category_id}")

        with open(image_path, "rb") as f:
            files = {"file": (filename, f)}
            for attempt in range(MAX_RETRIES):
                try:
                    response = self.session.post(url, data=data, files=files)
                    response.raise_for_status()
                    return response.json()
                except requests.HTTPError as e:
                    if attempt < MAX_RETRIES - 1:
                        logger.warning(
                            f"上传失败，重试中 ({attempt+1}/{MAX_RETRIES}): {e}"
                        )
                        continue
                    logger.error(f"上传失败: {e}")
                    raise

    def get_categories(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取所有分类列表。

        参数:
            skip (int): 分页起始位置
            limit (int): 单页限制数量

        返回:
            List[Dict[str, Any]]: 分类信息列表

        异常:
            requests.HTTPError: 请求失败时抛出
        """
        url = f"{self.base_url}/api/categories/"
        params = {"skip": skip, "limit": limit}

        logger.debug(f"获取分类列表: skip={skip}, limit={limit}")
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_category_with_images(self, category_id: str) -> Dict[str, Any]:
        """
        获取特定分类及其包含的所有图片。

        参数:
            category_id (str): 分类ID

        返回:
            Dict[str, Any]: 分类及其图片信息

        异常:
            requests.HTTPError: 请求失败时抛出
        """
        url = f"{self.base_url}/api/categories/{category_id}/"

        logger.debug(f"获取分类及图片: category_id={category_id}")
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def download_file(self, url: str, output_path: str) -> None:
        """
        下载文件到指定路径。

        参数:
            url (str): 文件URL
            output_path (str): 保存路径

        异常:
            requests.HTTPError: 请求失败时抛出
        """
        from .config import DOWNLOAD_CHUNK_SIZE

        logger.debug(f"下载文件: {url} -> {output_path}")
        response = self.session.get(url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                f.write(chunk)
