from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.user_information.api import user_information_router
from app.auth.api import auth_router

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI()


app.include_router(auth_router)
app.include_router(user_information_router)
