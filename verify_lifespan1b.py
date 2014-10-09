#!/usr/bin/env python
from hcpxnat.interface import HcpInterface
from datetime import datetime
import envoy

# Use hcpxnat config file or assign each instance variable, e.g.,
# xnat = HcpInterface(url='http://intradb..', username='user', password='pass', project='Proj')
idb = HcpInterface(config='/data/intradb/home/hileman/.hcpxnat_intradb.cfg')
idb.project = 'LS_Phase1b'
##pipeline = 'dcm2nii'
pipeline = 'all'
timestamp = datetime.now().strftime("%Y%m%d")
outf = '/data/intradb/home/hileman/pipeline/log/%s_%s_%s.csv' % (idb.project, pipeline, timestamp)
##SUBSET = ['LS6135_V1_A', 'LS3029_V1_A']
##SUBSET = ['LS6135_V1_A']

if __name__ == "__main__":
    sessions = idb.getSessions(idb.project)
    session_labels = list()

    for s in sessions:
        session_labels.append(s.get('label'))

    session_labels = sorted(session_labels, key=lambda s: s.split('_')[0])

    for s in session_labels:
        sub = s.split('_')[0]
        
        ##if s not in SUBSET:
        ##    continue

        command = "python intradbPipelineResources.py -u %s -p %s -H %s -s %s -S %s -P %s -f %s -i %s" % \
                  (idb.username, idb.password, idb.url, sub, s, idb.project, outf, pipeline)
        print command
        p = envoy.run(command)
        if p.std_err:
            print p.std_err

    print "\nHere's your csv:\n", outf
