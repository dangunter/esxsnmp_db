#!/usr/bin/env python
"""
Convert ESxSNMP JSON to OpenTSDB-importable, which looks like this

# metric timestamp value tags..
met.ric 1353104545 80 host=alice
"""

import argparse
import gzip
import json
import logging
import sys

log = logging.getLogger("json2tsdb")
_hnd = logging.StreamHandler()
_hnd.setFormatter(logging.Formatter("%(name)s [%(levelname)s] %(message)s"))
log.addHandler(_hnd)
log.setLevel(logging.WARN)

class ConvertError(Exception): pass

def convert(ifile, ofile, offs):
    "Convert JSON `ifile` to metrics `ofile`. `i`th time."
    try:
        js = json.load(ifile)
    except ValueError, err:
        raise ConvertError("In file '{}': {}".format(ifile.name, err))
    min_ts, max_ts = sys.maxint, -1
    for oid_set in js:
        device = oid_set['device_name']
        ts = oid_set['timestamp'] + offs
        metric = 'snmp.' + oid_set['oid_name']
        for metric_port, value in oid_set['data']:
            port = metric_port.split('/')[1]
            base_rec = ("{metric} {timestamp:d} {value} dev={device} port={port}\n"
                        .format(metric=metric, timestamp=int(ts), value=value,
                                device=device, port=port))
            ofile.write(base_rec)
        min_ts = min(min_ts, ts)
        max_ts = max(max_ts, ts)
    return (min_ts, max_ts)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", dest="ifile", default="-", help="Input file (default=STDIN)")
    ap.add_argument("-n", dest="num", type=int, help="Number of copies of data", default=1)
    ap.add_argument("-o", dest="ofile", default="-", help="Output file (default=STDOUT)")
    ap.add_argument("-v", dest="vb", action="count", default=0, help="Increase verbosity")
    ap.add_argument("-z", dest="zip", action="store_true")
    args = ap.parse_args()
    if args.ofile == "-":
        ofile = sys.stdout
    else:
        ofile = open(args.ofile, "wb")
    if args.zip:
        ofile = gzip.GzipFile(fileobj=ofile)
    if args.vb > 1:
        log.setLevel(logging.DEBUG)
    elif args.vb > 0:
        log.setLevel(logging.INFO)

    offs = 0
    for i in xrange(args.num):
        if args.ifile == "-":
            ifile = sys.stdin
        else:
            ifile = open(args.ifile, "rb")
        try:
            min_ts, max_ts = convert(ifile, ofile, offs)
            log.info("timestamp min={} max={}".format(min_ts, max_ts))
            offs += max_ts - min_ts + 1
        except ConvertError, err:
            log.warn("Conversion error: {}".format(err))
            return -1
    return 0

if __name__ == "__main__":
    sys.exit(main())