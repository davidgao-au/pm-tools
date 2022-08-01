import datetime
from fileinput import filename
from genericpath import isdir
import io
import json
import sys
import getopt
import os.path
from os import path


from snapshot_retriever import SnapshotRetriever
from snapshots_formatter import SnapshotFormatter


def main(argv):
    inputfile = ''
    print ('Number of arguments:', len(sys.argv), 'arguments.')
    print ('Argument List:', str(sys.argv))
    print("Getting Pivotal Tracker analytical data....")
    opts, args = getopt.getopt(argv,"i:",["ifile="])

    for opt, arg in opts:
        if opt == '-i':
            inputfile = arg
            if not(path.exists(inputfile)) or path.isdir(inputfile):
                print("Invalid input file: %s" % inputfile)
                sys.exit(1)
    

    print("Input file: %s" % inputfile)

    formatter = SnapshotFormatter()

    if len(inputfile.strip()) > 1:
        print("Handling local file...")
        f = open(inputfile, "r")
        data = json.loads(f.read())
        f.close()
        formatter.format(data, "csv", os.path.basename(inputfile).replace(".json",''))
        return

    projectInfo = [
        {
            "name": "infra-cn",
            "id": 2185743
        },
        {
            "name": "ec",
            "id": 2555292
        },
        {
            "name": "gps",
            "id": 2322272
        },
        {
            "name": "sdk",
            "id": 2405917
        }
    ]

    # ts = datetime.datetime.now()
    # dateFormat = "%Y%m%d%H%M%S"
    downloader = SnapshotRetriever()

    for p in projectInfo:
        print("Downloading project snapshots for %s" % p["name"])
        data = downloader.load(p["id"])
        formatter.format(data, "csv", getFileName(p["name"]))

def getFileName(basename):
    ts = datetime.datetime.now()
    filename="tracker_snapshots_{}_{}".format( basename, ts.strftime("%Y%m%d%H%M%S"))
    return filename

main(sys.argv[1:])

print("done")
