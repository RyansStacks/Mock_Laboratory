/* Collector Views */
/* Containers Needed */
CREATE MATERIALIZED VIEW collector_containers_view
AS
SELECT row_number() OVER (ORDER BY samples.barcode_id,orders.customer_id) AS unique_id, 
orders.order_id, orders.customer_id, customers.first_name, customers.last_name, 
panels.panel_name, samples.barcode_id, containers.container_type, containers.container_color,
containers.sample_type
FROM orders
LEFT OUTER JOIN panels
ON orders.panel_id = panels.panel_id
LEFT OUTER JOIN containers
ON panels.container_id = containers.container_id
LEFT OUTER JOIN customers
ON orders.customer_id = customers.customer_id
LEFT OUTER JOIN samples
ON samples.order_id = orders.order_id
LEFT OUTER JOIN customer_tests
ON orders.order_id = customer_tests.order_id 
WHERE orders.order_id
NOT IN
(SELECT samples.order_id
FROM samples);

CREATE TABLE collector_containers
AS
SELECT * 
FROM collector_containers_view
ORDER BY unique_id;
ALTER TABLE ONLY collector_containers
ADD CONSTRAINT  collector_containers_pk PRIMARY KEY(unique_id );

/*  Customer Views */

/* Customer Individual Charges */
CREATE MATERIALIZED VIEW customers_charges_discrete
AS
SELECT row_number() OVER (ORDER BY orders.order_id,orders.customer_id) AS unique_id, 
orders.customer_id, orders.order_id, customers.first_name, customers.last_name, panels.panel_charge
FROM orders
LEFT OUTER JOIN panels
ON orders.panel_id = panels.panel_id
LEFT OUTER JOIN customers
ON orders.customer_id = customers.customer_id;

CREATE TABLE customers_individual_charges
AS
SELECT * 
FROM customers_charges_discrete
ORDER BY unique_id;
ALTER TABLE ONLY customers_individual_charges
ADD CONSTRAINT  customers_individual_charges_pk PRIMARY KEY(unique_id );


/*  Customer Grouped Charges */

CREATE MATERIALIZED VIEW customer_charges_grouped
AS
SELECT orders.customer_id, customers.first_name, customers.last_name, SUM(panels.panel_charge)
FROM orders
LEFT OUTER JOIN panels
ON orders.panel_id = panels.panel_id
LEFT OUTER JOIN customers
ON orders.customer_id = customers.customer_id
GROUP BY orders.customer_id, customers.first_name, customers.last_name;

CREATE TABLE customer_grouped_charges
AS
SELECT * 
FROM customer_charges_grouped
ORDER BY customer_id;
ALTER TABLE ONLY customer_grouped_charges
ADD CONSTRAINT  customer_grouped_charges_pk PRIMARY KEY(customer_id );


/* Customer Reports */

/* Calculate GFR */
DROP MATERIALIZED VIEW IF EXISTS report_GFR; 
CREATE MATERIALIZED VIEW report_GFR 
AS
SELECT orders.order_id, analytes.analyte_id,
ROUND(EXTRACT(YEARS FROM AGE(NOW(),customers.date_of_birth))/10 +
	customer_tests.result*10 + 60,1) as GFR
FROM customers
RIGHT OUTER JOIN orders
ON customers.customer_id = orders.customer_id
LEFT OUTER JOIN customer_tests
ON customer_tests.order_id = orders.order_id
LEFT OUTER JOIN analytes
ON analytes.analyte_id = customer_tests.analyte_id
WHERE analytes.analyte_name = 'CREATININE';

DROP TABLE IF EXISTS report_GFR_table; 
CREATE TABLE report_GFR_table 
AS 
SELECT * FROM report_GFR ;
		
