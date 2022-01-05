import json

from sqlalchemy.orm import Session

from database import db_models as db_model
from models import models as pydantic_models
from user_base import UserBase
from daos.common_dao import CommonDao
from logger import LOGGER
from constants.constraint_constants import UserConstraints as u_c
from utils import constraint_checks as c_c
from custom_exceptions.constraint_exception import (
    LimitOverflowException,
    ObjectAlreadyPresentException,
    NoDataException
)


# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()
#
#
# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()
#
#
# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()


# def create_user(db: Session, user: schemas.UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
#
#
# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()
#
#
# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item

class UserService(UserBase):
    def __init__(self, db: Session):
        self.db = db
        self.common_dao = CommonDao(self.db)

    def describe_user(self, request: str) -> str:

        # deserialize json
        user_details = json.loads(request)

        user_model = self.common_dao.get_object(
            object_type=db_model.User,
            filter_condition=db_model.User.user_id == user_details['id']
        )
        if user_model is None:
            raise NoDataException

        # convert from sqlalchemy to pydantic model
        pydantic_user_model = pydantic_models.UserWithTeamsAndTasks.from_orm(user_model)
        return json.dumps(
            {
                'name': pydantic_user_model.user_name,
                'display_name': pydantic_user_model.user_display_name,
                'creation_time': str(pydantic_user_model.create_time)
            }
        )

    def create_user(self, request: str) -> str:
        # deserialize json
        user_details = json.loads(request)

        user_obj = db_model.User(
            user_name=user_details['name'],
            user_display_name=user_details['display_name']
        )

        # check if user with same name exists
        temp_user = self.common_dao.get_object(
            object_type=db_model.User,
            filter_condition=db_model.User.user_name == user_details['name']
        )

        if temp_user:
            LOGGER.warning("User with same name already present")
            raise ObjectAlreadyPresentException(message="User with same name already present")
        else:
            if not c_c.check_len_constraint(user_details['name'], u_c.user_name_len.value):
                LOGGER.warning(f"name length is greater than allowed length of: {u_c.user_name_len.value}")
                raise LimitOverflowException(message="name greater than allowed length")

            if not c_c.check_len_constraint(user_details['display_name'], u_c.user_display_name_len.value):
                LOGGER.warning(
                    f"display name length is greater than allowed length of: {u_c.user_display_name_len.value}"
                )
                raise LimitOverflowException(message="display name greater than allowed length")

            user_model = self.common_dao.create_object(user_obj)
            LOGGER.info(f"User with user_name: {user_details['name']} created")

            # convert from sqlalchemy to pydantic model
            pydantic_user_model = pydantic_models.UserWithTeamsAndTasks.from_orm(user_model)
            return json.dumps(
                {
                    'id': pydantic_user_model.user_id
                }
            )

    def list_users(self) -> str:
        user_models = self.common_dao.get_objects(
            object_type=db_model.User
        )
        print("----------")
        user_list = []
        for user_model in user_models:
            pydantic_user_model = pydantic_models.UserWithTeamsAndTasks.from_orm(user_model)
            user_list.append(
                {
                    'name': pydantic_user_model.user_name,
                    'display_name': pydantic_user_model.user_display_name,
                    'creation_time': str(pydantic_user_model.create_time)
                }
            )
        return json.dumps(user_list)

    def update_user(self, request: str) -> str:

        # deserialize json
        user_update_details = json.loads(request)
        update_payload = {}
        if 'name' in user_update_details['user']:
            update_payload['user_name'] = user_update_details['user']['name']

        if 'display_name' in user_update_details['user']:
            update_payload['user_display_name'] = user_update_details['user']['display_name']

        update_status = self.common_dao.update_object(
            object_type=db_model.User,
            filter_condition=db_model.User.user_id == user_update_details['id'],
            update_payload=update_payload
        )

        if update_status == 0:
            LOGGER.warning("could not update the given user")
            raise NoDataException
        else:
            LOGGER.info("Updated the user details")
            return json.dumps(
                {
                    'status': update_status
                }
            )

    def get_user_teams(self, request: str) -> str:

        # deserialize json
        user_details = json.loads(request)
        print(user_details)
        user_model = self.common_dao.get_object(
            object_type=db_model.User,
            filter_condition=db_model.Team.team_id == user_details['id']
        )
        if user_model is None:
            return json.dumps(
                []
            )

        # convert from sqlalchemy to pydantic model
        pydantic_user_model = pydantic_models.UserWithTeamsAndTasks.from_orm(user_model)

        user_teams = []
        for team in pydantic_user_model.teams:
            user_teams.append(
                {
                    'id': team.team_id,
                    'name': team.team_name,
                    'description': team.description
                }
            )
        return json.dumps(user_teams)


# if __name__ == '__main__':
#     from database.database import session, engine
#     from database import db_models
#     from database.database import session
#
#     db_models.Base.metadata.create_all(bind=engine)
#
#     db = session()
#     user_service = UserService(db)
#
#     print(
#         user_service.get_user_teams(json.dumps(
#             {
#                 'id': 1
#             }
#         ))
#     )
