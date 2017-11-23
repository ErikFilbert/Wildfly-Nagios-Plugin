#!/usr/bin/env python

import sys
import socket
import json
import httplib
from base64 import b64encode
import pprint
import collections
import optparse
import socket

parameters = '?operation=resource&include-runtime=true&recursive'

myhostname=socket.gethostbyaddr(socket.gethostname())[0]
p = optparse.OptionParser(conflict_handler="resolve", description="This Nagios plugin checks the health of Wildfly.")
p.add_option('-H', '--host', action='store', type='string', dest='host', default='https://'+myhostname, help='The Wildfly Managemend URI')
p.add_option('-P', '--port', action='store', type='int', dest='port', default=9990, help='The Wildfly Management Port')
p.add_option('-u', '--user', action='store', type='string', dest='user', default=None, help='The username you want to login as')
p.add_option('-p', '--pass', action='store', type='string', dest='passwd', default=None, help='The password you want to use for that user')
p.add_option('-W', '--warning', action='store', type='int', dest='warning', default=None, help='The warning threshold we want to set')
p.add_option('-C', '--critical', action='store', type='int', dest='critical', default=None, help='The critical threshold we want to set')
p.add_option('-A', '--path', action='store', type='string', dest='path', default='/management', help='Path, e.g. /management/core-service/platform-mbean/type/threading')
p.add_option('-k', '--key', action='store', type='string', dest='key', default=None, help='Key, e.g. thread-count')

options, arguments = p.parse_args()
url = options.host+':'+str(options.port)
user = options.user
passwd = options.passwd
path = options.path
key = options.key
w = options.warning
c = options.critical

def flatten(d, parent_key='', sep='/'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

try:
    if 'https://' in url:
        url = url.replace('https://', '')
        conn = httplib.HTTPSConnection(url)
    else:
        conn = httplib.HTTPConnection(url)

    if user:
        auth = b64encode(user+":"+passwd).decode("ascii")
        headers = {'Authorization' : 'Basic %s' %  auth }
        conn.request("GET", path+parameters, "", headers)
    else:
        conn.request("GET", path+parameters)

    resp = conn.getresponse()
    body = resp.read()
    dbody = json.loads(body)

    res = flatten(dbody)[key]

    if w and c:
        if res > c:
            print 'CRITICAL - '+path+'/'+key+': '+str(res)+' | '+key+'='+str(res)+';'+str(w)+';'+str(c)
            sys.exit(2)
        elif res > w:
            print 'WARNING - '+path+'/'+key+': '+str(res)+' | '+key+'='+str(res)+';'+str(w)+';'+str(c)
            sys.exit(1)
        else:
            print 'OKAY - '+path+'/'+key+': '+str(res)+' | '+key+'='+str(res)+';'+str(w)+';'+str(c)
            sys.exit(0)
    else:
        print 'OKAY - '+path+'/'+key+': '+str(res)
        sys.exit(0)
except socket.error as (errno, strerror):
    print "I/O error({0}): {1}".format(errno, strerror)+'. Wildfly Down? | '+key+'=0;'+str(w)+';'+str(c)
    sys.exit(0)
except ValueError:
    print "UNKNOWN - Could not read JSON, status: "+str(resp.status)+" body: "+body
    sys.exit(3)
