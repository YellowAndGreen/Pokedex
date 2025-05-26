#!/usr/bin/env python3
"""
从文件夹导入到数据库的主脚本。
扫描指定目录下的Category文件夹，并将其中的图片上传到对应的类别。
"""

import os
import sys
import argparse
import logging
import time
from typing import List, Tuple, Dict, Any, Optional

from tqdm import tqdm

from .api_client import APIClient
from .file_utils import scan_folders, get_image_files
from .config import DEFAULT_API_URL

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def setup_arg_parser() -> argparse.ArgumentParser:
    """
    设置命令行参数解析器。

    返回:
        argparse.ArgumentParser: 参数解析器
    """
    parser = argparse.ArgumentParser(description="将文件夹结构导入到图鉴数据库")
    parser.add_argument("root_dir", help="包含Category文件夹的根目录")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API基础URL")
    # 旧的 --thumbnail 参数定义（将被移除或注释掉）
    # parser.add_argument(
    #     "--thumbnail", action="store_true", help="将第一张图片设置为类别缩略图"
    # )
    
    # 将 thumbnail 的默认值设为 True
    parser.set_defaults(thumbnail=True)
    # 添加 --no-thumbnail 标志，如果使用此标志，则 thumbnail 会被设为 False
    parser.add_argument(
        "--no-thumbnail",
        dest="thumbnail",  # 确保它作用于 args.thumbnail
        action="store_false",
        help="不将第一张图片设置为类别缩略图 (默认启用缩略图设置)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    parser.add_argument("--dry-run", action="store_true", help="仅测试，不实际上传")

    return parser


def process_category(
    client: APIClient,
    category_name: str,
    category_path: str,
    set_thumbnail: bool = False,
    dry_run: bool = False,
) -> Tuple[int, int]:
    """
    处理单个分类文件夹。

    参数:
        client (APIClient): API客户端实例
        category_name (str): 分类名称
        category_path (str): 分类文件夹路径
        set_thumbnail (bool): 是否设置缩略图
        dry_run (bool): 是否仅测试不上传

    返回:
        Tuple[int, int]: 成功上传的图片数量和总图片数量
    """
    if dry_run:
        logger.info(f"[DRY RUN] 创建分类: {category_name}")
        category_id = "dry-run-id"
    else:
        try:
            category = client.create_category(name=category_name)
            category_id = category["id"]
            logger.debug(f"创建分类成功: {category_name} (ID: {category_id})")
        except Exception as e:
            logger.error(f"创建分类 '{category_name}' 失败: {e}")
            return 0, 0

    # 获取该分类下的所有图片
    try:
        images = get_image_files(category_path)
        logger.info(f"分类 '{category_name}' 下发现 {len(images)} 张图片")
    except Exception as e:
        logger.error(f"获取分类 '{category_name}' 的图片列表失败: {e}")
        return 0, 0

    success_count = 0

    # 处理每张图片
    images_pbar = tqdm(
        enumerate(images),
        total=len(images),
        desc=f"上传 {category_name} 图片",
        unit="张",
    )
    for i, image_path in images_pbar:
        # 提取图片名作为标题
        filename = os.path.basename(image_path)
        title = os.path.splitext(filename)[0]

        # 设置第一张图片为缩略图
        set_as_thumbnail = set_thumbnail and i == 0

        if dry_run:
            logger.debug(f"[DRY RUN] 上传图片: {filename} 到类别: {category_name}")
            success_count += 1
            continue

        try:
            client.upload_image(
                image_path=image_path,
                category_id=category_id,
                title=title,
                set_as_thumbnail=set_as_thumbnail,
            )
            success_count += 1
        except Exception as e:
            logger.error(f"上传图片 '{filename}' 失败: {e}")

    return success_count, len(images)


def main():
    """主函数"""
    # 解析命令行参数
    parser = setup_arg_parser()
    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("启用详细日志")

    # 初始化API客户端
    client = APIClient(base_url=args.api_url)

    # 记录开始时间
    start_time = time.time()

    try:
        # 扫描文件夹结构
        logger.info(f"扫描目录: {args.root_dir}")
        categories = scan_folders(args.root_dir)

        if not categories:
            logger.warning(f"未在 {args.root_dir} 下找到任何分类文件夹")
            return

        # 统计数据
        total_categories = len(categories)
        total_images = 0
        success_images = 0

        # 进度条设置
        categories_pbar = tqdm(categories, desc="处理分类", unit="个")

        # 处理每个分类文件夹
        for category_name, category_path in categories_pbar:
            categories_pbar.set_description(f"处理分类: {category_name}")

            # 处理单个分类
            success_count, total_count = process_category(
                client=client,
                category_name=category_name,
                category_path=category_path,
                set_thumbnail=args.thumbnail,
                dry_run=args.dry_run,
            )

            # 更新统计
            total_images += total_count
            success_images += success_count

        # 计算运行时间和成功率
        elapsed_time = time.time() - start_time
        success_rate = (success_images / total_images * 100) if total_images > 0 else 0

        # 打印结果
        mode = "[DRY RUN] " if args.dry_run else ""
        logger.info(f"{mode}导入完成!")
        logger.info(f"共处理 {total_categories} 个分类，{total_images} 张图片")
        logger.info(f"成功上传 {success_images} 张图片 (成功率: {success_rate:.2f}%)")
        logger.info(f"耗时: {elapsed_time:.2f} 秒")

    except KeyboardInterrupt:
        logger.info("\n任务被用户中断")
        return
    except Exception as e:
        logger.error(f"发生错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
