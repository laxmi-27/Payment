
logging.basicConfig(level=logging.DEBUG)


@app.route('/add_purchase_order', methods=['GET', 'POST'])
def add_purchase_order():
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        # Fetch form fields
        purchase_date = request.form.get('purchase_date')
        supplier_name = request.form.get('supplier_name')
        purchase_order_no = request.form.get('purchase_order_no')
        item_name = request.form.get('item_name')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')
        rate = request.form.get('rate')
        amount = request.form.get('amount')
        GST_Amount = request.form.get('GST_Amount')
        TDS = request.form.get('TDS')
        final_amount = request.form.get('final_amount')
        LogHelper.log_action("Add purchase order", f"User {current_user.id} Added puirchase Order'{  purchase_order_no}'")
        # Insert into database
        insert_query = """
            INSERT INTO purchase_order (
                purchase_date, supplier_name, purchase_order_no, item_name, quantity, unit, rate, amount,
                GST_Amount, TDS, final_amount
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            purchase_date, supplier_name, purchase_order_no, item_name, quantity, unit, rate, amount,
            GST_Amount, TDS, final_amount
        ))
        connection.commit()

    # ✅ Always fetch updated data
    cursor.execute("SELECT * FROM purchase_order")
    purchases = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('add_purchase_order.html', purchases=purchases)


# Show all purchases
@app.route('/purchase_orders')
def show_purchase_orders():
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM purchase_order")
    purchases = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('add_purchase_order.html', purchases=purchases)


# Delete purchase order
@app.route('/delete_purchase/<int:id>', methods=['POST'])
def delete_purchase(id):
    connection = config.get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM purchase_order WHERE purchase_id = %s", (id,))
    connection.commit()
    cursor.close()
    connection.close()
    LogHelper.log_action("Delete purchase order", f"User {current_user.id} Deleted puirchase Order'{ id}'")
    return render_template(('add_purchase_order.html'))


# Edit purchase order (form + update logic)
@app.route('/update_purchase/<int:id>', methods=['GET', 'POST'])
def update_purchase(id):
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        # ✅ Form submitted - update all fields
        data = request.form
        cursor.execute("""
            UPDATE purchase_order 
            SET purchase_date = %s,
                supplier_name = %s,
                purchase_order_no = %s,
                item_name = %s,
                quantity = %s,
                unit = %s,
                rate = %s,
                amount = %s,
                GST_Amount = %s,
                TDS = %s,
                final_amount = %s
            WHERE purchase_id = %s
        """, (
            data['purchase_date'], data['supplier_name'], data['purchase_order_no'], data['item_name'],
            data['quantity'],
            data['unit'], data['rate'], data['amount'], data['GST_Amount'], data['TDS'], data['final_amount'],
            id
        ))
        connection.commit()
        cursor.close()
        connection.close()
        LogHelper.log_action("Delete purchase order", f"User {current_user.id} Deleted puirchase Order'{ id}'")
        return redirect(url_for('show_purchase_orders'))

    # Show edit form
    cursor.execute("SELECT * FROM purchase_order WHERE purchase_id = %s", (id,))
    purchase = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('edit_purchase.html', purchase=purchase)


# SHOW all GRNs + ADD form
@app.route('/grn', methods=['GET'])
def grn_page():
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch purchase orders for dropdown
    cursor.execute("SELECT purchase_id, supplier_name FROM purchase_order")
    purchase_orders = cursor.fetchall()

    # Fetch all GRNs to display
    cursor.execute("SELECT * FROM goods_receive_note")
    grns = cursor.fetchall()
    print(grns)
    cursor.close()
    connection.close()

    # Render the template with both datasets
    return render_template('grn_form.html', purchase_orders=purchase_orders, grns=grns)


# ADD new GRN
@app.route('/add_grn', methods=['POST', 'GET'])
def add_grn():
    data = request.form
    connection = config.get_db_connection()
    cursor = connection.cursor()
    query = """
            INSERT INTO goods_receive_note
            (grn_date, purchase_id, supplier_name, item_description, received_quantity, unit, rate, amount, remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
            """
    cursor.execute(query, (
        data.get('grn_date'),
        data.get('purchase_id'),
        data.get('supplier_name'),
        data.get('item_description'),
        data.get('received_quantity'),
        data.get('unit'),
        data.get('rate'),
        data.get('amount'),
        data.get('remarks')
    ))
    connection.commit()

    cursor.execute("SELECT * FROM goods_receive_note")
    grns = cursor.fetchall()
    print(grns)
    query = "select * from purchase_order"
    cursor.execute(query)
    purchase_orders = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('grn_form.html', purchase_orders=purchase_orders, grns=grns)


# UPDATE GRN
@app.route('/update_grn/<int:grn_id>', methods=['GET', 'POST'])
def update_grn(grn_id):
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.form
        query = """
            UPDATE goods_receive_note
            SET grn_date=%s, purchase_id=%s, supplier_name=%s, item_description=%s,
                received_quantity=%s, unit=%s, rate=%s, amount=%s, remarks=%s
            WHERE grn_id=%s
        """
        cursor.execute(query, (
            data['grn_date'], data['purchase_id'], data['supplier_name'],
            data['item_description'], data['received_quantity'], data['unit'],
            data['rate'], data['amount'], data['remarks'], grn_id
        ))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('grns'))

    cursor.execute("SELECT * FROM goods_receive_note WHERE grn_id = %s", (grn_id,))
    grn = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template("edit_grn.html", grn=grn)


# DELETE GRN
@app.route('/delete_grn/<int:grn_id>', methods=['POST'])
def delete_grn(grn_id):
    connection = config.get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM goods_receive_note WHERE grn_id = %s", (grn_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return render_template("grn_form.html")


@app.route('/work_order_report', methods=['GET'])
def work_order_report():
    return render_template('work_order_report.html')




# ✅ Vendor Name Search (for Select2)
@app.route('/get_vendor_names')
def get_vendor_names():
    query = request.args.get('q', '')
    connection = config.get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT vendor_name FROM work_order WHERE vendor_name LIKE %s", (f"%{query}%",))
    vendors = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return jsonify(vendors)


# ✅ Work Order Number Search (with or without vendor)
@app.route('/get_work_order_numbers')
def get_work_order_numbers():
    vendor = request.args.get('vendor_name', '')
    query = request.args.get('q', '')
    connection = config.get_db_connection()
    cursor = connection.cursor()

    if vendor:
        cursor.execute(
            "SELECT DISTINCT work_order_number FROM work_order WHERE vendor_name = %s AND work_order_number LIKE %s",
            (vendor, f"%{query}%"))
    else:
        cursor.execute("SELECT DISTINCT work_order_number FROM work_order WHERE work_order_number LIKE %s",
                       (f"%{query}%",))

    orders = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return jsonify(orders)


# ✅ Get Work Order Data (Filtered)
@app.route('/get_work_order_data')
def get_work_order_data():
    vendor = request.args.get('vendor_name')
    order_number = request.args.get('work_order_number')

    query = "SELECT * FROM work_order WHERE 1=1"
    params = []

    if vendor:
        query += " AND vendor_name = %s"
        params.append(vendor)
    if order_number:
        query += " AND work_order_number = %s"
        params.append(order_number)

    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(data)




@app.route('/download_work_order_report')
def download_work_order_report():
    vendor_name = request.args.get('vendor_name')
    work_order_number = request.args.get('work_order_number')

    if work_order_number == "null":
        work_order_number = None

    query = "SELECT * FROM work_order WHERE 1=1"
    params = []

    if vendor_name:
        query += " AND vendor_name = %s"
        params.append(vendor_name)
    if work_order_number:
        query += " AND work_order_number = %s"
        params.append(work_order_number)

    conn = config.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    if not data:
        return "No data found for the selected filters", 404

    # Convert to DataFrame
    df = pd.DataFrame(data)

    output_path = 'static/downloads/work_order_report.xlsx'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False, startrow=2)  # Leave space for heading

    # Load workbook for styling
    wb = load_workbook(output_path)
    ws = wb.active

    # Add a merged title
    title = "Work Order Report"
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(df.columns))
    title_cell = ws.cell(row=1, column=1)
    title_cell.value = title
    title_cell.font = Font(size=14, bold=True, color="1F4E78")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")

    # Style header row (row 3 because data starts from row 3)
    header_font = Font(bold=True)
    for col_num, column_name in enumerate(df.columns, 1):
        cell = ws.cell(row=3, column=col_num)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        # Optional: adjust column width
        max_length = max(len(str(column_name)), 12)
        ws.column_dimensions[get_column_letter(col_num)].width = max_length + 2

    wb.save(output_path)
    return send_file(output_path, as_attachment=True)


@app.route('/purchase_order_report', methods=['GET'])
def purchase_order_report():
    return render_template('purchase_order_report.html')


@app.route('/get_supplier_names')
def get_supplier_names():
    query = request.args.get('q', '')  # Get the search term from Select2
    connection = config.get_db_connection()
    cursor = connection.cursor()

    # Fetch distinct supplier names that match the search query
    cursor.execute(
        "SELECT supplier_name FROM purchase_order WHERE supplier_name LIKE %s",
        (f"%{query}%",)
    )
    suppliers = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()
    return jsonify(suppliers)


@app.route('/get_purchase_order_numbers')
def get_purchase_order_numbers():
    supplier = request.args.get('supplier_name', '')
    query = request.args.get('q', '')

    connection = config.get_db_connection()
    cursor = connection.cursor()

    if supplier:
        cursor.execute("""
            SELECT purchase_order_no 
            FROM purchase_order 
            WHERE supplier_name = %s AND purchase_order_no LIKE %s
        """, (supplier, f"%{query}%"))
    else:
        cursor.execute("""
            SELECT purchase_order_no 
            FROM purchase_order 
            WHERE purchase_order_no LIKE %s
        """, (f"%{query}%",))

    orders = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return jsonify(orders)


@app.route('/get_purchase_order_data')
def get_purchase_order_data():
    supplier = request.args.get('supplier_name')
    order_no = request.args.get('purchase_order_no')

    query = "SELECT * FROM purchase_order WHERE 1=1"
    params = []

    if supplier:
        query += " AND supplier_name = %s"
        params.append(supplier)
    if order_no:
        query += " AND purchase_order_no = %s"
        params.append(order_no)

    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(data)


@app.route('/download_purchase_order_report')
def download_purchase_order_report():
    supplier_name = request.args.get('supplier_name')
    purchase_order_no = request.args.get('purchase_order_no')

    if purchase_order_no == "null":
        purchase_order_no = None
        LogHelper.log_action("Download purchase order", f"User {current_user.id} Download puirchase Order'{ purchase_order_no}'")
    query = "SELECT * FROM purchase_order WHERE 1=1"
    params = []

    if supplier_name:
        query += " AND supplier_name = %s"
        params.append(supplier_name)
    if purchase_order_no:
        query += " AND purchase_order_no = %s"
        params.append(purchase_order_no)

    conn = config.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    if not data:
        return "No data found for the selected filters", 404

    # Convert to DataFrame
    df = pd.DataFrame(data)

    output_path = 'static/downloads/purchase_order_report.xlsx'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_excel(output_path, index=False, startrow=2)  # Reserve space for heading

    # Load workbook for styling
    wb = load_workbook(output_path)
    ws = wb.active

    # Add a merged title
    title = "Purchase Order Report"
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(df.columns))
    title_cell = ws.cell(row=1, column=1)
    title_cell.value = title
    title_cell.font = Font(size=14, bold=True, color="1F4E78")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")

    # Style header row (row 3 because data starts from row 3)
    header_font = Font(bold=True)
    for col_num, column_name in enumerate(df.columns, 1):
        cell = ws.cell(row=3, column=col_num)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        max_length = max(len(str(column_name)), 12)
        ws.column_dimensions[get_column_letter(col_num)].width = max_length + 2

    wb.save(output_path)
    return send_file(output_path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


