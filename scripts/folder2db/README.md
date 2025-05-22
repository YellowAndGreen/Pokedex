# 图鉴式图片管理工具 - 文件夹与数据库转换工具

这个工具包提供了在文件夹结构和图鉴数据库之间进行数据迁移的功能。

## 功能

1. **文件夹导入到数据库** (`folder2db.py`)：扫描指定目录下的分类文件夹，并将图片上传到数据库中。
2. **数据库导出到文件夹** (`db2folder.py`)：从数据库获取所有分类和图片，保存到指定目录。

## 安装依赖

```bash
pip install requests tqdm
```

## 使用方法

### 从文件夹导入到数据库

```bash
python -m scripts.folder2db.folder2db /path/to/categories --api-url http://yourapi.com
```

参数说明：
- `/path/to/categories`：包含分类文件夹的根目录
- `--api-url`：API服务器地址（可选，默认为 http://localhost:8000）
- `--thumbnail`：将每个分类的第一张图片设为缩略图（可选）
- `--verbose`：显示详细日志（可选）
- `--dry-run`：仅测试，不实际上传（可选）

### 从数据库导出到文件夹

```bash
python -m scripts.folder2db.db2folder /path/to/output/directory --api-url http://yourapi.com
```

参数说明：
- `/path/to/output/directory`：导出图片的目标根目录
- `--api-url`：API服务器地址（可选，默认为 http://localhost:8000）
- `--skip-existing`：跳过已存在的文件（可选）
- `--verbose`：显示详细日志（可选）
- `--category`：仅导出指定名称的分类（可选）

## 文件夹结构要求

对于导入功能，需要遵循以下结构：

```
root_directory/
  ├── Category1/
  │   ├── image1.jpg
  │   ├── image2.png
  │   └── ...
  ├── Category2/
  │   ├── image1.jpg
  │   └── ...
  └── ...
```

导出功能会创建相同的结构。

## 示例

### 导入示例

```bash
# 导入图片，并将第一张图片设为类别缩略图
python -m scripts.folder2db.folder2db /home/user/my_categories --thumbnail

# 测试模式，不实际上传
python -m scripts.folder2db.folder2db /home/user/my_categories --dry-run
```

### 导出示例

```bash
# 导出所有分类到指定目录
python -m scripts.folder2db.db2folder /home/user/exported_images

# 仅导出特定分类
python -m scripts.folder2db.db2folder /home/user/exported_images --category "动物"

# 跳过已存在的文件
python -m scripts.folder2db.db2folder /home/user/exported_images --skip-existing
``` 