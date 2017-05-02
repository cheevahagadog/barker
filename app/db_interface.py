# -*- coding:utf-8 -*-
"""Helper classes for db access and for creating the newsletter"""

from sqlalchemy import create_engine
import config
import pandas as pd


class DBInterface(object):
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
