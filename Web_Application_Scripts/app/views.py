from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import scipy.stats
import qrcode
import os
import io
import base64
import seaborn as sns
import matplotlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

# import app from init.py
from app import app


# correct for Heroku mistake of no ql in URI
DATABASE_URI = os.environ['DATABASE_URL']
DATABASE_URI = DATABASE_URI[:8]+'ql' + DATABASE_URI[8:]
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQL_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
# Map schema
Base = automap_base()
Base.prepare(db.engine, reflect=True)

# HOME PAGE
@app.route('/')
def index():
    return render_template("index.html")


# ABOUT THIS PROJECT
@app.route('/about')
def about():
    return render_template("about.html")


# ORDERS
@app.route('/orders')
def orders_home():
    return render_template('orders.html')


@app.route('/place_order', methods=['POST', 'GET'])
def place_orders():
    if request.method == 'GET':
        return 'You must submit the form to access this age'
    if request.method == 'POST':
        complete = request.form
        complete = len(complete)
        if complete < 12:
            return render_template('incorrect.html', display="You have not fully completed the form!")
        else:
            dictionary = request.form
            panels = [k for k, v in dictionary.items() if v == 'on']
            first_name = request.form.get('first_name')
            first_name = first_name.title()
            last_name = request.form.get('last_name')
            last_name = last_name.title()
            date_of_birth = request.form.get('date_of_birth')
            street_number = request.form.get('street_number')
            street_name = request.form.get('street_name').title()
            street_name = street_name.title()
            street_suffix = request.form.get('street_suffix').title()
            city = request.form.get('city')
            city = city.title()
            state = request.form.get('state')
            state = state.title()
            zip_code = request.form.get('zip')
            email = request.form.get('email')
            phone = request.form.get('phone')
            # Is customer in DB?

            Customers1 = Base.classes.customers
            customers1 = db.session.query(Customers1).filter_by(first_name=first_name, last_name=last_name,
                                                                date_of_birth=date_of_birth).count()
            Addresses1 = Base.classes.addresses
            addresses1 = db.session.query(Addresses1).filter_by(street_number=street_number, street_name=street_name,
                                                                street_suffix=street_suffix, city=city, state=state,
                                                                zip=zip_code).count()
            Phone_Numbers1 = Base.classes.phone_numbers
            phone_numbers1 = db.session.query(Phone_Numbers1).filter_by(phone_number=phone).count()

            Email_Addresses1 = Base.classes.email_addresses
            email_addresses1 = db.session.query(Email_Addresses1).filter_by(email=email).count()
            # existing customers (in database under following tables):
            if customers1 > 0 and addresses1 > 0 and phone_numbers1 > 0 and email_addresses1 > 0:
                Customers1 = Base.classes.customers
                customers1 = db.session.query(Customers1.customer_id).filter_by(first_name=first_name,
                                                                                last_name=last_name,
                                                                                date_of_birth=date_of_birth).first()
                customer_id = customers1[0]
                current = datetime.now()
                order_date = current.strftime('%Y-%m-%d')
                order_time = current.strftime('%H:%M:%S')
                Orders1 = Base.classes.orders
                last = db.session.query(Orders1).order_by(Orders1.order_id.desc()).first()
                last = last.order_id + 1

                for panel in panels:
                    orders1 = Orders1(customer_id=customer_id, panel_id=panel, order_date=str(order_date),
                                      order_time=str(order_time))
                    db.session.add(orders1)
                    db.session.commit()

                return render_template('place_orders.html', first_name=first_name, last_name=last_name, id=customer_id,
                                       panels=panels)

            # new customer (must add contact info prior to orders):
            else:
                Customers2 = Base.classes.customers
                customers2 = db.session.query(Customers2.customer_id).order_by(Customers2.customer_id.desc()).first()
                customer_id = customers2[0] + 1  # customer id for new customer equals last row id plus 1

                Email_Addresses2 = Base.classes.email_addresses
                new_email = Email_Addresses2(email=email)
                db.session.add(new_email)
                db.session.commit()

                Phone_Numbers2 = Base.classes.phone_numbers
                new_phone = Phone_Numbers2(phone_number=phone)
                db.session.add(new_phone)
                db.session.commit()

                Addresses2 = Base.classes.addresses
                new_address = Addresses2(street_number=street_number, street_name=street_name,
                                         street_suffix=street_suffix, city=city, state=state, zip=zip_code)
                db.session.add(new_address)
                db.session.commit()

                Customers3 = Base.classes.customers
                new_customer = Customers3(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth)
                db.session.add(new_customer)
                db.session.commit()

                # Create order for new customer or customer with 'changed' contact info:
                current = datetime.now()
                order_date = current.strftime('%Y-%m-%d')
                order_time = current.strftime('%H:%M:%S')

                Orders1 = Base.classes.orders

                for panel in panels:  # dynamically create multiple orders from multiple panes
                    orders1 = Orders1(customer_id=customer_id, panel_id=panel, order_date=order_date,
                                      order_time=order_time)
                    db.session.add(orders1)
                    db.session.commit()

            return render_template('place_orders.html', first_name=first_name, last_name=last_name, id=customer_id,
                                   panels=panels)



