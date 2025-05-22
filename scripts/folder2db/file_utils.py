#!/usr/bin/env python3
"""
文件系统操作工具模块，提供文件夹扫描、图片获取等功能。
"""

import os
import logging
from typing import List, Tuple, Dict, Any, Optional

from .config import SUPPORTED_FORMATS

# 配置日志
logger = logging.getLogger(__name__)


def scan_folders(root_dir: str) -> List[Tuple[str, str]]:
    """
    扫描根目录获取所有分类文件夹。

    参数:
        root_dir (str): 要扫描的根目录路径

    返回:
        List[Tuple[str, str]]: 分类名称和路径的元组列表 [(category_name, full_path), ...]
    """
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"目录不存在: {root_dir}")

    if not os.path.isdir(root_dir):
        raise NotADirectoryError(f"指定路径不是目录: {root_dir}")

    categories = []
    for item in os.listdir(root_dir):
        full_path = os.path.join(root_dir, item)
        if os.path.isdir(full_path):
            categories.append((item, full_path))

    logger.info(f"扫描到 {len(categories)} 个分类文件夹")
    return categories


def get_image_files(directory: str) -> List[str]:
    """
    获取目录中的所有图片文件。

    参数:
        directory (str): 要扫描的目录路径

    返回:
        List[str]: 图片文件的完整路径列表
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"目录不存在: {directory}")

    image_files = []

    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in SUPPORTED_FORMATS:
                image_files.append(full_path)

    # 按文件名排序，确保处理顺序一致
    return sorted(image_files)


def ensure_dir(directory: str) -> None:
    """
    确保目录存在，如果不存在则创建。

    参数:
        directory (str): 要确保存在的目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug(f"创建目录: {directory}")


def sanitize_filename(filename: str) -> str:
    """
    确保文件名合法，替换或移除不允许的字符。

    参数:
        filename (str): 原始文件名

    返回:
        str: 处理后的合法文件名
    """
    # 替换不允许的字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # 确保文件名不为空
    if not filename:
        filename = "untitled"

    return filename
