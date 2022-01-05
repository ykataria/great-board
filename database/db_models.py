from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import func, Table

from database.database import Base


user_team_association = Table(
    "users_to_teams", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.user_id")),
    Column("team_id", Integer, ForeignKey("teams.team_id")),
)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    user_name = Column(String(64), unique=True, index=True, nullable=False)
    user_display_name = Column(String(64))
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"User Model: {self.user_name}"

    # relationships
    tasks = relationship("Task", backref="user")
    teams = relationship("Team", secondary=user_team_association, back_populates="users")


class Team(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    team_name = Column(String(64), unique=True, index=True, nullable=False)
    description = Column(String(128))
    team_admin = Column(Integer, ForeignKey("users.user_id"))
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"Team Model: {self.team_name}"

    # relationships
    users = relationship("User", secondary=user_team_association, back_populates="teams")


class Board(Base):
    __tablename__ = "boards"

    board_id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    board_name = Column(String(64), unique=True, index=True, nullable=False)
    description = Column(String(128))
    board_team_id = Column(Integer, ForeignKey("teams.team_id"))
    board_status = Column(String(10))
    board_end_time = Column(DateTime)
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"Board Model: {self.board_name}"

    # relationships
    tasks = relationship("Task", backref="board")


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    task_title = Column(String(64), unique=True, index=True, nullable=False)
    description = Column(String(128))
    board_id = Column(Integer, ForeignKey("boards.board_id"))
    task_assign_id = Column(Integer, ForeignKey("users.user_id"))
    task_status = Column(String(20))
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"Board Model: {self.task_title}"

