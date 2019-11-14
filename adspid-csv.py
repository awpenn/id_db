import psycopg2
import csv
from dotenv import load_dotenv
import os

import calendar
import time

current_records = []
new_records = []
success_id_log = []
error_log = {}
special_cohorts = ['LOAD', 'RAS', 'UPN'] #change to correct codes for production
g_cohorts = ["KGAD", "NIMH", "ADNI", "CCS"]
load_file = "test.csv"
family_data_creation = False

def main():
    load_dotenv()
    DBIP = os.getenv('DBIP')
    DBPASS = os.getenv('DBPASS')
    DBPORT = os.getenv('DBPORT')
    DB = os.getenv('DB')
    DBUSER = os.getenv('DBUSER')
    global family_data_creation
    
    select_casefam = input("Are you loading family data? (y/n)")
    if select_casefam == 'y':
        family_data_creation = True
        print('family ids will be checked and generated.')
    if select_casefam == 'n':
        print('family ids will not be checked and generated.')




    connect_database(DBIP, DBPASS, DBPORT, DB, DBUSER)

def connect_database(DBIP, DBPASS, DBPORT, DB, DBUSER):
    global current_records
    global connection
    load_dotenv()

    try:
        connection = psycopg2.connect(
                        user = DBUSER,
                        password = DBPASS,
                        host = DBIP,
                        port = DBPORT,
                        database = DB
                    )

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM lookup")

        current_records = cursor.fetchall()
        create_dict()

    except (Exception, psycopg2.Error) as error:
        print('Error in database connection', error)
    

    finally:
        if(connection):
            cursor.close()
            connection.close()
            print('database connection closed')
            generate_errorlog()
            generate_success_list()

def create_dict(): 

    current_records_dict = {}
    new_records_dict = {}
    legacy_check_dict = {}
    global special_cohorts

    def combine_new_and_legacy_dicts(processed_legacy_dict):

        combined_new_records_dict = {**new_records_dict, **processed_legacy_dict}
        compare(current_records_dict, combined_new_records_dict)

    for row in current_records:
        #mostly just for reference to variables in the cr dict
        table_id = row[0]
        adspid = row[1]
        site_fam = row[2]
        site_indiv_id = row[3]
        cohort = row[4]
        site_combined_id = row[5]
        
        current_records_dict[f'{cohort}-{site_combined_id}'] = row

    with open(f'./source_files/{load_file}', mode='r', encoding='utf-8-sig') as csv_file:
        new_records = csv.reader(csv_file)

        for row in new_records:
            site_fam_id = row[0]
            site_indiv_id = row[1]
            ## if looking at family data, make combined id with site_fam_id + site_indiv_id, else is same as indiv_id
            if family_data_creation:
                site_combined_id = f'{site_fam_id}_{site_indiv_id}'
            else:
                site_combined_id = site_indiv_id
            cohort = row[2]
            
            row.insert(2, site_combined_id)
            ## add conditional to check case/fam switch selected at beginning
            if cohort in special_cohorts and family_data_creation:
                if '26_' in site_fam_id or '26-' in site_fam_id:
                    legacy_check_dict[f'{cohort}-{site_combined_id}'] = row
                else:
                    new_records_dict[f'{cohort}-{site_combined_id}'] = row
            else:
                new_records_dict[f'{cohort}-{site_combined_id}'] = row

    if len(legacy_check_dict) > 0:

        legacy_check(legacy_check_dict, combine_new_and_legacy_dicts)
    
    else:
        print('none to special check')
        compare(current_records_dict, new_records_dict)

