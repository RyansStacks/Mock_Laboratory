![stockphoto.png]([stockphoto.png](https://github.com/RyansStacks/Mock_Laboratory/blob/main/img/stockphoto.png))

# Clinical Laboratory Database and Stastistical Application Creation

## Background

As an experience data analyst with some data engineering skills, it is apparent that the creation of databases or repositories to properly store data needed for reporting and business needs of stakeholders is crucial.This project aims to demonstrate the skills and techniques needed to create an entity relational database to be used to pull various reports by stakeholders using a basic python application design. The client is a medical laboratory that needs to store information about employees, staff, quality control, and medical test results. An important skill as a data analyst is to be able to obtain the business requirements from a client and translate into technical deliverables. This is a summary of an actual project that highlights high level techniques that have produced a final application.

Note, only a high-level summary for the project is given with code examples that highlight key processes that is represented by a plethora of other code. The complete project with all the code and proposal may be seen at the GitHub repository:

https://github.com/RyansStacks/Mock_Laboratory

## Client Requirements

![ServiceNow](servicenow.png)

Perhaps, your organization utlizes a formal ticket system or you simply get an email from your director that a new project is needed. In this project, we received a ServiceNow ticket from the client. At this point we are given very high level information, but it is imperative to setup a Teams meeting with the client to note the specifics and the laboratory's workflow. This is sometimes called the __Physical Schema__ where we document in flowcharts and annotated dictionaries the real world process of the client that will be used in the project.

### Laboratory Physical Schema

Below, is a flowchart that depicts the very specific entities that will needed to be incorporated into the database. Typically, one may think of an entity as being represented in a table; however, in an entity relational database entities may be further divided into tables in a process called normalization that is explained further on.

![physicalschema.png](physicalschema.png)

## Database Design

### Entity Relational Diagram

The relationships seen in the __Logical Schema__ are formally noted with the idea of __Cardinality__ that describes the relationship of similar instances between two or more tables that will be created. For example, we may decide to create a _Customers_ and _Panels_ tables that share the relationship that customers order one or more panels (groups of medical test). We also note in the opposite direction that one or more panels may belong to many customers. This aforementioned _Many-to-Many_ relationship has formal rule sets in database design where in this situation we may want to create a _Bridge Table_ so that each row in the bridge table will relate to one specific customer order. This is obviously important if we want to track one specific order by a customer. In this case, we create the _Orders_ table to handle this complexity. Reducing complexity of relationships between entities (tables) is a processed called __Normalization__.

![erdiagram.png](erdiagram.png)

### Logical Schema

Building upon the __Physical Schema__, we create what is commonly referred to as a __Logical Schema__ that serves as the centerpiece between the real-world __Physical Schema__ and the actual database tables. Potential tables are listed with relationships between each table. The major question a data analyst is answering is what is the relationship between each table? 

![logicalschema.png](logicalschema.png)

### SQL to Create the Database

SQL contains specific syntax that allows users to create an actual database from a script in a language that is collaboratively called the __Data Definition Language (DDL)__. Tables are specifically created in an entity relational database using a __Primary Key(PK) - Foreign Key (FK) Relationship__ so that a reference table contains a unique set of instances that may be linked to fact table that is seen as the _working table_. This is where the efficiency comes into play with an entity relational database, that we reduce the number of rows that need to be queried by referencing entities when we can. For example, if a lab almost always runs the same set of test, then a _Test Results_ table may only need to link to a table _Test_ that will only contain the unique list of test. This is in comparison to adding the test name itself everytime to the _Test Results_ table where in larger databases this would cause a memory bloat. 

We may describe the linkage using SQL by declaring specific columns as __Foreign Keys__ with corresponding __Primary Keys__ so that we may perform SQL Joins to elicity information from the linked tables as the same time. Also, note we describe the data types of each column as well as any constraints (ie. we may always want specific columns to have data populate when adding data). We may even automate IDs assigned to each table using the `SERIAL` data type in SQL.

#### Creating Table

Below, script to create table that references the analyzers that run the laboratory test. Here, a `CHECK` is placed so that if any new analyzer is entered an alert will populate.

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

#### Creating Foreign Keys

Here QC panels that are run to on analyzers are linked to the _Analyzer_ table via a Primary - Foreign Key constraint.

/* QC_panels FK */
ALTER TABLE QC_panels
ADD CONSTRAINT QC_panels_analyzers_fkey
FOREIGN KEY (serial_id) 
REFERENCES analyzers (serial_id)
ON DELETE CASCADE;

## Advanced SQL Scripts for Dynamic Database Updates

As we add new information to the database via the Python application that we create, we may want to provide a way to automatically update various tables with this information behind the scenes. Luckily, SQL contains advanced functioning using `TRIGGERS` and `FUNCTIONS` that serve to autoperform an operations such as deletions, updates, and new row additions when specific criteria is met. This criteria may occur for example when a new order is placed, subsequent tables may populate with the testing information for the lab technologist to view on their machines so they may know to run the ordered test. Below is an example of a `TRIGGER` used to populate subsequent tables:

First the actual function that will perform the action is created.


```python
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
```

The Trigger is then create using the function above.


```python
CREATE TRIGGER customer_charges_grouped_trig
AFTER INSERT ON charges
FOR EACH ROW 
EXECUTE PROCEDURE customer_grouped_charges_trig();
```

## Using Python to Elicit from Database (API)

Data storage and the use of `TRIGGERS` are excellent in performing data storage and updates; however, when more sophisticated business needed are needed to be answered, one should turn to a programming langauge. For this project, Python is the perfect language for data analytics that may be built _on top off_ the SQL database we created by using an __Application Programming Interface (API)__. The application runs on a server (object) so that the user may phsyically interact with the database by visually viewing different buttons, drop downs, and other objects that may working with data much simpler. We have all used web pages before and an API works nearly identically where the data comes from our database and is displayed specifically in this project within .html files that may be viewed with a web browser such as `Chrome`. The linkage between Python and SQL is handled with a Python library called `Flask` that creates the server object that is needed by the browser to convert the .html code into dynamically viewable pages for the client. 

### API Directory

Below, a classic design for a directory needed for Python Flask to properly run each of the files. 

![directory.png](directory.png)


### Python Code Example

Below, is an excerpt of Python code that is used to elicit data from the database and then create data visualizations used specifically for the client called _Levy-Jenning Plots_. The _Levy-Jennings Plots_ are used to check if quality control values (commerical product that mimics analyte values found in our bodies) are within range. Note, as like most examples demonstrated in this high-level overview, that a multitude of code may be examined at the project `GitHub` repository:

https://github.com/RyansStacks/Mock_Laboratory

All the Python code runs on the Flask object set to the app variable below. 


```python
from flask import Flask

# run with debugger off for deploy
if __name__ == '__main__':
    app.run(debug=False)

# Initiate app
app = Flask(__name__)


from app import views
```

#### Python Code that Creates the Application Views

Each of the Python scripts are linked to the application via a Python decorator `app.route('/missing_tests')`. The `'/missing_tests')` will be the URL in the web appication or an 'address' within a software. 

#### Levy Jennings QC Control Charts with Python

Below, codes used by the laboratory manager to view if quality control values as a table. Using `CSS` or `html` user may manipulate this view with a dropdown. The actual database is cloned as a Python object then converted to a `Pandas` dataframe where any number of data manipulations may be performed. Note, we also have brought in `Seaborn' from Python to create more stunning visualizations on the application.


```python
# QC SCATTER PLOT
@app.route('/qc_scatter_graph', methods=['POST', 'GET'])
def qc_scatter_plot():
    req = request.form
    start = request.form["start_date"]
    end = request.form["end_date"]
    if start > end:
        return 'Please choose a start date prior to an end date!'
    else:
        analytes = req.getlist('analyte_name')
        QC_Values = Base.classes.manager_individual_qc_report
        query = db.session.query(QC_Values).filter(QC_Values.analyte_name.in_(analytes)).filter(
            QC_Values.qc_date.between(start, end)).all()
        columns = []
        keys = QC_Values.__table__.columns
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns.extend(column)
        data = []
        for c in query:
            series = [c.unique_id, c.qc_date, c.qc_time, c.qc_level, c.analyte_name, float(c.qc_value),
                      c.units_of_measure, c.make, c.model, c.alert]
            data.append(series)
        df = pd.DataFrame(data, columns=columns)
        df1 = df[(df['analyte_name'] == analytes[0]) & (df['qc_level'] == str(1))]
        df2 = df[(df['analyte_name'] == analytes[0]) & (df['qc_level'] == str(2))]
        df3 = df[(df['analyte_name'] == analytes[0]) & (df['qc_level'] == str(3))]
        y1 = df1['qc_value']
        y2 = df2['qc_value']
        y3 = df3['qc_value']

        fig, ax = plt.subplots(3, 1, sharex=False, figsize=(12, 8),
                               constrained_layout=True)

        fig.suptitle(analytes[0])

        qc1 = sns.scatterplot(data=df1, x='qc_date', y='qc_value', ax=ax[0])
        qc1.set_title(f"{analytes[0]} QC LEVEL 1")
        qc1.axhline(y1.mean() + (2 * y1.std()),
                    color='green',
                    lw=3,
                    alpha=0.7)
        qc1.axhline(y1.mean() - (2 * y1.std()),
                    color='green',
                    lw=3,
                    alpha=0.7)

        qc2 = sns.scatterplot(data=df2, x='qc_date', y='qc_value', ax=ax[1])
        qc2.set_title(f"{analytes[0]} QC LEVEL 2")
        qc2.axhline(y2.mean() + (2 * y2.std()),
                    color='green',
                    lw=3,
                    alpha=0.7)
        qc2.axhline(y2.mean() - (2 * y2.std()),
                    color='green',
                    lw=3,
                    alpha=0.7)

        qc3 = sns.scatterplot(data=df3, x='qc_date', y='qc_value', ax=ax[2])
        qc3.set_title(f"{analytes[0]} QC LEVEL 3")
        qc3.axhline(y3.mean() + (2 * y3.std()),
                    color='green',
                    lw=3,
                    alpha=0.7)
        qc3.axhline(y3.mean() - (2 * y3.std()),
                    color='green',
                    lw=3,
                    alpha=0.7)

        obj = io.BytesIO()
        fig.savefig(obj, format='png')
        get = obj.getbuffer()
        encoded = base64.b64encode(obj.getbuffer()).decode("utf-8")
        string1 = base64.b64encode(obj.getbuffer()).decode("utf-8")

        return f"<img src='data:image/png;base64,{string1}'/>"
```

#### Dynamic Interplay Between SQL and Python

Using the idea of SQL `TRIGGERS` we can perform more elaborate business functions for the client such as finding all orders that do not have a test result yet. This is strictly handled by SQL table that will populate a special table in the database called _Missing Tests_ in a data warehous fashion. 
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

Then, elicit the data from the Materialized View created above:


```python
#########################################################
# Missing tests
@app.route('/missing_tests')
def missing_tests():
    Missing_Tests = Base.classes.missing_tests_report
    missing_tests_query = db.session.query(Missing_Tests).all()
    # If Query finds a matching customer in DB...
    if len(missing_tests_query) > 0:
        keys = Missing_Tests.__table__.columns
        columns = []
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns.extend(column)
        data = []
        for c in missing_tests_query:
            series = [c.order_id, c.customer_id, c.analyte_name, c.result,
                      c.explanation]
            data.append(series)
        df = pd.DataFrame(data, columns=columns)
        missing_tests_display = df.to_html(index=False)
        del keys, column, columns, series, data, df  # guarantees no cross-over from previous results
    else:
        missing_tests_display = 'You currently do not have have any results at this time!'

    return render_template('missing_tests.html', missing_tests_display=missing_tests_display)
```

## Application

The application serves as the high level representation of the code using buttons, forms, dropdowns, and user friendly GUI based functionalities.

![app.png](app.png)

## Special Considerations

There is are many special considerations that must be given to the project that are key to success. The most important would be the validation process that involves testing specific instances found in both the database and application against a known method. For example, to test the quality control charts and tables, it was possible to compare the quality control values that were actually ran on a specific datetime versus the values that are produced by the application itself. 

Testing the SQL `TRIGGERS` may be performed by injected mock data such as fake orders and then observing if data in expected subsequent tables automatically populated correctly. A video highlighting this process may be found on the `GitHub` repository.

## Summary

First, we demonstrated the proper way to form a classic entity relational database from starting with the client's workflow that may also include several meetings. Using formal diagraming, the complexity of taking such requirements and creating a database may be simplified. The project also highlighted the role SQL and Python plays in developing __Business Solutions__ from a technological standpoint. Various functionalities with both SQL and Python may be used to perform complex task needed for stakeholders. We were able to create a system of orders, data visualizations, barcode scanners (not seen), and reports just with code alone!
