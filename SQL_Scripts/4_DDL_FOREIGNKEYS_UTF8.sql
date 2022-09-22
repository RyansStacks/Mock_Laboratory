/* Foreign Keys for Laboratory Database */

/* QC_panels FK */
ALTER TABLE QC_panels
ADD CONSTRAINT QC_panels_analyzers_fkey
FOREIGN KEY (serial_id) 
REFERENCES analyzers (serial_id)
ON DELETE CASCADE;

ALTER TABLE QC_panels
ADD CONSTRAINT QC_panels_analytes_fkey
FOREIGN KEY (analyte_id) 
REFERENCES analytes (analyte_id)
ON DELETE CASCADE;

ALTER TABLE QC_panels
ADD CONSTRAINT QC_panels_panels_fkey
FOREIGN KEY (panel_id) 
REFERENCES panels(panel_id)
ON DELETE CASCADE;

/* QC_analytes FK */
ALTER TABLE QC_analytes
ADD CONSTRAINT QC_analytes_managers_fkey
FOREIGN KEY (manager_id) 
REFERENCES managers(manager_id)
ON DELETE CASCADE;

ALTER TABLE QC_analytes
ADD CONSTRAINT QC_analytes_panels_fkey
FOREIGN KEY (QC_panel_id) 
REFERENCES QC_panels(QC_panel_id)
ON DELETE CASCADE;

/* QC_values FK */
ALTER TABLE QC_values
ADD CONSTRAINT QC_values_QC_analytes_fkey
FOREIGN KEY (QC_analyte_id) 
REFERENCES QC_analytes(QC_analyte_id)
ON DELETE CASCADE;


/* analytes FK */
ALTER TABLE analytes
ADD CONSTRAINT analytes_panels_fkey
FOREIGN KEY (panel_id) 
REFERENCES panels(panel_id)
ON DELETE CASCADE;

ALTER TABLE analytes
ADD CONSTRAINT analytes_analyzers_fkey
FOREIGN KEY (serial_id) 
REFERENCES analyzers(serial_id)
ON DELETE CASCADE;


/* panels FK */
ALTER TABLE panels
ADD CONSTRAINT panels_containers_fkey
FOREIGN KEY (container_id) 
REFERENCES containers(container_id)
ON DELETE CASCADE;


/* charges FK */
ALTER TABLE charges
ADD CONSTRAINT charges_panels_fkey
FOREIGN KEY (panel_id) 
REFERENCES panels(panel_id)
ON DELETE CASCADE;

ALTER TABLE charges
ADD CONSTRAINT charges_orders_fkey
FOREIGN KEY (order_id) 
REFERENCES orders(order_id)
ON DELETE CASCADE;

ALTER TABLE charges
ADD CONSTRAINT charges_customers_fkey
FOREIGN KEY (customer_id) 
REFERENCES customers(customer_id)
ON DELETE CASCADE;

/* customers FK */
ALTER TABLE customers
ADD CONSTRAINT customers_addresses_fkey
FOREIGN KEY (address_id) 
REFERENCES addresses(address_id)
ON DELETE CASCADE;

ALTER TABLE customers
ADD CONSTRAINT customers_phone_numbers_fkey
FOREIGN KEY (phone_id) 
REFERENCES phone_numbers(phone_id)
ON DELETE CASCADE;

ALTER TABLE customers
ADD CONSTRAINT customers_email_addresses_fkey
FOREIGN KEY (email_id) 
REFERENCES email_addresses(email_id)
ON DELETE CASCADE;


/* orders FK */
ALTER TABLE orders
ADD CONSTRAINT orders_panels_fkey
FOREIGN KEY (panel_id) 
REFERENCES panels(panel_id)
ON DELETE CASCADE;

ALTER TABLE orders
ADD CONSTRAINT orders_customers_fkey
FOREIGN KEY (customer_id) 
REFERENCES customers(customer_id)
ON DELETE CASCADE;


/* customer_tests FK */
ALTER TABLE customer_tests
ADD CONSTRAINT customer_tests_employee_fkey
FOREIGN KEY (employee_id) 
REFERENCES employees(employee_id)
ON DELETE CASCADE;

ALTER TABLE customer_tests
ADD CONSTRAINT customer_tests_analytes_fkey
FOREIGN KEY (analyte_id) 
REFERENCES analytes(analyte_id)
ON DELETE CASCADE;

ALTER TABLE customer_tests
ADD CONSTRAINT customer_tests_orders_fkey
FOREIGN KEY (order_id) 
REFERENCES orders(order_id)
ON DELETE CASCADE;

/* samples FK */
ALTER TABLE samples
ADD CONSTRAINT samples_orders_fkey
FOREIGN KEY (order_id) 
REFERENCES orders(order_id)
ON DELETE CASCADE;

ALTER TABLE samples
ADD CONSTRAINT samples_employees_fkey
FOREIGN KEY (employee_id) 
REFERENCES employees(employee_id)
ON DELETE CASCADE;

ALTER TABLE samples
ADD CONSTRAINT samples_customers_fkey
FOREIGN KEY (customer_id) 
REFERENCES customers(customer_id)
ON DELETE CASCADE;


/* employees FK */
ALTER TABLE employees
ADD CONSTRAINT employees_managers_fkey
FOREIGN KEY (manager_id) 
REFERENCES managers(manager_id)
ON DELETE CASCADE;

ALTER TABLE employees
ADD CONSTRAINT employees_email_addresses_fkey
FOREIGN KEY (email_id) 
REFERENCES email_addresses(email_id)
ON DELETE CASCADE;

ALTER TABLE employees
ADD CONSTRAINT employees_phone_numbers_fkey
FOREIGN KEY (phone_id) 
REFERENCES phone_numbers(phone_id)
ON DELETE CASCADE;

ALTER TABLE employees
ADD CONSTRAINT employees_addresses_fkey
FOREIGN KEY (address_id) 
REFERENCES addresses(address_id)
ON DELETE CASCADE;

ALTER TABLE employees
ADD CONSTRAINT employees_employment_records_fkey
FOREIGN KEY (record_id) 
REFERENCES employment_records(record_id)
ON DELETE CASCADE;

