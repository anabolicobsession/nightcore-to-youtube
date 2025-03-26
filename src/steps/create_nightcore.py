import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from playwright.async_api import BrowserContext, Page, async_playwright

from src import config
from src.utils.working_directory import WorkingDirectory


Speed = int
Reverb = int
SpeedsAndReverbs = list[tuple[Speed, Reverb]]


logger = logging.getLogger(__name__)


def remove_previous_nightcore(working_directory: WorkingDirectory):
    if paths := working_directory.get_nightcore_paths():
        for x in paths: x.unlink()
        logger.info(f'Cleared files: {", ".join([x.name for x in paths])}')


async def move_slider(page: Page, selector, steps):
    slider = await page.wait_for_selector(selector, timeout=3000)
    key = 'ArrowRight' if steps > 0 else 'ArrowLeft'
    await slider.click()
    for _ in range(abs(steps)): await page.keyboard.press(key)


async def set_slider_value(page: Page, selector, target_value, step):
    slider = await page.wait_for_selector(selector, timeout=3000)
    initial_value = float(await slider.get_attribute('aria-valuenow'))
    steps = round(abs(target_value - initial_value) / step)
    key = 'ArrowRight' if target_value > initial_value else 'ArrowLeft'
    await slider.click()
    for _ in range(steps): await page.keyboard.press(key)


def setup_page_methods():
    Page.move_slider = move_slider
    Page.set_slider_value = set_slider_value


async def set_nightcore_parameters(page, speed=config.STANDARD_SPEED, reverb=config.STANDARD_REVERB):
    await page.move_slider('div[role="slider"][aria-valuemin="-60"][aria-valuemax="0"]', 300)  # set standard volume (100% - maximum)
    await page.set_slider_value('div[role="slider"][aria-valuemin="0.5"][aria-valuemax="2"]', speed / 100, step=0.01)
    await page.set_slider_value('div[role="slider"][aria-valuemin="0.01"][aria-valuemax="10"]', reverb / 10 + 0.01, step=0.05)


class Selector:
    PAUSE = r'body > main > div.container.mx-auto.px-2.md\:px-5.mt-5.sm\:mt-20.md\:mt-36.text-center > div > div.relative > div.flex.gap-1.items-center.justify-center > button'
    DOWNLOAD = r'body > main > div.container.mx-auto.px-2.md\:px-5.mt-5.sm\:mt-20.md\:mt-36.text-center > div > div.mt-10.space-y-2.max-w-\[300px\].mx-auto > button:nth-child(1)'


class Downloader:
    def __init__(self, page: Page, directory: Path):
        self.page = page
        self.directory = directory
        self.file_name = None
        self.page.on('download', lambda download: asyncio.create_task(self.handle_download(download)))
        self.download = None

    @asynccontextmanager
    async def download_as(self, file_name):
        self.file_name = file_name
        yield
        await self.page.wait_for_event('download')
        await self.download.path()  # wait for download to complete
        self.file_name = None

    async def handle_download(self, download):
        self.download = download
        await download.save_as(self.directory / (self.file_name if self.file_name else download.suggested_filename))


async def _create_nightcore(
        context: BrowserContext,
        working_directory: WorkingDirectory,
        speed: Speed,
        reverb: Reverb,
        verbose=False,
):
    page = await context.new_page()
    downloader = Downloader(page, directory=working_directory.get_path(raise_if_not_exists=True))

    def wrap_log(log: str):
        return f'{speed:>3}x{reverb:<2}: {log}'

    await page.goto('https://nightcore.studio/')

    if verbose: logger.info('Uploading track')
    await page.set_input_files('input[type="file"]', working_directory.get_track_path(raise_if_not_exists=True))
    await (await page.wait_for_selector(Selector.PAUSE, timeout=5000)).click()

    if verbose: logger.info('Setting up parameters')
    await set_nightcore_parameters(page, speed=speed, reverb=reverb)

    if verbose: logger.info('Downloading')
    async with downloader.download_as(working_directory.speed_and_reverb_to_path(speed, reverb, 'mp3').name): await (await page.wait_for_selector(Selector.DOWNLOAD, timeout=1000)).click()

    await page.close()


async def create_nightcore(
        working_directory: WorkingDirectory,
        speeds_and_reverbs: SpeedsAndReverbs,
        gui: bool = False,
):
    setup_page_methods()
    remove_previous_nightcore(working_directory)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir='/home/whiplash/.config/microsoft-edge',
            args=['--profile-directory=Profile 34'],
            channel='msedge',
            headless=not gui,
        )
        await asyncio.gather(
            *[
                _create_nightcore(context, working_directory, *x, verbose=y)
                for x, y in zip(
                    speeds_and_reverbs,
                    [True] + [False] * (len(speeds_and_reverbs) - 1),
                )
            ]
        )
        await context.close()
