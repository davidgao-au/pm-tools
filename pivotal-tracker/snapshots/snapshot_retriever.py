import os
from pathlib import Path
import json
import datetime
import requests

class SnapshotRetriever:
  def __init__(self) -> None:
    pass


  def load(self, projectId):
    if projectId is None:
      raise ValueError("projectId is required!")

    apiToken = os.environ.get("TRACER_TOKEN")
    if apiToken is None:
      raise ValueError("TRACER_TOKEN missing in environment variable!")

    urlPattern = "https://www.pivotaltracker.com/services/v5/projects/{}/history/snapshots"

    dateFormat = "%Y-%m-%d"
    endDate=datetime.datetime.today().date()
    startDate = endDate.replace(month=endDate.month - 6)

    response = requests.get(
      urlPattern.format(projectId),
      headers={"X-TrackerToken": apiToken},
      params={
        "fields": "current,backlog,icebox",
        "start_date": startDate.strftime(dateFormat),
        "end_date": endDate.strftime(dateFormat)
      }
    )

    response.raise_for_status()

    if response.status_code != 200:
      raise ValueError("Failed to load snapshots. {}".format(response.reason))

    result = response.json()


    f = open("{}/snapshots_{}_{}.json".format(Path.home(),projectId, datetime.datetime.now().strftime("%Y%m%d%H%M%S")), "w")
    f.write(json.dumps(result))
    f.close()

    return result
