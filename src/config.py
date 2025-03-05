import inspect
import re
from pathlib import Path


# working-directory
AUDIO_EXTENSIONS = ['mp3', 'opus']
COVER_EXTENSIONS = ['png', 'jpg']
VIDEO_EXTENSIONS = ['mp4']

ARTIST_SEPARATORS = ',&'

SPEED_REVERB_NAME_SEPARATOR = '_'
NIGHTCORE_NAME_PATTERN = re.compile(rf'\d+(?:{SPEED_REVERB_NAME_SEPARATOR}\d+)?')

METADATA_DISCOVERY_YEARS = list(range(2023, 2100))
METADATA_DISCOVERY_SEASONS = [1, 2, 3, 4]
METADATA_PLAYLISTS_MAPPING = {
    'w': 'west',
    'p': 'phonk',
    'e': 'electronic',
    's': 'east',
}


# create-nightcore
STANDARD_SPEED = 100
STANDARD_REVERB = 0


# nightcore-to-video
MIN_VIDEO_RATIO = 16 / 9
MAX_VIDEO_RATIO = 32 / 9


# upload-to-youtube
def resolve_project_path(project_path: str) -> Path:
    path = Path(inspect.getfile(inspect.currentframe()))
    path = Path(*path.parts[:path.parts.index('src')])
    return path / project_path

_CREDENTIALS_PATH = Path('.credentials')
CLIENT_SECRET_PATH = resolve_project_path(_CREDENTIALS_PATH / 'client_secret_329273851917-v02c17fqgfp0kvidntpei8n2iuh8fp00.apps.googleusercontent.com.json')
TOKEN_PATH = resolve_project_path(_CREDENTIALS_PATH / 'token.pickle')
QUATH_SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.upload',
]
