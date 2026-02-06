import logging
from github import Github, GithubException

from core.config import settings

logger = logging.getLogger(__name__)

# Initialize GitHub client
g = Github(settings.GH_ACCESS_TOKEN, timeout=60)


def create_repo(github_org: str, github_repo: str, private: bool = True, description: str = "") -> bool:
    """
    Create a new GitHub repository in the specified organization or user account.
    
    Args:
        github_org: Organization name or username
        github_repo: Repository name
        private: Whether the repository should be private
        description: Repository description
        
    Returns:
        True if successful, raises exception otherwise
    """
    try:
        user = g.get_user()
        
        # Check if target is the authenticated user or an organization
        if user.login == github_org:
            org = user
        else:
            org = g.get_organization(github_org)
        
        logger.info(f"Creating repository {github_org}/{github_repo}")
        org.create_repo(
            github_repo,
            private=private,
            description=description,
            auto_init=False  # We'll push our own initial commit
        )
        logger.info(f"Successfully created repository {github_org}/{github_repo}")
        return True
        
    except GithubException as e:
        logger.error(f"Failed to create repository {github_org}/{github_repo}: {e}")
        raise


def check_repo_exists(github_org: str, github_repo: str) -> bool:
    """
    Check if a repository already exists.
    
    Args:
        github_org: Organization name or username
        github_repo: Repository name
        
    Returns:
        True if repository exists, False otherwise
    """
    try:
        g.get_repo(f"{github_org}/{github_repo}")
        return True
    except GithubException:
        return False
