-- On new insert to generated_ids table, 
-- query the table's column names (HARDCODE excluding those with int and bool datatypes),
--go through each column and turn string 'NULL's into actual NULLs
CREATE OR REPLACE FUNCTION cleanup_nulls() 
	RETURNS TRIGGER AS 
		$cleanup_nulls_trigger$
        DECLARE
        _colname TEXT;
		_table_name TEXT;
        BEGIN
		_table_name := TG_ARGV[0];
			for _colname in EXECUTE format('SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = $1 AND data_type = $2') USING _table_name, 'character varying'
				LOOP
					EXECUTE format('UPDATE %I SET %I = NULL WHERE %I = $1', _table_name, _colname, _colname) USING 'NULL';
				END LOOP;
				RETURN NULL;
        END
	
		$cleanup_nulls_trigger$ 
LANGUAGE plpgsql;



--TRIGGER DECLARATIONS
CREATE TRIGGER cleanup_nulls_trigger AFTER INSERT ON generated_ids -- if you make it AFTER UPDATE will loop. 
-- either look into that query-depth thing from consent_base(?) or leave as INSERT(?)
	FOR EACH STATEMENT
	EXECUTE PROCEDURE cleanup_nulls("generated_ids");

CREATE TRIGGER cleanup_nulls_trigger AFTER INSERT ON cohort_identifier_codes -- if you make it AFTER UPDATE will loop. 
	FOR EACH STATEMENT
	EXECUTE PROCEDURE cleanup_nulls("cohort_identifier_codes");

CREATE TRIGGER cleanup_nulls_trigger AFTER INSERT ON alias_ids -- if you make it AFTER UPDATE will loop. 
	FOR EACH STATEMENT
	EXECUTE PROCEDURE cleanup_nulls("alias_ids");

CREATE TRIGGER cleanup_nulls_trigger AFTER INSERT ON sample_ids -- if you make it AFTER UPDATE will loop. 
	FOR EACH STATEMENT
	EXECUTE PROCEDURE cleanup_nulls("sample_ids");