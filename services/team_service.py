import json

from sqlalchemy.orm import Session

from database import db_models as db_model
from models import models as pydantic_models
from team_base import TeamBase
from daos.common_dao import CommonDao
from logger import LOGGER
from constants.constraint_constants import TeamConstraints as t_c
from utils import constraint_checks as c_c
from custom_exceptions.constraint_exception import (
    LimitOverflowException,
    ObjectAlreadyPresentException,
    NoDataException
)


class TeamService(TeamBase):
    def __init__(self, db: Session):
        self.db = db
        self.common_dao = CommonDao(self.db)

    def create_team(self, request: str) -> str:
        team_details = json.loads(request)

        team_obj = db_model.Team(
            team_name=team_details['name'],
            description=team_details['description'],
            team_admin=team_details['admin']
        )

        # check if team with same name exists
        temp_team = self.common_dao.get_object(
            object_type=db_model.Team,
            filter_condition=db_model.Team.team_name == team_details['name']
        )

        if temp_team:
            LOGGER.warning("team with same name already present")
            raise ObjectAlreadyPresentException(message="Team with same name already present")
        else:
            if not c_c.check_len_constraint(team_details['name'], t_c.team_name_len.value):
                LOGGER.warning(f"name length is greater than allowed length of: {t_c.team_name_len.value}")
                raise LimitOverflowException(message="name greater than allowed length")

            if not c_c.check_len_constraint(team_details['description'], t_c.team_description_len.value):
                LOGGER.warning(
                    f"description is greater than allowed length of: {t_c.team_description_len.value}"
                )
                raise LimitOverflowException(message="description greater than allowed length")

            team_model = self.common_dao.create_object(team_obj)
            LOGGER.info(f"Team with team name: {team_details['name']} created")

            # convert from sqlalchemy to pydantic model
            pydantic_team_model = pydantic_models.TeamWithUsers.from_orm(team_model)
            return json.dumps(
                {
                    'id': pydantic_team_model.team_id
                }
            )

    def describe_team(self, request: str) -> str:

        # deserialize json
        team_details = json.loads(request)

        team_model = self.common_dao.get_object(
            object_type=db_model.Team,
            filter_condition=db_model.Team.team_id == team_details['id']
        )
        if team_model is None:
            raise NoDataException

        # convert from sqlalchemy to pydantic model
        pydantic_team_model = pydantic_models.TeamWithUsers.from_orm(team_model)

        return json.dumps(
            {
                'name': pydantic_team_model.team_name,
                'description': pydantic_team_model.description,
                'creation_time': str(pydantic_team_model.create_time),
                'admin': pydantic_team_model.team_admin
            }
        )

    def list_teams(self) -> str:
        team_models = self.common_dao.get_objects(
            object_type=db_model.Team
        )

        teams_list = []
        for team_model in team_models:
            pydantic_team_model = pydantic_models.TeamWithUsers.from_orm(team_model)
            teams_list.append(
                {
                    'name': pydantic_team_model.team_name,
                    'display_name': pydantic_team_model.description,
                    'description': str(pydantic_team_model.create_time),
                    'admin': pydantic_team_model.team_admin
                }
            )
        return json.dumps(teams_list)

    def update_team(self, request: str) -> str:
        # deserialize json
        team_update_details = json.loads(request)
        update_payload = {}
        if 'name' in team_update_details['team']:
            update_payload['team_name'] = team_update_details['team']['name']

        if 'description' in team_update_details['team']:
            update_payload['description'] = team_update_details['team']['description']

        if 'admin' in team_update_details['team']:
            update_payload['team_admin'] = team_update_details['team']['admin']

        update_status = self.common_dao.update_object(
            object_type=db_model.Team,
            filter_condition=db_model.Team.team_id == team_update_details['id'],
            update_payload=update_payload
        )

        if update_status == 0:
            LOGGER.warning("could not update the team details")
            raise NoDataException
        else:
            LOGGER.info("Updated team details")
            return json.dumps(
                {
                    'status': update_status
                }
            )

    def add_users_to_team(self, request: str):
        # deserialize json
        users_team_details = json.loads(request)

        team_id = users_team_details['id']
        users = users_team_details['users']

        # check user limit
        # TODO add better logic for checking and enforcing limit
        current_users_list = self.list_team_users(json.dumps({'id': team_id}))

        if len(current_users_list) + len(users) > t_c.max_users_per_team.value:
            raise LimitOverflowException(
                f"Cannot add more than {t_c.max_users_per_team.value} users, "
                f"current users in team: {len(current_users_list)}"
            )

        team_model = self.common_dao.get_object(
            object_type=db_model.Team,
            filter_condition=db_model.Team.team_id == team_id
        )
        if team_model is None:
            raise NoDataException

        for user_id in users:

            user_model = self.common_dao.get_object(
                object_type=db_model.User,
                filter_condition=db_model.User.user_id == user_id
            )
            if user_model is None:
                LOGGER.warning(f"User with user id : {user_id} does not exists")

            LOGGER.info(f"Added user_id: {user_id} to Team: {team_id}")
            team_model.users.append(user_model)

            self.db.add(team_model)
            self.db.commit()

    def list_team_users(self, request: str):
        # deserialize json
        team_details = json.loads(request)

        team_model = self.common_dao.get_object(
            object_type=db_model.Team,
            filter_condition=db_model.Team.team_id == team_details['id']
        )
        if team_model is None:
            raise NoDataException

        # convert from sqlalchemy to pydantic model
        pydantic_team_model = pydantic_models.TeamWithUsers.from_orm(team_model)

        team_users = []
        for user in pydantic_team_model.users:
            team_users.append(
                {
                    'id': user.user_id,
                    'name': user.user_name,
                    'display_name': user.user_display_name
                }
            )
        return json.dumps(team_users)

    def remove_users_from_team(self, request: str):
        # deserialize json
        users_team_details = json.loads(request)

        team_id = users_team_details['id']
        users = users_team_details['users']

        team_model = self.common_dao.get_object(
            object_type=db_model.Team,
            filter_condition=db_model.Team.team_id == team_id
        )
        if team_model is None:
            raise NoDataException

        for user_id in users:

            user_model = self.common_dao.get_object(
                object_type=db_model.User,
                filter_condition=db_model.User.user_id == user_id
            )
            if user_model is None:
                LOGGER.warning(f"User with user id : {user_id} does not exists")

            LOGGER.info(f"Removed user_id: {user_id} from Team: {team_id}")
            team_model.users.remove(user_model)

            self.db.add(team_model)
            self.db.commit()


