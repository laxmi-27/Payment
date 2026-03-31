import config
from datetime import datetime
from flask import send_file
import os
import openpyxl
from openpyxl.styles import Font, PatternFill

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
                credit_note = ReportHelper.execute_sp(cursor, 'GetCreditNote', [contractor_id])
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

    # @staticmethod
    # def generate_excel(contractor_id, contInfo, invoices, hold_types, hold_data,
    #                 extra_payments_map, credit_note_map, gst_release_map, output_file):
    @staticmethod
    def generate_excel(contractor_id, contInfo, invoices, hold_types, hold_data,
                 credit_note_map, gst_release_map, output_file):
                 

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Contractor Report"

        # Contractor Info
        for field, value in contInfo.items():
            sheet.append([field.replace("_", " "), value])
        sheet.append([])

        # Headers
        base_headers = ["PMC No", "Village", "Work Type", "Invoice Details", "Invoice Date", "Invoice No",
                        "Basic Amount", "Debit", "After Debit Amount", "GST (18%)", "Amount", "TDS (1%)",
                        "SD (5%)", "On Commission", "Hydro Testing", "GST SD Amount"]

        hold_headers = [ht['hold_type'] for ht in hold_types]

        payment_headers = ["Final Amount", "Payment Amount", "TDS Payment", "Total Paid", "UTR"]

        all_headers = base_headers + hold_headers + payment_headers
        sheet.append(all_headers)

        for cell in sheet[sheet.max_row]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")

        processed_gst_releases = set()
        appended_credit_keys = set()
        previous_pmc_no = None

        for inv in invoices:
            pmc_no = str(inv["PMC_No"]).strip()

            invoice_no = (
                inv["invoice_no"].replace(" ", "") if inv["invoice_no"] else ""
                if inv["invoice_no"] not in (None, "", 0)
                else ""
            )

            # key = (pmc_no, invoice_no)
            key = (pmc_no)

            # Yellow separator
            if previous_pmc_no and pmc_no != previous_pmc_no:
                sheet.append([""] * len(all_headers))
                yellow_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
                for cell in sheet[sheet.max_row]:
                    cell.fill = yellow_fill

            previous_pmc_no = pmc_no

            # Invoice Row
            row = [
                pmc_no,
                inv.get("Village_Name", ""),
                inv.get("Work_Type", ""),
                inv.get("Invoice_Details", ""),
                inv.get("Invoice_Date", ""),
                # inv.get("invoice_no",""),
                invoice_no,
                inv.get("Basic_Amount", ""),
                inv.get("Debit_Amount", ""),
                inv.get("After_Debit_Amount", ""),
                inv.get("GST_Amount", ""),
                inv.get("Amount", ""),
                inv.get("TDS_Amount", ""),
                inv.get("SD_Amount", ""),
                inv.get("On_Commission", ""),
                inv.get("Hydro_Testing", ""),
                inv.get("GST_SD_Amount", "")
            ]

            # Hold values
            invoice_holds = hold_data.get(inv["Invoice_Id"], {})
            for ht_id in [ht['hold_type_id'] for ht in hold_types]:
                row.append(invoice_holds.get(ht_id, ""))

            # Payment values
            row += [
                inv.get("Final_Amount", ""),
                inv.get("Payment_Amount", ""),
                inv.get("TDS_Payment_Amount", ""),
                inv.get("Total_Amount", ""),
                inv.get("UTR", "")
            ]

            sheet.append(row)

            # # Extra Payments
            # if pmc_no in extra_payments_map:
            #     for ep in extra_payments_map[pmc_no]:
            #         extra_row = [pmc_no] + [""] * (len(base_headers) - 1)
            #         extra_row += [""] * len(hold_headers)
            #         extra_row += [
            #             "",
            #             ep.get("Payment_Amount", ""),
            #             ep.get("TDS_Payment_Amount", ""),
            #             ep.get("Total_Amount", ""),
            #             ep.get("utr", "")
            #         ]
            #         sheet.append(extra_row)

            #     del extra_payments_map[pmc_no]

            # GST Releases
            if key in gst_release_map and key not in processed_gst_releases:
                for gr in gst_release_map[key]:
                    gst_row = [
                        pmc_no, "", "", "GST Release Note", "", gr.get("Invoice_No", ""),
                        gr.get("Basic_Amount", ""), "", "", "", "", "", "", "", "", ""
                    ]

                    gst_row += [""] * len(hold_headers)

                    gst_row += [
                        gr.get("Final_Amount", ""),
                        "",
                        "",
                        gr.get("Total_Amount", ""),
                        gr.get("UTR", "")
                    ]

                    sheet.append(gst_row)

                processed_gst_releases.add(key)

            # Credit Notes
            if key in credit_note_map and key not in appended_credit_keys:
                for cn in credit_note_map[key]:
                    cn_row = [
                        pmc_no, "", "", cn.get("Invoice_Details", "Credit Note"), "",
                        cn.get("Invoice_No", ""),
                        cn.get("Basic_Amount", ""),
                        cn.get("Debit_Amount", ""),
                        cn.get("After_Debit_Amount", ""),
                        cn.get("GST_Amount", ""),
                        cn.get("Amount", ""),
                        "", "", "", "", ""
                    ]

                    cn_row += [""] * len(hold_headers)

                    cn_row += [
                        cn.get("Final_Amount", ""),
                        "",
                        "",
                        cn.get("Total_Amount", ""),
                        cn.get("UTR", "")
                    ]

                    sheet.append(cn_row)

                appended_credit_keys.add(key)

        # SAVE ONCE AT END
        workbook.save(output_file)


    @staticmethod
    def create_contractor_report(contractor_id):
        # DOWNLOAD_FOLDER = os.path.join("static", "download")
        # os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        fileName=f"Contractor_Report_{contractor_id}.xlsx"
        # output_file = os.path.join(DOWNLOAD_FOLDER, )
       
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
        # # # -------- Extra Payments MAP --------
        # # extra_payments_raw = ReportHelper.execute_sp(cursor, 'GetExtraPayments')
        # # extra_payments_map = {}
        # # for ep in extra_payments_raw:
        # #     pmc = str(ep['pmc_no']).strip()
        # #     extra_payments_map.setdefault(pmc, []).append(ep)

        # -------- Credit Note MAP --------
        credit_note_raw = ReportHelper.execute_sp(cursor, 'GetCreditNotesByContractor', [contractor_id])
        credit_note_map = {}
        for cn in credit_note_raw:
            # key = (
            #     str(cn['PMC_No']).strip(),
            #     str(cn['Invoice_No']).replace(" ", "") if cn['Invoice_No'] else ""
            # )
            key = (
                str(cn['PMC_No']).strip()
            )
            credit_note_map.setdefault(key, []).append(cn)

        # -------- GST MAP --------
        gst_release_raw = ReportHelper.execute_sp(cursor, 'GstReleasesByContractorId', [contractor_id])
        gst_release_map = {}
        for gr in gst_release_raw:
            # key = (
            #     str(gr['PMC_No']).strip(),
            #     str(gr['Invoice_No']).replace(" ", "") if gr['Invoice_No'] else ""
            # )
            key = (
                str(gr['PMC_No']).strip()
            )
            gst_release_map.setdefault(key, []).append(gr)

        # print("GST MAP:", gst_release_map)
                # Generate Excel
        # ReportHelper.generate_excel(
        #             contractor_id, contInfo, invoices, hold_types, hold_data,
        #             extra_payments_map, credit_note_map, gst_release_map, output_file
        #     )
        ReportHelper.generate_excel(
                    contractor_id, contInfo, invoices, hold_types, hold_data,
                    credit_note_map, gst_release_map, output_file
            )

        return output_file, None




