# -*- coding:utf-8 -*-
"""Helper classes for db access and for creating the newsletter"""

from sqlalchemy import create_engine
import config
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from textblob import TextBlob
from gensim.summarization import summarize
import datetime
import os
import json
from os.path import expanduser


class DataBaseInterface(object):
    def __init__(self):
        self.engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

    def load_data_from_table(self, table_name=None, where_statement=None):
        """Loads all data (or data matching where statement) from the database and
        returns a pandas dataframe
        
        Args:
            table_name: name of table in SQLite db
            where_statement: SQL where statement query option
            
        Return:
            Pandas Dataframe
        """
        if not table_name:
            raise Exception("Missing table name.")

        if not where_statement:
            where_statement = ""

        df = pd.read_sql_query("SELECT * FROM " + table_name + " " + where_statement, con=self.engine)
        return df

    def save_data(self, df, table_name=None, replace_or_append='replace'):
        """Save a pandas dataframe into a SQLite table
        
        Args:
            df: Pandas dataframe to save to table
            table_name: str, name of table in SQLite db
            replace_or_append: str, option on how to save the new data, default=replace
            
        Return:
            None
        """
        if not table_name:
            raise Exception("Missing table name.")

        df.to_sql(name=table_name, con=self.engine, if_exists=replace_or_append, index=False)
        print("Saved to {}".format(table_name))
        return None


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


def get_bookmarks():
    try:
        home = expanduser("~")
        path_to_bookmarks = "Library/Application Support/Google/Chrome/Default/Bookmarks"

        # Convert the bookmark JSON to a dictionary
        big_path = os.path.join(home, path_to_bookmarks)
        if os.path.isfile(big_path):
            with open(big_path) as data_file:
                data = json.load(data_file)
            try:
                data = data['roots']['bookmark_bar']
            except ValueError:
                return "Do you have bookmarks on your bookmark bar?"
            else:
                return data
        else:
            return "File not found at location of {}".format(big_path)
    except:
        return "There is a problem with your path to the bookmarks"


def get_file_time(dtms):
    """Parses a Chrome bookmark timestamp to python datetime object
    
    Args:
        dtms: str, chrome bookmark timestamp (i.e. '13114201346955574')
        
    Returns:
        datetime.datetime representation of timestamp (i.e. datetime.datetime(2016, 7, 28, 17, 42, 26, 955574) )
    """
    if dtms:
        seconds, micros = divmod(int(dtms), 1000000)
        days, seconds = divmod(seconds, 86400)
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, micros)


def searcher(dict_, folder_name=None, counter=0, parent_folder_name=None, skip=[]) -> list:
    """recursive JSON bookmark flattening function that will exclude folder names supplied
    
    Args:
        dict_: json /  dictionary containing all bookmarks
        folder_name: the immediate parent folder of a given bookmark
        counter: 
        parent_folder_name: name of the folder on the bookmark bar
        skip: list of str, folders in your bookmarks that you would like to exclude from your newsletter
        
    Returns:
        results: list
    """
    results = []

    if dict_.get('children'):
        folder_name = dict_['name']
        if counter == 1:
            parent_folder_name = folder_name
            counter = 0
        if folder_name == "Bookmarks Bar":
            counter = 1
        for i in dict_['children']:
            if folder_name not in skip:
                r = searcher(i, folder_name, counter, parent_folder_name, skip)
                results.extend(r)
    else:
        results.append({
            "bookmark_bar_parent": parent_folder_name,
            "immediate_parent":    folder_name,
            "date_modified":       dict_.get('date_modified'),
            "date_added":          dict_.get('date_added'),
            "name":                dict_.get('name'),
            "type":                dict_.get('type'),
            "url":                 dict_.get('url')
        })
    return results


def transform_json_to_df(json_data):
    """Using recursive function, flatten out the json and convert to pandas df"""
    output = searcher(json_data, skip=config.EXCLUDE_FOLDERS)
    df = pd.DataFrame.from_records(output)
    df.date_modified = df.date_modified.apply(get_file_time)
    df.date_added = df.date_added.apply(get_file_time)
    return df


def fetch_newsletter_data(df, use_recent=False, verbose=True) -> (bool, pd.DataFrame):
    df = df[(df['bookmark_bar_parent'].isin(config.TOP_FOCUS_FOLDERS))
            | (df['immediate_parent'].isin(config.SUB_FOCUS_FOLDERS))]
    df = df[~df['url'].str.contains('|'.join(config.URL_STEMS_TO_EXCLUDE))]
    if len(df) >= config.NUM_LINKS_TO_INCLUDE:
        if use_recent:
            df.sort_values(['date_added', 'date_modified'], ascending=[False, False], inplace=True)
            df.reset_index(drop=True, inplace=True)
            return True, df.ix[0:config.NUM_LINKS_TO_INCLUDE]
        else:
            return True, df.sample(config.NUM_LINKS_TO_INCLUDE)
    else:
        if verbose:
            print("Unable to find {} bookmarks to use".format(config.NUM_LINKS_TO_INCLUDE))
        return False, None


def creating_link_info(df, verbose=True) -> dict:
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
    bookmark_dict = {k: [get_page_summary(k, v), v] for k, v in bookmark_dict.items()}
    return bookmark_dict


def get_upcoming_meetup_calendar_events(params, verbose=True) -> (bool, list):
    r = requests.get("http://api.meetup.com/self/calendar", params=params)
    if r.status_code == 200:
        meetups = []
        for i in r.json():
            if i['group']['urlname'] not in config.DO_NOT_INCLUDE_GROUPS and i['visibility'] == 'public':
                time = int(i['time'])/1000
                time_obj = datetime.datetime.fromtimestamp(time)
                meetups.append({ "date": time_obj.strftime('%A %b %-d %-I%p:'),
                                 "group_name": i['group']['name'],
                                 "event_name": i['name'],
                                 "link": i['link']})
        if verbose:
            print("Found {} meetups to add to the newsletter".format(len(meetups)))
        return True, meetups
    else:
        print("Failed to connect to Meetup API with code: {}".format(r.status_code))
        return False, []


def create_meetup_info(verbose=True) -> (bool, list):
    """Creates meetup information ready for the HTML template.
    
    Args:
        meetup_list: JSON-like list of meetup dicts
        verbose: bool, default=True
        
    Returns:
        list of meetup event data
    """
    params = {"state": config.STATE, "key": config.MEETUP_API_KEY, "page": 10, "order": 'time'}
    if verbose:
        print("Getting upcoming meetup info...")
    success, meetup_data = get_upcoming_meetup_calendar_events(params)
    if success:
        return True, meetup_data
    else:
        return False, []
