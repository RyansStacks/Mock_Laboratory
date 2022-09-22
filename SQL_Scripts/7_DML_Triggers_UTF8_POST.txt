/* manager_individual_QC_report Trigger */
CREATE OR REPLACE FUNCTION individual_QC_trig_func()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN

DROP TABLE manager_individual_QC_report ;
DROP MATERIALIZED VIEW  manager_individual_QC;

CREATE MATERIALIZED VIEW manager_individual_QC AS
SELECT row_number() OVER (ORDER BY QC_analytes.QC_level, analytes.analyte_name) AS unique_id,
	QC_values.QC_date,   QC_values.QC_time,    QC_analytes.QC_level, 
	analytes.analyte_name,   QC_values.QC_value,   analytes.units_of_measure, 
	analyzers.make,   analyzers.model,
	   CASE
	   WHEN (QC_values.QC_value > QC_analytes.QC_range_high)
	   THEN 'High'
	   WHEN (QC_values.QC_value < QC_analytes.QC_range_low)
	   THEN 'Low'
	   ELSE 'Normal'
   END alert
FROM  QC_analytes
LEFT OUTER JOIN QC_values
ON QC_analytes.QC_analyte_id =  QC_values.QC_analyte_id
LEFT OUTER JOIN QC_panels
ON QC_analytes.QC_panel_id = QC_panels.QC_panel_id
LEFT OUTER JOIN analytes
ON QC_panels.analyte_id = analytes.analyte_id
LEFT OUTER JOIN analyzers
ON QC_panels.serial_id = analyzers.serial_id;

CREATE TABLE manager_individual_QC_report
AS 
SELECT *
FROM manager_individual_QC 
ORDER BY unique_id;
ALTER TABLE ONLY manager_individual_QC_report
ADD CONSTRAINT manager_individual_QC_report_pk PRIMARY KEY(unique_id );

RETURN NULL;
END;
$$;

CREATE TRIGGER individual_QC_trig
AFTER INSERT ON qc_values
FOR EACH ROW 
EXECUTE PROCEDURE individual_QC_trig_func();

/*  Manager Grouped Q.C. Trigger */
CREATE OR REPLACE FUNCTION grouped_QC_trig_func()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN

DROP TABLE manager_grouped_QC_report ;
DROP MATERIALIZED VIEW  manager_grouped_QC;

CREATE MATERIALIZED VIEW manager_grouped_QC AS
SELECT row_number() OVER (ORDER BY qc_level, analyte_name) AS unique_id,
			qcp.qc_level,
			analytes.analyte_name,
			qcp.mean,
			qcp.sd,
			analytes.units_of_measure,
			analyzers.make,
			analyzers.model	
	FROM analytes, analyzers,
	(SELECT *
	FROM QC_panels,
	(SELECT *
	FROM QC_analytes,
	(SELECT QC_values.QC_analyte_id,
		ROUND(AVG(QC_values.QC_value),1) as Mean,
		ROUND(STDDEV_SAMP(QC_values.QC_value),1) as SD
	FROM QC_values
	RIGHT OUTER JOIN QC_analytes
	ON QC_analytes.QC_analyte_id = QC_values.QC_analyte_id
	GROUP BY QC_values.QC_analyte_id) AS agg
	WHERE QC_analytes.qc_analyte_id = agg.qc_analyte_id) as qca
	WHERE qca.qc_panel_id = QC_panels.qc_panel_id) as qcp
	WHERE qcp.analyte_id = analytes.analyte_id 
		AND qcp.serial_id = analyzers.serial_id
	ORDER BY qcp.qc_level;

CREATE TABLE manager_grouped_QC_report
AS 
SELECT *
FROM manager_grouped_QC 
ORDER BY unique_id;
ALTER TABLE ONLY manager_grouped_QC_report
ADD CONSTRAINT  manager_grouped_QC_report_pk PRIMARY KEY(unique_id );

RETURN NULL;
END;
$$;

CREATE TRIGGER grouped_QC_trig
AFTER INSERT ON qc_values
FOR EACH ROW 
EXECUTE PROCEDURE grouped_QC_trig_func();

