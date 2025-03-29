from sqlalchemy.orm import Session

from service.db import get_db
from service.users.models.user import UserDB
from service.users.scemas.user import UserCreate
from service.users.utils import hash_password


class UserService:

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> UserDB:
        hashed_pw = hash_password(user_data.password)
        user = UserDB(username=user_data.username, password=hashed_pw)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str):
        return self.db.query(UserDB).filter(UserDB.username == username).first()

    @staticmethod
    def insert_default_users():
        db: Session = next(get_db())
        user_service = UserService(db)
        users = user_service.get_user_by_username("admin")
        if users is None:
            admin_user = UserDB(
                username="admin",
                password="password",
            )
            user_service.create_user(admin_user)

        users = user_service.get_user_by_username("hello")
        if users is None:
            hello_user = UserDB(
                username="hello",
                password="world",
            )
            user_service.create_user(hello_user)
