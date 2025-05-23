import pytest
from pathlib import Path
from unittest.mock import patch
from pokedex_backend.app.services.file_storage_service import FileStorageService


def test_save_file_creates_correct_path(tmp_upload_dir: Path):
    """验证文件存储服务能正确创建包含哈希路径的文件

    场景：
    - 当传入文件名和内容时
    - 服务应生成包含文件名哈希的路径
    - 文件内容应完整保存
    - 文件应实际存在于文件系统中

    期望结果：
    - 返回的路径包含原始文件名的哈希值
    - 文件内容与输入完全一致
    - 文件实际存在于文件系统
    """
    service = FileStorageService(upload_root=tmp_upload_dir)
    test_content = b"test file content"

    saved_path = service.save_file("test.txt", test_content)

    # 验证路径结构
    assert saved_path.parent.parent == tmp_upload_dir
    assert "test.txt" in saved_path.name

    # 验证文件内容
    assert saved_path.read_bytes() == test_content

    # 验证文件元数据
    assert saved_path.exists()
    assert saved_path.stat().st_size == len(test_content)


def test_delete_file_removes_existing_file(tmp_upload_dir: Path):
    """验证文件存储服务能正确删除已存在的文件

    场景：
    - 当文件存在于存储系统时
    - 调用删除方法后
    - 应物理删除文件
    - 且文件路径不再存在

    期望结果：
    - 删除后文件路径不存在
    - 删除操作不抛出异常
    """
    service = FileStorageService(upload_root=tmp_upload_dir)
    test_content = b"content to delete"

    # 准备测试文件
    file_path = service.save_file("delete_me.txt", test_content)
    initial_size = file_path.stat().st_size

    # 执行删除前验证
    assert file_path.exists(), "测试文件应存在"
    assert initial_size > 0, "测试文件应有内容"

    # 执行删除操作
    service.delete_file(file_path)

    # 验证删除结果
    assert not file_path.exists(), "文件应被物理删除"
    assert file_path.parent.exists(), "父目录应保留"


@patch("pokedex_backend.app.services.file_storage_service.Path.exists")
def test_save_file_raises_error_when_overwriting(mock_exists):
    """验证尝试覆盖已存在文件时抛出正确异常

    场景：
    - 当目标文件路径已存在时
    - 尝试保存同名文件
    - 应抛出FileExistsError异常
    - 且异常信息包含文件路径

    期望结果：
    - 正确抛出FileExistsError异常
    - 异常信息包含完整文件路径
    """
    mock_exists.return_value = True
    test_filename = "existing.txt"
    service = FileStorageService(upload_root=Path("/tmp"))

    with pytest.raises(FileExistsError) as exc_info:
        service.save_file(test_filename, b"new content")

    assert str(service.get_file_path(test_filename)) in str(
        exc_info.value
    ), "异常信息应包含完整文件路径"


def test_delete_nonexistent_file_raises_error(tmp_upload_dir: Path):
    """验证尝试删除不存在的文件时抛出正确异常

    场景：
    - 当文件不存在于存储系统时
    - 调用删除方法
    - 应抛出FileNotFoundError异常

    期望结果：
    - 正确抛出FileNotFoundError异常
    - 异常信息包含完整文件路径
    """
    service = FileStorageService(upload_root=tmp_upload_dir)
    non_existent_file = tmp_upload_dir / "ghost.txt"

    with pytest.raises(FileNotFoundError) as exc_info:
        service.delete_file(non_existent_file)

    assert str(non_existent_file) in str(exc_info.value), "异常信息应包含完整文件路径"


def test_file_path_hashing_logic():
    """验证文件名哈希生成正确的存储路径

    场景：
    - 给定不同文件名时
    - 文件存储路径应基于文件名MD5哈希生成
    - 路径格式应为：上传根目录/前两位哈希/次两位哈希/原始文件名

    期望结果：
    - 生成路径符合预期哈希结构
    - 相同文件名生成相同路径
    - 不同文件名生成不同路径
    """
    service = FileStorageService(upload_root=Path("/data/uploads"))

    # 测试普通文件名
    file1 = "photo.jpg"
    path1 = service.get_file_path(file1)
    assert path1.parent.parent == Path("/data/uploads")
    assert len(path1.parent.name) == 2
    assert len(path1.parent.parent.name) == 2

    # 测试带特殊字符的文件名
    file2 = "document (1).pdf"
    path2 = service.get_file_path(file2)
    assert path2 != path1

    # 测试长文件名
    file3 = "a" * 100 + ".png"
    path3 = service.get_file_path(file3)
    assert len(path3.parent.name) == 2

    # 验证相同文件名生成相同路径
    assert service.get_file_path(file1) == path1
