from typing import Dict
from fastapi.testclient import TestClient
from app.core.config import settings
from sqlalchemy.orm import Session
from app.tests.utils.utils import cleanup_object
from app.tests.utils.user import create_user_and_login


class Storage:
    custom_service_id = None
    user_headers = None
    user_id = None
    custom_service_init = None


def test_send_email(**kwargs):
    return True


def test_create_custom_service(client: TestClient, superuser_token_headers: Dict[str, str], db: Session, mocker):
    mocker.patch("app.utils.send_email", test_send_email)
    user_token_headers, user_id = create_user_and_login(client, superuser_token_headers)
    Storage.user_headers = user_token_headers
    Storage.user_id = user_id
    units = client.get(f"{settings.API_V1_STR}/units/", headers=user_token_headers).json()
    if len(units) == 0:
        unit = client.post(f"{settings.API_V1_STR}/units/", json={'name': 'kg', 'short_name': 'kg'},
                           headers=superuser_token_headers).json()
    else:
        unit = units[0]

    custom_service_init = {
        "name": "string",
        "description": "string",
        "unit_id": unit['id']
    }
    Storage.custom_service_init = custom_service_init

    response_post_200 = client.post(f"{settings.API_V1_STR}/custom_service/",
                                    json=custom_service_init, headers=user_token_headers)
    assert response_post_200.status_code == 200

    unit = client.get(f"{settings.API_V1_STR}/units/1", headers=superuser_token_headers).json()
    if 'id' not in unit:
        db.execute("INSERT INTO unit (id, name, short_name) VALUES (1, 'kg','kg')")
        db.commit()

    response_post_200_no_unit = client.post(f"{settings.API_V1_STR}/custom_service/",
                                            json={"name": "string", "description": "string"},
                                            headers=user_token_headers)
    assert response_post_200_no_unit.status_code == 200

    Storage.custom_service_id = response_post_200.json()['id']
    assert custom_service_init == cleanup_object(response_post_200.json(),
                                                 ['id', 'categories', 'owner_id', 'additional_units',
                                                  'default_price', 'reference', 'tax'])


def test_get_custom_service(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    response_get_200 = client.get(f"{settings.API_V1_STR}/custom_service/{Storage.custom_service_id}",
                                  headers=Storage.user_headers).json()
    assert Storage.custom_service_init == cleanup_object(response_get_200, ['id', 'categories', 'owner_id',
                                                                            'additional_units',
                                                                            'default_price', 'reference', 'tax'])

    response_get_200 = client.get(f"{settings.API_V1_STR}/custom_service/{Storage.custom_service_id}",
                                  headers=superuser_token_headers).json()
    assert Storage.custom_service_init == cleanup_object(response_get_200, ['id', 'categories', 'owner_id',
                                                                            'additional_units',
                                                                            'default_price', 'reference', 'tax'])

    response_get_custom_service = client.get(f"{settings.API_V1_STR}/custom_service/",
                                             headers=Storage.user_headers).json()
    assert len(response_get_custom_service) > 0

    response_get_custom_service = client.get(f"{settings.API_V1_STR}/custom_service/?owner_id={Storage.user_id}",
                                             headers=superuser_token_headers).json()
    assert len(response_get_custom_service) > 0


def test_get_notfound_custom_service(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    response_get_404 = client.get(f"{settings.API_V1_STR}/custom_service/9999999999",
                                  headers=Storage.user_headers)
    assert response_get_404.status_code == 404


def test_put_custom_service(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    response_put = client.put(f"{settings.API_V1_STR}/custom_service/{Storage.custom_service_id}",
                              json={'name': 'name2', 'description': 'www'}, headers=Storage.user_headers)
    assert response_put.status_code == 200
    response_put = response_put.json()
    assert response_put['name'] == 'name2'
    assert response_put['description'] == 'www'

    response_put = client.put(f"{settings.API_V1_STR}/custom_service/{Storage.custom_service_id}",
                              json={'name': 'name2', 'description': 'www'}, headers=superuser_token_headers)
    assert response_put.status_code == 200


def test_put_notfound_custom_service(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    response_put = client.put(f"{settings.API_V1_STR}/custom_service/9999999999",
                              json={'name': 'name2'}, headers=Storage.user_headers)
    assert response_put.status_code == 404


def test_delete_custom_service(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    response_delete_200 = client.delete(f"{settings.API_V1_STR}/custom_service/{Storage.custom_service_id}",
                                        headers=Storage.user_headers)
    assert response_delete_200.status_code == 200

    response_post_200 = client.post(f"{settings.API_V1_STR}/custom_service/",
                                    json=Storage.custom_service_init, headers=Storage.user_headers).json()

    response_delete_200 = client.delete(f"{settings.API_V1_STR}/custom_service/{response_post_200['id']}",
                                        headers=superuser_token_headers)
    assert response_delete_200.status_code == 200


def test_delete_notfound_custom_service(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    response_delete_404 = client.delete(f"{settings.API_V1_STR}/custom_service/9999999999",
                                        headers=Storage.user_headers)
    assert response_delete_404.status_code == 404
