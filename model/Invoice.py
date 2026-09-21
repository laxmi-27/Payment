
import config
import mysql.connector

# ------------------- Helper Functions -------------------
def clear_results(cursor):
    """Consume all stored results to prevent cursor issues."""
    for r in cursor.stored_results():
        r.fetchall()

def fetch_one(cursor):
    """Fetch first row from stored results."""
    for result in cursor.stored_results():
        return result.fetchone()
    return None

def fetch_all(cursor):
    """Fetch all rows from stored results."""
    data = []
    for result in cursor.stored_results():
        data.extend(result.fetchall())
    return data

def get_numeric_values(data):
    """Return numeric fields for invoices safely."""
    return [
        float(data.get('basic_amount') or 0),
        float(data.get('debit_amount') or 0),
        float(data.get('after_debit_amount') or 0),
        float(data.get('amount') or 0),
        float(data.get('gst_amount') or 0),
        float(data.get('tds_amount') or 0),
        float(data.get('sd_amount') or 0),
        float(data.get('on_commission') or 0),
        float(data.get('hydro_testing') or 0),
        float(data.get('gst_sd_amount') or 0),
        float(data.get('final_amount') or 0),
    ]

def execute_db_operation(operation_func):
    """General DB operation wrapper with commit/rollback."""
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        result = operation_func(cursor)
        connection.commit()
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


# ------------------- Village Functions -------------------
def get_village_id(village_name):
    def operation(cursor):
        cursor.callproc("GetVillageIdByName", (village_name,))
        return fetch_one(cursor)
    return execute_db_operation(operation)

def get_all_villages():
    def operation(cursor):
        cursor.callproc("GetAllVillages")
        return fetch_all(cursor)
    return execute_db_operation(operation)

 
# ------------------- Invoice Functions -------------------
def insert_invoice(data, village_id):
    def operation(cursor):

        cursor.callproc('SaveInvoice', [
            data.get('pmc_no'),
            village_id,
            data.get('work_type'),
            data.get('invoice_details'),
            data.get('invoice_date'),
            data.get('invoice_no'),
            *get_numeric_values(data),
            data.get('subcontractor_id'),
            0,  # is_extra
            0   # sort_order
        ])
        invoice_id = None
        for result in cursor.stored_results():
            row = result.fetchone()
            if row:
                invoice_id = row['invoice_id']

        return invoice_id

    return execute_db_operation(operation)

def get_all_invoice_details():
    def operation(cursor):
        cursor.callproc('GetAllInvoiceDetails')
        return fetch_all(cursor)
    return execute_db_operation(operation)

def get_invoice_by_id(invoice_id):
    def operation(cursor):
        cursor.callproc('GetInvoiceDetailsById', [invoice_id])
        invoice = fetch_one(cursor)

        cursor.callproc('GetHoldAmountsByInvoiceId', [invoice_id])
        hold_amounts = fetch_all(cursor)

        if invoice:
            invoice["hold_amounts"] = hold_amounts
        return invoice
    return execute_db_operation(operation)

def update_invoice(data, invoice_id):
    def operation(cursor):
        cursor.callproc("GetVillageIdByName", (data.get('village'),))
        village = fetch_one(cursor)
        if not village:
            raise Exception("Village not found")
        village_id = village['Village_Id']

        cursor.callproc('UpdateInvoice', [
            data.get('pmc_no'),
            village_id,
            data.get('work_type'),
            data.get('invoice_details'),
            data.get('invoice_date'),
            data.get('invoice_no'),
            *get_numeric_values(data),
            invoice_id
        ])
        clear_results(cursor)
    execute_db_operation(operation)


def delete_invoice_data(invoice_id, user_id):
    def operation(cursor):
        # Fetch PMC and Invoice_No from DB
        cursor.callproc('GetInvoicePMCById', (invoice_id,))
        record = {}
        for result in cursor.stored_results():
            record = result.fetchone() or {}
        if not record:
            raise Exception("Invoice not found")

        # Use exact DB keys
        pmc_no = record['PMC_No']
        invoice_no = record['Invoice_No']

        # Delete invoice
        cursor.callproc("DeleteInvoice", (invoice_id,))
        clear_results(cursor)


    execute_db_operation(operation)



# ------------------- Hold Types Functions -------------------
def insert_hold_types(data, invoice_id):
    def operation(cursor):
        hold_types = data.getlist('hold_type[]')
        hold_amounts = data.getlist('hold_amount[]')

        for hold_type, hold_amount in zip(hold_types, hold_amounts):
            if not hold_type:
                continue

            cursor.callproc('GetHoldTypeIdByName', [hold_type])
            hold_type_result = fetch_one(cursor)

            if not hold_type_result:
                cursor.callproc('InsertHoldType', [hold_type, 0])
                cursor.execute("SELECT @_InsertHoldType_1")
                hold_type_id = cursor.fetchone()[0]
            else:
                hold_type_id = hold_type_result['hold_type_id']

            cursor.callproc('InsertInvoiceSubcontractorHold', [
                data.get('subcontractor_id'),
                invoice_id,
                hold_type_id,
                float(hold_amount or 0)
            ])
            clear_results(cursor)
    execute_db_operation(operation)

def get_all_hold_types():
    def operation(cursor):
        cursor.callproc("GetAllHoldTypes")
        return fetch_all(cursor)
    return execute_db_operation(operation)


# ------------------- Contractor Functions -------------------
def search_contractors(sub_query):
    def operation(cursor):
        cursor.callproc('SearchContractorsByName', [sub_query])
        return fetch_all(cursor)
    return execute_db_operation(operation)