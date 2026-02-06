import uuid
from core.config import settings


def get_unique_output_dir() -> str:
    """Generate a unique output directory path for cookiecutter"""
    unique_id = str(uuid.uuid4())
    return settings.COOKIECUTTER_OUTPUT_DIR.format(uuid=unique_id)
