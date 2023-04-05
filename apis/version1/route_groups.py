from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from db.session import get_db

from db.models.users import User

from apis.version1.route_login import get_current_user_from_token

from db.repository.groups import get_group_by_id
from db.repository.groups import clear_group_users
from db.repository.groups import clear_group_passwords
from db.repository.groups import delete_group_by_id


router = APIRouter()


@router.delete("/api-delete/{id}")
def delete_group(
        id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token)
):
    group_to_delete = get_group_by_id(id=id, db=db)
    if not group_to_delete:
        return {"message": f"Группы с id={id} не существует."}
    if current_user.is_superuser:
        clear_group_users(group=group_to_delete, db=db)
        clear_group_passwords(group=group_to_delete, db=db)
        delete_group_by_id(id=id, db=db)
        return {"message": f"Группа с id={id} успешно удалена."}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недостаточно прав для выполнения данного действия."
    )
