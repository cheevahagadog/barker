# -*- coding:utf-8 -*-
"""Fetches the bookmarks from Chrome files and saves them into a SQLite db"""

from app.helpers import DataBaseInterface, get_bookmarks, transform_json_to_df


if __name__ == '__main__':
    dbi = DataBaseInterface()
    success, bookmarks_dict = get_bookmarks()
    if success:
        data = transform_json_to_df(bookmarks_dict)
        dbi.save_data(data, table_name='bookmarks')
        print("Bookmarks table updated, {} entries".format(len(data)))
