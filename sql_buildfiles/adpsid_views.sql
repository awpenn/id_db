/*DROP AND RECREATE*/
DROP VIEW IF EXISTS lookup;
DROP VIEW IF EXISTS builder_lookup;
DROP VIEW IF EXISTS lookup_cc;
DROP VIEW IF EXISTS lookup_fam;

/*Views creation*/

	/*create lookup view to be able to filter ids by identifier code for cohort*/

		CREATE VIEW lookup AS
		SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, identifier_code AS cohort_identifier_code, site_combined_id, adsp_family_id, adsp_indiv_partial_id, comments, subject_type
		FROM generated_ids
		JOIN cohort_identifier_codes
		ON generated_ids.cohort_identifier_code = cohort_identifier_codes.id WHERE "valid" = TRUE;

	/*create lookup view with no valid filter for checker script*/

		CREATE VIEW builder_lookup AS
		SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, identifier_code AS cohort_identifier_code, site_combined_id, adsp_family_id, adsp_indiv_partial_id, comments, subject_type
		FROM generated_ids
		JOIN cohort_identifier_codes
		ON generated_ids.cohort_identifier_code = cohort_identifier_codes.id;

		--select * from lookup where identifier_code = 'VAN';
	
	/*create view to filter by case/control subjects*/
	CREATE VIEW lookup_cc AS
	SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, identifier_code AS cohort_identifier_code, site_combined_id, adsp_family_id, adsp_indiv_partial_id, comments, subject_type
		FROM generated_ids
		JOIN cohort_identifier_codes
		ON generated_ids.cohort_identifier_code = cohort_identifier_codes.id WHERE "subject_type" = 'case/control' AND "valid" = TRUE;
		
	/*create view to filter by family subjects*/
	CREATE VIEW lookup_fam AS
	SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, identifier_code AS cohort_identifier_code, site_combined_id, adsp_family_id, adsp_indiv_partial_id, comments, subject_type
		FROM generated_ids
		JOIN cohort_identifier_codes
		ON generated_ids.cohort_identifier_code = cohort_identifier_codes.id WHERE "subject_type" = 'family' AND "valid" = TRUE;