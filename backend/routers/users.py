from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.auth import get_current_user

from backend.entities import (
    Chat,
    ChatCollection,
    UserCollection,
    User,
    Metadata,
    UserInDB,
    UserUpdate,
)
from backend import database as db

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("", description="Get all users registered under the Pony Express")
def get_users(session: Session = Depends(db.get_session)):
    users = db.get_all_users(session)
    users = [User.from_db(user) for user in users]
    users.sort(key=lambda x: x.id)

    return UserCollection(meta=Metadata(count=len(users)), users=users)


@users_router.get("/me")
def get_self(user: UserInDB = Depends(get_current_user)):
    """Get current user."""
    return {"user": User.from_db(user)}


@users_router.put("/me")
def update_self(update: UserUpdate, user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    """Update the username or email of the current user."""

    if update.username is not None:
        user.username = update.username
    if update.email is not None:
        user.email = update.email

    session.add(user)
    session.commit()
    session.refresh(user)

    return {"user": User.from_db(user)}


@users_router.get("/{user_id}", description="Gets the user with the given id")
def get_user(user_id: str, session: Session = Depends(db.get_session)):
    try:
        user = db.get_user_by_id(session, user_id)
        return {"user": User.from_db(user)}
    except KeyError:
        raise HTTPException(404, {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "User",
                "entity_id": user_id
            }
        })


@users_router.get("/{user_id}/chats", description="Gets the chats of the user with the given id")
def get_user_chats(user_id: str, session: Session = Depends(db.get_session)):
    try:
        # User presence test
        db.get_user_by_id(session, user_id)

        chats = db.get_user_chats(session, user_id)
        chats = [Chat.from_db(chat) for chat in chats]
        chats.sort(key=lambda x: x.name)

        return ChatCollection(meta=Metadata(count=len(chats)), chats=chats)

    except KeyError:
        raise HTTPException(404, {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "User",
                "entity_id": user_id
            }
        })
