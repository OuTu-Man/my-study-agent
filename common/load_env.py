import os

from dotenv import load_dotenv
from loguru import logger


def load_env():
    load_dotenv()
    logger.info("✅ loaded the env")


if __name__ == "__main__":
    load_env()
    print(os.environ)
