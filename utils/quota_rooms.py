from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Dict, Any
from app.tests.utils.quota import create_quota
from app.tests.utils.rooms import create_room


def create_quota_room(client: TestClient, headers: Any, json=False):
    if 'superuser' not in headers:
        headers = {'user': headers, 'superuser': headers}

    response_quota, _ = create_quota(client, headers['user'], json=True)
    response_room, _ = create_room(client, headers['superuser'], json=True)
    quota_room_data = {
        "name": "WC 343",
        "status": True,
        "room_id": response_room['id'],
        "quota_id": response_quota['id'],
        "length": 11.1,
        "width": 10,
        "height": 1,
        "custom_square": None
    }
    if json:
        return client.post(f"{settings.API_V1_STR}/quota_rooms/",
                           json=quota_room_data, headers=headers['user']).json(), quota_room_data
    return client.post(f"{settings.API_V1_STR}/quota_rooms/",
                       json=quota_room_data, headers=headers['user']), quota_room_data
