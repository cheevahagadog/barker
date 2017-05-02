# -*- coding: utf-8 -*-
""" Configuration settings for how you would like barker to work for you."""

import os
import time

basedir = os.path.abspath(os.path.dirname(__file__))


# ---- FEEDBACK WHILE RUNNING -------------#
VERBOSE = True

# ---- NEWSLETTER/PERSONAL SETTINGS ------ #
PERSONAL_DATA = {
    'NAME': "Nathan",
    'TWITTER_HANDLE': "data_cheeves",
    'WEBSITE_URL': "http://www.github.com/cheevahagadog",
    'WEBSITE_DESCRIPTION': "My weekly helpful reminder of the great things I've bookmarked.",
    'EMAIL_SUBJECT': "Your weekly newsletter!",
    'HEADER_LOGO': "http://placehold.it/350x65",  # OR "../static/img/yourlogo.png"
    'PERSONAL_IMG': "http://placehold.it/150",  # OR "../static/img/yourimage.jpg"
    'DATE': time.strftime("%x")
}


# ---- BOOKMARK SETTINGS ------ #
EXCLUDE_FOLDERS = ['Personal', 'Projects', 'Mealio', 'FrontAnalytics', "Dependency hell!", "PC Automation w/ R"]
USE_MOST_RECENT_BOOKMARKS = True

# If included, barker will only use bmks from these top level folders
BOOKMARK_BAR_FOCUS_FOLDERS = ['Data Science', 'Review']

# OTHER_FOCUS_FOLDERS - Use when you want to use bmks from a sub folder with a specific name
OTHER_FOCUS_FOLDERS = ['Great Blogs']

NUM_LINKS_TO_INCLUDE = 7  # This will be the number of links in the newsletter
URL_STEMS_TO_EXCLUDE = ['http://stackoverflow.com', "https://docs.google"]

# If barker can't detect where your Chrome bmks are saved, enter full path to Bookmarks directory
BOOKMARK_PATH = None


# ---- MEETUP SETTINGS ------ #
MEETUP_API_KEY = os.environ.get("MEETUP_API_KEY")
STATE = "UT"
DO_NOT_INCLUDE_GROUPS = []


# ---- EMAIL SETTINGS --------#
EMAIL = True
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


# ---- STORAGE SETTINGS ------#
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'barker.db')
