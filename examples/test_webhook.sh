#!/bin/bash

# Test script for sending webhook requests to the service
# Simulates DX self-service workflow requests
# Usage: ./test_webhook.sh [template_type]

# Configuration
SERVICE_URL="${SERVICE_URL:-http://localhost:8000}"
ENDPOINT="${SERVICE_URL}/api/service"
GITHUB_ORG="${GITHUB_ORG:-your-github-username}"

# Template type (default: python)
TEMPLATE_TYPE="${1:-python}"

# Generate unique repository name and workflow run ID
TIMESTAMP=$(date +%s)
REPO_NAME="test-${TEMPLATE_TYPE}-${TIMESTAMP}"
WORKFLOW_RUN_ID="test-run-${TIMESTAMP}"

echo "Testing DX webhook with:"
echo "  Service URL: ${SERVICE_URL}"
echo "  Template Type: ${TEMPLATE_TYPE}"
echo "  GitHub Org: ${GITHUB_ORG}"
echo "  Repository: ${REPO_NAME}"
echo "  DX Workflow Run ID: ${WORKFLOW_RUN_ID}"
echo ""

# Build payload based on template type (DX format)
case $TEMPLATE_TYPE in
  django)
    PAYLOAD=$(cat <<EOF
{
  "dx_workflow_run_id": "${WORKFLOW_RUN_ID}",
  "template_type": "django",
  "github_organization": "${GITHUB_ORG}",
  "github_repository": "${REPO_NAME}",
  "project_name": "testproject",
  "description": "Test Django project"
}
EOF
)
    ;;
  
  go)
    PAYLOAD=$(cat <<EOF
{
  "dx_workflow_run_id": "${WORKFLOW_RUN_ID}",
  "template_type": "go",
  "github_organization": "${GITHUB_ORG}",
  "github_repository": "${REPO_NAME}",
  "app_name": "testapp",
  "project_short_description": "Test Go service"
}
EOF
)
    ;;
  
  cpp)
    PAYLOAD=$(cat <<EOF
{
  "dx_workflow_run_id": "${WORKFLOW_RUN_ID}",
  "template_type": "cpp",
  "github_organization": "${GITHUB_ORG}",
  "github_repository": "${REPO_NAME}",
  "project_name": "testproject",
  "description": "Test C++ project"
}
EOF
)
    ;;
  
  python)
    PAYLOAD=$(cat <<EOF
{
  "dx_workflow_run_id": "${WORKFLOW_RUN_ID}",
  "template_type": "python",
  "github_organization": "${GITHUB_ORG}",
  "github_repository": "${REPO_NAME}",
  "project_name": "Test Package",
  "project_slug": "test_package",
  "project_short_description": "Test Python package"
}
EOF
)
    ;;
  
  *)
    echo "Unknown template type: ${TEMPLATE_TYPE}"
    echo "Supported types: django, go, cpp, python"
    exit 1
    ;;
esac

# Send request
echo "Sending request..."
echo ""

RESPONSE=$(curl -s -X POST "${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}")

echo "Response:"
echo "${RESPONSE}" | python3 -m json.tool

echo ""
echo "Check the service logs for progress."
echo "Repository will be created at: https://github.com/${GITHUB_ORG}/${REPO_NAME}"
echo ""
echo "Note: DX status updates will only work if DX_API_KEY is configured in .env"
