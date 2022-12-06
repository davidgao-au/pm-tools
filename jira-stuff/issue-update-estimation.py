import datetime
import os
import time
import json
import logging

import jira.client
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
import dateutil.parser
from dateutil.parser import *
# from datetime import *
import requests
from typing import cast

from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
from jira.resources import Board

from utils import *

logging.basicConfig(level=logging.INFO)


class IssueFieldUpdater(JiraClient):
    JQL_BACKLOG_ISSUES = "project = {projectKey} AND type = Story ORDER BY created DESC"

    def __int__(self) -> None:
        JiraClient.__init__()
        pass

    def __extract_legacy_estimation(self, issue: Issue):
        _legacy_estimation_fields = [
            "customfield_10152",
            "customfield_10028",
            "customfield_10157",
            "customfield_10134",
            "customfield_10333"
        ]
        _story_points = None
        for cf in _legacy_estimation_fields:
            try:
                _estimation = issue.get_field(cf)
                if _estimation is not None:
                    logging.debug(f"{issue.key}: Legacy estimation is {_estimation} story points")
                    _story_points = _estimation
                    break
                # else:
                #     print(f"{issue.key}: No legacy estimation found")
            except AttributeError:
                logging.debug("%s: Field %s not found", issue.key, cf)
                continue
        if _story_points is None:
            logging.debug("%s: No legacy estimation found", issue.key)
        return _story_points

    def update_estimation(self, project_key, estimation_field_id: str):
        offset = 0
        max_results = 50

        _project = self.jira.project(project_key)
        _jql = self.JQL_BACKLOG_ISSUES.format(projectKey=_project.key)
        should_stop = False

        while not should_stop:

            # _issues = cast(ResultList[Issue], self.jira.search_issues(_jql, startAt=offset, maxResults=max_results))
            _issues = self.jira.search_issues(_jql, startAt=offset, maxResults=max_results)
            logging.info(
                f"Pagination: startAt={_issues.startAt}, maxResult={_issues.maxResults}, total={_issues.total}, isLast={_issues.isLast}")
            for s in _issues:
                _target_estimation = s.get_field(estimation_field_id)
                _legacy_story_point = self.__extract_legacy_estimation(s)
                if _target_estimation is not None:
                    logging.debug(f"{s.key}: Estimation already available")
                    continue
                elif _legacy_story_point is not None:
                    logging.info("%s: Copying value from legacy estimation: %s", s.key, _legacy_story_point)
                    self.__do_update_issue_estimation(s, estimation_field_id, _legacy_story_point)
            if not _issues.isLast:
                offset += max_results
                if offset > _issues.total:
                    should_stop = True
            else:
                should_stop = True

    def __do_update_issue_estimation(self, issue: Issue, estimation_field_id: str, new_value):
        issue.update(fields={estimation_field_id: new_value}, notify=False)


client = IssueFieldUpdater()

myBoard = client.update_estimation("IC", "customfield_10016")
# print(f"Found board id={myBoard.id}, name={myBoard.name}")
# client.getEstimationFieldFromBoard(myBoard)
# rawRecord = client.jira.find("board/{0}/configuration", 51)
