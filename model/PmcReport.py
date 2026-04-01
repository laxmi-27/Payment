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
            pmc_info = ReportHelper.execute_sp(cursor, 'GetContractorInfoByPmcNo', [pmc_no], True)

            if not pmc_info:
                return None

            cursor.callproc("Get_pmc_hold_types", (pmc_no, pmc_info["Contractor_Id"]))
            hold_types = next(cursor.stored_results()).fetchall()

            # Extract hold_type_ids
            hold_type_ids = [ht['hold_type_id'] for ht in hold_types]

            invoices = []
            hold_amount_total = 0
            # if hold_type_ids:
            #         hold_type_ids_str = ",".join(map(str, hold_type_ids))
            #         cursor.callproc(
            #             'GetInvoices_WithHold',
            #             [pmc_no, pmc_info["Contractor_Id"], hold_type_ids_str]
            #         )
            # else:
            #         cursor.callproc(
            #             'GetInvoices_NoHold',
            #             [pmc_no, pmc_info["Contractor_Id"]]
            #         )

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
                # key = (
                #     str(cn['PMC_No']).strip(),
                #     str(cn['Invoice_No']).replace(" ",     "") if cn['Invoice_No'] else ""
                # )
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
                # key = (
                #     str(gr['PMC_No']).strip(),
                #     str(gr['Invoice_No']).replace(" ", "") if gr['Invoice_No'] else ""
                # )
                key = (
                    str(gr['PMC_No']).strip()
                )
                gst_release_map.setdefault(key, []).append(gr)

       # ================= DATA MAPPING =================
            hold_data = {}
            for h in hold_amounts:
                hold_data.setdefault(h['Invoice_Id'], {})[h['hold_type_id']] = h['hold_amount']

            # credit_note_map = {}
            # for cn in credit_notes:
            #     pmc = cn.get("PMC_No")
            #     if pmc:
            #         credit_note_map.setdefault(pmc, []).append(cn)
                
            # gst_map = {}
            # for gst in gst_releases:
            #     pmc = gst.get("PMC_No")
            #     if pmc:
            #         gst_map.setdefault(pmc, []).append(gst)

            # ================= LOG =================
            LogHelper.log_action(
                "Download PMC Report",
                f"User {current_user.id} Download PMC Report '{pmc_no}'"
            )

            # # ================= EXCEL =================
            # workbook = openpyxl.Workbook()
            # sheet = workbook.active
            # sheet.title = "PMC Report"

            # # HEADER INFO
            # sheet.append(["", "", "Laxmi Civil Engineering Services PVT. LTD."])
            # sheet.append(["Contractor Name", contractor_info["Contractor_Name"]])
            # sheet.append(["State", contractor_info["State_Name"]])
            # sheet.append(["District", contractor_info["District_Name"]])
            # sheet.append(["Block", contractor_info["Block_Name"]])
            # sheet.append([])

            # base_headers = [
            #     "PMC No", "Village", "Work Type", "Invoice Details",
            #     "Invoice Date", "Invoice No", "Basic Amount", "Debit", "After Debit Amount",
            #     "GST", "Amount", "TDS", "SD", "On Commission", "Hydro Testing", "GST SD Amount"
            # ]

            # hold_headers = [ht['hold_type'] for ht in hold_types]
            # payment_headers = ["Final Amount", "Payment Amount", "TDS Payment", "Total Paid", "UTR"]

            # headers = base_headers + hold_headers + payment_headers 
            # sheet.append(headers)
            # for cell in sheet[sheet.max_row]:
            #     cell.font = Font(bold=True)

            # # ================= INVOICE ROWS =================
            # for inv in invoices:
            #     row = [
            #         pmc_no,
            #         inv.get("Village_Name", ""),
            #         inv.get("Work_Type", ""),
            #         inv.get("Invoice_Details", ""),
            #         inv.get("Invoice_Date", ""),
            #         inv.get("invoice_no", ""),
            #         inv.get("Basic_Amount", ""),
            #         inv.get("Debit_Amount", ""),
            #         inv.get("After_Debit_Amount", ""),
            #         inv.get("GST_Amount", ""),
            #         inv.get("Amount", ""),
            #         inv.get("TDS_Amount", ""),
            #         inv.get("SD_Amount", ""),
            #         inv.get("On_Commission", ""),
            #         inv.get("Hydro_Testing", ""),
            #         inv.get("GST_SD_Amount", "")
            #     ]

            #     # HOLD DATA
            #     invoice_holds = hold_data.get(inv.get("Invoice_Id"), {})
            #     for ht_id in hold_type_map.keys():
            #         row.append(invoice_holds.get(ht_id, ""))

            #     # PAYMENT DATA
            #     row += [
            #         inv.get("Final_Amount", ""),
            #         inv.get("Payment_Amount", ""),
            #         inv.get("TDS_Payment_Amount", ""),
            #         inv.get("Total_Amount", ""),
            #         inv.get("UTR", "")
            #     ]

            #     # GST release placeholders (will add real GST below)
            #     row += ["", ""]

            #     sheet.append(row)

            # for pmc, cn_list in credit_note_map.items():
            #     for cn in cn_list:
            #         cn_row = [
            #             pmc_no,
            #             "", "", "Credit Note",
            #             "", cn.get("Invoice_No", ""),
            #             cn.get("Basic_Amount", ""),
            #             "", "", "", "", "", "", "", "", "", "", ""
            #         ]
            #         cn_row += [""] * len(hold_headers)
            #         cn_row += [
            #             cn.get("Final_Amount", ""),
            #             cn.get("Total_Amount", ""),
            #             cn.get("UTR", "")
            #         ]
            #         sheet.append(cn_row)

            # # ================= GST RELEASE ROWS =================
            # for gst in gst_releases:
            #     gst_row = [
            #         gst.get("PMC_No", ""),
            #         "", "", "GST Release Note",
            #         "", gst.get("Invoice_No", ""),
            #         gst.get("Basic_Amount", ""),
            #         "", "", "", "", "", "", "", "", ""
            #     ]
            #     gst_row += [""] * len(hold_headers)
            #     gst_row += [
            #         gst.get("Final_Amount", ""),
            #         "",
            #         "",
            #         gst.get("Total_Amount", ""),
            #         gst.get("UTR", "")
            #     ]
            #     sheet.append(gst_row)

            # # ================= AUTO WIDTH =================
            # for col in sheet.columns:
            #     max_len = max((len(str(cell.value)) for cell in col if cell.value), default=0)
            #     sheet.column_dimensions[col[0].column_letter].width = max_len + 2

            # workbook.save(output_file)
            # workbook.close()


            ReportHelper.generate_excel(
                    0, contractor_info, invoices, hold_types, hold_data,
                    credit_note_map,gst_release_map, output_file
            )
            # ReportHelper.generate_excel(
            #         contractor_id, contInfo, invoices, hold_types, hold_data,
            #         credit_note_map, gst_release_map, output_file
            # )
            return output_folder, filename

        except Exception as e:
            print(f"Error generating PMC report: {e}")
            return None

        finally:
            cursor.close()
            connection.close()
