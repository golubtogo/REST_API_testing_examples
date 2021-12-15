from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Dict


def create_custom_service(client: TestClient, headers: Dict[str, str], json=False):
    units = client.get(f"{settings.API_V1_STR}/units/", headers=headers).json()
    if len(units) == 0:
        unit = client.post(f"{settings.API_V1_STR}/units/", json={'name': 'kg', 'short_name': 'kg'},
                           headers=headers).json()
    else:
        unit = units[0]

    custom_service_data = {
        "name": "string",
        "description": "string",
        "unit_id": unit['id']
    }

    if json:
        return client.post(f"{settings.API_V1_STR}/custom_service/",
                           json=custom_service_data, headers=headers).json(), custom_service_data
    return client.post(f"{settings.API_V1_STR}/custom_service/",
                       json=custom_service_data, headers=headers), custom_service_data
