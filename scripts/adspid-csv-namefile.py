import sys
sys.path.append('/id_db/.venv/lib/python3.6/site-packages')

import psycopg2
import csv
from dotenv import load_dotenv
import os

import calendar
import datetime
import time

new_records = []
success_id_log = []
error_log = {}
family_data_creation = False
create_family_ids = False

special_cohorts = ['LOAD', 'RAS', 'UPN']

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
    
    alert_last_created_id()

    LOADFILE = get_filename()

    print("Warning: You can only load data of one subject_type (e.g. case/control, family, etc.) at a time.")
    time.sleep(2.5)
    select_casefam = input('Are you loading family data? (y/n) ')
    if select_casefam not in ['y', 'n', 'Y', 'N', 'yes', 'no', 'YES', 'NO', 'Yes', 'No']:
        main()

    else:
        if select_casefam in ['y', 'Y', 'yes', 'Yes', 'YES']:
            family_data_creation = True

            select_make_famids = input('Do you want family ids checked and generated for these subjects?(y/n) ')
            if select_make_famids in ['y', 'Y', 'yes', 'Yes', 'YES']:
                print('family ids will be checked and generated.')
                create_family_ids = True
            else:
                print('family ids will not be checked and generated for these family study subjects.')
    
            
    if select_casefam in ['n', 'N', 'no', 'No', 'NO']:
        print('family ids will not be checked and generated.')
    
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
            #print('database connection closed')

def create_dict():
    """creates dicts of to-be-added subject data and already-in-database data.  Dict elements have keys created by concatenating the cohort code and lookup id"""

    current_records_dict = {}
    new_records_dict = {}
    legacy_check_dict = {}
    global special_cohorts

    def combine_new_and_legacy_dicts(processed_legacy_dict):

        combined_new_records_dict = {**new_records_dict, **processed_legacy_dict}
        compare(current_records_dict, combined_new_records_dict)

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

        ## check if any new ids are for MIAMI, so can flag 
        flag_keys = ['DUK26057', '-1000']
        flagged_ids_dict = {}

        for row in new_records:
            if row[ 2 ] == 'MIA':
                if any( keys in row[ 0 ] for keys in flag_keys ):
                    flagged_ids_dict[ row[ 1 ] ] = row

        if flagged_ids_dict:
            DUK26057_and_1000_special_flag( flagged_ids_dict )

        csv_file.seek( 0 ) ## have to reset the reader after looping through above in order to loop below
        for row in new_records:
            site_fam_id = row[0]
            site_indiv_id = row[1]

            if family_data_creation:
                lookup_id = f'{site_fam_id}_{site_indiv_id}'
            else:
                lookup_id = site_indiv_id
            cohort_identifier_code = row[2]
            
            row.insert(2, lookup_id)

            if cohort_identifier_code in special_cohorts and family_data_creation:
                if '26_' in site_fam_id or '26-' in site_fam_id:
                    legacy_check_dict[f'{cohort_identifier_code}-{lookup_id}'] = row
                else:
                    new_records_dict[f'{cohort_identifier_code}-{lookup_id}'] = row
            else:
                new_records_dict[f'{cohort_identifier_code}-{lookup_id}'] = row

    if len(legacy_check_dict) > 0:

        legacy_check(legacy_check_dict, combine_new_and_legacy_dicts)
    
    else:
        compare(current_records_dict, new_records_dict)

