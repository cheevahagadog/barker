# -*- coding:utf-8 -*-
"""Fetches bookmark data and renders the email HTML file"""

import config
from jinja2 import Environment, FileSystemLoader
from helpers import DataBaseInterface, fetch_newsletter_data, get_page_summary, get_upcoming_meetup_calendar_events


if __name__ == '__main__':
    dbi = DataBaseInterface()
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/skeleton.html")

    # Get bookmark data
    df = dbi.load_data_from_table('bookmarks')
    df = fetch_newsletter_data(df)
    bookmark_data = df.set_index('name')['url'].to_dict()

    # Summarize pages
    print("Getting page information...")
    bookmark_data = {k: [get_page_summary(k, v), v] for k, v in bookmark_data.items()}

    # add in local meetups
    params = {"state": 'UT', "key": config.MEETUP_API_KEY, "page": 10, "order": 'time'}
    print("Getting upcoming meetup info...")
    meetup_data = get_upcoming_meetup_calendar_events(params)
    html = template.render(bookmark_data=bookmark_data, page_data=config.PERSONAL_DATA, meetup_data=meetup_data)
    print("newsletter html updated!")
    with open('templates/newsletter.html', 'w') as myFile:
        myFile.write(html)
