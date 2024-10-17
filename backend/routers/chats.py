from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from backend.auth import get_current_user

from backend.entities import (
    Chat,
    ChatCollection,
    ChatInDB,
    ChatResponse,
    CreateMessage,
    Message,
    MessageCollection,
    UpdateChat,
    Metadata,
    UpdateMessage,
    User,
    UserCollection,
    UserInDB,
)
from backend import database as db

chats_router = APIRouter(prefix="/chats", tags=["Chats"])


def chat_has_user(chat: ChatInDB, other_user: UserInDB) -> bool:
    for user in chat.users:
        if user.id == other_user.id:
            return True
    return False


def user_guard(session: Session, other_user: UserInDB, chat_id: int):
    chat = db.get_chat_by_id(session, chat_id)
    if chat_has_user(chat, other_user):
        return

    raise HTTPException(403, {
            "error": "no_permission",
            "error_description": "requires permission to view chat"
    })


@chats_router.get("", description="Gets all chats created under the Pony Express")
def get_chats(session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    chats = db.get_all_chats(session)
    chats = [Chat.from_db(chat) for chat in chats if chat_has_user(chat, user)]
    chats.sort(key=lambda x: x.name)

    return ChatCollection(meta=Metadata(count=len(chats)), chats=chats)


@chats_router.get("/{chat_id}", description="Gets a chat with the given id, optionally including users, messages, or both", response_model=ChatResponse, response_model_exclude_none=True)
def get_chat(chat_id: int, include: Annotated[list[str], Query()] = [], session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    try:
        user_guard(session, user, chat_id)
        chat = db.get_chat_by_id(session, chat_id)
        return ChatResponse.from_db(chat, "messages" in include, "users" in include)
    except KeyError:
        raise HTTPException(404, {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "Chat",
                "entity_id": chat_id
            }
        })


@chats_router.put("/{chat_id}", description="Update the name of the chat with the given id")
def update_chat(chat_id: int, update: UpdateChat, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    try:
        chat = db.get_chat_by_id(session, chat_id)
        if chat.owner_id != user.id:
            raise HTTPException(403, {
                "detail": {
                    "error": "no_permission",
                    "error_description": "requires permission to view chat"
                }
            })
        chat = db.update_chat(session, chat_id, update)
        return {"chat": Chat.from_db(chat)}
    except KeyError:
        raise HTTPException(404, {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "Chat",
                "entity_id": chat_id
            }
        })


@chats_router.get("/{chat_id}/messages", description="Get all messages inside the chat with the given id")
def get_chat_messages(chat_id: int, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    try:
        user_guard(session, user, chat_id)
        chat = db.get_chat_by_id(session, chat_id)
        messages = [Message.from_db(msg) for msg in chat.messages]

        return MessageCollection(meta=Metadata(count=len(messages)), messages=messages)
    except KeyError:
        raise HTTPException(404, {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "Chat",
                "entity_id": chat_id
            }
        })


@chats_router.get("/{chat_id}/users", description="Gets all users participating in the chat with the given id")
def get_chat_users(chat_id: int, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    try:
        user_guard(session, user, chat_id)
        chat = db.get_chat_by_id(session, chat_id)
        users = [User(**user.model_dump()) for user in chat.users]
        users.sort(key=lambda x: x.id)

        return UserCollection(meta=Metadata(count=len(users)), users=users)
    except KeyError:
        raise HTTPException(404, {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "Chat",
                "entity_id": chat_id
            }
        })


@chats_router.post("/{chat_id}/messages", description="Creates a new message in the given chat", status_code=201)
def create_chat_message(chat_id: int, message: CreateMessage, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    try:
        user_guard(session, user, chat_id)
        return {"message": Message.from_db(db.create_message(session, chat_id, message, user))}
    except KeyError:
        raise HTTPException(404, {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "Chat",
                "entity_id": chat_id
            }
        })


@chats_router.put("/{chat_id}/messages/{message_id}", description="Update the text of a message with the given messaage id and chat id")
def update_message(chat_id: int, message_id: str, update: UpdateMessage, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    try:
        msg = db.get_msg_by_id(session, chat_id, message_id)

        if msg.user_id != user.id:
            raise HTTPException(403, {
                "error": "no_permission",
                "error_description": "requires permission to edit message"
            })
        
        msg = db.update_msg(session, chat_id, message_id, update)

        return {"message": Message.from_db(msg)}
    except KeyError:
        raise HTTPException(404, {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "Chat",
                "entity_id": chat_id
            }
        })


@chats_router.delete("/{chat_id}/messages/{message_id}", description="Deletes the message with the given messaage id and chat id", status_code=204)
def delete_message(chat_id: int, message_id: str, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    try:
        msg = db.get_msg_by_id(session, chat_id, message_id)

        if msg.user_id != user.id:
            raise HTTPException(403, {
                "error": "no_permission",
                "error_description": "requires permission to edit message"
            })
        
        db.delete_msg(session, chat_id, message_id)
    except KeyError:
        raise HTTPException(404, {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "Chat",
                "entity_id": chat_id
            }
        })
