intradb_pipe_resources
======================

Scan Intradb for missing or erroneous pipeline resources.

Prerequisites:
python
requests module
envoy module
 (on NRG cluster, source /nrgpackages/scripts/epd-python_setup.sh)
hcpxnat (see Installation)

Installation:
./install.sh

Usage:

python intradbPipelineResources.py -u user -p pass -H hostname -s 100307 -S 100307_strc -P HCP_Phase2 -i all
Cutoff Date Usage:
python intradbPipelineResources.py -u user -p pass -H hostname -P HCP_Phase2 -d 20131210

Options:
  -h, --help   show this help message and exit
  -u USERNAME, --username=USERNAME
  -p PASSWORD, --password=PASSWORD
  -H HOSTNAME, --hostname=HOSTNAME
  -s SUBJECT,  --subject=SUBJECT
  -S SESSION,  --session=SESSION
  -P PROJECT,  --project=PROJECT
  -f CSV,      --csv-file=CSV
  -i PIPELINE, --pipeline=PIPELINE
                validation, facemask, dcm2nii, level2qc, or all
  -d CUTOFF,   --cutoff-date=CUTOFF
                Check sessions back to a given date (format=YYYYDDMM)
