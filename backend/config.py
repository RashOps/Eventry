"""
Fichier permettant de charger et de controler les variables d'environnement du projet
FIchier à la racine : .env
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import List
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings): 
    """
    Centralized configuration management for Eventry.
    Loads variables from the .env file and environment with validation.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database - MongoDB
    mongo_uri: str = Field(
        default="mongodb://localhost:27017/",
        description="MongoDB connection URI",
        min_length=10
    )

    mongo_db_name: str = Field(
        default="eventry",
        description="Main database name",
        min_length=1,
        max_length=64
    )

    # Database - PostegreSQL
    sql_user: str = Field(
        default="Admin",
        description="POSTEGRESQL USER",
        alias="SQL_USER"
    )

    sql_password: str = Field(
        default="12345678",
        description="POSTGRESQL PASSWORD CONNECTION",
        alias="SQL_PASSWORD"
    )

    sql_database: str = Field(
        default="Eventry",
        description="POSTEGRESQL DATABASE",
        alias="SQL_DATABASE"
    )

    sql_port: int = Field(
        default=5432,
        description="POSTEGRESQL PORT DOCKER",
        alias="SQL_PORT"
    )

    sql_host: str = Field(
        default="localhost",
        description="POSTEGRESQL HOST",
        alias="SQL_HOST"
    )

    # CORS ORIGIN
    cors_origins: List[str] = Field(
        default=["http://localhost:5173"],
        description="Allowed CORS origins"
    )

settings = Settings()