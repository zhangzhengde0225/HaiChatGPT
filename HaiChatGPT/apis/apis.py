import os, sys
from pathlib import Path
here = Path(__file__).parent


# try damei
try:
    import damei
except:
    sys.path.insert(0, f'{here.parent.parent.parent}/damei')
    import damei


try:
    import HaiGF
except:
    sys.path.insert(0, f'{here.parent.parent.parent}/hai-gui-framework')
    import HaiGF



