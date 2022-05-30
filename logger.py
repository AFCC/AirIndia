import logging, os
from logging.handlers import TimedRotatingFileHandler

CWD = os.path.abspath(os.getcwd())
logging.basicConfig(level=logging.INFO,
                    handlers=[TimedRotatingFileHandler(
                        CWD + "\\logs\\log_file.txt", when="midnight"), logging.StreamHandler()],
                    format='%(asctime)s - %(levelname)s - %(message)s')