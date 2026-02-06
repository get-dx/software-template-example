from cookiecutter.main import cookiecutter

from actions.base_create_service import BaseCreateService
from utils import get_unique_output_dir


class CreateCustomService(BaseCreateService):
    """Create a service from a custom cookiecutter template URL"""
    
    def __init__(self, cookiecutter_url: str):
        """
        Initialize with a custom cookiecutter template URL.
        
        Args:
            cookiecutter_url: URL to the cookiecutter template repository
        """
        self.cookiecutter_url = cookiecutter_url
    
    def _create_cookiecutter(self, props: dict) -> str:
        """
        Generate project from custom cookiecutter template.
        
        Args:
            props: Template-specific properties (varies by template)
        """
        return cookiecutter(
            self.cookiecutter_url,
            extra_context=props,
            no_input=True,
            output_dir=get_unique_output_dir()
        )
