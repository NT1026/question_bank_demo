from sqlalchemy.orm import Mapped

from models.base import Base, BaseType


class User(Base):
    __tablename__ = "User"
    id: Mapped[BaseType.uuid]
    username: Mapped[BaseType.str_10]
    # password: Mapped[BaseType.hashed_password]
    password: Mapped[BaseType.str_10]
    name: Mapped[BaseType.str_10]
    role: Mapped[BaseType.str_10]
    created_at: Mapped[BaseType.datetime]

    def __init__(
        self,
        id: str,
        username: str,
        password: str,
        name: str,
        role: str,
        created_at,
    ):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.role = role
        self.created_at = created_at

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, password={self.password}, name={self.name}, role={self.role}, created_at={self.created_at})"
