import json
import io
from pathlib import Path

class SnapshotFormatter:
  def __init__(self) -> None:
    pass

  def format(self, data, type="json", filename=None):
    print("%d records in the data. type: " % len(data))
    result = []
    for i in data:
      recordInfo = self.__formatItem(i)
      result.append(recordInfo)

    output = io.StringIO()
    fileBasename = "output"
    extension = "json"
    if type is not None:
      fmt = type.strip()
      if fmt.casefold() == "json":
        print(json.dumps(result), file=output)
      elif fmt.casefold() == "csv":
        extension = "csv"
        print("Date,Current - Stories,Current-Points,backlog-stories,backlog-points,icebox-stories,icebox-stories", file=output)
        for r in result:
          print("%s,%d,%d,%d,%d,%d,%d" % (r["date"], r["current"]["count"], r["current"]["points"], r["backlog"]["count"], r["backlog"]["points"], r["icebox"]["count"], r["icebox"]["points"]), file=output)
    else:
      print(json.dumps(result), file=output)

    if filename is not None:
      fileBasename = filename

    f = open("{}/{}.{}".format(Path.home(),fileBasename, extension), "w")
    f.write(output.getvalue())
    f.close()
    output.close()


  def __formatItem(self, record):
    snapshotInfo = {
      "date": "",
      "current": {},
      "backlog": {},
      "icebox": {}
    }
    snapshotInfo["date"] = record["date"]
    snapshotInfo["current"] = self.__getAnalytics(record["current"])
    snapshotInfo["backlog"] = self.__getAnalytics(record["backlog"])
    snapshotInfo["icebox"] = self.__getAnalytics(record["icebox"])
    # print(json.dumps(snapshotInfo))
    # print("="*80)
    return snapshotInfo


  def __getAnalytics(self,storySnapshots):
    info = {
      "count": 0,
      "points": 0
    }

    if len(storySnapshots) < 1:
      return info
    
    info["count"]=len(storySnapshots)
    points=0
    for c in storySnapshots:
      points +=c.get("estimate",0)
    info["points"] = points

    return info

