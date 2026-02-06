from typing import Dict, Type

from actions.base_create_service import BaseCreateService
from actions.create_cpp_service import CreateCPPService
from actions.create_django_service import CreateDjangoService
from actions.create_go_service import CreateGoService
from actions.create_python_service import CreatePythonService

# Map template types to their corresponding action classes
TEMPLATE_TYPE_TO_CLASS_MAPPING: Dict[str, Type[BaseCreateService]] = {
    "django": CreateDjangoService,
    "go": CreateGoService,
    "cpp": CreateCPPService,
    "c++": CreateCPPService,  # Alias
    "python": CreatePythonService,
    # "custom" is handled separately as it requires a URL parameter
}
