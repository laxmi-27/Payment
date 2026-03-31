import config
import mysql.connector
import config
import mysql.connector
from enum import Enum
from model.Utilities import  ItemCRUDType

class Paymentmodel:

    # ---------------- Database Connection ----------------
    @staticmethod
    def get_connection():
        connection = config.get_db_connection()
        if not connection:
            return None
        return connection

    # ---------------- Payment Methods ----------------
    @staticmethod
    def fetch_all_payments():
        connection = Paymentmodel.get_connection()
        payments = []
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.callproc('GetAllPayments')
                for result in cursor.stored_results():
                    payments = result.fetchall()
            except mysql.connector.Error as e:
                print(f"Error fetching payment history: {e}")
            finally:
                cursor.close()
                connection.close()
        return payments

    @staticmethod
    def insert_payment(subcontractor_id, pmc_no, invoice_no, amount, tds_amount, total_amount, utr):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False

        cursor = None
        try:
            cursor = connection.cursor()

            cursor.callproc('GetInvoiceId', [subcontractor_id, pmc_no, invoice_no])

            invoice_id = None
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    invoice_id = row[0]

            if not invoice_id:
                return False

            cursor.callproc(
                'InsertPayments',
                [pmc_no, invoice_no, amount, tds_amount, total_amount, utr, invoice_id]
            )

            connection.commit()
            return True

        except Exception as e:
            print(e)
            return False

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # @staticmethod
    # def update_inpayment(subcontractor_id, pmc_no, invoice_no, amount, tds_amount, total_amount, utr):
    #     connection = Paymentmodel.get_connection()
    #     if not connection:
    #         return False
    #     try:
    #         cursor = connection.cursor()
    #         cursor.callproc('UpdateInpaymentRecord', [
    #             subcontractor_id, pmc_no, invoice_no, amount, tds_amount, total_amount, utr
    #         ])
    #         connection.commit()
    #         return True
    #     except mysql.connector.Error as e:
    #         print(f"Error updating inpayment: {e}")
    #         return False
    #     finally:
    #         cursor.close()
    #         connection.close()

    @staticmethod
    def fetch_payment_by_id(payment_id):
        connection = Paymentmodel.get_connection()
        if not connection:
            return None
        payment_data = {}
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.callproc("GetPaymentById", (payment_id,))
            for result in cursor.stored_results():
                payment_data = result.fetchone()
            if payment_data:
                payment_data = [
                    payment_data.get('Payment_Id'),
                    payment_data.get('PMC_No'),
                    payment_data.get('Invoice_No'),
                    payment_data.get('Payment_Amount'),
                    payment_data.get('TDS_Payment_Amount'),
                    payment_data.get('Total_Amount'),
                    payment_data.get('UTR')
                ]
        except mysql.connector.Error as e:
            print(f"Error fetching payment data: {e}")
        finally:
            cursor.close()
            connection.close()
        return payment_data

    @staticmethod
    def call_update_payment_proc(payment_id, pmc_no, invoice_no, amount, tds_amount, total_amount, utr):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False
        try:
            cursor = connection.cursor()
            cursor.callproc("UpdatePayment", (payment_id, pmc_no, invoice_no, amount, tds_amount, total_amount, utr))
            connection.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating payment: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def delete_payment(payment_id):
        connection = Paymentmodel.get_connection()
        if not connection:
            return False, None, None
        try:
            cursor = connection.cursor(dictionary=True)
            # Fetch PMC & Invoice before deleting
            cursor.callproc('GetPaymentById', [payment_id])
            record = {}
            for result in cursor.stored_results():
                record = result.fetchone() or {}
            if not record:
                return False, None, None
            pmc_no = record['PMC_No']
            invoice_no = record['Invoice_No']
            # Delete payment
            cursor.callproc("DeletePayment", (payment_id,))
            connection.commit()
            # Reset inpayment fields
            # cursor.callproc("ResetInpayment", [pmc_no, invoice_no])
            # connection.commit()
            return True, pmc_no, invoice_no
        except mysql.connector.Error as e:
            print(f"Error deleting payment: {e}")
            return False, None, None
        finally:
            cursor.close()
            connection.close()

    # ---------------- Item CRUD Methods ----------------
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