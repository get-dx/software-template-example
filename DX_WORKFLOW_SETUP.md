# Creating a DX Workflow for the Software Template Service

This guide shows how to create a DX self-service workflow that integrates with this Python service to generate GitHub repositories from templates.

## Overview

When configured, the DX workflow will:
1. Collect user input (template type, repo name, etc.)
2. Send an HTTP request to this Python service
3. Receive real-time status updates as the service creates the repository
4. Display a link to the newly created GitHub repository

## Architecture

```
┌─────────────────────┐
│  DX Self-Service    │
│  User triggers      │
│  workflow           │
└──────────┬──────────┘
           │
           │ HTTP POST /api/service
           │
           ▼
┌─────────────────────┐
│  Python Service     │
│  (This Service)     │
│                     │
│  1. Generate code   │
│  2. Create repo     │
│  3. Push code       │
└──────────┬──────────┘
           │
           │ Status updates via DX API:
           │ - workflowRuns.postMessage
           │ - workflowRuns.addLink
           │ - workflowRuns.changeStatus
           │
           ▼
┌─────────────────────┐
│  DX API             │
│  Updates workflow   │
│  run status         │
└─────────────────────┘
```

## Prerequisites

1. **Python Service Running** - Follow the README to set up the service
2. **Service URL** - If running locally, you need:
   - Your local IP address (e.g., `http://10.17.0.113:8000`)
   - Or use `http://0.0.0.0:8000` if DX is running on the same machine
   - Or use a tunnel service like ngrok for testing: `ngrok http 8000`
3. **DX API Key** - Required for the Python service to send status updates back to DX
   - Get it from: https://app.getdx.com/admin/webapi
   - Requires `workflows:write` scope
4. **GitHub Token** - Required by the Python service (not DX)

## Step 1: Create a DX Workflow

### Navigate to DX Self-Service

1. Go to https://app.getdx.com/self-service
2. Click **"Create workflow"**

### Basic Details

- **Name**: `Create Service from Template`
- **Description**: `Create a new GitHub repository from a cookiecutter template`
- **Icon**: Choose GitHub icon or similar
- **Identifier**: `create_service_from_template`

### Scope

Choose based on your needs:
- **Global**: Can be run from anywhere in DX
- **Entity-specific**: Can be run from specific entity types

### Execution Type

Select **Event-driven** - This allows the Python service to report progress back to DX in real-time.

## Step 2: Configure Workflow Parameters

Add these parameters to collect user input:

### Parameter 1: Template Type
- **Name**: `Template Type`
- **Identifier**: `template_type`
- **Type**: `select`
- **Required**: `true`
- **Options**:
  ```
  django - Django Web Application
  go - Go Service
  cpp - C++ Project
  python - Python Package
  custom - Custom Template
  ```

### Parameter 2: GitHub Organization
- **Name**: `GitHub Organization`
- **Identifier**: `github_organization`
- **Type**: `string`
- **Required**: `true`
- **Description**: `GitHub organization or username`

### Parameter 3: Repository Name
- **Name**: `Repository Name`
- **Identifier**: `github_repository`
- **Type**: `string`
- **Required**: `true`
- **Description**: `Name for the new repository`

### Parameter 4: Project Name
- **Name**: `Project Name`
- **Identifier**: `project_name`
- **Type**: `string`
- **Required**: `false`
- **Description**: `Name of the project (used by templates)`

### Parameter 5: Description
- **Name**: `Description`
- **Identifier**: `description`
- **Type**: `string`
- **Required**: `false`
- **Description**: `Project description`

### Parameter 6: Custom Template URL (Optional)
- **Name**: `Custom Template URL`
- **Identifier**: `cookiecutter_url`
- **Type**: `string`
- **Required**: `false`
- **Description**: `URL to custom cookiecutter template (only needed for custom type)`

## Step 3: Configure HTTP Request

This is the critical part that connects DX to your Python service.

### Method
`POST`

### URL
```
http://YOUR_SERVICE_IP:8000/api/service
```

Replace `YOUR_SERVICE_IP` with:
- Your local IP (e.g., `10.17.0.113`) if running locally
- Your server IP/domain if deployed
- `host.docker.internal` if DX is in Docker and service is on host

### Headers
```
Content-Type: application/json
```

### Body

