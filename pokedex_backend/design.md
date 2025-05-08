**I. 方案概述**

本方案旨在为 FastAPI 后端项目添加一套物种信息查询 API。主要包含两个核心功能：

1.  **物种名称建议 API**:
    * 端点：`/api/v1/species/suggestions`
    * 功能：接收用户输入的单个查询字符串。后端会利用此字符串，同时对数据库中存储的物种中文名、中文名全拼以及中文名拼音首字母进行前缀匹配搜索。
    * 输出：返回一个最多包含10个匹配物种的**中文名列表**，非常适用于搜索框的自动建议或快速查找功能。

2.  **物种详细信息 API**:
    * 端点：`/api/v1/species/details/{chinese_name}`
    * 功能：通过提供一个精确的、完整的物种**中文名**（作为URL路径的一部分）。
    * 输出：返回该特定物种的全部详细信息。

该方案将使用 FastAPI 构建 API，SQLModel 作为 ORM 与数据库交互，并利用 `pypinyin` 库处理中文名到拼音的转换。数据模型将包含物种的目、科、属、中文名、英文名、学名、链接以及由中文名生成的全拼和首字母拼音，以便高效搜索。

**II. API 设计**

**API 1: 物种名称建议 (Species Name Suggestions)**

* **端点 (Endpoint):** `/api/v1/species/suggestions`
* **方法 (Method):** `GET`
* **查询参数 (Query Parameters):**
    * `q`: `str`, **必需**。用户输入的搜索词。后端将使用此单一字符串尝试匹配物种的中文名、全拼或拼音首字母。
    * `limit`: `int`, 可选, 默认 `10`。返回建议结果的最大数量 (例如，可限定范围 `1` 到 `20`)。
* **成功响应 (Success Response):** `200 OK`
    * **内容 (Content):** 一个 JSON 数组，每个元素是匹配到的物种的中文名字符串。
        ```json
        [
          "小印加雀",
          "大印加雀",
          "白颊林雀"
        ]
        ```
* **错误响应 (Error Responses):**
    * `400 Bad Request`: 若查询参数 `q` 为空。
    * `422 Unprocessable Entity`: 若查询参数类型不正确 (FastAPI 自动处理)。

**API 2: 物种详细信息 (Species Full Details)**

* **端点 (Endpoint):** `/api/v1/species/details/{chinese_name}`
* **方法 (Method):** `GET`
* **路径参数 (Path Parameter):**
    * `chinese_name`: `str`, **必需**。要查询物种的**精确**中文名。如果中文名中包含特殊字符 (如 `/`)，客户端在发起请求时需要进行 URL 编码。
* **成功响应 (Success Response):** `200 OK`
    * **内容 (Content):** 一个 JSON 对象，包含该物种的完整信息 (基于 `SpeciesRead` 模型)。
        ```json
        {
          "id": 1,
          "order_details": "雀形目Passeriformes",
          "family_details": "裸鼻雀科 Thraupidae",
          "genus_details": "印加雀属Incaspiza",
          "name_chinese": "小印加雀",
          "name_english": "Little Inca Finch",
          "name_latin": "Incaspiza watkinsi",
          "href": "https://dongniao.net/...",
          "pinyin_full": "xiaoyinjiaque",
          "pinyin_initials": "xyjq"
        }
        ```
* **错误响应 (Error Responses):**
    * `404 Not Found`: 如果根据提供的 `chinese_name` 未找到对应物种。
    * `422 Unprocessable Entity`: 若路径参数存在问题 (FastAPI 自动处理)。

**III. 核心代码实现**

**A. 数据模型 (Data Models - `app/models/species_models.py`)**

