import dotenv
import os
import logging as log

log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
dotenv.load_dotenv()

RULE_34_BACKEND_URL: str = os.getenv('RULE_34_BACKEND_URL', 'https://api.rule34.xxx/index.php')
IMAGE_PLACEHOLDER_URL: str = os.getenv('PLACEHOLDER_IMAGE_URL', 'https://developers.elementor.com/docs/assets/img/elementor-placeholder-image.png')
TAGS_PATH: str = os.getenv('TAGS_PATH', 'tags.json')
GROUP_COUNT: int = 14
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")