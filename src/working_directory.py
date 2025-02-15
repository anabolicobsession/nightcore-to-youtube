from pathlib import Path


class WorkingDirectory:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    @property
    def track_path(self) -> Path:
        if track_path := next(
                (file for file in self.path.glob('*.mp3') if not all(c.isdigit() or c == '_' for c in file.stem)),
                None
        ):
            return track_path
        else:
            raise FileNotFoundError(f'Couldn\'t find track file in directory: {self.path}')

    @property
    def track_name(self) -> str:
        return self.track_path.stem
