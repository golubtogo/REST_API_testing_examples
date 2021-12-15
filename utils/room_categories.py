from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Dict


def create_room_categories(client: TestClient, headers: Dict[str, str], json=False):
    rooms_data = {
        "name": "string",
        "room_type": "string",
    }
    files = {("image", ('site.png', open("app/email-templates/src/images/site.png", 'rb'), 'image/png'))}
    category_data = {
        "name": "Category Name",
        "description": "Category description",
        "parent_id": 1,
    }

    room_response = client.post(f"{settings.API_V1_STR}/rooms/", data=rooms_data, files=files, headers=headers).json()

    category_response = client.post(f"{settings.API_V1_STR}/categories/", data=category_data, files=files,
                                    headers=headers).json()
    room_category_data = [{
        'category_id': category_response['id'],
        'room_id': room_response['id']
    }]
    if json:
        return client.post(f"{settings.API_V1_STR}/room_categories/", json=room_category_data,
                           headers=headers).json(), room_category_data
    return client.post(f"{settings.API_V1_STR}/room_categories/", json=room_category_data,
                       headers=headers), room_category_data
