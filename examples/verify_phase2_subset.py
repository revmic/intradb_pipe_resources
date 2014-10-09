#!/usr/bin/env python
from hcpxnat.interface import HcpInterface
from datetime import datetime
import envoy

# Use hcpxnat config file or assign each instance variable, e.g.,
# xnat = HcpInterface(url='http://intradb..', username='user', password='pass', project='Proj')
idb = HcpInterface(config='/data/intradb/home/hileman/.hcpxnat_intradb.cfg')
# Check resources for which pipeline?
pipeline = 'all'
timestamp = datetime.now().strftime("%Y%m%d")
outf = '/data/intradb/home/hileman/pipeline/log/%s_%s_%s_subset.csv' % (idb.project, pipeline, timestamp)
print outf

lst = "112516_fnca,127630_strc,173637_strc,173637_fnca,173637_diff,173637_fncb,181131_strc,346137_strc,680250_diff,680250_fncb"
session_labels = lst.split(',')
session_labels = sorted(session_labels, key=lambda s: s.split('_')[0])

if __name__ == "__main__":

    for s in session_labels:
        sub = s.split('_')[0]
        command = "python intradbPipelineResources.py -u %s -p %s -H %s -s %s -S %s -P %s -f %s -i %s" % \
                            (idb.username, idb.password, idb.url, sub, s, idb.project, outf, pipeline)
        print command
        p = envoy.run(command)
        if p.std_err:
            print p.std_err
