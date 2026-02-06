from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DXWorkflowRequest(BaseModel):
    """
    Schema for incoming workflow requests from DX self-service platform.
    
    This matches the structure that DX sends when dispatching a workflow
    to an external HTTP endpoint.
    """
    
    # DX workflow run ID - critical for reporting back status
    dx_workflow_run_id: str = Field(..., description="DX workflow run ID for status updates")
    
    # Template configuration
    template_type: str = Field(..., description="Type of template (django, go, cpp, python, custom)")
    
    # GitHub configuration
    github_organization: str = Field(..., description="Target GitHub organization")
    github_repository: str = Field(..., description="Target repository name")
    
    # Template-specific properties (flexible dict for different template needs)
    # These come from DX workflow parameters
    project_name: Optional[str] = Field(None, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    app_name: Optional[str] = Field(None, description="Application name (for Go templates)")
    project_short_description: Optional[str] = Field(None, description="Short description")
    project_slug: Optional[str] = Field(None, description="Project slug (for Python packages)")
    author_name: Optional[str] = Field(None, description="Author name")
    full_name: Optional[str] = Field(None, description="Full name")
    email: Optional[str] = Field(None, description="Email address")
    
    # Optional custom template URL (for custom templates)
    cookiecutter_url: Optional[str] = Field(None, description="Custom cookiecutter template URL")
    
    # Optional entity information (if workflow is entity-specific)
    entity_identifier: Optional[str] = Field(None, description="DX entity identifier")
    entity_name: Optional[str] = Field(None, description="DX entity name")
    
    def get_properties_dict(self) -> dict:
        """Extract all non-None properties into a dict for cookiecutter"""
        props = {}
        if self.project_name:
            props['project_name'] = self.project_name
        if self.description:
            props['description'] = self.description
        if self.app_name:
            props['app_name'] = self.app_name
        if self.project_short_description:
            props['project_short_description'] = self.project_short_description
        if self.project_slug:
            props['project_slug'] = self.project_slug
        if self.author_name:
            props['author_name'] = self.author_name
        if self.full_name:
            props['full_name'] = self.full_name
        if self.email:
            props['email'] = self.email
        return props


class WorkflowResponse(BaseModel):
    """Response returned to the self-service platform"""
    status: str = Field(..., description="Status of the operation (SUCCESS, FAILURE, PENDING)")
    message: str = Field(..., description="Human-readable message")
    execution_id: str = Field(..., description="Execution ID for tracking")
    repository_url: Optional[str] = Field(None, description="URL of created repository")
    error: Optional[str] = Field(None, description="Error message if status is FAILURE")