# CUSTOMERS VIEWS
# Customer Log-In (precedes Customer View)
@app.route('/customer_login')
def customer_login():
    return render_template('customer_login.html')


# Global
login_id = None


# CUSTOMER DASHBOARD
@app.route('/customer_dashboard', methods=['POST', 'GET'])
def customer_home():
    global login_id
    if request.method == 'GET':
        return customer_login()
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        login_id = customer_id
        Customer = Base.classes.customers
        check = db.session.query(Customer.customer_id).filter_by(customer_id=login_id).count()
        first = db.session.query(Customer.first_name).filter_by(customer_id=login_id).first()
        last = db.session.query(Customer.last_name).filter_by(customer_id=login_id).first()

        if check > 0:
            return render_template('customer_dashboard.html', first=first, last=last)
        else:
            return render_template('incorrect.html',
                                   display='Not Listed: Please contact the IT Department!')


# CUSTOMER CONTACT INFO
@app.route('/contact_info')
def contact_info():
    customer_id = login_id
    # customer contact
    Customers1 = Base.classes.customers
    customers = db.session.query(Customers1).filter_by(customer_id=customer_id).first()

    Customers2 = Base.classes.customers
    address_id = db.session.query(Customers2.address_id).filter_by(customer_id=customer_id).first()

    Customers3 = Base.classes.customers
    phone_id = db.session.query(Customers3.phone_id).filter_by(customer_id=customer_id).first()

    Customers4 = Base.classes.customers
    email_id = db.session.query(Customers4.email_id).filter_by(customer_id=customer_id).first()

    Address = Base.classes.addresses
    address = db.session.query(Address).filter_by(address_id=address_id[0]).first()

    Email = Base.classes.email_addresses
    email = db.session.query(Email).filter_by(email_id=email_id[0]).first()

    Phone = Base.classes.phone_numbers
    phone = db.session.query(Phone).filter_by(phone_id=phone_id[0]).first()

    customer_display1 = f'{customers.first_name} {customers.last_name}'
    customer_display2 = f'{address.street_number}  {address.street_name} {address.street_suffix}'
    customer_display3 = f'{address.city}  {address.state} {address.zip}'
    customer_display4 = f'{phone.phone_number}'
    customer_display5 = f'{email.email}'

    return render_template('contact_info.html', customer_display1=customer_display1,
                           customer_display2=customer_display2,
                           customer_display3=customer_display3,
                           customer_display4=customer_display4,
                           customer_display5=customer_display5)


@app.route('/results_form')
def results_form():
    return render_template('results_form.html')


@app.route('/results', methods=['POST', 'GET'])
def results_dashboard():
    req = request.form
    customer_id = login_id
    analytes = req.getlist('analyte_name')
    alerts = req.getlist('alert')
    start = req["start_date"]
    end = req["end_date"]
    Customer_Reports = Base.classes.customer_reports
    query1 = db.session.query(Customer_Reports).filter_by(customer_id=customer_id).filter(
        Customer_Reports.result_date.between(start, end)).filter(Customer_Reports.analyte_name.in_(analytes)).filter(
        Customer_Reports.alert.in_(alerts)).all()
    if len(query1) > 0:
        columns = []
        keys = Customer_Reports.__table__.columns
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns.extend(column)
        data = []
        for c in query1:
            series = [c.unique_id, c.order_id, c.customer_id, c.first_name, c.last_name,
                      c.analyte_name, float(c.result), c.units_of_measure, c.result_date.strftime("%Y-%m-%d"),
                      c.result_time.strftime('%H:%M'), c.alert]
            data.append(series)

        df = pd.DataFrame(data, columns=columns)
        customer_display1 = df.to_html(index=False)
        return render_template('results_tab.html', customer_results_display=customer_display1)
    else:
        return 'You currently do not have have any results at this time!'