def legacy_check(legacy_check_dict, callback):
    """takes a dict of subject data to check in "legacy" condition, processes the legacy check subject data if necessary, and passes the reprocessed dict to the 'combine_new_and_legacy_dicts' function"""

    processed_legacy_dict = {}
    for key, value in legacy_check_dict.items():
        query_family_id = value[0]
        site_indiv_id = value[1]
        lookup_id = value[2]
        cohort_identifier_code = value[3]

        returned_cohort_code_tuple = database_connection(f"SELECT DISTINCT cohort_identifier_code FROM lookup WHERE site_fam_id = '{query_family_id}'")

        if len(returned_cohort_code_tuple) == 1 :
            returned_cohort_code = returned_cohort_code_tuple[0][0]

        else:
            if len(returned_cohort_code_tuple) > 1:
                print(f'More than one cohort found associated with {key}. Selecting for legacy criteria. Please check database after upload to ensure accuracy.')
                        
                error_log[key] = [value, 'More than one cohort found for subject in legacy check. Writing with one selected from legacy cohorts, but check database to ensure accuracy.']
                        
                print('Associated cohort codes found:')
                for var in returned_cohort_code_tuple:
                    print(var[0])

                    if var[0] in special_cohorts:
                        returned_cohort_code = var[0]
                        processed_legacy_dict[f'{returned_cohort_code}-{lookup_id}'] = [query_family_id, site_indiv_id, lookup_id, returned_cohort_code]
                    
                    else:
                        error_log[key] = [value, 'More than one cohort found for subject in legacy check, and none found matching legacy conditions. Check your loadfile and the database.']
                        break
            else:
                print(f'No associated cohort was found for {key}.  NIALOAD has been assigned, but check the database and log to assure correctness.')
                returned_cohort_code = 'LOAD'
                error_log[key] = [value, 'No cohort was found for the family of this subject, suggesting it is new. NIALOAD was assigned, but check for correctness.']


        processed_legacy_dict[f'{returned_cohort_code}-{lookup_id}'] = [query_family_id, site_indiv_id, lookup_id, returned_cohort_code]

    callback(processed_legacy_dict)

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
        write_to_database(records_to_database_dict)
    else:
        print('No new records to create.....')

