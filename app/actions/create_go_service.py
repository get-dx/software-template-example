from cookiecutter.main import cookiecutter

from actions.base_create_service import BaseCreateService
from utils import get_unique_output_dir
from core.config import settings


class CreateGoService(BaseCreateService):
    """Create a Go service from cookiecutter-golang template"""
    
    def _create_cookiecutter(self, props: dict) -> str:
        """
        Generate Go project from cookiecutter template.
        
        Expected props:
            - app_name: Name of the Go application
            - project_short_description: Project description
            - docker_hub_username: (optional) Docker Hub username
            - docker_image: (optional) Docker image name
        """
        return cookiecutter(
            settings.COOKIECUTTER_GO_URL,
            extra_context=props,
            no_input=True,
            output_dir=get_unique_output_dir()
        )
