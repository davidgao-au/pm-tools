from typing import Dict, Any

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
from jira.resilientsession import ResilientSession
from jira.resources import Issue, AgileResource

from utils import *


class BoardConfiguration(AgileResource):
    def __init__(
        self,
        options: Dict[str, str],
        session: ResilientSession,
        raw: Dict[str, Any] = None,
    ):
        AgileResource.__init__(self, "board/{0}/configuration", options, session, raw)
