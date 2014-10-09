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
outf = '/data/intradb/home/hileman/pipeline/log/%s_%s_%s.csv' % (idb.project, pipeline, timestamp)
print outf

SUBSET = ['111514_xtra','814649_xtra','173132_fncb','555348_fnca','127731_diff','127731_fnca','127731_fncb','127731_strc','127731_xtra','311320_strc','153732_xtra','311320_fnca','192439_xtra','204521_xtra','201515_diff','588565_fnca','555348_diff','191437_xtra','166438_xtra','201515_strc','588565_strc','201515_xtra','151526_xtra','191033_xtra','660951_xtra','568963_xtra','130316_fncb','898176_xtrb','381543_fnca','205119_xtra','175540_xtra','580650_fnca','917255_xtra','104416_diff','151425_strc','571144_diff','199251_diff','293748_xtra','571144_fncb','107018_strc','497865_fncb','151425_fnca','107018_fncb','555348_fncb','195445_strc','286650_strc','368551_fncb','286650_fncb','286650_fnca','825048_xtra','559053_xtra','100307_xtra','286650_diff','168341_xtrb','195445_fncb','158035_xtra','479762_fnca','285446_fnca','665254_xtra','187345_strc','671855_diff','107018_fnca','109123_xtra','108222_fnca','201515_fnca','135225_fncb','671855_fnca','104416_fnca','187345_fncb','195445_fnca','107018_diff','177746_xtra','187345_fnca','671855_fncb','158136_xtra','187345_diff','106521_xtrb','195445_diff','671855_strc','715950_xtrb','601127_xtra','102816_xtra','993675_fnca','195041_xtra','169444_fncb','767464_fncb','100610_xtra','255639_xtra','201515_fncb','207426_fncb','584355_strc','767464_diff','725751_xtra','820745_xtra','156334_xtra','250427_xtra','104416_strc','877168_xtra','395958_xtrb','912447_xtra','154532_strc','154532_fnca','580650_strc','183337_strc','139839_xtra','183337_fnca','140117_xtra','183337_diff','162026_xtra','104416_xtra','872764_xtra','368551_diff','555348_strc','786569_fncb','108323_xtra','182840_xtra','181232_fnca','381543_fncb','679770_diff','172029_xtra','193441_fncb','124624_fnca','679770_fncb','588565_fncb','221319_xtrb','113922_xtra','212318_xtra','381543_diff','125525_xtra','994273_fncb','381543_strc','192641_xtra','680957_xtrb','203721_fnca','588565_diff','390645_xtra','116524_xtrb','727553_fncb','433839_fnca','685058_fncb','512835_xtrb']

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
