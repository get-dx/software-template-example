# Software Template Service

A Python service that creates GitHub repositories from cookiecutter templates. Designed to integrate with DX self-service workflows, this service allows users to quickly scaffold new projects with proper structure and best practices.

## Features

- **Template Support**: Pre-configured templates for Python, Django, Go, C++, and custom cookiecutter templates
- **GitHub Integration**: Automatically creates repositories and pushes generated code
- **DX Integration**: Reports real-time progress back to DX workflows
- **Background Processing**: Handles long-running operations without blocking
- **Configurable**: Easy to add new templates or customize existing ones

## Supported Templates

| Template | Description                           | Use Case                                |
| -------- | ------------------------------------- | --------------------------------------- |
| `python` | Python package with testing framework | CLI tools, libraries, packages          |
| `django` | Full Django web application           | Web applications, APIs                  |
| `go`     | Go service with standard structure    | Microservices, APIs                     |
| `cpp`    | C++ project with CMake                | System tools, performance-critical apps |
| `custom` | Any cookiecutter template URL         | Your own templates                      |

## Quick Start

### Prerequisites

- **Python 3.9+**
- **Git** installed locally
- **GitHub Personal Access Token** with `repo` and `workflow` scopes
  - Create at: https://github.com/settings/tokens
- **DX API Key** (if using with DX)
  - Get from: https://app.getdx.com/admin/webapi
  - Requires `workflows:write` scope

### Installation

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd software-template-example
```

2. **Set up Python environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Required: GitHub token with 'repo' and 'workflow' scopes
GH_ACCESS_TOKEN=ghp_your_github_token_here

# Required for DX integration: API key with 'workflows:write' scope
DX_API_KEY=your_dx_api_key_here

# Optional: DX API URL (defaults to production)
DX_API_URL=https://api.getdx.com
```

4. **Run the service**

```bash
cd app
python main.py
```

The service will start on `http://localhost:8000`

### Docker Deployment (Alternative)

```bash
# Configure .env first (see step 3 above)

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop the service
docker-compose down
```

## Usage

### Test the Service

```bash
# Health check
curl http://localhost:8000/api/health

# Create a Python package repository
curl -X POST http://localhost:8000/api/service \
  -H "Content-Type: application/json" \
  -d '{
    "dx_workflow_run_id": "test-123",
    "template_type": "python",
    "github_organization": "your-github-username",
    "github_repository": "my-new-package",
    "project_name": "My New Package",
    "description": "A test Python package"
  }'
```

### API Endpoint

**POST** `/api/service`

**Request Body:**

```json
{
  "dx_workflow_run_id": "workflow-run-id",
  "template_type": "python",
  "github_organization": "your-org",
  "github_repository": "repo-name",
  "project_name": "Project Name",
  "description": "Project description",
  "cookiecutter_url": ""
}
```

**Response:**

```json
{
  "status": "PENDING",
  "message": "Service creation queued for your-org/repo-name",
  "execution_id": "workflow-run-id"
}
```

The service processes the request in the background and reports status back to DX via their API.

### Interactive API Documentation

Visit http://localhost:8000/api/docs for full interactive API documentation.

## Integration with DX

**Quick Summary:**

1. Create an event-driven workflow in DX
2. Add parameters for template type, GitHub org/repo, project details
3. Configure HTTP POST to `http://your-service:8000/api/service`
4. Include `"dx_workflow_run_id": "{{run.id}}"` in the request body

The Python service will:

- Generate code from the cookiecutter template
- Create a GitHub repository
- Push the generated code
- Send real-time status updates back to DX
- Add a link to the repository in the DX workflow run

## Customization

### Adding a New Template

1. **Create an action handler** in `app/actions/`:

```python
from cookiecutter.main import cookiecutter
from actions.base_create_service import BaseCreateService
from utils import get_unique_output_dir

class CreateMyTemplateService(BaseCreateService):
    def _create_cookiecutter(self, props: dict) -> str:
        return cookiecutter(
            "https://github.com/user/my-cookiecutter-template",
            extra_context=props,
            no_input=True,
            output_dir=get_unique_output_dir()
        )
```

2. **Register it** in `app/mappings.py`:

```python
from actions.create_my_template_service import CreateMyTemplateService

TEMPLATE_TYPE_TO_CLASS_MAPPING = {
    "python": CreatePythonService,
    "django": CreateDjangoService,
    "go": CreateGoService,
    "cpp": CreateCppService,
    "mytemplate": CreateMyTemplateService,  # Add this
}
```

3. **Use it** in DX workflows with `"template_type": "mytemplate"`

### Changing Template URLs

Edit `app/core/config.py` to point to different cookiecutter templates:

```python
class Settings(BaseSettings):
    # ... other settings ...

    COOKIECUTTER_PYTHON_URL: str = "https://github.com/your-org/your-python-template"
    COOKIECUTTER_DJANGO_URL: str = "https://github.com/your-org/your-django-template"
```

## Troubleshooting

### GitHub Token Issues

**Error**: `refusing to allow a Personal Access Token to create or update workflow without 'workflow' scope`

