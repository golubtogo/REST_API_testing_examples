from typing import Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings
from app.tests.utils.messages import create_message
from app.tests.utils.user import create_user_and_login
from app.tests.utils.utils import cleanup_object


class Storage:
    message_id = None
    message_data = None
    user_headers = None


def test_send_email(**kwargs):
    return True


def test_create_message(client: TestClient, superuser_token_headers: Dict[str, str], db: Session, mocker) -> None:
    mocker.patch("app.utils.send_email", test_send_email)
    user_headers, _ = create_user_and_login(client, superuser_token_headers)
    response, message_data = create_message(client, user_headers)
    assert response.status_code == 200
    assert message_data == cleanup_object(response.json(), ['id', 'owner_id'])
    Storage.message_id = response.json()['id']
    Storage.message_data = message_data
    Storage.user_headers = user_headers


def test_get_messages(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response_get_200_list = client.get(f"{settings.API_V1_STR}/messages", headers=Storage.user_headers).json()
    assert len(response_get_200_list) > 0

    response_get_200_list = client.get(f"{settings.API_V1_STR}/messages?quota_id={Storage.message_data['quota_id']}",
                                       headers=Storage.user_headers).json()
    assert len(response_get_200_list) > 0

    response_get_200 = client.get(f"{settings.API_V1_STR}/messages/{Storage.message_id}",
                                  headers=Storage.user_headers).json()
    assert Storage.message_data == cleanup_object(response_get_200, ['id', 'owner_id'])

    response_get_200 = client.get(f"{settings.API_V1_STR}/messages/{Storage.message_id}",
                                  headers=superuser_token_headers).json()
    assert Storage.message_data == cleanup_object(response_get_200, ['id', 'owner_id'])

    response_get_404 = client.get(f"{settings.API_V1_STR}/messages/999999999",
                                  headers=superuser_token_headers)
    assert response_get_404.status_code == 404


def test_put_messages(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    message_data = Storage.message_data
    message_data['message'] = "new message"
    response_put_200 = client.put(f"{settings.API_V1_STR}/messages/{Storage.message_id}",
                                  json=message_data,
                                  headers=Storage.user_headers).json()

    assert message_data == cleanup_object(response_put_200, ['id', 'owner_id'])

    message_data['message'] = "new message2"
    response_put_200 = client.put(f"{settings.API_V1_STR}/messages/{Storage.message_id}",
                                  json=message_data,
                                  headers=superuser_token_headers).json()

    assert message_data == cleanup_object(response_put_200, ['id', 'owner_id'])

    response_put_404 = client.put(f"{settings.API_V1_STR}/messages/999999999",
                                  json=message_data,
                                  headers=superuser_token_headers)

    assert response_put_404.status_code == 404


def test_delete_messages(client: TestClient, superuser_token_headers: Dict[str, str], db: Session, mocker) -> None:
    mocker.patch("app.utils.send_email", test_send_email)
    response_delete_200 = client.delete(f"{settings.API_V1_STR}/messages/{Storage.message_id}",
                                        headers=Storage.user_headers)
    assert response_delete_200.status_code == 200

    response_create_200, message_data = create_message(client, Storage.user_headers, json=True)
    response_delete_200 = client.delete(f"{settings.API_V1_STR}/messages/{response_create_200['id']}",
                                        headers=superuser_token_headers)
    assert response_delete_200.status_code == 200

    response_delete_404 = client.delete(f"{settings.API_V1_STR}/messages/9999999999",
                                        headers=superuser_token_headers)
    assert response_delete_404.status_code == 404
