from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.links.api import links_api
from app.api.parents_list.api import parents_list_router
from app.api.school.api import school_router
from app.api.user_information.api import user_information_router
from app.auth.api import auth_router
from app.emailmanager.api import email_router
from app.settings import FRONTEND_URL

app = FastAPI()

origins = [
    f"{FRONTEND_URL}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(email_router)
app.include_router(user_information_router)
app.include_router(school_router)
app.include_router(parents_list_router)
app.include_router(links_api)