Copy this JSON exactly (DX will replace the `{{...}}` variables):

```json
{
  "dx_workflow_run_id": "{{run.id}}",
  "template_type": "{{data.template_type}}",
  "github_organization": "{{data.github_organization}}",
  "github_repository": "{{data.github_repository}}",
  "project_name": "{{data.project_name}}",
  "description": "{{data.description}}",
  "cookiecutter_url": "{{data.cookiecutter_url}}"
}
```

**Important**: `{{run.id}}` is critical - it allows the Python service to send status updates back to this specific workflow run.

## Step 4: Save and Test

1. Click **"Save"** to create the workflow
2. Click **"Run workflow"** to test it
3. Fill in the parameters:
   - Template Type: `python`
   - GitHub Organization: `your-github-username`
   - Repository Name: `test-python-package`
   - Project Name: `Test Package`
   - Description: `A test Python package`
4. Click **"Run"**

### What You Should See

In the DX workflow run detail page, you'll see:

1. **Triggered workflow run** - Initial event
2. **Sent HTTP request** - Request sent to your Python service
3. **Custom messages** from the Python service:
   - "🚀 Starting creation of python service..."
   - "⚙️ Generating project from cookiecutter template..."
   - "✅ Successfully created repository and pushed initial code!"
4. **Link added** - Clickable link to the GitHub repository
5. **Changed status** - SUCCESS or FAILED

### Verify on GitHub

Check your GitHub account - you should see the new repository with all the generated code!

## Troubleshooting

### DX shows "Status code: null"

**Problem**: DX cannot reach your Python service.

**Solutions**:
- Verify the Python service is running: `curl http://localhost:8000/`
- Use your local IP address instead of `localhost` in the workflow URL
- If DX is in Docker, use `http://host.docker.internal:8000/api/service`
- Check firewall settings

### No status updates appear in DX

**Problem**: Python service cannot communicate back to DX.

**Solutions**:
- Verify `DX_API_KEY` is set in the Python service's `.env` file
- Verify the API key has `workflows:write` scope
- Check Python service logs for API errors: Look for `POST http://localhost:3000/workflowRuns.postMessage` errors

### Repository created but empty

**Problem**: GitHub push failed (usually token permissions).

**Solutions**:
- Check Python service logs for the specific error
- Verify GitHub token has both `repo` and `workflow` scopes
- The most common error: missing `workflow` scope (see README)

### "Repository already exists" error

**Problem**: The repository name is already taken.

**Solutions**:
- Delete the existing repository on GitHub
- Use a different repository name
- The Python service will NOT overwrite existing repositories

## Advanced: Template-Specific Workflows

Instead of one workflow with a template selector, you can create separate workflows for each template type:

### Example: Python Package Workflow

**Parameters**:
1. GitHub Organization (string, required)
2. Repository Name (string, required)
3. Project Name (string, required)
4. Description (string, optional)

**HTTP Body**:
```json
{
  "dx_workflow_run_id": "{{run.id}}",
  "template_type": "python",
  "github_organization": "{{data.github_organization}}",
  "github_repository": "{{data.github_repository}}",
  "project_name": "{{data.project_name}}",
  "description": "{{data.description}}"
}
```

This approach provides a cleaner UX with only relevant parameters for each template.

## Supported Template Types

| Type | Description | Key Parameters |
|------|-------------|----------------|
| `python` | Python package with testing | `project_name`, `description` |
| `django` | Django web application | `project_name`, `description`, `author_name` |
| `go` | Go service | `project_name` (as app_name), `description` |
| `cpp` | C++ project with CMake | `project_name`, `description` |
| `custom` | Any cookiecutter template | `cookiecutter_url` + template-specific params |

## Next Steps

- **Customize templates**: Modify `app/core/config.py` to point to your own cookiecutter templates
- **Add more templates**: See README for instructions on adding new template types
- **Deploy to production**: Deploy the Python service to a cloud provider for permanent availability
- **Add validation**: Customize parameter validation in the Python service
- **Integrate with catalog**: Link created repositories to DX catalog entities

## Support

- **Python Service Logs**: `docker-compose logs -f app` or check console output
- **DX Workflow Logs**: Available in each workflow run detail page
- **API Documentation**: http://localhost:8000/api/docs (when service is running)
