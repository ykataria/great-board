from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime


class BoardModel(BaseModel):
    name: str
    description: Optional[str]
    team_id: Optional[int]
    creation_time: Optional[datetime] = None


class TaskModel(BaseModel):
    title: str
    description: str
    board_id: Optional[int]
    user_id: Optional[int]
    creation_time: Optional[datetime] = None


class BoardIdModel(BaseModel):
    id: int


class TaskIdModel(BaseModel):
    id: int


class UpdateTaskModel(BaseModel):
    id: int
    status: str


class BoardListModel(BoardIdModel):
    name: str
    status: str
    tasks: List[int]


class TeamBoardListModel(BaseModel):
    boards: List[BoardListModel]


