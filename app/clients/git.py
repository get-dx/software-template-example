import logging
import os
import shutil
from pathlib import Path
from git import Repo

from core.config import settings

logger = logging.getLogger(__name__)

remote_name = "origin"


def init_repo(path: str) -> Repo:
    """
    Initialize a git repository at the specified path.
    
    Args:
        path: Directory path to initialize as git repo
        
    Returns:
        Initialized Repo object
    """
    logger.info(f"Initializing git repository at {path}")
    return Repo.init(path)


def remove_workflow_files(repo_path: str) -> None:
    """
    Remove GitHub Actions workflow files from the repository.
    This is necessary when the GitHub token doesn't have 'workflow' scope.
    
    Args:
        repo_path: Path to the git repository
    """
    workflows_dir = Path(repo_path) / ".github" / "workflows"
    if workflows_dir.exists():
        logger.warning(f"Removing .github/workflows directory (requires 'workflow' scope on token)")
        shutil.rmtree(workflows_dir)
        
        # Remove .github directory if it's now empty
        github_dir = Path(repo_path) / ".github"
        if github_dir.exists() and not any(github_dir.iterdir()):
            github_dir.rmdir()
            logger.info("Removed empty .github directory")


def upload_all_files(
    repo: Repo,
    remote_org: str,
    remote_repo: str,
    commit_msg: str = "Initial commit from template",
    head_branch: str = "main",
    exclude_workflows: bool = False
) -> None:
    """
    Stage all files, commit, and push to remote GitHub repository.
    
    Args:
        repo: Git repository object
        remote_org: GitHub organization or username
        remote_repo: Repository name
        commit_msg: Commit message
        head_branch: Name of the main branch
        exclude_workflows: If True, removes .github/workflows before committing
                          (use this if token doesn't have 'workflow' scope)
    """
    try:
        # Remove workflow files if requested
        if exclude_workflows:
            remove_workflow_files(repo.working_dir)
        
        logger.info(f"Staging all files in {repo.working_dir}")
        repo.git.add('.')
        
        logger.info(f"Creating commit: {commit_msg}")
        repo.index.commit(commit_msg)
        
        # Create remote URL with authentication token
        remote_url = f"https://{settings.GH_ACCESS_TOKEN}@github.com/{remote_org}/{remote_repo}"
        
        logger.info(f"Adding remote origin: {remote_org}/{remote_repo}")
        repo.create_remote(name=remote_name, url=remote_url)
        
        logger.info(f"Creating branch: {head_branch}")
        branch = repo.create_head(head_branch)
        
        logger.info(f"Pushing to remote: {remote_name}/{head_branch}")
        repo.git.push("--set-upstream", remote_name, branch)
        
        logger.info(f"Successfully pushed all files to {remote_org}/{remote_repo}")
        
    except Exception as e:
        logger.error(f"Failed to upload files to {remote_org}/{remote_repo}: {e}")
        raise
