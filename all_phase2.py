#!/usr/bin/env python
from hcpxnat.interface import HcpInterface
import envoy

idb = HcpInterface(config='/home/NRG/mhilem01/.hcpxnat_intradb.cfg')
outf = '/home/NRG/mhilem01/temp/hcp_phase2_resources.csv'

if __name__ == "__main__":
    sessions = idb.getSessions(idb.project)
    session_labels = list()

    for s in sessions:
        session_labels.append(s.get('label'))

    session_labels = sorted(session_labels, key=lambda s: s.split('_')[0])

    for s in session_labels:
        sub = s.split('_')[0]
        command = "python intradbPipelineResources.py -u %s -p %s -H %s -s %s -S %s -P %s -f %s -i all" % \
                            (idb.username, idb.password, idb.url, sub, s, idb.project, outf)
        print command
        p = envoy.run(command)
        if p.std_err:
            print p.std_err
