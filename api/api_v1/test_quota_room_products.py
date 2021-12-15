from typing import Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.tests.utils.quota_room_products import create_quota_room_products
from app.tests.utils.services import create_services
from app.tests.utils.user import create_user_and_login
from app.tests.utils.utils import cleanup_object
from app.core.config import settings


class Storage:
    quota_room_products_id = None
    quota_room_products_data = None
    cleanup = ['id', 'owner_id', 'custom_product_id']
    user_header = None
    response_200 = None
    quota_room_products_data2 = None


def test_send_email(**kwargs):
    return True


def test_create_quota_room_products(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response_post_200, quota_room_products_data = create_quota_room_products(client, superuser_token_headers, db)
    assert response_post_200.status_code == 200
    response_post_200 = response_post_200.json()
    Storage.quota_room_products_id = response_post_200['id']
    Storage.quota_room_products_data = quota_room_products_data
    response_post = cleanup_object(response_post_200, ['id', 'owner_id', 'custom_product_id'])
    assert quota_room_products_data == response_post


def test_get_quota_room_products(client: TestClient, superuser_token_headers: Dict[str, str], db: Session, mocker):
    mocker.patch("app.utils.send_email", test_send_email)
    url = f"{settings.API_V1_STR}/quota_room_products/{Storage.quota_room_products_id}"
    response_get_quota_room_products_200 = client.get(url, headers=superuser_token_headers).json()
    assert Storage.quota_room_products_data == cleanup_object(response_get_quota_room_products_200, Storage.cleanup)

    response_get_quota_room_products_200 = client.get(f"{settings.API_V1_STR}/quota_room_products/",
                                                      headers=superuser_token_headers).json()

    assert len(response_get_quota_room_products_200) > 0
    quota_room_id = Storage.quota_room_products_data['quota_room_id']
    response = client.get(f"{settings.API_V1_STR}/quota_room_products/?quota_room_id={quota_room_id}",
                          headers=superuser_token_headers).json()
    assert len(response) > 0
    response_get_quota_room_products_404 = client.get(f"{settings.API_V1_STR}/quota_room_products/99999999",
                                                      headers=superuser_token_headers)
    assert response_get_quota_room_products_404.status_code == 404
    user_header, _ = create_user_and_login(client, superuser_token_headers)
    Storage.user_header = user_header
    headers = {'superuser': superuser_token_headers, 'user': user_header}
    response_post_200, quota_room_products_data = create_quota_room_products(client, headers, db, json=True)
    Storage.response_200 = response_post_200
    url = f"{settings.API_V1_STR}/quota_room_products/{response_post_200['id']}"
    response_get_quota_room_products_200 = client.get(url, headers=user_header)
    assert response_get_quota_room_products_200.status_code == 200


def test_put_quota_room_products(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response_service2, quota_room_products_data = create_services(client, superuser_token_headers, json=True)
    quota_room_products_data2 = {
        "quota_room_id": Storage.response_200['quota_room_id'],
        "service_id": response_service2['id'],
        "service_product_id": Storage.response_200['service_product_id']
    }
    Storage.quota_room_products_data2 = quota_room_products_data2
    response_put_quota_room_products = client.put(
        f"{settings.API_V1_STR}/quota_room_products/{Storage.quota_room_products_id}",
        json=quota_room_products_data2,
        headers=superuser_token_headers).json()
    assert response_put_quota_room_products['service_id'] == quota_room_products_data2['service_id']
    quota_room_products_data3 = {
        "quota_room_id": Storage.response_200['quota_room_id'],
        "service_id": response_service2['id'],
        "service_product_id": '09090909090'
    }
    response_404 = client.post(f"{settings.API_V1_STR}/quota_room_products/",
                               json=quota_room_products_data3,
                               headers=superuser_token_headers)

    headers = {'superuser': superuser_token_headers, 'user': Storage.user_header}
    response_post_200_user, _ = create_quota_room_products(client, headers=headers, db=db, json=True)
    response_put_quota_room_products = client.put(
        f"{settings.API_V1_STR}/quota_room_products/{response_post_200_user['id']}",
        json=quota_room_products_data2,
        headers=Storage.user_header)
    assert response_put_quota_room_products.status_code == 200

    assert response_404.status_code == 404

    response_404 = client.put(f"{settings.API_V1_STR}/quota_room_products/09090909090",
                              json=quota_room_products_data2,
                              headers=superuser_token_headers)
    assert response_404.status_code == 404


def test_delete_quota_room_products(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response_delete = client.delete(f"{settings.API_V1_STR}/quota_room_products/{Storage.quota_room_products_id}",
                                    headers=superuser_token_headers).json()
    assert response_delete['quota_room_id'] == Storage.quota_room_products_data2['quota_room_id']
    assert response_delete['service_id'] == Storage.quota_room_products_data2['service_id']
    assert response_delete['service_product_id'] == Storage.quota_room_products_data2['service_product_id']
    response_404 = client.delete(f"{settings.API_V1_STR}/quota_room_products/09090909090",
                                 headers=superuser_token_headers)
    assert response_404.status_code == 404

    headers = {'superuser': superuser_token_headers, 'user': Storage.user_header}
    response_post_200_user, _ = create_quota_room_products(client, headers=headers, db=db, json=True)
    response_delete_200 = client.delete(
        f"{settings.API_V1_STR}/quota_room_products/{response_post_200_user['id']}",
        headers=Storage.user_header)
    assert response_delete_200.status_code == 200
