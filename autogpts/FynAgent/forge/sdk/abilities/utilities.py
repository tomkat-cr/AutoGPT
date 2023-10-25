import os
from ..forge_log import ForgeLogger

LOG = ForgeLogger(__name__)


def log_debug(message):
    """Sends a message to the Forge log if log level is set to Debug"""
    if os.getenv("LOG_LEVEL") == "DEBUG":
        LOG.info(message)


def get_default_resultset():
    """Returns an standard base resultset, to be used in the building
       of responses to the outside world
    """
    resultset = {
        'error': False,
        'error_message': None,
        'resultset': {}
    }
    return resultset