def legacy_check(legacy_check_dict, callback):
    print('legacy check hit')
    print(legacy_check_dict)
    # -legacy_check dict passed to function that looks for cohort identifiers associated with family id (insert check for only one associated)
    # -[will] build dict of subject info objects to be compared as usual, but with appropriate cohort identifier attached

    processed_legacy_dict = {}
    for key, value in legacy_check_dict.items():
        query_family_id = value[0]
        site_indiv_id = value[1]
        site_combined_id = value[2]
        cohort = value[3]

        cursor = connection.cursor()
        cursor.execute(f"SELECT DISTINCT identifier_code FROM lookup WHERE site_fam_id = '{query_family_id}'")
        returned_cohort_code_tuple = cursor.fetchall()
        print(f'length of tuple returned for family_id {query_family_id} fetch is {len(returned_cohort_code_tuple)}')

        if len(returned_cohort_code_tuple) == 1 :
            returned_cohort_code = returned_cohort_code_tuple[0][0]

        else:
            if len(returned_cohort_code_tuple) > 1:
                print(f"More than one cohort found associated with {key}. Selecting for legacy criteria. Please check database after upload to ensure accuracy.")
                        
                error_log[key] = [value, "More than one cohort found for subject in legacy check. Writing with one selected from legacy cohorts, but check database to ensure accuracy."]
                        
                print("Associated cohort codes found:")
                for var in returned_cohort_code_tuple:
                    print(var[0])

                    if var[0] in special_cohorts:
                        returned_cohort_code = var[0]
                        processed_legacy_dict[f'{returned_cohort_code}-{site_combined_id}'] = [query_family_id, site_indiv_id, site_combined_id, returned_cohort_code]
                    
                    else:
                        error_log[key] = [value, "More than one cohort found for subject in legacy check, and none found matching legacy conditions. Check your loadfile and the database."]
                        break
            else:
                print(f'No associated cohort was found for {key}.  NIALOAD has been assigned, but check the database and log to assure correctness.')
                returned_cohort_code = 'LOAD'
                error_log[key] = [value, "No cohort was found for the family of this subject, suggesting it is new. NIALOAD was assigned, but check for correctness."]


        processed_legacy_dict[f'{returned_cohort_code}-{site_combined_id}'] = [query_family_id, site_indiv_id, site_combined_id, returned_cohort_code]

    callback(processed_legacy_dict)

def compare(current_records_dict, new_records_dict):
    print('compare function hit')
    records_to_database_dict = {}
    for key, value in new_records_dict.items():
        try:
            if current_records_dict[key]:
                print(f'record exists for: {current_records_dict[key]}')

                error_log[key] = [value, "A record for this subject already exists in the database. Check the database and your loadfile for correctness."]

        except:
            print(f'new record will be created for {key}')

            records_to_database_dict[key] = new_records_dict[key]
    
    if len(records_to_database_dict) > 0:
        print(records_to_database_dict)
        write_to_database(records_to_database_dict)
    else:
        print('No new records to create.....')

