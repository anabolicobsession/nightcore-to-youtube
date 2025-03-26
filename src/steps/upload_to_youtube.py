import logging
import pickle
import re
import sys
import time
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from src import config
from src.utils.metadata import Metadata
from src.utils.utils import ExitCode
from src.utils.working_directory import WorkingDirectory


logger = logging.getLogger(__name__)


SLOWED_NAMES = [
    'Super Deeply Slowed',
    'Deeply Slowed',
    'Slowed',
    'Slightly Slowed',
]
SPED_UP_NAMES = [
    'Slightly Sped Up',
    'Sped Up',
    'Super Sped Up',
]


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


def generate_speed_names(amount_slowed, amount_sped_up):
    match amount_slowed:
        case 0: slowed = []
        case 1: slowed = [-2]
        case 2: slowed = [-3, -2]
        case 3: slowed = [-3, -2, -1]
        case 4: slowed = [-4, -3, -2, -1]
        case _: raise ValueError(f'Unexpected amount of slowed versions: {amount_slowed}')

    match amount_sped_up:
        case 0: sped_up = []
        case 1: sped_up = [1]
        case 2: sped_up = [1, 2]
        case 3: sped_up = [0, 1, 2]
        case _: raise ValueError(f'Unexpected amount of sped up versions: {amount_slowed}')

    return [config.SLOWED_NAMES[x] for x in slowed] + [config.SPED_UP_NAMES[x] for x in sped_up]


def parse_to_hashtags(string: str) -> list[str]:
    return re.sub(r'[^a-zA-Z0-9\s]', '', string).split()


def wait_for_uploading_to_finish(service, id, check_interval=1):
    while True:
        response = service.videos().list(part='processingDetails', id=id).execute()
        status = response['items'][0]['processingDetails']['processingStatus']

        match status:
            case 'succeeded':
                return
            case 'failed':
                logger.error(f'Processing failed')
                sys.exit(ExitCode.GENERAL_ERROR)

        time.sleep(check_interval)


def upload_video(
        service,
        path: Path,
        artist: str,
        name: str,
        speed_name: str,
        speed_name_max_length: str,
        is_sped_up: bool,
        metadata: Metadata,
) -> bool:

    # setting up YouTube metadata
    title = f'{artist} - {name} ({speed_name})'
    tags = [
        *parse_to_hashtags(artist.lower()),
        *parse_to_hashtags(name.lower()),
        *(
            ['sped', 'spedup', 'nightcore']
            if is_sped_up else
            ['slowed', 'reverb', 'slow']
        )
    ]

    formatted_speed_name = f"'{speed_name}'"
    logger.info(f'Uploading: {formatted_speed_name:<{speed_name_max_length + 2}} {" ".join(["#" + x for x in tags])}')

    body = {
        'snippet': {
            'title': title,
            'description': metadata.represent(),
            'tags': tags,
            'categoryId': '10',  # music category
        },
        'status': {
            'privacyStatus': 'public',
            'madeForKids': False
        }
    }

    # uploading video
    media = MediaFileUpload(path, mimetype='video/*', resumable=True)
    request = service.videos().insert(part=','.join(body), body=body, media_body=media)
    response = None

    while response is None:
        try:
            status, response = request.next_chunk()
        except errors.ResumableUploadError:
            logger.warning(f'Daily upload limit exceeded. Cancelling uploads')
            return False

    wait_for_uploading_to_finish(service, response['id'])
    return True


def upload_to_youtube(working_directory: WorkingDirectory, uploaded_video_count: Optional[int]):
    # sort videos by speed
    videos = working_directory.get_video_paths(raise_if_not_exist=True)
    speeds = [working_directory.path_to_speed_and_reverb(x)[0] for x in videos]

    amount_slowed = len([x for x in sorted(speeds) if x < config.STANDARD_SPEED])
    sorted_speed_names = generate_speed_names(amount_slowed=amount_slowed, amount_sped_up=len(speeds) - amount_slowed)
    sorted_videos_and_speeds = sorted(zip(videos, speeds), key=lambda x: x[1])

    videos_and_parameters = list(zip(*zip(*sorted_videos_and_speeds), sorted_speed_names))
    if uploaded_video_count: videos_and_parameters = videos_and_parameters[:uploaded_video_count] if uploaded_video_count > 0 else videos_and_parameters[uploaded_video_count:]

    # upload videos
    service = build('youtube', 'v3', credentials=get_credentials())
    track_name = working_directory.get_track_path(raise_if_not_exists=True).stem

    for video, speed, speed_name in videos_and_parameters:
        artist, name = tuple(track_name.split(' - ', 1))
        if not upload_video(
            service,
            path=video,
            artist=artist,
            name=name,
            speed_name=speed_name,
            speed_name_max_length=max([len(x) for _, _, x in videos_and_parameters]),
            is_sped_up=speed > config.STANDARD_SPEED,
            metadata=working_directory.get_metadata(),
        ):
            return
