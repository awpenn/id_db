--fdw/foreign table setup for nacc connection
CREATE EXTENSION postgres_fdw;

CREATE SERVER nacc_link FOREIGN DATA WRAPPER postgres_fdw OPTIONS (hostaddr '127.0.0.1', dbname '[DB_NAME]');

CREATE USER MAPPING FOR database_administrator
SERVER nacc_link
OPTIONS (user 'database_administrator', password '[PASS]');

CREATE USER MAPPING FOR manager
SERVER nacc_link[
OPTIONS (user 'manager', password '[PASS]');

CREATE USER MAPPING FOR viewer
SERVER nacc_link
OPTIONS (user 'viewer', password '[PASS]');

CREATE USER MAPPING FOR test_user
SERVER nacc_link
OPTIONS (user 'test_user', password '[PASS]');

CREATE USER MAPPING FOR test_user
SERVER nacc_link
OPTIONS (user 'tester', password '[PASS]');

CREATE SCHEMA nacc_linked;

CREATE FOREIGN TABLE nacc_linked
    (id integer,
    nacc_id text, 
    gwas_round text, 
    exome_round text, 
    whole_exome_round text, 
    whole_genome_round text,
    apoe text, 
    center_access_gwas boolean, 
    center_access_exomechip boolean, 
    center_access_wes boolean, 
    center_access_wgs boolean, 
    investigator_access_adgc_gwas boolean,
    investigator_access_adgc_exomechip boolean, 
    niagads_gwas_round text, 
    niagads_exomechip_round text, 
    niagads_whole_exome_round text, 
    niagads_whole_genome_round text) 

SERVER nacc_link
OPTIONS (schema_name 'public', table_name 'nacc_availability_with_rounds');

--fdw/foreign table setup for consentdb connection
CREATE SERVER consent_db_link FOREIGN DATA WRAPPER postgres_fdw OPTIONS (hostaddr '127.0.0.1', dbname '[DB_NAME]');

CREATE USER MAPPING FOR database_administrator
SERVER consent_db_link
OPTIONS (user 'database_administrator', password '[PASS]');

CREATE USER MAPPING FOR manager
SERVER consent_db_link[
OPTIONS (user 'manager', password '[PASS]');

CREATE USER MAPPING FOR viewer
SERVER consent_db_link
OPTIONS (user 'viewer', password '[PASS]');

CREATE USER MAPPING FOR test_user
SERVER consent_db_link
OPTIONS (user 'test_user', password '[PASS]');

CREATE USER MAPPING FOR test_user
SERVER consent_db_link
OPTIONS (user 'tester', password '[PASS]');

CREATE SCHEMA consent_db_linked;

CREATE FOREIGN TABLE cdb_subjects_cohorts_linked
    (
        subjid text, 
        cohort_name text, 
        resolved_consent_name text,
        institution text, 
        primary_investigator text,
        study_name text, 
        access text, 
        cohort_gsr text,
        file_name text, 
        date_submitted date, 
        note text, 
        gds_consent_description text,
        use_limitation text, 
        irb boolean, 
        pub boolean,
        col boolean, 
        npu boolean, 
        mds boolean, 
        gso boolean, 
        ds_detail text, 
        oth_detail text
    ) 

SERVER consent_db_link
OPTIONS (schema_name 'public', table_name 'subjects_cohorts');

--from by_cohorts table
CREATE FOREIGN TABLE cdb_cohorts_linked
    (
        resolved_consent_name text, 
        resolved_consent_code text, 
        gds_consent_description text,
        cohort_name text, 
        institution text, 
        primary_investigator text, 
        study_name text, 
        access text, 
        cohort_gsr text,
        file_name text, 
        date_submitted date, 
        note text, 
		use_limitation text, 
        irb boolean, 
        pub boolean, 
        col boolean, 
        npu boolean, 
        mds boolean, 
        gso boolean, 
        ds_detail text, 
        oth_detail text
    ) 

SERVER consent_db_link
OPTIONS (schema_name 'public', table_name 'by_cohorts'); 