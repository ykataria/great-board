import json
from datetime import datetime
from sqlalchemy.orm import Session

from database import db_models as db_model
from models import models as pydantic_models
from project_board_base import ProjectBoardBase
from daos.common_dao import CommonDao
from logger import LOGGER
from constants.constraint_constants import BoardAndTaskConstraints as b_c
from utils import constraint_checks as c_c
from utils import export_board
from custom_exceptions.constraint_exception import (
    LimitOverflowException,
    ObjectAlreadyPresentException,
    NoDataException,
    ConstraintViolationException
)


class BoardTaskService(ProjectBoardBase):

    def __init__(self, db: Session):
        self.db = db
        self.common_dao = CommonDao(self.db)

    def create_board(self, request: str) -> str:
        # deserialize json
        board_details = json.loads(request)

        board_obj = db_model.Board(
            board_name=board_details['name'],
            description=board_details['description'],
            board_team_id=board_details['team_id'],
            board_status='OPEN'
        )

        # check if board with same name exists
        temp_board = self.common_dao.get_object(
            object_type=db_model.Board,
            filter_condition=db_model.Board.board_name == board_details['name']
        )

        if temp_board:
            LOGGER.warning("Board with same name already present")
            raise ObjectAlreadyPresentException(message="Board with same name already present")
        else:
            if not c_c.check_len_constraint(board_details['name'], b_c.board_name_len.value):
                LOGGER.warning(f"Board name length is greater than allowed length of: {b_c.board_name_len.value}")
                raise LimitOverflowException(message="board name greater than allowed length")

            if not c_c.check_len_constraint(board_details['description'], b_c.board_description_len.value):
                LOGGER.warning(
                    f"description length is greater than allowed length of: {b_c.board_description_len.value}"
                )
                raise LimitOverflowException(message="description greater than allowed length")

            board_model = self.common_dao.create_object(board_obj)
            LOGGER.info(f"board with board_name: {board_details['name']} created")

            # convert from sqlalchemy to pydantic model
            pydantic_board_model = pydantic_models.BoardWithTasks.from_orm(board_model)
            return json.dumps(
                {
                    'id': pydantic_board_model.board_id
                }
            )

    def add_task(self, request: str) -> str:
        # deserialize json
        task_details = json.loads(request)

        task_obj = db_model.Task(
            task_title=task_details['title'],
            description=task_details['description'],
            board_id=task_details['board_id'],
            task_assign_id=task_details['user_id'],
            task_status='OPEN'
        )

        # check if board with same name exists
        temp_task = self.common_dao.get_object(
            object_type=db_model.Task,
            filter_condition=db_model.Task.task_title == task_details['title']
        )

        if temp_task:
            LOGGER.warning("Task with same title already present")
            raise ObjectAlreadyPresentException(message="Task with same title already present")
        else:
            if not c_c.check_len_constraint(task_details['title'], b_c.task_title_len.value):
                LOGGER.warning(f"Task title length is greater than allowed length of: {b_c.task_title_len.value}")
                raise LimitOverflowException(message="Task title greater than allowed length")

            if not c_c.check_len_constraint(task_details['description'], b_c.task_description_len.value):
                LOGGER.warning(
                    f"description length is greater than allowed length of: {b_c.task_description_len.value}"
                )
                raise LimitOverflowException(message="description greater than allowed length")

            task_model = self.common_dao.create_object(task_obj)
            LOGGER.info(f"Task with title: {task_details['title']} created")

            # convert from sqlalchemy to pydantic model
            pydantic_task_model = pydantic_models.TaskBase.from_orm(task_model)
            return json.dumps(
                {
                    'id': pydantic_task_model.task_id
                }
            )

    def list_boards(self, request: str) -> str:
        # deserialize json
        board_details = json.loads(request)

        # fetch boards list
        board_models = self.db.query(db_model.Board).\
            filter(db_model.Board.board_team_id == board_details['id']).all()

        board_list = []
        for board in board_models:
            pydantic_board_model = pydantic_models.BoardWithTasks.from_orm(board)
            board_list.append(
                {
                    'id': pydantic_board_model.board_id,
                    'name': pydantic_board_model.board_name,
                    'status': pydantic_board_model.board_status,
                    'tasks': [task.task_id for task in pydantic_board_model.tasks]
                }
            )

        return json.dumps(board_list)

    def update_task_status(self, request: str):
        # deserialize json
        task_details = json.loads(request)

        update_payload = {
            'task_status': task_details['status']
        }

        update_status = self.common_dao.update_object(
            object_type=db_model.Task,
            filter_condition=db_model.Task.task_id == task_details['id'],
            update_payload=update_payload
        )

        if update_status == 0:
            LOGGER.warning("could not update task status")
            raise NoDataException
        else:
            LOGGER.info("Updated task status")
            return json.dumps(
                {
                    'status': update_status
                }
            )

    def close_board(self, request: str) -> str:
        # deserialize json
        board_details = json.loads(request)

        board_model = self.common_dao.get_object(
            object_type=db_model.Board,
            filter_condition=db_model.Board.board_id == board_details['id']
        )

        if board_model is None:
            raise NoDataException

        # check each task status
        LOGGER.info(f"Checking status of tasks for the Board: {board_model.board_name}")
        for task in board_model.tasks:
            if task.task_status != "COMPLETE":
                LOGGER.warning(f"Status of Task: {task.task_title} not COMPLETE, current Status: {task.task_status}")
                raise ConstraintViolationException(f"Status Task : {task.task_title} not COMPLETE")
            LOGGER.info(f"Status os task: {task.task_title} = {task.task_status}")

        # update status of Board to CLOSED
        update_payload = {
            'board_status': 'CLOSED',
            'board_end_time': datetime.now()
        }

        update_status = self.common_dao.update_object(
            object_type=db_model.Board,
            filter_condition=db_model.Board.board_id == board_details['id'],
            update_payload=update_payload
        )

        if update_status == 0:
            LOGGER.warning("could not update the board status")
            raise NoDataException
        else:
            LOGGER.info("Successfully updated board status")
            return json.dumps(
                {
                    'status': update_status
                }
            )

    def export_board(self, request: str) -> str:
        # deserialize json
        board_details = json.loads(request)

        # fetch board model
        board_model = self.common_dao.get_object(
            object_type=db_model.Board,
            filter_condition=db_model.Board.board_id == board_details['id']
        )

        if board_model is None:
            raise NoDataException

        data = self.db.query(
            db_model.User,
            db_model.Team,
            db_model.Task
        ).filter(
            db_model.User.user_id == db_model.Task.task_assign_id
        ).filter(
            db_model.Team.team_id == board_model.board_team_id
        ).filter(
            db_model.Task.board_id == board_model.board_id
        ).all()

        if len(data) == 0:
            LOGGER.warning(f"No Board data to export")
            raise NoDataException

        task_details = []
        export_details = {
            'board_name': board_model.board_name,
            'board_description': board_model.description,
            'board_status': board_model.board_status,
            'team_name': data[0].Team.team_name
        }

        for row in data:
            user_model = row.User
            task_model = row.Task

            task_details.append(
                {
                    "task_title": task_model.task_title,
                    "task_description": task_model.description,
                    "user_display_name": user_model.user_display_name,
                    "task_status": task_model.task_status
                }
            )

        export_details['task_details'] = task_details
        try:
            file_name = export_board.export_project_board(export_details)

            return json.dumps({'out_file': file_name})
        except IOError as e:
            LOGGER.error("Could not export board due to following error: " + e)
            raise
