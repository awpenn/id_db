/* Create enum list for subject_type*/
CREATE TYPE "public"."subject_type" AS ENUM('case/control', 'family', 'other');       

/*Create tables for adspid_id database*/

	/*cohort identifier code table*/
	CREATE TABLE IF NOT EXISTS "cohort_identifier_codes" (
		"id" SERIAL NOT NULL,
		"cohort_identifier_code" VARCHAR(10) NOT NULL,
		"full_sitename" VARCHAR(100),
		"description" VARCHAR (100),
		"createdat" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
		PRIMARY KEY ("id")
	);
	
	/*main adspid table*/
	CREATE TABLE IF NOT EXISTS "generated_ids" (
		"id" SERIAL NOT NULL,
			--PK for table
		"site_fam_id" VARCHAR(50) NOT NULL,
			--non-ADSP family id (site specific)
		"site_indiv_id" VARCHAR (50),
			--non-ADSP individual id (site specific)
		"cohort_identifier_code_key" INTEGER REFERENCES "cohort_identifier_codes" ("id")
			ON DELETE SET NULL ON UPDATE CASCADE,
			--FKEY for lettered code assigned to cohort from `cohort_identifier_code` table
		"lookup_id" VARCHAR(50),
			--non-ADSP combined family and individual ids
		"adsp_family_id" VARCHAR(50),
		"adsp_indiv_partial_id" VARCHAR(50),
			--unique part of generated ADSP ID for individual
		"adsp_id" VARCHAR(50) UNIQUE,
		"comments" VARCHAR (500),
		"valid" BOOLEAN NOT NULL DEFAULT TRUE, 
			--boolean indicating whether id is valid.
		"subject_type" "public"."subject_type" DEFAULT 'other',
			--enum list with values case/control, family, and other, indicating subject is member of case/control or family study
		"createdat" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
		PRIMARY KEY("id")
	);
	
	/*create table to manage tracking alias ids for records in generated_ids, ie. when data comes in from site where there are multiple site ids for the same
	subject, one is chosen and given a record in generated_ids, but the other ids still need to be recorded*/

	CREATE TABLE IF NOT EXISTS "alias_ids"(
		"id" SERIAL NOT NULL,
			--PK for table
		"alias_site_indiv_id" VARCHAR(50) NOT NULL,
			--id that doesn't serve as primary site_indiv_id for a record in generated_ids table, but which is still associated with said record as alias id.
		"generated_ids_lookup_id" VARCHAR(50),
			--lookup_id for record in generated_ids to which the alias_site_indiv_id is linked.
		"cohort_identifier_code" VARCHAR(50)
		    --lettered cohort code for subject
	);
	
	/*for testing python, not production*/
	CREATE TABLE "new_ids" (
		"id" SERIAL NOT NULL,
		"site_family_id" VARCHAR(25),
		"site_indiv_id" VARCHAR(25),
		--"site_combined_id" VARCHAR(25),
		--local_id is the combined fam and indiv id
		"cohort" VARCHAR(10),
		PRIMARY KEY ("id")
	);	