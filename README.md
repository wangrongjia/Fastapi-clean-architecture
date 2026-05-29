# FastAPI Clean Architecture

A **minimalistic production-ready FastAPI project template** following a modular and clean architecture principles.

I was confused to see many starter projects on github with unstructured code and inconsistent project structure, and with go guidelines for setting up a FastAPI project for beginners. I wanted to have a good starting point for my FastAPI projects and I could not find one anywhere online. So I decided to create one from scratch.

You can go through the git history to see how this project has evovled from a single `main.py` file to this current state of structured architecture.

- the starting main.py file is taken from the code example in the fastapi official docs. These docs are very well written with good explanations by Sebastián Ramírez (tiangolo), the creator of FastAPI and SQLModel libraries used in this project)

There are still a couple of things I want to do (like refactoring and adding new things) to make this as complete as possible for my use cases, and I'll try updating this over time.

## Features

- A minimalistic FastAPI application with **modular and clearn architecture**
  - specifically, **controller-service-repository** layered architecture
  - controller layer: for handling **HTTP requests and routing**
  - service layer: for handling **business logic and data access**
  - repository layer: for handling **database operations**
- Database integration using **SQLModel** (uses **SQLAlchemy** under the hood)
- Creating multiple database models with inheritance using SQLModel (which also uses Pydantic under the hood)
- Database migrations with **Alembic**
- Project wide settings configuration using **Pydantic-settings** (a separate mini library from **Pydantic**)
- **Dockerfile and docker-compose** set up for containerized development, and possibly production deployment
- Testing (using in-memory instead of file memory) with **Pytest** and mocking support from **Pytest-mock** plugin for pytest
- Sample **api.http** file for testing API endpoints in VSCode (REST Client extension is needed)

---

### Dependencies

- **uv**: for python project and virtual environment setup and management
- **git**: for tracking code changes and version control
- **fastapi**: for API!
- **sqlmodel**: for database tables and data models (uses sqlalchemy and pydantic under the hood)
- **alembic**: for database migrations
- **pydantic**: for data validation and serialization
- **pydantic-settings**: for project wide configuration settings
- **pytest**: for testing, with fixures (dependencies) confuration in conftest.py
- **pytest-mock**: (plugin for pytest) for mocking database repository while testing the service layer
- **logging**: for basic logging including logging to file and console set up
- **postgresql**: SQL database (can be replaced with **SQLite** in the configuration settings)
- **dockerfile**: for containerizing fastapi app
- **docker-compose**: for creating and running all services at once: fastapi-app, postgresql, alembic, and pgadmin services.
- **run.sh**: script file for making sure to start postgresql server on local machine before starting the fastapi server
- **api.http**: for testing the api inside vscode IDE (need REST Client vscode extension) with pre-defined API test endpoints

## Project tree structure

```txt
.
├── app/                                   # FastAPI application code
│   ├── models/                            # Database models and Pydantic schemas
│   │   ├── hero_models.py                 # Hero model and schema definitions
│   │   └── __init__.py                    # Marks models/ as a Python package
│   ├── repositories/                      # Database access layer (CRUD operations)
│   │   ├── hero_repository.py             # Hero repository for DB operations
│   │   └── __init__.py                    # Marks repositories/ as a Python package
│   ├── routers/                           # API route definitions
│   │   ├── hero_router.py                 # Hero-related API endpoints
│   │   └── __init__.py                    # Marks routers/ as a Python package
│   ├── services/                          # Business logic layer
│   │   ├── hero_service.py                # Hero-related service functions
│   │   └── __init__.py                    # Marks services/ as a Python package
│   ├── config.py                          # Project-wide configuration settings
│   ├── db.py                              # Database connection setup
│   ├── dependencies.py                    # FastAPI dependency injections
│   ├── logging_config.py                  # Logging setup (console + file)
│   └── main.py                            # FastAPI application entrypoint
│   ├── __init__.py                        # Marks app/ as a Python package
├── logs/                                  # Log folder
│   ├── app.log                            # Log output file
│   └── .gitkeep                           # Placeholder file to track logs/ folder
├── migrations/                            # Alembic database migration scripts
│   ├── versions/                          # Auto-generated migration scripts
│   │   └── 1350d4a96879_init_migratin.py  # Initial DB migration
│   ├── env.py                             # Alembic environment configuration
│   ├── README                             # Alembic folder usage notes
│   └── script.py.mako                     # Alembic migration template script
├── tests/                                 # Automated tests
│   ├── test_repositories/                  # Tests for database repositories
│   │   ├── __init__.py
│   │   └── test_hero_repository.py         # Tests for Hero repository
│   ├── test_routers/                       # Tests for API routes
│   │   ├── __init__.py
│   │   └── test_hero_router.py             # Tests for Hero API endpoints
│   ├── test_services/                      # Tests for business logic services
│   │   ├── __init__.py
│   │   └── test_hero_service.py            # Tests for Hero services
│   ├── conftest.py                         # Pytest fixtures and setup
│   └── __init__.py                         # Marks tests/ as a Python package
├── alembic.ini                             # Alembic configuration file
├── api.http                                # Predefined HTTP requests for testing APIs in VSCode
├── database.db                             # Local SQLite database (if used in config.py file)
├── docker-compose.yml                      # Docker Compose setup for app + services
├── Dockerfile                              # Docker image definition for FastAPI app
├── .dockerignore                           # Files/folders to ignore when building Docker image
├── .env                                    # Environment variables for local development
├── .env-example                            # Example environment variables template
├── .gitignore                              # Files/folders ignored by Git
├── pyproject.toml                          # Python project metadata and dependencies
├── .python-version                         # Python version manager file (e.g., pyenv)
├── README.md                               # Project documentation
├── run.sh                                  # Script to start local DB and FastAPI server
└── uv.lock                                 # Dependency lock file created by UV package manager
```

## Running this project

### Locally

```bash
uv run fastapi dev app/main.py --port 8083

# OR

./run.sh
```

### Using Docker

```bash
docker-compose up --build
```

## Testing the API

- FastAPI's Swagger UI: http://localhost:8083/docs

OR

- Run inside VSCode with the "REST Client" extension
- in api.http file

## Inspiration

- FastAPI official docs
- SQLModel official docs
- `controller-service-repository` architecture from CodeWithMosh
