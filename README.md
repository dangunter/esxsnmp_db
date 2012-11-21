# ESxSNMP DB

For [ESNet SNMP](http://code.google.com/p/esxsnmp/) database backend.

## Files

* data/ - Input data
    - router_a_ifhcin_long.json - Sample JSON data (8K points, 1 device)
* opentsdb/ - experiments with [OpenTSDB](http://opentsdb.net)
    - json2tsdb.py - Convert ESNet SNMP JSON into something importable by OpenTSDB