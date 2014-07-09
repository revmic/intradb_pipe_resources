from hcpxnat.interface import HcpInterface
from optparse import OptionParser
import time
import sys


"""
Checks for the existence of intradb pipeline resources.
Used as part of the Sanity Check suite.
"""
__author__ = "Michael Hileman"
__email__ = "hilemanm@mir.wuslt.edu"
__version__ = "0.8.2"

parser = OptionParser(usage='\npython intradbPipelineResources.py -u user -p pass ' +
            '-H hostname -s 100307 -S 100307_strc -P HCP_Phase2 -i all\n' +
            'Cutoff Date Usage:\npython intradbPipelineResources.py -u user -p pass ' +
            '-H hostname -P HCP_Phase2 -d 20131210')
parser.add_option("-u", "--username", action="store", type="string", dest="username")
parser.add_option("-p", "--password", action="store", type="string", dest="password")
parser.add_option("-H", "--hostname", action="store", type="string", dest="hostname")
parser.add_option("-s", "--subject", action="store", type="string", dest="subject")
parser.add_option("-S", "--session", action="store", type="string", dest="session")
parser.add_option("-P", "--project", action="store", type="string", dest="project")
parser.add_option("-f", "--csv-file", action="store", type="string", dest="csv")
parser.add_option("-i", "--pipeline", action="store", type="string", dest="pipeline",
    help='validation, facemask, dcm2nii, level2qc, or all')
parser.add_option("-d", "--cutoff-date", action="store", type="string", dest="cutoff",
    help="Check sessions back to a given date (format=YYYYDDMM)")
(opts, args) = parser.parse_args()


if not opts.username:
    parser.print_help()
    sys.exit(-1)

if opts.csv:
    try:
        csv_file = open(opts.csv, 'a')
    except:
        print "Problem with file " + opts.csv
        exit(-1)

idb = HcpInterface(opts.hostname, opts.username, opts.password, opts.project)
idb.subject_label = opts.subject


idb.session_label = opts.session

deface_types = ('Bias_Transmit', 'Bias_Receive', 'T1w', 'T2w')


def verifyValidation():
    """
    Checks for ProtocolVal at the experiment level.
    """
    print "--Verifying Validation"
    uri = '/REST/experiments?xsiType=val:protocolData&project=%s&session_label=%s' % \
        (idb.project, idb.session_label)
    validation = idb.getJson(uri)
    
    if validation:
        msg = "ProtocolVal resource exists"
        status = True
    else:
        msg = "ProtocolVal resource missing"
        status = False
    print msg

    writeCsv('', 'protocolVal', 'Protocol Validation', status, msg)
    return status


def verifyFacemask():
    """
    Checks for DICOM_DEFACE resource and also NIFTI_RAW (if NIFTI exists)
    for appropriate scan types: Bias_Receive, Bias_Transmit, T1w, and T2w
    """
    print "--Verifying Facemask"
    resource_dict = {}

    uri = '/REST/projects/%s/subjects/%s/experiments/%s/scans/*/resources' % \
        (idb.project, idb.subject_label, idb.session_label)
    resources = idb.getJson(uri)

    # Build resources dictionary
    for r in resources:
        scan_type = r.get('cat_desc')
        scan_id = r.get('cat_id')
        resource_label = r.get('label')

        if scan_type in deface_types:
            if scan_id not in resource_dict:
                resource_dict[scan_id] = []
            resource_dict[scan_id].append(resource_label)

    for scanid, value in resource_dict.iteritems():
        status = True
        msg = 'pass'

        if 'DICOM_DEFACED' not in resource_dict[scanid]:
            msg = "Missing DICOM_DEFACED. Run Facemask."
            status = False
        if 'NIFTI' in resource_dict[scanid] and 'NIFTI_RAW' not in resource_dict[scanid]:
            msg = "Has NIFTI but is missing NIFTI_RAW resource"
            status = False

        lname = 'Verify facemask resources'
        writeCsv(scanid, 'facemask', lname, status, msg)


def verifyNifti():
    """
    Every scan should have NIFTI, and if facemask scan type,
    there should be NIFTI_RAW and NIFTI should be newer than DICOM_DEFACED
    """
    
