from fastapi import APIRouter

links_api = APIRouter(
    tags=["links"],
    prefix="/links",
)
