import config
from model.excel import excel
from model.Report import ReportHelper
from model.FolderAndFile import FolderAndFile
from decimal import Decimal
class UnifiedReportService:

    # Static variable to cache report data
    # _cached_report_data = None
    # _cached_contractor_id = None
    # _cached_pmc_no = None

    @staticmethod
    def get_report(contractor_id=None, pmc_no=None):

        # If cached and same request, return cached data
        # if (UnifiedReportService._cached_report_data and
        #     contractor_id == UnifiedReportService._cached_contractor_id and
        #     pmc_no == UnifiedReportService._cached_pmc_no):
        #     return UnifiedReportService._cached_report_data

        connection = config.get_db_connection()
        cursor = connection.cursor(dictionary=True, buffered=True)

        try:
            # ================= BASIC INFO =================
            if contractor_id:
                info = ReportHelper.execute_sp(cursor,'GetContractorInfo',[contractor_id],True)
            else:
                info = ReportHelper.execute_sp(cursor,'GetContractorInfoByPmcNo',[pmc_no],True)


                contractor_id = info["Contractor_Id"] if info else None

            if not info:
                return None

            # ================= HOLD TYPES =================
            hold_types = ReportHelper.execute_sp(cursor,'GetHoldTypesByContractor',[contractor_id]) or []


            # ================= INVOICES =================
            if pmc_no:
                invoices = ReportHelper.execute_sp(cursor,'GetInvoicesByContractorOrPMCNo',[None, pmc_no]) or []
                credit_notes = ReportHelper.execute_sp(cursor,'NewGetCreditNotesByPMCNo',[pmc_no]) or []
                gst_rel = ReportHelper.execute_sp(cursor,'GetGSTReleaseDetailsByPMC',[pmc_no]) or []
                payments = ReportHelper.execute_sp(cursor,'GetPaymentsByPMC',[pmc_no]) or []

            else:
                invoices = ReportHelper.execute_sp(cursor,'GetInvoicesByContractorOrPMCNo',[contractor_id, None]) or []
                credit_notes = ReportHelper.execute_sp(cursor,'GetCreditNotesByContractor',[contractor_id]) or []
                gst_rel = ReportHelper.execute_sp(cursor,'GstReleasesByContractorId',[contractor_id]) or []
                payments = ReportHelper.execute_sp(cursor,'GetPayments',[contractor_id]) or []

            # ================= HOLD AMOUNTS =================
            hold_amounts = ReportHelper.execute_sp(cursor,'GetHoldAmountsByContractor',[contractor_id]) or []

            hold_data = {}
            for h in hold_amounts:
                hold_data.setdefault(h["Invoice_Id"], {})[h["hold_type_id"]] = h["hold_amount"]

            # ================= CREDIT NOTES =================

            credit_note_map = {}
            for cn in credit_notes:
                key = str(cn.get("PMC_No")).strip()
                credit_note_map.setdefault(key, []).append(cn)

            # ================= GST RELEASE =================
            gst_release_map = {}
            for gr in gst_rel:
                key = str(gr.get("PMC_No")).strip()
                gst_release_map.setdefault(key, []).append(gr)

            # ================= PAYMENTS =================
            total = {
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
                "sum_invo_final_amt": sum(r.get("Final_Amount", 0) or 0 for r in invoices),
                "sum_invo_hold_amt": sum(r.get("hold_amount", 0) or 0 for r in hold_amounts),
                "sum_gst_basic_amt": sum(r.get("Basic_Amount", 0) or 0 for r in gst_rel),
                "sum_gst_final_amt": sum(r.get("Final_Amount", 0) or 0 for r in gst_rel),
                "sum_gst_total_amt": sum(r.get("Total_Amount", 0) or 0 for r in gst_rel),
                "sum_pay_total_amt": sum(Decimal(r.get("Total_amount") or 0) for r in payments),
                "sum_pay_payment_amt": sum(Decimal(r.get("Payment_Amount") or 0) for r in payments),
                "sum_pay_tds_payment_amt": sum(Decimal(r.get("TDS_Payment_Amount") or 0) for r in payments),
                "sum_credit_basic_amt": sum(Decimal(c.get("Basic_Amount") or 0) for c in credit_notes),
                "sum_credit_final_amt": sum(Decimal(c.get("Final_Amount") or 0) for c in credit_notes),
                "sum_credit_total_amt": sum(Decimal(c.get("Total_Amount") or 0) for c in credit_notes),
            }

            # Prepare final report
            report_data = {
                "info": info,
                "invoices": invoices,
                "hold_types": hold_types,
                "payments": payments,
                "hold_data": hold_data,
                "hold_release": hold_data,
                "credit_note_map": credit_note_map,
                "credit_note": credit_notes,
                "gst_release_map": gst_release_map,
                "gst_rel": gst_rel,
                "total": total
            }

            # # Cache the report
            # UnifiedReportService._cached_report_data = report_data
            # UnifiedReportService._cached_contractor_id = contractor_id
            # UnifiedReportService._cached_pmc_no = pmc_no

            return report_data

        finally:
            cursor.close()
            connection.close()

    # ================= DOWNLOAD EXCEL =================
    @staticmethod
    def download(contractor_id=None, pmc_no=None):
        # Use cached report if available
        report_data = UnifiedReportService.get_report(contractor_id, pmc_no)

        if not report_data:
            return None

        fileName = (
            f"Contractor_Report_{contractor_id}.xlsx"
            if contractor_id else f"PMC_Report_{pmc_no}.xlsx"
        )

        output_file = FolderAndFile.get_download_path(fileName)

        excel.generate_excel(
            contractor_id or 0,
            report_data["info"],
            report_data["invoices"],
            report_data["hold_types"],
            report_data["hold_data"],
            report_data["credit_note_map"],
            report_data["gst_release_map"],
            report_data["payments"],
            report_data["total"],
            output_file
        )

        return output_file