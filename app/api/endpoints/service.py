import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from mappings import TEMPLATE_TYPE_TO_CLASS_MAPPING
from actions.create_custom_service import CreateCustomService
from api.deps import verify_webhook
from clients.self_service import dx_client
from schemas.webhook import DXWorkflowRequest, WorkflowResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def process_service_creation(
    workflow_run_id: str,
    github_org: str,
    github_repo: str,
    template_type: str,
    properties: dict,
    cookiecutter_url: Optional[str] = None
):
    """
    Background task to process service creation.
    This runs asynchronously and reports status back to DX.
    """
    try:
        logger.info(f"Processing service creation for DX workflow run {workflow_run_id}")
        
        # Post initial message to DX
        dx_client.post_message(
            workflow_run_id=workflow_run_id,
            message=f"🚀 Starting creation of **{template_type}** service in `{github_org}/{github_repo}`"
        )
        
        # Get the appropriate action class
        if template_type == "custom":
            if not cookiecutter_url:
                raise ValueError("Custom template requires cookiecutter_url")
            dx_client.post_message(
                workflow_run_id=workflow_run_id,
                message=f"📦 Using custom template: `{cookiecutter_url}`"
            )
            action = CreateCustomService(cookiecutter_url)
        else:
            action_class = TEMPLATE_TYPE_TO_CLASS_MAPPING.get(template_type.lower())
            if not action_class:
                raise ValueError(f"Unknown template type: {template_type}")
            action = action_class()
        
        # Post message about generating from template
        dx_client.post_message(
            workflow_run_id=workflow_run_id,
            message="⚙️ Generating project from cookiecutter template..."
        )
        
        # Execute service creation
        logger.info(f"Creating {template_type} service")
        action_status = action.create(github_org, github_repo, properties)
        
        repository_url = f"https://github.com/{github_org}/{github_repo}"
        
        if action_status == 'SUCCESS':
            logger.info(f"Successfully created service at {repository_url}")
            
            # Add link to the created repository
            dx_client.add_link(
                workflow_run_id=workflow_run_id,
                url=repository_url,
                label=f"Repository: {github_org}/{github_repo}",
                icon="github"
            )
            
            # Post success message
            dx_client.post_message(
                workflow_run_id=workflow_run_id,
                message=f"✅ Successfully created repository and pushed initial code!"
            )
            
            # Mark workflow as succeeded
            dx_client.change_status(
                workflow_run_id=workflow_run_id,
                status="SUCCEEDED"
            )
        else:
            logger.error(f"Failed to create {template_type} service")
            
            # Post failure message
            dx_client.post_message(
                workflow_run_id=workflow_run_id,
                message=f"❌ Failed to create service"
            )
            
            # Mark workflow as failed
            dx_client.change_status(
                workflow_run_id=workflow_run_id,
                status="FAILED"
            )
            
    except Exception as e:
        error_message = f"Error creating service: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        # Post error message to DX
        dx_client.post_message(
            workflow_run_id=workflow_run_id,
            message=f"❌ **Error:** {str(e)}"
        )
        
        # Mark workflow as failed
        dx_client.change_status(
            workflow_run_id=workflow_run_id,
            status="FAILED"
        )


@router.post("/service", response_model=WorkflowResponse)
async def handle_create_service_webhook(
    workflow: DXWorkflowRequest,
    background_tasks: BackgroundTasks,
    _verified: bool = Depends(verify_webhook)
):
    """
    Webhook endpoint to handle service creation requests from DX self-service workflows.
    
    This endpoint:
    1. Validates the incoming request from DX
    2. Queues the service creation as a background task
    3. Returns immediately with 200 OK
    4. Reports progress back to DX via their API
    """
    logger.info(f"Received DX workflow request: {workflow.model_dump()}")
    
    try:
        # Extract parameters
        workflow_run_id = workflow.dx_workflow_run_id
        template_type = workflow.template_type
        github_org = workflow.github_organization
        github_repo = workflow.github_repository
        properties = workflow.get_properties_dict()
        cookiecutter_url = workflow.cookiecutter_url
        
        # Validate template type
        if template_type != "custom" and template_type.lower() not in TEMPLATE_TYPE_TO_CLASS_MAPPING:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown template type: {template_type}. "
                       f"Supported types: {', '.join(TEMPLATE_TYPE_TO_CLASS_MAPPING.keys())}, custom"
            )
        
        # Queue background task for service creation
        background_tasks.add_task(
            process_service_creation,
            workflow_run_id=workflow_run_id,
            github_org=github_org,
            github_repo=github_repo,
            template_type=template_type,
            properties=properties,
            cookiecutter_url=cookiecutter_url
        )
        
        logger.info(f"Queued service creation for DX workflow run {workflow_run_id}")
        
        return WorkflowResponse(
            status="PENDING",
            message=f"Service creation queued for {github_org}/{github_repo}",
            execution_id=workflow_run_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "software-template-service"}
