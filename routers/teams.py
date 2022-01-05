import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.team_service import TeamService
from custom_exceptions.constraint_exception import NoDataException
from models import team_models
from connect_db import get_db


router = APIRouter(
    prefix="/team",
    tags=["teams"]
)


@router.get("/{team_id}", response_model=team_models.TeamModel)
def get_team(team_id: int, db: Session = Depends(get_db)):
    try:
        return json.loads(TeamService(db).describe_team(json.dumps({'id': team_id})))
    except NoDataException:
        raise HTTPException(status_code=404, detail="Team not found")


@router.post("", response_model=team_models.TeamIdModel)
def create_team(team_model: team_models.TeamModel, db: Session = Depends(get_db)):
    return json.loads(TeamService(db).create_team(team_model.json()))


@router.get("s", response_model=team_models.TeamListModel)
def get_teams(db: Session = Depends(get_db)):
    team_list = json.loads(TeamService(db).list_teams())
    return {
        'teams': team_list
    }


@router.put("")
def update_team(team_update_model: team_models.UpdateTeamModel, db: Session = Depends(get_db)):
    try:
        return json.loads(
            TeamService(db).update_team(
                team_update_model.json()
            )
        )
    except NoDataException:
        raise HTTPException(
            status_code=403, detail="cannot update Team"
        )


@router.post("/add_users")
def add_users_to_team(team_user_model: team_models.UpdateUserTeamModel, db: Session = Depends(get_db)):
    try:
        return json.dumps(TeamService(db).add_users_to_team(team_user_model.json()))
    except NoDataException:
        raise HTTPException(
            status_code=404, detail="Cannot find given Team"
        )


@router.post("/remove_users")
def remove_users_from_team(team_user_model: team_models.UpdateUserTeamModel, db: Session = Depends(get_db)):
    try:
        return json.dumps(TeamService(db).remove_users_from_team(team_user_model.json()))
    except NoDataException:
        raise HTTPException(
            status_code=404, detail="Cannot find given Team"
        )


@router.get("/users/{team_id}", response_model=team_models.TeamUsersModel)
def get_team_users(team_id: int, db: Session = Depends(get_db)):
    try:
        team_users = json.loads(
            TeamService(db).list_team_users(
                json.dumps({'id': team_id})
            )
        )
        return {
            "users": team_users
        }
    except NoDataException:
        raise HTTPException(
            status_code=404, detail="Cannot find given Team"
        )
