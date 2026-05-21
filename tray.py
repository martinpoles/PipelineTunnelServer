import threading
import sys
import os

from PIL import Image
import pystray
from pystray import MenuItem as item

from logger import logger
from main import main
from ngrok_util import stop_ngrok

def run_app():

    try:
        logger.info("Starting application")
        main()

    except Exception as e:
        logger.exception(e)


def quit_app(icon):

    logger.info("Closing application")

    stop_ngrok()

    icon.stop()

    sys.exit()

def resource_path(relative_path):

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


image = Image.open(resource_path("icon.png"))

icon = pystray.Icon(
    "PipelineTunnel",
    image,
    "PipelineTunnel",
    menu=pystray.Menu(
        item("Quit", quit_app)
    )
)

threading.Thread(
    target=run_app,
    daemon=True
).start()

icon.run()