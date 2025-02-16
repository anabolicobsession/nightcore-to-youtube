from pathlib import Path
from typing import Optional


def has_extension(path: Path, extension: str):
    return path.suffix.lower() == '.' + extension


class WorkingDirectory:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        
    def get_path(self) -> Path:
        return self.path

    def get_track_path(self) -> Optional[Path]:
        return next((x for x in self.path.iterdir() if self._is_track_path(x)), None)

    def get_nightcore_paths(self) -> list[Path]:
        return [x for x in self.path.iterdir() if self._is_nightcore_path(x)]

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
