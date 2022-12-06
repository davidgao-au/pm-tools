import datetime
import os
import time
import json

import jira.client
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
import dateutil.parser
from dateutil.parser import *
# from datetime import *
import requests

from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue

from utils import *

# def create_session():
#     email = os.environ.get('JIRA_USER_NAME')
#     api_token = os.environ.get('JIRA_API_TOKEN')
#
#     if not email:
#         print("Missing Jira user name!")
#         exit(1)
#     else:
#         print("Using JIRA user name: ", email)
#
#     if not api_token:
#         print("Missing Jira API token")
#         exit(1)
#     return JIRA(
#         server="https://autonomic-ai.atlassian.net",
#         basic_auth=(email, api_token)
#     )
#


class SprintUpdater:
    def __init__(self) -> None:
        self.jira = create_session()

    def list_boards(self):
        boards = self.jira.boards()
        for b in boards:
            print(f"JIRA board: {b.name} ({b.id})")

    def list_sprints(self, board_id, start_at: int = 0, max_results: int = 50):
        _sprints = self.jira.sprints(board_id=board_id, startAt=start_at, maxResults=max_results)
        print(
            f"{len(_sprints)} sprints loaded. total={_sprints.total}, startAt={_sprints.startAt}, last={_sprints.isLast}")
        return _sprints

    def start_sprint(self, _sprint_id):
        _sprint = self.jira.sprint(_sprint_id)
        state = _sprint.state
        if "future" == state:
            print(f"Starting sprint {_sprint.name}, startDate={_sprint.startDate}...")
            _sprint.update(fields={
                "id": _sprint_id,
                "name": _sprint.name,
                "startDate": _sprint.startDate,
                "endDate": _sprint.endDate,
                "state": "active"
            },
                async_=False,
                notify=False)
            # self.jira.update_sprint(_sprint_id, _sprint.name, _sprint.startDate, _sprint.endDate, "active")

    def finish_sprint(self, _sprint):
        state = _sprint.state
        if "closed" == state or "future" == state:
            return

        _sprint_issues = self.jira.search_issues(f"sprint = {_sprint.id} and type NOT IN (Subtask, Sub-task) ORDER BY "
                                                 f"created DESC", maxResults=200)
        _count = len(_sprint_issues)
        _done_issues = 0
        for i in _sprint_issues:
            _issue_id = i.id
            _issue_status = i.get_field("status")
            # print(f"{_sprint.id} Issue {_issue_id} status: {_issue_status.name} ({_issue_status.statusCategory.key})")
            if "done" == _issue_status.statusCategory.key:
                _done_issues += 1

        # print(f"{_sprint.name} has {_done_issues} done issues!")
        if _count == _done_issues:
            print(f"All issues are done! Completing sprint {_sprint.name}...")
            # _sprint.update(fields={"state": "closed"})
            self.jira.update_sprint(_sprint.id, _sprint.name, _sprint.startDate, _sprint.endDate, "closed")
        else:
            print(f"Detected {_count - _done_issues} remaining issues in sprint {_sprint.name}")

    def __reset_session(self):
        self.jira.kill_session()

    def closeOverdueSprints(self, jira_board_id, cutoff_date: datetime.datetime):
        offset = 0
        max_results = 50
        should_stop = False
        while not should_stop:
            sprints = self.list_sprints(jira_board_id, offset, max_results)
            for s in sprints:
                # print(f"sprint {s.id}-{s.name}")
                has_date_info = s.raw.__contains__('startDate')
                if has_date_info:
                    start_date = dateutil.parser.isoparse(s.startDate)
                    if start_date < cutoff_date:
                        print(f"Checking sprint {s.name} (id:{s.id}, state:{s.state}, start date: {start_date.date()})")
                        self.start_sprint(s.id)
                        self.finish_sprint(s)
                    else:
                        print(f"future sprint {s.id}-{s.name} start date: {start_date.date()}")
                else:
                    print(f"sprint {s.id}-{s.name}: No date info")

            if not sprints.isLast:
                offset += max_results
            else:
                should_stop = True


end_date = dateutil.parser.isoparse("2022-11-28T00:00:00.000Z")
updater = SprintUpdater()
updater.closeOverdueSprints(jira_board_id=51, cutoff_date=end_date)
