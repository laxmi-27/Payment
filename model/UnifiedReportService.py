import config
from decimal import Decimal
from model.Report import ReportHelper
from model.FolderAndFile import FolderAndFile


def _fsum(lst, key):
    return round(sum(float(r.get(key) or 0) for r in lst), 2)


def _actual_paid(r):
    """Prefer Amount_after_TDS_Deduction (net transfer); fall back to Amount_with_TDS."""
    ta = float(r.get('Amount_after_TDS_Deduction') or r.get('Total_Amount') or 0)
    if ta > 0:
        return ta
    return float(r.get('Amount_with_TDS') or r.get('Payment_Amount') or 0)


class UnifiedReportService:

    @staticmethod
    def get_report(contractor_id=None, pmc_no=None):
        connection = config.get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            # ── Contractor Info ────────────────────────────────────────────
            if contractor_id:
                cursor.execute("""
                    SELECT s.Contractor_Id, s.Contractor_Name, s.Address, s.PAN_No,
                           s.Mobile_No, s.Email, s.GST_Registration_Type, s.GST_No,
                           MAX(st.State_Name)   AS State_Name,
                           MAX(d.District_Name) AS District_Name,
                           MAX(b.Block_Name)    AS Block_Name
                    FROM subcontractors s
                    LEFT JOIN assign_subcontractors asg ON s.Contractor_Id = asg.Contractor_Id
                    LEFT JOIN villages v  ON asg.Village_Id  = v.Village_Id
                    LEFT JOIN blocks   b  ON v.Block_Id      = b.Block_Id
                    LEFT JOIN districts d ON b.District_id   = d.District_id
                    LEFT JOIN states   st ON d.State_Id      = st.State_Id
                    WHERE s.Contractor_Id = %s
                    GROUP BY s.Contractor_Id
                """, (contractor_id,))
                info = cursor.fetchone()
            else:
                info = ReportHelper.execute_sp(cursor, 'GetContractorInfoByPmcNo', [pmc_no], True)
                contractor_id = info["Contractor_Id"] if info else None

            if not info:
                return None

            # ── Hold Types ─────────────────────────────────────────────────
            hold_types = ReportHelper.execute_sp(cursor, 'GetHoldTypesByContractor',
                                                 [contractor_id]) or []

            # ── Invoices with aggregated payments (one row per invoice) ────
            inv_where = "i.PMC_No = %s" if pmc_no else "i.Subcontractor_Id = %s"
            inv_param = pmc_no if pmc_no else contractor_id
            cursor.execute(f"""
                SELECT
                    i.Invoice_Id,
                    i.PMC_No,
                    i.Invoice_Date,
                    i.Invoice_No          AS invoice_no,
                    i.Invoice_Details,
                    i.Work_Type,
                    COALESCE(v.Village_Name, '')  AS Village_Name,
                    COALESCE(i.Basic_Amount,  0)  AS Basic_Amount,
                    COALESCE(i.Debit_Amount,  0)  AS Debit_Amount,
                    COALESCE(i.After_Debit_Amount, 0) AS After_Debit_Amount,
                    COALESCE(i.Amount,        0)  AS Amount,
                    COALESCE(i.GST_Amount,    0)  AS GST_Amount,
                    COALESCE(i.TDS_Amount,    0)  AS TDS_Amount,
                    COALESCE(i.SD_Amount,     0)  AS SD_Amount,
                    COALESCE(i.On_Commission, 0)  AS On_Commission,
                    COALESCE(i.Hydro_Testing, 0)  AS Hydro_Testing,
                    COALESCE(i.GST_SD_Amount, 0)  AS GST_SD_Amount,
                    COALESCE(i.Final_Amount,  0)  AS Final_Amount,
                    COALESCE(SUM(p.Amount_with_TDS),            0) AS Payment_Amount,
                    COALESCE(SUM(p.TDS_Payment_Amount),         0) AS TDS_Payment_Amount,
                    COALESCE(SUM(p.Amount_after_TDS_Deduction), 0) AS Total_Amount,
                    GROUP_CONCAT(DISTINCT p.UTR ORDER BY p.Payment_Id SEPARATOR ' | ') AS UTR,
                    i.sort_order
                FROM invoices i
                LEFT JOIN villages v ON i.Village_Id = v.Village_Id
                LEFT JOIN payment  p ON p.Invoice_Id  = i.Invoice_Id
                WHERE {inv_where}
                GROUP BY i.Invoice_Id
                ORDER BY i.Invoice_Id ASC
            """, (inv_param,))
            invoices = cursor.fetchall()

            # ── Payment Detail rows ────────────────────────────────────────
            pay_where = "i.PMC_No = %s" if pmc_no else "i.Subcontractor_Id = %s"
            pay_param = pmc_no if pmc_no else contractor_id
            cursor.execute(f"""
                SELECT p.Payment_Id,
                       p.PMC_No,
                       p.invoice_no          AS Invoice_No,
                       p.Amount_with_TDS            AS Payment_Amount,
                       p.TDS_Payment_Amount,
                       p.Amount_after_TDS_Deduction  AS Total_Amount,
                       p.UTR,
                       i.Invoice_Date,
                       i.Invoice_Details
                FROM payment p
                JOIN invoices i ON p.Invoice_Id = i.Invoice_Id
                WHERE {pay_where}
                ORDER BY p.PMC_No ASC, p.Payment_Id ASC
            """, (pay_param,))
            payments = cursor.fetchall()

            # ── Credit Notes ───────────────────────────────────────────────
            credit_notes = (
                ReportHelper.execute_sp(cursor, 'NewGetCreditNotesByPMCNo', [pmc_no])
                if pmc_no else
                ReportHelper.execute_sp(cursor, 'GetCreditNotesByContractor', [contractor_id])
            ) or []

            # ── GST Releases (direct query to include sort_order) ──────────
            if pmc_no:
                cursor.execute("""
                    SELECT GST_Release_Id, PMC_No, Invoice_No, Basic_Amount,
                           Final_Amount, Total_Amount, UTR, Contractor_ID, sort_order
                    FROM gst_releases WHERE PMC_No = %s
                """, (pmc_no,))
            else:
                cursor.execute("""
                    SELECT GST_Release_Id, PMC_No, Invoice_No, Basic_Amount,
                           Final_Amount, Total_Amount, UTR, Contractor_ID, sort_order
                    FROM gst_releases WHERE Contractor_ID = %s
                """, (contractor_id,))
            gst_rel = cursor.fetchall() or []

            # ── Hold Amounts ───────────────────────────────────────────────
            hold_amounts = ReportHelper.execute_sp(cursor, 'GetHoldAmountsByContractor',
                                                   [contractor_id]) or []
            hold_data = {}
            for h in hold_amounts:
                hold_data.setdefault(h["Invoice_Id"], {})[h["hold_type_id"]] = h["hold_amount"]

            # ── Annotate rows — single source of truth for every amount ──────
            # This is the ONLY place paid/balance/status are calculated.
            # Both the template and the Excel download read these fields directly;
            # neither re-derives them.
            for inv in invoices:
                ta  = float(inv.get('Total_Amount')       or 0)
                pa  = float(inv.get('Payment_Amount')     or 0)
                tds = float(inv.get('TDS_Payment_Amount') or 0)
                rp  = round(ta if ta > 0 else pa + tds, 2)
                fa  = float(inv.get('Final_Amount') or 0)
                rb  = round(fa - rp, 2)
                if   rb < -0.01:  rs = 'Excess'
                elif rb <= 0.01:  rs = 'Paid'
                elif rp > 0:      rs = 'Partial'
                else:             rs = 'Pending'
                inv['row_paid']    = rp
                inv['row_balance'] = rb
                inv['row_status']  = rs

            for pay in payments:
                ta  = float(pay.get('Total_Amount')       or 0)
                pa  = float(pay.get('Payment_Amount')     or 0)
                tds = float(pay.get('TDS_Payment_Amount') or 0)
                pay['row_paid'] = round(ta if ta > 0 else pa + tds, 2)

            for cn in credit_notes:
                ta  = float(cn.get('Total_Amount')       or 0)
                pa  = float(cn.get('Payment_Amount')     or 0)
                cn['row_paid'] = round(ta if ta > 0 else pa, 2)

            # ── Maps for template ──────────────────────────────────────────
            credit_note_map = {}
            for cn in credit_notes:
                credit_note_map.setdefault(str(cn.get("PMC_No") or ""), []).append(cn)

            gst_release_map = {}
            for gr in gst_rel:
                gst_release_map.setdefault(str(gr.get("PMC_No") or ""), []).append(gr)

            # ── Unified rows: invoices + GST releases merged in source Excel order ──
            # Each row tagged with _row_type so excel.py can render it correctly.
            # Sort key: sort_order (set during upload from source row index).
            # Fallback when sort_order is NULL: invoices before GST releases, by PK.
            _inv_tagged = [dict(r, _row_type='invoice') for r in invoices]
            _gst_tagged = []
            for _gr in gst_rel:
                _d = dict(_gr)
                _d['invoice_no'] = _d.get('Invoice_No')  # normalise key to match invoice rows
                _d['_row_type'] = 'gst_release'
                _gst_tagged.append(_d)

            def _unified_sort_key(r):
                so = r.get('sort_order')
                if so is not None:
                    return (0, int(so))
                if r['_row_type'] == 'invoice':
                    return (1, int(r.get('Invoice_Id') or 0))
                return (2, int(r.get('GST_Release_Id') or 0))

            unified_rows = sorted(_inv_tagged + _gst_tagged, key=_unified_sort_key)

            # ── Totals — derived from annotated rows, not re-computed ──────
            sum_actual_paid = round(sum(p['row_paid'] for p in payments), 2)
            sum_invo_final  = _fsum(invoices, 'Final_Amount')
            # GST paid: prefer Total_Amount (actual transfer); fall back to Final_Amount
            sum_gst_paid = round(sum(
                float(gr.get('Total_Amount') or 0) if float(gr.get('Total_Amount') or 0) > 0
                else float(gr.get('Final_Amount') or 0)
                for gr in gst_rel
            ), 2)

            total = {
                "sum_invo_basic_amt":       _fsum(invoices, 'Basic_Amount'),
                "sum_invo_debit_amt":       _fsum(invoices, 'Debit_Amount'),
                "sum_invo_after_debit_amt": _fsum(invoices, 'After_Debit_Amount'),
                "sum_invo_amt":             _fsum(invoices, 'Amount'),
                "sum_invo_gst_amt":         _fsum(invoices, 'GST_Amount'),
                "sum_invo_tds_amt":         _fsum(invoices, 'TDS_Amount'),
                "sum_invo_ds_amt":          _fsum(invoices, 'SD_Amount'),
                "sum_invo_on_commission":   _fsum(invoices, 'On_Commission'),
                "sum_invo_hydro_test":      _fsum(invoices, 'Hydro_Testing'),
                "sum_invo_gst_sd_amt":      _fsum(invoices, 'GST_SD_Amount'),
                "sum_invo_final_amt":       sum_invo_final,
                "sum_invo_hold_amt":        round(sum(float(h.get("hold_amount") or 0) for h in hold_amounts), 2),
                "sum_gst_basic_amt":        _fsum(gst_rel, 'Basic_Amount'),
                "sum_gst_final_amt":        _fsum(gst_rel, 'Final_Amount'),
                "sum_gst_total_amt":        _fsum(gst_rel, 'Total_Amount'),
                "sum_pay_payment_amt":      _fsum(payments, 'Payment_Amount'),
                "sum_pay_tds_payment_amt":  _fsum(payments, 'TDS_Payment_Amount'),
                "sum_pay_total_amt":        _fsum(payments, 'Total_Amount'),
                "sum_credit_basic_amt":     _fsum(credit_notes, 'Basic_Amount'),
                "sum_credit_final_amt":     _fsum(credit_notes, 'Final_Amount'),
                "sum_credit_total_amt":     _fsum(credit_notes, 'Total_Amount'),
                "sum_actual_paid":          sum_actual_paid,
                "sum_balance":              round(sum_invo_final - sum_actual_paid, 2),
                "sum_gst_paid":             sum_gst_paid,
            }

            return {
                "info":             info,
                "invoices":         invoices,
                "rows":             unified_rows,   # merged invoice+GST rows in source order
                "hold_types":       hold_types,
                "payments":         payments,
                "hold_data":        hold_data,
                "hold_release":     hold_data,
                "credit_note":      credit_notes,
                "credit_note_map":  credit_note_map,
                "gst_rel":          gst_rel,
                "gst_release_map":  gst_release_map,
                "total":            total,
            }

        finally:
            cursor.close()
            connection.close()

    # ── Excel Download ─────────────────────────────────────────────────────
    @staticmethod
    def download(contractor_id=None, pmc_no=None):
        from model.excel import excel
        report_data = UnifiedReportService.get_report(contractor_id, pmc_no)
        if not report_data:
            return None

        import re as _re
        _cname = (report_data["info"].get("Contractor_Name") or "").strip()
        _safe  = _re.sub(r'[\\/*?:"<>|]', '', _cname) if _cname else ""
        fileName = (
            f"{_safe}.xlsx" if _safe
            else (f"Contractor_Report_{contractor_id}.xlsx" if contractor_id else f"PMC_Report_{pmc_no}.xlsx")
        )
        output_file = FolderAndFile.get_download_path(fileName)

        excel.generate_excel(
            contractor_id or 0,
            report_data["info"],
            report_data["rows"],           # unified invoice+GST rows in source order
            report_data["hold_types"],
            report_data["hold_data"],
            report_data["credit_note_map"],
            report_data["payments"],
            report_data["total"],
            output_file
        )
        return output_file
