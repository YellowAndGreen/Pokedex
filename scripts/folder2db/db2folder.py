#!/usr/bin/env python3
"""
从数据库导出到文件夹的主脚本。
获取数据库中的所有分类和图片，并保存到指定目录下对应的文件夹中。
"""

import os
import sys
import argparse
import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from tqdm import tqdm

from .api_client import APIClient
from .file_utils import ensure_dir, sanitize_filename
from .config import DEFAULT_API_URL, DEFAULT_LIMIT

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
    parser = argparse.ArgumentParser(description="从图鉴数据库导出到文件夹结构")
    parser.add_argument("output_dir", help="导出图片的目标根目录")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API基础URL")
    parser.add_argument("--skip-existing", action="store_true", help="跳过已存在的文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    parser.add_argument("--category", help="仅导出指定名称的分类")

    return parser


def download_image(
    client: APIClient, image_url: str, output_path: str, skip_existing: bool = False
) -> bool:
    """
    下载单张图片。

    参数:
        client (APIClient): API客户端实例
        image_url (str): 图片URL
        output_path (str): 保存路径
        skip_existing (bool): 是否跳过已存在的文件

    返回:
        bool: 是否成功下载
    """
    # 检查文件是否已存在
    if skip_existing and os.path.exists(output_path):
        logger.debug(f"跳过已存在的文件: {output_path}")
        return True

    try:
        client.download_file(image_url, output_path)
        return True
    except Exception as e:
        logger.error(f"下载图片 '{image_url}' 失败: {e}")
        return False


def process_category(
    client: APIClient,
    category: Dict[str, Any],
    output_dir: str,
    skip_existing: bool = False,
) -> Tuple[int, int]:
    """
    处理单个分类。

    参数:
        client (APIClient): API客户端实例
        category (Dict[str, Any]): 分类信息
        output_dir (str): 输出根目录
        skip_existing (bool): 是否跳过已存在的文件

    返回:
        Tuple[int, int]: 成功下载的图片数量和总图片数量
    """
    category_name = category["name"]
    category_id = category["id"]

    # 创建分类文件夹
    category_dir = os.path.join(output_dir, category_name)
    ensure_dir(category_dir)

    # 获取该分类下的所有图片
    try:
        category_with_images = client.get_category_with_images(category_id)
        images = category_with_images.get("images", [])
        logger.info(f"分类 '{category_name}' 下有 {len(images)} 张图片")
    except Exception as e:
        logger.error(f"获取分类 '{category_name}' 的图片列表失败: {e}")
        return 0, 0

    success_count = 0

    # 处理每张图片
    images_pbar = tqdm(
        images, desc=f"下载 {category_name} 图片", unit="张", leave=False
    )
    for image in images_pbar:
        # 获取图片URL
        image_url = image["image_url"]

        # 使用原始文件名或根据标题/ID生成文件名
        if image.get("original_filename"):
            filename = image["original_filename"]
        elif image.get("title"):
            # 添加适当的扩展名
            filename = f"{image['title']}.jpg"
        else:
            filename = f"{image['id']}.jpg"

        # 确保文件名安全
        filename = sanitize_filename(filename)
        output_path = os.path.join(category_dir, filename)

        images_pbar.set_description(f"下载: {filename}")

        # 下载图片
        if download_image(client, image_url, output_path, skip_existing):
            success_count += 1

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

    # 确保输出目录存在
    ensure_dir(args.output_dir)

    # 初始化API客户端
    client = APIClient(base_url=args.api_url)

    # 记录开始时间
    start_time = time.time()

    try:
        # 获取所有分类
        logger.info("获取分类列表...")
        try:
            categories = client.get_categories(limit=DEFAULT_LIMIT)
        except Exception as e:
            logger.error(f"获取分类列表失败: {e}")
            return 1

        logger.info(f"获取到 {len(categories)} 个分类")

        # 如果指定了特定分类，进行过滤
        if args.category:
            logger.info(f"仅导出指定的分类: {args.category}")
            categories = [c for c in categories if c["name"] == args.category]
            if not categories:
                logger.error(f"未找到指定的分类: {args.category}")
                return 1

        # 统计数据
        total_categories = len(categories)
        total_images = 0
        success_images = 0

        # 进度条设置
        categories_pbar = tqdm(categories, desc="导出分类", unit="个")

        # 处理每个分类
        for category in categories_pbar:
            category_name = category["name"]
            categories_pbar.set_description(f"导出分类: {category_name}")

            # 处理单个分类
            success_count, total_count = process_category(
                client=client,
                category=category,
                output_dir=args.output_dir,
                skip_existing=args.skip_existing,
            )

            # 更新统计
            total_images += total_count
            success_images += success_count

        # 计算运行时间和成功率
        elapsed_time = time.time() - start_time
        success_rate = (success_images / total_images * 100) if total_images > 0 else 0

        # 打印结果
        logger.info("导出完成!")
        logger.info(f"共导出 {total_categories} 个分类，{total_images} 张图片")
        logger.info(f"成功下载 {success_images} 张图片 (成功率: {success_rate:.2f}%)")
        logger.info(f"文件保存在: {os.path.abspath(args.output_dir)}")
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