```python
from typing import Optional, List
from sqlmodel import Field, SQLModel
from pypinyin import pinyin, Style # 用于生成拼音

# --- 拼音处理工具函数 ---
def get_pinyin_full(text: str) -> str:
    """将中文文本转换为全拼 (小写)"""
    if not text:
        return ""
    return "".join(item[0] for item in pinyin(text, style=Style.NORMAL, heteronyms=False)).lower()

def get_pinyin_initials(text: str) -> str:
    """将中文文本转换为拼音首字母 (小写)"""
    if not text:
        return ""
    return "".join(item[0][0] for item in pinyin(text, style=Style.FIRST_LETTER, heteronyms=False)).lower()

# --- SQLModel 定义 ---
class SpeciesBase(SQLModel):
    order_details: str = Field(description="目信息 (例如: 雀形目Passeriformes)")
    family_details: str = Field(description="科信息 (例如: 裸鼻雀科 Thraupidae)")
    genus_details: str = Field(description="属信息 (例如: 印加雀属Incaspiza)")
    
    # 为确保第二个API的准确性，中文名应在数据库中唯一
    name_chinese: str = Field(index=True, unique=True, description="中文种名")
    name_english: Optional[str] = Field(default=None, description="英文种名")
    name_latin: Optional[str] = Field(default=None, description="学名 (拉丁文学名)")
    href: Optional[str] = Field(default=None, description="相关链接")

    # 衍生字段，用于高效搜索，在数据入库时生成
    pinyin_full: Optional[str] = Field(default=None, index=True, description="中文名全拼 (小写)")
    pinyin_initials: Optional[str] = Field(default=None, index=True, description="中文名拼音首字母 (小写)")

class Species(SpeciesBase, table=True):
    # __tablename__ = "species" # SQLModel 会自动推断，但也可显式指定
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

class SpeciesCreate(SpeciesBase):
    # 用于创建新物种记录时的数据模型
    # pinyin_full 和 pinyin_initials 将在数据入库前根据 name_chinese 计算填充
    pass

class SpeciesRead(SpeciesBase): 
    # 用于从API读取/返回物种信息的数据模型
    id: int
    # 默认情况下，SpeciesBase 中的所有字段都会被包含。
    # pinyin_full 和 pinyin_initials 字段默认也会包含在API响应中，这与 /species/details/{chinese_name} API的示例输出一致。
    # 若不希望某些内部字段 (如拼音) 暴露给API消费者，可通过Config进行配置：
    # class Config:
    #     fields = {
    #         'pinyin_full': {'exclude': True},
    #         'pinyin_initials': {'exclude': True}
    #     }

# --- 数据填充逻辑的辅助说明 (实际应在独立脚本中) ---
# 示意如何根据输入JSON数据创建并准备 Species 对象用于数据库存储
# from app.database import engine, Session # 假设这些在您的项目中已定义
#
# def prepare_species_for_db(raw_data_item: dict) -> Optional[SpeciesCreate]:
#     """根据原始字典数据，创建一个 SpeciesCreate 对象"""
#     chinese_name = raw_data_item.get("中文种名")
#     if not chinese_name:
#         return None # 如果没有中文名，则跳过此条数据
#
#     return SpeciesCreate(
#         order_details=raw_data_item.get("目", ""),
#         family_details=raw_data_item.get("科", ""),
#         genus_details=raw_data_item.get("属", ""),
#         name_chinese=chinese_name,
#         name_english=raw_data_item.get("英文种名"),
#         name_latin=raw_data_item.get("学名"),
#         href=raw_data_item.get("href"),
#         pinyin_full=get_pinyin_full(chinese_name),
#         pinyin_initials=get_pinyin_initials(chinese_name)
#     )
#
# def example_json_data_import(session: Session, all_raw_data: List[dict]):
#     """示例：如何将一批原始数据转换为Species对象并添加到数据库会话"""
#     new_species_objects = []
#     skipped_count = 0
#     for raw_item in all_raw_data:
#         species_to_create = prepare_species_for_db(raw_item)
#         if species_to_create:
#             # 检查数据库中是否已存在相同中文名的物种
#             # 注意：此检查依赖于数据库会话(session)的查询能力。
#             # 在实际脚本中，需要确保 session 是有效的。
#             # from sqlmodel import select # 确保 select 已导入
#             # existing = session.exec(select(Species).where(Species.name_chinese == species_to_create.name_chinese)).first()
#             # if not existing:
#             #     db_species = Species.model_validate(species_to_create) # SQLModel v0.0.14+
#             #     new_species_objects.append(db_species)
#             # else:
#             #     print(f"物种 '{species_to_create.name_chinese}' 已存在，跳过。")
#             #     skipped_count += 1
#             # 简化版，实际应使用上面的查询逻辑，此处仅为示意
#             # 为了在设计文档中保持简洁，我们将详细的查重逻辑放在实际的导入脚本中
#             # 此处仅示意模型转换和添加
#             db_species = Species.model_validate(species_to_create) 
#             new_species_objects.append(db_species) 
#
#     if new_species_objects:
#         # session.add_all(new_species_objects) # 实际操作时取消注释
#         # session.commit() # 提交事务应在调用此函数的地方处理，或者根据实际情况
#         pass
#     print(f"准备添加 {len(new_species_objects)} 条新的物种记录。跳过 {skipped_count} 条已存在的记录。")
#
# # 示例输入数据结构
# # example_data_list = [
# #     {
# #         "目": "雀形目Passeriformes", "科": "裸鼻雀科 Thraupidae", "属": "印加雀属Incaspiza",
# #         "href": "https://example.com/species/1", "中文种名": "小印加雀", 
# #         "英文种名": "Little Inca Finch", "学名": "Incaspiza watkinsi"
# #     },
# #     # ... 更多数据
# # ]
# # with Session(engine) as session:
# #     example_json_data_import(session, example_data_list)
# #     session.commit() # 最终提交
```

