from .settings import CACHE_MAX_AGE

try:
    from gevent import subprocess
    from gevent import sleep
except ImportError:
    import subprocess
    from time import sleep

try:
    import json
except ImportError:
    import simplejson as json

import time
import sys
import os


PYTHON_VERSION = sys.version_info[0]
CACHE = {}

def cache_load(cf):
    if not os.path.isfile(cf): return
    global CACHE
    f = open(cf, 'r')
    try: CACHE = json.load(f)
    except: pass
    f.close()

def cache_save(cf):
    global CACHE
    f = open(cf, 'w')
    json.dump(CACHE, f)
    f.close()

def do_query(dl, force=0, cache_file=None, slow_down=0, ignore_returncode=0):
    k = '.'.join(dl)
    if cache_file: cache_load(cache_file)
    if force or k not in CACHE or CACHE[k][0] < time.time() - CACHE_MAX_AGE:
        CACHE[k] = (
            int(time.time()),
            _do_whois_query(dl, ignore_returncode),
        )
        if cache_file: cache_save(cache_file)
        if slow_down: sleep(slow_down)

    return CACHE[k][1]

def _do_whois_query(dl, ignore_returncode):
    """
		Linux 'whois' command wrapper
    """
    p = subprocess.Popen(['whois', '.'.join(dl)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    r = p.communicate()[0]
    r = r.decode() if PYTHON_VERSION == 3 else r
    if not ignore_returncode and p.returncode != 0: raise Exception(r)
    return r