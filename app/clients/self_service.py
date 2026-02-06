import logging
import httpx
from typing import Optional, Literal

from core.config import settings

logger = logging.getLogger(__name__)


class DXClient:
    """
    Client for communicating with DX self-service platform.
    
    Uses DX's workflow API endpoints to report status back to workflow runs.
    See: https://docs.getdx.com/self-service/
    """
    
    def __init__(self):
        self.api_url = settings.DX_API_URL
        self.api_key = settings.DX_API_KEY
        
    def post_message(
        self,
        workflow_run_id: str,
        message: str
    ) -> bool:
        """
        Post a message to a DX workflow run.
        
        Args:
            workflow_run_id: DX workflow run ID
            message: Markdown-supported message to post
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_url or not self.api_key:
            logger.warning("DX API not configured, skipping message post")
            return False
            
        try:
            url = f"{self.api_url}/workflowRuns.postMessage"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "workflow_run_id": workflow_run_id,
                "message": message
            }
            
            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
            logger.info(f"Posted message to DX workflow run {workflow_run_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to post message to DX: {e}")
            return False
    
    def add_link(
        self,
        workflow_run_id: str,
        url: str,
        label: str,
        icon: Optional[str] = None
    ) -> bool:
        """
        Add a link to a DX workflow run.
        
        Args:
            workflow_run_id: DX workflow run ID
            url: URL to link to
            label: Label for the link
            icon: Optional icon name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_url or not self.api_key:
            logger.warning("DX API not configured, skipping link add")
            return False
            
        try:
            api_url = f"{self.api_url}/workflowRuns.addLink"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            link_data = {
                "url": url,
                "label": label
            }
            if icon:
                link_data["icon"] = icon
                
            payload = {
                "workflow_run_id": workflow_run_id,
                "link": link_data
            }
            
            with httpx.Client() as client:
                response = client.post(api_url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
            logger.info(f"Added link to DX workflow run {workflow_run_id}: {label}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add link to DX: {e}")
            return False
    
    def change_status(
        self,
        workflow_run_id: str,
        status: Literal["SUCCEEDED", "FAILED"]
    ) -> bool:
        """
        Change the status of a DX workflow run.
        
        Args:
            workflow_run_id: DX workflow run ID
            status: Either "SUCCEEDED" or "FAILED"
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_url or not self.api_key:
            logger.warning("DX API not configured, skipping status change")
            return False
            
        try:
            url = f"{self.api_url}/workflowRuns.changeStatus"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "workflow_run_id": workflow_run_id,
                "status": status
            }
            
            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
            logger.info(f"Changed DX workflow run {workflow_run_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to change DX workflow status: {e}")
            return False


# Singleton instance
dx_client = DXClient()
