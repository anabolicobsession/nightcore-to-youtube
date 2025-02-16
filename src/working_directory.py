from pathlib import Path
from typing import Optional


def has_extension(path: Path, extension: str):
    return path.suffix.lower() == '.' + extension


class WorkingDirectory:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        
    def get_path(self, raise_if_not_exists=False) -> Path:
        if raise_if_not_exists and not self.path.exists():
            raise FileNotFoundError(f'Working directory doesn\'t exist: {self.path}')

        return self.path

    def get_track_path(self, raise_if_not_exists=False) -> Optional[Path]:
        path = next((x for x in self.path.iterdir() if self._is_track_path(x)), None),

        if raise_if_not_exists and not path:
            raise FileNotFoundError(f'Couldn\'t find track file in directory: {self.path}')

        return path

    def get_nightcore_paths(self, raise_if_not_exist=False) -> list[Path]:
        paths = [x for x in self.path.iterdir() if self._is_nightcore_path(x)]

        if raise_if_not_exist and not paths:
            raise FileNotFoundError(f'Couldn\'t find nightcore files in directory: {self.path}')

        return paths

    @staticmethod
    def _is_track_path(path: Path):
        return (
                path.is_file() and
                has_extension(path, 'mp3') and
                not WorkingDirectory._has_nightcore_name(path)
        )

    @staticmethod
    def _is_nightcore_path(path: Path):
        return (
                path.is_file() and
                has_extension(path, 'mp3') and
                WorkingDirectory._has_nightcore_name(path)
        )

    @staticmethod
    def _has_nightcore_name(path: Path):
        return all(c.isdigit() or c == '_' for c in path.stem)
