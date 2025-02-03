import logging
import os
from contextlib import contextmanager
from os.path import join

from playwright.sync_api import Page, sync_playwright

from paths import Path, absolutize_project_path


DOWNLOADS_DIR = 'downloads'


logger = logging.getLogger(__name__)


Speed = int
Reverb = int
SpeedsAndReverbs = list[tuple[Speed, Reverb]]


class Selector:
    PAUSE = r'body > main > div.container.mx-auto.px-2.md\:px-5.mt-5.sm\:mt-20.md\:mt-36.text-center > div > div.relative > div.flex.gap-1.items-center.justify-center > button'
    DOWNLOAD = r'body > main > div.container.mx-auto.px-2.md\:px-5.mt-5.sm\:mt-20.md\:mt-36.text-center > div > div.mt-10.space-y-2.max-w-\[300px\].mx-auto > button:nth-child(1)'


def create_nightcore(track_dir: Path, speeds_and_reverbs: SpeedsAndReverbs):
    remove_previous_nightcore(track_dir)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir='/home/whiplash/.config/microsoft-edge',
            args=['--profile-directory=Profile 34'],
            channel='msedge',
            headless=False,
        )

        setup_page_methods()
        page = context.pages[0]
        downloader = Downloader(page)

        page.goto('https://nightcore.studio/')
        page.set_input_files('input[type="file"]', absolutize_project_path('input.mp3'))
        page.wait_for_selector(Selector.PAUSE, timeout=2000).click()
        set_nightcore_parameters(page, speed=1.3, reverb=5)
        with downloader.download_as('output.mp3'): page.wait_for_selector(Selector.DOWNLOAD, timeout=1000).click()

        page.pause()
        context.close()


def remove_previous_nightcore(dir_path: Path):
    removed = []

    for name in os.listdir(dir_path):
        path = os.path.join(dir_path, name)

        if os.path.isfile(path):
            base_name, extension = os.path.splitext(name)

            if base_name.isdigit() and extension.lower() == '.mp3':
                os.remove(path); removed.append(name)

    logger.info(f'Removed from {dir_path}: {", ".join(removed)}')


class Downloader:
    DOWNLOADS_PATH = absolutize_project_path(DOWNLOADS_DIR)

    def __init__(self, page: Page):
        self.page = page
        self.page.on('download', self.handle_download)
        self.file_name = None

    def handle_download(self, download):
        download.save_as(join(self.DOWNLOADS_PATH, download.suggested_filename if not self.file_name else self.file_name))
        self.file_name = None

    @contextmanager
    def download_as(self, file_name, wait_for_download_to_start=3000, wait_for_download_to_complete=0):
        self.file_name = file_name
        yield
        self.page.wait_for_event('download', timeout=wait_for_download_to_start)
        self.page.wait_for_timeout(wait_for_download_to_complete)


def set_nightcore_parameters(page, speed=1, reverb=0):
    page.move_slider('div[role="slider"][aria-valuemin="-60"][aria-valuemax="0"]', 300)
    page.set_slider_value('div[role="slider"][aria-valuemin="0.5"][aria-valuemax="2"]', speed, step=0.01)
    page.set_slider_value('div[role="slider"][aria-valuemin="0.01"][aria-valuemax="10"]', reverb + 0.01, step=0.05)


def setup_page_methods():
    Page.move_slider = move_slider
    Page.set_slider_value = set_slider_value


def move_slider(page: Page, selector, steps):
    slider = page.wait_for_selector(selector, timeout=3000)
    key = 'ArrowRight' if steps > 0 else 'ArrowLeft'
    slider.click()
    for _ in range(abs(steps)): page.keyboard.press(key)


def set_slider_value(page: Page, selector, target_value, step):
    slider = page.wait_for_selector(selector, timeout=3000)
    initial_value = float(slider.get_attribute('aria-valuenow'))
    steps = int(abs(target_value - initial_value) / step)
    key = 'ArrowRight' if target_value > initial_value else 'ArrowLeft'
    slider.click()
    for _ in range(steps): page.keyboard.press(key)
