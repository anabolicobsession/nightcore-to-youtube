from pathlib import Path


def has_extension(path: Path, extension: str):
    return path.suffix.lower() == '.' + extension


class WorkingDirectory:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    @property
    def track_path(self) -> Path:
        if path := next((x for x in self.path.iterdir() if self._is_track_path(x)), None):
            return path
        else:
            raise FileNotFoundError(f'Couldn\'t find track file in directory: {self.path}')

    @property
    def nightcore_paths(self) -> list[Path]:
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
