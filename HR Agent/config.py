import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or "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" #"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"  "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"
