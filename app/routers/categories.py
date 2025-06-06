from fastapi import HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uuid
from app.crud import category as category_crud
from app.database import get_session


async def delete_category(
    *, session: Session = Depends(get_session), category_id: uuid.UUID
):
    """
    删除指定ID的类别。

    重要提示:
    此操作会级联删除类别下的所有图片记录及其对应的物理文件。
    在执行删除前，会首先检查类别是否存在。
    """
    db_category = category_crud.get_category_by_id(
        session=session, category_id=category_id
    )
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="类别未找到")

    await category_crud.delete_category(session=session, category_id=category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
