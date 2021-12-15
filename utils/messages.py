from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Dict
from app.tests.utils.project import create_project
from app.tests.utils.quota import create_quota


def create_message(client: TestClient, headers: Dict[str, str], json=False):
    response_quota, _ = create_quota(client, headers, json=True)
    response_project, _ = create_project(client, headers, json=True)

    message_data = {
        "phone": "123123213",
        "message": "123123123",
        "quota_id": response_quota['id'],
        "project_id": response_project['id'],
    }

    if json:
        return client.post(f"{settings.API_V1_STR}/messages/",
                           json=message_data,
                           headers=headers).json(), message_data
    return client.post(f"{settings.API_V1_STR}/messages/",
                       json=message_data,
                       headers=headers), message_data
