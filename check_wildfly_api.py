#!/usr/bin/env python

#       Copyright (C) 2017 Erik Filbert
#       Site: github.com/ErikFilbert
#
#       This program is free software; you can redistribute it and/or
#       modify it under the terms of the GNU General Public License
#       as published by the Free Software Foundation; either version 2
#       of the License, or (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import sys
import socket
import json
import httplib
from base64 import b64encode
import pprint
import collections
import optparse
import socket
import re

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
p.add_option('-s', '--string', action='store', type='string', dest='matchString', default=None, help='Output should match to string')

options, arguments = p.parse_args()
url = options.host+':'+str(options.port)
user = options.user
passwd = options.passwd
path = options.path
key = options.key
w = options.warning
c = options.critical
matchString = options.matchString

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
    if resp.status == 200:
        dbody = json.loads(body)

        if matchString:
            rx = re.compile(key)
            for k,v in flatten(dbody).iteritems():
                if rx.match(k):
                    key = k
                    res = str(v)
        else:
            res = int(flatten(dbody)[key])
    else:
	    print('UNKNOWN - %s/%s: Response not 200: Status: %i, Body: %s' % (path,key,resp.status,body))
	    sys.exit(3)

    if w and c:
        if res > c:
            print ('CRITICAL - %s/%s: %i | %s=%i;%i;%i' % (path,key,res,key,res,w,c))
            sys.exit(2)
        elif res > w:
            print ('WARNING - %s/%s: %i | %s=%i;%i;%i' % (path,key,res,key,res,w,c))
            sys.exit(1)
        else:
            print ('OKAY - %s/%s: %i | %s=%i;%i;%i' % (path,key,res,key,res,w,c))
            sys.exit(0)
    elif matchString:
        if res == matchString:
            print ('OKAY - %s/%s: %s | %s=1' % (path,key,res,key))
            sys.exit(0)
        else:
            print ('CRITICAL - %s/%s: %s | %s=1' % (path,key,res,key))
            sys.exit(1)
    else:
        print ('OKAY - '+path+'/'+key+': '+str(res))
        sys.exit(0)
    
except socket.error as (errno, strerror):
    print ('I/O error(%s): %s . Wildfly Down? | %s=0;%s;%s' % (errno,strerror,key,str(w),str(c)))
    sys.exit(0)
except ValueError as (ex):
    print ('UNKNOWN - Could not read JSON, status: %i body: %s\nCause: %s' % (resp.status,body,ex))
    sys.exit(3)
