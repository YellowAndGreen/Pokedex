#!/usr/bin/env python3
"""数据导入脚本

从指定的JSON文件加载物种数据，并将其导入到数据库中。
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

import typer  # 用于创建命令行接口
from sqlmodel import Session, select

# 路径调整：确保可以从脚本目录正确导入app模块
# 这通常需要将项目根目录添加到 sys.path 或使用正确的PYTHONPATH
# 为简单起见，假设脚本从 pokedex_backend 目录运行，或者PYTHONPATH已设置
# 或者在IDE中运行时，通常会自动处理项目源根
from app.database import engine, get_session, create_db_and_tables
from app.models.species_info_models import (
    Species,
    SpeciesCreate,
    get_pinyin_full,
    get_pinyin_initials,
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_species_from_json_item(raw_item: Dict) -> Optional[SpeciesCreate]:
    """将从JSON读取的单个原始字典项转换为 SpeciesCreate 对象，并填充拼音。

    参数:
        raw_item (Dict): 从JSON文件读取的原始字典数据。

    返回:
        Optional[SpeciesCreate]: 如果数据有效则返回 SpeciesCreate 对象，否则返回 None。
    """
    chinese_name = raw_item.get("中文种名")
    if not chinese_name:
        logger.warning(f"跳过缺少 '中文种名' 的记录: {raw_item}")
        return None

    # 创建 SpeciesCreate 实例，并填充拼音
    species_data = SpeciesCreate(
        order_details=raw_item.get("目", ""),
        family_details=raw_item.get("科", ""),
        genus_details=raw_item.get("属", ""),
        name_chinese=chinese_name,
        name_english=raw_item.get("英文种名"),
        name_latin=raw_item.get("学名"),
        href=raw_item.get("href"),
        pinyin_full=get_pinyin_full(chinese_name),  # 直接生成拼音
        pinyin_initials=get_pinyin_initials(chinese_name),  # 直接生成拼音
    )
    return species_data


def import_data(db: Session, json_data_path: Path, dry_run: bool = False) -> None:
    """从JSON文件加载数据并导入到数据库中。

    参数:
        db (Session): 数据库会话。
        json_data_path (Path): 包含物种数据的JSON文件路径。
        dry_run (bool): 如果为 True，则仅模拟导入过程而不实际写入数据库。
    """
    logger.info(f"开始从 '{json_data_path}' 导入数据...")
    if dry_run:
        logger.info("DRY RUN 模式：不会对数据库进行任何更改。")

    try:
        with open(json_data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"错误：JSON文件未找到于 '{json_data_path}'")
        return
    except json.JSONDecodeError:
        logger.error(f"错误：无法解析JSON文件 '{json_data_path}'")
        return

    species_records = data.get("数据记录")
    if not isinstance(species_records, list):
        logger.error("错误：JSON文件顶层需要有 '数据记录' 键，其值为列表。")
        return

    new_species_to_add: List[Species] = []
    processed_count = 0
    skipped_existing_count = 0
    skipped_invalid_count = 0

    for raw_item in species_records:
        processed_count += 1
        species_create_obj = prepare_species_from_json_item(raw_item)

        if not species_create_obj:
            skipped_invalid_count += 1
            continue

        # 检查数据库中是否已存在相同中文名的物种
        existing_species = db.exec(
            select(Species).where(
                Species.name_chinese == species_create_obj.name_chinese
            )
        ).first()

        if existing_species:
            logger.info(
                f"物种 '{species_create_obj.name_chinese}' 已存在于数据库中，跳过。"
            )
            skipped_existing_count += 1
            continue

        # 将 SpeciesCreate 对象转换为 Species ORM 模型实例
        db_species = Species.model_validate(species_create_obj)
        new_species_to_add.append(db_species)
        logger.info(f"准备添加新物种: {db_species.name_chinese}")

    if not dry_run and new_species_to_add:
        db.add_all(new_species_to_add)
        # db.commit() # 事务提交将由 get_session 的上下文管理器处理
        logger.info(
            f"成功将 {len(new_species_to_add)} 条新物种记录添加到会话。提交将在会话结束时发生。"
        )
    elif dry_run and new_species_to_add:
        logger.info(f"DRY RUN: 将会添加 {len(new_species_to_add)} 条新物种记录。")
    else:
        logger.info("没有新的物种记录需要添加到数据库。")

    logger.info(f"--- 导入摘要 ---")
    logger.info(f"总共处理JSON记录: {processed_count}")
    if dry_run:
        logger.info(f"计划添加新记录: {len(new_species_to_add)}")
    else:
        logger.info(f"已添加新记录: {len(new_species_to_add)}")
    logger.info(f"因已存在而跳过: {skipped_existing_count}")
    logger.info(f"因数据无效而跳过: {skipped_invalid_count}")
    logger.info("数据导入过程完成。")


# 使用 Typer 创建命令行应用
cli_app = typer.Typer()


@cli_app.command()
def run_import(
    json_file: Path = typer.Option(
        ...,
        help="包含物种数据的JSON文件路径 (例如: index.json)",
        exists=True,  # Typer会自动检查文件是否存在
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="执行模拟运行，不实际写入数据库。"
    ),
):
    """从JSON文件导入物种数据到数据库。"""
    logger.info("初始化数据库连接和表结构...")
    # 确保表已创建，这在主应用启动时也会做，但脚本独立运行时也需要
    # 注意：create_db_and_tables()会使用在app.database中定义的engine
    create_db_and_tables()
    logger.info("数据库表检查/创建完成。")

    # 获取数据库会话
    # 使用 get_session() 的上下文管理特性来确保会话正确关闭和事务处理
    with next(get_session()) as db_session:
        import_data(db=db_session, json_data_path=json_file, dry_run=dry_run)


if __name__ == "__main__":
    # 当脚本直接执行时，运行Typer CLI应用
    # 例如: python -m scripts.import_species_data run-import --json-file path/to/index.json
    # 或者: python scripts/import_species_data.py run-import --json-file path/to/index.json
    cli_app()
