import logging

FORMAT: str = '%(asctime)s [%(levelname)s] - %(message)s'

class GUIHandler(logging.Handler):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def emit(self, record):
        try:
            message = self.format(record)
            self.textbox.write(f"{message}\n")
        except Exception:
            self.handleError(record)

def setup(textbox=None, LEVEL: int=20):
    debug = logging.NOTSET
    if LEVEL >= 10:
        debug = logging.DEBUG
    if LEVEL >= 20:
        debug = logging.INFO
    if LEVEL >= 30:
        debug = logging.WARNING
    if LEVEL >= 40:
        debug = logging.ERROR
    if LEVEL >= 50:
        debug = logging.CRITICAL

    logger = logging.getLogger()
    logger.setLevel(debug)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    stdio_handler = logging.StreamHandler()
    stdio_handler.setLevel(debug)
    stdio_handler.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(stdio_handler)

    if textbox:
        gui_handler = GUIHandler(textbox)
        gui_handler.setLevel(debug)
        gui_handler.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(gui_handler)
