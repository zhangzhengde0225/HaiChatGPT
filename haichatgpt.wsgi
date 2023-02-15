import os
import sys
from pathlib import Path
here = Path(__file__).parent

sys.path.insert(0, str(here))

from HaiChatGPT.src.browser.app import app as application