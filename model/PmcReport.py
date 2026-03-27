import openpyxl
from openpyxl.styles import Font, PatternFill
import config
from flask_login import current_user
from model.Log import LogHelper

from model.Report import ReportHelper
from model.FolderAndFile import FolderAndFile

class PmcReport:

    @staticmethod
    def get_pmc_report(pmc_no):

        connection = config.get_db_connection()
        cursor = connection.cursor(dictionary=True, buffered=True)

        try:

            # cursor.callproc("GetContractorInfoByPmcNo", (pmc_no,))
            # pmc_info = next(cursor.stored_results()).fetchone()
            pmc_info = ReportHelper.execute_sp(cursor, 'GetContractorInfoByPmcNo', [pmc_no], True)

            if not pmc_info:
                return None

            cursor.callproc("Get_pmc_hold_types", (pmc_no, pmc_info["Contractor_Id"]))
            hold_types = next(cursor.stored_results()).fetchall()

            # Extract hold_type_ids
            hold_type_ids = [ht['hold_type_id'] for ht in hold_types]

            invoices = []
            hold_amount_total = 0
            if hold_type_ids:
                    hold_type_ids_str = ",".join(map(str, hold_type_ids))
                    cursor.callproc(
                        'GetInvoices_WithHold',
                        [pmc_no, pmc_info["Contractor_Id"], hold_type_ids_str]
                    )
            else:
                    cursor.callproc(
                        'GetInvoices_NoHold',
                        [pmc_no, pmc_info["Contractor_Id"]]
                    )
            for result in cursor.stored_results():
                    invoices = result.fetchall()

            if hold_type_ids:
                hold_amount_total = sum(row.get('hold_amount', 0) or 0 for row in invoices)

            total_invo_final = sum(row.get('Final_Amount', 0) or 0 for row in invoices)


            # GST RELEASE
            # cursor.callproc('GetGSTReleaseByPMC', [pmc_no])
            # gst_rel = []
            # for result in cursor.stored_results():
            #     gst_rel = result.fetchall()
            
            gst_rel = ReportHelper.execute_sp(cursor, 'GetGSTReleaseByPMC', [pmc_no])

            total_gst_basic = sum(row.get('basic_amount', 0) or 0 for row in gst_rel)
            total_gst_final = sum(row.get('final_amount', 0) or 0 for row in gst_rel)

            # ---------------- HOLD RELEASE ----------------
            # cursor.callproc('GetHoldReleaseByPMC', [pmc_no])
            # hold_release = []
            # for result in cursor.stored_results():
            #     hold_release = result.fetchall()

            hold_release = ReportHelper.execute_sp(cursor, 'GetHoldReleaseByPMC', [pmc_no])

            # ---------------- CREDIT NOTE ----------------
            # cursor.callproc('GetCreditNoteByPMC', [pmc_no])
            # credit_note = []
            # for result in cursor.stored_results():
            #     credit_note = result.fetchall()
            
            credit_note = ReportHelper.execute_sp(cursor, 'GetCreditNoteByPMC', [pmc_no])

            payments = ReportHelper.execute_sp(cursor, 'GetPaymentsByPMC', [pmc_no])


            # ---------------- PAYMENTS ----------------
            # cursor.callproc('GetPaymentsByPMC', [pmc_no])
            # payments = []
            # for result in cursor.stored_results():
            #     payments = result.fetchall()

            

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
            # filename
            filename = f"PMC_Report_{pmc_no}.xlsx"

            output_folder = FolderAndFile.get_download_folder()
            output_file = FolderAndFile.get_download_path(filename)

            # ================= DATA FETCH =================

            contractor_info = ReportHelper.execute_sp(cursor, 'GetContractorDetailsByPMC', [pmc_no], "one")

            if not contractor_info:
                return None

            hold_types = ReportHelper.execute_sp(cursor, 'GetHoldTypesByContractor', [contractor_info["Contractor_Id"]])

            hold_type_map = {ht['hold_type_id']: ht['hold_type'] for ht in hold_types}

            invoices = ReportHelper.execute_sp(cursor, 'GetInvoicesAndGstReleaseByPmcNo', [pmc_no])

            credit_notes = ReportHelper.execute_sp(cursor, 'GetCreditNoteByContractor', [contractor_info["Contractor_Id"]])

            hold_amounts = ReportHelper.execute_sp(cursor, 'GetHoldAmountsByContractor', [contractor_info["Contractor_Id"]])

            all_payments = ReportHelper.execute_sp(cursor, 'GetAllPaymentsByPMC', [pmc_no])

            gst_releases = ReportHelper.execute_sp(cursor, 'GetGSTReleaseDetailsByPMC', [pmc_no])

            # ================= DATA MAPPING =================

            hold_data = {}
            for h in hold_amounts:
                hold_data.setdefault(h['Invoice_Id'], {})[h['hold_type_id']] = h['hold_amount']

            payments_map = {}
            for pay in all_payments:
                if pay['invoice_no']:
                    payments_map.setdefault(pay['invoice_no'], []).append(pay)

            # ================= LOG =================
            LogHelper.log_action(
                "Download PMC Report",
                f"User {current_user.id} Download PMC Report '{pmc_no}'"
            )

            # ================= EXCEL =================
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "PMC Report"

            # HEADER INFO
            sheet.append(["", "", "Laxmi Civil Engineering Services PVT. LTD."])
            sheet.append(["Contractor Name", contractor_info["Contractor_Name"]])
            sheet.append(["State", contractor_info["State_Name"]])
            sheet.append(["District", contractor_info["District_Name"]])
            sheet.append(["Block", contractor_info["Block_Name"]])
            sheet.append([])

            base_headers = [
                "PMC No","Village","Work Type","Invoice Details","Invoice Date","Invoice No",
                "Basic Amount","Debit","After Debit Amount","GST","Amount","TDS",
                "SD","On Commission","Hydro Testing","GST SD Amount"
            ]

            hold_headers = [ht['hold_type'] for ht in hold_types]

            payment_headers = [
                "Final Amount","Payment Amount","TDS Payment","Total Paid","UTR"
            ]

            headers = base_headers + hold_headers + payment_headers
            sheet.append(headers)

            # STYLE
            for cell in sheet[sheet.max_row]:
                cell.font = Font(bold=True)

            # DATA
            seen_invoices = set()

            for inv in invoices:

                invoice_no = inv["Invoice_No"]
                payments = payments_map.get(invoice_no, [])

                if invoice_no in seen_invoices:
                    continue

                seen_invoices.add(invoice_no)

                first_payment = payments[0] if payments else None

                row = [
                    pmc_no,
                    inv["Village_Name"],
                    inv["Work_Type"],
                    inv["Invoice_Details"],
                    inv["Invoice_Date"],
                    invoice_no,
                    inv["Basic_Amount"],
                    inv["Debit_Amount"],
                    inv["After_Debit_Amount"],
                    inv["GST_Amount"],
                    inv["Amount"],
                    inv["TDS_Amount"],
                    inv["SD_Amount"],
                    inv["On_Commission"],
                    inv["Hydro_Testing"],
                    inv["GST_SD_Amount"]
                ]

                # HOLD DATA
                invoice_holds = hold_data.get(inv["Invoice_Id"], {})
                for ht_id in hold_type_map.keys():
                    row.append(invoice_holds.get(ht_id, ""))

                # PAYMENT DATA
                row += [
                    inv["Final_Amount"],
                    first_payment["Payment_Amount"] if first_payment else "",
                    first_payment["TDS_Payment_Amount"] if first_payment else "",
                    first_payment["Total_amount"] if first_payment else "",
                    first_payment["UTR"] if first_payment else ""
                ]

                sheet.append(row)

            # AUTO WIDTH
            for col in sheet.columns:
                max_len = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                sheet.column_dimensions[col[0].column_letter].width = max_len + 2

            # SAVE
            workbook.save(output_file)
            workbook.close()

            return output_folder, filename

        except Exception as e:
            print(f"Error generating PMC report: {e}")
            return None

        finally:
            cursor.close()
            connection.close()

    # @staticmethod
    # def download_pmc_report(pmc_no):

    #     connection = config.get_db_connection()
    #     cursor = connection.cursor(dictionary=True)

    #     # output_folder = "static/download"
    #     # output_file = os.path.join(output_folder, f"PMC_Report_{pmc_no}.xlsx")
    #     output_folder = FolderAndFile.get_download_folder
    #     filename = f"PMC_Report_{pmc_no}.xlsx"
    #     output_file = FolderAndFile.get_download_path(filename)

    #     try:

    #         cursor.callproc('GetContractorDetailsByPMC', [pmc_no])
    #         contractor_info = next(cursor.stored_results()).fetchone()

    #         if not contractor_info:
    #             return None

    #         cursor.callproc('GetHoldTypesByContractor', [contractor_info["Contractor_Id"]])
    #         hold_types = next(cursor.stored_results()).fetchall()

    #         hold_type_map = {ht['hold_type_id']: ht['hold_type'] for ht in hold_types}

    #         cursor.callproc('GetInvoicesAndGstReleaseByPmcNo', [pmc_no])
    #         invoices = next(cursor.stored_results()).fetchall()

    #         cursor.callproc('GetCreditNoteByContractor',[contractor_info["Contractor_Id"]])

    #         credit_notes = []
    #         for result in cursor.stored_results():
    #             credit_notes = result.fetchall()

    #         credit_note_map = {}
    #         for cn in credit_notes:
    #             key = (cn["PMC_No"], cn["Invoice_No"])
    #             credit_note_map.setdefault(key, []).append(cn)

    #         cursor.callproc('GetHoldAmountsByContractor', [contractor_info["Contractor_Id"]])
    #         hold_amounts = next(cursor.stored_results()).fetchall()

    #         hold_data = {}
    #         for h in hold_amounts:
    #             hold_data.setdefault(h['Invoice_Id'], {})[h['hold_type_id']] = h['hold_amount']

    #         cursor.callproc('GetAllPaymentsByPMC', [pmc_no])
    #         all_payments = next(cursor.stored_results()).fetchall()

    #         payments_map = {}
    #         extra_payments = []

    #         for pay in all_payments:
    #             if pay['invoice_no']:
    #                 payments_map.setdefault(pay['invoice_no'], []).append(pay)
    #             else:
    #                 extra_payments.append(pay)

    #       # ---------------- GST RELEASE DETAILS ----------------
    #         cursor.callproc('GetGSTReleaseDetailsByPMC', [pmc_no])

    #         gst_releases = []
    #         for result in cursor.stored_results():
    #             gst_releases = result.fetchall()

    #         gst_release_map = {}

    #         for gr in gst_releases:

    #             invoice_nos = []

    #             if gr['Invoice_No']:

    #                 cleaned = gr['Invoice_No'].replace(' ', '')

    #                 if '&' in cleaned:
    #                     invoice_nos = cleaned.split('&')

    #                 elif ',' in cleaned:
    #                     invoice_nos = cleaned.split(',')

    #                 else:
    #                     invoice_nos = [cleaned]

    #             for inv_no in invoice_nos:
    #                 gst_release_map.setdefault(inv_no, []).append(gr)

    #         LogHelper.log_action(
    #             "Download PMC Report",
    #             f"User {current_user.id} Download PMC Report '{pmc_no}'"
    #         )

    #         workbook = openpyxl.Workbook()
    #         sheet = workbook.active
    #         sheet.title = "PMC Report"

    #         sheet.append(["", "", "Laxmi Civil Engineering Services PVT. LTD."])
    #         sheet.append(["Contractor Name", contractor_info["Contractor_Name"], "", "GST No", contractor_info["GST_No"], "", "GST Type", contractor_info["GST_Registration_Type"]])
    #         sheet.append(["State", contractor_info["State_Name"], "", "PAN No", contractor_info["PAN_No"], "", "Address", contractor_info["Address"]])
    #         sheet.append(["District", contractor_info["District_Name"], "", "Mobile No", contractor_info["Mobile_No"]])
    #         sheet.append(["Block", contractor_info["Block_Name"], "", "Email", contractor_info["Email"]])
    #         sheet.append([])

    #         base_headers = [
    #             "PMC No","Village","Work Type","Invoice Details","Invoice Date","Invoice No",
    #             "Basic Amount","Debit","After Debit Amount","GST (18%)","Amount","TDS (1%)",
    #             "SD (5%)","On Commission","Hydro Testing","GST SD Amount"
    #         ]

    #         hold_headers = [ht['hold_type'] for ht in hold_types]

    #         payment_headers = [
    #             "Final Amount","Payment Amount","TDS Payment","Total Paid","UTR"
    #         ]

    #         sheet.append(base_headers + hold_headers + payment_headers)

    #         header_fill = PatternFill(start_color="ADD8E6",end_color="ADD8E6",fill_type="solid")
    #         header_font = Font(bold=True)

    #         for cell in sheet[sheet.max_row]:
    #             cell.font = header_font
    #             cell.fill = header_fill

    #         seen_invoices = set()
    #         processed_payments = set()

    #         for inv in invoices:

    #             invoice_no = inv["Invoice_No"]
    #             payments = payments_map.get(invoice_no, [])

    #             if invoice_no not in seen_invoices:

    #                 seen_invoices.add(invoice_no)
    #                 first_payment = payments[0] if payments else None

    #                 row = [
    #                     pmc_no, inv["Village_Name"], inv["Work_Type"],
    #                     inv["Invoice_Details"], inv["Invoice_Date"], invoice_no,
    #                     inv["Basic_Amount"], inv["Debit_Amount"],
    #                     inv["After_Debit_Amount"], inv["GST_Amount"],
    #                     inv["Amount"], inv["TDS_Amount"], inv["SD_Amount"],
    #                     inv["On_Commission"], inv["Hydro_Testing"], inv["GST_SD_Amount"]
    #                 ]

    #                 invoice_holds = hold_data.get(inv["Invoice_Id"], {})

    #                 for ht_id in hold_type_map.keys():
    #                     row.append(invoice_holds.get(ht_id, ""))

    #                 row += [
    #                     inv["Final_Amount"],
    #                     first_payment["Payment_Amount"] if first_payment else "",
    #                     first_payment["TDS_Payment_Amount"] if first_payment else "",
    #                     first_payment["Total_amount"] if first_payment else "",
    #                     first_payment["UTR"] if first_payment else ""
    #                 ]

    #                 sheet.append(row)

    #         workbook.save(output_file)
    #         workbook.close()

    #         return output_folder, filename

    #     finally:

    #         cursor.close()
    #         connection.close()