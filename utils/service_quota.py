from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Dict
from app.tests.utils.quota import create_quota
from app.tests.utils.services import create_services


def create_service_quota(client: TestClient, headers: Dict[str, str], json=False):
    if 'superuser' not in headers:
        headers = {'user': headers, 'superuser': headers}

    response_service, service_quota_data = create_services(client, headers['superuser'], json=True)
    response_quota, service_quota_data = create_quota(client, headers['user'], json=True)
    service_quota_data = {
        'name': 'sqd',
        'status': True,
        'service_id': response_service['id'],
        'quota_id': response_quota['id'],
    }
    if json:
        return client.post(f"{settings.API_V1_STR}/service_quota/", json=service_quota_data,
                           headers=headers['user']).json(), service_quota_data
    return client.post(f"{settings.API_V1_STR}/service_quota/", json=service_quota_data,
                       headers=headers['user']), service_quota_data
