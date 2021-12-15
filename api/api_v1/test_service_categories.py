from typing import Dict
from fastapi.testclient import TestClient
from app.core.config import settings
from sqlalchemy.orm import Session
from app.tests.utils.service_categories import create_service_categories


def test_create_service_categories(client: TestClient, db: Session, superuser_token_headers: Dict[str, str]) -> None:
    response, service_category_data = create_service_categories(client, db, superuser_token_headers)
    assert response.status_code == 200
    response = response.json()
    assert response == service_category_data


def test_get_service_categories(client: TestClient, db: Session, superuser_token_headers: Dict[str, str]) -> None:
    response, service_category_data = create_service_categories(client, db, superuser_token_headers)
    assert response.status_code == 200

    response_get_service_categories = client.get(
        f"{settings.API_V1_STR}/service_categories/{service_category_data[0]['service_id']}",
        headers=superuser_token_headers).json()
    assert len(response_get_service_categories) > 0
