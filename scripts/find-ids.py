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

    retrieved_data = find_corresponding_ids(LOADFILE)

    create_csv(retrieved_data)

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

def find_corresponding_ids(loadfile):
    """takes loadfile name, reads header to determine if getting adspids or site_indivs, makes dict of returned data keyed by supplied id, returns the dict"""
    retrieved_data_dict = {}
    supplied_id_type = '' # will be `adsp_id` or `site_indiv_id`

    def handle_db_query(row):
        """takes parsed row from file-reader, handles based on supplied_id_type, builds data dict"""
        supplied_id = row[0]
        
        if supplied_id_type == 'adsp_id':

            retrieved_data = database_connection(f"SELECT * FROM lookup WHERE adsp_id = '{supplied_id}'")
            if retrieved_data:
                retrieved_data_dict[supplied_id] = retrieved_data[0]
            else:
                print(f"No matching records found for {supplied_id_type} {supplied_id}")
                error_log[f'{supplied_id}-NONE'] = [supplied_id, f'No record was found matching {supplied_id}.']
        else:
            supplied_cohort_code = row[1]
            retrieved_data = database_connection(f"SELECT * FROM lookup WHERE site_indiv_id = '{supplied_id}' AND cohort_identifier_code = '{supplied_cohort_code}'")
            if retrieved_data:
                retrieved_data_dict[supplied_id] = retrieved_data[0]
            else:
                print(f"No matching records found for {supplied_id_type} {supplied_id}")
                error_log[f'{supplied_id}-NONE'] = [supplied_id, f'No record was found matching {supplied_id}.']

    with open(f'../source_files/{LOADFILE}', mode='r', encoding='utf-8-sig') as csv_file:
        """"determine whether am looking for data by adspid or site_indiv_id"""
        ids_from_loadfile = csv.reader(csv_file)
        for row in ids_from_loadfile:
            if ids_from_loadfile.line_num == 1:
                for column in row:
                    if row.index(column) == 0:
                        supplied_id_type = column
            else:
                handle_db_query(row)

    return retrieved_data_dict

def create_csv(retrieved_data_dict):
    """takes the dict created in the lookup function, creates a csv of the data"""
    timestamp = calendar.timegm(time.gmtime())
    retrieved_columns = database_connection("SELECT column_name FROM information_schema.columns WHERE table_name = 'lookup'")
    column_names = ["supplied_id"]

    for name in retrieved_columns:
        column_names.append(name[0])

    with open(f'../log_files/ids-{timestamp}.csv', mode='w+', encoding='utf-8-sig') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(column_names)
        for key, record in retrieved_data_dict.items():
            reclist = list(record)
            reclist.insert(0,key)
            csv_writer.writerow(reclist)

def generate_errorlog():
    """creates error log and writes to 'log_files' directory"""

    timestamp = calendar.timegm(time.gmtime())
    f = open(f'../log_files/{timestamp}-log.txt', 'w+')
    f.write(f'{str(len(error_log.items()))} flag(s) raised in runtime. See details below: \n\n')
    for key, value in error_log.items():
        f.write(f'Error: {value[1]} \n')
        f.write(f'family_site_id: {value[0][0]}\n')
        f.write(f'indiv_site_id: {value[0][1]}\n')
        f.write(f'combined_site_id: {value[0][2]}\n')
        f.write(f'cohort_identifier_code: {value[0][3]}\n\n')

def generate_success_list():
    """creates a list of successfully created and inserted ADSP IDs"""

    timestamp = calendar.timegm(time.gmtime())
    f = open(f'../log_files/success_lists/{timestamp}-generated_ids.txt', 'w+')
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
