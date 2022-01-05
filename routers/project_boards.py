import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.board_task_service import BoardTaskService
from custom_exceptions.constraint_exception import NoDataException, ConstraintViolationException
from models import board_models
from connect_db import get_db


router = APIRouter(
    prefix="/board",
    tags=["boards"]
)


@router.post("", response_model=board_models.BoardIdModel)
def create_board(board_model: board_models.BoardModel, db: Session = Depends(get_db)):
    return json.loads(BoardTaskService(db).create_board(board_model.json()))


@router.post("/task", response_model=board_models.TaskIdModel)
def create_and_add_task(task_model: board_models.TaskModel, db: Session = Depends(get_db)):
    return json.loads(
        BoardTaskService(db).add_task(
            task_model.json()
        )
    )


@router.put("/task")
def update_task_status(task_update_model: board_models.UpdateTaskModel, db: Session = Depends(get_db)):
    try:
        return json.loads(
            BoardTaskService(db).update_task_status(
                task_update_model.json()
            )
        )
    except NoDataException:
        raise HTTPException(
            status_code=403, detail="cannot update task status"
        )


@router.get("s/{team_id}", response_model=board_models.TeamBoardListModel)
def get_team_boards(team_id: int, db: Session = Depends(get_db)):
    board_list = json.loads(
        BoardTaskService(db).list_boards(json.dumps({'id': team_id}))
    )

    return {
        'boards': board_list
    }


@router.get("/close/{board_id}")
def close_board(board_id: int, db: Session = Depends(get_db)):
    try:
        return json.loads(
            BoardTaskService(db).close_board(
                json.dumps(
                    {'id': board_id}
                )
            )
        )
    except NoDataException:
        raise HTTPException(
            status_code=404, detail="Board Not found"
        )
    except ConstraintViolationException:
        raise HTTPException(
            status_code=403, detail="Tasks should have COMPLETE status"
        )


@router.get("/export")
def export_board(board_id: int, db: Session = Depends(get_db)):
    try:
        return json.loads(
            BoardTaskService(db).export_board(json.dumps({'id': board_id}))
        )
    except NoDataException:
        raise HTTPException(
            status_code=404, detail="Board Not found"
        )
    except Exception:
        raise HTTPException(
            status_code=500, detail="Some server error"
        )