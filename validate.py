import psycopg2
import csv
from dotenv import load_dotenv
import os

import calendar
import time

        
def connect_database():
    global current_records
    global connection

    load_dotenv()
    
    DBIP = os.getenv('DBIP')
    DBPASS = os.getenv('DBPASS')
    DBPORT = os.getenv('DBPORT')
    DB = os.getenv('DB')
    DBUSER = os.getenv('DBUSER')

    try:
        connection = psycopg2.connect(
                        user = DBUSER,
                        password = DBPASS,
                        host = DBIP,
                        port = DBPORT,
                        database = DB
                    )

        cursor = connection.cursor()
        main()

    except (Exception, psycopg2.Error) as error:
        print('Error in database connection', error)

    finally:
        if(connection):
            cursor.close()
            connection.close()
            print('database connection closed')
            generate_errorlog()
            generate_success_list()

def main():
    confirm = input("Have you checked the newly added subject information for correctness and now want to validate them? (y/n)")
    if confirm == 'y':
        get_filename()

    else:
        print('Please review the newly added data and validate when ready.')
def validate(data):
    for adspid_id in data:
        print(adspid_id)


def get_filename():
    filename = input("Please enter the name of file containing newly created ids: ")
    try:
        with open(f"./log_files/success_lists/{filename}", "r") as file_data:
            for line in file_data:
                data = list(line.split(', '))
                validate(data)

    except:
        print('That file does not exist, try again')
        get_filename()

if __name__ == "__main__":
    connect_database()
