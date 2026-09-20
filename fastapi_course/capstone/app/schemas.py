"""The shapes of data coming into and going out of the API."""

from datetime import date, datetime
from typing import ClassVar, Literal, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

TaskStatus = Literal["todo", "in_progress", "done"]
Priority = Literal["low", "medium", "high"]
Role = Literal["owner", "member"]


class ORMModel(BaseModel):
    """Base for response schemas that are built from database objects."""
    model_config = ConfigDict(from_attributes=True)


class PartialUpdate(BaseModel):
    """Base for PATCH bodies.

    Every field is optional. But a client sending an explicit null for a
    column that can't be empty would crash the database write, so each
    subclass lists those fields in `non_nullable`.
    """
    # ClassVar: a setting for the class itself, not a field clients can send.
    non_nullable: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode="after")
    def reject_nulls_for_required_columns(self) -> Self:
        for name in self.non_nullable:
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} can't be null")
        return self


# ---- Paging -------------------------------------------------------------------
# A GENERIC model: Page[TaskOut] is a page of tasks, Page[ProjectOut] would be a
# page of projects. ItemT is a placeholder that gets filled in where it's used.

class Page[ItemT](BaseModel):
    total: int
    skip: int
    limit: int
    items: list[ItemT]


# ---- Users and auth --------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=100)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)


class UserOut(ORMModel):
    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ---- Projects ------------------------------------------------------------------

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)


class ProjectUpdate(PartialUpdate):
    non_nullable = ("name", "description")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)


class ProjectOut(ORMModel):
    id: int
    name: str
    description: str
    created_at: datetime


class MemberOut(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str | None
    role: Role


class ProjectDetail(ProjectOut):
    members: list[MemberOut]


class MemberAdd(BaseModel):
    email: EmailStr


# ---- Tasks ---------------------------------------------------------------------

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    priority: Priority = "medium"
    due_date: date | None = None
    assignee_id: int | None = None


class TaskUpdate(PartialUpdate):
    non_nullable = ("title", "description", "status", "priority")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = None
    priority: Priority | None = None
    due_date: date | None = None          # null is allowed: it clears the due date
    assignee_id: int | None = None        # null is allowed: it unassigns the task


class TaskOut(ORMModel):
    id: int
    project_id: int
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    due_date: date | None
    assignee_id: int | None
    created_by_id: int
    created_at: datetime
    updated_at: datetime
