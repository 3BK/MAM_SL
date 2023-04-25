#!/usr/bin/env python3

import time
import sys
import os
import json
import base64

# selenium 4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import logging
from webdriver_manager.core.logger import set_logger

#TODO store hazmat in protected file
TARGET_URL      = ''
TARGET_USERNAME = ''
TARGET_PASSWORD = ''

def get_status_code(mydriver, url):
    for entry in mydriver.get_log('performance'):
        for k, v in entry.items():
            if k == 'message' and 'status' in v:
                msg = json.loads(v)['message']['params']
                for mk, mv in msg.items():
                    if mk == 'response':
                        response_url = mv['url']
                        response_status = mv['status']
                        if response_url == url:
                            return response_status

def bk_debug(driver):
  print("innerHTML")
  print (driver.page_source)
  print("outerHTML")
  html = driver.execute_script("return document.documentElement.outerHTML;")
  print("attributes")
  ids = driver.find_elements(By.XPATH,'//*[@id]')
  for my_ii in ids:
    print (my_ii.get_attribute('id'))

capabilities = DesiredCapabilities.CHROME
capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

logger = logging.getLogger("custom_logger")
logger.setLevel(logging.CRITICAL)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler("custom.log"))
set_logger(logger)

options = Options()

if sys.platform == "linux" or sys.platform == "linux2":
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox") # indent this line
    options.add_argument("--headless") # Add this line
    options.add_argument("--disable-gpu") # Add this line
    options.add_argument('--log-level=ALL')

service=ChromeService(executable_path=ChromeDriverManager(path=r'./Drivers/').install(), port=9515, log_path='./chromedriver.log')

driver = webdriver.Chrome( service=service ,options=options)

try:
  t_username  = TARGET_USERNAME
  t_password = TARGET_PASSWORD
  t_opening = time.time()
  driver.get(TARGET_URL)
  WebDriverWait(driver, 10).until(lambda x: ("IBM" +b'\302\240'.decode('utf-8') + "Maximo") in driver.title)
  t_opened = time.time()
  assert ("IBM" +b'\302\240'.decode('utf-8') + "Maximo") in driver.title
  username = driver.find_element(By.ID, "j_username")
  password = driver.find_element(By.ID, "j_password")
  loginbutton = driver.find_element(By.ID, "loginbutton")
  t_loggingin = time.time()
  username.send_keys(t_username)

  password.send_keys("")
  password.send_keys(t_password)
  loginbutton.click()

  WebDriverWait(driver, 30).until(lambda x: any(t in x.title for t in ['Start Center', 'IBM']))

  if ("IBM") in driver.title:
    body =driver.find_element(By.TAG_NAME, 'body').text

    if 'Login Error' in body:
      print('Login Error')
      returnbutton = driver.find_element(By.XPATH, "//button[text()= 'Return']")
      returnbutton.click()
    else:
      content = driver.find_element(By.CLASS_NAME,'messageDesc').text
      print(content)
      print ("open (%s); login (-); logout (-); total (-)" % ((t_opened-t_opening)))
      operand = "N" +":"+ str(t_opened-t_opening) +":"+ ":"+ ":"

  if ("Start Center") in driver.title:
    t_loggedin = time.time()
    assert "Start Center" in driver.title
    logoutbutton = driver.find_element(By.ID, 'titlebar_hyperlink_8-lbsignout')
    t_loggingout = time.time()
    logoutbutton.click()
    WebDriverWait(driver, 30).until(lambda x: any(t in x.title for t in ['IBM']))

    body = driver.find_element(By.TAG_NAME, 'body').text

    if "You have successfully signed out" in body:
      t_loggedout = time.time()
      print ("open (%s); login (%s); logout (%s); total (%s)" % ((t_opened-t_opening),(t_loggedin-t_loggingin), (t_loggedout-t_loggingout), (t_loggedout-t_opening)))
      operand = "N" +":"+ str(t_opened-t_opening) +":"+ str(t_loggedin-t_loggingin) +":"+ str(t_loggedout-t_loggingout)+":"+ str(t_loggedout-t_opening)
    else:
      print(body)
      print ("open (%s); login (%s); logout - ; total -" % ((t_opened-t_opening),(t_loggedin-t_loggingin)))
      operand = "N" +":"+ str(t_opened-t_opening) +":"+ str(t_loggedin-t_loggingin) +"::"
    driver.quit()
except:
  log_file = open("./test.log","a")
  sys.stdout = log_file
  print("%s" % (time.time()), flush=True)
  print("Unexpected error: %s" % ( sys.exc_info()[0]), flush=True)
  log_file.close()
  raise
