/*DROP AND RECREATE*/
DROP VIEW IF EXISTS lookup;
DROP VIEW IF EXISTS builder_lookup;
DROP VIEW IF EXISTS lookup_cc;
DROP VIEW IF EXISTS lookup_fam;
DROP VIEW IF EXISTS lookup_aliases;

/*Views creation*/

	/*create lookup view to be able to filter ids by identifier code for cohort*/

		CREATE VIEW lookup AS
		SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, cohort_identifier_codes.cohort_identifier_code, lookup_id, adsp_family_id, adsp_indiv_partial_id, comments, subject_type
		FROM generated_ids
		JOIN cohort_identifier_codes
		ON generated_ids.cohort_identifier_code_key = cohort_identifier_codes.id WHERE "valid" = TRUE;

	/*create lookup view with no valid filter for checker script*/

		CREATE VIEW builder_lookup AS
		SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, cohort_identifier_codes.cohort_identifier_code, lookup_id, adsp_family_id, adsp_indiv_partial_id, comments, subject_type
		FROM generated_ids
		JOIN cohort_identifier_codes
		ON generated_ids.cohort_identifier_code_key = cohort_identifier_codes.id;

		--select * from lookup where identifier_code = 'VAN';
	
	/*create view to filter by case/control subjects*/
	CREATE VIEW lookup_cc AS
	SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, cohort_identifier_codes.cohort_identifier_code, lookup_id, adsp_family_id, adsp_indiv_partial_id, comments, subject_type
		FROM generated_ids
		JOIN cohort_identifier_codes
		ON generated_ids.cohort_identifier_code_key = cohort_identifier_codes.id WHERE "subject_type" = 'case/control' AND "valid" = TRUE;
		
	/*create view to filter by family subjects*/
	CREATE VIEW lookup_fam AS
	SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, cohort_identifier_codes.cohort_identifier_code, lookup_id, adsp_family_id, adsp_indiv_partial_id, comments, subject_type
		FROM generated_ids
		JOIN cohort_identifier_codes
		ON generated_ids.cohort_identifier_code_key = cohort_identifier_codes.id WHERE "subject_type" = 'family' AND "valid" = TRUE;
		
	/*create view to generated table of records in generated_ids that have associated alias ids*/
	/*need to spell out the fields because some duplicate*/
	CREATE VIEW lookup_aliases AS
	SELECT alias_site_indiv_id AS alias_id, generated_ids.adsp_id AS adsp_id, site_fam_id, cohort_identifier_codes.cohort_identifier_code, lookup_id, adsp_family_id, valid, subject_type FROM alias_ids
		JOIN generated_ids ON alias_ids.adsp_id=generated_ids.adsp_id
		JOIN cohort_identifier_codes ON generated_ids.cohort_identifier_code_key=cohort_identifier_codes.id;