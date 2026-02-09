from cookiecutter.main import cookiecutter

from actions.base_create_service import BaseCreateService
from utils import get_unique_output_dir
from core.config import settings


class CreateDjangoService(BaseCreateService):
    """Create a Django service from cookiecutter-django template"""
    
    def _create_cookiecutter(self, props: dict) -> str:
        """
        Generate Django project from cookiecutter template.
        
        Expected props:
            - project_name: Name of the Django project
            - description: Project description
            - author_name: (optional) Author name
            - email: (optional) Author email
        
        Note: Post-generation hooks are controlled by COOKIECUTTER_ACCEPT_HOOKS setting.
        The Django template hooks require 'uv' and other dependencies. If hooks are
        disabled, the project structure will be complete but users need to run
        setup commands manually.
        """
        return cookiecutter(
            settings.COOKIECUTTER_DJANGO_URL,
            extra_context=props,
            no_input=True,
            output_dir=get_unique_output_dir(),
            accept_hooks=settings.COOKIECUTTER_ACCEPT_HOOKS
        )
