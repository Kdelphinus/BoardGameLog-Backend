import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from domain.user import user_router

app = FastAPI()
load_dotenv()

# CORS 해결
origins = [f"http://{os.getenv("BASE_IP")}"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
