# scan.target.py
The purpose of scan.target is to scan a Maximo target using Python3, Selenium and Chrome to produce a json measurement file for a timeseries database such as influxdb or equivalent.

## Expected result
```
{'topic': 'frontend-latency', 'tagunits': 'Phase', 'units': 'msec', '_records': [{'tag': 'rod-emms-vpn.open', 'measure': '856'}, {'tag': 'rod-emms-vpn.loggingin', 'measure': '1568'}, {'tag': 'rod-emms-vpn.loggingout', 'measure': '633'}, {'tag': 'rod-emms-vpn.total', 'measure': '3099'}]}
```