def write_to_database(records_to_database_dict):
    """takes as input a dict of new subject data, generates new ADSP ids, constructs INSERT statements and sends to the 'database_connection' function"""
    
    for key, value in records_to_database_dict.items():
        #need select statement to get id of cohort identifier code, adsp_family_id for site_fam_id, next adsp_indiv_partial_id based on the cohort,
        #next adspid based on the cohort
        site_fam_id = value[0]
        site_indiv_id = value[1]
        if not family_data_creation:
            lookup_id = site_indiv_id
            subject_type = 'case/control'
        else:
            lookup_id = value[2]
            subject_type = 'family'

        cohort_identifier_code = value[3]

        id_prefix = database_connection(f"SELECT DISTINCT adsp_id_leading_letter FROM cohort_identifier_codes WHERE cohort_identifier_code = '{cohort_identifier_code}'")[0][0]

        ## initialized as NA, will change if fam is switched on
        adsp_family_id = 'NA'

        ## get cohort id
        retrieved_cohort_id = database_connection(f"SELECT DISTINCT id FROM cohort_identifier_codes WHERE cohort_identifier_code = '{cohort_identifier_code}'")
        for row in retrieved_cohort_id:
            cohort_identifier_code_key = row[0]

        ## get adsp_family_id based on site_fam_id AND the cohort retrieved above, or flag if none exists, IF family id switch is True
        if family_data_creation:
            if create_family_ids:
                retrieved_fam_id = database_connection(f"SELECT DISTINCT adsp_family_id FROM generated_ids WHERE site_fam_id = '{site_fam_id}' AND cohort_identifier_code_key = '{cohort_identifier_code_key}'")
                if len(retrieved_fam_id) > 0:
                    for row in retrieved_fam_id:
                        adsp_family_id = row[0]   
                else:
                    print(f'there seems to be no adsp_family_id found associated with site family id {site_fam_id}. Please check the database')
                    # error_log[key] = [value, 'No adsp_family_id was found for this subject's site_family_id']
                    make_fam_id = input('Do you want to generate a new ADSP_family_id for this site_family_id?(y/n)')
                    if(make_fam_id == 'y'):
                        print(f'making fam id, finding last made family id for {cohort_identifier_code}')
                        retrieved_adsp_family = database_connection(f"SELECT adsp_family_id FROM lookup WHERE cohort_identifier_code = 'LOAD' AND adsp_family_id != 'NULL' AND adsp_family_id != 'NA' ORDER BY adsp_family_id DESC LIMIT 1")

                        if retrieved_adsp_family[0][0] == 'NULL':
                            make_first_fam_id = input('There are no existing family ids for this cohort.  Do you want to create the first one?(y/n) ')
                            if make_first_fam_id == 'y':
                                # need to check valid length here and re-call, then assign as adsp_family_id
                                adsp_family_id = create_first_family_id()

                            else:
                                error_log[key] = [value, 'There were no adsp_family_ids for this cohort and user did not wish to create new one.']
                                continue
                        else:
                            print(f'An adsp_family_id was returned as last made for {cohort_identifier_code}')
                            most_recent_family_id = retrieved_adsp_family[0][0]

                            prefix = most_recent_family_id[:2]
                            id_numeric_end = len(most_recent_family_id)-1
                            incremental = int(most_recent_family_id[2:id_numeric_end])+1
                            print('New family id:')
                            print(f'{prefix}{str(incremental).zfill(4)}F')
                            adsp_family_id = f'{prefix}{str(incremental).zfill(4)}F'
                
                    else:
                        print('No adsp family id will be created. "NA" will be assigned')
                        adsp_family_id = "NA"
            else:
                adsp_family_id = "NA"
        ## `builder_lookup` ignores validity flag when looking for the latest adsp_partial_id created, so doesnt duplicate one that was created and made not valid
                                                
        # qstring = f"SELECT adsp_indiv_partial_id FROM builder_lookup WHERE cohort_identifier_code = '{cohort_identifier_code}' order by createdat DESC, adsp_indiv_partial_id DESC LIMIT 1"
        qstring = f"SELECT adsp_indiv_partial_id FROM last_partial_by_cohort WHERE cohort_identifier_code = '{cohort_identifier_code}'"
        retrieved_partial = database_connection( qstring )

        if len(retrieved_partial) < 1:
            print(f"No adsp_indiv_partial found associated with {cohort_identifier_code}.")
            make_first_indiv_partial = input(f"Do you want to create the first individual id for {cohort_identifier_code} (y/n) ")
            if make_first_indiv_partial == 'y':
                if adsp_family_id is not 'NA':
                    adsp_indiv_partial_id = f'{adsp_family_id[:2]}{str("1").zfill(6)}'
                else:
                    adsp_indiv_partial_id = f'{get_indiv_id_prefix(cohort_identifier_code)}{str("1").zfill(6)}'
                    
                adsp_id = f'{id_prefix}-{cohort_identifier_code}-{adsp_indiv_partial_id}'

                database_connection(f"INSERT INTO generated_ids (site_fam_id, site_indiv_id, cohort_identifier_code_key, lookup_id, adsp_family_id, adsp_indiv_partial_id, adsp_id, subject_type) VALUES ('{site_fam_id}','{site_indiv_id}',{cohort_identifier_code_key},'{lookup_id}','{adsp_family_id}','{adsp_indiv_partial_id}','{adsp_id}','{subject_type}')")
                success_id_log.append(adsp_id)

            else:   
                error_log[key] = [value, f'Error: No indiv_partial was returned when queried for cohort code: {cohort_identifier_code}, and the user chose not to create the first id for the cohort. No record was created.']
                continue
        else:
            for row in retrieved_partial:
                last_partial_created = row[0]
            
            prefix = database_connection(f"SELECT DISTINCT adsp_generated_ids_prefix FROM cohort_identifier_codes WHERE cohort_identifier_code = '{cohort_identifier_code}'")[0][0]

            # incremental = int(last_partial_created[2:])+1
            incremental = int( last_partial_created[ len( prefix ): ] ) + 1

            adsp_indiv_partial_id = f'{ prefix }{str( incremental ).zfill( 6 ) }'

            adsp_id = f'{ id_prefix }-{ cohort_identifier_code }-{ adsp_indiv_partial_id }'

            database_connection(f"INSERT INTO generated_ids (site_fam_id, site_indiv_id, cohort_identifier_code_key, lookup_id, adsp_family_id, adsp_indiv_partial_id, adsp_id, subject_type) VALUES ('{site_fam_id}','{site_indiv_id}',{cohort_identifier_code_key},'{lookup_id}','{adsp_family_id}','{adsp_indiv_partial_id}','{adsp_id}','{subject_type}')")
            success_id_log.append(adsp_id)

def create_first_family_id():
    """takes no input, returns new family id construction based on user input"""
    
    def prompt_for_prefix():
        while True:
            try:
                prefix_input = input("Enter two-letter code that will serve as first two characters of the new family_id...")

            except ValueError:
                continue

            if len(prefix_input) is not 2:
                print('Please enter two letters for prefix.')
                continue
            else:        
                break

        return prefix_input.upper()
    
    first_adsp_family_id = f'{prompt_for_prefix()}{str("1").zfill(4)}F'
    
    return first_adsp_family_id

def get_indiv_id_prefix(cohort_identifier_code):
    while True:
        try: 
            prefix_input = input(f"Enter two-letter code that will serve as first two characters of new adsp_ids for {cohort_identifier_code}...")
        except ValueError:
            continue
        if len(prefix_input) is not 2:
            print('please enter two letters for prefix.')
            continue
        else:
            break

    return prefix_input

