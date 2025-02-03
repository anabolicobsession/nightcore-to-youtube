import inspect
import os


Path = str


def absolutize_project_path(project_path: Path) -> Path:
    return os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), project_path)
