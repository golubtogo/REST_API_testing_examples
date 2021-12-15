from typing import Dict
from fastapi.testclient import TestClient
from app.core.config import settings
from sqlalchemy.orm import Session
from app.tests.utils.room_categories import create_room_categories


class Storage:
    room_category_data = None


def test_create_room_categories(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response, room_category_data = create_room_categories(client, superuser_token_headers)
    assert response.status_code == 200
    response = response.json()
    assert response == room_category_data
    get_by_room_response = client.get(f"{settings.API_V1_STR}/room_categories/{room_category_data[0]['room_id']}",
                                      headers=superuser_token_headers)
    assert len(get_by_room_response.json()) == 1
    Storage.room_category_data = room_category_data


def test_get_room_categories(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response, room_category_data = create_room_categories(client, superuser_token_headers)
    assert response.status_code == 200
    response_get_room_categories = client.get(f"{settings.API_V1_STR}/room_categories/",
                                              headers=superuser_token_headers).json()
    assert len(response_get_room_categories) > 0


def test_delete_room_categories(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response_get_room_categories = client.post(f"{settings.API_V1_STR}/room_categories/",
                                               json=[{'room_id': Storage.room_category_data[0]['room_id'],
                                                      'category_id': 0}],
                                               headers=superuser_token_headers).json()
    assert len(response_get_room_categories) == 0
