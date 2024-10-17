from datetime import datetime

from pydantic import BaseModel
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class User(BaseModel):
    """Represents an API response for a user."""

    id: int
    created_at: datetime
    email: str
    username: str

    @staticmethod
    def from_db(user_in_db: "UserInDB") -> "User":
        return User(**user_in_db.model_dump())


class UserCreate(BaseModel):
    """Represents parameters for adding a new user to the system."""

    id: int
    email: str
    username: str


class UserUpdate(BaseModel):
    """Represents parameters for updating a user in the system."""

    username: str = None
    email: str = None


class Metadata(BaseModel):
    """Represents metadata for a collection."""

    count: int


class UserCollection(BaseModel):
    """Represents an API response for a collection of users."""

    meta: Metadata
    users: list[User]


class Message(BaseModel):
    """Represents a public message in a chat."""
    id: int
    chat_id: int
    user: User
    created_at: datetime
    text: str

    @staticmethod
    def from_db(msg_in_db: "MessageInDB") -> "Message":
        return Message(id=msg_in_db.id, chat_id=msg_in_db.chat_id, created_at=msg_in_db.created_at, text=msg_in_db.text, user=User.from_db(msg_in_db.user))


class MessageCollection(BaseModel):
    """Represents an API response for a collection of messages."""
    meta: Metadata
    messages: list[Message]


class UpdateChat(BaseModel):
    """Represents parameters for updating a chat."""
    name: str


class UpdateMessage(BaseModel):
    """Represents parameters for updating a message in a chat."""
    text: str


class ChatMetadata(BaseModel):
    """Represents metadata for a chat."""

    message_count: int
    user_count: int


class Chat(BaseModel):
    """Represents a public chat."""
    id: int
    name: str
    owner: User
    created_at: datetime

    @staticmethod
    def from_db(chat_in_db: "ChatInDB") -> "Chat":
        return Chat(**chat_in_db.model_dump(), owner=User(**chat_in_db.owner.model_dump()))


class ChatResponse(BaseModel):
    """Represents an API response for a chat."""
    meta: ChatMetadata
    chat: Chat
    messages: Optional[list[Message]]
    users: Optional[list[User]]

    @staticmethod
    def from_db(chat_in_db: "ChatInDB", include_messages: bool, include_users: bool) -> "ChatResponse":
        response = ChatResponse(
            chat=Chat(**chat_in_db.model_dump(), owner=User(**chat_in_db.owner.model_dump())),
            meta=ChatMetadata(message_count=len(chat_in_db.messages), user_count=len(chat_in_db.users)),
            messages=None,
            users=None
        )
        if include_messages:
            response.messages = [Message.from_db(msg) for msg in chat_in_db.messages]
        if include_users:
            response.users = [User.from_db(user) for user in chat_in_db.users]
        return response


class ChatCollection(BaseModel):
    """Represents an API response for a collection of chats."""
    meta: Metadata
    chats: list[Chat]


class CreateMessage(BaseModel):
    """Represents parameters for adding a new message to a chat."""
    text: str


class UserChatLinkInDB(SQLModel, table=True):
    """Database model for many-to-many relation of users to chats."""

    __tablename__ = "user_chat_links"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    chat_id: int = Field(foreign_key="chats.id", primary_key=True)


class UserInDB(SQLModel, table=True):
    """Database model for user."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    hashed_password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    chats: list["ChatInDB"] = Relationship(
        back_populates="users",
        link_model=UserChatLinkInDB,
    )


class ChatInDB(SQLModel, table=True):
    """Database model for chat."""

    __tablename__ = "chats"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    owner_id: int = Field(foreign_key="users.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    owner: UserInDB = Relationship()
    users: list[UserInDB] = Relationship(
        back_populates="chats",
        link_model=UserChatLinkInDB,
    )
    messages: list["MessageInDB"] = Relationship(back_populates="chat")


class MessageInDB(SQLModel, table=True):
    """Database model for message."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    user_id: int = Field(foreign_key="users.id")
    chat_id: int = Field(foreign_key="chats.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    user: UserInDB = Relationship()
    chat: ChatInDB = Relationship(back_populates="messages")
