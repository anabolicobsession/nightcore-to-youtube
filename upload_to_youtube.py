import inspect
import logging
import os
import pickle

import click
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import ResumableUploadError
from googleapiclient.http import MediaFileUpload


def absolutize_project_path(project_path):
    return os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), project_path)


CLIENT_SECRET_PATH = absolutize_project_path('credentials/client_secret_329273851917-v02c17fqgfp0kvidntpei8n2iuh8fp00.apps.googleusercontent.com.json')
TOKEN_PATH = absolutize_project_path('credentials/token.pickle')
QUATH_SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']


logger = logging.getLogger(__name__)


@click.command()
@click.argument('track_name')
def main(track_name):
    service = build('youtube', 'v3', credentials=get_youtube_credentials())

    speeds = []
    for file_name in os.listdir('.'):
        if file_name.endswith('.mp4'):
            base_name = os.path.splitext(file_name)[0]
            speeds.append((file_name, int(base_name if '_' not in base_name else base_name.split('_')[0]) / 100))
    speeds.sort(key=lambda x: x[1])

    amount_slowed = len([x for _, x in speeds if x < 1])
    speed_names = generate_speed_names(amount_slowed=amount_slowed, amount_sped_up=len(speeds) - amount_slowed)

    for file_name, speed_name in zip(list(zip(*speeds))[0], speed_names):
        if file_name.endswith('.mp4'):
            title = track_name + f' ({speed_name})'
            response = upload_video(service, path=file_name, title=title)
            if not response: return


def get_youtube_credentials():
    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token: creds = pickle.load(token)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, QUATH_SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

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


def upload_video(service, path, title):
    print(f'Uploading: {title}')

    body = {
        'snippet': {
            'title': title,
            'categoryId': '10'
        },
        'status': {
            'privacyStatus': 'public',
            'madeForKids': False
        }
    }

    media = MediaFileUpload(path, mimetype='video/*', resumable=True)
    request = service.videos().insert(part='snippet,status', body=body, media_body=media)

    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status: print(f'Uploading {status.progress() * 100:.0%}')
        except ResumableUploadError:
            logger.warning(f'Daily upload limit exceeded!')
            return None

    return response


if __name__ == '__main__':
    main()
