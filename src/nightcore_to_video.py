import logging
import multiprocessing
import time
import traceback
from enum import Enum
from pathlib import Path
from typing import Self

import ffmpeg
from PIL import Image

from src import config
from src.working_directory import WorkingDirectory


Ratio = float


logger = logging.getLogger(__name__)


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


def nightcore_to_video(
        working_directory: WorkingDirectory,
        preset: Preset = Preset.DEFAULT,
        ratio: Ratio = config.MIN_VIDEO_RATIO,
):
    remove_previous_video(working_directory)

    nightcores = working_directory.get_nightcore_paths(raise_if_not_exist=True)
    cover = working_directory.get_cover_path()
    videos = [x.with_suffix('.mp4') for x in nightcores]

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
        pool.starmap(_nightcore_to_video, args)


def remove_previous_video(working_directory: WorkingDirectory):
    if paths := working_directory.get_video_paths():
        for video in paths: video.unlink()
        logger.info(f'Removed obsolete files: {", ".join(["`" + x.name + "`" for x in paths])}')


def _nightcore_to_video(
        nightcore: Path,
        cover: Path,
        video: Path,
        preset: Preset,
        ratio: Ratio,
):
    with Image.open(cover) as x:
        width, height = x.size
        speed, reverb = WorkingDirectory.path_to_speed_and_reverb(nightcore)

        new_width = round(height * ratio)
        if new_width % 2 != 0: new_width += 1

        def wrap_log(log: str):
            return f'{speed:>3}x{reverb:<2}: {log}'

        try:
            logger.info(wrap_log('Starting convertion')); start_time = time.time()

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

            logger.info(wrap_log(f'Convertion completed in {(time.time() - start_time):.0f}s'))

        except Exception as _:
            traceback.print_exc()