@app.route('/charges')
def charges_dashboard():
    customer_id = login_id
    Individual_Charges = Base.classes.customers_individual_charges
    query2 = db.session.query(Individual_Charges).filter_by(customer_id=customer_id).all()
    # customer individual charges table
    if len(query2) < 1:
        return 'You currently do not have have any charges at this time!'
    else:
        columns = []
        keys = Individual_Charges.__table__.columns
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns.extend(column)
        data = []
        for c in query2:  # c = columns
            series = [c.unique_id, c.customer_id, c.order_id, c.first_name, c.last_name,
                      float(c.panel_charge)]
            data.append(series)
        df = pd.DataFrame(data, columns=columns)
        charges_display1 = df.to_html(index=False)

        # customer grouped charges table
        Grouped_Charges = Base.classes.customer_grouped_charges
        query3 = db.session.query(Grouped_Charges).filter_by(customer_id=customer_id).all()
        columns = []
        keys = Grouped_Charges.__table__.columns
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns.extend(column)
        data = []
        for c in query3:  # c = columns
            series = [c.customer_id, c.first_name, c.last_name,
                      c.sum]
            data.append(series)
        df = pd.DataFrame(data, columns=columns)
        charges_display2 = df.to_html(index=False)

        return render_template('charges.html', charges_display1=charges_display1,
                               charges_display2=charges_display2)


# EMPLOYEES VIEWS
# Employee Log-In (precedes Employee Dashboard)
@app.route('/employee_login')
def employee_login():
    return render_template('employee_login.html')


# Employee Dashboard
@app.route('/employee', methods=['POST', 'GET'])
def employee_dashboard():
    if request.method == 'GET':
        return f"Access Denied: Must Log-In to View This Page!"
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        # Verify employee in database
        Employees = Base.classes.employees
        employee = db.session.query(Employees).filter_by(employee_id=employee_id).count()

        if employee < 1:
            return render_template('incorrect.html',
                                   display='Not Listed: Please contact the IT Department!')
        else:
            return render_template('employee_dashboard.html', employee_display=employee_id)


# COLLECTOR VIEWS
# Collection Tubes  - Displays tubes needed to be drawn per order
@app.route('/collection_tubes')
def collection_containers():
    Collector_Containers = Base.classes.collector_containers
    collector_containers_query = db.session.query(Collector_Containers).all()
    # If Query finds a matching customer in DB...
    if len(collector_containers_query) > 0:
        keys = Collector_Containers.__table__.columns
        columns = []
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns.extend(column)
        data = []
        for c in collector_containers_query:
            series = [c.unique_id, c.order_id, c.customer_id, c.first_name, c.last_name,
                      c.panel_name, c.barcode_id, c.container_type, c.container_color, c.sample_type]
            data.append(series)
        df = pd.DataFrame(data, columns=columns)
        # convert floats from nulls
        bar_list = []
        for bar in df['barcode_id']:
            if "." in str(bar):
                bar = int(bar)
                bar_list.append(bar)
            else:
                bar_list.append('NULL')  # Note this doesn't affect DB only used for app view
        df['barcode_id'] = bar_list

        collection_containers_display = df.to_html(index=False)
        del keys, column, columns, series, data, df  # guarantees no cross-over from previous results
    else:
        collection_containers_display = 'You currently do not have have any samples to collect at this time!'

    return render_template('collection_tubes.html', collection_containers_display=collection_containers_display)


# Enter Order ID for Barcode
@app.route('/print_barcode')
def print_barcode():
    return render_template('print_barcode.html')


