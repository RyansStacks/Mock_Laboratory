/* updates charges after */
CREATE OR REPLACE FUNCTION orders_charges_trig_func()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN
INSERT INTO charges
 SELECT nextval('charges_sequence') as charge_id, 
 new.panel_id,
 new.order_id, 
 new.customer_id
  FROM orders, charges_sequence
  ORDER BY new.order_id desc
  LIMIT 1;
RETURN NULL;
END;
$$;

CREATE TRIGGER orders_charges
AFTER INSERT ON orders
FOR EACH ROW 
EXECUTE PROCEDURE orders_charges_trig_func();



/*  updates customer tests after insert into orders*/
CREATE OR REPLACE FUNCTION orders_tests_trig_func()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN
INSERT INTO customer_tests 
SELECT  nextval('customer_tests_sequence') as test_id,
 o.employee_id,
 a.analyte_id,
 o.order_id,
ROUND(a.analyte_mean::numeric + (random()/2)::numeric, 1) AS result,
 o.result_date,
 o.result_time
 FROM(SELECT 
floor(random()*(100035-100000+1))+100000 as employee_id,
 orders.order_id,
orders.panel_id,
orders.order_date as result_date,
 orders.order_time as result_time
  FROM orders, customer_tests_sequence
  ORDER BY orders.order_id desc
  LIMIT 1) as o
LEFT OUTER JOIN
(SELECT analytes.panel_id, 
analytes.analyte_id, 
analytes.analyte_mean 
 FROM panels
LEFT OUTER JOIN analytes
 ON panels.panel_id = analytes.panel_id) as a
ON o.panel_id = a.panel_id;
RETURN NULL;
END;
$$;
CREATE TRIGGER orders_tests 
AFTER INSERT ON orders
FOR EACH ROW 
EXECUTE PROCEDURE orders_tests_trig_func();



 /*   updates samples table after insert into orders */
CREATE OR REPLACE FUNCTION orders_samples_trig_func()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN

INSERT INTO samples
 SELECT nextval('samples_sequence') as barcode_id, 
 NEW.order_id, 
 floor(random()*(100040-100000+1))+100000 as employee_id,
 NEW.customer_id,
NEW.order_date as collection_date,
 orders.order_time as collection_time
  FROM orders, samples_sequence
  ORDER BY NEW.order_id desc
  LIMIT 1;
RETURN NULL;
END;
$$;
CREATE TRIGGER orders_samples
AFTER INSERT ON orders
FOR EACH ROW 
EXECUTE PROCEDURE orders_samples_trig_func();

/* Collector Container Trigger */
CREATE OR REPLACE FUNCTION collector_containers_trig_func()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN

DROP TABLE collector_containers ;
DROP MATERIALIZED VIEW  collector_containers_view;

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

RETURN NULL;
END;
$$;

CREATE TRIGGER collector_containers_trig
AFTER INSERT ON samples
FOR EACH ROW 
EXECUTE PROCEDURE collector_containers_trig_func();

/*  Customer Charges Trigger */
CREATE OR REPLACE FUNCTION customer_charges_trig_func()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN

DROP TABLE customers_individual_charges;
DROP MATERIALIZED VIEW customers_charges_discrete;

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


RETURN NULL;
END;
$$;

CREATE TRIGGER customer_charges_trig
AFTER INSERT ON charges
FOR EACH ROW 
EXECUTE PROCEDURE customer_charges_trig_func();

/*  Customer Grouped Charges  Trigger */
CREATE OR REPLACE FUNCTION customer_grouped_charges_trig()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN

DROP TABLE customer_grouped_charges;
DROP MATERIALIZED VIEW customer_charges_grouped;

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

RETURN NULL;
END;
$$;

CREATE TRIGGER customer_charges_grouped_trig
AFTER INSERT ON charges
FOR EACH ROW 
EXECUTE PROCEDURE customer_grouped_charges_trig();

/* Customer Reports Trigger */
CREATE OR REPLACE FUNCTION  customer_reports_trig()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN

DROP MATERIALIZED VIEW IF EXISTS report_GFR; 
DROP TABLE IF EXISTS report_GFR_table; 
DROP MATERIALIZED VIEW IF EXISTS report_alerts;
DROP TABLE IF EXISTS report_alerts_table;
DROP TABLE IF EXISTS customer_reports;

/* Calculate GFR */
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


CREATE TABLE report_GFR_table 
AS 
SELECT * FROM report_GFR ;
		
/* create table with alerts relative to customer results (+/- 2SD)*/

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


CREATE TABLE report_alerts_table
AS SELECT * FROM report_alerts;
/* merge two tables into one final customer report */
UPDATE report_alerts_table
SET result = report_GFR_table.gfr
FROM report_GFR_table
WHERE report_alerts_table.analyte_name = 'GFR'
AND report_GFR_table.order_id = report_alerts_table.order_id;

CREATE TABLE customer_reports
AS 
SELECT *
FROM report_alerts_table
ORDER BY unique_id;

ALTER TABLE ONLY customer_reports 
ADD CONSTRAINT customer_reports_pk PRIMARY KEY(unique_id );

RETURN NULL;
END;
$$;

CREATE TRIGGER  customer_reports_trig
AFTER INSERT ON customer_tests
FOR EACH ROW 
EXECUTE PROCEDURE  customer_reports_trig();






