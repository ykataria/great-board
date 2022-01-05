from typing import Union, Any, List, Dict
from sqlalchemy.orm import Session
from database import db_models as db_model


class CommonDao:
    def __init__(self, db: Session):
        self.db = db

    def get_object(
            self,
            object_type: Union[db_model.User, db_model.Team, db_model.Board, db_model.Task],
            filter_condition: Any
    ) -> Union[db_model.Team, db_model.User, db_model.Board, db_model.Task]:
        """returns object based on condition passed
        :param object_type: type of the object
        :type object_type: Union[db_model.User, db_model.Team, db_model.Board, db_model.Task]
        :param filter_condition: filter condition
        :type filter_condition:
        """
        return self.db.query(object_type).filter(filter_condition).first()

    def create_object(
            self,
            object_payload: Union[db_model.User, db_model.Team, db_model.Board, db_model.Task]
    ) -> Union[db_model.Team, db_model.User, db_model.Board, db_model.Task]:
        """creates Object in DB based on the data passed
        :param object_payload:
        :type object_payload: Union[db_model.User, db_model.Team, db_model.Board, db_model.Task]
        """
        self.db.add(object_payload)
        self.db.commit()
        self.db.refresh(object_payload)
        return object_payload

    def get_objects(
            self,
            object_type: Union[db_model.User, db_model.Team, db_model.Board, db_model.Task],
    ) -> Union[List[db_model.Team], List[db_model.User], List[db_model.Board], List[db_model.Task]]:
        """ get list of object based
        :param object_type: object to fetch
        :type object_type: db_model.Board, db_model.Task
        :return: list of objects
        :rtype:
        """
        return self.db.query(object_type).all()

    def update_object(
            self,
            object_type: Union[db_model.User, db_model.Team, db_model.Board, db_model.Task],
            filter_condition: Any,
            update_payload: Dict[str, str]
    ):
        """Update object by passing object, filter condition and payload
        :param object_type:
        :type object_type: Union[db_model.User, db_model.Team, db_model.Board, db_model.Task]
        :param filter_condition:
        :type filter_condition: Any
        :param update_payload:
        :type update_payload: Dict[str, str]
        :return: status (0 or 1)
        :rtype: into
        """
        status = self.db.query(object_type).filter(filter_condition).update(update_payload)
        self.db.commit()
        return status
