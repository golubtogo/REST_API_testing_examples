from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Dict
from app.tests.utils.quota_room_service import create_quota_room_service
from app.tests.utils.service_products import create_service_products


def create_quota_room_products(client: TestClient, headers: Dict[str, str], db, json=False):
    if 'superuser' not in headers:
        headers = {'user': headers, 'superuser': headers}

    response_service_product, quota_room_products_data = create_service_products(client, headers['superuser'],
                                                                                 json=True)
    service_id = response_service_product['service_id']
    response_quota_room_service, _ = create_quota_room_service(client, headers['superuser'], db, service_id, json=True)
    quota_room_products_data = {
        "quota_room_id": response_quota_room_service['quota_room_id'],
        "service_id": response_quota_room_service['service_id'],
        "service_product_id": response_service_product['id']
    }

    if json:
        return client.post(f"{settings.API_V1_STR}/quota_room_products/", json=quota_room_products_data,
                           headers=headers['user']).json(), quota_room_products_data
    return client.post(f"{settings.API_V1_STR}/quota_room_products/", json=quota_room_products_data,
                       headers=headers['user']), quota_room_products_data
