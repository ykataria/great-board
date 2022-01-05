from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime

from models.common_models import TeamModel


class UserModel(BaseModel):
    name: str
    display_name: Optional[str]
    creation_time: Optional[datetime] = None


class UsersListModel(BaseModel):
    users: List[UserModel]


class CreateUserModel(BaseModel):
    name: str
    display_name: str


class UserIdModel(BaseModel):
    id: int


class UpdateUserModel(UserIdModel):
    user: UserModel


class UserTeamsModel(BaseModel):
    teams: List[TeamModel]
