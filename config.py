from dataclasses import dataclass
from pathlib import Path

XML_DIR = Path(__file__).parent / "xml"


@dataclass
class DatabaseSettings:
    db_host: str = "localhost"
    db_port: str = "5432"
    db_username: str = "postgres"
    db_password: str = ""
    db_
