# -*- coding:utf-8 -*-
"""Fetches the bookmarks from Chrome files and saves them into a SQLite db"""

import pandas as pd
import config
import datetime
import os
import json
from app.db_interface import DBInterface


class CollectUpdateBookmarks(object):
    """Collects bookmark json from Chrome files and saves to bookmarks table"""

    def __init__(self):
        self.dbi = DBInterface()

    def original_count(self):
        """Return the original count of bookmarks in the table"""
        try:
            df = self.dbi.load_data_from_table('bookmarks')
            count = len(df)
        except:
            count = 0
            return False, count
        else:
            return True, count

    @staticmethod
    def get_bookmarks() -> (bool, dict):
        """Searches for the bookmark file path and returns a JSON of bookmark data from the Bookmarks bar location"""
        if config.BOOKMARK_PATH:
            full_path = config.BOOKMARK_PATH
        else:
            try:
                home = os.path.expanduser("~")
            except Exception as e:
                print(e, "There is a problem with your path to the bookmarks")  # Maybe a windows error?
                return False, {}
            else:
                path_to_bookmarks = "Library/Application Support/Google/Chrome/Default/Bookmarks"
                full_path = os.path.join(home, path_to_bookmarks)
        if os.path.isfile(full_path):
            try:
                with open(full_path) as data_file:
                    data = json.load(data_file)
                data = data['roots']['bookmark_bar']
            except (ValueError, KeyError):
                print("Unable to find bookmarks on your Bookmarks bar. Are you sure you have bookmarks on your bookmarks\
                 bar?")
                return False, {}
            else:
                return True, data
        else:
            print("File not found at location of {}. Check path to your Chrome bookmarks.".format(full_path))
            return False, {}

    def searcher(self, dict_, folder_name=None, counter=0, parent_folder_name=None, skip=[]) -> list:
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
                    r = self.searcher(i, folder_name, counter, parent_folder_name, skip)
                    results.extend(r)
        else:
            results.append({
                "bookmark_bar_parent": parent_folder_name,
                "immediate_parent": folder_name,
                "date_modified": dict_.get('date_modified'),
                "date_added": dict_.get('date_added'),
                "name": dict_.get('name'),
                "type": dict_.get('type'),
                "url": dict_.get('url')
            })
        return results

    @staticmethod
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

    def transform_json_to_df(self, json_data):
        """Using recursive function, flatten out the json and convert to pandas df"""
        output = self.searcher(json_data, skip=config.EXCLUDE_FOLDERS)
        df = pd.DataFrame.from_records(output)
        df.date_modified = df.date_modified.apply(self.get_file_time)
        df.date_added = df.date_added.apply(self.get_file_time)
        return df

    def main(self):
        success, bookmarks_dict = self.get_bookmarks()
        if success:
            data = self.transform_json_to_df(bookmarks_dict)
            self.dbi.save_data(data, table_name='bookmarks')
            if config.VERBOSE:
                print("Bookmarks table updated, {} entries".format(len(data)))
            return True
        else:
            return False

if __name__ == '__main__':
    collecter = CollectUpdateBookmarks()
    collecter.main()
