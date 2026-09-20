from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DbSession, Membership, OwnerMembership
from app.models import Project, ProjectMember, Task, User
from app.schemas import (
    MemberAdd,
    MemberOut,
    ProjectCreate,
    ProjectDetail,
    ProjectOut,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def to_detail(project: Project) -> ProjectDetail:
    members = sorted(project.members, key=lambda m: (m.role != "owner", m.user_id))
    return ProjectDetail(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        members=[MemberOut(user_id=m.user_id, email=m.user.email,
                           full_name=m.user.full_name, role=m.role) for m in members],
    )


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, user: CurrentUser, db: DbSession):
    project = Project(**data.model_dump())
    project.members.append(ProjectMember(user_id=user.id, role="owner"))
    db.add(project)
    db.commit()
    db.refresh(project)
    return to_detail(project)


@router.get("", response_model=list[ProjectOut])
def list_my_projects(user: CurrentUser, db: DbSession):
    statement = (select(Project).join(Project.members)
                 .where(ProjectMember.user_id == user.id).order_by(Project.id))
    return db.scalars(statement).all()


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(membership: Membership):
    return to_detail(membership.project)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(changes: ProjectUpdate, membership: OwnerMembership, db: DbSession):
    project = membership.project
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(membership: OwnerMembership, db: DbSession):
    db.delete(membership.project)          # cascades to its members and tasks
    db.commit()


# ---- Members --------------------------------------------------------------------

@router.post("/{project_id}/members", response_model=MemberOut,
             status_code=status.HTTP_201_CREATED)
def add_member(data: MemberAdd, membership: OwnerMembership, db: DbSession):
    new_user = db.scalar(select(User).where(User.email == data.email.lower()))
    if new_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user with that email")
    if db.get(ProjectMember, (membership.project_id, new_user.id)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="That user is already a member")
    db.add(ProjectMember(project_id=membership.project_id, user_id=new_user.id, role="member"))
    db.commit()
    return MemberOut(user_id=new_user.id, email=new_user.email,
                     full_name=new_user.full_name, role="member")


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(user_id: int, membership: OwnerMembership, db: DbSession):
    target = db.get(ProjectMember, (membership.project_id, user_id))
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if target.role == "owner":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The project owner can't be removed")

    # Someone who has left the project shouldn't keep tasks in it.
    assigned = select(Task).where(Task.project_id == membership.project_id,
                                  Task.assignee_id == user_id)
    for task in db.scalars(assigned):
        task.assignee_id = None

    db.delete(target)
    db.commit()