# Displays Barcode - Pulls from Missing Test table (test not run)
@app.route('/barcode', methods=['POST', 'GET'])
def barcode():
    if request.method == 'GET':
        return f"Access Denied: Must Log-In to View This Page!"
    if request.method == 'POST':
        order_id = request.form['order_id']
        Samples = Base.classes.samples
        samples = db.session.query(Samples).filter_by(order_id=order_id).all()
        if len(samples) < 1:
            return render_template('incorrect.html',
                                   display="You have entered an invalid or missing order id number!")
        else:
            ### get keys values
            keys = []
            columns = Samples.__table__.columns
            for column in columns:
                column = f'"{column}'.split(".")[1::2]
                keys.extend(column)
            values = []
            for c in samples:  # c = columns
                values = [int(c.barcode_id), c.order_id, c.employee_id, c.customer_id,
                          c.collection_date.strftime("%Y-%m-%d"), c.collection_time.strftime('%H:%M')]
            # create dict to use to display k,v pairs in html
            display_dict = {}
            for k, v in zip(keys, values):
                display_dict[k] = v
            # create the barcode and store in static folder
            qr = qrcode.QRCode(version=1,
                               error_correction=qrcode.constants.ERROR_CORRECT_L,
                               box_size=10,
                               border=2)

            qr.add_data(int(order_id))
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            root = os.path.dirname(os.getcwd())
            path = r'app\static\barcode.png'
            img.save(path)
            display_dict = display_dict

        return render_template('barcode.html', display_dict=display_dict)

# TECH VIEWS

# customer results
@app.route('/customer_results')
def customer_results():
    return render_template('customer_results.html')


# Summary of Patient Range Stats
@app.route('/customer_results_table', methods=['POST', 'GET'])
def customer_results_table():
    if request.method == 'GET':
        return f"Access Denied: Must Log-In to View This Page!"
    if request.method == 'POST':
        req1 = request.form['order_id']
        req2 = request.form['customer_id']
        if len(req1) == 0 and len(req2) == 0:
            customer_results_display = 'Please go back and make a selection!'
        elif len(req1) != 0 and len(req2) != 0:
            customer_results_display = 'Please enter only one field!'
        else:
            if len(req1) > 0:
                Customer_Ranges = Base.classes.customer_reports
                query1 = db.session.query(Customer_Ranges).filter_by(order_id=int(req1)).all()
                if len(query1) == 0:
                    return 'You have entered an invalid ID, Please Try Again!'
                else:
                    columns = []
                    keys = Customer_Ranges.__table__.columns
                    for column in keys:
                        column = f'"{column}'.split(".")[1::2]
                        columns.extend(column)
                    data = []
                    for c in query1:
                        series = [c.unique_id, c.order_id, c.customer_id, c.first_name, c.last_name,
                                  c.analyte_name, float(c.result), c.units_of_measure,
                                  c.result_date.strftime("%Y-%m-%d"),
                                  c.result_time.strftime('%H:%M'), c.alert]
                        data.append(series)
                    df = pd.DataFrame(data, columns=columns)
                    customer_results_display = df.to_html(index=False)
                    del keys, column, columns, series, data, df  # guarantees no cross-over from previous results
            else:
                Customer_Ranges = Base.classes.customer_reports
                query2 = db.session.query(Customer_Ranges).filter_by(customer_id=int(req2)).all()
                if len(query2) > 0:
                    columns = []
                    keys = Customer_Ranges.__table__.columns
                    for column in keys:
                        column = f'"{column}'.split(".")[1::2]
                        columns.extend(column)
                    data = []
                    for c in query2:
                        series = [c.unique_id, c.order_id, c.customer_id, c.first_name, c.last_name,
                                  c.analyte_name, float(c.result), c.units_of_measure,
                                  c.result_date.strftime("%Y-%m-%d"),
                                  c.result_time.strftime('%H:%M'), c.alert]
                        data.append(series)
                    df = pd.DataFrame(data, columns=columns)
                    customer_results_display = df.to_html(index=False)
                    del keys, column, columns, series, data, df  # guarantees no cross-over from previous results

    return render_template('customer_results_tab.html', customer_results_display=customer_results_display)


# Patient Range Form to Select Attributes
@app.route('/patient_ranges')
def customer_ranges_home():
    return render_template('patient_ranges.html')


