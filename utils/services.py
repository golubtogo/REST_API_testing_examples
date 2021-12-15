from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Dict


def create_services(client: TestClient, headers: Dict[str, str], json=False):
    units = client.get(f"{settings.API_V1_STR}/units/", headers=headers).json()
    if len(units) == 0:
        unit = client.post(f"{settings.API_V1_STR}/units/", json={'name': 'kg', 'short_name': 'kg'},
                           headers=headers).json()
    else:
        unit = units[0]

    services_data = {
        "name": "string",
        "description": "string",
        "reference": "string",
        "default_price": 10.0,
        "tax": 10.0,
        "unit_id": unit['id'],
        "additional_units": 0.0,
    }

    if json:
        return client.post(f"{settings.API_V1_STR}/services/", json=services_data,
                           headers=headers).json(), services_data
    return client.post(f"{settings.API_V1_STR}/services/", json=services_data, headers=headers), services_data
