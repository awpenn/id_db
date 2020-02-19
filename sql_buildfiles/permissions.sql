--PREVENT TABLE DROPS FOR NONSUPERUSER
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

--BASIC PERMISSIONS FOR MANAGER ROLE
GRANT INSERT, SELECT, UPDATE ON TABLE public.alias_ids TO manager;

GRANT INSERT, SELECT, UPDATE ON TABLE public.cohort_identifier_codes TO manager;

GRANT INSERT, SELECT, UPDATE ON TABLE public.generated_ids TO manager;

GRANT INSERT, SELECT, UPDATE ON TABLE public.sample_ids TO manager;

GRANT SELECT ON public.lookup TO manager;
GRANT SELECT ON public.lookup_aliases TO manager;
GRANT SELECT ON public.lookup_cc TO manager;
GRANT SELECT ON public.lookup_fam TO manager;
GRANT SELECT ON public.subjects_samples TO manager;
GRANT SELECT ON public.subjects_samples_id TO manager;


--MANAGER USAGE FOR SEQUENCES
GRANT USAGE ON SEQUENCE public.alias_ids_id_seq TO manager;

GRANT USAGE ON SEQUENCE public.cohort_identifier_codes_id_seq TO manager;

GRANT USAGE ON SEQUENCE public.generated_ids_id_seq TO manager;

GRANT USAGE ON SEQUENCE public.sample_ids_id_seq TO manager;


--PERMISSIONS FOR VIEWER ROLE
SELECT public.alias_ids TO manager;

SELECT public.cohort_identifier_codes TO manager;

SELECT public.generated_ids TO manager;

SELECT public.sample_ids TO manager;

GRANT SELECT ON public.lookup TO manager;
GRANT SELECT ON public.lookup_aliases TO manager;
GRANT SELECT ON public.lookup_cc TO manager;
GRANT SELECT ON public.lookup_fam TO manager;
GRANT SELECT ON public.subjects_samples TO manager;
GRANT SELECT ON public.subjects_samples_id TO manager;