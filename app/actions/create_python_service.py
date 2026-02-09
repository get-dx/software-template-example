from cookiecutter.main import cookiecutter

from actions.base_create_service import BaseCreateService
from utils import get_unique_output_dir
from core.config import settings


class CreatePythonService(BaseCreateService):
    """Create a Python package from cookiecutter-pypackage template"""
    
    def _create_cookiecutter(self, props: dict) -> str:
        """
        Generate Python package from cookiecutter template.
        
        Expected props:
            - project_name: Name of the Python project
            - project_slug: Project slug (package name)
            - project_short_description: Project description
            - full_name: (optional) Author full name
            - email: (optional) Author email
        """
        return cookiecutter(
            settings.COOKIECUTTER_PYTHON_URL,
            extra_context=props,
            no_input=True,
            output_dir=get_unique_output_dir(),
            accept_hooks=settings.COOKIECUTTER_ACCEPT_HOOKS
        )
