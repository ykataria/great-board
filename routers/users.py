import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.user_service import UserService
from custom_exceptions.constraint_exception import NoDataException
from models import user_models
from connect_db import get_db


router = APIRouter(
    prefix="/user",
    tags=["users"]
)


@router.get("/{user_id}", response_model=user_models.UserModel)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return json.loads(UserService(db).describe_user(json.dumps({'id': user_id})))
    except NoDataException:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("", response_model=user_models.UserIdModel)
def create_user(user_model: user_models.UserModel, db: Session = Depends(get_db)):
    return json.loads(UserService(db).create_user(user_model.json()))


@router.get("s", response_model=user_models.UsersListModel)
def get_users(db: Session = Depends(get_db)):
    users_list = json.loads(UserService(db).list_users())
    return {
        'users': users_list
    }


@router.get("/teams/{user_id}", response_model=user_models.UserTeamsModel)
def get_user_teams(user_id: int, db: Session = Depends(get_db)):

    user_teams = json.loads(
        UserService(db).get_user_teams(
            json.dumps({'id': user_id})
        )
    )
    return {
        "teams": user_teams
    }


@router.put("")
def update_user(user_update_model: user_models.UpdateUserModel, db: Session = Depends(get_db)):

    try:
        return json.loads(
            UserService(db).update_user(
                json.dumps(user_update_model.dict())
            )
        )
    except NoDataException:
        raise HTTPException(
            status_code=403, detail="cannot update user"
        )
