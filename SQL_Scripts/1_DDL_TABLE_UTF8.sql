CREATE TABLE analyzers(
serial_id		varchar
	NOT NULL 
	CHECK (serial_id in ('SN100000','SN100100','SN100300','SN100200')),
make 		varchar
	NOT NULL CHECK(make <>'') 
	CHECK (make in ('Roche', 'ACL', 'Sysmex')),
model		varchar
	NOT NULL CHECK(model <>'') 
	CHECK (model in ('Cobas_C', 'Cobas_I', 'Tops', 'H1000')),
CONSTRAINT analyzers_pkey PRIMARY KEY(serial_id)
);


CREATE TABLE QC_panels(
QC_panel_id	 integer
 	NOT NULL  
	CHECK (QC_panel_id BETWEEN 100000 AND 100027),
analyte_id		integer
	NOT NULL 
	CHECK (analyte_id  BETWEEN 100000 AND 100027),
serial_id		varchar
	NOT NULL CHECK(serial_id <>'') 
CHECK(serial_id in ('SN100000', 'SN100100','SN100300','SN100200')),
panel_id		integer
	NOT NULL 
	CHECK (panel_id BETWEEN 100000 AND 100006),
CONSTRAINT QC_panels_pkey PRIMARY KEY(QC_panel_id)
);



CREATE TABLE QC_analytes(
QC_analyte_id		integer
	NOT NULL 
	CHECK (QC_analyte_id BETWEEN 100000 AND 100081),
QC_panel_id		integer
 	NOT NULL  
	CHECK (QC_panel_id BETWEEN 100000 AND 100027),
QC_level			varchar
	NOT NULL CHECK(QC_level <>'') 
	CHECK (QC_level in ('1','2','3')),
manager_id		varchar
	NOT NULL CHECK(manager_id <>'') 
	CHECK (CAST(manager_id as int) BETWEEN 100000 AND 999999),
QC_range_low		numeric 
	NOT NULL CHECK(CAST(QC_range_low as varchar) <> '') 
	CHECK ( QC_range_low > 0),
QC_mean			numeric 
	NOT NULL CHECK(CAST(QC_mean as varchar) <> '') 
	CHECK ( QC_mean > 0) ,
QC_range_high		numeric 
	NOT NULL CHECK(CAST(QC_range_high as varchar) <> '') 
	CHECK ( QC_range_high > 0),
CONSTRAINT QC_analytes_pkey PRIMARY KEY(QC_analyte_id)
);


CREATE TABLE QC_values(
QC_value_id		integer
	NOT NULL 
	CHECK (QC_value_id  BETWEEN 100000 AND 999999),
QC_analyte_id		integer
	NOT NULL 
	CHECK (QC_analyte_id BETWEEN 100000 AND 100081),
QC_value			numeric 
	NOT NULL CHECK(CAST(QC_value as varchar) <>'') 
	CHECK (QC_value > 0),
QC_date			date 
	NOT NULL CHECK(CAST(QC_date as varchar) <>''),
QC_time			time 
	NOT NULL CHECK(CAST(QC_time as varchar) <>''),
CONSTRAINT QC_values_pkey PRIMARY KEY(QC_value_id)
);


CREATE TABLE containers(
container_id		integer
	NOT NULL 
	CHECK (container_id BETWEEN 1000 AND 1040),
container_type		varchar
	CHECK (container_type in ('tube')),
container_color		varchar
	CHECK (container_color in ('blue','red','lavendar')),
sample_type		varchar
	CHECK (sample_type in ('plasma', 'serum', 'whole blood')),
CONSTRAINT containers_pkey PRIMARY KEY(container_id)
);


CREATE TABLE panels(
panel_id			integer
	NOT NULL 
	CHECK (panel_id  BETWEEN 100000 AND 100007),
panel_name		varchar
	CHECK (panel_name in ('BMP', 'LIVER','RENAL', 'DIABETES', 'LIPID','CBC','COAG')),
container_id		integer
	NOT NULL 
	CHECK (container_id BETWEEN 1000 AND 1040),
panel_charge		numeric 
	NOT NULL CHECK(CAST(panel_charge as varchar) <>'') CHECK ( panel_charge > 0),
CONSTRAINT panels_pkey PRIMARY KEY(panel_id)
);


CREATE TABLE analytes(
analyte_id			integer
	NOT NULL 
	CHECK (analyte_id BETWEEN 100000 AND 100027),
serial_id			varchar
	NOT NULL CHECK(serial_id <>'') 
	CHECK (serial_id in ('SN100000', 'SN100100', 'SN100300', 'SN100200')),
panel_id			integer
	NOT NULL 
	CHECK (panel_id BETWEEN 100000 AND 999999),
analyte_name		varchar
	NOT NULL CHECK(analyte_name <>''),
analyte_mean		numeric  
	NOT NULL CHECK(CAST(analyte_mean as varchar) <>'') ,
analyte_sd			numeric 
	NOT NULL CHECK(CAST(analyte_sd as varchar)<>''),
units_of_measure		varchar
	NOT NULL CHECK(units_of_measure <>'') 
	CHECK (units_of_measure in ('mg/dL', 'sec', 'g/dL', '%', 'U/L', '/mL', 'mmol/L', 'g/L', 'mL/min/1.73 m²')),
CONSTRAINT analytes_pkey PRIMARY KEY(analyte_id)
);


