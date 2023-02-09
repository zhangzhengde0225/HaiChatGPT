
import os

api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    os.environ["OPENAI_API_KEY"] = "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"
