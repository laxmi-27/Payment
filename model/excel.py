import openpyxl
from openpyxl.styles import Font, PatternFill


from model.FolderAndFile import FolderAndFile

class excel:

    @staticmethod
    def generate_excel(contractor_id,info, invoices, hold_types, hold_data, credit_note_map, gst_release_map, payments,total,output_file):            

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Contractor Report"

        # Contractor Info
        for field, value in info.items():
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

        # total calculation
        hold_totals = {ht['hold_type_id']: 0 for ht in hold_types}

        for inv in invoices:
            invoice_holds = hold_data.get(inv["Invoice_Id"], {})
            for ht_id in hold_totals:
                hold_totals[ht_id] += invoice_holds.get(ht_id, 0) or 0

        totalrow = ["Total","-","-","-","-","-",total.get('sum_invo_basic_amt', 0)+total.get('sum_gst_basic_amt')+ total.get('sum_credit_basic_amt'),
                   total.get('sum_invo_debit_amt', 0), total.get('sum_invo_after_debit_amt', 0),total.get('sum_invo_gst_amt', 0),total.get('sum_invo_amt', 0),
                   total.get('sum_invo_tds_amt', 0),total.get('sum_invo_ds_amt', 0),total.get('sum_invo_on_commission', 0), total.get('sum_invo_hydro_test', 0),
                   total.get('sum_invo_gst_sd_amt', 0)]
                   
        for ht in hold_types:
            totalrow.append(hold_totals.get(ht['hold_type_id'], 0))

        totalrow += [ total.get('sum_invo_final_amt', 0)+ total.get('sum_gst_final_amt', 0) + total.get('sum_credit_final_amt', 0),"","",
                     total.get('sum_pay_total_amt', 0)+ total.get('sum_gst_total_amt', 0) + total.get('sum_credit_total_amt', 0)]
        
        
        sheet.append(totalrow)
        # Apply style (color + bold)
        for cell in sheet[sheet.max_row]:
            cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Yellow
            cell.font = Font(bold=True)

        # summary report
        sheet.append([""])
        sheet.append([""])
        sheet.append(["","","Summary Report","",""])
        summary1 = ["", "Advance / Suplus" , total.get('sum_pay_total_amt', 0)+ total.get('sum_gst_total_amt', 0) + total.get('sum_credit_total_amt', 0)]
        summary2 = ["", "Hold Amt", total["sum_invo_hold_amt"]]
        summary3 = ["", "Amount With TDS", total["sum_invo_tds_amt"]]
        sheet.append(summary1)
        sheet.append(summary2)
        sheet.append(summary3)


        # SAVE ONCE AT END
        workbook.save(output_file)