print "--Verifying DicomToNifti"

    # Collect all scan resources into dictionary
    resource_dict = {}
    uri = '/REST/projects/%s/subjects/%s/experiments/%s/scans/*/resources' % \
        (idb.project, idb.subject_label, idb.session_label)
    resources = idb.getJson(uri)

    for r in resources:
        scan_type = r.get('cat_desc')
        scan_id = r.get('cat_id')

        if scan_id not in resource_dict:
            resource_dict[scan_id] = {"type": scan_type, "resources": []}
        resource_dict[scan_id]["resources"].append(r.get('label'))

    for scanid, value in resource_dict.iteritems():
        status = True
        msg = 'pass'
        
        nii_uri = '/REST/projects/%s/subjects/%s/experiments/%s/scans/%s/resources/NIFTI/files' % \
                   (idb.project, idb.subject_label, idb.session_label, scanid)
        dcm_uri = '/REST/projects/%s/subjects/%s/experiments/%s/scans/%s/resources/DICOM/files' % \
                   (idb.project, idb.subject_label, idb.session_label, scanid)

        # Check that all have NIFTI
        if 'NIFTI' not in resource_dict[scanid]["resources"]:
            msg = "Missing NIFTI resource. Run dcm2nii."
            print msg
            status = False
        writeCsv(scanid, 'dcm2nii', 'Dicom to Nifti conversion', status, msg)

        if status == False:
            continue
            # Skip following checks since resource doesn't exist for comparison

        if resource_dict[scanid]["type"] in deface_types:
            # We want to check against the defaced Dicoms in this case
            dcm_uri = '/REST/projects/%s/subjects/%s/experiments/%s/scans/%s/resources/DICOM_DEFACED/files' % \
                       (idb.project, idb.subject_label, idb.session_label, scanid)

            # Check for NIFTI_RAW
            if 'NIFTI_RAW' not in resource_dict[scanid]["resources"]:
                msg = "Defaced scan (" + scanid + ") is missing NIFTI_RAW resource"
                print msg
                writeCsv(scanid, 'dcm2nii', 'Dicom to Nifti', False, msg)
                continue

        # Check that NIFTI files are newer than DICOM
        nifti_files = idb.getJson(nii_uri)
        dicom_files = idb.getJson(dcm_uri)

        try:
            dt = idb.getHeaderField(nifti_files[0].get('URI'), 'Last-Modified')
            nii_date = time.strptime(dt, "%a, %d %b %Y %H:%M:%S %Z")
            dt = idb.getHeaderField(dicom_files[0].get('URI'), 'Last-Modified')
            dcm_date = time.strptime(dt, "%a, %d %b %Y %H:%M:%S %Z")
        except IndexError:
            msg = "Cannot check dates for DICOM and NIFTI - one or both resources do not exist"
            print msg
            writeCsv(scanid, 'dcm2nii', 'Dicom to Nifti', False, msg)
            continue

        if nii_date < dcm_date:
            msg = "NIFTI resource is older than DICOM"
            print msg
            status = False

        writeCsv(scanid, 'dcm2nii', 'Dicom to Nifti', status, msg)


def verifyQC():
    """
    Verifies existence of QC Assessment for BOLD, DWI, T1w, and T2w
    """
    print "--Verifying Level2QC"
    # Get all the scans and their types
    uri = '/REST/projects/%s/subjects/%s/experiments/%s/scans' % \
        (idb.project, idb.subject_label, idb.session_label)
    scans = idb.getJson(uri)
    has_qc = list()
    needs_qc = list()

    # Collect which scans have QC into a list based on assessement name
    uri = '/REST/experiments?xsiType=xnat:qcAssessmentData&project=%s&session_label=%s' % \
        (idb.project, idb.session_label)
    qc_assessments = idb.getJson(uri)

    for qc in qc_assessments:
        qc_label = qc.get('label').split('_')
        # Get scan number from scan portion of qc label
        for part in qc_label:
            if 'SCAN' in part:
                has_qc.append(part[4:])  # Based on file name - Might be too fragile

    # Check that each scan that should has an assessment
    for scan in scans:
        sd = scan.get('series_description').lower()
        if (sd.startswith('bold') or sd.startswith('dwi') or sd.startswith('t1w') or sd.startswith('t2w')) \
            and not (sd.endswith('sbref') or sd.endswith('sbref_old') or sd.endswith('se')
                     or sd.endswith('se_old') or sd.endswith('meg')):
            needs_qc.append(scan.get('ID'))

    for s in needs_qc:
        if s not in has_qc:
            msg = "Missing Level 2 QC"
            print msg
            status = False
        else:
            msg = 'pass'
            status = True

        writeCsv(s, 'level2qc', 'Level 2 QC', status, msg)


def verifyAll():
    verifyValidation()
    verifyFacemask()
    verifyNifti()
    verifyQC()


def writeCsv(scan_num, check_sname, check_lname, success, desc):
    if not opts.csv:
        return
    if scan_num:
        idb.scan_id = scan_num
        series_desc = idb.getScanXmlElement('xnat:series_description')
    else:
        series_desc = ""

    if success:
        lst = [idb.session_label, scan_num, series_desc, check_sname, check_lname, 'PASS', '']
    else:
        lst = [idb.session_label, scan_num, series_desc, check_sname, check_lname, 'FAIL', desc]
    row = ",".join(lst)
    csv_file.write(row + '\n')


def getSessionsByDate(cutoff):
    return ['100307_fnca', '100408_fncb']


if __name__ == '__main__':
    print "Verifying %s on %s for project %s" % (opts.pipeline, idb.url, idb.project)
    print "Subject: %s - Session: %s" % (idb.subject_label, idb.session_label)

    """ TODO
    if opts.cutoff:
        session_list = getSessionsByDate(opts.cutoff)
        for s in session_list:
            idb.session_label = s
            idb.subject_label = s.split('_')
            verifyAll()
        sys.exit(0)
    """

    if opts.pipeline == "all":
        verifyAll()
    elif opts.pipeline == "validation":
        verifyValidation()
    elif opts.pipeline == "facemask":
        verifyFacemask()
    elif opts.pipeline == "dcm2nii":
        verifyNifti()
    elif opts.pipeline == "level2qc":
        verifyQC()
