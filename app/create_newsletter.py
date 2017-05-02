# -*- coding:utf-8 -*-
"""Fetches bookmark data and renders the email HTML file"""

from jinja2 import Environment, FileSystemLoader
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from textblob import TextBlob
import datetime
from gensim.summarization import summarize
import config
from app.db_interface import DBInterface


class NewsletterTemplate(object):
    """Uses bookmark data to produce the newsletter"""
    def __init__(self):
        self.dbi = DBInterface()
        self.env = Environment(loader=FileSystemLoader('app/templates/'))
        self.template = self.env.get_template("skeleton.html")
        self.all_bookmarks_df = self.dbi.load_data_from_table('bookmarks')

    def filter_and_select_links(self, use_recent=False, verbose=True) -> (bool, pd.DataFrame):
        """Pulling from all bookmarks, filters out folders the user doesn't want to show, and/or draws a random
        number of links to fulfill the user's desired number of links"""
        df = self.all_bookmarks_df
        original_len = filtered_len = len(df)
        if config.BOOKMARK_BAR_FOCUS_FOLDERS or config.OTHER_FOCUS_FOLDERS:
            df = df[(df['bookmark_bar_parent'].isin(config.BOOKMARK_BAR_FOCUS_FOLDERS))
                    | (df['immediate_parent'].isin(config.OTHER_FOCUS_FOLDERS))]
            filtered_len = len(df)
        df = df[~df['url'].str.contains('|'.join(config.URL_STEMS_TO_EXCLUDE))]
        url_filtered_len = len(df)
        if url_filtered_len >= config.NUM_LINKS_TO_INCLUDE:
            if use_recent:
                df.sort_values(['date_added', 'date_modified'], ascending=[False, False], inplace=True)
                df.reset_index(drop=True, inplace=True)
                return True, df.ix[0:config.NUM_LINKS_TO_INCLUDE]
            else:
                return True, df.sample(config.NUM_LINKS_TO_INCLUDE)
        else:
            if verbose:
                print("Of the {0} bookmarks found, {1} were removed by focus folders and {2} were removed by URL stems"
                      .format(original_len, original_len - filtered_len, original_len - url_filtered_len))
                print("Unable to find {} bookmarks".format(config.NUM_LINKS_TO_INCLUDE))
            return False, None

    @staticmethod
    def get_page_summary(title, url, verbose=False) -> str:
        """Request HTML of a bookmarked link and creates a summary to be used in the newsletter

        Args:
            title: str, bookmark title as saved in your bookmarks
            url: str, link in bookmark
            verbose: bool, prints out helpful debugging feedback, default= False

        Returns:
                Summary text of bookmarked link
        """
        r = requests.get(url)
        if verbose:
            print('requesting web page data...')
        if r.status_code == 200:
            soup = bs(r.text, "html5lib")
            for script in soup.find_all('script'):
                script.extract()
            for code in soup.find_all('code'):
                code.extract()

            paragraphs = soup.find_all('p')[0:10]
            text = [paragraph.get_text() for paragraph in paragraphs]
            text = list(filter(None, text))
            blob = TextBlob(" ".join(text))
            tokenized_text = [str(sentence) for sentence in blob.sentences]

            if len(tokenized_text) == 1:
                if verbose:
                    print("One sentence found for \t {}".format(title))
                return "  ".join(tokenized_text)
            elif not tokenized_text:
                if verbose:
                    print("No text found for \t {}".format(title))
                return title
            elif len(tokenized_text) <= 5:
                if verbose:
                    print("LTE 5 sentences found for \t {}".format(title))
                return "  ".join(tokenized_text)
            else:
                try:
                    ntext = summarize("  ".join(tokenized_text), word_count=50)
                    if verbose:
                        print("summarizing text for \t {}...".format(title))
                    return ntext
                except:
                    return "  ".join(tokenized_text)[:150] + " ..."
        else:
            if verbose:
                print("bad request for \t {}".format(title))
            return title

    def creating_link_info(self, df, verbose=True) -> dict:
        """Creates the bookmark data so it's ready for use in the HTML template.

        Args:
            df: pandas Dataframe of selected bookmarks
            verbose: bool, default=True

        Returns:
            dictionary of bookmark title: 
        """
        bookmark_dict = df.set_index('name')['url'].to_dict()
        if verbose:
            print("Summarizing bookmark pages...")
        bookmark_dict = {k: [self.get_page_summary(k, v), v] for k, v in bookmark_dict.items()}
        return bookmark_dict

    @staticmethod
    def get_upcoming_meetup_calendar_events(params, verbose=True) -> (bool, list):
        r = requests.get("http://api.meetup.com/self/calendar", params=params)
        if r.status_code == 200:
            meetups = []
            for i in r.json():
                if i['group']['urlname'] not in config.DO_NOT_INCLUDE_GROUPS and i['visibility'] == 'public':
                    time = int(i['time']) / 1000
                    time_obj = datetime.datetime.fromtimestamp(time)
                    meetups.append({"date": time_obj.strftime('%A %b %-d %-I%p:'),
                                    "group_name": i['group']['name'],
                                    "event_name": i['name'],
                                    "link": i['link']})
            if verbose:
                print("Found {} meetups to add to the newsletter".format(len(meetups)))
            return True, meetups
        else:
            print("Failed to connect to Meetup API with code: {}".format(r.status_code))
            return False, []

    def create_meetup_info(self, verbose=True) -> (bool, list):
        """Creates meetup information ready for the HTML template.

        Args:
            verbose: bool, default=True

        Returns:
            list of meetup event data
        """
        params = {"state": config.STATE, "key": config.MEETUP_API_KEY, "page": 10, "order": 'time'}
        if verbose:
            print("Getting upcoming meetup info...")
        success, meetup_data = self.get_upcoming_meetup_calendar_events(params)
        if success:
            return True, meetup_data
        else:
            return False, []

    def fill_html_template(self, bookmark_dict, meetup_data):
        """Render HTML template with bookmark links, personal and meetup data"""
        html = self.template.render(bookmark_data=bookmark_dict, page_data=config.PERSONAL_DATA, meetup_data=meetup_data)
        return html

    def main(self):
        """populate template"""
        success, filtered_df = self.filter_and_select_links(use_recent=config.USE_MOST_RECENT_BOOKMARKS)
        if success:
            bookmark_dict = self.creating_link_info(df=filtered_df, verbose=config.VERBOSE)
            success, meetup_data = self.create_meetup_info()
            html = self.fill_html_template(bookmark_dict, meetup_data)
            with open('app/templates/newsletter.html', 'w') as f:
                f.write(html)
            if config.VERBOSE:
                print("newsletter html updated!")
            return True
        else:
            return False


if __name__ == '__main__':
    templater = NewsletterTemplate()
    templater.main()
