from typing import Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.tests.utils.categories import create_category
from app.tests.utils.quota_rooms import create_quota_room
from app.tests.utils.user import create_user_and_login
from app.tests.utils.utils import cleanup_object
from app.core.config import settings


class Storage:
    quota_room_id = None
    quota_room_data = None
    user_header = None


def test_send_email(**kwargs):
    return True


def test_create_quota_rooms(client: TestClient, superuser_token_headers: Dict[str, str], db: Session, mocker) -> None:
    mocker.patch("app.utils.send_email", test_send_email)
    user_header, user_id = create_user_and_login(client, superuser_token_headers)
    Storage.user_header = user_header
    headers = {'superuser': superuser_token_headers, 'user': Storage.user_header}
    response_quota_room_post_200, quota_room_data = create_quota_room(client, headers)
    assert response_quota_room_post_200.status_code == 200
    Storage.quota_room_id = response_quota_room_post_200.json()['id']
    Storage.quota_room_data = quota_room_data
    assert quota_room_data == cleanup_object(response_quota_room_post_200.json(), ['id'])

    quota_room_data = {
        "name": "WC 343",
        "status": True,
        "room_id": quota_room_data['room_id'],
        "quota_id": 999999999,
        "length": 11.1,
        "width": 10,
        "height": 1
    }
    response_404 = client.post(f"{settings.API_V1_STR}/quota_rooms/",
                               json=quota_room_data, headers=headers['user'])
    assert response_404.status_code == 404


def test_get_quota_rooms(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response_quota_room = client.get(f"{settings.API_V1_STR}/quota_rooms/{Storage.quota_room_id}",
                                     headers=Storage.user_header)
    assert response_quota_room.status_code == 200
    assert Storage.quota_room_data == cleanup_object(response_quota_room.json(), ['id', 'owner_id'])

    category, _ = create_category(client=client, db=db, headers=superuser_token_headers, json=True)
    client.post(f"{settings.API_V1_STR}/quota_room_categories/",
                json=[{
                    'category_id': category['id'],
                    'quota_room_id': Storage.quota_room_id
                }],
                headers=Storage.user_header)
    response = client.get(f"{settings.API_V1_STR}/quota_rooms/?quota_id={Storage.quota_room_data['quota_id']}",
                          headers=Storage.user_header).json()
    assert len(response[0]['categories']) == 1
    assert len(response) > 0

    response = client.get(f"{settings.API_V1_STR}/quota_rooms/",
                          headers=Storage.user_header).json()
    assert len(response) > 0

    response = client.get(f"{settings.API_V1_STR}/quota_rooms/999999999", headers=superuser_token_headers)
    assert response.status_code == 404


def test_put_quota_rooms(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    quota_room_data2 = {"name": "my quota room22",
                        "quota_id": Storage.quota_room_data['quota_id'],
                        "room_id": Storage.quota_room_data['room_id'],
                        "height": 11,
                        "width": 12,
                        "length": 10,
                        "custom_square": None,
                        "status": True}
    response_quota_room = client.put(f"{settings.API_V1_STR}/quota_rooms/{Storage.quota_room_id}",
                                     json=quota_room_data2,
                                     headers=superuser_token_headers).json()
    assert quota_room_data2 == cleanup_object(response_quota_room, ['id', 'owner_id'])

    response_quota_room = client.put(f"{settings.API_V1_STR}/quota_rooms/{Storage.quota_room_id}",
                                     json=quota_room_data2,
                                     headers=Storage.user_header).json()
    assert quota_room_data2 == cleanup_object(response_quota_room, ['id', 'owner_id'])

    response_404 = client.put(f"{settings.API_V1_STR}/quota_rooms/09090909090",
                              json=quota_room_data2,
                              headers=superuser_token_headers)
    assert response_404.status_code == 404


def test_delete_quota_rooms(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    response_delete = client.delete(f"{settings.API_V1_STR}/quota_rooms/{Storage.quota_room_id}",
                                    headers=superuser_token_headers)
    assert response_delete.status_code == 200

    headers = {'superuser': superuser_token_headers, 'user': Storage.user_header}
    response_quota_room_post_200, quota_room_data = create_quota_room(client, headers, json=True)
    response_delete = client.delete(f"{settings.API_V1_STR}/quota_rooms/{response_quota_room_post_200['id']}",
                                    headers=Storage.user_header)
    assert response_delete.status_code == 200

    response_404 = client.delete(f"{settings.API_V1_STR}/quota_rooms/09090909090",
                                 headers=superuser_token_headers)
    assert response_404.status_code == 404