# Summary of Patient Range Stats
@app.route('/patient_ranges_tab', methods=['POST', 'GET'])
def customer_ranges_table():
    req = request.form
    analytes = req.getlist('analyte_name')
    Patient_Ranges = Base.classes.manager_range_report
    query = db.session.query(Patient_Ranges).filter(Patient_Ranges.analyte_name.in_(analytes)).all()
    columns = []
    keys = Patient_Ranges.__table__.columns
    for column in keys:
        column = f'"{column}'.split(".")[1::2]
        columns.extend(column)
    data = []
    for c in query:
        series = [c.analyte_name, c.n, c.mean_actual, c.sd_actual,
                  c.mean_target, c.sd_target, c.make, c.model]
        data.append(series)
    df = pd.DataFrame(data, columns=columns)
    patient_ranges_tab = df.to_html(index=False)
    del keys, column, columns, series, data, df

    return render_template('patient_ranges_tab.html', analytes=analytes, patient_ranges_tab=patient_ranges_tab)


##################################################
@app.route('/moving_averages')
def moving_averages():
    return render_template('moving_averages.html')


@app.route('/moving_averages_table', methods=['POST', 'GET'])
def moving_averages_tab():
    req = request.form
    if len(req) < 1:
        return 'Please make a select!'
    else:
        analytes_ = req.getlist('analyte_name')
        start = req["start_date"]
        end = req["end_date"]
        Results = Base.classes.customer_reports
        query = db.session.query(Results).filter(Results.analyte_name.in_(analytes_)).filter(
            Results.result_date.between(start, end)).all()

        if len(query) < 0:
            return 'Sorry no results for this selection!'
        else:
            columns = []
            keys = Results.__table__.columns
            for column in keys:
                column = f'"{column}'.split(".")[1::2]
                columns.extend(column)
            data = []
            for c in query:
                series = [c.unique_id, c.order_id, c.customer_id, c.first_name, c.last_name,
                          c.analyte_name, float(c.result), c.units_of_measure,
                          c.result_date.strftime("%Y-%m-%d"),
                          c.result_time.strftime('%H:%M'), c.alert]
                data.append(series)
            df = pd.DataFrame(data, columns=columns)

            # descriptive statistics
            descriptive = pd.pivot_table(df, values=['result'], index=['analyte_name', 'result_date'],
                                         aggfunc={np.mean, np.std, np.min, np.max}).round(2)
            moving_averages_display1 = descriptive.to_html(index=False)

            # smooth moving averages per analyte
            SMA = df.loc[:, ['result_date', 'analyte_name', 'result']]
            SMA['Smooth Moving Average'] = SMA['result'].rolling(5).mean()
            SMA = SMA.loc[:, ['result_date', 'analyte_name', 'Smooth Moving Average']]
            cols = ['analyte_name', 'result_date']
            SMA = SMA.sort_values(by=cols)
            moving_averages_display2 = SMA.to_html(index=False)

            # z_SCORES means vs. expect mean (population - manufacturer)
            # obtain EXPECTED MEANS from database
            Tests = Base.classes.analytes
            query2 = db.session.query(Tests).filter(Tests.analyte_name.in_(analytes_)).all()
            columns = []
            keys = Tests.__table__.columns
            for column in keys:
                column = f'"{column}'.split(".")[1::2]
                columns.extend(column)
            data1 = []
            for a in query2:
                series = [a.analyte_id, a.serial_id, a.panel_id, a.analyte_name,
                          a.analyte_mean, a.analyte_sd, a.units_of_measure]
                data1.append(series)
            df1 = pd.DataFrame(data1, columns=columns)
            df1 = df1.loc[:, ['analyte_name', 'analyte_mean', 'analyte_sd']]
            # df2 = pd.pivot_table(df, values=['result'], index=['analyte_name'],aggfunc={np.mean, np.std}).round(2)
            df2 = df.groupby(df['analyte_name']).result.agg(["mean", 'std']).round(2)
            combined = merged = pd.merge(df1, df2, on='analyte_name', how="inner")
            combined['z_score'] = combined['mean'].astype(float) - combined['analyte_mean'].astype(float)
            combined['p_value'] = combined[['z_score']].applymap(lambda x: scipy.stats.t.sf(abs(x), 1))
            moving_averages_display3 = combined.to_html(index=False)

    return render_template('moving_averages_tab.html', analytes=analytes_,
                           moving_averages_tab2=moving_averages_display2,
                           moving_averages_tab3=moving_averages_display3)


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


# MANAGER VIEWS
# QC INDIVIDUAL RESULTS
@app.route('/qc_values')
def qc_values_home():
    return render_template('qc_values.html')


