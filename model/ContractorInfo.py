from mysql.connector import Error
import config


class ContractorInfo:
    def __init__(self, contractor_id):
        self.ID = contractor_id
        self.contInfo = None
        self.fetchData()

    def fetchData(self):
        """Fetch basic contractor info by ID."""
        try:
            connection = config.get_db_connection()
            with connection.cursor(dictionary=True, buffered=True) as cursor:
                cursor.callproc('GetContractorInfo', [self.ID])                     #Change  GetContractorInfoById to GetContractorInfo
                # Get the first result set
                for result in cursor.stored_results():
                    self.contInfo = result.fetchone()
        except Error as e:
            print(f"Error fetching contractor info: {e}")
        finally:
            if connection.is_connected():
                connection.close()

    def fetchalldata(self):
        """Fetch hold types and invoices for contractor."""
        data = {}
        try:
            connection = config.get_db_connection()
            with connection.cursor(dictionary=True, buffered=True) as cursor:
                # Fetch Hold Types
                cursor.callproc('GetHoldAmountsAndHoldTypeByCtr', [self.ID])
                hold_types = []
                for result in cursor.stored_results():
                    hold_types = result.fetchall()
                hold_type_map = {ht['hold_type_id']: ht['hold_type'] for ht in hold_types}
                data['hold_types'] = hold_type_map

                # Fetch Invoices
                cursor.callproc('GetInvoicesByContractor', [self.ID])
                invoices = []
                for result in cursor.stored_results():
                    invoices = result.fetchall()

                # Remove duplicate invoices
                seen_ids = set()
                unique_invoices = []
                for inv in invoices:
                    if inv['Invoice_Id'] not in seen_ids:
                        seen_ids.add(inv['Invoice_Id'])
                        unique_invoices.append(inv)
                data['invoices'] = unique_invoices

        except Error as e:
            print(f"Error fetching contractor data: {e}")
        finally:
            if connection.is_connected():
                connection.close()

        return data
