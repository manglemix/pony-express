from datetime import datetime
from random import randint
from typing import Sequence
from sqlmodel import Session, SQLModel, create_engine, select, insert, delete

from backend.entities import (
    ChatInDB,
    CreateMessage,
    MessageInDB,
    UpdateChat,
    UpdateMessage,
    UserInDB,
    UserCreate,
)

engine = create_engine(
    "sqlite:///backend/pony_express.db",
    echo=True,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


#   -------- users --------   #


def get_all_users(session: Session) -> Sequence[UserInDB]:
    """
    Retrieve all users from the database.

    :return: ordered list of users
    """

    return session.exec(select(UserInDB)).all()


def create_user(session: Session, user_create: UserCreate) -> UserInDB:
    """
    Create a new user in the database.

    :param user_create: attributes of the user to be created
    :return: the newly created user
    """

    user = UserInDB(
        created_at=datetime.now(),
        **user_create.model_dump(),
    )
    session.exec(insert(UserInDB).values(**user.model_dump()))
    return user


def get_user_by_id(session: Session, user_id: str) -> UserInDB:
    """
    Retrieve an user from the database.

    :param user_id: id of the user to be retrieved
    :return: the retrieved user
    """

    user = session.exec(select(UserInDB).where(UserInDB.id == user_id)).first()
    if user is None:
        raise KeyError
    return user


def delete_user(session: Session, user_id: str):
    """
    Delete an user from the database.

    :param user_id: the id of the user to be deleted
    """

    session.exec(delete(UserInDB).where(UserInDB.id == user_id))


def get_user_chats(session: Session, user_id: str) -> list[ChatInDB]:
    """
    Gets all the chats that the user is in

    :param user_id: the id of the user to be scan
    """

    user = get_user_by_id(session, user_id)
    return [chat for chat in get_all_chats(session) if user in chat.users]


#   -------- chats --------   #


def get_all_chats(session: Session) -> Sequence[ChatInDB]:
    """
    Retrieve all chats from the database.

    :return: ordered list of chats
    """

    return session.exec(select(ChatInDB)).all()


def get_chat_by_id(session: Session, chat_id: int) -> ChatInDB:
    """
    Retrieve a chat from the database.

    :param chat_id: id of the chat to be retrieved
    :return: the retrieved chat
    """

    chat = session.exec(select(ChatInDB).where(ChatInDB.id == chat_id)).first()
    if chat is None:
        raise KeyError
    return chat


def update_chat(session: Session, chat_id: int, chat_update: UpdateChat) -> ChatInDB:
    """
    Update a chat in the database.

    :param chat_id: id of the chat to be updated
    :param chat_update: attributes to be updated on the chat
    :return: the updated chat
    """

    chat = get_chat_by_id(session, chat_id)
    chat.name = chat_update.name
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat


def delete_chat(session: Session, chat_id: int):
    """
    Delete a chat from the database.

    :param chat_id: the id of the chat to be deleted
    """

    session.exec(delete(ChatInDB).where(ChatInDB.id == chat_id))


def create_message(session: Session, chat_id: int, message: CreateMessage, user: UserInDB) -> MessageInDB:
    while True:
        chat = get_chat_by_id(session, chat_id)
        msg = MessageInDB(id=randint(1, 100000000), text=message.text, user_id=user.id, chat_id=chat.id, created_at=datetime.now(), user=user, chat=chat)
        chat.messages.append(msg)
        if user not in chat.users:
            chat.users.append(user)
        session.add(chat)
        try:
            session.commit()
        except Exception as e:
            if not hasattr(e, "args"):
                raise e
            err: str = e.args[0]
            if "UNIQUE constraint failed: messages.id" not in err:
                raise e
            continue

        session.refresh(chat)
        return msg


def get_msg_by_id(session: Session, chat_id: int, msg_id: str) -> MessageInDB:
    """
    Retrieve a message from the database.

    :param msg_id: id of the chat to be retrieved
    :return: the retrieved message
    """

    msgs = session.exec(select(MessageInDB).where(MessageInDB.id == msg_id)).all()
    if len(msgs) == 0:
        raise KeyError
    
    for msg in msgs:
        if msg.chat_id == chat_id:
            return msg
    raise KeyError


def update_msg(session: Session, chat_id: int, message_id: str, msg_update: UpdateMessage) -> MessageInDB:
    """
    Update a message in the database.

    :param chat_id: id of the chat to be updated
    :param message_id: id of the message to be updated
    :param msg_update: attributes to be updated on the message
    :return: the updated message
    """

    msg = get_msg_by_id(session, chat_id, message_id)
    msg.text = msg_update.text
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg


def delete_msg(session: Session, chat_id: int, message_id: str) :
    """
    Deetes a message in the database.

    :param chat_id: id of the chat to be updated
    :param message_id: id of the message to be updated
    """

    msg = get_msg_by_id(session, chat_id, message_id)
    session.delete(msg)
    session.commit()
