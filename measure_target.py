#!/usr/bin/env python3
"""
MAM Service Level Scanner
"""

import sys
import ssl
import base64
import time
import rrdtool
import urllib3
import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_

TARGET_USERNAME = 'username'
TARGET_PASSWORD = 'username'
HOST            = 'FQDN'
TARGET_URL      = 'TARGET_URL'
TAG             = 'LISTENER'
MEASUREMENTS1   = 'MEASUREMENTS.rrd'
MEASUREMENTS2   = 'MEASUREMENTS.json'
CIPHERS         = (  \
                   'TLS_AES_256_GCM_SHA384:' \
                   'TLS_AES_128_GCM_SHA256:' \
                   'ECDHE-RSA-AES256-GCM-SHA384:' \
                   'ECDHE-RSA-AES128-GCM-SHA256'
                  )

class Tls13Adapter(HTTPAdapter):
    """
    Enable TLSv1.2 .
    """
    def __init__(self, ssl_options=0, login='', password='', **kwargs):
        self.login       = login
        self.password    = password
        self.ssl_options = ssl_options
        super(Tls13Adapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = ssl_.create_urllib3_context( ciphers   = CIPHERS, \
                                           cert_reqs = ssl.CERT_REQUIRED, \
                                           options   = self.ssl_options)

        self.poolmanager = PoolManager(*pool_args, \
                                        ssl_context = ctx, \
                                        cert_reqs='CERT_REQUIRED', \
                                       **pool_kwargs)

with open(TARGET_USERNAME, 'r', encoding='ascii') as fd:
    T_USERNAME = fd.read().rstrip()

with open(TARGET_PASSWORD, 'r', encoding='ascii') as fd:
    T_PASSWORD = base64.b64decode(fd.read()).decode("utf-8").rstrip()

URL = "https://" + HOST + "/" + TAG
ses = requests.Session()
adapter = Tls13Adapter( ssl_options=ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | \
                        ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1, \
                        login = '', password ='' )
ses.mount(URL, adapter)
t_opening = time.time()
resp = ses.request( 'GET', URL)
t_opened = time.time()

if resp.status_code == 200:
    print('success connecting')
    #print(URL)
    #print(resp.headers)
    print(resp.content.decode('utf-8'))
else:
    print(req)


URL = "https://" + HOST + "/" + TAG
values = {'j_username': T_USERNAME, 'j_password': T_PASSWORD}

t_loggingin = time.time()
t_loggedout = None
t_loggingout = None
resp = ses.request( 'POST', URL, data = values)
t_loggedin = time.time()


if resp.status_code == 200:
    lines = resp.text.split('\n')
    foundlogouturl=False
    myfaillist={}
    for line in lines:
        if 'LOGOUTURL' in line:
            foundlogouturl=True
            logouturl = line.split('"')
            logouturl = logouturl[1].strip()
            if logouturl.startswith(TARGET_URL):
                t_loggingout = time.time()
                resp = ses.request( 'GET', logouturl)
                t_loggedout = time.time()
            else:
                print("logout url doesn't match: "+ logouturl)
            if resp.status_code != 200:
                #body_unicode= resp.content.decode()
                print(resp)
                print(resp.headers)
                print(resp.text)
        if 'name="logoutExitPage"' in line:
            fragment = line[line.find('<')+1:line.rfind('>')].split(' ')
            for el in fragment:
                if '=' in el:
                    key = el[:el.find('=')]
                    value = el[el.find('=')+1:]
                    myfaillist[key] = value.replace('"','')
                print('  '+el)
    if foundlogouturl == False:
        t_loggedin = t_loggingin  + 99999
        print(myfaillist)
        print(myfaillist["value"])
        logouturl = 'https://' +HOST + '/' + TAG + myfaillist["value"]
        print('trying harder with ' + logouturl)
        t_loggingout = time.time()
        resp = ses.request( 'GET', logouturl)
        t_loggedout = time.time()
        if resp.status_code != 200:
            #body_unicode= resp.content.decode()
            print(resp)
            print(resp.headers)
            print(resp.text)

        print('Couldnt find logouturl')
        print(lines)
else:
    print(resp)
    print(resp.headers)
    print(resp.content.decode('utf-8'))

operand = "N:"
if t_opened is not None and t_opening is not None:
    operand += str(round(t_opened-t_opening,2))

operand += ":"
if t_loggedin is not None and t_loggingin is not None:
    operand += str(round(t_loggedin-t_loggingin,2))

operand += ":"
if t_loggingout is not None and t_loggedout is not None:
    operand += str(round(t_loggedout-t_loggingout,2))

operand += ":"
if t_loggingout is not None and t_opening is not None:
    operand += str(round(t_loggedout-t_opening,2))

print(operand)
rrdtool.update(MEASUREMENTS1, operand)

with open(MEASUREMENTS2,'w') as m_fd:
    m_fd.write("""{
        "topic"    : "frontend-latency",
        "tagunits" : "Phase",
        "units"    : "msec",
        "_records" : [""")
    myflag=0
    if t_opened is not None and t_opening is not None:
        m_fd.write("""{ "tag" : "target.open",
                 "measure" : """ +str(int(round(t_opened-t_opening,3)*1000)) + """
                }""")
        myflag=+1

    if t_loggedin is not None and t_loggingin is not None:
        if myflag>0:
            m_fd.write(',')
        m_fd.write("""{ "tag" : "target.loggingin",
                 "measure" : """ +str(int(round(t_loggedin-t_loggingin,3)*1000)) + """
                }""")
        myflag=+1

    if t_loggingout is not None and t_loggedout is not None:
        if myflag>0:
            m_fd.write(',')
        m_fd.write("""{ "tag" : "target.loggingout",
                 "measure" : """ +str(int(round(t_loggedout-t_loggingout,3)*1000)) + """
                }""")
        myflag=+1

    if t_loggingout is not None and t_opening is not None:
        if myflag>0:
            m_fd.write(',')
        m_fd.write("""{ "tag" : "target.total",
                 "measure" : """ +str(int(round(t_loggedout-t_opening,3)*1000)) + """
                }""")
        myflag=+1

    m_fd.write("""        ]
}""")
