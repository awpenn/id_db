import psycopg2
import csv
from dotenv import load_dotenv
import os

current_records = []
new_records = []

def main():
    load_dotenv()
    DBIP = os.getenv('DBIP')
    DBPASS = os.getenv('DBPASS')
    DBPORT = os.getenv('DBPORT')
    DB = os.getenv('DB')
    DBUSER = os.getenv('DBUSER')
    
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
        print('select statement from database')
        cursor.execute("SELECT * FROM lookup")
        current_records = cursor.fetchall()

        create_dict()

    except (Exception, psycopg2.Error) as error :
        print('Error in database connection', error)

    finally:
        if(connection):
            cursor.close()
            connection.close()
            print('database connection closed')

def create_dict(): 
    current_records_dict = {}
    new_records_dict = {}
    legacy_check_dict = {}
    special_cohorts = ['NCRD'] #change this when figure out what the fams are

    def combine_new_and_legacy_dicts(processed_legacy_dict):
        print(processed_legacy_dict)
        
        
        # compare(current_records_dict, new_records_dict)
    for row in current_records:
        #mostly just for reference to variables in the cr dict
        table_id = row[0]
        adspid = row[1]
        site_fam = row[2]
        site_indiv_id = row[3]
        cohort = row[4]
        site_combined_id = row[5]
        
        current_records_dict[f'{cohort}-{site_combined_id}'] = row

    with open('./source_files/new_ids.csv', mode='r', encoding='utf-8-sig') as csv_file:
        new_records = csv.reader(csv_file)

        for row in new_records:
            print('this is a row from the csv')
            site_fam_id = row[0]
            site_indiv_id = row[1]
            site_combined_id = row[2]
            cohort = row[3]
            if cohort in special_cohorts:
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
            # compare(current_records_dict, new_records_dict)

def legacy_check(legacy_check_dict, callback):
    print('leg check hit')
    callback('callback returns to ofunc')

def compare(current_records_dict, new_records_dict):
    records_to_database_dict = {}
    for key, value in new_records_dict.items():
        try:
            if current_records_dict[key]:
                print(f'record exists for: {current_records_dict[key]}')
        except:
            print(f'new record will be created for {key}')
            records_to_database_dict[key] = new_records_dict[key]
    
    if len(records_to_database_dict) > 0:
        write_to_database(records_to_database_dict)
    else:
        print('No new records to create.....')
def write_to_database(records_to_database_dict):
    for key, value in records_to_database_dict.items():
        #need select statement to get id of cohort identifier code, adsp_family_id for site_fam_id, next adsp_indiv_partial_id based on the cohort,
        #next adspid based on the cohort
        site_fam_id = value[0]
        site_combined_id = value[2]
        site_indiv_id = value[1]
        cohort_identifier = value[3]
    
        # #get cohort id
        cursor = connection.cursor()
        cursor.execute(f"SELECT DISTINCT id FROM cohort_identifier_codes WHERE identifier_code = '{cohort_identifier}'")
        retrieved_cohort_id = cursor.fetchall()   
        for row in retrieved_cohort_id:
            cohort_identifier_id = row[0]

        cursor.execute(f"SELECT DISTINCT adsp_family_id FROM generated_ids WHERE site_fam_id = '{site_fam_id}'")
        retrieved_fam_id = cursor.fetchall()
        for row in retrieved_fam_id:
            adsp_family_id = row[0]     

        cursor.execute(f"SELECT adsp_indiv_partial_id FROM lookup WHERE identifier_code = '{cohort_identifier}' ORDER BY adsp_indiv_partial_id DESC LIMIT 1")
        retrieved_partial = cursor.fetchall()
        for row in retrieved_partial:
            last_partial_created = row[0]
        
        prefix = last_partial_created[:2]
        incremental = int(last_partial_created[2:])+1

        adsp_indiv_partial_id = f'{prefix}{str(incremental).zfill(6)}'

        adsp_id = f'A-{cohort_identifier}-{adsp_indiv_partial_id}'

        cursor.execute(f"INSERT INTO generated_ids (site_fam_id, site_indiv_id, cohort_identifier_code, site_combined_id, adsp_family_id, adsp_indiv_partial_id, adsp_id) VALUES ('{site_fam_id}','{site_indiv_id}',{cohort_identifier_id},'{site_combined_id}','{adsp_family_id}','{adsp_indiv_partial_id}','{adsp_id}')")
        connection.commit()

if __name__ == "__main__":
    main()