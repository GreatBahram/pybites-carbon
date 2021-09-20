import argparse
import os

import pyperclip

from . import __version__ as version


def get_code_from_file(filename: str) -> str:
    if not os.path.isfile(filename):
        raise argparse.ArgumentTypeError(f"No such file: {filename}")
    with open(os.path.abspath(filename), mode="rt") as fp:
        return fp.read()


def environ_or_required(key: str) -> dict:
    if os.environ.get(key):
        return {"default": os.environ.get(key)}
    else:
        return {"required": True}


def get_args():
    parser = argparse.ArgumentParser(
        description="Create a carbon code image",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {version}"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--file", type=get_code_from_file, help="File with code", dest="code"
    )
    group.add_argument(
        "-c",
        "--clipboard",
        help="Use code on clipboard",
        action="store_const",
        const=pyperclip.paste(),
        dest="code",
    )
    group.add_argument("-s", "--snippet", help="Code snippet", dest="code")

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        default=False,
        help="Run Selenium in interactive (not headless) mode",
    )
    parser.add_argument(
        "-w",
        "--webdriver",
        help="Which selenium webdriver to use",
        choices=["firefox", "chrome"],
        default="chrome",
    )
    parser.add_argument(
        "--driver-path",
        help="Where the webdriver is located, accept value from environment variable as well (DRIVER_PATH)",
        **environ_or_required("DRIVER_PATH"),
    )
    parser.add_argument(
        "-l", "--language", help="Programming language", default="python"
    )
    parser.add_argument(
        "-b", "--background", help="Background color", default="#ABB8C3"
    )
    parser.add_argument("-t", "--theme", help="Name of the theme", default="seti")
    parser.add_argument(
        "-d",
        "--destination",
        default=os.getcwd(),
        help="Specify folder where image should be stored (defaults to current directory)",
    )
    return parser.parse_args()
