from sqlalchemy import create_engine
import config
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from textblob import TextBlob
from gensim.summarization import summarize
import datetime
import os, json
from os.path import expanduser


class DataBaseInterface(object):
    def __init__(self):
        self.engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

    def load_data_from_table(self, table_name=None, where_statement=None):
        """
        Loads all data (or data matching where statement) from the database and
        returns a pandas dataframe
        :param table_name:
        :param where_statement:
        :return: Pandas Dataframe
        """
        if not table_name:
            raise Exception("Missing table name.")

        if not where_statement:
            where_statement = ""

        # Fetch data from SQL table and return as pandas dataframe
        df = pd.read_sql_query("SELECT * FROM " + table_name + " " + where_statement,
                               con=self.engine)
        return df

    def save_data(self, df, table_name=None, replace_or_append='replace'):
        if not table_name:
            raise Exception("Missing table name.")

        df.to_sql(name=table_name, con=self.engine,
                  if_exists=replace_or_append, index=False)
        return "Saved to {}".format(table_name)


def get_page_summary(title, url):
    r = requests.get(url)
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
            print("One sentence found for \t {}".format(title))
            return "  ".join(tokenized_text)
        elif not tokenized_text:
            print("No text found for \t {}".format(title))
            return title
        elif len(tokenized_text) <= 5:
            print("LTE 5 sentences found for \t {}".format(title))
            return "  ".join(tokenized_text)
        else:
            try:
                ntext = summarize("  ".join(tokenized_text), word_count=50)
                print("summarizing text for \t {}...".format(title))
                return ntext
            except:
                return "  ".join(tokenized_text)[:150] + " ..."
    else:
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
                return data
            except ValueError:
                return "Do you have bookmarks on your bookmark bar?"
        else:
            return "File not found at location of {}".format(big_path)
    except:
        return "There is a problem with your path to the bookmarks"


def get_file_time(dtms):
    seconds, micros = divmod(int(dtms), 1000000)
    days, seconds = divmod(seconds, 86400)
    return datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, micros) #.strftime('%m-%d-%Y %H:%M:%S %Z'))


def transform_json_to_df(json_data):
    """Using recursive function, flatten out the json and convert to pandas df"""
    output = searcher(json_data, skip=config.EXCLUDE_FOLDERS)
    df = pd.DataFrame.from_records(output)
    df.date_added = df.date_added.apply(get_file_time)
    return df


def searcher(d, name=None, counter=0, g_name=None, skip=None):
    """JSON bookmark flattening function that will exclude folder names supplied"""
    results = []

    if d.get('children'):
        name = d['name']
        if counter == 1:
            g_name = name
            counter = 0
        if name == "Bookmarks Bar":
            counter = 1
        for i in d['children']:
            if name not in skip:
                r = searcher(i, name, counter, g_name, skip)
                results.extend(r)
    else:
        results.append({
            "bookmark_bar_parent": g_name,
            "immediate_parent":    name,
            # "date_modified":       d.get('date_modified'),
            "date_added":          d['date_added'],
            "name":                d['name'],
            "type":                d['type'],
            "url":                 d.get('url')
        })
    return results


def fetch_newsletter_data(df):
    df = df[(df['bookmark_bar_parent'].isin(config.TOP_FOCUS_FOLDERS))
            | (df['immediate_parent'].isin(config.SUB_FOCUS_FOLDERS))]
    df = df[~df['url'].str.contains('|'.join(config.URL_STEMS_TO_EXCLUDE))]
    return df.sample(config.NUM_LINKS_TO_INCLUDE)


def get_upcoming_meetup_calendar_events(params):
    r = requests.get("http://api.meetup.com/self/calendar", params=params)
    if r.status_code == 200:
        data = []
        for i in r.json():
            if i['group']['urlname'] not in config.DO_NOT_INCLUDE_GROUPS and i['visibility'] == 'public':
                time = int(i['time'])/1000
                time_obj = datetime.datetime.fromtimestamp(time)
                data.append({
                        "date": time_obj.strftime('%A %b %-d %-I%p:'),
                        "group_name": i['group']['name'],
                        "event_name": i['name'],
                        "link": i['link']
                })
        return data