def generate_errorlog():
    """creates error log and writes to 'log_files' directory"""
    if len(error_log) > 0:
        date = datetime.date.today()
        time = datetime.datetime.now().strftime("%H:%M:%S")
        f = open(f'./log_files/{ date }-{ time }-log.txt', 'w+')
        f.write(f'{str(len(error_log.items()))} flag(s) raised in runtime. See details below: \n\n')
        for key, value in error_log.items():
            f.write(f'Error: {value[1]} \n')
            f.write(f'family_site_id: {value[0][0]}\n')
            f.write(f'indiv_site_id: {value[0][1]}\n')
            f.write(f'combined_site_id: {value[0][2]}\n')
            f.write(f'cohort_identifier_code: {value[0][3]}\n\n')

def generate_success_list():
    """creates a list of successfully created and inserted ADSP IDs"""

    if len(success_id_log) > 0:
        date = datetime.date.today()
        time = datetime.datetime.now().strftime("%H:%M:%S")
        f = open(f'./log_files/success_lists/{ date }-{ time }-generated_ids.txt', 'w+')
        for id in success_id_log:
            if success_id_log.index(id) >= len(success_id_log)-1:
                f.write(id)
            else:
                f.write(id + ', \n')

        f.close()

def generate_DUK_or_1000_checklist( flagged_ids ):
    date = datetime.date.today()
    time = datetime.datetime.now().strftime("%H:%M:%S")
    
    f = open(f'./log_files/{ date }-{ time }-DUK26057-or-1000-checklist.txt', 'w+')
    f.write(f'{ str( len( flagged_ids ) ) } subjects from DUK26057 or *-1000 family: \n\n')

    for key, value in flagged_ids.items():
        f.write(f'family_site_id: {value[0]}\n')
        f.write(f'indiv_site_id: {value[1]}\n')
        f.write(f'cohort_identifier_code: {value[2]}\n\n')

def DUK26057_and_1000_special_flag( flagged_ids ):
    """tages dict of flagged ids/data, asks user to check and either continue or exit program"""

    while True:
        try:
            if len( flagged_ids ) > 5:
                generate_DUK_or_1000_checklist( flagged_ids )
                notice_input = input(
                    f"{ len( flagged_ids ) } subject(s) with DUK26057 or *-1000 family_ids are in loadfile. A file has been generated containing these subjects data.  Please check for correctness.  Do you want to continue with ID generation? (selecting 'no' will exit program). (y/n) "
                )
            else:
                notice_input = input(
                    f"The load file contains { len( flagged_ids ) } subject(s) from MIA with either family_id = DUK26057 or ending in '-1000'. Please check the following ids for correctness: { str( [ f for f in flagged_ids.keys() ] ).translate({ord(i): None for i in '[]'}) }.  Do you want to continue the script (no will exit the program)? (y/n)"
                )
        except ValueError:
            continue

        if notice_input in ['y', 'Y', 'yes', 'Yes', 'YES']:
            print( "ID generation will continue..." )
            time.sleep( 2.5 )
            return

        elif notice_input in ['n', 'N', 'no', 'No', 'NO']:
            print( "Program will now exit." )
            sys.exit()
        else:
            print("Please input a valid entry. ")
            continue

def alert_last_created_id():
    """no args, no return. Returns last created adsp_indiv_partial_id by cohort"""
    cohort_identifier_codes = [ x[ 0 ].lower() for x in database_connection( "SELECT cohort_identifier_code FROM cohort_identifier_codes" ) ]
    while True:
        try:
            cohort_input = input( f"What cohort are you generating ids for? ( enter cohort identifier code ). " )
        except ValueError:
            continue
        if cohort_input.lower() not in cohort_identifier_codes:
            print( f"{ cohort_input.upper() } is not a cohort in the database.  Please try again." ) 
            continue
        else:
            qstring = f"SELECT adsp_indiv_partial_id FROM last_partial_by_cohort WHERE cohort_identifier_code = '{cohort_input.upper()}'"
            last_partial_created = database_connection( qstring )[ 0 ][ 0 ]
            print( f"The last adsp_indiv_partial_id created for { cohort_input.upper() } was { last_partial_created }. " )
            break

if __name__ == '__main__':
    main()
    generate_errorlog()
    generate_success_list()
    print('Script done processing new ids.  Check error and success logs, and database to ensure accuracy and completeness.')