"""Reusable dependencies: who is asking, and what they're allowed to touch.

Every access rule in the API lives in this file. Routes ask for a dependency
by its type alias - `membership: OwnerMembership` - and can't forget a check.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ProjectMember, Task, User
from app.security import decode_access_token

DbSession = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    def unauthorized(detail: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail,
                             headers={"WWW-Authenticate": "Bearer"})

    try:
        user_id = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise unauthorized("Token has expired")
    except jwt.InvalidTokenError:
        raise unauthorized("Could not validate credentials")

    user = db.get(User, user_id)
    if user is None:
        raise unauthorized("Could not validate credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="This account has been deactivated")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# ---- Project access -------------------------------------------------------------
# Not a member -> 404, so outsiders can't even confirm a project exists.
# A member, but the action needs the owner -> 403.

def get_membership(project_id: int, user: CurrentUser, db: DbSession) -> ProjectMember:
    membership = db.get(ProjectMember, (project_id, user.id))
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return membership


Membership = Annotated[ProjectMember, Depends(get_membership)]


def require_owner(membership: Membership) -> ProjectMember:
    if membership.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only the project owner can do this")
    return membership


OwnerMembership = Annotated[ProjectMember, Depends(require_owner)]


def get_task_for_member(task_id: int, user: CurrentUser, db: DbSession) -> Task:
    task = db.get(Task, task_id)
    if task is None or db.get(ProjectMember, (task.project_id, user.id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


MemberTask = Annotated[Task, Depends(get_task_for_member)]


# ---- Paging ---------------------------------------------------------------------

class PageParams(BaseModel):
    skip: int
    limit: int


def pagination(skip: Annotated[int, Query(ge=0)] = 0,
               limit: Annotated[int, Query(ge=1, le=100)] = 20) -> PageParams:
    return PageParams(skip=skip, limit=limit)


Pagination = Annotated[PageParams, Depends(pagination)]
