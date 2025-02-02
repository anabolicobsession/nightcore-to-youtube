import click


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
def main(track_dir, speeds_and_reverbs, start_step, end_step, step):
    ...


if __name__ == '__main__':
    main()
