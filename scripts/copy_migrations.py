import io
import logging
import os
import tarfile
from enum import Enum
from pathlib import Path, PurePosixPath

import docker
import dotenv
from docker.models.containers import Container

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

dotenv.load_dotenv(ENV_FILE)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class KindEnum(Enum):
    MODIFY = 0
    ADD = 1
    DELETE = 2


def get_new_migrations(container: Container) -> list[PurePosixPath]:
    migration_files = []
    changes = container.diff()
    for change in changes:
        path: str = change["Path"]
        kind: int = change["Kind"]
        if (
            kind == KindEnum.ADD.value and
            "migrations" in path and
            path.endswith(".py")
        ):
            logger.info(f"Detected new migration file: {path}")
            migration_files.append(PurePosixPath(path))
    
    return migration_files


def copy_files(container: Container, migration_file_paths: list[PurePosixPath]) -> None:
    for file_path in migration_file_paths:
        destination_path = (BASE_DIR / file_path.relative_to("/app")).parent

        try:
            bits, _ = container.get_archive(file_path.as_posix())
            file_like = io.BytesIO(b"".join(bits))
            with tarfile.open(fileobj=file_like) as tar:
                tar.extractall(path=destination_path)
        except Exception as e:
            logger.error(f"Error while copying {file_path}: {e}")


if __name__ == "__main__":
    web_container_name = os.environ.get("WEB_CONTAINER_NAME")
    if not web_container_name:
        raise KeyError("Unable to load WEB_CONTAINER_NAME from env")

    client = docker.from_env()
    container = client.containers.get(web_container_name)

    new_migration_files = get_new_migrations(container)

    copy_files(container, new_migration_files)
