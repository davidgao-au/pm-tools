import json
import io
from operator import le
from pathlib import Path
from posixpath import split
import re

class SnapshotFormatter:
  def __init__(self) -> None:
    pass

  def format(self, data, type="json", filename=None):
    print("%d records in the data. type: %s" % (len(data), type))
    result = []
    acceptedStories=set()
    unfinishedStories=set()

    for i in data:
      recordInfo = self.__formatItem(i,acceptedStories, unfinishedStories)
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
        print("Date, Finished, Unfinished", file=output)
        for r in result:
          # print("%s,%d,%d,%d,%d,%d,%d" % (r["date"], r["current"]["count"], r["current"]["points"], r["backlog"]["count"], r["backlog"]["points"], r["icebox"]["count"], r["icebox"]["points"]), file=output)
          print("%s,%d,%d" % (r["date"], r["done"], r["unfinished"]), file=output)
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


  def __formatItem(self, record,acceptedStories, unfinishedStories):
    snapshotInfo = {
      "date": "",
      "done": 0,
      "unfinished": 0
    }

   

    snapshotInfo["date"] = record["date"]
    splitCurrent = self.__splitCurrent(record["current"], acceptedStories, unfinishedStories)
    self.__cumulativeCount(record["backlog"], unfinishedStories)
    self.__cumulativeCount(record["icebox"], unfinishedStories)
    snapshotInfo["done"] = splitCurrent["done"]
    snapshotInfo["unfinished"] = splitCurrent["unfinished"] + len(unfinishedStories)
    # print("%s - %d accepted vs %d unfinished" % (record["date"],len(acceptedStories), len(unfinishedStories)))
    return snapshotInfo


  def __splitCurrent(self,currentStories, acceptedStories, unfinishedStories):
    splitCurrent = {
      "done": 0,
      "unfinished": 0
    }

    doneStates=["accepted"]

    for s in currentStories:
      state = s["state"]
      if state in doneStates:
        acceptedStories.add(s["story_id"])
      else:
        unfinishedStories.add(s["story_id"])
    
    splitCurrent["done"]=len(acceptedStories)
    splitCurrent["unfinished"]=len(unfinishedStories)
    return splitCurrent


  def __cumulativeCount(self, input, storiesSet):
    for i in input:
      storiesSet.add(i["story_id"])

    return len(storiesSet)

  def __loadFinishedStories(self, input, finishedStories):
    finished_states = ["accepted"]
    s = {
      "id": 0,
      "points": 0
    }
    for i in input:
      state = i["state"]
      if state in finished_states:
        finished_states.add(i["story_id"])


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


# jsonPath = "/Users/david/snapshots_2555292_20220801190921.json"
# f = open(jsonPath,"r")
# data = json.loads(f.read())

# fmt = SnapshotFormatter()
# fmt.format(data)