LOGGER_NAME = 'thompson_narrative_collector'

import logging
import sys
from logging import getLogger, Formatter, Logger, StreamHandler

# Formatter
custmoFormatter = Formatter(
    fmt='[%(asctime)s]%(levelname)s - %(filename)s#%(funcName)s:%(lineno)d: %(message)s',
    datefmt='Y/%m/%d %H:%M:%S'
)

# StreamHandler
STREAM_LEVEL = logging.DEBUG
STREAM_FORMATTER = custmoFormatter
STREAM = sys.stderr

st_handler = StreamHandler(stream=STREAM)
st_handler.setLevel(STREAM_LEVEL)
st_handler.setFormatter(STREAM_FORMATTER)

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)
logger.addHandler(st_handler)
logger.propagate = False