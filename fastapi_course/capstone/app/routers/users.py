from fastapi import APIRouter

from app.dependencies import CurrentUser, DbSession
from app.schemas import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(changes: UserUpdate, user: CurrentUser, db: DbSession):
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
