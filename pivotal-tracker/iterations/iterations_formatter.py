import json
import io
from pathlib import Path

class IterationFormatter:
  def __init__(self) -> None:
    pass

  def format(self, data, filename=None):
    print("%d records in the data" % (len(data)))
    result = []
    for i in data:
      iterationData = self.__formatItem(i)
      result.append(iterationData)

    output = io.StringIO()
    fileBasename = "output"
    print("Iteration,Stories,Points,Start,Finish", file=output)
    for r in result:
        print("%s,%d,%d,%d,%d,%d,%d" % (r["number"], r["stories"]["count"], r["stories"]["points"], r["start"], r["finish"]), file=output)

    if filename is not None:
      fileBasename = filename

    f = open("{}/{}.csv".format(Path.home(),fileBasename), "w")
    f.write(output.getvalue())
    f.close()
    output.close()


  def __formatItem(self, record):
    iterationInfo = {
      "number": "",
      "stories": {},
      "start": "",
      "finish": ""
    }
    iterationInfo["number"] = record["number"]
    iterationInfo["stories"] = self.__getAnalytics(record["stories"])
    iterationInfo['start'] = record["start"]
    iterationInfo['finish'] = record["finish"]
    return iterationInfo


  def __getAnalytics(self,stories):
    info = {
      "count": 0,
      "points": 0
    }

    if len(stories) < 1:
      return info
    
    info["count"]=len(stories)
    points=0
    for c in stories:
      points +=c.get("estimate",0)
    info["points"] = points
    return info



formatter = IterationFormatter()