import logging
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src import config
from src.working_directory import WorkingDirectory


logger = logging.getLogger(__name__)


def get_credentials():
    creds = None

    # load token
    if config.TOKEN_PATH.exists():
        with config.TOKEN_PATH.open('rb') as file:
            creds = pickle.load(file)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRET_PATH, config.QUATH_SCOPES)
            creds = flow.run_local_server(port=0)

        # save new token
        with config.TOKEN_PATH.open('wb') as file:
            pickle.dump(creds, file)

    return creds


SLOWED_NAMES = [
    'Deeply Slowed',
    'Slowed',
    'Slightly Slowed',
]

SPED_UP_NAMES = [
    'Slightly Sped Up',
    'Sped Up',
    'Super Sped Up',
]

def generate_speed_names(amount_slowed, amount_sped_up):
    match amount_slowed:
        case 0: slowed = []
        case 1: slowed = [1]
        case 2: slowed = [0, 1]
        case 3: slowed = [0, 1, 2]
        case _: raise ValueError(f'Unexpected amount of slowed versions: {amount_slowed}')

    match amount_sped_up:
        case 0: sped_up = []
        case 1: sped_up = [1]
        case 2: sped_up = [1, 2]
        case 3: sped_up = [0, 1, 2]
        case _: raise ValueError(f'Unexpected amount of sped up versions: {amount_slowed}')

    return [SLOWED_NAMES[x] for x in slowed] + [SPED_UP_NAMES[x] for x in sped_up]


def upload_to_youtube(working_directory: WorkingDirectory):
    service = build('youtube', 'v3', credentials=get_credentials())

    # sort videos by speed
    videos = working_directory.get_video_paths(raise_if_not_exist=True)
    speeds = [working_directory.path_to_speed_and_reverb(x)[0] for x in videos]

    amount_slowed = len([x for x in sorted(speeds) if x < config.STANDARD_SPEED])
    sorted_speed_names = generate_speed_names(amount_slowed=amount_slowed, amount_sped_up=len(speeds) - amount_slowed)

    sorted_videos_and_speeds = sorted(zip(videos, speeds), key=lambda x: x[1])
    sorted_videos = list(zip(*sorted_videos_and_speeds))[0]
