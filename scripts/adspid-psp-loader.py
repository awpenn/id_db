import sys
sys.path.append('/id_db/.venv/lib/python3.6/site-packages')

import psycopg2
import csv
from dotenv import load_dotenv
import os

import calendar
import time

new_records = []
success_id_log = []
error_log = {}

load_dotenv()
DBIP = os.getenv('DBIP')
DBPASS = os.getenv('DBPASS')
DBPORT = os.getenv('DBPORT')
DB = os.getenv('DB')
DBUSER = os.getenv('DBUSER')
LOADFILE = ''

def main():
    """main conductor function for the script.  Takes some input about the type of data being uploaded and runs the process from there."""
    
    global family_data_creation
    global create_family_ids
    global LOADFILE
   
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
    
    create_dict()

def database_connection(query):
    """takes a string SQL statement as input, and depending on the type of statement either performs an insert or returns data from the database"""

    try:
        connection = psycopg2.connect(user = DBUSER, password = DBPASS, host = DBIP, port = DBPORT, database = DB)
        cursor = connection.cursor()
        cursor.execute(query)

        if "INSERT" in query:
            connection.commit()
            cursor.close()
            connection.close()
            
        else:
            returned_array = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return returned_array

    except (Exception, psycopg2.Error) as error:
        print('Error in database connection', error)
    

    finally:
        if(connection):
            cursor.close()
            connection.close()
            print('database connection closed')

def create_dict():
    """creates dicts of to-be-added subject data and already-in-database data.  Dict elements have keys created by concatenating the cohort code and lookup id"""

    current_records_dict = {}
    new_records_dict = {}

    current_records = database_connection('SELECT * FROM lookup')

    for row in current_records:

        table_id = row[0]
        adspid = row[1]
        site_fam = row[2]
        site_indiv_id = row[3]
        cohort_identifier_code = row[4]
        lookup_id = row[5]
        
        current_records_dict[f'{cohort_identifier_code}-{lookup_id}'] = row

    with open(f'./source_files/{LOADFILE}', mode='r', encoding='utf-8-sig') as csv_file:
        new_records = csv.reader(csv_file) 

        for row in new_records:
            site_indiv_id = row[0]
            cohort_identifier_code = row[1]
            lookup_id = site_indiv_id


            new_records_dict[f'{cohort_identifier_code}-{lookup_id}'] = row

    compare(current_records_dict, new_records_dict)

def compare(current_records_dict, new_records_dict):
    """takes as input the dict made of subject data from the database and the dict created from data in the loadfile.  Compares new data with existing data to determine if new db writes need to occur, and if new subjects are found, they are passed to the 'write_to_database' function"""

    records_to_database_dict = {}
    for key, value in new_records_dict.items():
        try:
            if current_records_dict[key]:
                print(f'record exists for: {current_records_dict[key]}')

                error_log[key] = [value, 'A record for this subject already exists in the database. Check the database and your loadfile for correctness.']

        except:
            print(f'new record will be created for {key}')

            records_to_database_dict[key] = new_records_dict[key]
    
    if len(records_to_database_dict) > 0: 
        print(records_to_database_dict)
        write_to_database(records_to_database_dict)
    else:
        print('No new records to create.....')

def write_to_database(records_to_database_dict):
    """takes as input a dict of new subject data, generates new ADSP ids, constructs INSERT statements and sends to the 'database_connection' function"""
    
    for key, value in records_to_database_dict.items():
        #need select statement to get id of cohort identifier code, adsp_family_id for site_fam_id, next adsp_indiv_partial_id based on the cohort,
        #next adspid based on the cohort

        site_indiv_id = value[0]
        site_fam_id = 'NA'
        subject_type = 'case/control'
        lookup_id = site_indiv_id
        adsp_family_id = 'NA'
        adsp_indiv_partial_id = 'NA'

        cohort_identifier_code = value[1]

        id_prefix = database_connection(f"SELECT DISTINCT adsp_id_leading_letter FROM cohort_identifier_codes WHERE cohort_identifier_code = '{cohort_identifier_code}'")[0][0]

        ## get cohort id
        retrieved_cohort_id = database_connection(f"SELECT DISTINCT id FROM cohort_identifier_codes WHERE cohort_identifier_code = '{cohort_identifier_code}'")
        
        for row in retrieved_cohort_id:
            cohort_identifier_code_key = row[0]

            adsp_id = f'{id_prefix}-{cohort_identifier_code}-{site_indiv_id}'

            database_connection(f"INSERT INTO generated_ids (site_fam_id, site_indiv_id, cohort_identifier_code_key, lookup_id, adsp_family_id, adsp_indiv_partial_id, adsp_id, subject_type) VALUES ('{site_fam_id}','{site_indiv_id}',{cohort_identifier_code_key},'{lookup_id}','{adsp_family_id}','{adsp_indiv_partial_id}','{adsp_id}','{subject_type}')")
            success_id_log.append(adsp_id)

def generate_errorlog():
    """creates error log and writes to 'log_files' directory"""

    timestamp = calendar.timegm(time.gmtime())
    f = open(f'./log_files/{timestamp}-log.txt', 'w+')
    f.write(f'{str(len(error_log.items()))} flag(s) raised in runtime. See details below: \n\n')
    for key, value in error_log.items():

        f.write(f'Error: {value[1]} \n')
        f.write(f'site_indiv_id: {value[0][0]}\n')
        f.write(f'cohort_identifier_code: {value[0][1]}\n\n')

def generate_success_list():
    """creates a list of successfully created and inserted ADSP IDs"""

    timestamp = calendar.timegm(time.gmtime())
    if len(success_id_log) > 0:
        f = open(f'./log_files/success_lists/{timestamp}-generated_ids.txt', 'w+')
        for id in success_id_log:
            if success_id_log.index(id) >= len(success_id_log)-1:
                f.write(id)
            else:
                f.write(id + ', ')

        f.close()

if __name__ == '__main__':
    main()
    generate_errorlog()
    generate_success_list()
    print('Loading complete.')