from pathlib import Path
from typing import Iterable, Optional

from src import config
from src.utils.metadata import Metadata


Extension = str


def has_any_of_extensions(path: Path, extensions: Iterable[Extension]):
    return any(path.suffix.casefold() == '.' + x for x in extensions)


class TooManyFilesError(Exception):
    ...


class WorkingDirectory:
    def __init__(self, path: str | Path):
        self.path = Path(path)

        if not (self.path.exists() and self.path.is_dir()):
            raise FileNotFoundError(f'Working directory doesn\'t exist: `{self.path}/`')

    def get_path(self, raise_if_not_exists=False) -> Path:
        if raise_if_not_exists and not self.path.exists():
            raise FileNotFoundError(f'Working directory doesn\'t exist: `{self.path}/`')

        return self.path

    def get_track_path(self, raise_if_not_exists=False) -> Optional[Path]:
        paths = [x for x in self.path.iterdir() if self._is_track_path(x)]

        if raise_if_not_exists and not paths:
            raise FileNotFoundError(f'Couldn\'t find track file in directory: `{self.path}/`')
        elif len(paths) > 1:
            raise TooManyFilesError(f'There are multiple track files in directory: `{self.path}/`')

        return paths[0] if paths else None

    def get_cover_path(self, raise_if_not_exists=False) -> Optional[Path]:
        paths = [x for x in self.path.iterdir() if self._is_cover_path(x)]

        if raise_if_not_exists and not paths:
            raise FileNotFoundError(f'Couldn\'t find cover art file in directory: `{self.path}/`')
        elif len(paths) > 1:
            raise TooManyFilesError(f'There are multiple cover art files in directory: `{self.path}/`')

        return paths[0] if paths else None

    def get_nightcore_paths(self, raise_if_not_exist=False) -> list[Path]:
        paths = [x for x in self.path.iterdir() if self._is_nightcore_path(x)]

        if raise_if_not_exist and not paths:
            raise FileNotFoundError(f'Couldn\'t find nightcore files in directory: `{self.path}/`')

        return paths

    def get_video_paths(self, raise_if_not_exist=False) -> list[Path]:
        paths = [x for x in self.path.iterdir() if self._is_video_path(x)]

        if raise_if_not_exist and not paths:
            raise FileNotFoundError(f'Couldn\'t find nightcore files in directory: `{self.path}/`')

        return paths

    def get_metadata(self) -> Metadata:
        return Metadata.from_string(self.get_cover_path(raise_if_not_exists=True).stem)

    def speed_and_reverb_to_path(self, speed, reverb, extension) -> Path:
        return self.path / f'{speed}{config.SPEED_REVERB_NAME_SEPARATOR}{reverb}.{extension}'

    @staticmethod
    def path_to_speed_and_reverb(path: Path) -> (int, int):
        return tuple(map(int, path.stem.split(config.SPEED_REVERB_NAME_SEPARATOR)))

    @staticmethod
    def _is_track_path(path: Path):
        return (
                path.is_file() and
                has_any_of_extensions(path, config.AUDIO_EXTENSIONS) and
                not WorkingDirectory._has_nightcore_stem(path)
        )

    @staticmethod
    def _is_cover_path(path: Path):
        return (
                path.is_file() and
                has_any_of_extensions(path, config.COVER_EXTENSIONS)
        )

    @staticmethod
    def _is_nightcore_path(path: Path):
        return (
                path.is_file() and
                has_any_of_extensions(path, config.AUDIO_EXTENSIONS) and
                WorkingDirectory._has_nightcore_stem(path)
        )

    @staticmethod
    def _is_video_path(path: Path):
        return (
                path.is_file() and
                has_any_of_extensions(path, config.VIDEO_EXTENSIONS) and
                WorkingDirectory._has_nightcore_stem(path)
        )

    @staticmethod
    def _has_nightcore_stem(path: Path):
        return bool(config.NIGHTCORE_NAME_PATTERN.fullmatch(path.stem))
