
from pathlib import Path
import environ

env = environ.FileAwareEnv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent