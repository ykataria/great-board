from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime

from models.common_models import UserModel


class TeamModel(BaseModel):
    name: str
    description: str
    admin: Optional[int] = None
    creation_time: Optional[datetime] = None


class TeamListModel(BaseModel):
    teams: List[TeamModel]


class TeamIdModel(BaseModel):
    id: int


class UpdateTeamModel(TeamIdModel):
    team: TeamModel


class UpdateUserTeamModel(TeamIdModel):
    users: List[int]


class TeamUsersModel(BaseModel):
    users: List[UserModel]
