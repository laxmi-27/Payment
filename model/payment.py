import config
import mysql.connector
from model.Utilities import ItemCRUDType


class Paymentmodel:

    @staticmethod
    def get_connection():
        return config.get_db_connection()

    # ----------------------------------------------------------
    # FETCH ALL  (returns list of dicts with Contractor_Name)
    # ----------------------------------------------------------
    @staticmethod
    def fetch_all_payments():
        """Return one unified payment-history list.

        Includes:
          1. Normal invoice payments from ``payment``
          2. GST release records from ``gst_releases``
          3. Hold release records from ``hold_release``

        Release rows are read separately because they are intentionally stored
        outside the normal ``payment`` table.  This is why the old Payment
        History showed only the three invoice-payment UTRs.
        """
        connection = Paymentmodel.get_connection()
        if not connection:
            return []

        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            records = []

            # Existing payment stored procedure preserves the current
            # payment fields (date/status/TDS/etc.) used by the UI.
            cursor.callproc('GetAllPayments')
            for result in cursor.stored_results():
                records = result.fetchall() or []
                break

            for row in records:
                row['Record_Type'] = 'Payment'
                row['Record_Key'] = f"payment:{row.get('Payment_Id')}"

            # GST releases
            cursor.execute(
                """
                SELECT
                    g.GST_Release_Id AS Record_Id,
                    g.PMC_No,
                    g.Invoice_No,
                    g.Final_Amount AS Amount_with_TDS,
                    0 AS TDS_Percentage,
                    0 AS TDS_Payment_Amount,
                    g.Total_Amount AS Amount_after_TDS_Deduction,
                    g.UTR,
                    s.Contractor_Name,
                    NULL AS Payment_Date,
                    'GST Released' AS Payment_Status,
                    COALESCE(g.sort_order, g.GST_Release_Id) AS Sort_Order
                FROM gst_releases g
                LEFT JOIN subcontractors s
                    ON s.Contractor_Id = g.Contractor_ID
                WHERE g.UTR IS NOT NULL AND TRIM(g.UTR) <> ''
                ORDER BY Sort_Order ASC, g.GST_Release_Id ASC
                """
            )
            gst_rows = cursor.fetchall() or []
            for row in gst_rows:
                row['Payment_Id'] = None
                row['Record_Type'] = 'GST Release'
                row['Record_Key'] = f"gst:{row.get('Record_Id')}"
            records.extend(gst_rows)

            # Hold releases.  Include them even when their UTR is blank so
            # the Payment History represents every release record.
            cursor.execute(
                """
                SELECT
                    h.Hold_Release_Id AS Record_Id,
                    h.PMC_No,
                    h.Invoice_No,
                    h.Final_Amount AS Amount_with_TDS,
                    0 AS TDS_Percentage,
                    0 AS TDS_Payment_Amount,
                    h.Total_Amount AS Amount_after_TDS_Deduction,
                    h.UTR,
                    s.Contractor_Name,
                    NULL AS Payment_Date,
                    'Hold Released' AS Payment_Status,
                    h.Hold_Release_Id AS Sort_Order
                FROM hold_release h
                LEFT JOIN subcontractors s
                    ON s.Contractor_Id = h.Contractor_Id
                ORDER BY h.Hold_Release_Id ASC
                """
            )
            hold_rows = cursor.fetchall() or []
            for row in hold_rows:
                row['Payment_Id'] = None
                row['Record_Type'] = 'Hold Release'
                row['Record_Key'] = f"hold:{row.get('Record_Id')}"
            records.extend(hold_rows)

            return records

        except mysql.connector.Error as e:
            print(f"Error fetching unified payment history: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # FETCH BY ID  (returns dict with Contractor_Name + new fields)
    # ----------------------------------------------------------
    @staticmethod
    def fetch_payment_by_id(payment_id):
        connection = Paymentmodel.get_connection()
        if not connection:
            return None
        payment_data = None
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.callproc("GetPaymentById", (payment_id,))
            for result in cursor.stored_results():
                payment_data = result.fetchone()
        except mysql.connector.Error as e:
            print(f"Error fetching payment data: {e}")
        finally:
            if cursor:
                cursor.close()
            connection.close()
        return payment_data

    # ----------------------------------------------------------
    # INSERT PAYMENT
    # ----------------------------------------------------------
    @staticmethod
    def insert_payment(subcontractor_id, pmc_no, invoice_no,
                       amount, tds_percentage, tds_amount, total_amount,
                       utr, payment_date, payment_status):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False

        cursor = None
        try:
            cursor = connection.cursor()
            invoice_id = None

            pmc_no    = int(pmc_no) if pmc_no else None
            invoice_no = invoice_no.strip() if invoice_no else None

            # Step 1: find existing invoice
            if invoice_no:
                cursor.callproc('GetInvoiceId', [subcontractor_id, pmc_no, invoice_no])
                for result in cursor.stored_results():
                    row = result.fetchone()
                    if row:
                        invoice_id = row[0]
                while cursor.nextset():
                    pass

            # Step 2: create placeholder invoice if none found
            if not invoice_id:
                cursor.callproc('InsertInvoiceExtraPayment', [subcontractor_id, pmc_no])
                for result in cursor.stored_results():
                    row = result.fetchone()
                    if row:
                        invoice_id = row[0]
                while cursor.nextset():
                    pass

            if not invoice_id:
                print("ERROR: Invoice ID not found for payment insert")
                return False

            amount_f   = float(amount)         if amount         else 0.0
            tds_pct    = float(tds_percentage) if tds_percentage  else 0.0
            tds_amt_f  = float(tds_amount)     if tds_amount      else 0.0
            total_f    = float(total_amount)   if total_amount    else 0.0
            pay_date   = payment_date          if payment_date    else None
            pay_status = payment_status        if payment_status  else 'Paid'

            cursor.callproc(
                'InsertPayments',
                [pmc_no, invoice_no, amount_f, tds_pct,
                 tds_amt_f, total_f, utr,
                 invoice_id, pay_date, pay_status]
            )
            connection.commit()
            return True

        except Exception as e:
            print(f"Error in insert_payment: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # ----------------------------------------------------------
    # UPDATE PAYMENT
    # ----------------------------------------------------------
    @staticmethod
    def call_update_payment_proc(payment_id, pmc_no, invoice_no,
                                  amount, tds_percentage, tds_amount, total_amount,
                                  utr, payment_date, payment_status):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False
        try:
            cursor = connection.cursor()
            pmc_no_i   = int(pmc_no)           if pmc_no        else None
            amount_f   = float(amount)          if amount        else 0.0
            tds_pct    = float(tds_percentage)  if tds_percentage else 0.0
            tds_amt_f  = float(tds_amount)      if tds_amount    else 0.0
            total_f    = float(total_amount)    if total_amount  else 0.0
            pay_date   = payment_date           if payment_date  else None
            pay_status = payment_status         if payment_status else 'Paid'
            cursor.callproc("UpdatePayment", (
                payment_id, pmc_no_i, invoice_no,
                amount_f, tds_pct, tds_amt_f, total_f,
                utr, pay_date, pay_status
            ))
            connection.commit()
            return True
        except Exception as e:
            print(f"Error updating payment: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # DELETE PAYMENT
    # ----------------------------------------------------------
    @staticmethod
    def delete_payment(payment_id):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False, None, None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('GetPaymentById', [payment_id])
            record = {}
            for result in cursor.stored_results():
                record = result.fetchone() or {}
            if not record:
                return False, None, None
            pmc_no     = record.get('PMC_No')
            invoice_no = record.get('Invoice_No')
            cursor.callproc("DeletePayment", (payment_id,))
            connection.commit()
            return True, pmc_no, invoice_no
        except mysql.connector.Error as e:
            print(f"Error deleting payment: {e}")
            return False, None, None
        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # SEARCH CONTRACTORS  (for autocomplete)
    # ----------------------------------------------------------
    @staticmethod
    def search_contractors(query):
        connection = Paymentmodel.get_connection()
        if not connection:
            return []
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('SearchContractorsByName', [query])
            results = []
            for result in cursor.stored_results():
                results = result.fetchall()
            return results
        except mysql.connector.Error as e:
            print(f"Error searching contractors: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # GET INVOICES BY CONTRACTOR + PMC
    # ----------------------------------------------------------
    @staticmethod
    def get_invoices_by_contractor_pmc(contractor_id, pmc_no):
        connection = Paymentmodel.get_connection()
        if not connection:
            return []
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('GetInvoicesByContractorPMC', [contractor_id, int(pmc_no)])
            results = []
            for result in cursor.stored_results():
                results = result.fetchall()
            return results
        except mysql.connector.Error as e:
            print(f"Error fetching invoices for contractor/PMC: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # CHECK DUPLICATE UTR
    # ----------------------------------------------------------
    @staticmethod
    def check_duplicate_utr(utr, exclude_id=0):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False
        try:
            cursor = connection.cursor()
            # UTR must be unique across all payment/release sources.
            # Otherwise an imported GST/Hold release UTR could be entered
            # again from the Payment module.
            params = [utr]
            payment_sql = "SELECT COUNT(*) FROM payment WHERE UTR = %s"
            if exclude_id:
                payment_sql += " AND Payment_Id != %s"
                params.append(exclude_id)

            cursor.execute(payment_sql, tuple(params))
            payment_count = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM gst_releases WHERE UTR = %s", (utr,))
            gst_count = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM hold_release WHERE UTR = %s", (utr,))
            hold_count = cursor.fetchone()[0] or 0

            return (payment_count + gst_count + hold_count) > 0
        except mysql.connector.Error as e:
            print(f"Error checking duplicate UTR: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # ITEM CRUD (unchanged)
    # ----------------------------------------------------------
    @staticmethod
    def fetch_items(item_type: ItemCRUDType):
        connection = Paymentmodel.get_connection()
        items = []
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.callproc('GetItemsByType', [item_type.value])
                for result in cursor.stored_results():
                    items = result.fetchall()
            except mysql.connector.Error as e:
                print(f"Error fetching {item_type.name}: {e}")
            finally:
                cursor.close()
                connection.close()
        return items

    @staticmethod
    def insert_item(item_type: ItemCRUDType, name: str):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False
        try:
            cursor = connection.cursor()
            cursor.callproc('InsertItem', [item_type.value, name])
            connection.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error inserting {item_type.name}: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def update_item(item_type: ItemCRUDType, item_id: int, new_name: str):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False
        try:
            cursor = connection.cursor()
            cursor.callproc('UpdateItem', [item_type.value, item_id, new_name])
            connection.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating {item_type.name}: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def delete_item(item_type: ItemCRUDType, item_id: int):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False
        try:
            cursor = connection.cursor()
            cursor.callproc('DeleteItem', [item_type.value, item_id])
            connection.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error deleting {item_type.name}: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
