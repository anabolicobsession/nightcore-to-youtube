import logging
import multiprocessing
import sys
import traceback
from enum import Enum
from pathlib import Path
from typing import Self

import ffmpeg
from PIL import Image

from src import config
from src.utils.utils import ExitCode
from src.utils.working_directory import WorkingDirectory


Ratio = float


logger = logging.getLogger(__name__)


def remove_previous_video(working_directory: WorkingDirectory):
    if paths := working_directory.get_video_paths():
        for video in paths: video.unlink()
        logger.info(f'Cleared files: {", ".join([x.name for x in paths])}')


class Preset(Enum):
    VERY_SLOW = 'veryslow'
    SLOWER = 'slower'
    SLOW = 'slow'
    MEDIUM = 'medium'
    FAST = 'fast'
    SUPER_FAST = 'superfast'
    ULTRA_FAST = 'ultrafast'

    @classmethod
    @property
    def DEFAULT(cls) -> Self:
        return cls.ULTRA_FAST


def _nightcore_to_video(
        nightcore: Path,
        cover: Path,
        video: Path,
        preset: Preset,
        ratio: Ratio,
) -> bool:

    with Image.open(cover) as x:
        width, height = x.size
        speed, reverb = WorkingDirectory.path_to_speed_and_reverb(nightcore)

        new_width = round(height * ratio)
        if new_width % 2 != 0: new_width += 1

        def wrap_log(log: str):
            return f'{speed:>3}x{reverb:<2}: {log}'

        try:
            (
                ffmpeg
                .output(
                    ffmpeg.input(nightcore),
                    (
                        ffmpeg.input(cover, loop=1)
                        .filter('scale', new_width, height, force_original_aspect_ratio='decrease')
                        .filter('pad', new_width, height, '(iw-ow)/2', '(ih-oh)/2', color='black')
                    ),
                    str(video),
                    vcodec='libx264',
                    crf=18,
                    preset=preset.value,
                    shortest=None,
                    acodec='aac',
                    **{'c:a': 'copy'},
                )
                .global_args('-loglevel', 'quiet')
                .run(overwrite_output=True)
            )

        except ffmpeg.Error as e:
            logger.info(wrap_log(f'Most likely caught keyboard interruption: {e}'))
            return False

        except Exception:
            traceback.print_exc()
            return False

    return True


def nightcore_to_video(
        working_directory: WorkingDirectory,
        preset: Preset = Preset.DEFAULT,
        ratio: Ratio = config.MIN_VIDEO_RATIO,
):
    # preparation
    remove_previous_video(working_directory)

    nightcores = working_directory.get_nightcore_paths(raise_if_not_exist=True)
    cover = working_directory.get_cover_path()
    videos = [x.with_suffix('.mp4') for x in nightcores]

    # conversion
    logger.info('Creating videos concurrently')
    N = len(nightcores)
    args = zip(
        nightcores,
        [cover] * len(nightcores),
        videos,
        [preset] * N,
        [ratio] * N,
    )
    processes = min(multiprocessing.cpu_count(), len(nightcores))

    with multiprocessing.Pool(processes=processes) as pool:
        if not(all(pool.starmap(_nightcore_to_video, args))):
            sys.exit(ExitCode.GENERAL_ERROR)
