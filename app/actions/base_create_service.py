import logging
import shutil
from typing import Literal
from abc import ABC, abstractmethod

from clients import git, github
from core.config import settings

logger = logging.getLogger(__name__)


class BaseCreateService(ABC):
    """
    Base class for creating services from templates.
    Subclasses implement specific template logic.
    """
    
    def create(
        self,
        github_org: str,
        github_repo: str,
        props: dict
    ) -> Literal['FAILURE', 'SUCCESS']:
        """
        Main method to create a service from a template.
        
        Args:
            github_org: GitHub organization or username
            github_repo: Repository name
            props: Template-specific properties
            
        Returns:
            'SUCCESS' or 'FAILURE'
        """
        project_dir = None
        try:
            logger.info(f"{self.__class__.__name__} - Starting service creation")
            
            # Step 1: Generate project from cookiecutter template
            logger.info(f"{self.__class__.__name__} - Generating from cookiecutter template")
            project_dir = self._create_cookiecutter(props)
            
            # Step 2: Create GitHub repository
            logger.info(f"{self.__class__.__name__} - Creating GitHub repository")
            description = props.get('description', '') or props.get('project_short_description', '')
            github.create_repo(github_org, github_repo, description=description)
            
            # Step 3: Initialize git repository
            logger.info(f"{self.__class__.__name__} - Initializing git repository")
            repo = git.init_repo(project_dir)
            
            # Step 4: Push all files to GitHub
            logger.info(f"{self.__class__.__name__} - Uploading files to GitHub")
            git.upload_all_files(
                repo, 
                github_org, 
                github_repo,
                exclude_workflows=settings.EXCLUDE_GITHUB_WORKFLOWS
            )
            
            logger.info(f"{self.__class__.__name__} - Service created successfully")
            return 'SUCCESS'
            
        except Exception as err:
            logger.error(f"{self.__class__.__name__} - Error creating service: {err}", exc_info=True)
            return 'FAILURE'
            
        finally:
            # Clean up temporary directory
            if project_dir:
                try:
                    logger.info(f"{self.__class__.__name__} - Cleaning up temporary directory")
                    shutil.rmtree(project_dir)
                except Exception as e:
                    logger.warning(f"Failed to clean up directory {project_dir}: {e}")
    
    @abstractmethod
    def _create_cookiecutter(self, props: dict) -> str:
        """
        Create a project from a cookiecutter template.
        Must be implemented by subclasses.
        
        Args:
            props: Template-specific properties
            
        Returns:
            Path to the generated project directory
        """
        raise NotImplementedError("Subclasses must implement '_create_cookiecutter'")
