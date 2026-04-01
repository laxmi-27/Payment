import openpyxl
from openpyxl.styles import Font, PatternFill
import config
from flask_login import current_user
from model.Log import LogHelper
from model.excel import excel
from model.Report import ReportHelper
from model.FolderAndFile import FolderAndFile

class PmcReport:

    @staticmethod
    def get_pmc_report(pmc_no):

        connection = config.get_db_connection()
        cursor = connection.cursor(dictionary=True, buffered=True)

        try:
            pmc_info = ReportHelper.execute_sp(cursor, 'GetContractorInfoByPmcNo', [pmc_no], True)

            if not pmc_info:
                return None

            cursor.callproc("Get_pmc_hold_types", (pmc_no, pmc_info["Contractor_Id"]))
            hold_types = next(cursor.stored_results()).fetchall()

            # Extract hold_type_ids
            hold_type_ids = [ht['hold_type_id'] for ht in hold_types]

            invoices = []
            hold_amount_total = 0
            hold_type_ids_str = ",".join(map(str, hold_type_ids))
            cursor.callproc(
                        'GetInvoices_WithHold',
                        [pmc_no, pmc_info["Contractor_Id"], hold_type_ids_str]
                    )
            
            for result in cursor.stored_results():
                    invoices = result.fetchall()

            if hold_type_ids:
                hold_amount_total = sum(row.get('hold_amount', 0) or 0 for row in invoices)

            total_invo_final = sum(row.get('Final_Amount', 0) or 0 for row in invoices)

            gst_rel = ReportHelper.execute_sp(cursor, 'GetGSTReleaseByPMC', [pmc_no])
            total_gst_basic = sum(row.get('basic_amount', 0) or 0 for row in gst_rel)
            total_gst_final = sum(row.get('final_amount', 0) or 0 for row in gst_rel)

            hold_release = ReportHelper.execute_sp(cursor, 'GetHoldReleaseByPMC', [pmc_no])
            
            credit_note = ReportHelper.execute_sp(cursor, 'GetCreditNoteByPMC', [pmc_no])

            payments = ReportHelper.execute_sp(cursor, 'GetPaymentsByPMC', [pmc_no])
            total_pay_amount = sum(row.get('Payment_Amount', 0) or 0 for row in payments)
            total_pay_total = sum(row.get('Total_amount', 0) or 0 for row in payments)

            totals = {
                "sum_invo_basic_amt": sum(row.get('Basic_Amount', 0) or 0 for row in invoices),
                "sum_invo_debit_amt": sum(row.get('Debit_Amount', 0) or 0 for row in invoices),
                "sum_invo_after_debit_amt": sum(row.get('After_Debit_Amount', 0) or 0 for row in invoices),
                "sum_invo_amt": sum(row.get('Amount', 0) or 0 for row in invoices),
                "sum_invo_gst_amt": sum(row.get('GST_Amount', 0) or 0 for row in invoices),
                "sum_invo_tds_amt": sum(row.get('TDS_Amount', 0) or 0 for row in invoices),
                "sum_invo_ds_amt": sum(row.get('SD_Amount', 0) or 0 for row in invoices),
                "sum_invo_on_commission": sum(row.get('On_Commission', 0) or 0 for row in invoices),
                "sum_invo_hydro_test": sum(row.get('Hydro_Testing', 0) or 0 for row in invoices),
                "sum_invo_gst_sd_amt": sum(row.get('GST_SD_Amount', 0) or 0 for row in invoices),
                "sum_invo_final_amt": total_invo_final,
                "sum_invo_hold_amt": hold_amount_total,
                "sum_gst_basic_amt": total_gst_basic,
                "sum_gst_final_amt": total_gst_final,
                "sum_pay_payment_amt": total_pay_amount,
                "sum_pay_tds_payment_amt": sum(row.get('TDS_Payment_Amount', 0) or 0 for row in payments),
                "sum_pay_total_amt": total_pay_total
            }

            return {
                "info": pmc_info,
                "invoices": invoices,
                "hold_types": hold_types,
                "gst_rel": gst_rel,
                "payments": payments,
                "credit_note": credit_note,
                "hold_release": hold_release,
                "total": totals
            }

        finally:
            cursor.close()
            connection.close()


    @staticmethod
    def download_pmc_report(pmc_no):

        connection = config.get_db_connection()
        if not connection:
            return None

        cursor = connection.cursor(dictionary=True)

        try:
            filename = f"PMC_Report_{pmc_no}.xlsx"

            output_folder = FolderAndFile.get_download_folder()
            output_file = FolderAndFile.get_download_path(filename)

            # ================= DATA FETCH =================

            contractor_info = ReportHelper.execute_sp(
                cursor, 'GetContractorInfoByPmcNo', [pmc_no]                        
            )

            contractor_info = contractor_info[0] if contractor_info else None
            print("contractor_info:::",contractor_info)

            if not contractor_info:
                return None

            hold_types = ReportHelper.execute_sp(
                cursor, 'GetHoldTypesByContractor',
                [contractor_info["Contractor_Id"]]
            )

            hold_type_map = {
                ht['hold_type_id']: ht['hold_type'] for ht in hold_types
            }

            invoices = ReportHelper.execute_sp(
                cursor, 'GetInvoicesByContractorOrPMCNo', [None,pmc_no]
            )

            credit_notes = ReportHelper.execute_sp(
                cursor, 'NewGetCreditNotesByPMCNo', [pmc_no]
            )
            credit_note_map = {}
            for cn in credit_notes:
                key = (
                    str(cn['PMC_No']).strip()
                )
                credit_note_map.setdefault(key, []).append(cn)

            hold_amounts = ReportHelper.execute_sp(
                cursor, 'GetHoldAmountsByContractor',
                [contractor_info["Contractor_Id"]]
            )

            gst_releases = ReportHelper.execute_sp(
                cursor, 'GetGSTReleaseDetailsByPMC', [pmc_no]
            )
            gst_release_map = {}
            for gr in gst_releases:

                key = (
                    str(gr['PMC_No']).strip()
                )
                gst_release_map.setdefault(key, []).append(gr)

       # ================= DATA MAPPING =================
            hold_data = {}
            for h in hold_amounts:
                hold_data.setdefault(h['Invoice_Id'], {})[h['hold_type_id']] = h['hold_amount']


            # ================= LOG =================
            LogHelper.log_action(
                "Download PMC Report",
                f"User {current_user.id} Download PMC Report '{pmc_no}'"
            )

            excel.generate_excel(
                    0, contractor_info, invoices, hold_types, hold_data,
                    credit_note_map,gst_release_map, output_file
            )

            return output_folder, filename

        except Exception as e:
            print(f"Error generating PMC report: {e}")
            return None

        finally:
            cursor.close()
            connection.close()
