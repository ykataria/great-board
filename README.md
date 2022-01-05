# FactWise Board
### _Project Boards made easy_


This project assists in project management by providing user, team, task and board manager

- Awesome tool for project management
- Add Users, Teams, Tasks and boards

### About

Project is developed over the provided files implmenting the methods, for persistence used SQLite with SqlAlchemy ORM.
Later wrapped the functions and exposed endpoints using FastAPI.

All SqlAlchemy models along with connection details etc are defined in the database package.
Keeping the scope of project in mind no data mirgation tool like Alembic is used (This could be definately be a future enhancement).

For logging Loguru is used with custom defined logging colors and format.

##### Folder structure
- main.py: This is the root of the project for starting application
- DB, Out: folders for storing db and export files resp
- database: Contains database connection, database models
- services: Consists of service files assisting in differnt service
- routers: has differnt routers
- models: has pydantic models
- utils, constants, etc: includes all other files and packages

## Tech

All the project requirements are written in requirements.txt file in root folder:

Major dependecies:
- fastapi==0.70.1
- pydantic==1.9.0
- SQLAlchemy==1.4.29
- tabulate==0.8.9

## Installation
In order to run, use following

```
cd factwise-python
python main.py
```
This should start uvicorn server on localhost port 8000.
In order to access the services use the endpoints exposed for respective service and function. These can directly be tested from browser, open:

```sh
http://127.0.0.1:8000/docs
```
to access Swagger docs. This constains info about each API endpoint helping in respective functionality.

Database can be accessed standalone either using sqlite command line or SQLite Studio: https://sqlitestudio.pl/

## Other Info
There are many enhancements and better logic/techniques due to time conststraint and keeping in mind the scope of the project I tried implementing functionality keeping best practices in mind :)


## License
None

**Free Software, It was a fun Poroject Assignment :)**
