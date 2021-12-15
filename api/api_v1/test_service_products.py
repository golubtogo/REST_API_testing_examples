from typing import Dict
from fastapi.testclient import TestClient
from app.core.config import settings
from sqlalchemy.orm import Session
from app.tests.utils.service_products import create_service_products
from app.tests.utils.utils import cleanup_object


def test_create_service_products(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response, service_product_data = create_service_products(client, superuser_token_headers)
    assert response.status_code == 200
    response = response.json()
    assert service_product_data == cleanup_object(response, ['id'])


def test_get_service_products(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response, service_product_data = create_service_products(client, superuser_token_headers)
    assert response.status_code == 200
    response = response.json()
    url = f"{settings.API_V1_STR}/service_products/?service_id={response['service_id']}"
    response_get_service_products = client.get(url,
                                               headers=superuser_token_headers).json()
    assert service_product_data == cleanup_object(response_get_service_products[0], ['id', 'name'])
    response_get_service_products = client.get(f"{settings.API_V1_STR}/service_products/{response['id']}",
                                               headers=superuser_token_headers).json()
    assert service_product_data == cleanup_object(response_get_service_products, ['id'])
    response_get_service_products = client.get(f"{settings.API_V1_STR}/service_products/",
                                               headers=superuser_token_headers).json()
    assert len(response_get_service_products) > 0
    response_get_service_products = client.get(f"{settings.API_V1_STR}/service_products/9999999999",
                                               headers=superuser_token_headers)
    assert response_get_service_products.status_code == 404


def test_put_service_products(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    response_post, service_product_data = create_service_products(client, superuser_token_headers, json=True)
    service_product_data2 = service_product_data
    service_product_data2['price'] = 20
    response = client.put(f"{settings.API_V1_STR}/service_products/{response_post['id']}",
                          json=service_product_data2, headers=superuser_token_headers)
    assert response.status_code == 200
    response = response.json()
    assert response['price'] == service_product_data2['price']
    response = client.put(f"{settings.API_V1_STR}/service_products/9999999999",
                          json=service_product_data2, headers=superuser_token_headers)
    assert response.status_code == 404


def test_delete_service_products(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    response_post, service_product_data = create_service_products(client, superuser_token_headers, json=True)
    response = client.delete(f"{settings.API_V1_STR}/service_products/{response_post['id']}",
                             headers=superuser_token_headers)
    assert response.status_code == 200
    response = cleanup_object(response.json(), ['id'])
    assert response == service_product_data
    response = client.delete(f"{settings.API_V1_STR}/service_products/9999999999",
                             json=service_product_data, headers=superuser_token_headers)
    assert response.status_code == 404
