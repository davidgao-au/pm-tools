import json
import io
from pathlib import Path
from posixpath import split
import re

class SnapshotFormatter:
  def __init__(self) -> None:
    pass

  def format(self, data, type="json", filename=None):
    print("%d records in the data. type: %s" % (len(data), type))
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
        print("Date,Working Stories,Working Points,backlog-stories,backlog-points,icebox-stories,icebox-points,To-Do Stories,To-Do Points", file=output)
        for r in result:
          working = r["working"]
          backlog = r["backlog"]
          icebox = r["icebox"]
          todoCount = backlog["count"]+icebox["count"]
          todoPoints=backlog["points"] + icebox["points"]
          print("%s,%d,%d,%d,%d,%d,%d,%d,%d" % (r["date"], working["count"], working["points"], backlog["count"], backlog["points"], icebox["count"], icebox["points"], todoCount,todoPoints), file=output)
    else:
      print(json.dumps(result), file=output)

    if filename is not None:
      fileBasename = filename

    outputFile = "{}/data/{}.{}".format(Path.home(),fileBasename, extension)
    print("Output file: %s" % outputFile)
    f = open(outputFile, "w")
    f.write(output.getvalue())
    f.close()
    output.close()


  def __formatItem(self, record):
    snapshotInfo = {
      "date": "",
      "working": {},
      "backlog": {},
      "icebox": {}
    }
    snapshotInfo["date"] = record["date"]
    splitCurrent = self.__splitCurrent(record["current"])


    snapshotInfo["working"] = splitCurrent["working"]
    snapshotInfo["backlog"] = self.__getAnalytics(record["backlog"])
    snapshotInfo["backlog"]["count"] += splitCurrent["backlog"]["count"]
    snapshotInfo["backlog"]["points"] += splitCurrent["backlog"]["points"]

    snapshotInfo["icebox"] = self.__getAnalytics(record["icebox"])
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

  def __splitCurrent(self,currentStories):
    splitCurrent = {
      "working": {},
      "backlog": {}
    }
    working = {
      "count": 0,
      "points": 0
    }
    backlog = {
      "count": 0,
      "points": 0
    }

    workingState=["started","finished","delivered"]

    for s in currentStories:
      state = s["state"]
      if state in workingState:
        working["count"] +=1
        working["points"] += s.get("estimate",0)
      else:
        backlog["count"]+=1
        backlog["points"]+= s.get("estimate",0)
    
    splitCurrent["working"]=working
    splitCurrent["backlog"]=backlog
    return splitCurrent