@app.route('/qc_values_tab', methods=['POST', 'GET'])
def qc_values_tab():
    req = request.form
    start = req["start_date"]
    end = req["end_date"]
    if start > end:
        qc_values_tab = 'Please choose a start date prior to an end date!'
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
            series = [c.unique_id, c.qc_date, c.qc_time, c.qc_level, c.analyte_name, c.qc_value, c.units_of_measure,
                      c.make, c.model, c.alert]
            data.append(series)
        df = pd.DataFrame(data, columns=columns)
        qc_values_tab = df.to_html(index=False)
        del keys, column, columns, series, data, df

    return render_template('qc_values_tab.html', qc_values_tab=qc_values_tab)


# QC CUMULATIVE RESULTS
@app.route('/qc_cumulative')
def qc_individual_home():
    return render_template('qc_cumulative.html')


@app.route('/qc_cumulative_tab', methods=['POST', 'GET'])
def qc_individual_tab():
    req = request.form
    start = request.form["start_date"]
    end = request.form["end_date"]
    if start > end:
        qc_cumulative_tab = 'Please choose a start date prior to an end date!'
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
        df = df.loc[:, ['qc_date', 'qc_level', 'analyte_name', 'qc_value']]
        df = df.pivot_table(values='qc_value', index=['analyte_name', 'qc_level'], aggfunc=['mean', 'std']).round(1)
        df = df.reset_index()
        qc_cumulative_tab = df.to_html(index=False)
        del keys, column, columns, series, data, df

    return render_template('qc_cumulative_tab.html', analytes=analytes, qc_cumulative_tab=qc_cumulative_tab)


# QC CURRENT SUMMARY
@app.route('/qc_summary')
def qc_grouped():
    QC_Summary = Base.classes.manager_grouped_qc_report
    qc_summary_query = db.session.query(QC_Summary).all()
    # If Query finds a matching customer in DB...
    if len(qc_summary_query) > 0:
        keys = QC_Summary.__table__.columns
        columns = []
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns.extend(column)
        data = []
        for c in qc_summary_query:
            series = [c.unique_id, c.qc_level, c.analyte_name, float(c.mean),
                      float(c.sd), c.units_of_measure, c.make, c.model]
            data.append(series)
        df = pd.DataFrame(data, columns=columns)
        qc_summary_display = df.to_html(index=False)
        del keys, column, columns, series, data, df  # guarantees no cross-over from previous results
    else:
        qc_summary_display = 'You currently do not have have any results at this time!'

    return render_template('qc_summary.html', qc_summary_display=qc_summary_display)


# QC VISUALS

# QC SCATTER PLOT FORM
@app.route('/qc_scatter')
def qc_scatter_home():
    return render_template('qc_scatter.html')


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


# QC WESTGARD RULES
@app.route('/westgard')
def westgard_home():
    return render_template('westgard.html')