**B. CRUD 操作 (CRUD Operations - `app/crud/species_crud.py`)**

```python
from typing import List, Optional
from sqlmodel import Session, select, or_
from sqlalchemy import func # 用于数据库端的 lower 函数

# 确保从正确的模型路径导入
from app.models.species_models import Species 

def search_species_names_by_term(
    db: Session,
    search_term: str, # 用户输入的单一查询字符串
    limit: int = 10
) -> List[str]:
    """
    根据用户提供的单个 search_term 字符串，构造查询以进行前缀匹配。
    该查询会尝试将 search_term 与以下三个预存字段进行 OR 匹配：
    1. 物种的中文名 (name_chinese)
    2. 物种的中文名全拼 (pinyin_full) - 已小写存储
    3. 物种的中文名拼音首字母 (pinyin_initials) - 已小写存储
    函数返回匹配到的物种中文名列表。
    """
    if not search_term:
        return []

    term_lower = search_term.lower() # 将输入统一转为小写，以匹配已小写存储的拼音字段

    # 构建 OR 查询条件
    # func.lower(Species.name_chinese) 用于在数据库层面进行不区分大小写的中文名匹配 (如果需要)
    conditions = or_(
        func.lower(Species.name_chinese).startswith(term_lower), # 匹配中文名前缀
        Species.pinyin_full.startswith(term_lower),              # 匹配全拼前缀
        Species.pinyin_initials.startswith(term_lower)           # 匹配拼音首字母前缀
    )

    # 构建查询语句，仅选择物种的中文名 (Species.name_chinese)
    statement = select(Species.name_chinese).where(conditions).limit(limit)
    
    # 执行查询并获取所有结果
    matched_chinese_names = db.exec(statement).all()
    return matched_chinese_names # SQLModel/SQLAlchemy 将返回字符串列表

def get_species_by_exact_chinese_name(
    db: Session,
    name_chinese: str
) -> Optional[Species]:
    """
    根据精确的物种中文名查找并返回完整的物种信息对象。
    为提升用户体验，匹配时忽略输入的大小写。
    """
    # 使用 func.lower 确保与数据库中的 name_chinese 进行不区分大小写的比较
    # 假设数据库中的 name_chinese 字段本身可能大小写不一，或者希望查询时更灵活
    statement = select(Species).where(func.lower(Species.name_chinese) == name_chinese.lower())
    
    # 如果能保证 name_chinese 存储和查询时大小写完全一致，可以直接比较：
    # statement = select(Species).where(Species.name_chinese == name_chinese)
    
    result = db.exec(statement).first() # 获取单个匹配结果
    return result
```

**C. API 路由 (API Routers - `app/routers/species.py`)**

