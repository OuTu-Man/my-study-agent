import os

from dotenv import load_dotenv


def load_env():
    load_dotenv()


if __name__ == "__main__":
    load_env()
    print(os.environ)
