-- drop builder lookup view and recreated with createdat column
DROP VIEW IF EXISTS builder_lookup;
CREATE VIEW builder_lookup AS
	SELECT generated_ids.id AS id, adsp_id, site_fam_id, site_indiv_id, cohort_identifier_codes.cohort_identifier_code, lookup_id, adsp_family_id, adsp_indiv_partial_id, comments, subject_type, generated_ids.createdat as createdat
	FROM generated_ids
	JOIN cohort_identifier_codes
	ON generated_ids.cohort_identifier_code_key = cohort_identifier_codes.id;



-- NEW LAST ID CREATED LOOKUP VIEW
CREATE VIEW last_partial_by_cohort AS
	SELECT cohort_identifier_code, adsp_indiv_partial_id
	FROM 
	generated_ids g
	JOIN (
			SELECT cohort_identifier_code, max(generated_ids.id) AS maxid
			FROM generated_ids
			JOIN cohort_identifier_codes
			ON generated_ids.cohort_identifier_code_key = cohort_identifier_codes.id
			GROUP BY cohort_identifier_code
		) j
	ON g.id = j.maxid
	ORDER BY cohort_identifier_code ASC;

	

-- REDO PERMISSIONS

--PREVENT TABLE DROPS FOR NONSUPERUSER
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

--BASIC PERMISSIONS FOR MANAGER ROLE
GRANT INSERT, SELECT, UPDATE ON TABLE public.alias_ids TO manager;

GRANT INSERT, SELECT, UPDATE ON TABLE public.cohort_identifier_codes TO manager;

GRANT INSERT, SELECT, UPDATE ON TABLE public.generated_ids TO manager;

GRANT INSERT, SELECT, UPDATE ON TABLE public.sample_ids TO manager;

GRANT SELECT ON TABLE public.cdb_subjects_cohorts_linked TO manager;

GRANT SELECT ON TABLE public.nacc_linked TO manager;

GRANT SELECT ON TABLE public.cdb_cohorts_linked TO manager;


GRANT SELECT ON public.lookup TO manager;
GRANT SELECT ON public.builder_lookup TO manager;
GRANT SELECT ON public.lookup_aliases TO manager;
GRANT SELECT ON public.lookup_cc TO manager;
GRANT SELECT ON public.lookup_fam TO manager;
GRANT SELECT ON public.subjects_samples TO manager;
GRANT SELECT ON public.subjects_samples_ids TO manager;

GRANT SELECT ON public.last_partial_by_cohort TO manager;

-- TESTER PERMISSIONS FOR SANDBOX TESTING (ADSPID DB)

GRANT INSERT, SELECT, UPDATE ON TABLE public.alias_ids TO tester;

GRANT INSERT, SELECT, UPDATE ON TABLE public.cohort_identifier_codes TO tester;

GRANT INSERT, SELECT, UPDATE ON TABLE public.generated_ids TO tester;

GRANT INSERT, SELECT, UPDATE ON TABLE public.sample_ids TO tester;



--MANAGER USAGE FOR SEQUENCES
GRANT USAGE ON SEQUENCE public.alias_ids_id_seq TO manager;

GRANT USAGE ON SEQUENCE public.cohort_identifier_codes_id_seq TO manager;

GRANT USAGE ON SEQUENCE public.generated_ids_id_seq TO manager;

GRANT USAGE ON SEQUENCE public.sample_ids_id_seq TO manager;


--PERMISSIONS FOR VIEWER ROLE
GRANT SELECT ON public.alias_ids TO viewer;

GRANT SELECT ON public.cohort_identifier_codes TO viewer;

GRANT SELECT ON public.generated_ids TO viewer;

GRANT SELECT ON public.sample_ids TO viewer;

GRANT SELECT ON TABLE public.cdb_subjects_cohorts_linked TO viewer;

GRANT SELECT ON TABLE public.nacc_linked TO viewer;

GRANT SELECT ON TABLE public.cdb_cohorts_linked TO viewer;

GRANT SELECT ON public.lookup TO viewer;
GRANT SELECT ON public.builder_lookup TO viewer;
GRANT SELECT ON public.lookup_aliases TO viewer;
GRANT SELECT ON public.lookup_cc TO viewer;
GRANT SELECT ON public.lookup_fam TO viewer;
GRANT SELECT ON public.subjects_samples TO viewer;
GRANT SELECT ON public.subjects_samples_ids TO viewer;

GRANT SELECT ON public.last_partial_by_cohort TO viewer;

-- PERMISSIONS FOR ID CHECK AND GENERATE

GRANT SELECT ON TABLE public.cohort_identifier_codes TO adsp_id_generator;

GRANT INSERT, SELECT, UPDATE ON TABLE public.generated_ids TO adsp_id_generator;

GRANT INSERT, SELECT ON TABLE public.sample_ids TO adsp_id_generator;

GRANT USAGE ON SEQUENCE public.generated_ids_id_seq TO adsp_id_generator;

GRANT SELECT ON public.lookup TO adsp_id_generator;
GRANT SELECT ON public.builder_lookup TO adsp_id_generator;
GRANT SELECT ON public.lookup_aliases TO adsp_id_generator;
GRANT SELECT ON public.lookup_cc TO adsp_id_generator;
GRANT SELECT ON public.lookup_fam TO adsp_id_generator;a
GRANT SELECT ON public.subjects_samples TO adsp_id_generator;
GRANT SELECT ON public.subjects_samples_ids TO adsp_id_generator;
GRANT SELECT ON public.last_partial_by_cohort TO adsp_id_generator;