**Solution**: Your GitHub token needs both `repo` AND `workflow` scopes:

1. Go to https://github.com/settings/tokens
2. Edit your token
3. Check both ✅ `repo` and ✅ `workflow`
4. Update `GH_ACCESS_TOKEN` in `.env`
5. Restart the service

**Alternative**: If you can't add workflow scope, set `EXCLUDE_GITHUB_WORKFLOWS=true` in `.env` (generated repos won't have CI/CD workflows)

### Django Template Hook Errors

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'uv'` or `Hook script failed (exit status: 1)`

**Cause**: The Django cookiecutter template has post-generation hooks that require `uv` (a Python package manager) and other dependencies.

**Solution**: The service is configured to skip post-generation hooks by default (`COOKIECUTTER_ACCEPT_HOOKS=false`). This generates the complete project structure without running setup scripts. The generated repository will be fully functional, but users may need to run initial setup commands manually.

**Alternative**: If you want to run hooks, install the required dependencies (`uv`, etc.) and set `COOKIECUTTER_ACCEPT_HOOKS=true` in `.env`

### DX Connection Issues

**Symptom**: DX shows "Status code: null" or no logs appear in Python service

**Solutions**:

- If running locally: Use your machine's IP address (e.g., `http://10.17.0.113:8000`) instead of `localhost` in DX workflow
- Find your IP: `ipconfig getifaddr en0` (macOS) or `hostname -I` (Linux)
- If DX is in Docker: Use `http://host.docker.internal:8000/api/service`
- Verify service is running: `curl http://localhost:8000/`

### Empty Repositories

If a repository is created but has no code, check the Python service logs for the push error. Common causes:

- Missing `workflow` scope on GitHub token
- Repository permissions issues
- Network connectivity problems

### Missing Status Updates in DX

If the repository is created but DX shows no progress messages:

- Verify `DX_API_KEY` is set in `.env`
- Verify the key has `workflows:write` scope
- Check Python logs for API errors

## Project Structure

```
software-template-example/
├── app/
│   ├── actions/              # Template-specific creation logic
│   │   ├── base_create_service.py
│   │   ├── create_python_service.py
│   │   ├── create_django_service.py
│   │   ├── create_go_service.py
│   │   └── create_cpp_service.py
│   ├── api/
│   │   ├── endpoints/        # API route handlers
│   │   │   └── service.py    # Main webhook endpoint
│   │   └── deps.py           # Request dependencies
│   ├── clients/              # External service clients
│   │   ├── github.py         # GitHub API client
│   │   ├── git.py            # Git operations
│   │   └── self_service.py   # DX API client
│   ├── core/
│   │   └── config.py         # Configuration and settings
│   ├── schemas/
│   │   └── webhook.py        # Request/response models
│   ├── main.py               # FastAPI application
│   ├── mappings.py           # Template type mappings
│   └── utils.py              # Utility functions
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # This file
```

## Configuration Reference

### Environment Variables

| Variable                    | Required | Description                                                | Default                 |
| --------------------------- | -------- | ---------------------------------------------------------- | ----------------------- |
| `GH_ACCESS_TOKEN`           | Yes      | GitHub token with `repo` and `workflow` scopes             | -                       |
| `DX_API_KEY`                | For DX   | DX API key with `workflows:write` scope                    | -                       |
| `DX_API_URL`                | No       | DX API base URL                                            | `https://api.getdx.com` |
| `EXCLUDE_GITHUB_WORKFLOWS`  | No       | Exclude workflow files if token lacks `workflow` scope     | `false`                 |
| `COOKIECUTTER_ACCEPT_HOOKS` | No       | Run post-generation hooks (requires template dependencies) | `false`                 |
| `WEBHOOK_SECRET`            | No       | Secret for webhook signature verification                  | -                       |

### Template URLs

Configure in `app/core/config.py`:

- `COOKIECUTTER_PYTHON_URL`: Python package template
- `COOKIECUTTER_DJANGO_URL`: Django project template
- `COOKIECUTTER_GO_URL`: Go service template
- `COOKIECUTTER_CPP_URL`: C++ project template

## Development

### Running in Development Mode

The service runs with auto-reload enabled by default:

```bash
cd app
python main.py
```

Changes to Python files will automatically restart the server.

### Viewing Logs

```bash
# Docker
docker-compose logs -f app

# Local
# Logs print to stdout where you ran python main.py
```

### API Testing

Use the interactive docs at http://localhost:8000/api/docs to test endpoints directly in your browser.

## Security Considerations

- **Never commit `.env`** - It contains sensitive tokens
- **Use HTTPS in production** - Protect tokens in transit
- **Rotate tokens regularly** - Minimize impact of compromised tokens
- **Limit token scopes** - Only grant necessary permissions
- **Enable webhook secrets** - Set `WEBHOOK_SECRET` to verify request authenticity

## Support

- **API Documentation**: http://localhost:8000/api/docs
- **DX Integration**: See [Self Service Examples](https://docs.getdx.com/self-service/examples/software-templates/)
