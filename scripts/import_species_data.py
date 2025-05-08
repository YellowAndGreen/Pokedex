#!/usr/bin/env python3
"""数据导入脚本

从指定的JSON文件加载物种数据，并将其导入到数据库中。
"""
import json
import logging
import os  # os 模块在此脚本中未直接使用，如果后续也不使用可以考虑移除
import sys
from pathlib import Path  # 确保 Path 只导入一次
from typing import List, Dict, Optional

import typer  # 用于创建命令行接口
from sqlmodel import Session, select

# 计算项目根目录 (当前脚本的上两级目录)
project_root = Path(__file__).resolve().parent.parent
# 将包含 'app' 模块的 'pokedex_backend' 目录添加到 Python 搜索路径的起始位置，
# 以优先加载项目内部模块。
# 假设项目结构为: project_root/pokedex_backend/app/*
sys.path.insert(0, str(project_root / "pokedex_backend"))


from app.database import engine, get_session, create_db_and_tables
from app.models.species_info_models import (
    Species,
    SpeciesCreate,
    get_pinyin_full,
    get_pinyin_initials,
)

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
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

    pinyin_full_str = ""
    pinyin_initials_str = ""
    try:
        # 尝试为中文名生成全拼和首字母拼音
        pinyin_full_str = get_pinyin_full(chinese_name)
        pinyin_initials_str = get_pinyin_initials(chinese_name)
    except Exception as e:
        logger.warning(f"为 '{chinese_name}' 生成拼音时出错: {e}. 将使用空拼音。")

    # 创建 SpeciesCreate 数据模型实例
    species_data = SpeciesCreate(
        order_details=raw_item.get("目", ""),
        family_details=raw_item.get("科", ""),
        genus_details=raw_item.get("属", ""),
        name_chinese=chinese_name,
        name_english=raw_item.get("英文种名"),
        name_latin=raw_item.get("学名"),
        href=raw_item.get("href"),
        pinyin_full=pinyin_full_str,
        pinyin_initials=pinyin_initials_str,
    )
    return species_data


def import_data(db: Session, json_data_path: Path, dry_run: bool = False) -> None:
    """从JSON文件加载数据并导入到数据库中。

    参数:
        db (Session): 数据库会话，用于执行数据库操作。
        json_data_path (Path): 包含物种数据的JSON文件路径。
        dry_run (bool): 若为 True，则仅模拟导入过程而不实际写入数据库。
    """
    logger.info(f"开始从 '{json_data_path}' 导入数据...")
    if dry_run:
        logger.info("DRY RUN 模式：不会对数据库进行任何更改。")

    try:
        with open(json_data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"错误：JSON文件未找到于 '{json_data_path}'")
        raise  # 文件未找到，向上抛出异常终止后续操作
    except json.JSONDecodeError as e:
        logger.error(f"错误：无法解析JSON文件 '{json_data_path}': {e}")
        raise  # JSON解析失败，向上抛出异常

    species_records = data.get("数据记录")
    if not isinstance(species_records, list):
        logger.error("错误：JSON文件顶层需要有 '数据记录' 键，其值为列表。")
        raise ValueError("JSON文件格式错误：缺少 '数据记录' 列表。")

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

        # 检查数据库中是否已存在相同中文名的物种，避免重复导入
        statement = select(Species).where(
            Species.name_chinese == species_create_obj.name_chinese
        )
        existing_species = db.exec(statement).first()

        if existing_species:
            logger.info(
                f"物种 '{species_create_obj.name_chinese}' 已存在于数据库中，跳过。"
            )
            skipped_existing_count += 1
            continue

        # 将通过验证的 SpeciesCreate 数据对象转换为 Species ORM 模型实例
        db_species = Species.model_validate(species_create_obj)
        new_species_to_add.append(db_species)
        logger.info(f"准备添加新物种: {db_species.name_chinese}")

    if not dry_run and new_species_to_add:
        try:
            db.add_all(new_species_to_add)  # 将所有新物种添加到当前数据库会话
            # 事务提交将由 get_session 的上下文管理器在会话成功结束时处理。
            logger.info(
                f"成功将 {len(new_species_to_add)} 条新物种记录添加到会话。提交将在会话成功结束时发生。"
            )
        except Exception as e:
            logger.error(f"添加物种到数据库会话时发生错误: {e}")
            # 异常将传播到 get_session 的 except 块，由其处理回滚。
            raise
    elif dry_run and new_species_to_add:
        logger.info(f"DRY RUN: 将会添加 {len(new_species_to_add)} 条新物种记录。")
    else:
        logger.info("没有新的物种记录需要添加到数据库。")

    logger.info("--- 导入摘要 ---")
    logger.info(f"总共处理JSON记录: {processed_count}")
    if dry_run:
        logger.info(f"计划添加新记录: {len(new_species_to_add)}")
    else:
        logger.info(f"已添加新记录 (在事务提交前): {len(new_species_to_add)}")
    logger.info(f"因已存在而跳过: {skipped_existing_count}")
    logger.info(f"因数据无效而跳过: {skipped_invalid_count}")
    logger.info("数据导入过程完成。")


# 使用 Typer 创建命令行应用
cli_app = typer.Typer()


@cli_app.command()
def run_import(
    json_file: Path = typer.Option(
        ...,  # '...' 表示此参数是必需的
        help="包含物种数据的JSON文件路径 (例如: data/species_data.json)",
        exists=True,  # Typer 会自动检查文件是否存在
        file_okay=True,  # 必须是文件
        dir_okay=False,  # 不能是目录
        readable=True,  # 文件必须可读
        resolve_path=True,  # 将路径解析为绝对路径
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="执行模拟运行，不实际写入数据库。"
    ),
):
    """从JSON文件导入物种数据到数据库的命令行入口。"""
    logger.info("初始化数据库连接和表结构...")
    try:
        # 确保数据库表已根据模型定义创建或存在
        create_db_and_tables()
        logger.info("数据库表检查/创建完成。")

        # 使用 get_session 生成器管理数据库会话和事务
        # for 循环确保 get_session 的 try/except/finally (含 commit/rollback) 正确执行
        for db_session_instance in get_session():
            try:
                import_data(
                    db=db_session_instance, json_data_path=json_file, dry_run=dry_run
                )
                # 若 import_data 成功, get_session 内部应处理事务提交
            except Exception as e:
                # 捕获 import_data 中未处理或重新抛出的异常
                logger.error(f"数据导入过程中发生顶层错误: {e}")
                logger.info("由于发生错误，事务可能已被回滚 (由 get_session 控制)。")
                sys.exit(1)  # 表示脚本执行失败

        logger.info("数据导入命令执行完毕。")

    except Exception as e:
        # 捕获 create_db_and_tables 或 get_session 本身初始化时可能发生的严重错误
        logger.critical(f"脚本执行过程中发生无法处理的严重错误: {e}", exc_info=True)
        sys.exit(1)  # 表示脚本执行失败


if __name__ == "__main__":
    # 当脚本直接执行时 (e.g., python script_name.py ...)，运行Typer CLI应用
    # 示例用法:
    # python -m scripts.import_species_data --json-file path/to/your/data.json
    # python scripts/import_species_data.py path/to/your/data.json --dry-run
    cli_app()
