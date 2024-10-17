from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.chats import chats_router
from backend.routers.users import users_router
from backend.auth import auth_router
from backend.database import create_db_and_tables

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Pony Express API",
    description="API for managing express ponies or something idk.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(chats_router)
app.include_router(users_router)


@app.get("/", include_in_schema=False)
def default() -> str:
    return HTMLResponse(
        content=f"""
        <html>
            <body>
                <h1>{app.title}</h1>
                <p>{app.description}</p>
                <h2>API docs</h2>
                <ul>
                    <li><a href="/docs">Swagger</a></li>
                    <li><a href="/redoc">ReDoc</a></li>
                </ul>
            </body>
        </html>
        """,
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://52.34.77.97", "http://4550.najmanhusaini.com", "https://4550.najmanhusaini.com", "https://api.4550.najmanhusaini.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
