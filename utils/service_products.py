from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Dict
from app.tests.utils.products import create_product
from app.tests.utils.services import create_services


def create_service_products(client: TestClient, headers: Dict[str, str], json=False):
    response_service, service_product_data = create_services(client, headers, json=True)
    response_product, service_product_data = create_product(client, headers, json=True)
    service_product_data = {
        'service_id': response_service['id'],
        'product_id': response_product['id'],
        "price": 10,
    }
    if json:
        return client.post(f"{settings.API_V1_STR}/service_products/", json=service_product_data,
                           headers=headers).json(), service_product_data
    return client.post(f"{settings.API_V1_STR}/service_products/", json=service_product_data,
                       headers=headers), service_product_data