@app.route('/westgard_table', methods=['POST', 'GET'])
def westgard_table():
    req = request.form
    analyte = req.getlist('analyte_name')
    if len(analyte) < 1:
        return 'Please Make a Selection!'
    else:
        # Create dataframe for qc_analytes table
        QC_Analytes = Base.classes.qc_analytes
        qc_analytes = db.session.query(QC_Analytes).all()
        columns1 = []
        keys = QC_Analytes.__table__.columns
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns1.extend(column)
        data1 = []
        for c in qc_analytes:
            series = [c.qc_analyte_id, c.qc_panel_id, c.qc_level, c.manager_id, float(c.qc_range_low),
                      float(c.qc_mean), float(c.qc_range_low)]
            data1.append(series)
        qc_analytes_df = pd.DataFrame(data1, columns=columns1)

        # Create dataframe for qc_values table
        QC_Values = Base.classes.qc_values
        qc_values = db.session.query(QC_Values).all()
        columns2 = []
        keys = QC_Values.__table__.columns
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns2.extend(column)
        data2 = []
        for c in qc_values:
            series = [c.qc_value_id, c.qc_analyte_id, float(c.qc_value), c.qc_date, c.qc_time]
            data2.append(series)
        qc_values_df = pd.DataFrame(data2, columns=columns2)

        # Create dataframe for qc_analytes table
        Analytes = Base.classes.analytes
        analytes = db.session.query(Analytes).filter(Analytes.analyte_name.in_(analyte)).all()
        columns3 = []
        keys = Analytes.__table__.columns
        for column in keys:
            column = f'"{column}'.split(".")[1::2]
            columns3.extend(column)
        data3 = []
        for c in analytes:
            series = [c.analyte_id, c.serial_id, c.panel_id, c.analyte_name, float(c.analyte_mean),
                      float(c.analyte_sd), c.units_of_measure]
            data3.append(series)
        analytes_df = pd.DataFrame(data3, columns=columns3)

        # merge on foreign key qc_analyte_id
        merge = pd.merge(qc_analytes_df, qc_values_df, how='left', on='qc_analyte_id')
        merge = merge.drop(['manager_id', ], axis=1)
        # to_numpy silences new warning due to change in ufunc behavior
        merge[['Deviation']] = np.subtract(merge[['qc_value']], merge[['qc_mean']].to_numpy())
        merge[['1SD']] = np.subtract(merge[['qc_range_high']], merge[['qc_mean']].to_numpy())
        merge[['1SD']] = np.abs(np.divide(merge[['1SD']], 2))
        merge[['SDI']] = np.divide(merge[['Deviation']], merge[['1SD']].to_numpy())
        zero_df = pd.DataFrame([{'SDI': 0}])
        # add zero to beginning since day1 cant have a difference
        pre = pd.concat([zero_df, merge[['SDI']][1:]], axis=0).reset_index(drop=True)
        post = pd.concat([zero_df, merge[['SDI']][:-1]], axis=0).reset_index(drop=True)
        merge[['DeltaSDI']] = post - pre
        # Creating a Range 4SD (subsequent results 4SD apart)
        merge[['Range4SD Rule']] = merge[['DeltaSDI']].applymap(lambda s: "VIOLATION" if (s > 4 or s < -4) else "OK")
        # Create a 3 SD rule - any results > or < 3SD = violation
        merge[['>3SD Rule']] = merge[['SDI']].applymap(lambda r: "VIOLATION" if (r < -3 or r > 3) else "OK")
        # Create a > 2SD outlier column
        merge[['>2SD Outlier']] = merge[['SDI']].applymap(lambda r: "VIOLATION" if (r < -2 or r > 2) else "OK")
        # Creating a 2-2SD rule column - any two subsequent results > or < (+/-) 2SD but less than (+/-)3SD respectively
        pre_list = pre.iloc[:, 0].tolist()
        post_list = post.iloc[:, 0].tolist()
        outcomes = []
        for pr, po in zip(pre_list, post_list):
            if (pr > 2 and po > 2 and pr < 3 and po < 3) or (pr < -2 and po < -2 and pr > -3 and po > -3):
                outcomes.append("VIOLATION")
            else:
                outcomes.append("OK")
        merge[['2-2SD Rule']] = pd.Series([outcomes])
        # note a qc_panel_id, although confusingly named, corresponds to 1 analyte
        # qc_panel_id is PK for qc_panel which maps an analyte to a panel to clarify
        final = pd.merge(analytes_df, merge, left_on='analyte_id', right_on='qc_panel_id')
        final = final[['qc_date', 'qc_time','analyte_name', 'qc_value','qc_mean', '1SD', 'SDI',
                       'DeltaSDI', '>2SD Outlier','2-2SD Rule', '>3SD Rule', 'Range4SD Rule']]
        display2 = final.to_html(index=False)
        # Finally, create a table that gives the viewer definitions of each rule:
        r_sdi = "Standard Deviation Index (Standard Deviation Units"
        r_delta = "Difference in SDI from previous run"
        r_2sd = " ALl values with SDI > 2 are considered and outlier"
        r_22sd = "If two subsequent runs are: 2SD>SDI<3SD or -2SD>SDI<-3SD in a row"
        r_3sd = "If any value is > (+/-)3SD"
        r_r4s = "If two subsequent values are > (+/-)4SD apart"
        index = ['SDI', 'DeltaSDI', '>2SD Outlier', '2-2SD Rule','>3SD Rule', 'Range4SD Rule']
        definitions = [r_sdi,r_delta,r_2sd,r_22sd, r_3sd,r_r4s]
        columns_ = ["________________________Definitions_____________________________________"]
        rules_df = pd.DataFrame(definitions, index=index, columns=columns_)
        display1 = rules_df.to_html(index=False)

        return render_template('westgard_tab.html', analytes=analytes[0],
                               display1=display1,
                               display2=display2)



