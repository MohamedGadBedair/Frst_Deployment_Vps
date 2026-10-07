from io import BytesIO
from pathlib import Path
from unittest.mock import patch,AsyncMock

import pytest
from httpx import AsyncClient
from conftest import auth_header,create_user,login_user

# ===================={Test Create Users}====================================
@pytest.mark.anyio
async def test_create_user_success(client:AsyncClient):
    response=await client.post('/api/users/',json={'username':'testuser','email':'test@example.com','password':'testpassword123'})
    data = response.json()
    assert response.status_code==201
    assert response.json()['username']=='testuser'
    assert response.json()['email']=='test@example.com'
    assert 'id' in data
    assert 'password' not in data
    assert 'password_hash' not in data
    assert 'hash_password' not in data
@pytest.mark.anyio
async def test_create_user_validation_errors(client:AsyncClient):
    # first with empty body
    response=await client.post('/api/users/')
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with invalid body
    response=await client.post('/api/users/',json={})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with only username
    response=await client.post('/api/users/',json={'username':'test'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with only email
    response=await client.post('/api/users/',json={'email':'test@example.com'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with only password
    response=await client.post('/api/users/',json={'password':'test'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with only username and email
    response=await client.post('/api/users/',json={'username':'test','email':'test@example.com'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with only username and password
    response=await client.post('/api/users/',json={'username':'test','password':'test'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # finally with only email and password
    response=await client.post('/api/users/',json={'email':'test@example.com','password':'test'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
@pytest.mark.anyio
async def test_create_users_duplicate(client:AsyncClient):
    # first create user
    await create_user(client,username='testuser',email='test@example.com',password='testpassword123')
    # then try to create user with same email
    response=await client.post('/api/users/',json={'username':'mohamed','email':'test@example.com','password':'testpassword123'})
    assert response.status_code==400
    assert response.json()['detail']=='this user already exist'
    # then try to create user with same username
    response=await client.post('/api/users/',json={'username':'testuser','email':'test@example.com','password':'testpassword123'})
    assert response.status_code==400
    assert response.json()['detail']=='this user already exist'
    # finally try to create user with same username and email
    response=await client.post('/api/users/',json={'username':'testuser','email':'test@example.com','password':'testpassword123'})
    assert response.status_code==400
    assert response.json()['detail']=='this user already exist'
# =========================={Test Login Users}===============================
@pytest.mark.anyio
async def test_login_user_success(client:AsyncClient):
    await create_user(client,username='testuser',email='test@example.com',password='testpassword123')
    response=await client.post('/api/users/token',data={'username':'test@example.com','password':'testpassword123'})
    assert response.status_code==200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()
@pytest.mark.anyio
async def test_login_user_validation_errors(client:AsyncClient):
    # first create user
    await create_user(client)
    # then test with empty body
    response=await client.post('/api/users/token')
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then test with invalid body
    response=await client.post('/api/users/token',data={})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then test with only username
    response=await client.post('/api/users/token',data={'username':'test@example.com'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then test with only password
    response=await client.post('/api/users/token',data={'password':'test'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
# ==========================={Test Get Current User}===============================
@pytest.mark.anyio
async def test_get_current_user_success(client:AsyncClient):
    # create user
    await create_user(client)
    # login user
    token=await login_user(client)
    # get current user
    headers=auth_header(token)
    response=await client.get('/api/users/me',headers=headers)
    assert response.status_code==200
# ==============================={Test Update User Info}=================================
@pytest.mark.anyio
async def test_update_user_success(client:AsyncClient):
    # create user
    user=await create_user(client)
    # login user
    token=await login_user(client)
    headers=auth_header(token)
    # update only username
    response=await client.patch('/api/users/',headers=headers,json={'username':'testuser2'})
    assert response.status_code==202
    data = response.json()
    assert data['username']=='testuser2'
    assert data['email']==user['email']
    assert 'id' in response.json()
    assert 'password' not in response.json()
    assert 'password_hash' not in response.json()
    assert 'hash_password' not in response.json()
    # update only email
    response=await client.patch('/api/users/',headers=headers,json={'email':'test2@example.com'})
    assert response.status_code==202
    data = response.json()
    assert data['username']=='testuser2'
    assert data['email']=='test2@example.com'
    assert 'id' in response.json()
    assert 'password' not in response.json()
    assert 'password_hash' not in response.json()
    assert 'hash_password' not in response.json()
    # update both username and email
    response=await client.patch('/api/users/',headers=headers,json={'username':'testuser3','email':'test3@example.com'})
    assert response.status_code==202
    data = response.json()
    assert data['username']=='testuser3'
    assert data['email']=='test3@example.com'
    assert 'id' in response.json()
    assert 'password' not in response.json()
    assert 'password_hash' not in response.json()
    assert 'hash_password' not in response.json()
@pytest.mark.anyio
async def test_update_user_validation_errors(client:AsyncClient):
    # create user
    await create_user(client)
    # login user
    token=await login_user(client)
    headers=auth_header(token)
    # update user
    # first with empty body
    response=await client.patch('/api/users/',headers=headers)
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with invalid body
    response=await client.patch('/api/users/',headers=headers,data={})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with the same username and email
    response=await client.patch('/api/users/',headers=headers,json={'username':'testuser','email':'test@example.com'})
    assert response.status_code==400
    assert response.json()['detail']=='no defferant in data to update'
# =============================={Test Update User Profile Picture}===============================
@pytest.mark.anyio
async def test_update_user_profile_picture_success(client:AsyncClient):
    # create user
    await create_user(client)
    # login user
    token=await login_user(client)
    headers=auth_header(token)
    # update user profile picture
    test_img_path = Path(__file__).parent / './media/test_img.jpg'
    image_bytes = test_img_path.read_bytes()
    response=await client.patch('/api/users/picture',headers=headers,files={'file':('test_img.jpg',BytesIO(image_bytes),'image/jpeg')}) 
    assert response.status_code==202
    data = response.json()
    assert 'image_file' in data
@pytest.mark.anyio
async def test_update_user_profile_picture_validation_errors(client:AsyncClient):
    # create user
    await create_user(client)
    # login user
    token=await login_user(client)
    headers=auth_header(token)
    # update user profile picture
    # first with empty body
    response=await client.patch('/api/users/picture',headers=headers)
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with invalid body
    response=await client.patch('/api/users/picture',headers=headers,data={})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with too large file
    test_img_path = Path(__file__).parent / './media/sizetest.mp3'
    image_bytes = test_img_path.read_bytes()
    response=await client.patch('/api/users/picture',headers=headers,files={'file':('sizetest.mp3',BytesIO(image_bytes),'audio/mp3')}) 

    assert response.status_code==400
    assert response.json()['detail']=='file is too large, maxmum size is 5MB'
    # then with invalid file
    test_img_path = Path(__file__).parent / './media/typetest.mp3'
    image_bytes = test_img_path.read_bytes()
    response=await client.patch('/api/users/picture',headers=headers,files={'file':('typetest.mp3',BytesIO(image_bytes),'audio/mp3')}) 
    assert response.status_code==400
    assert response.json()['detail']=='Invalid image. please upload a valid imge (JPEG,PNG,GIF,WebP)'
@pytest.mark.anyio
async def test_delete_user_profile_picture(client:AsyncClient):
    # create user
    await create_user(client)
    # login user
    token=await login_user(client)
    headers=auth_header(token)
    # first update user profile picture
    test_img_path = Path(__file__).parent / './media/test_img.jpg'
    image_bytes = test_img_path.read_bytes()
    response=await client.patch('/api/users/picture',headers=headers,files={'file':('test_img.jpg',BytesIO(image_bytes),'image/jpeg')})
    assert response.status_code==202
    assert response.json()['image_file']
    # then delete user profile picture
    response=await client.delete('/api/users/picture',headers=headers)
    assert response.status_code==204
# ======================================{Test Delete User}=====================================
@pytest.mark.anyio
async def test_delete_user_success(client:AsyncClient):
    # create user
    await create_user(client)
    # login user
    token=await login_user(client)
    headers=auth_header(token)
    # delete user
    response=await client.delete('/api/users/',headers=headers)
    assert response.status_code==204
    # try to get current user
    response=await client.get('/api/users/me',headers=headers)
    assert response.status_code==401
    assert response.json()['detail']=='user not found'
    # try to login user
    response=await client.post('/api/users/token',data={'username':'test@example.com','password':'testpassword123'})
    assert response.status_code==401
    assert response.json()['detail']=='Incorrect email or password'
@pytest.mark.anyio
async def test_delete_user_validation_errors(client:AsyncClient):
    # create user
    await create_user(client)
    # login user
    token=await login_user(client)
    headers=auth_header(token)
    # delete user without authorization
    response=await client.delete('/api/users/')
    assert response.status_code==401
    assert response.json()['detail']=='Not authenticated'
# ==============================={Test Change User password}=================================
@pytest.mark.anyio
async def test_change_user_password_success(client:AsyncClient):
    # create user
    await create_user(client)
    # login user
    token=await login_user(client)
    headers=auth_header(token)
    # change user password
    response=await client.patch('/api/users/me/password',headers=headers,json={'current_password':'testpassword123','new_password':'testpassword123'})
    assert response.status_code==200
    assert response.json()['message']=='password changed successfully'
    # try to login user
    response=await client.post('/api/users/token',data={'username':'test@example.com','password':'testpassword123'})
    assert response.status_code==200
@pytest.mark.anyio
async def test_change_user_password_validation_errors(client:AsyncClient):
    # create user
    await create_user(client)
    # login user
    token=await login_user(client)
    headers=auth_header(token)
    # change user password
    # first without authorization
    response=await client.patch('/api/users/me/password',json={'current_password':'testpassword123','new_password':'testpassword123'})
    assert response.status_code==401
    assert response.json()['detail']=='Not authenticated'
    # then with empty body
    response=await client.patch('/api/users/me/password',headers=headers)
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with invalid body
    response=await client.patch('/api/users/me/password',headers=headers,data={})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then without current password
    response=await client.patch('/api/users/me/password',headers=headers,json={'new_password':'testpassword123'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then without new  password
    response=await client.patch('/api/users/me/password',headers=headers,json={'current_password':'testpassword123'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='Field required'
    # then with invalid current password
    response=await client.patch('/api/users/me/password',headers=headers,json={'current_password':'testpassword','new_password':'testpassword123'})
    assert response.status_code==400
    assert response.json()['detail']=='invalid data'
    # then with invalid new password
    response=await client.patch('/api/users/me/password',headers=headers,json={'current_password':'testpassword123','new_password':'test'})
    assert response.status_code==422
    assert response.json()['detail'][0]['msg']=='String should have at least 8 characters'
# # ==============================={Test Forgot User Password}=================================
@pytest.mark.anyio
async def test_forgot_user_password_success(client:AsyncClient): 
    # create user
    await create_user(client)
    # reset user password
    with patch(
        'Routers.user.send_password_reset_email',
        new_callable=AsyncMock,
    )as mock_send:
        response = await client.post(
            '/api/users/forgot_password',
            json={'email': 'test@example.com'},
        )
    assert response.status_code==202
    mock_send.assert_awaited_once()
    call_kwargs = mock_send.call_args.kwargs
    assert call_kwargs['to_email'] == 'test@example.com'
    assert call_kwargs['username'] == 'testuser'
    assert 'token' in  call_kwargs
 