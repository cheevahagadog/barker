# -*- coding:utf-8 -*-
"""Fetches bookmark data and renders the email HTML file"""

from jinja2 import Environment, FileSystemLoader

import config
from app.helpers import DataBaseInterface, fetch_newsletter_data, creating_link_info, create_meetup_info

dbi = DataBaseInterface()
env = Environment(loader=FileSystemLoader('app/templates'))
template = env.get_template("skeleton.html")

if __name__ == '__main__':
    df = dbi.load_data_from_table('bookmarks')
    success, df = fetch_newsletter_data(df, use_recent=config.FOCUS_RECENT)
    if success:
        bookmark_dict = creating_link_info(df)
        success, meetup_data = create_meetup_info()
        html = template.render(bookmark_data=bookmark_dict, page_data=config.PERSONAL_DATA, meetup_data=meetup_data)
        with open('app/templates/newsletter.html', 'w') as myFile:
            myFile.write(html)
            print("newsletter html updated!")
