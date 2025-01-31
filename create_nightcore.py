import inspect
import os

from playwright.sync_api import Page, sync_playwright


def absolutize_project_path(project_path):
    return os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), project_path)


def main():
    Page.set_slider_value = set_slider_value

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            '/home/whiplash/.config/google-chrome',
            args=['--profile-directory=Profile 34'],
            headless=False,
        )
        page: Page
        page = browser.pages[0]

        page.goto('https://nightcore.studio/')
        page.set_input_files('input[type="file"]', absolutize_project_path('input.mp3'))
        page.wait_for_selector(r"body > main > div.container.mx-auto.px-2.md\:px-5.mt-5.sm\:mt-20.md\:mt-36.text-center > div > div.relative > div.flex.gap-1.items-center.justify-center > button", timeout=3000)
        page.set_slider_value('div[role="slider"][aria-valuemin="0.5"][aria-valuemax="2"]', 0.5, step=0.01)

        page.pause()
        browser.close()


def set_slider_value(page: Page, selector, target_value, step):
    slider = page.wait_for_selector(selector, timeout=3000)
    initial_value = float(slider.get_attribute('aria-valuenow'))
    steps = int(abs(target_value - initial_value) / step)
    key = 'ArrowRight' if target_value > initial_value else 'ArrowLeft'
    slider.click()
    for _ in range(steps): page.keyboard.press(key)


if __name__ == '__main__':
    main()
