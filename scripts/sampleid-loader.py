import psycopg2
import csv
from dotenv import load_dotenv
import os

import calendar
import time

load_dotenv()
DBIP = os.getenv('DBIP')
DBPASS = os.getenv('DBPASS')
DBPORT = os.getenv('DBPORT')
DB = os.getenv('DB')
DBUSER = os.getenv('DBUSER')


current_samples_ids = []
new_samples_initial_dict = {}
new_samples_for_database_dict = {}
marked_as_duplicate_dict = {}
error_list = []



def main():

    def get_filename():
        while True:
            try:
                filename_input = input(f"Enter loadfile name. ")
            except ValueError:
                continue
            if len(filename_input) < 4:
                print('Please enter a valid filename.')
                continue
            else:
                if '.csv' not in filename_input:
                    print("Please make sure you've uploaded a .csv file.")
                    continue
                else:
                    filename = filename_input
                    break
        
        return filename

    LOADFILE = get_filename()

    create_existing_ids_list()
    create_new_samples_dict(LOADFILE)
    look_for_duplicates()
    write_to_database()
    generate_duplicate_report()

    if len(error_list) > 0:
        write_error_log()

def database_connection(query):
    try:
        connection = psycopg2.connect(user = DBUSER, password = DBPASS, host = DBIP, port = DBPORT, database = DB)
        cursor = connection.cursor()
        cursor.execute(query)

        if "INSERT" in query:
            connection.commit()
        else:
            returned_array = cursor.fetchall()
            return returned_array

        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error:
        print('Error in database connection', error)
        error_list.append(error)
        
    finally:
        if(connection):
            cursor.close()
            connection.close()
            print('database connection closed')
 
def create_existing_ids_list():
    current_samples = database_connection("select * from sample_ids")

    for row in current_samples:
        current_samples_ids.append(row[1])

def create_new_samples_dict(LOADFILE):

    with open(f'./source_files/{LOADFILE}', mode='r', encoding='utf-8-sig') as csv_file:
        new_samples = csv.reader(csv_file)
        for row in new_samples:
            sample_id = row[0]
            data_type = row[1]
            sequencing_study = row[2]
            subject_adsp_id = row[3]

            new_samples_initial_dict[sample_id] = row

def look_for_duplicates():
    for dictkey, new_sample in new_samples_initial_dict.items():
        if dictkey in current_samples_ids:
            marked_as_duplicate_dict[dictkey] = new_sample
        else:
            new_samples_for_database_dict[dictkey] = new_sample

def write_to_database():
    for dictkey, record in new_samples_for_database_dict.items():
        sample_id = record[0]
        data_type = record[1]
        sequencing_study = record[2]
        subject_adsp_id = record[3]

        query_string = f"INSERT INTO sample_ids (sample_id, data_type, sequencing_study, subject_adsp_id) VALUES ('{sample_id}', '{data_type}', '{sequencing_study}', '{subject_adsp_id}')"
        database_connection(query_string)

def generate_duplicate_report():
    if len(marked_as_duplicate_dict) > 0:
        timestamp = calendar.timegm(time.gmtime())
        f = open(f'./log_files/{timestamp}-log.txt', 'w+')
        f.write(f'{str(len(marked_as_duplicate_dict.items()))} duplicate sample_id(s) found. See details below: \n\n')
        for dictkey, record in marked_as_duplicate_dict.items():
            f.write(f'sample_id: {record[0]}\n')
            f.write(f'data_type: {record[1]}\n')
            f.write(f'sequencing_study: {record[2]}\n')
            f.write(f'subject-adsp_id: {record[3]}\n\n')
        
        f.write('\n\n\n Please alter these ids to generate uniqueness and re-submit.')
        f.close()

def write_error_log():
    if len(error_list) > 0:
        timestamp = calendar.timegm(time.gmtime())
        f = open(f'./log_files/{timestamp}-error-log.txt', 'w+')
        f.write(f'{str(len(error_list))} error(s) occured during data check and load. See details below: \n\n')
        for error in error_list:
            f.write(f"Error:\n {error}\n")
    
    f.close()

if __name__ == '__main__':
    main()

