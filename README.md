Usage: check_wildfly_api.py [options]

This Nagios plugin checks the health of Wildfly.

```
Options:
  -h, --help            show this help message and exit
  -H HOST, --host=HOST  The Wildfly Managemend URI
  -P PORT, --port=PORT  The Wildfly Management Port
  -u USER, --user=USER  The username you want to login as
  -p PASSWD, --pass=PASSWD
                        The password you want to use for that user
  -W WARNING, --warning=WARNING
                        The warning threshold we want to set
  -C CRITICAL, --critical=CRITICAL
                        The critical threshold we want to set
  -A PATH, --path=PATH  Path, e.g. /management/core-service/platform-
                        mbean/type/threading
  -k KEY, --key=KEY     Key, e.g. thread-count
```
