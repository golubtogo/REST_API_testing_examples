from typing import Dict
from fastapi.testclient import TestClient
from app.core.config import settings
from sqlalchemy.orm import Session
from app.tests.utils.service_quota import create_service_quota
from app.tests.utils.user import create_user_and_login
from app.tests.utils.utils import cleanup_object


class Storage:
    user_headers = None
    service_quota_id = None
    service_quota_data = None
    user_id = None


def test_send_email(**kwargs):
    return True


def test_create_service_quota(client: TestClient, superuser_token_headers: Dict[str, str], db: Session, mocker):
    mocker.patch("app.utils.send_email", test_send_email)
    Storage.user_headers, Storage.user_id = create_user_and_login(client, superuser_token_headers)
    headers = {'superuser': superuser_token_headers, 'user': Storage.user_headers}
    response, service_quota_data = create_service_quota(client, headers)
    assert response.status_code == 200
    assert service_quota_data == cleanup_object(response.json(), ['id', 'owner_id'])
    Storage.service_quota_id = response.json()['id']
    Storage.service_quota_data = service_quota_data


def test_get_service_quota(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response_get_service_quota = client.get(f"{settings.API_V1_STR}/service_quota/{Storage.service_quota_id}",
                                            headers=superuser_token_headers).json()
    assert Storage.service_quota_data == cleanup_object(response_get_service_quota, ['id', 'owner_id'])

    response_get_service_quota = client.get(f"{settings.API_V1_STR}/service_quota/{Storage.service_quota_id}",
                                            headers=Storage.user_headers).json()
    assert Storage.service_quota_data == cleanup_object(response_get_service_quota, ['id', 'owner_id'])

    headers = {'superuser': superuser_token_headers, 'user': superuser_token_headers}
    create_service_quota(client, headers)
    response_get_service_quota = client.get(f"{settings.API_V1_STR}/service_quota/?owner_id=1",
                                            headers=superuser_token_headers).json()
    assert len(response_get_service_quota) > 0

    create_service_quota(client, superuser_token_headers)
    response_get_service_quota = client.get(f"{settings.API_V1_STR}/service_quota/?owner_id=1",
                                            headers=Storage.user_headers).json()
    assert len(response_get_service_quota) > 0

    response_get_service_quota = client.get(f"{settings.API_V1_STR}/service_quota/9999999999",
                                            headers=superuser_token_headers)
    assert response_get_service_quota.status_code == 404


def test_put_service_quota(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    service_quota_data2 = Storage.service_quota_data
    service_quota_data2['name'] = "www"

    response = client.put(f"{settings.API_V1_STR}/service_quota/{Storage.service_quota_id}",
                          json=service_quota_data2, headers=Storage.user_headers)
    assert response.status_code == 200

    response = client.put(f"{settings.API_V1_STR}/service_quota/{Storage.service_quota_id}",
                          json=service_quota_data2, headers=superuser_token_headers)
    assert response.status_code == 200
    response = response.json()
    assert response['name'] == service_quota_data2['name']

    response = client.put(f"{settings.API_V1_STR}/service_quota/9999999999",
                          json=service_quota_data2, headers=superuser_token_headers)
    assert response.status_code == 404


def test_delete_service_quota(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    headers = {'superuser': superuser_token_headers, 'user': Storage.user_headers}
    response_post, service_quota_data = create_service_quota(client, headers=headers, json=True)
    response = client.delete(f"{settings.API_V1_STR}/service_quota/{response_post['id']}",
                             headers=superuser_token_headers)
    assert response.status_code == 200
    response = cleanup_object(response.json(), ['id', 'owner_id'])
    assert response == service_quota_data
    response = client.delete(f"{settings.API_V1_STR}/service_quota/9999999999",
                             json=service_quota_data, headers=superuser_token_headers)
    assert response.status_code == 404

    headers = {'superuser': superuser_token_headers, 'user': Storage.user_headers}
    response, service_quota_data = create_service_quota(client, headers, json=True)
    response_delete = client.delete(f"{settings.API_V1_STR}/service_quota/{response['id']}",
                                    headers=Storage.user_headers)
    assert response_delete.status_code == 200
