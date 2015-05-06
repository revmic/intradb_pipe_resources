#!/usr/bin/env python
from hcpxnat.interface import HcpInterface
from datetime import datetime
import envoy

# Use hcpxnat config file or assign each instance variable, e.g.,
# xnat = HcpInterface(url='http://intradb..', username='user', password='pass', project='Proj')
idb = HcpInterface(config='/data/intradb/home/hileman/.hcpxnat_intradb.cfg')
# Check resources for which pipeline?
pipeline = 'facemask'
timestamp = datetime.now().strftime("%Y%m%d")
outf = '/data/intradb/home/hileman/pipeline/log/%s_%s_%s.csv' % (idb.project, pipeline, timestamp)
print outf

SUBSET=["237334_strc", "213421_strc", "213421_fnca", "910443_diff", "156031_diff", "663755_fncb", "910443_xtra", "156031_fncb", "663755_xtra", "910443_fncb", "663755_diff", "788674_fnca", "663755_strc", "156031_strc", "910443_strc", "910443_fnca", "156031_fnca", "788674_strc", "663755_fnca", "693764_fncb", "604537_diff", "604537_fnca", "693764_diff", "618952_diff", "693764_xtra", "112314_diff", "656657_strc", "112314_xtra", "112314_fncb", "656657_fnca", "686969_diff", "686969_xtra", "196346_diff", "686969_fncb", "196346_xtra", "196346_fncb", "143426_strc", "143426_fnca", "886674_strc", "886674_fnca", "196346_strc", "686969_strc", "196346_fnca", "686969_fnca", "391748_fnca", "517239_strc", "517239_fnca", "213017_strc", "213017_fnca", "749058_diff", "308129_diff", "749058_fncb", "308129_fncb", "618952_strc", "112314_strc", "618952_fnca", "112314_fnca", "749058_strc", "308129_strc", "749058_fnca", "308129_fnca", "169949_strc", "129634_diff", "129634_fncb", "169949_fnca", "391748_strc", "173738_diff", "173738_fncb", "173839_diff", "395251_diff", "395251_fncb", "173839_fncb", "173839_xtra", "212015_diff", "212015_fncb", "212015_strc", "173839_strc", "212015_fnca", "173839_fnca", "395251_strc", "395251_fnca", "192136_diff", "192136_fncb", "192136_xtra", "766563_diff", "210112_strc", "138837_diff", "210112_fnca", "138837_fncb", "192136_strc", "604537_strc", "192136_fnca", "202719_diff", "172433_diff", "191942_diff", "202719_fncb", "172433_fncb", "191942_fncb", "202719_strc", "172433_strc"]

if __name__ == "__main__":
    sessions = idb.getSessions(idb.project)
    session_labels = list()

    for s in sessions:
        session_labels.append(s.get('label'))

    session_labels = sorted(session_labels, key=lambda s: s.split('_')[0])

    for s in session_labels:
        if s not in SUBSET:
            continue

        sub = s.split('_')[0]
        command = "python intradbPipelineResources.py -u %s -p %s -H %s -s %s -S %s -P %s -f %s -i %s" % \
                            (idb.username, idb.password, idb.url, sub, s, idb.project, outf, pipeline)
        print command
        p = envoy.run(command)
        if p.std_err:
            print p.std_err

    print "Here's yoru output:", outf
