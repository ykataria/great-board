from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime


class UserModel(BaseModel):
    name: str
    display_name: Optional[str]
    creation_time: Optional[datetime] = None


class TeamModel(BaseModel):
    name: str
    description: str
    creation_time: Optional[datetime] = None
    admin: Optional[int] = None