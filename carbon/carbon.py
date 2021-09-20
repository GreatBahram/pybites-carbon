import importlib
import os
from contextlib import contextmanager
from time import sleep
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

CARBON_URL = "https://carbon.now.sh?l={language}&code={code}&bg={background}&t={theme}"

# in case of a slow connection it might take a bit longer to download the image
SECONDS_SLEEP_BEFORE_DOWNLOAD = int(os.environ.get("SECONDS_SLEEP_BEFORE_DOWNLOAD", 3))


def _create_carbon_url(code, **carbon_options: str) -> str:
    language = carbon_options["language"]
    background = carbon_options["background"]
    theme = carbon_options["theme"]

    url = CARBON_URL.format(
        language=quote_plus(language),
        code=quote_plus(code),
        background=quote_plus(background),
        theme=quote_plus(theme),
    )

    return url


def load_driver_dynamically(webdriver: str):
    """Load the driver and its corresponding driver according to
    the user input."""
    try:
        driver = importlib.import_module(f"selenium.webdriver.{webdriver}.webdriver")
        driver = getattr(driver, "WebDriver")
        options = importlib.import_module(f"selenium.webdriver.{webdriver}.options")
        options = getattr(options, "Options")
    except ModuleNotFoundError:
        raise ValueError(f"invalid webdriver: {webdriver}") from None
    return driver, options


def _validate_driver_path(driver_path) -> None:
    DRIVER_PATH = os.environ.get("DRIVER_PATH")
    if DRIVER_PATH is None:
        raise SystemExit("Please set the DRIVER_PATH environment variable")


@contextmanager
def cwd(path):
    old_path = os.getcwd()
    try:
        yield os.chdir(path)
    finally:
        os.chdir(old_path)


def create_code_image(code: str, **kwargs: str) -> None:
    """Generate a beautiful Carbon code image"""
    WebDriver, Options = load_driver_dynamically(kwargs["webdriver"])

    options = Options()
    options.headless = not bool(kwargs.get("interactive", False))
    destination = kwargs.get("destination", os.getcwd())
    # prefs = {"download.default_directory": destination}
    # options.add_experimental_option("prefs", prefs)
    # NEXT: options.add_argument(f"download.default_directory={destination}")
    # TODO: change download directory for any webdriver
    # TODO: never ask for download the folling mime type
    from selenium.webdriver import Firefox

    url = _create_carbon_url(code, **kwargs)
    with cwd(destination):
        with Firefox(executable_path=kwargs["driver_path"]) as driver:
            driver.get(url)
            driver.find_element_by_id("export-menu").click()
            driver.find_element_by_id("export-png").click()
            # make sure it has time to download the image
            sleep(SECONDS_SLEEP_BEFORE_DOWNLOAD)
