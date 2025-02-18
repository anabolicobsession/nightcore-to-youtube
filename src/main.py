import asyncio
import logging
from enum import Enum, auto
from pathlib import Path
from typing import Self

import click

from src.create_nightcore import Reverb, Speed, SpeedsAndReverbs, create_nightcore
from src.nightcore_to_video import Preset, nightcore_to_video
from src.working_directory import WorkingDirectory


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class RangeParamType(click.ParamType):
    name = 'range'
    TYPE = (int, int)

    def __init__(self, min_start=None, max_end=None):
        self.min_start = min_start
        self.max_end = max_end

    def convert(self, value, param, ctx) -> TYPE:
        try:
            start, end = map(int, value.split(':'))
            if not (start <= end): raise ValueError('Start should be less or equal to end')
            if not (self._is_within_range(start) and self._is_within_range(end)): raise ValueError(f'Given range is not within allowed range: `{self.min_start}:{self.max_end}`')
            return start, end

        except Exception as e:
            self.fail(f'Invalid range format: `{value}`. Expected format: `start:end`. Error: {str(e)}', param, ctx)

    def _is_within_range(self, x: int):
        return self.min_start <= x <= self.max_end


class Step(Enum):
    CREATE_NIGHTCORE = auto()
    NIGHTCORE_TO_VIDEO = auto()

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
    type=RangeParamType(min_start=Step.min.value, max_end=Step.max.value),
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
def cli(**kwargs):
    asyncio.run(async_cli(**kwargs))


async def async_cli(
        working_directory: Path,
        speeds_and_reverbs: tuple[int],
        steps: RangeParamType.TYPE,
        step: int,
        gui: bool,
        preset: str,
):
    def has_step(checked_step: Step):
        return checked_step.value in set(range(steps[0], steps[1] + 1) if not step else [step])


    # parameter validation
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
