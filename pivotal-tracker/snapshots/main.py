import datetime
import io

from snapshot_retriever import SnapshotRetriever
from snapshots_formatter import SnapshotFormatter


def main():
    print("Getting Pivotal Tracker analytical data....")

    projectInfo = [
        {
            "name": "infra-cn",
            "id": 2185743
        },
        {
            "name": "ec",
            "id": 2555292
        }
    ]

    ts = datetime.datetime.now()
    dateFormat = "%Y%m%d%H%M%S"
    downloader = SnapshotRetriever()
    formatter = SnapshotFormatter()

    for p in projectInfo:
        print("Downloading project snapshots for %s" % p["name"])
        data = downloader.load(p["id"])
        formatter.format(data, "csv", "snapshots_{}_{}".format( p["name"], ts.strftime(dateFormat)))


main()

print("done")
