import os

from jira import JIRA


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
