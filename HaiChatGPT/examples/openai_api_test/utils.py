
import os, sys
from pathlib import Path
here = Path(__file__).parent


def get_api_key():
    root_path = here.parent.parent.parent
    if root_path not in sys.path:
        sys.path.append(str(root_path))
    from HaiChatGPT.apis import AuthManager

    auth_manager = AuthManager()
    api_key = auth_manager.current_api_key

    return api_key