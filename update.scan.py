#!/usr/bin/env python3

# selenium 4
import logging
import os
from datetime import datetime

#from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.logger import set_logger

os.environ['WDM_PROGRESS_BAR'] = str(0)

now = datetime.now()
now_d = now.strftime("%Y%m%d")

logger = logging.getLogger("update_logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler("../audit/update."+now_d+".log"))

set_logger(logger)

executable_path=ChromeDriverManager(path=r'./Drivers/',cache_valid_range=7).install()
