import asyncio
import logging
from enum import Enum, auto
from pathlib import Path

import click

from src.create_nightcore import Reverb, Speed, SpeedsAndReverbs, create_nightcore
from src.nightcore_to_video import Preset, nightcore_to_video
from src.working_directory import WorkingDirectory


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@click.command(help="""
Create slowed and nightcore versions of a track and upload them to YouTube.

<track-directory>: Directory where the track and its cover art are located.
[<speed> [reverb]]...: Speed and reverb parameters of the final tracks.
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
    '-s',
    '--start-step',
    type=click.IntRange(1, 3),
    default=1,
    show_default=True,
    help='Starting pipeline step.',
    metavar='',
)
@click.option(
    '-e',
    '--end-step',
    type=click.IntRange(1, 3),
    default=3,
    show_default=True,
    help='Ending pipeline step.',
    metavar='',
)
@click.option(
    '-st',
    '--step',
    type=click.IntRange(1, 3),
    show_default=True,
    help='Single pipeline step.',
    metavar='',
)
@click.option(
    '--gui',
    '-g',
    is_flag=True,
    help='Run with a graphical interface instead of console mode.',
)
@click.option(
    '--preset',
    '-p',
    type=click.Choice([x.value for x in Preset], case_sensitive=False),
    default=Preset.DEFAULT.value,
    show_default=True,
    help='Preset for `ffmpeg`.',
)
def cli(**kwargs):
    asyncio.run(async_cli(**kwargs))


async def async_cli(
        working_directory: Path,
        speeds_and_reverbs: tuple[int],
        start_step: int,
        end_step: int,
        step: int,
        gui: bool,
        preset: str,
):
    # parameter validation
    if not (start_step <= end_step):
        raise click.BadParameter(f'The starting step ({start_step}) must be greater than or equal to the ending step ({end_step}).')

    def has_step(checked_step: Step):
        return checked_step.value in {step} if step else set(range(start_step, end_step + 1))

    speed_and_reverbs = extract_speed_and_reverb_tuples(speeds_and_reverbs)

    if has_step(Step.CREATE_NIGHTCORE):
        if not speed_and_reverbs:
            raise click.MissingParameter("At least one speed parameter of the final track is required if 'create-nightcore' step is involved")


    # conversions
    working_directory = WorkingDirectory(working_directory)
    preset = Preset(preset)


    # pipeline steps
    if has_step(Step.CREATE_NIGHTCORE):
        logger.info(f'{Step.CREATE_NIGHTCORE.value}. Creating nightcore')
        await create_nightcore(working_directory, speed_and_reverbs, gui=gui)

    if has_step(Step.NIGHTCORE_TO_VIDEO):
        logger.info(f'{Step.NIGHTCORE_TO_VIDEO.value}. Converting nightcore to video')
        nightcore_to_video(working_directory, preset=preset)


class Step(Enum):
    CREATE_NIGHTCORE = auto()
    NIGHTCORE_TO_VIDEO = auto()


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
