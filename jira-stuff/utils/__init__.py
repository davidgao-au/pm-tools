import logging
import os

from jira import JIRA

LOG = logging.getLogger(__name__)


class JiraClient:
    def __init__(self) -> None:
        self.jira = create_session()

    def find_board(self, board_id: int):
        boards = self.jira.boards()
        for b in boards:
            if b.id == board_id:
                return b
        LOG.error(f"Board with id {board_id} not found")
        return None


def create_session():
    email = os.environ.get('JIRA_USER_NAME')
    api_token = os.environ.get('JIRA_API_TOKEN')

    if not email:
        print("Missing Jira user name!")
        exit(1)
    else:
        print("Using JIRA user name: ", email)

    if not api_token:
        print("Missing Jira API token")
        exit(1)
    return JIRA(
        server="https://autonomic-ai.atlassian.net",
        basic_auth=(email, api_token)
    )


