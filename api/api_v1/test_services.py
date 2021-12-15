from typing import Dict
from fastapi.testclient import TestClient
from app.core.config import settings
from sqlalchemy.orm import Session
from app.tests.utils.categories import create_category
from app.tests.utils.utils import cleanup_object
from app.tests.utils.user import create_user_and_login
from app.tests.utils.services import create_services


def test_send_email(**kwargs):
    return True


def test_create_services(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response, services_data = create_services(client, superuser_token_headers)
    assert response.status_code == 200
    cleanup_data = cleanup_object(response.json(), ['id', 'categories', 'owner_id'])
    assert services_data == cleanup_data


def test_get_services(client: TestClient, superuser_token_headers: Dict[str, str], db: Session, mocker) -> None:
    mocker.patch("app.utils.send_email", test_send_email)
    response_post_create, services_data = create_services(client, superuser_token_headers)
    assert response_post_create.status_code == 200
    assert services_data == cleanup_object(response_post_create.json(), ['id', 'categories', 'owner_id'])

    response_get = client.get(f"{settings.API_V1_STR}/services/9999999999",
                              headers=superuser_token_headers)
    assert response_get.status_code == 404

    response_post = response_post_create.json()
    response_superuser_get = client.get(f"{settings.API_V1_STR}/services/{response_post['id']}",
                                        headers=superuser_token_headers).json()
    assert services_data == cleanup_object(response_superuser_get, ['id', 'categories', 'owner_id'])

    user_token_headers, _ = create_user_and_login(client, superuser_token_headers)
    response_post, services_data = create_services(client, user_token_headers)
    assert response_post.status_code == 400

    response_get_services = client.get(f"{settings.API_V1_STR}/services/",
                                       headers=superuser_token_headers).json()
    assert len(response_get_services) > 0

    response_category, service_category_data = create_category(client, db, superuser_token_headers, json=True)
    response_post_create = response_post_create.json()
    service_category_data = [{
        'category_id': response_category['id'],
        'service_id': response_post_create['id']
    }]

    response_service_category = client.post(f"{settings.API_V1_STR}/service_categories/", json=service_category_data,
                                            headers=superuser_token_headers).json()
    assert service_category_data == response_service_category
    response_service_category_get = client.get(f"{settings.API_V1_STR}/services/?category_id={response_category['id']}",
                                               json=service_category_data,
                                               headers=superuser_token_headers).json()
    assert len(response_service_category_get) > 0


def test_put_services(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    response_post, services_data = create_services(client, superuser_token_headers, json=True)
    services_data2 = services_data
    services_data2['name'] = "www"
    response = client.put(f"{settings.API_V1_STR}/services/{response_post['id']}",
                          json=services_data2, headers=superuser_token_headers)
    assert response.status_code == 200
    response = response.json()
    assert response['name'] == services_data2['name']

    response = client.put(f"{settings.API_V1_STR}/services/9999999999",
                          json=services_data2, headers=superuser_token_headers)
    assert response.status_code == 404


def test_delete_services(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response_post, services_data = create_services(client, superuser_token_headers, json=True)
    response = client.delete(f"{settings.API_V1_STR}/services/{response_post['id']}", headers=superuser_token_headers)
    assert response.status_code == 200
    response = cleanup_object(response.json(), ['id', 'categories', 'owner_id'])
    assert response == services_data

    response = client.delete(f"{settings.API_V1_STR}/services/9999999999",
                             json=services_data, headers=superuser_token_headers)
    assert response.status_code == 404
