from fastapi.testclient import TestClient
from backend.entities import Chat, ChatCollection, MessageCollection, UserCollection

from backend.main import app


def test_get_all_chats():
    client = TestClient(app)
    response = client.get("/chats")
    assert response.status_code == 200
    chats = ChatCollection(**response.json())
    assert chats.meta.count == 6
    assert len(chats.chats) == 6


def test_get_chat():
    client = TestClient(app)
    response = client.get("/chats/36b18c30f5eb4c7888229474d12e426f")
    assert response.status_code == 200
    chat = Chat(**response.json()["chat"])
    assert chat.name == "sensory apparatus"


def test_update_chat():
    client = TestClient(app)
    response = client.put("/chats/6ad56d52b138432a9bba609533015cf3", json={"name": "phenotype"})
    assert response.status_code == 200
    assert Chat(**response.json()["chat"]).name == "phenotype"
    response = client.get("/chats/6ad56d52b138432a9bba609533015cf3")
    assert response.status_code == 200
    assert Chat(**response.json()["chat"]).name == "phenotype"


def test_delete_chat():
    client = TestClient(app)
    response = client.delete("/chats/6ad56d52b138432a9bba609533015cf3")
    assert response.status_code == 204
    response = client.get("/chats/6ad56d52b138432a9bba609533015cf3")
    assert response.status_code == 404
    assert response.json() == {
            "detail": {
                "type": "entity_not_found",
                "entity_name": "Chat",
                "entity_id": "6ad56d52b138432a9bba609533015cf3"
            }
        }


def test_get_chat_users():
    client = TestClient(app)
    response = client.get("/chats/e0ec0881a2c645de842ca5dd0fa7985b/users")
    assert response.status_code == 200
    users = UserCollection(**response.json())
    assert users.meta.count == 2
    assert len(users.users) == 2
    user_names = [user.id for user in users.users]
    assert "newt" in user_names
    assert "ripley" in user_names


def test_get_chat_messages():
    client = TestClient(app)
    response = client.get("/chats/e0ec0881a2c645de842ca5dd0fa7985b/messages")
    assert response.status_code == 200
    messages = MessageCollection(**response.json())
    assert messages.meta.count == 59
    assert len(messages.messages) == 59


def test_get_invalid_chat_id():
    client = TestClient(app)
    response = client.get("/chats/124h33d")
    assert response.status_code == 404


def test_get_invalid_chat_users():
    client = TestClient(app)
    response = client.get("/chats/jtere3443d/users")
    assert response.status_code == 404


def test_get_invalid_chat_messages():
    client = TestClient(app)
    response = client.get("/chats/jtere3443d/messages")
    assert response.status_code == 404
