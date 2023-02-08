import os, sys
from pathlib import Path
here = Path(__file__).parent

try:
    import HaiGF
except:
    sys.path.insert(0, f'{here.parent.parent.parent}/hai-gui-framework')
    import HaiGF