def write_to_database(records_to_database_dict):
    for key, value in records_to_database_dict.items():
        #need select statement to get id of cohort identifier code, adsp_family_id for site_fam_id, next adsp_indiv_partial_id based on the cohort,
        #next adspid based on the cohort
        site_fam_id = value[0]
        site_indiv_id = value[1]
        if not family_data_creation:
            site_combined_id = site_indiv_id
            subject_type = 'case/control'
        else:
            site_combined_id = value[2]
            subject_type = 'family'

        cohort_identifier = value[3]

        if cohort_identifier in g_cohorts:
            id_prefix = "G"
        else:
            id_prefix = "A"



        ## initialized as 0, will change if fam is switched on
        adsp_family_id = 0

        ## get cohort id
        cursor = connection.cursor()
        cursor.execute(f"SELECT DISTINCT id FROM cohort_identifier_codes WHERE identifier_code = '{cohort_identifier}'")
        retrieved_cohort_id = cursor.fetchall()
        for row in retrieved_cohort_id:
            cohort_identifier_id = row[0]

        ## get adsp_family_id or flag if none exists, IF family id switch is True
        if family_data_creation:
            cursor.execute(f"SELECT DISTINCT adsp_family_id FROM generated_ids WHERE site_fam_id = '{site_fam_id}'")
            retrieved_fam_id = cursor.fetchall()
            if len(retrieved_fam_id) > 0:
                for row in retrieved_fam_id:
                    adsp_family_id = row[0]   
            else:
                print(f'there seems to be no adsp_family_id found associated with site family id {site_fam_id}. Please check the database')
                # error_log[key] = [value, "No adsp_family_id was found for this subject's site_family_id"]
                make_fam_id = input("Do you want to generate a new ADSP_family_id for this site_family_id?(y/n)")
                if(make_fam_id == 'y'):
                    print(f'making fam id, finding last made family id for {cohort_identifier}')
                    cursor.execute(f"SELECT adsp_family_id FROM lookup WHERE identifier_code = '{cohort_identifier}' AND adsp_family_id IS NOT NULL ORDER BY adsp_family_id DESC LIMIT 1")
                    retrieved_adsp_family = cursor.fetchall()
                    
                    if len(retrieved_adsp_family) < 1:
                        print(retrieved_adsp_family)
                        error_log[key] = [value, "Error: Attempted to create new adsp_family_id, but no adsp_family_ids found associated with this cohort."]
                        continue
                    else:
                        print(f'An adsp_family_id was returned as last made for {cohort_identifier}')
                        most_recent_family_id = retrieved_adsp_family[0][0]
                        print(retrieved_adsp_family)
                        prefix = most_recent_family_id[:2]
                        id_numeric_end = len(most_recent_family_id)-1
                        incremental = int(most_recent_family_id[2:id_numeric_end])+1

                        print(f'{prefix}{str(incremental).zfill(4)}F')
                        adsp_family_id = f'{prefix}{str(incremental).zfill(4)}F'
            
                else:
                    continue

        cursor.execute(f"SELECT adsp_indiv_partial_id FROM builder_lookup WHERE identifier_code = '{cohort_identifier}' ORDER BY adsp_indiv_partial_id DESC LIMIT 1")
        retrieved_partial = cursor.fetchall()

        if len(retrieved_partial) < 1:
            print(f"No adsp_indiv_partial found associated with {cohort_identifier}.  Check that you're using the correct cohort identifier code (letter-based). No record will be created.")
            
            error_log[key] = [value, f"Error: No indiv_partial was returned when queried for cohort code: {cohort_identifier}. Check that letter code and not table key is in loadfile."]
        else:

            for row in retrieved_partial:
                last_partial_created = row[0]
            
            prefix = last_partial_created[:2]
            incremental = int(last_partial_created[2:])+1

            adsp_indiv_partial_id = f'{prefix}{str(incremental).zfill(6)}'

            adsp_id = f'{id_prefix}-{cohort_identifier}-{adsp_indiv_partial_id}'

            cursor.execute(f"INSERT INTO generated_ids (site_fam_id, site_indiv_id, cohort_identifier_code, site_combined_id, adsp_family_id, adsp_indiv_partial_id, adsp_id, subject_type) VALUES ('{site_fam_id}','{site_indiv_id}',{cohort_identifier_id},'{site_combined_id}','{adsp_family_id}','{adsp_indiv_partial_id}','{adsp_id}','{subject_type}')")
            connection.commit()
            success_id_log.append(adsp_id)

def generate_errorlog():
    timestamp = calendar.timegm(time.gmtime())
    f = open(f"./log_files/{timestamp}-log.txt", "w+")
    f.write(f"{str(len(error_log.items()))} flag(s) raised in runtime. See details below: \n\n")
    for key, value in error_log.items():
        f.write(f"Error: {value[1]} \n")
        f.write(f'family_site_id: {value[0][0]}\n')
        f.write(f'indiv_site_id: {value[0][1]}\n')
        f.write(f'combined_site_id: {value[0][2]}\n')
        f.write(f'cohort code: {value[0][3]}\n\n')

def generate_success_list():
    timestamp = calendar.timegm(time.gmtime())
    f = open(f"./log_files/success_lists/{timestamp}-generated_ids.txt", "w+")
    for id in success_id_log:
        if success_id_log.index(id) >= len(success_id_log)-1:
            f.write(id)
        else:
            f.write(id + ", ")

    f.close()
if __name__ == "__main__":
    main()