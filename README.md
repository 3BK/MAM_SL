# measure_target.2.0.py
Expected result

## Failure
```
$ ./measure_target.2.0.py
Login Error
The LTPA token that is used to login is invalid. LTPA tokens are used for the login process when WebSphere Application Server Security is enabled. Wait a few seconds and then try again to log in. If the problem persists, clear your browser cookies or restart the browser.
Return
```

## Success
```
$ measure_target.2.0.py
open (0.5806760787963867); login (1.434309482574463); logout (0.6135632991790771); total (2.680819034576416)
```
