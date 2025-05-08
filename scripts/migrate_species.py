#!/usr/bin/env python3
"""
物种字段迁移脚本

功能：
1. 将原index.json中的"种"字段拆分为"中文种名"和"学名"
2. 生成符合JSON规范的新文件
3. 保留原始文件备份
4. 支持大文件流式处理
"""

import ijson
import json
import logging
from pathlib import Path
from typing import Iterator, Dict, Any
from scripts.logging_config import configure_logging

configure_logging()


def process_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理单个数据项，拆分种名字段

    参数:
        item (Dict[str, Any]): 原始数据项

    返回:
        Dict[str, Any]: 处理后的数据项

    异常处理:
        - 记录格式错误并保留原始值
    """
    if "种" in item:
        species_field = item["种"]
        try:
            # 使用正则表达式匹配中文名、英文名和拉丁学名
            import re

            pattern = r"^([\u4e00-\u9fa5]+)([A-Za-z ].+?) {2,}([A-Z][a-z]+ [a-z]+)$"
            match = re.match(pattern, species_field)

            if match:
                chinese_name = match.group(1).strip()
                english_name = match.group(2).strip()
                scientific_name = match.group(3).strip()

                item["中文种名"] = chinese_name
                item["英文种名"] = english_name
                item["学名"] = scientific_name
            else:
                # 尝试简单分割作为fallback
                parts = [p.strip() for p in species_field.split("  ") if p]
                if len(parts) >= 2:
                    item["中文种名"] = parts[0]
                    item["学名"] = " ".join(parts[1:])
                else:
                    raise ValueError("格式解析失败")

            del item["种"]
        except Exception as e:
            logging.warning(f"种字段格式错误: {species_field} | 错误: {str(e)}")
            item["中文种名"] = ""
            item["英文种名"] = ""
            item["学名"] = species_field
    return item


def stream_process(input_path: Path, output_path: Path) -> None:
    """流式处理JSON数据"""
    with input_path.open("rb") as infile, output_path.open(
        "w", encoding="utf-8"
    ) as outfile:
        outfile.write('{\n  "数据记录": [\n')

        # 修正为正确的JSON路径并添加容错处理
        # 修正为根数组结构
        prefix = "item"
        items = ijson.items(infile, prefix)
        if not items:
            logging.error(f"未找到有效数据路径: {prefix}")
            raise ValueError("无效的JSON结构")
        first_item = True
        for item in items:
            processed = process_item(item)
            if not first_item:
                outfile.write(",\n")
            json.dump(processed, outfile, ensure_ascii=False, indent=2)
            first_item = False

        outfile.write("\n  ]\n}")


def main() -> None:
    """主迁移流程"""
    input_path = Path("index.json")
    backup_path = Path("index.json.bak")
    output_path = Path("index_new.json")

    try:
        # 创建备份
        input_path.rename(backup_path)
        logging.info(f"创建备份文件: {backup_path}")

        # 流式处理
        logging.info("开始迁移数据...")
        stream_process(backup_path, output_path)

        # 替换原文件
        output_path.rename(input_path)
        logging.info("数据迁移完成")

    except Exception as e:
        logging.error(f"迁移失败: {str(e)}")
        raise


if __name__ == "__main__":
    main()
