import uvicorn
from fastapi import FastAPI

from database.database import engine
from database import db_models

from routers import users, teams, project_boards


db_models.Base.metadata.create_all(bind=engine)
app = FastAPI()


app.include_router(users.router)
app.include_router(teams.router)
app.include_router(project_boards.router)


@app.get("/")
def root():
    return {"message": "Hello This is FactWise Board"}


if __name__ == '__main__':
    uvicorn.run(app)
