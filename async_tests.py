import os
import random
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from faker import Faker
from httpx import AsyncClient

from main import app

load_dotenv()

fake = Faker()

BASE_URL = os.getenv('BASE_URL')


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        yield ac


@pytest.fixture
def user_data():
    return {
        'username': 'test2232232',
        'password': 'testpassw3ort123',
        'email': 'teste32332mail@mail.com'
    }


@pytest.fixture
def to_do_date():
    future_date = fake.date_between(start_date='today', end_date='+300d')
    future_date_utc = datetime.combine(future_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    to_do_date = future_date_utc.isoformat(timespec='seconds').replace('+00:00', 'Z')
    return to_do_date


@pytest_asyncio.fixture
async def access_token(async_client, user_data):
    response = await async_client.post('/api/v1/auth/token', json=user_data)
    token_data = response.json()
    access_token = token_data['access_token']
    return access_token


@pytest.mark.asyncio
async def test_auth(async_client, user_data):
    reg_response = await async_client.post('/api/v1/auth/registration', json=user_data)

    assert reg_response.status_code == 200

    auth_response = await async_client.post('/api/v1/auth/token', json=user_data)

    assert auth_response.status_code == 200
    token_data = auth_response.json()
    refresh_token = token_data['refresh_token']

    refresh_token_response = await async_client.post('/api/v1/auth/token/refresh', json={
        'refresh_token': refresh_token
    })

    assert refresh_token_response.status_code == 200


@pytest.mark.asyncio
async def test_create_task(async_client, access_token, to_do_date):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    add_task_response = await async_client.post('/api/v1/tasks/add',
                                                json={'task_info': fake.sentence(10), 'datetime_to_do': to_do_date},
                                                headers=headers)
    assert add_task_response.status_code == 200

    return add_task_response.json()


@pytest.mark.asyncio
async def test_get_task(async_client, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    get_task_list_response = await async_client.get('/api/v1/tasks/list',
                                                    headers=headers)
    assert get_task_list_response.status_code == 200

    task_data = get_task_list_response.json()
    task_id = task_data[0]['id']

    get_task_response = await async_client.get(f'/api/v1/tasks/{task_id}',
                                               headers=headers)

    assert get_task_response.status_code == 200


@pytest.mark.asyncio
async def test_update_task(async_client, access_token, to_do_date):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    task_data = await test_create_task(async_client, access_token, to_do_date)

    async def update_task_data(field_name, value):
        update_task_response = await async_client.patch(f'/api/v1/tasks/{task_data["id"]}/update',
                                                        json={field_name: value}, headers=headers)

        assert update_task_response.status_code == 200
        response_data = update_task_response.json()
        assert response_data[field_name] == value

    task_info = fake.sentence(5)
    await update_task_data('task_info', task_info)

    await update_task_data('datetime_to_do', to_do_date)


@pytest.mark.asyncio
async def test_create_task_unauthorized(async_client, to_do_date):
    response = await async_client.post('/api/v1/tasks/add',
                                       json={'task_info': 'Unauthorized task', 'datetime_to_do': to_do_date})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_task_missing_task_info(async_client, access_token, to_do_date):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = await async_client.post('/api/v1/tasks/add',
                                       json={'datetime_to_do': to_do_date},
                                       headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_invalid_datetime(async_client, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = await async_client.post('/api/v1/tasks/add',
                                       json={'task_info': 'Invalid datetime task', 'datetime_to_do': 'invalid-date'},
                                       headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_task_invalid_id(async_client, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    invalid_task_id = '99999999'
    response = await async_client.get(f'/api/v1/tasks/{invalid_task_id}', headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task_invalid_data(async_client, access_token, to_do_date):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    task_data = await test_create_task(async_client, access_token, to_do_date)

    async def update_date(inv_datetime):
        response = await async_client.patch(f'/api/v1/tasks/{task_data["id"]}/update',
                                            json={'datetime_to_do': inv_datetime}, headers=headers)
        assert response.status_code == 400

    invalid_datetime = '2004-10-13T15:20:10'
    date_in_the_past = '2004-10-13T15:20:10.907Z'
    dates = (invalid_datetime, date_in_the_past)

    for date in dates:
        await update_date(date)


@pytest.mark.asyncio
async def test_access_another_users_task(async_client, user_data, to_do_date):
    other_user_data = {
        'username': 'otheruser' + ''.join(random.choices(fake.user_name(), k=5)),
        'password': 'otherpassword123',
        'email': fake.email()
    }
    reg_response = await async_client.post('/api/v1/auth/registration', json=other_user_data)
    assert reg_response.status_code == 200

    auth_response = await async_client.post('/api/v1/auth/token', json=other_user_data)
    assert auth_response.status_code == 200
    other_access_token = auth_response.json()['access_token']

    headers_other = {
        'Authorization': f'Bearer {other_access_token}'
    }
    task_response = await async_client.post('/api/v1/tasks/add',
                                            json={'task_info': 'Other user task',
                                                  'datetime_to_do': to_do_date},
                                            headers=headers_other)
    assert task_response.status_code == 200
    task_data = task_response.json()

    auth_response = await async_client.post('/api/v1/auth/token', json=user_data)
    access_token = auth_response.json()['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    get_response = await async_client.get(f'/api/v1/tasks/{task_data["id"]}', headers=headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_registration_existing_username(async_client, user_data):
    reg_response = await async_client.post('/api/v1/auth/registration', json=user_data)
    assert reg_response.status_code == 400


@pytest.mark.asyncio
async def test_login_incorrect_password(async_client, user_data):
    invalid_user_data = user_data.copy()
    invalid_user_data['password'] = 'fsdfsd11'
    auth_response = await async_client.post('/api/v1/auth/token', json=invalid_user_data)
    assert auth_response.status_code == 400


@pytest.mark.asyncio
async def test_refresh_token_invalid(async_client):
    invalid_refresh_token = ('eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI'
                             '4ODMyMDEzfQ.A8qwiQP_JGPf2qpSS5_R3H9REXkTInV_njGPyoDlN92SYE4iv4RYy0UMXw3LP6HiRpgJooqRy'
                             'kjyKueVF1lf4q')
    refresh_response = await async_client.post('/api/v1/auth/token/refresh',
                                               json={'refresh_token': invalid_refresh_token})
    assert refresh_response.status_code == 401


@pytest.mark.asyncio
async def test_create_task_long_task_info(async_client, access_token, to_do_date):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    long_task_info = 'A' * 10000
    response = await async_client.post('/api/v1/tasks/add',
                                       json={'task_info': long_task_info, 'datetime_to_do': to_do_date},
                                       headers=headers)
    assert response.status_code == 422