#!/usr/bin/env python3

# selenium 4
import time
import sys
import os
import subprocess
import json
import base64
from datetime import datetime
import tldextract

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
  return


def try_to_login(driver, my_stats):
    am_i_logged_in = False
    now = datetime.now()
    now_d = now.strftime("%Y%m%d")
    try:
        t_username = ''
        t_token    = ''
        t_url      = ''
        with open('./target_username') as fd:
            t_username = fd.read().rstrip()
        with open('./target_url') as fd:
            t_url = fd.read().rstrip()
        domain_info = tldextract.extract(t_url)
        with open('./target_token') as fd:
            t_token = base64.b64decode(fd.read()).decode("utf-8").rstrip()

        my_stats['opening'] = time.time()
        for i in range(8):
            driver.delete_all_cookies()
            driver.get(t_url)
            WebDriverWait(driver, 10).until(lambda x: ("IBM" +b'\302\240'.decode('utf-8') + "Maximo") in driver.title)
            my_stats['opened'] = time.time()
            assert ("IBM" +b'\302\240'.decode('utf-8') + "Maximo") in driver.title
            username = driver.find_element(By.ID, "j_username")
            password = driver.find_element(By.ID, "j_password")
            loginbutton = driver.find_element(By.ID, "loginbutton")
            my_stats['loggingin'] = time.time()

            username.send_keys(t_username)
            password.send_keys("")
            password.send_keys(t_token)
            loginbutton.click()

            WebDriverWait(driver, 30).until(lambda x: any(t in x.title for t in ['Start Center', 'IBM']))

            if ("IBM") in driver.title:
              body =driver.find_element(By.TAG_NAME, 'body').text
              if 'Login Error' in body:
                #print('LTPA error')
                returnbutton = driver.find_element(By.XPATH, "//button[text()= 'Return']")
                my_stats['loggingout'] = time.time()
                t_loggingout = time.time()
                returnbutton.click()
                WebDriverWait(driver, 10).until(lambda x: ("IBM" +b'\302\240'.decode('utf-8') + "Maximo") in driver.title)
                my_stats['loggedout'] = time.time()
                #print('loggedout')

              else:
                content = driver.find_element(By.CLASS_NAME,'messageDesc').text
                print(driver.title)
                #print(content)

            if ("Start Center") in driver.title:
                #print('loggedin')
                my_stats['loggedin'] = time.time()
                am_i_logged_in = True
                break

            time.sleep(1)

        return am_i_logged_in

    except:
        log_file = open("../audit/exception."+now_d+".log","a")
        sys.stdout = log_file
        print("%s" % (time.time()), flush=True)
        print("Unexpected error: %s" % ( sys.exc_info()[0]), flush=True)
        log_file.close()
        raise


now = datetime.now()
now_d = now.strftime("%Y%m%d")

capabilities = DesiredCapabilities.CHROME
capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

logger = logging.getLogger("custom_logger")
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler("../audit/custom."+now_d+".log"))
set_logger(logger)

options = Options()

if sys.platform == "linux" or sys.platform == "linux2":
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument('--log-level=ALL')

# If file exists, delete it.
myfile = "../intermediate/measurement.json"
if os.path.isfile(myfile):
    os.remove(myfile)

service=ChromeService(executable_path=ChromeDriverManager(path=r'./Drivers/').install(), port=9515, log_path='../audit/chromedriver.'+now_d+'.log')


driver = webdriver.Chrome( service=service ,options=options)

#print(driver.get_cookies())
#driver.delete_all_cookies()

measurements = {'topic':'frontend-latency', 'tagunits':'Phase', 'units':'msec', '_records' : []}
my_stats = {}
if True == try_to_login(driver, my_stats):
    #print('success')
    try:
      with open('./target_url') as fd:
          t_url = fd.read().rstrip()
      domain_info = tldextract.extract(t_url)

      if ("Start Center") in driver.title:
        my_stats['loggedin'] = time.time()
        assert "Start Center" in driver.title
        logoutbutton = driver.find_element(By.ID, 'titlebar_hyperlink_8-lbsignout')
        my_stats['loggingout'] = time.time()
        logoutbutton.click()

        WebDriverWait(driver, 30).until(lambda x: any(t in x.title for t in ['IBM']))

        body =driver.find_element(By.TAG_NAME, 'body').text
        if "You have successfully signed out" in body:
          returnbutton = driver.find_element(By.XPATH, "//button[text()= 'Return']")
          returnbutton.click()
          WebDriverWait(driver, 10).until(lambda x: ("IBM" +b'\302\240'.decode('utf-8') + "Maximo") in driver.title)

          my_stats['loggedout'] = time.time()
          measurements['_records'].append({'tag':domain_info.subdomain+'.open','measure': (int(round(my_stats['opened']-my_stats['opening'],3)*1000))})
          measurements['_records'].append({'tag':domain_info.subdomain+'.loggingin','measure': (int(round(my_stats['loggedin']-my_stats['loggingin'],3)*1000))})
          measurements['_records'].append({'tag':domain_info.subdomain+'.loggingout','measure': (int(round(my_stats['loggedout']-my_stats['loggingout'],3)*1000))})
          measurements['_records'].append({'tag':domain_info.subdomain+'.total','measure': (int(round(my_stats['loggedout']-my_stats['opening'],3)*1000))})
          with open('../intermediate/measurement.json','w') as fd:
              json.dump(measurements, fd)
          #print(measurements)

        else:
          print(driver.page_source)
          measurements['_records'].append({'tag':domain_info.subdomain+'.open','measure': (int(round(my_stats['opened']-my_stats['opening'],3)*1000))})
          measurements['_records'].append({'tag':domain_info.subdomain+'.loggingin','measure': (int(round(my_stats['loggedin']-my_stats['loggingin'],3)*1000))})
          measurements['_records'].append({'tag':domain_info.subdomain+'.loggingout','measure':-1})
          measurements['_records'].append({'tag':domain_info.subdomain+'.total','measure': -1})
          with open('../intermediate/measurement.json','w') as fd:
              json.dump(measurements, fd)
      #print(measurements)
      #print(my_stats)
      driver.quit()
    except:
      log_file = open("../audit/exception."+now_d+".log","a")
      sys.stdout = log_file
      print("%s" % (time.time()), flush=True)
      print("Unexpected error: %s" % ( sys.exc_info()[0]), flush=True)
      log_file.close()
      raise
else:
    print(driver.title)
    driver.quit()
