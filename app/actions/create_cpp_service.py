from cookiecutter.main import cookiecutter

from actions.base_create_service import BaseCreateService
from utils import get_unique_output_dir
from core.config import settings


class CreateCPPService(BaseCreateService):
    """Create a C++ service from cpp_cookiecutter template"""
    
    def _create_cookiecutter(self, props: dict) -> str:
        """
        Generate C++ project from cookiecutter template.
        
        Expected props:
            - project_name: Name of the C++ project
            - description: Project description
            - author_name: (optional) Author name
        """
        return cookiecutter(
            settings.COOKIECUTTER_CPP_URL,
            extra_context=props,
            no_input=True,
            output_dir=get_unique_output_dir(),
            accept_hooks=settings.COOKIECUTTER_ACCEPT_HOOKS
        )
