from contextlib import asynccontextmanager
from typing import Annotated

from fastapi.exceptions import RequestValidationError,HTTPException
from fastapi import FastAPI, Request, Depends,status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

 
from sqlalchemy import select,text
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, get_db
from Routers import user, post
import models
from schemas import PaginationPostResponse

from service.pagination_utils import Home_pagination_post,user_pagination_post

#=================================={app creation}=====================================
@asynccontextmanager
async def lifespan(_app:FastAPI):
    yield
    # shutdown
    await engine.dispose()
app=FastAPI(lifespan=lifespan)
#==================================={files connection}=================================
app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/media', StaticFiles(directory='media'), name='media')
templates= Jinja2Templates("templates")
#===================================={API Routers}=====================================
app.include_router(user.router,prefix='/api/users',tags=['Users'])
app.include_router(post.router,prefix='/api/posts',tags=['Posts'])
# =================================={ Helth Chick Route }=========================================
@app.get('/health')
async def health_chick(db:Annotated[AsyncSession,Depends(get_db)]):
    try:
        await db.execute(text('SELECT 1'))
    except Exception as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='database unavailable'
        )from exc
    return{'status':'healthy'}
# =================================={Web Pages}=========================================
# User Login Page
@app.get('/login',include_in_schema=False)
async def login_page(request:Request):
    return templates.TemplateResponse(
        request,
        'login.html',
        {'title':'login'}
    )
# User Register page
@app.get('/register',include_in_schema=False)
async def register_page(request:Request):
    return templates.TemplateResponse(
        request,
        'register.html',
        {'titel':'Register'}
    )
# User Account Page
@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )

@app.get("/forgot-password", include_in_schema=False)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request,
        "forgot_password.html",
        {"title": "Forgot Password"},
    )

@app.get("/reset-password", include_in_schema=False)
async def reset_password_page(request: Request):
    response = templates.TemplateResponse(
        request,
        "reset_password.html",
        {"title": "Reset Password"},
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

# ------------------------------------------------------------------------
# Home Page
@app.get('/posts',name='posts',include_in_schema= False)
@app.get('/',name='home', include_in_schema= False)
async def home(
    request:Request,
    pagination_posts:Annotated[
        PaginationPostResponse,
        Depends(Home_pagination_post)
        ]
    ):
    
    return templates.TemplateResponse(
        request,
        'home.html',
        {
            'posts': pagination_posts.posts,
            'total':pagination_posts.total,
            'skip':pagination_posts.skip,
            "limit":pagination_posts.limit,
            'has_more':pagination_posts.has_more,
            'title': 'home',
        }
    )
# Post View Page
@app.get(
        "/post/{post_id}",
        name='post_page',
        include_in_schema= False
        )
async def get_post(
    request:Request,
    post_id:int,
    db:Annotated[AsyncSession,Depends(get_db)]
    ):
    # db_post= db.query(models.Post).options(selectinload(models.Post.author)).filter(models.Post.id==post_id).first()
    q = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id==post_id).order_by(models.Post.created_at.desc()))
    post = q.scalars().first()
    if post:
        return templates.TemplateResponse(
            request,
            'post.html',
            {
                'post':post,
                'title':'home',
            }
        )
    else:
        return templates.TemplateResponse(
            request,
            'error.html',
            {
                'message':'post not found',
                'title':'Error_404'
            },
            status_code=404
        )
# User Posts Page
@app.get(
    '/user/{user_id}/posts',
    include_in_schema=False,
    name='user_posts'
    )
async def user_posts_page(
    request:Request,
    pagination_posts:Annotated[
        PaginationPostResponse,
        Depends(user_pagination_post)
        ]
    ):
    
    return templates.TemplateResponse(
        request,
        'home.html',
        {
            'posts': pagination_posts.posts,
            'total':pagination_posts.total,
            "limit":pagination_posts.limit,
            'has_more':pagination_posts.has_more,
            'title': 'user_posts',
        }
    )
# ------------------------------------------------------------------------
# Exception Handling
@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