CREATE TABLE orders(
order_id			serial,
customer_id		integer,
panel_id			integer,
order_date		date,
order_time			time,
CONSTRAINT orders_pkey PRIMARY KEY(order_id)
);


CREATE TABLE charges(
charge_id		serial
	NOT NULL 
	CHECK (charge_id BETWEEN 100000 AND 999999),
panel_id		integer
	NOT NULL 
	CHECK (panel_id BETWEEN 100000 AND 999999),
order_id		serial
	NOT NULL 
	CHECK (order_id BETWEEN 100000 AND 999999),
customer_id	integer
	NOT NULL 
	CHECK (order_id BETWEEN 100000 AND 999999)
);


CREATE TABLE customer_tests(
test_id		serial
	NOT NULL 
	CHECK (test_id BETWEEN 100000 AND 999999),
employee_id	integer
	NOT NULL 
	CHECK (employee_id BETWEEN 100000 AND 999999),
analyte_id		integer
 	NOT NULL 
	CHECK (analyte_id BETWEEN 100000 AND 999999),
order_id		integer
	NOT NULL 
	CHECK (order_id BETWEEN 100000 AND 999999),
result		numeric
	NOT NULL CHECK(CAST(result as varchar) <>''),
result_date		date
	NOT NULL CHECK(CAST(result_date as varchar) <>''),
result_time			time 
	NOT NULL CHECK(CAST(result_time as varchar) <>''),
CONSTRAINT customer_tests_pkey PRIMARY KEY(test_id)
);


CREATE TABLE customers(
customer_id		serial,
address_id		serial,
phone_id			serial,
email_id			serial,
first_name			varchar,
last_name			varchar ,
date_of_birth		date,
CONSTRAINT customers_pkey PRIMARY KEY(customer_id)
);


CREATE TABLE samples(
barcode_id		serial
	NOT NULL 
	CHECK (barcode_id BETWEEN 100000 AND 999999),
order_id			integer
	NOT NULL 
	CHECK (order_id BETWEEN 100000 AND 999999),
employee_id		integer
	NOT NULL
	CHECK (employee_id BETWEEN 100000 AND 999999),
customer_id		integer
	NOT NULL
	CHECK (customer_id BETWEEN 100000 AND 999999),
collection_date		date
	NOT NULL CHECK(CAST(collection_date as varchar) <>''),
collection_time		time 
	NOT NULL CHECK(CAST(collection_time as varchar) <>''),
	CONSTRAINT samples_pkey PRIMARY KEY(barcode_id)
);


CREATE TABLE employees(
employee_id		integer
	NOT NULL 
	CHECK (employee_id BETWEEN 100000 AND 999999),
location_site		varchar
	NOT NULL CHECK(location_site <>'')
	CHECK (location_site in ('100541', '100542','100543','100544','100545')),
certification		varchar ,
email_id			integer
	NOT NULL 
	CHECK (email_id BETWEEN 100000 AND 999999),
phone_id			integer
	NOT NULL
	CHECK (phone_id BETWEEN 100000 AND 999999),
address_id		integer
	NOT NULL 
	CHECK (address_id BETWEEN 100000 AND 999999),
record_id			integer
 	NOT NULL
	CHECK (record_id BETWEEN 100000 AND 999999),
manager_id		varchar
	NOT NULL CHECK(manager_id <>'') 
	CHECK(manager_id in ('Not Applicable','100000','100001')),
first_name		varchar 
	NOT NULL CHECK(first_name <>'')
	CHECK (first_name ~ '^[A-Z].*$'),
last_name		varchar
	NOT NULL CHECK(last_name <>'')
	CHECK (last_name ~ '^[A-Z].*$'),
CONSTRAINT employees_pkey PRIMARY KEY(employee_id)
);


CREATE TABLE managers(
manager_id		varchar
	NOT NULL CHECK(manager_id <>'') 
	CHECK (manager_id in ('100000', '100001', 'Not Applicable' )),
CONSTRAINT managers_pkey PRIMARY KEY(manager_id)
);


CREATE TABLE employment_records(
record_id		integer
	NOT NULL
	CHECK (record_id BETWEEN 100000 AND 999999),
department	varchar
	CHECK (department in ('specimen collection','laboratory')),
salary		numeric 
	NOT NULL CHECK(CAST(salary as varchar) <>'') 
	CHECK (salary > 20000),
CONSTRAINT employment_record_pkey PRIMARY KEY(record_id)
);


CREATE TABLE addresses(
address_id		serial 	NOT NULL 
CHECK (address_id BETWEEN 100000 AND 999999),
street_number		varchar 	NOT NULL ,
street_name		varchar 	NOT NULL, 
street_suffix		varchar 	NOT NULL, 
city				varchar 	NOT NULL, 
state				varchar 	NOT NULL ,
zip				varchar 	NOT NULL ,
CONSTRAINT address_pkey PRIMARY KEY(address_id)
);


CREATE TABLE email_addresses(
email_id		serial		NOT NULL 
CHECK (email_id BETWEEN 100000 AND 999999),
email			varchar	NOT NULL ,
CONSTRAINT email_pkey PRIMARY KEY(email_id)
);
	

CREATE TABLE phone_numbers(
phone_id			serial 	NOT NULL
CHECK (phone_id BETWEEN 100000 AND 999999),
phone_number		varchar,
CONSTRAINT phone_number_pkey PRIMARY KEY(phone_id)
);


