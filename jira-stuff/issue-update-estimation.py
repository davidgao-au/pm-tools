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

    ISSUE_ESTIMATION_FIELD_ID="customfield_10016"

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

    def update_estimation(self, project_key):
        _jql = self.JQL_BACKLOG_ISSUES.format(projectKey=project_key)
        self.__update_issues(project_key, _jql, self.__do_update_issue_estimation)


    def close_reviews(self, project_key):
        _jql = f"Project = {project_key} AND type = Review AND status != pass ORDER BY created DESC"
        self.__update_issues(project_key, _jql, self.__do_close_review)

    def __update_issues(self, project_key: str, jql: str, callback):
        offset = 0
        max_results = 50
        should_stop = False

        _project = self.jira.project(project_key)

        while not should_stop:
            _issues = self.jira.search_issues(jql, startAt=offset, maxResults=max_results)
            logging.info(
                f"Pagination: startAt={_issues.startAt}, maxResult={_issues.maxResults}, total={_issues.total}, isLast={_issues.isLast}")
            for s in _issues:
                callback(s)
            if not _issues.isLast:
                offset += max_results
                if offset > _issues.total:
                    should_stop = True
            else:
                should_stop = True

    def __do_update_issue_estimation(self, issue: Issue):
        _target_estimation = issue.get_field(self.ISSUE_ESTIMATION_FIELD_ID)
        _legacy_story_point = self.__extract_legacy_estimation(issue)
        if _target_estimation is not None:
            logging.debug(f"{issue.key}: Estimation already available")
            return
        elif _legacy_story_point is not None:
            logging.info("%s: Copying value from legacy estimation: %s", issue.key, _legacy_story_point)
            issue.update(fields={self.ISSUE_ESTIMATION_FIELD_ID: _legacy_story_point}, notify=False)


    def __do_close_review(self, issue: Issue):
        try:
            _issue_links = issue.get_field("issuelinks")
            for _link in _issue_links:
                _outward_issue = _link.outwardIssue
                _o_status = _outward_issue.fields.status.statusCategory.key
                if "done" == _o_status:
                    logging.info(f"{issue.key} --> {_outward_issue.key}: outward issue is {_o_status}")

                    # _transitions = self.jira.transitions(_outward_issue.key)
                    # logging.info("Transitions: %s" % _transitions)
                    # for _t in _transitions:
                    #     logging.debug(f"Transition: {_t.id}, {_t.name}")
                    self.jira.transition_issue(issue.key, "Pass")

        except AttributeError:
            return

client = IssueFieldUpdater()

# client.update_estimation("CQ")
client.close_reviews("IC")