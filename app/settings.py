from os import getenv

BASE_ROUTE = getenv("BASE_ROUTE", "/credhive")
DATABASE_URL = getenv("DATABASE_URL", "postgresql+asyncpg://udit@localhost:5432/udit")
