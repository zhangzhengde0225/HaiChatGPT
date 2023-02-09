
import os
import logging
os.environ["LOGGING_LEVEL"] = logging.ERROR

from . import env

from .version import __version__, __version_suffix__, __appname__, __author__, __email__, __affiliation__, __supervisor__, __collaborator__, __url__
# from .apis import HaiGF, 
from .apis import HaiChatGPT

