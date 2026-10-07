from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy import select
from sqlalchemy.orm import load_only,selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from auth import CurrentUser
from models import Post
from database import get_db
from schemas import (
    PostCreate,
    PostUpdata,
    PostResponse,
    PaginationPostResponse
     )

from service.pagination_utils import Api_pagination_post

router=APIRouter()

# =================================== {PostsAPIS} =======================================

# get posts in the database
@router.get(
        "",
        status_code=status.HTTP_200_OK,
        response_model=PaginationPostResponse
        )
async def get_post(pagination_post:Annotated[PaginationPostResponse,Depends(Api_pagination_post)]):
    return pagination_post

# Create Post API
@router.post(
        '/',
        response_model=PostResponse,
        status_code=status.HTTP_201_CREATED)
async def create_post(post:PostCreate,db:Annotated[AsyncSession,Depends(get_db)],current_user:CurrentUser):
    
    new_post=Post(
    title=post.title,
    content=post.content,
    author_id=current_user.id,
    author=current_user
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post,attribute_names=['author'])
    return new_post
# Get Posts API
@router.get(
        "/{post_id}",
        status_code=status.HTTP_200_OK,
        response_model=PostResponse
        )
async def get_post(post_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    # db_post= db.query(Post).options(selectinload(Post.author)).filter(id==post_id).first()
    post_q=await db.execute(select(Post).options(selectinload(Post.author)).where(Post.id==post_id))
    post = post_q.scalars().first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='post not found')
    
    post=post
    return post

# Delete Post API
@router.delete(
        '/{post_id}',
        status_code=status.HTTP_204_NO_CONTENT
        )
async def delete_post(post_id:int,db:Annotated[AsyncSession,Depends(get_db)],current_user:CurrentUser):
    
    post_q=await db.execute(select(Post).options(load_only(Post.title,Post.author_id)).where(Post.id == post_id))
    post=post_q.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'post with id {post_id} not found')
    
    if post.author_id!=current_user.id :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not authorized for delete this post",
            headers={'WWW-Authenticate':'Bearer'}
        )
    
    await db.delete(post)
    await db.commit()

# Update Post API
@router.patch(
        "/{post_id}",
        status_code=status.HTTP_200_OK,
        response_model=PostResponse
        )
async def update_post(post_id:int,post:PostUpdata,db:Annotated[AsyncSession,Depends(get_db)],current_user:CurrentUser):
    count=0

    # db_post=db.query(Post).options(load_only(Post.title,Post.content)).filter(Post.id==post_id).first()
    db_post_q= await db.execute(select(Post).options(selectinload(Post.author)).where(Post.id==post_id))
    db_post = db_post_q.scalars().first()

    if not db_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='this post not found')
    
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not authorized for edit in this post",
            headers={'WWW-Authenticate':'Bearer'}
        )

    if post.title:
        db_post.title=post.title
    else:count+=1

    if post.content:
        db_post.content=post.content
    else:count+=1
    
    if count == 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='no change happend')
    else:
        await db.commit()
        await db.refresh(db_post,attribute_names=['author'])
        return(db_post)
