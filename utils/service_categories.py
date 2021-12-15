from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Dict
from app.tests.utils.categories import create_category
from app.tests.utils.services import create_services
from sqlalchemy.orm import Session


def create_service_categories(client: TestClient, db: Session, headers: Dict[str, str], json=False):
    response_service, service_category_data = create_services(client, headers, json=True)
    response_category, service_category_data = create_category(client, db, headers, json=True)

    service_category_data = [{
        'category_id': response_category['id'],
        'service_id': response_service['id']
    }]
    if json:
        return client.post(f"{settings.API_V1_STR}/service_categories/", json=service_category_data,
                           headers=headers).json(), service_category_data
    return client.post(f"{settings.API_V1_STR}/service_categories/", json=service_category_data,
                       headers=headers), service_category_data
