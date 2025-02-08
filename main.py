import logging
from enum import Enum

import click

from create_nightcore import Reverb, Speed, SpeedsAndReverbs, create_nightcore


logging.basicConfig(level=logging.INFO, format='%(message)s')


class Step(Enum):
    CREATE_NIGHTCORE = 1


class Main:
    def __init__(self, steps, track_dir, speeds_and_reverbs):
        self.steps = steps
        self.track_dir = track_dir
        self.speeds_and_reverbs = speeds_and_reverbs

    @staticmethod
    @click.command(help="""
    Create slowed and nightcore versions of a track and upload them to YouTube.
    
    <track-directory>: Directory where the track and its cover art are located.
    [<speed> [reverb]]...: Speed and reverb parameters of the final tracks.
    """)
    @click.argument(
        'track_dir',
        required=False,
        type=click.Path(exists=True, file_okay=False, readable=True),
        metavar='[track-directory]',
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
    def cli(track_dir, speeds_and_reverbs, start_step, end_step, step):
        if not (start_step <= end_step):
            raise click.BadParameter(f'The starting step ({start_step}) must be greater than or equal to the ending step ({end_step}).')

        main = Main(
            track_dir=track_dir,
            speeds_and_reverbs=Main.extract_speed_and_reverb_tuples(speeds_and_reverbs),
            steps={step} if step else set(range(start_step, end_step + 1)),
        )

        if main.has_step(Step.CREATE_NIGHTCORE):
            if not main.speeds_and_reverbs:
                raise click.MissingParameter("At least one speed parameter of the final track is required if 'create-nightcore' step is involved")

        main.run()

    def run(self):
        if self.has_step(Step.CREATE_NIGHTCORE): create_nightcore(self.track_dir, self.speeds_and_reverbs, debug=False)

    def has_step(self, checked_step: Step):
        return checked_step.value in self.steps

    @staticmethod
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
    Main.cli()
