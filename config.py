import yaml
import os
import logging


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