```python
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlmodel import Session

# 模拟的数据库会话依赖 (实际项目中应从 app.database 或类似模块导入真实的 get_db)
# def get_db_placeholder():
#     """占位符：实际应用中应提供一个真正的数据库会话生成器。"""
#     # 例如:
#     # from app.database import SessionLocal # 假设 SessionLocal 在 app.database 中定义
#     # db = SessionLocal()
#     # try:
#     #     yield db
#     # finally:
#     #     db.close()
#     # print("Warning: Using placeholder DB session. No actual DB operations will occur.")
#     # yield None # 在此方案中，CRUD将无法工作，需替换为真实会话
#     # 注意：下面的API将依赖于 app.database.get_db，此处仅为示意。
#     pass 

# 确保从正确的路径导入模型和CRUD操作
from app.models.species_models import SpeciesRead
# from app.crud import species_crud # 在实际项目中，这应该是正确的导入路径
# 下面将使用 design.md 中定义的 species_crud 内容，实际应分离到 app.crud.species_crud
import app.crud.species_crud as species_crud # 修正：为了文档内引用方便，暂时如此
from app.database import get_db # 实际项目中，get_db 从 app.database 导入

router = APIRouter(
    prefix="/api/v1/species",  # 所有此路由下的端点都将以此为前缀
    tags=["Species"],          # 在API文档中为此组端点打上 "Species" 标签
)

@router.get("/suggestions", response_model=List[str])
def get_species_suggestions_endpoint(
    *,
    db: Session = Depends(get_db), # 依赖注入数据库会话
    q: str = Query(..., min_length=1, description="搜索词 (可为中文、全拼或拼音首字母)"),
    limit: int = Query(10, gt=0, le=20, description="返回建议结果的最大数量") # gt=0 表示 limit 必须大于0, le=20 表示小于等于20
):
    """
    获取物种中文名搜索建议列表。
    后端将使用查询词 `q` 同时对物种的中文名、中文名全拼、
    以及中文名拼音首字母进行前缀匹配搜索。
    """
    # if db is None: # 使用真实的 get_db 后，此检查可以移除或依赖 FastAPI 的错误处理
    #     raise HTTPException(status_code=503, detail="数据库服务当前不可用 (模拟)。")
    
    # 调用CRUD函数执行搜索逻辑
    species_names_list = species_crud.search_species_names_by_term(db=db, search_term=q, limit=limit)
    return species_names_list

@router.get("/details/{chinese_name}", response_model=SpeciesRead)
def get_species_details_endpoint(
    *,
    db: Session = Depends(get_db), # 依赖注入数据库会话
    chinese_name: str = Path(..., description="要查询物种的精确中文名 (需URL编码若含特殊字符)")
):
    """
    根据物种的精确中文名获取其完整的详细信息。
    """
    # if db is None: # 使用真实的 get_db 后，此检查可以移除或依赖 FastAPI 的错误处理
    #     raise HTTPException(status_code=503, detail="数据库服务当前不可用 (模拟)。")

    # 调用CRUD函数获取物种详情
    species_instance = species_crud.get_species_by_exact_chinese_name(db=db, name_chinese=chinese_name)
    
    if not species_instance:
        # 如果未找到物种，则返回404错误
        raise HTTPException(status_code=404, detail=f"未找到名为 '{chinese_name}' 的物种。")
    return species_instance

# --- 如何在主应用中集成此路由 (示意) ---
# # In app/main.py or your main application file:
# from fastapi import FastAPI
# from app.routers import species as species_router # Assuming this file is app/routers/species.py
# # from app.database import create_db_and_tables # Function to create DB tables on startup
# from fastapi.middleware.cors import CORSMiddleware # 引入 CORS 中间件
#
# app = FastAPI(
#     title="物种信息查询 API",
#     description="提供物种名称建议和详细信息查询功能。"
# )
#
# # 配置 CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], # 允许所有来源，生产环境建议替换为实际的前端域名列表
#     allow_credentials=True,
#     allow_methods=["*"], # 允许所有 HTTP 方法
#     allow_headers=["*"], # 允许所有 HTTP 请求头
# )
#
# @app.on_event("startup")
# def on_startup():
# #     print("Creating database tables if they don't exist...")
# #     create_db_and_tables() # 创建包括 species 在内的所有 SQLModel 表
#     pass # 在实际应用中，此处应调用建表函数
#
# # 包含物种相关的路由
# app.include_router(species_router.router)
#
# # ... 其他应用配置，如CORS等 ...

**IV. 后续步骤概要**

1.  **数据库配置 (`app/database.py`)**:
    * 定义数据库连接URL (例如 SQLite, PostgreSQL, MySQL)。
      ```python
      # app/database.py
      from sqlmodel import create_engine, SQLModel, Session

      DATABASE_URL = "sqlite:///./pokedex.db" # SQLite 数据库文件将在项目根目录下创建
      # 如果使用 PostgreSQL:
      # DATABASE_URL = "postgresql://user:password@host:port/database" 
      # MySQL 类似

      engine = create_engine(DATABASE_URL, echo=True) # echo=True 会打印SQL语句，便于调试

      def create_db_and_tables():
          SQLModel.metadata.create_all(engine)

      def get_db():
          with Session(engine) as session:
              yield session
      ```
    * 创建 SQLModel `engine`。
    * 实现 `create_db_and_tables()` 函数，用于在应用启动时创建所有定义的 SQLModel 表。
    * 实现数据库会话生成器函数 `get_db`，供 FastAPI `Depends` 使用。

2.  **数据导入脚本 (例如 `scripts/import_species_data.py`)**:
    * 读取源 JSON 文件 (如 `物种列表更新.json`)。
    * 对每条记录，使用 `app.models.species_models` 中的 `prepare_species_for_db` （或类似逻辑）来转换数据并生成拼音字段。
    * 将处理后的数据批量存入数据库。注意处理 `name_chinese` 的唯一性约束冲突 (例如，通过查询检查物种是否已存在，若存在则跳过或更新)。
      ```python
      # scripts/import_species_data.py (示意)
      # import json
      # from typing import List, Dict
      # from sqlmodel import Session, select
      # from app.database import engine, get_db # 假设已定义
      # from app.models.species_models import Species, SpeciesCreate, get_pinyin_full, get_pinyin_initials

      # def prepare_species_for_db(raw_data_item: dict) -> Optional[SpeciesCreate]:
      #     # ... (与 design.md 中 III.A 部分的 prepare_species_for_db 函数类似)
      #     # ... (确保返回 SpeciesCreate 实例)
      #     pass # 实际实现

      # def import_data_from_json(json_file_path: str):
      #     with open(json_file_path, 'r', encoding='utf-8') as f:
      #         all_raw_data: List[Dict] = json.load(f)
      
      #     with Session(engine) as session:
      #         new_species_list = []
      #         skipped_count = 0
      #         for raw_item in all_raw_data:
      #             species_data = prepare_species_for_db(raw_item)
      #             if species_data:
      #                 # 检查是否已存在 (按中文名)
      #                 existing_species = session.exec(
      #                     select(Species).where(Species.name_chinese == species_data.name_chinese)
      #                 ).first()
      #                 if existing_species:
      #                     print(f"物种 '{species_data.name_chinese}' 已存在，跳过。")
      #                     skipped_count += 1
      #                     continue
      #                 
      #                 # 如果不存在，则创建新物种对象
      #                 # 注意：Species.model_validate(species_data) 用于从 Pydantic 模型创建 ORM 模型实例
      #                 db_species = Species.model_validate(species_data)
      #                 new_species_list.append(db_species)
      
      #         if new_species_list:
      #             session.add_all(new_species_list)
      #             session.commit()
      #             print(f"成功导入 {len(new_species_list)} 条新物种记录。")
      #         else:
      #             print("没有新的物种记录被导入。")
      #         if skipped_count > 0:
      #             print(f"共跳过 {skipped_count} 条已存在的物种记录。")

      # if __name__ == "__main__":
      #     create_db_and_tables() # 确保表已创建
      #     import_data_from_json("path/to/your/物种列表更新.json") # 替换为实际路径
      ```

3.  **主应用集成 (`app/main.py`)**:
    * 创建 FastAPI 应用实例。
    * 在 `startup` 事件中调用 `create_db_and_tables()`。
    * 使用 `app.include_router()` 注册 `species_router`。
    * 配置 CORS（跨域资源共享）等中间件。
      ```python
      # app/main.py
      from fastapi import FastAPI
      from fastapi.middleware.cors import CORSMiddleware
      from app.routers import species as species_router # 确保 species_router.router 存在
      from app.database import create_db_and_tables, engine # 引入 engine (如果需要直接操作)

      app = FastAPI(
          title="物种信息查询 API",
          description="提供物种名称建议和详细信息查询功能。"
      )

      # 配置 CORS
      app.add_middleware(
          CORSMiddleware,
          allow_origins=["*"], # 生产环境请指定具体来源 e.g., ["http://localhost:3000"]
          allow_credentials=True,
          allow_methods=["GET", "POST"], # 根据需要限定方法
          allow_headers=["*"], # 根据需要限定请求头
      )

      @app.on_event("startup")
      def on_startup():
          print("正在创建数据库表 (如果尚不存在)...")
          create_db_and_tables()
          print("数据库表检查/创建完成。")

      # 包含物种相关的路由
      app.include_router(species_router.router)

      # 可以在这里添加一个根路径的测试端点
      @app.get("/")
      async def root():
          return {"message": "欢迎使用物种信息查询 API"}
      ```

4.  **依赖安装 (`requirements.txt`)**:
    * `fastapi`
    * `uvicorn[standard]` (作为 ASGI 服务器)
    * `sqlmodel`
    * `pypinyin`
    * 相应的数据库驱动 (如 `psycopg2-binary` for PostgreSQL, `mysqlclient` for MySQL; SQLite 通常内置于 Python 标准库，无需额外安装驱动)。
    * (可选) `tqdm` 用于数据导入脚本显示进度。
