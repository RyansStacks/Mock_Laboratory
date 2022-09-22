
CREATE SEQUENCE orders_sequence
START 101000
INCREMENT 1;
ALTER TABLE orders
ALTER COLUMN  order_id  
SET DEFAULT nextval('orders_sequence');

CREATE SEQUENCE QC_values_sequence
START 100567
INCREMENT 1;
ALTER TABLE QC_values
ALTER COLUMN  QC_value_id 	
SET DEFAULT nextval('QC_values_sequence');

CREATE SEQUENCE charges_sequence
START 101000
INCREMENT 1;
ALTER TABLE charges
ALTER COLUMN  charge_id	 
SET DEFAULT nextval('charges_sequence');

CREATE SEQUENCE customer_tests_sequence
START 103847
INCREMENT 1;
ALTER TABLE customer_tests
ALTER COLUMN  test_id 
SET DEFAULT nextval('customer_tests_sequence');

CREATE SEQUENCE customers_sequence
START 100500
INCREMENT 1;
ALTER TABLE customers
ALTER COLUMN customer_id 	
SET DEFAULT nextval('customers_sequence');

CREATE SEQUENCE customers_address_sequence
START 100545
INCREMENT 1;
ALTER TABLE customers
ALTER COLUMN  address_id  
SET DEFAULT nextval('customers_address_sequence');
	
CREATE SEQUENCE customers_email_sequence
START 100540
INCREMENT 1;
ALTER TABLE customers
ALTER COLUMN  email_id  
SET DEFAULT nextval('customers_email_sequence');

	
CREATE SEQUENCE customers_phone_sequence
START 100540
INCREMENT 1;
ALTER TABLE customers
ALTER COLUMN  phone_id  
SET DEFAULT nextval('customers_phone_sequence');
	

CREATE SEQUENCE samples_sequence
START 101000
INCREMENT 1;
ALTER TABLE samples
ALTER COLUMN barcode_id 	
SET DEFAULT nextval('samples_sequence');

CREATE SEQUENCE addresses_sequence
START 100545
INCREMENT 1;
ALTER TABLE addresses
ALTER COLUMN  address_id 	
SET DEFAULT nextval('addresses_sequence');

CREATE SEQUENCE email_addresses_sequence
START 100540
INCREMENT 1;
ALTER TABLE email_addresses
ALTER COLUMN  email_id 	
SET DEFAULT nextval('email_addresses_sequence');

CREATE SEQUENCE phone_numbers_sequence
START 100540	
INCREMENT 1;
ALTER TABLE phone_numbers
ALTER COLUMN  phone_id 	
SET DEFAULT nextval('phone_numbers_sequence');
