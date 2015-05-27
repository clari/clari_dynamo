import logging

FORMAT = \
"%(asctime)s %(pathname)s:%(lineno)s:%(funcName)s - %(levelname)s - %(message)s"

logging.basicConfig(
    level=logging.DEBUG,
    format=FORMAT)