/* create table with alerts relative to customer results (+/- 2SD)*/
DROP MATERIALIZED VIEW IF EXISTS report_alerts;
CREATE MATERIALIZED VIEW report_alerts
AS
SELECT row_number() OVER (ORDER BY orders.order_id,orders.customer_id) AS unique_id, 
	orders.order_id,  orders.customer_id, customers.first_name, 
	customers.last_name, analytes.analyte_name, customer_tests.result,
	analytes.units_of_measure, 	customer_tests.result_date, customer_tests.result_time,
	CASE
	WHEN (customer_tests.result - analytes.analyte_mean) > (2*analytes.analyte_sd)
	THEN 'High'
	WHEN (customer_tests.result - analytes.analyte_mean) < (-2*analytes.analyte_sd)
	THEN 'Low'
	ELSE 'Normal'
	END alert
FROM orders
LEFT OUTER JOIN customer_tests
ON customer_tests.order_id = orders.order_id
LEFT OUTER JOIN customers
ON customers.customer_id = orders.customer_id
LEFT OUTER JOIN analytes
ON customer_tests.analyte_id = analytes.analyte_id;


DROP TABLE IF EXISTS report_alerts_table;
CREATE TABLE report_alerts_table
AS SELECT * FROM report_alerts;
		
/* merge two tables into one final customer report */
UPDATE report_alerts_table
SET result = report_GFR_table.gfr
FROM report_GFR_table
WHERE report_alerts_table.analyte_name = 'GFR'
AND report_GFR_table.order_id = report_alerts_table.order_id;


DROP TABLE IF EXISTS customer_reports;
CREATE TABLE customer_reports
AS 
SELECT *
FROM report_alerts_table
ORDER BY unique_id;

ALTER TABLE ONLY customer_reports 
ADD CONSTRAINT customer_reports_pk PRIMARY KEY(unique_id );


/* Missing Tests */
CREATE MATERIALIZED VIEW missing_tests
AS
SELECT orders.order_id,
		customers.customer_id,
		analytes.analyte_name,
		customer_tests.result,
	CASE
	WHEN analytes.analyte_name IS NULL AND customer_tests.result IS NULL
	THEN 'Order Did Not Crossover'
	WHEN analytes.analyte_name IS NOT NULL AND customer_tests.result IS NULL
	THEN 'Test Has Not Yet Resulted'
	ELSE 'Programming Error'
	END explanation
FROM customers
RIGHT OUTER JOIN orders
ON customers.customer_id = orders.customer_id
LEFT OUTER JOIN customer_tests
ON customer_tests.order_id = orders.order_id
LEFT OUTER JOIN analytes
ON analytes.analyte_id = customer_tests.analyte_id
WHERE customer_tests.result is NULL;

CREATE TABLE missing_tests_report
AS
SELECT * 
FROM missing_tests
ORDER BY order_id;
ALTER TABLE ONLY missing_tests_report
ADD CONSTRAINT  missing_tests_report_pk PRIMARY KEY(order_id);



/* Manager Views */
/*  Manager Individual Q.C. */
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



/*  Manager Grouped Q.C. */
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




/* Manager Patient Ranges */
CREATE MATERIALIZED VIEW ranges AS
SELECT 	agg.analyte_name,	
		agg.count as N,
		agg.mean_actual,
		agg.sd_actual,
		analytes.analyte_mean as mean_target,
		analytes.analyte_sd as sd_target,
		analyzers.make,
		analyzers.model
FROM analytes,analyzers,
(SELECT analytes.analyte_name, 
 COUNT(customer_tests.analyte_id),
 ROUND(AVG(customer_tests.result),2) AS mean_actual, 
ROUND(STDDEV_SAMP(customer_tests.result),2) as sd_actual,
analytes.units_of_measure
FROM orders
LEFT OUTER JOIN customer_tests
ON customer_tests.order_id = orders.order_id
LEFT OUTER JOIN analytes
ON customer_tests.analyte_id = analytes.analyte_id
GROUP BY analytes.analyte_name, analytes.units_of_measure) as agg
WHERE agg.analyte_name = analytes.analyte_name
AND analytes.serial_id = analyzers.serial_id;

CREATE TABLE manager_range_report
AS 
SELECT *
FROM ranges 
ORDER BY analyte_name;

ALTER TABLE ONLY manager_range_report
ADD CONSTRAINT  manager_range_report_pk PRIMARY KEY(analyte_name);



