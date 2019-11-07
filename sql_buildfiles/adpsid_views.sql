/*Views creation*/

	/*create lookup view to be able to filter ids by identifier code for cohort*/

		CREATE VIEW lookup AS
		SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, identifier_code, site_combined_id, adsp_family_id, adsp_indiv_partial_id
		FROM generated_ids
		JOIN cohort_identifier_codes
		ON generated_ids.cohort_identifier_code = cohort_identifier_codes.id WHERE "valid" = TRUE;

		--select * from lookup where identifier_code = 'VAN';