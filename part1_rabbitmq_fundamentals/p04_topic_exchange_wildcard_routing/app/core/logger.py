import logging, sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)

