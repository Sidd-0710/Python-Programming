from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.dependencies import CurrentUser, DbSession, MemberTask, Membership, Pagination
from app.models import ProjectMember, Task
from app.schemas import Page, Priority, TaskCreate, TaskOut, TaskStatus, TaskUpdate

router = APIRouter(tags=["tasks"])

PRIORITY_ORDER = case({"high": 0, "medium": 1, "low": 2}, value=Task.priority)


def ensure_assignee_is_member(db: Session, project_id: int, assignee_id: int | None) -> None:
    if assignee_id is not None and db.get(ProjectMember, (project_id, assignee_id)) is None:
        raise HTTPException(status_code=422,
                            detail="The assignee must be a member of the project")


@router.post("/projects/{project_id}/tasks", response_model=TaskOut,
             status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, membership: Membership, user: CurrentUser, db: DbSession):
    ensure_assignee_is_member(db, membership.project_id, data.assignee_id)
    task = Task(**data.model_dump(), project_id=membership.project_id, created_by_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/projects/{project_id}/tasks", response_model=Page[TaskOut])
def list_tasks(
    membership: Membership,
    db: DbSession,
    page: Pagination,
    # The client writes ?status=done, but `status` is already taken in this file
    # by fastapi's status module - so the parameter has another name, and an alias.
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    priority: Priority | None = None,
    assignee_id: int | None = None,
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    overdue: bool = False,
    sort: Literal["newest", "due_date", "priority"] = "newest",
):
    statement = select(Task).where(Task.project_id == membership.project_id)
    if task_status is not None:
        statement = statement.where(Task.status == task_status)
    if priority is not None:
        statement = statement.where(Task.priority == priority)
    if assignee_id is not None:
        statement = statement.where(Task.assignee_id == assignee_id)
    if q is not None:
        statement = statement.where(Task.title.ilike(f"%{q}%"))
    if overdue:
        statement = statement.where(Task.due_date < date.today(), Task.status != "done")

    total = db.scalar(select(func.count()).select_from(statement.subquery()))

    order_by = {
        "newest": [Task.id.desc()],
        "due_date": [Task.due_date.asc().nulls_last(), Task.id],
        "priority": [PRIORITY_ORDER, Task.id],
    }[sort]
    # *order_by unpacks the list, so order_by(*[a, b]) is order_by(a, b)
    statement = statement.order_by(*order_by).offset(page.skip).limit(page.limit)

    return {"total": total, "skip": page.skip, "limit": page.limit,
            "items": db.scalars(statement).all()}


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task: MemberTask):
    return task


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(changes: TaskUpdate, task: MemberTask, db: DbSession):
    updates = changes.model_dump(exclude_unset=True)
    if "assignee_id" in updates:
        ensure_assignee_is_member(db, task.project_id, updates["assignee_id"])
    for field, value in updates.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task: MemberTask, user: CurrentUser, db: DbSession):
    membership = db.get(ProjectMember, (task.project_id, user.id))
    if membership.role != "owner" and task.created_by_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only the project owner or the task's creator can delete it")
    db.delete(task)
    db.commit()
