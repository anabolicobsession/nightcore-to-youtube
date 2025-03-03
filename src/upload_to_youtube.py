import logging
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src import config
from src.working_directory import WorkingDirectory


logger = logging.getLogger(__name__)


def upload_to_youtube(working_directory: WorkingDirectory):
    service = build('youtube', 'v3', credentials=get_credentials())
    videos = working_directory.get_video_paths(raise_if_not_exist=True)
    speeds = [working_directory.path_to_speed_and_reverb(x)[0] for x in videos]

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
