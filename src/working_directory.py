from pathlib import Path
from typing import Optional


SPEED_REVERB_SEPARATOR = '_'


class WorkingDirectory:
    def __init__(self, path: str | Path):
        self.path = Path(path)

        if not (self.path.exists() and self.path.is_dir()):
            raise FileNotFoundError(f'Working directory doesn\'t exist: {self.path}')

    def get_path(self, raise_if_not_exists=False) -> Path:
        if raise_if_not_exists and not self.path.exists():
            raise FileNotFoundError(f'Working directory doesn\'t exist: {self.path}')

        return self.path

    def get_track_path(self, raise_if_not_exists=False) -> Optional[Path]:
        paths = [x for x in self.path.iterdir() if self._is_track_path(x)]

        if raise_if_not_exists and not paths:
            raise FileNotFoundError(f'Couldn\'t find track file in directory: {self.path}')
        elif len(paths) > 1:
            raise TooManyFilesError(f'There are multiple track files in directory: {self.path}')

        return paths[0] if paths else None

    def get_cover_path(self, raise_if_not_exists=False) -> Optional[Path]:
        paths = [x for x in self.path.iterdir() if self._is_cover_path(x)]

        if raise_if_not_exists and not paths:
            raise FileNotFoundError(f'Couldn\'t find cover art file in directory: {self.path}')
        elif len(paths) > 1:
            raise TooManyFilesError(f'There are multiple cover art files in directory: {self.path}')

        return paths[0] if paths else None

    def get_nightcore_paths(self, raise_if_not_exist=False) -> list[Path]:
        paths = [x for x in self.path.iterdir() if self._is_nightcore_path(x)]

        if raise_if_not_exist and not paths:
            raise FileNotFoundError(f'Couldn\'t find nightcore files in directory: {self.path}')

        return paths

    def get_video_paths(self, raise_if_not_exist=False) -> list[Path]:
        paths = [x for x in self.path.iterdir() if self._is_video_path(x)]

        if raise_if_not_exist and not paths:
            raise FileNotFoundError(f'Couldn\'t find nightcore files in directory: {self.path}')

        return paths

    def speed_and_reverb_to_path(self, speed, reverb, extension) -> Path:
        return self.path / f'{speed}{SPEED_REVERB_SEPARATOR}{reverb}.{extension}'

    @staticmethod
    def path_to_speed_and_reverb(path: Path) -> (int, int):
        return tuple(map(int, path.stem.split(SPEED_REVERB_SEPARATOR)))

    @staticmethod
    def _is_track_path(path: Path):
        return (
                path.is_file() and
                has_any_of_extensions(path, 'mp3') and
                not WorkingDirectory._has_nightcore_name(path)
        )

    @staticmethod
    def _is_cover_path(path: Path):
        return (
                path.is_file() and
                has_any_of_extensions(path, 'png', 'jpg')
        )

    @staticmethod
    def _is_nightcore_path(path: Path):
        return (
                path.is_file() and
                has_any_of_extensions(path, 'mp3') and
                WorkingDirectory._has_nightcore_name(path)
        )

    @staticmethod
    def _is_video_path(path: Path):
        return (
                path.is_file() and
                has_any_of_extensions(path, 'mp4')
        )

    @staticmethod
    def _has_nightcore_name(path: Path):
        return all(c.isdigit() or c == '_' for c in path.stem)


class TooManyFilesError(Exception):
    ...


Extension = str

def has_any_of_extensions(path: Path, *extensions: Extension):
    return any(path.suffix.lower() == '.' + x for x in extensions)
