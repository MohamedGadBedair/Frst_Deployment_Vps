import pytest 
from httpx import AsyncClient
from conftest import auth_header,create_user,login_user

# ===================={Test Get Posts}====================================
@pytest.mark.anyio
async def test_post_not_found(client:AsyncClient):
    
    response=await client.get('/api/posts/99')

    assert response.status_code==404
    assert response.json()['detail']=='post not found'
@pytest.mark.anyio
async def test_posts_empty(client:AsyncClient):
    
    response=await client.get('/api/posts')

    assert response.status_code==200
    data=response.json()
    assert data['posts']==[]
    assert data['total']==0
    assert data['has_more'] is False
@pytest.mark.anyio
async def test_get_post_with_pagination(client:AsyncClient):
    # first create user
    await create_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    # then create num of posts
    for i in range(20):
        response = await client.post(
            '/api/posts/',
            json={
                'title':f'My First Post {i}',
                'content':f'This Is The Content {i}'
            },
            headers=headers,
        )
    assert response.status_code==201
    # get post with pagination
    response = await client.get('/api/posts?skip=5&limit=5')
    assert response.status_code==200
    data=response.json()
    assert data['posts'][0]['title']=='My First Post 5'
    assert data['total']==20
    assert data['skip']==5
    assert data['limit']==5
    assert data['has_more'] is True
# ====================={Test Create Post}=================================
@pytest.mark.anyio
async def test_create_post_success(client:AsyncClient):
    # first create user
    user=await create_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    # then create post
    response = await client.post(
        '/api/posts/',
        json={
            'title':'My First Post',
            'content':'This Is The Content'
        },
        headers=headers,
    )
    assert response.status_code==201
    data=response.json()
    assert data['title']=='My First Post'
    assert data['content']=='This Is The Content'
    assert data['author']['username']==user['username']
@pytest.mark.anyio
async def test_create_post_unauthorized(client:AsyncClient):
    response=await client.post(
        '/api/posts/',
        json={
            'title':'My First Post',
            'content':'This Is The Content'
            })

    assert response.status_code==401
    assert response.json()['detail']=='Not authenticated'
# ====================={Test Update Post}==================================
@pytest.mark.anyio
async def test_update_post_success(client:AsyncClient):
    # first create user
    user=await create_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    # then create post
    response = await client.post(
        '/api/posts/',
        json={
            'title':'My First Post',
            'content':'This Is The Content'
        },
        headers=headers,
    )
    assert response.status_code==201
    data=response.json()
    assert data['title']=='My First Post'
    assert data['content']=='This Is The Content'
    assert data['author']['username']==user['username']
    post_id=data['id']
    # finally update post
    response = await client.patch(
        f'/api/posts/{post_id}',
        json={
            'title':'Updated My First Post',
            'content':'This Is The Content After Update'
        },
        headers=headers,
    )

    assert response.status_code==200
    data=response.json()
    assert data['title']=='Updated My First Post'
    assert data['content']=='This Is The Content After Update'
    assert data['author']['username']==user['username']
@pytest.mark.anyio
async def test_update_post_unauthorized(client:AsyncClient):
    # first create user
    user=await create_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    # then create post
    response = await client.post(
        '/api/posts/',
        json={
            'title':'My First Post',
            'content':'This Is The Content'
        },
        headers=headers,
    )
    assert response.status_code==201
    data=response.json()
    assert data['title']=='My First Post'
    assert data['content']=='This Is The Content'
    assert data['author']['username']==user['username']
    post_id=data['id']
    # create another user
    await create_user(client,username='newuser',email='new@example.com',password='newpassword')
    token2 = await login_user(client,user_email='new@example.com',user_password='newpassword')
    headers2 = auth_header(token2)
    # finally update post with another user
    response = await client.patch(
        f'/api/posts/{post_id}',
        json={
            'title':'Updated My First Post',
            'content':'This Is The Content After Update'
        },
        headers=headers2,
    )

    assert response.status_code==403
    assert response.json()['detail']=='you are not authorized for edit in this post'
# ====================={Test Delete Post}==================================
@pytest.mark.anyio
async def test_delete_post_success(client:AsyncClient):
    # first create user
    user=await create_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    # then create post
    response = await client.post(
        '/api/posts/',
        json={
            'title':'My First Post',
            'content':'This Is The Content'
        },
        headers=headers,
    )
    assert response.status_code==201
    data=response.json()
    assert data['title']=='My First Post'
    assert data['content']=='This Is The Content'
    assert data['author']['username']==user['username']
    post_id=data['id']
    
    # finally delete post
    response = await client.delete(
        f'/api/posts/{post_id}',
        headers=headers,
    )

    assert response.status_code==204
@pytest.mark.anyio
async def test_delete_post_unauthorized(client:AsyncClient):
    # first create user
    user=await create_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    # then create post
    response = await client.post(
        '/api/posts/',
        json={
            'title':'My First Post',
            'content':'This Is The Content'
        },
        headers=headers,
    )
    assert response.status_code==201
    data=response.json()
    assert data['title']=='My First Post'
    assert data['content']=='This Is The Content'
    assert data['author']['username']==user['username']
    post_id=data['id']
    
    # create another user
    await create_user(client,username='newuser',email='new@example.com',password='newpassword')
    token2 = await login_user(client,user_email='new@example.com',user_password='newpassword')
    headers2 = auth_header(token2)
    
    # finally try to delete post with another user
    response = await client.delete(
        f'/api/posts/{post_id}',
        headers=headers2,
    )

    assert response.status_code==403
    assert response.json()['detail']=='you are not authorized for delete this post'