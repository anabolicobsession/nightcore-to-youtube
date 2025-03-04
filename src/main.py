import asyncio
import inspect
import logging
import time
from enum import Enum, auto
from pathlib import Path
from typing import Self

import click

from src import config, param_types
from src.create_nightcore import Reverb, Speed, SpeedsAndReverbs, create_nightcore
from src.nightcore_to_video import Preset, nightcore_to_video
from src.upload_to_youtube import upload_to_youtube
from src.working_directory import WorkingDirectory


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class Step(Enum):
    CREATE_NIGHTCORE = auto()
    NIGHTCORE_TO_VIDEO = auto()
    UPLOAD_TO_YOUTUBE = auto()

    @classmethod
    @property
    def min(cls) -> Self:
        return min(cls, key=lambda step: step.value)

    @classmethod
    @property
    def max(cls) -> Self:
        return max(cls, key=lambda step: step.value)


@click.command(help="""
Create slowed and nightcore versions of a track and upload them to YouTube.

<working-directory>: Directory where the track and its cover art are located
[<speed> [reverb]]...: Speed and reverb parameters of the final tracks
""")
@click.argument(
    'working_directory',
    type=click.Path(path_type=Path, exists=True, file_okay=False, readable=True, writable=True),
    metavar='[working-directory]',
)
@click.argument(
    'speeds_and_reverbs',
    required=False,
    type=click.IntRange(0, 200),
    nargs=-1,
    metavar='[<speed> [reverb]]...',
)
@click.option(
    '--steps',
    '-ss',
    type=param_types.RangeParamType(min_start=Step.min.value, max_end=Step.max.value),
    default=f'{Step.min.value}:{Step.max.value}',
    show_default=True,
    help='Select pipeline steps using range',
    metavar='',
)
@click.option(
    '--step',
    '-s',
    type=click.IntRange(Step.min.value, Step.max.value),
    help='Select specific pipeline step',
    metavar='',
)
@click.option(
    '--gui',
    '-g',
    is_flag=True,
    help='Run the `create-nightcore` step with a graphical interface',
)
@click.option(
    '--preset',
    '-p',
    type=click.Choice([x.value for x in Preset], case_sensitive=False),
    default=Preset.DEFAULT.value,
    show_default=True,
    help='Set preset for the `ffmpeg` in the `nightcore-to-video` step',
)
@click.option(
    '--ratio',
    '-r',
    type=param_types.RatioParamType(min_ratio=config.MIN_VIDEO_RATIO, max_ratio=config.MAX_VIDEO_RATIO),
    default='16:9',
    show_default=True,
    help='Select a nightcore video ratio in the form of `width:height`',
    metavar='',
)
def cli(**kwargs):
    asyncio.run(async_cli(**kwargs))


async def async_cli(
        working_directory: Path,
        speeds_and_reverbs: tuple[int],
        steps: param_types.RangeParamType.TYPE,
        step: int,
        gui: bool,
        preset: str,
        ratio: param_types.RatioParamType.TYPE,
):
    # parameter validation and conversion
    working_directory = WorkingDirectory(working_directory.resolve())
    preset = Preset(preset)

    def has_step(checked_step: Step):
        return checked_step.value in set(range(steps[0], steps[1] + 1) if not step else [step])

    if has_step(Step.CREATE_NIGHTCORE):
        if not (speeds_and_reverbs := extract_speed_and_reverb_tuples(speeds_and_reverbs)):
            raise click.MissingParameter('At least one speed parameter of the final track is required if \'create-nightcore\' step is involved')

    logger.info(f'Detected track: \'{working_directory.get_track_path(raise_if_not_exists=True).stem}\'')


    # pipeline steps
    start_total_time = time.time()

    for current_step, log_message, callback in [
        (
                Step.CREATE_NIGHTCORE,
                'Creating nightcore',
                lambda: create_nightcore(working_directory, speeds_and_reverbs, gui=gui),
        ),
        (
                Step.NIGHTCORE_TO_VIDEO,
                'Converting nightcore to video',
                lambda: nightcore_to_video(working_directory, preset=preset, ratio=ratio),
        ),
        (
                Step.UPLOAD_TO_YOUTUBE,
                'Uploading videos to YouTube',
                lambda: upload_to_youtube(working_directory),
        ),
    ]:
        if has_step(current_step):
            logger.info('')
            logger.info(f'{current_step.value}. {log_message}')
            start_time = time.time()

            result = callback()
            if inspect.isawaitable(result): await result

            logger.info(f'Step execution time: {int(time.time() - start_time):.0f}s')

    logger.info('')
    logger.info(f'Pipeline execution time: {int(time.time() - start_total_time):.0f}s')


def extract_speed_and_reverb_tuples(speeds_and_reverbs: list[Speed | Reverb]) -> SpeedsAndReverbs:
    speeds = []
    reverbs = []
    i = 0

    while i < len(speeds_and_reverbs):
        speed = speeds_and_reverbs[i]
        if not (50 <= speed <= 200): raise click.BadParameter(f'Speed must be between 50 and 200 and reverb between 0 and 50. Given: {speed} ({i + 1}-th number parameter).')
        speeds.append(speed); i += 1

        if i < len(speeds_and_reverbs) and 0 <= speeds_and_reverbs[i] < 50: reverbs.append(speeds_and_reverbs[i]); i += 1
        else: reverbs.append(0)

    return list(zip(speeds, reverbs))


if __name__ == '__main__':
    cli()
