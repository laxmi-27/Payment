# -- end hold types controlller --------------------

# Route to display the HTML form
@app.route('/add_work_order', methods=['GET'])
def add_work_order():
    # Add database connection
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT Contractor_id, Contractor_Name FROM subcontractors")  # Adjust table/column names as needed
    subcontractor = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('add_work_order.html', subcontractor=subcontractor)  # This is your HTML form page


# Route to handle form submission (from action="/submit_work_order")
@app.route('/submit_work_order', methods=['POST', 'GET'])
def submit_work_order():
    vendor_name = request.form['vendor_name']
    work_order_type = request.form['work_order_type']
    work_order_amount = request.form['work_order_amount']
    boq_amount = request.form['boq_amount']
    work_done_percentage = request.form['work_done_percentage']
    work_order_number = request.form['work_order_number']
    gst_amount = request.form['gst_amount']
    tds_amount = request.form['tds_amount']
    security_deposite = request.form['security_deposite']
    sd_against_gst = request.form['sd_against_gst']
    final_total = request.form['final_total']
    tds_of_gst = request.form['tds_of_gst']
    LogHelper.log_action("Submit Work Order", f"User {current_user.id} Submit Work Order'{  work_order_type}'")
    # print("Good Morning How are U")
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # print("Good morning and how are you")
    insert_query = """
        INSERT INTO work_order 
        (vendor_name, work_order_type, work_order_amount, boq_amount, work_done_percentage,work_order_number,gst_amount,tds_amount
        ,security_deposit,sd_against_gst,final_total,tds_of_gst)
        VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(insert_query,
                   (vendor_name, work_order_type, work_order_amount, boq_amount, work_done_percentage, work_order_number
                    , gst_amount, tds_amount, security_deposite, sd_against_gst, final_total, tds_of_gst))
    connection.commit()

    # ✅ Fetch all data after insert
    select_query = "SELECT * FROM work_order"
    cursor.execute(select_query)
    wo = cursor.fetchall()
    # print("The Work order data is ",wo)
    print("The data from work order ", wo)  # should now print the data properly
    cursor.execute("SELECT Contractor_id, Contractor_Name FROM subcontractors")  # Adjust table/column names as needed
    subcontractor = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('add_work_order.html', work_order_type=work_order_type, wo=wo, subcontractor=subcontractor)


@app.route('/delete_work_order/<int:id>', methods=['POST'])
def delete_work_order(id):
    connection = config.get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM work_order WHERE work_order_id = %s", (id,))
    connection.commit()
    cursor.close()
    connection.close()
    LogHelper.log_action("delete Work Order", f"User {current_user.id} delete Work Order'{  id}'")
    return jsonify({'success': True})


@app.route('/update_work_order/<int:id>', methods=['GET', 'POST'])
def update_work_order(id):
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        work_order_type = request.form['work_order_type']
        work_order_amount = request.form['work_order_amount']
        boq_amount = request.form['boq_amount']
        work_done_percentage = request.form['work_done_percentage']
        work_order_number = request.form['work_order_number']
        gst_amount = request.form['gst_amount']
        tds_amount = request.form['tds_amount']
        security_deposite = request.form['security_deposite']
        sd_against_gst = request.form['sd_against_gst']
        final_amount = request.form['final_amount']
        tds_of_gst = request.form['tds_of_gst']
        update_query = """
            UPDATE work_order 
            SET work_order_type = %s,
                work_order_amount = %s,
                boq_amount = %s,
                work_done_percentage = %s,
                work_order_number= %s,
                gst_amount = %s,
                tds_amount= %s,
                security_deposite= %s,
                sd_against_gst=%s,
                final_amount= %s,
                tds_of_gst=%s
            WHERE work_order_id = %s
        """
        cursor.execute(update_query, (
        work_order_type, work_order_amount, boq_amount, work_done_percentage, work_order_number, gst_amount,
        tds_amount, security_deposite, sd_against_gst, final_amount, tds_of_gst, id))
        connection.commit()
        cursor.close()
        connection.close()

    # If GET request: fetch the existing record
    cursor.execute("SELECT * FROM work_order WHERE work_order_id = %s", (id,))
    work_order = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('update_work_order.html', work_order=work_order)


# Optional: Route to show a success message
@app.route('/success')
def success():
    return "Work Order Submitted Successfully!"


