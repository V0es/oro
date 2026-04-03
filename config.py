from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

XML_DIR = Path(__file__).parent / "xml"
XLSX_FILE = Path(__file__).parent / "responses.xlsx"


class DatabaseSettings(BaseModel):
    type: str = "postgresql"
    driver: str = "psycopg"
    host: str = "postgres"
    port: str = "5432"
    username: str = "postgres"
    password: str = "password"
    name: str = "postgres"

    def get_url(self) -> str:
        return f"{self.type}+{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


class XMLSettings(BaseModel):
    directory: Path = XML_DIR
    categories_path: str = "variables/categories"
    question_path: str = "metadata/questions/question"


class XLSXSettings(BaseModel):
    directory: Path = XLSX_FILE


class OutputSettings(BaseModel):
    folder: Path = Path(__file__).parent / "output"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )
    database: DatabaseSettings = DatabaseSettings()
    xml: XMLSettings = XMLSettings()
    xlsx: XLSXSettings = XLSXSettings()
    output: OutputSettings = OutputSettings()


@lru_cache()
def get_settings() -> Settings:
    return Settings()
