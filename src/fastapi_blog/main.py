from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi_blog.schemas import PostCreate, PostResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
posts: list[dict] = [
  {"id": 1, "title": "First Post", "lead": "This is the content of the first post.", "duration": "5", "date_posted": "2024-06-01"},
  {"id": 2, "title": "Second Post", "lead": "This is the content of the second post.", "duration": "5", "date_posted": "2024-06-02"}
]

@app.get("/", include_in_schema=False, name="home")
def home(request: Request):
  return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"})

@app.get("/posts/{post_id}", include_in_schema=False, name="post_page")
def post_page(request: Request,post_id: int):
  for post in posts:
    if post.get("id") == post_id:
      title = post['title'][:50]
      return templates.TemplateResponse(request, "post.html", {"post": post, "title": title})
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
  return posts

@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
  new_id = max(post.get("id", 0) for post in posts) + 1 if posts else 1
  new_post = {
    "id": new_id,
    "title": post.title,
    "lead": post.lead,
    "duration": post.duration,
    "date_posted": "2024-06-03"
  }
  posts.append(new_post)
  return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
  for post in posts:
    if post.get("id") == post_id:
      return post
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request:Request, exception: StarletteHTTPException):
  message = (
    exception.detail
    if exception.detail
    else "An error occurred. Please check your request and try again."
  )

  if request.url.path.startswith("/api"):
    return JSONResponse(
      status_code=exception.status_code,
      content={"detail": message},
    )

  return templates.TemplateResponse(
      request,
      "error.html",
      {
        "status_code": exception.status_code,
        "title": exception.status_code,
        "message": message,
      },
      status_code=exception.status_code
    )

@app.exception_handler(RequestValidationError)
def general_http_exception_handler(request:Request, exception: RequestValidationError):

  if request.url.path.startswith("/api"):
    return JSONResponse(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
      content={"detail": exception.errors()},
    )

  return templates.TemplateResponse(
      request,
      "error.html",
      {
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
        "message": "Invalid request. Please check your input and try again.",
      },
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )