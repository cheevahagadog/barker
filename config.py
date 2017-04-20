# -*- coding: utf-8 -*-

import os
import time

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'barker.db')

# Bookmark configs
EXCLUDE_FOLDERS = ['Personal', 'Projects', 'Mealio', 'FrontAnalytics', "Dependency hell!", "PC Automation w/ R"]
TOP_FOCUS_FOLDERS = ['Data Science', 'Review']
SUB_FOCUS_FOLDERS = ['Great Blogs']
NUM_LINKS_TO_INCLUDE = 7
URL_STEMS_TO_EXCLUDE = ['http://stackoverflow.com', "https://docs.google"]
SEARCH_RECENT = False

# Meetup settings
MEETUP_API_KEY = os.environ.get("MEETUP_API_KEY", None)
DO_NOT_INCLUDE_GROUPS = []

RUN = {
    "MONTHLY": 15,
    "WEEKLY": "SAT",
    "DAILY": "15:00",
    "HOURLY": '15'
}

EMAIL = False
DELIVERY_DIR = os.path.join(
    os.path.abspath(__file__),
    'delivery'
    )

# mail server settings
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", None)
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", None)

# administrator list

PERSONAL_DATA = {
    'NAME': "Nathan",
    'TWITTER_HANDLE': "data_cheeves",
    'WEBSITE_URL': "http://www.github.com/cheevahagadog",
    'WEBSITE_DESCRIPTION': "My weekly helpful reminder of the great things I've bookmarked.",
    'HEADER_LOGO': "../static/img/yourlogo.png",
    'PERSONAL_IMG': "../static/img/yourimage.jpg",
    'DATE': time.strftime("%x")
}


