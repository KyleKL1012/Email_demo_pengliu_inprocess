from email.mime import base
import yaml
import os
import logging

# def get_logger():
    # # create logger
    # current_logger = logging.getLogger(__name__)
    # current_logger.setLevel(logging.INFO)
    # # remove all previous handler
    # current_logger.handlers.clear()
    # # create handler
    # # fh = logging.FileHandler(log_file_name, encoding='UTF-8')
    # fh = logging.StreamHandler()
    # fh.setLevel(logging.INFO)
    # # create formatter
    # formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # # add formatter to handler
    # fh.setFormatter(formatter)
    # # add handler to logger
    # current_logger.addHandler(fh)
    # return current_logger

# logger = get_logger()


logger = logging.getLogger("streamlit")
logger.setLevel(level=logging.INFO)
logger.handlers.clear()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


basedir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(basedir,"config_file/esg_chat.yaml"), "r") as stream:
    config = yaml.safe_load(stream)