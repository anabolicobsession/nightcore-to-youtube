from pathlib import Path


class WorkingDirectory:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    @property
    def track_path(self) -> Path:
        if track_path := next(
                (file for file in self.path.glob('*.mp3') if not self.is_nightcore_file(file)),
                None
        ):
            return track_path
        else:
            raise FileNotFoundError(f'Couldn\'t find track file in directory: {self.path}')

    @property
    def track_name(self) -> str:
        return self.track_path.stem

    @staticmethod
    def is_nightcore_file(path: Path):
        return (
                path.is_file() and
                path.suffix.lower() == ".mp3" and
                all(c.isdigit() or c == '_' for c in path.stem)
        )
