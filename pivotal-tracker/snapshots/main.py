import datetime
import io

from snapshot_retriever import SnapshotRetriever
from snapshots_formatter import SnapshotFormatter

def main():
    print("Getting Pivotal Tracker analytical data....")

    projectInfo = {
        "infra-cn": 2185743,
        "ec": 2555292
    }
    ts=datetime.datetime.now()
    downloader = SnapshotRetriever()
    formatter = SnapshotFormatter()

    
    dateFormat = "%Y%m%d%H%M%S"
    
    print("Downloading Infra-cn project snapshots")
    data = downloader.load(projectInfo["infra-cn"])
    formatter.format(data, "csv", "snapshots_{}_{}".format("infra-cn",ts.strftime(dateFormat)))

    print("Downloading snapshots for EC")
    data = downloader.load(projectInfo["ec"])
    formatter.format(data, "csv", "snapshots_{}_{}".format("ec",ts.strftime(dateFormat)))
    
    

main()

print("done")