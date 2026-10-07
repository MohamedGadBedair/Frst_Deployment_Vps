from typing import Annotated
from sqlalchemy import select,func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query, Depends
from database import get_db
from models import Post
from config import settings
from schemas import (
    PaginationPostResponse,
    PostResponse
     )

async def Api_pagination_post(
    db:Annotated[AsyncSession,Depends(get_db)],
    skip:Annotated[int,Query(ge=0)]=0,
    limit:Annotated[int,Query(ge=1,le=100)]=settings.post_per_page
    ):

    count_result = await db.execute(select(func.count()).select_from(Post))
    total = count_result.scalar() or 0

    posts_q=await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .order_by(Post.created_at.desc())
        .offset(skip).limit(limit)
        )
    
    posts = posts_q.scalars().all()
    
    has_more =skip + len(posts)< total
    
    return PaginationPostResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
        )


async def user_pagination_post(
    user_id:int,
    db:Annotated[AsyncSession,Depends(get_db)],
    skip:Annotated[int,Query(ge=0)]=0,
    limit:Annotated[int,Query(ge=1,le=100)]=settings.post_per_page,
    ):

    count_result = await db.execute(select(func.count()).select_from(Post).where(Post.author_id==user_id))
    total = count_result.scalar() or 0

    posts_q=await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.author_id==user_id)
        .order_by(Post.created_at.desc())
        .offset(skip).limit(limit)
        )
    
    posts = posts_q.scalars().all()
    
    has_more =skip + len(posts)< total
    
    return PaginationPostResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
        )


async def user_pagination_post(
    user_id:int,
    db:Annotated[AsyncSession,Depends(get_db)],
    skip:Annotated[int,Query(ge=0)]=0,
    limit:Annotated[int,Query(ge=1,le=100)]=settings.post_per_page,
    ):

    count_result = await db.execute(select(func.count()).select_from(Post).where(Post.author_id==user_id))
    total = count_result.scalar() or 0

    posts_q=await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.author_id==user_id)
        .order_by(Post.created_at.desc())
        .offset(skip).limit(limit)
        )
    
    posts = posts_q.scalars().all()
    
    has_more =skip + len(posts)< total
    
    return PaginationPostResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
        )

async def Home_pagination_post(
    db:Annotated[AsyncSession,Depends(get_db)],
    limit:Annotated[int,Query(ge=1,le=100)]=settings.post_per_page
    ):

    count_result = await db.execute(select(func.count()).select_from(Post))
    total = count_result.scalar() or 0

    posts_q=await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .order_by(Post.created_at.desc())
        .limit(limit)
        )
    
    posts = posts_q.scalars().all()
    
    has_more = len(posts)< total
    
    return PaginationPostResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        limit=limit,
        has_more=has_more
        )
