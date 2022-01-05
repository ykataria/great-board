from typing import List
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from database import db_models

UserBase = sqlalchemy_to_pydantic(db_models.User)
TeamBase = sqlalchemy_to_pydantic(db_models.Team)
TaskBase = sqlalchemy_to_pydantic(db_models.Task)
BoardBase = sqlalchemy_to_pydantic(db_models.Board)


class UserWithTeamsAndTasks(UserBase):
    teams: List[TeamBase]
    tasks: List[TaskBase]


class TeamWithUsers(TeamBase):
    users: List[UserBase]


class BoardWithTasks(BoardBase):
    tasks: List[TaskBase]


class TaskWithUsers(TaskBase):
    user: List[UserBase]

