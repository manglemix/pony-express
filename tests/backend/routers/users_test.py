from fastapi.testclient import TestClient
from backend.entities import ChatCollection, User, UserCollection

from backend.main import app


def test_get_all_users():
    client = TestClient(app)
    response = client.get("/users")
    assert response.status_code == 200
    users = UserCollection(**response.json())
    assert users.meta.count == 10
    assert len(users.users) == 10


def test_create_user():
    client = TestClient(app)
    response = client.post("/users", json={"id": "adamOndra"})
    assert response.status_code == 200
    assert User(**response.json()["user"]).id == "adamOndra"
    response = client.get("/users/adamOndra")
    assert response.status_code == 200


def test_create_duplicate_user():
    client = TestClient(app)
    response = client.post("/users", json={"id": "ripley"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "type": "duplicate_entity",
            "entity_name": "User",
            "entity_id": "ripley"
        }
    }


def test_get_user_bishop():
    client = TestClient(app)
    response = client.get("/users/bishop")
    assert response.status_code == 200


def test_get_user_chats():
    client = TestClient(app)
    response = client.get("/users/sarah/chats")
    assert response.status_code == 200
    chats = ChatCollection(**response.json())
    assert chats.meta.count == 2
    assert len(chats.chats) == 2
    chat_names = [chat.name for chat in chats.chats]
    assert "skynet" in chat_names
    assert "terminators" in chat_names


def test_get_invalid_user_id():
    client = TestClient(app)
    response = client.get("/users/124h33d")
    assert response.status_code == 404


def test_get_invalid_user_chats():
    client = TestClient(app)
    response = client.get("/users/jtere3443d/chats")
    assert response.status_code == 404
