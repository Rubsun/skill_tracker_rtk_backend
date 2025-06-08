from dataclasses import dataclass

import toml


@dataclass
class DatabaseConfig:
    user: str
    password: str
    name: str
    host: str
    port: int

    def __post_init__(self) -> None:
        self.uri = (
            f"postgresql+asyncpg://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.name}"
        )



@dataclass
class Config:
    db: DatabaseConfig


def load_config(config_path: str) -> Config:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)
    return Config(
        db=DatabaseConfig(**data["db"]),
    )
