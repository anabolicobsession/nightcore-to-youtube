from pathlib import Path


StringPath = str
PROJECT_DIR_PATH = Path(__file__).resolve().parent.parent


def absolutize_project_path(project_path: StringPath) -> StringPath:
    return PROJECT_DIR_PATH / project_path
