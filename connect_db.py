# functions that will connect to the database
import sqlite3

from flask import g



def connect_db():

    # object that has the path to the database
    sql = sqlite3.connect('/Users/aaronsmith/development/code/flask-course/food-tracker-app/food_log.db')

    # changes default datatype to dictionaries instead of tuples
    sql.row_factory = sqlite3.Row
    return sql

# gets the database connection
def get_db():
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db




