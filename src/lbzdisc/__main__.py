import sys 
from lbzdisc import DEFAULT
import importlib.metadata
from pprint import pprint

try: 
    if sys.argv[0] in ("--version", "-v", "version"): 
        ver = importlib.metadata.version('listenbrainz-disc')
        print(f'Version {ver}')
    if sys.argv[0] in ("--defaults", "defaults"): 
        pprint(DEFAULT)
except IndexError: 
    pass
