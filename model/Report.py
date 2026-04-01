import config
from datetime import datetime
from flask import send_file
import openpyxl
from openpyxl.styles import Font, PatternFill
from model.excel import excel

from model.FolderAndFile import FolderAndFile

class ReportHelper:
    isSuccess = False
    resultMessage = ""
    data=[]

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""
        self.data = []

    @staticmethod
    def execute_sp(cursor, proc_name, params=[], fetch_one=False):
        cursor.callproc(proc_name, params)
        return (
            ReportHelper.fetch_one_result(cursor)
            if fetch_one else
            ReportHelper.fetch_all_results(cursor)
        )

    @staticmethod
    def fetch_all_results(cursor):
        data = []
        for result in cursor.stored_results():
            data = result.fetchall()
        return data


    @staticmethod
    def fetch_one_result(cursor):
        data = None
        for result in cursor.stored_results():
            data = result.fetchone()
        return data


    @staticmethod
    def search_contractor(request):
        subcontractor_name = request.form.get("subcontractor_name")
        pmc_no = request.form.get("pmc_no")
        state = request.form.get("state")
        district = request.form.get("district")
        block = request.form.get("block")
        village = request.form.get("village")
        year_from = request.form.get("year_from")
        year_to = request.form.get("year_to")

        connection = config.get_db_connection()
        if not connection:
            return []

        cursor = connection.cursor(dictionary=True)

        try:
            data = ReportHelper.execute_sp(
                cursor,
                "search_contractor_info",
                [
                    subcontractor_name or None,
                    pmc_no or None,
                    state or None,
                    district or None,
                    block or None,
                    village or None,
                    year_from or None,
                    year_to or None
                ]
            )

        except Exception as e:
            print(f"Error in search_contractor: {e}")
            data = []

        finally:
            cursor.close()
            connection.close()

        return data

    
    @staticmethod
    def get_contractor_report(contractor_id):
            connection = config.get_db_connection()
            cursor = connection.cursor(dictionary=True, buffered=True)
        
            try:
                # Contractor Info (only one fetch)
                contInfo = ReportHelper.execute_sp(cursor, 'GetContractorInfo', [contractor_id], True)
                # Hold Types
                hold_types = ReportHelper.execute_sp(cursor, 'GetContractorHoldTypes', [contractor_id])
                # Invoices
                invoices = ReportHelper.execute_sp(cursor, 'GetContractorInvoices', [contractor_id])
                # GST Release
                gst_rel = ReportHelper.execute_sp(cursor, 'GetGSTRelease', [contractor_id])
                # Hold Release
                hold_release = ReportHelper.execute_sp(cursor, 'GetHoldRelease', [contractor_id])
                # Credit Note
                credit_note = ReportHelper.execute_sp(cursor, 'GetCreditNotesByContractor', [contractor_id])
                # Payments
                payments = ReportHelper.execute_sp(cursor, 'GetPayments', [contractor_id])

                # Totals
                total = {
                    "sum_invo_basic_amt": float(sum(row['Basic_Amount'] or 0 for row in invoices)),
                    "sum_invo_debit_amt": float(sum(row['Debit_Amount'] or 0 for row in invoices)),
                    "sum_invo_after_debit_amt": float(sum(row['After_Debit_Amount'] or 0 for row in invoices)),
                    "sum_invo_amt": float(sum(row['Amount'] or 0 for row in invoices)),
                    "sum_invo_gst_amt": float(sum(row['GST_Amount'] or 0 for row in invoices)),
                    "sum_invo_tds_amt": float(sum(row['TDS_Amount'] or 0 for row in invoices)),
                    "sum_invo_ds_amt": float(sum(row['SD_Amount'] or 0 for row in invoices)),
                    "sum_invo_on_commission": float(sum(row['On_Commission'] or 0 for row in invoices)),
                    "sum_invo_hydro_test": float(sum(row['Hydro_Testing'] or 0 for row in invoices)),
                    "sum_invo_gst_sd_amt": float(sum(row['GST_SD_Amount'] or 0 for row in invoices)),
                    "sum_invo_final_amt": float(sum(row['Final_Amount'] or 0 for row in invoices)),
                    "sum_invo_hold_amt": float(sum(row['hold_amount'] or 0 for row in invoices)),

                    "sum_gst_basic_amt": float(sum(row['basic_amount'] or 0 for row in gst_rel)),
                    "sum_gst_final_amt": float(sum(row['final_amount'] or 0 for row in gst_rel)),

                    "sum_pay_payment_amt": float(sum(row['Payment_Amount'] or 0 for row in payments)),
                    "sum_pay_tds_payment_amt": float(sum(row['TDS_Payment_Amount'] or 0 for row in payments)),
                    "sum_pay_total_amt": float(sum(row['Total_amount'] or 0 for row in payments))
                }

                current_date = datetime.now().strftime('%Y-%m-%d')

            finally:
                cursor.close()
                connection.close()

            return {
                "contInfo": contInfo,
                "invoices": invoices,
                "hold_types": hold_types,
                "gst_rel": gst_rel,
                "payments": payments,
                "credit_note": credit_note,
                "hold_release": hold_release,
                "total": total,
                "current_date": current_date
            }
    @staticmethod
    def get_contractor_info(contractor_id):
        from model.ContractorInfo import ContractorInfo
        contractor = ContractorInfo(contractor_id)
        return contractor.contInfo if contractor.contInfo else None


    @staticmethod
    def create_contractor_report(contractor_id):

        fileName=f"Contractor_Report_{contractor_id}.xlsx"
        output_file = FolderAndFile.get_download_path(filename=fileName)

        # Fetch Data
        contInfo = ReportHelper.get_contractor_info(contractor_id)
        if not contInfo:
            return None, "No contractor found"

        connection = config.get_db_connection()
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        hold_types = ReportHelper.execute_sp(cursor, 'HoldTypesByContractorId', [contractor_id])
        invoices = ReportHelper.execute_sp(cursor, 'GetInvoicesByContractorOrPMCNo', [contractor_id,None])
        hold_amounts = ReportHelper.execute_sp(cursor, 'HoldAmountsByContractorId', [contractor_id])
        hold_data = {}
        for h in hold_amounts:
            hold_data.setdefault(h['Invoice_Id'], {})[h['hold_type_id']] = h['hold_amount']

        # -------- Credit Note MAP --------
        credit_note_raw = ReportHelper.execute_sp(cursor, 'GetCreditNotesByContractor', [contractor_id])
        credit_note_map = {}
        for cn in credit_note_raw:
 
            key = (
                str(cn['PMC_No']).strip()
            )
            credit_note_map.setdefault(key, []).append(cn)

        # -------- GST MAP --------
        gst_release_raw = ReportHelper.execute_sp(cursor, 'GstReleasesByContractorId', [contractor_id])
        gst_release_map = {}
        for gr in gst_release_raw:
            key = (
                str(gr['PMC_No']).strip()
            )
            gst_release_map.setdefault(key, []).append(gr)

        excel.generate_excel(
                    contractor_id, contInfo, invoices, hold_types, hold_data,
                    credit_note_map, gst_release_map, output_file
            )

        return output_file, None




