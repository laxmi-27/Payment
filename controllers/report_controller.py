import re
from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from io import BytesIO
from decimal import Decimal
from datetime import datetime, date

from model.Report import ReportHelper
from model.Log import LogHelper
from model.UnifiedReportService import UnifiedReportService

report_bp = Blueprint("report", __name__)


def _serialize_row(r):
    """Convert Decimal/date types in a row dict to JSON-safe types."""
    for k, v in r.items():
        if isinstance(v, Decimal):
            r[k] = float(v)
        elif isinstance(v, (date, datetime)):
            r[k] = str(v)


def _row_paid(r):
    """Actual amount paid: prefer the net amount (after TDS); fall back to the gross amount.
    The report query names these columns Total_Amount / Payment_Amount, older versions used
    Amount_after_TDS_Deduction / Amount_with_TDS - accept both."""
    ta = float(r.get('Amount_after_TDS_Deduction') or r.get('Total_Amount') or 0)
    if ta > 0:
        return ta
    return float(r.get('Amount_with_TDS') or r.get('Payment_Amount') or 0)


# ---------------- Report Page ----------------
@report_bp.route("/report")
@login_required
def report_page():
    return render_template("/report.html")


# ---------------- API: All States ----------------
@report_bp.route("/api/report/states")
@login_required
def api_report_states():
    import config
    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT State_Id, State_Name FROM states "
            "WHERE COALESCE(status,'Active')='Active' ORDER BY State_Name"
        )
        rows = cursor.fetchall()
        return jsonify({'states': [{'id': r[0], 'name': r[1]} for r in rows]})
    except Exception as e:
        return jsonify({'states': [], 'error': str(e)})
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


# ---------------- Search Contractor ----------------
@report_bp.route("/search_contractor", methods=["POST"])
@login_required
def search_contractor():
    subcontractor_name = request.form.get("subcontractor_name")
    LogHelper.log_action(
        "Search Contractor",
        f"User {current_user.id} searched contractor '{subcontractor_name}'"
    )

    rows = ReportHelper.search_contractor(request)

    for r in rows:
        _serialize_row(r)

    # Derive summary directly from rows
    total_invoice   = sum(float(r.get('Final_Amount') or 0) for r in rows)
    paid_amount     = sum(_row_paid(r) for r in rows)
    # Allow negative balance so UI can display "Excess Paid / Advance"
    pending_amount  = total_invoice - paid_amount

    pmc_list      = sorted({str(r['PMC_No'])      for r in rows if r.get('PMC_No')})
    state_list    = sorted({r['State_Name']        for r in rows if r.get('State_Name')})
    district_list = sorted({r['District_Name']     for r in rows if r.get('District_Name')})
    village_list  = sorted({r['Village_Name']      for r in rows if r.get('Village_Name')})

    pending_invoices = sum(
        1 for r in rows
        if (float(r.get('Final_Amount') or 0) - _row_paid(r)) > 0.01
    )

    summary = {
        "total_contractors":    len({r['Contractor_Id'] for r in rows if r.get('Contractor_Id')}),
        "total_pmc_records":    len(pmc_list),
        "pmc_list":             pmc_list,
        "states_covered":       len(state_list),
        "state_list":           state_list,
        "districts_covered":    len(district_list),
        "district_list":        district_list,
        "villages_covered":     len(village_list),
        "village_list":         village_list,
        "total_invoice_amount": round(total_invoice, 2),
        "paid_amount":          round(paid_amount, 2),
        "pending_amount":       round(pending_amount, 2),
        "pending_invoices":     pending_invoices,
    }

    return jsonify({"rows": rows, "summary": summary})


# ---------------- Download Filtered Report ----------------
@report_bp.route("/download_filtered_report", methods=["POST"])
@login_required
def download_filtered_report():
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    rows = ReportHelper.search_contractor(request)
    for r in rows:
        _serialize_row(r)

    filters = {
        "Subcontractor Name": request.form.get("subcontractor_name") or "All",
        "PMC No":             request.form.get("pmc_no")             or "All",
        "State":              request.form.get("state")              or "All",
        "District":           request.form.get("district")           or "All",
        "Block":              request.form.get("block")              or "All",
        "Village":            request.form.get("village")            or "All",
        "Date From":          request.form.get("year_from")          or "All",
        "Date To":            request.form.get("year_to")            or "All",
    }

    # Styles
    blue_fill  = PatternFill(start_color="183B70", end_color="183B70", fill_type="solid")
    alt_fill   = PatternFill(start_color="F5F8FF", end_color="F5F8FF", fill_type="solid")
    bold_white = Font(bold=True, color="FFFFFF", size=11)
    bold_blue  = Font(bold=True, color="183B70", size=11)
    thin_side  = Side(style='thin', color="CCCCCC")
    thin_bdr   = Border(bottom=thin_side)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Contractor Report"

    # Title
    ws.merge_cells('A1:Q1')
    ws['A1'] = "Payment Reconciliation — Contractor Report"
    ws['A1'].font = Font(bold=True, size=15, color="183B70")
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 28

    ws['A2'] = f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')}"
    ws['A2'].font = Font(color="888888", size=10)
    ws.append([])

    # Filters
    ws.append(["Applied Filters"])
    ws[f'A{ws.max_row}'].font = bold_blue
    for k, v in filters.items():
        r_idx = ws.max_row + 1
        ws.append([k, str(v)])
        ws[f'A{r_idx}'].font = Font(bold=True, color="555555", size=10)
        ws[f'B{r_idx}'].font = Font(color="333333", size=10)
    ws.append([])

    # ── Fetch hold types + amounts for all contractors in result ─────────
    import config as _cfg
    _hold_types = []
    _hold_data  = {}   # {invoice_id: {hold_type_id: amount}}
    invoice_ids = [r['Invoice_Id'] for r in rows if r.get('Invoice_Id')]
    contractor_ids = list({r['Contractor_Id'] for r in rows if r.get('Contractor_Id')})
    if invoice_ids and contractor_ids:
        _conn = _cfg.get_db_connection()
        try:
            _cur = _conn.cursor(dictionary=True)
            fmt_c = ','.join(['%s'] * len(contractor_ids))
            _cur.execute(
                f"SELECT DISTINCT ht.hold_type_id, ht.hold_type, ht.include_in_hold "
                f"FROM hold_types ht "
                f"JOIN invoice_subcontractor_hold_join ih ON ht.hold_type_id = ih.hold_type_id "
                f"WHERE ih.Contractor_Id IN ({fmt_c})",
                contractor_ids
            )
            _hold_types = _cur.fetchall()
            # SD_Amount / Hydro_Testing / On_Commission already have their own fixed columns.
            # A custom hold type with the same name would show (and count) them twice.
            _fixed_norm = {'sdamount', 'hydrotesting'}
            _hold_types = [h for h in _hold_types
                           if re.sub(r'[\s_]+', '', str(h['hold_type'] or '')).lower() not in _fixed_norm]
            fmt_i = ','.join(['%s'] * len(invoice_ids))
            _cur.execute(
                f"SELECT Invoice_Id, hold_type_id, hold_amount "
                f"FROM invoice_subcontractor_hold_join "
                f"WHERE Invoice_Id IN ({fmt_i})",
                invoice_ids
            )
            for h in _cur.fetchall():
                _hold_data.setdefault(h['Invoice_Id'], {})[h['hold_type_id']] = float(h['hold_amount'] or 0)
            _cur.close()
        except Exception as _he:
            print(f"Hold fetch error: {_he}")
        finally:
            _conn.close()

    # ── Summary ───────────────────────────────────────────────────────────
    def _fv(r, k): return float(r.get(k) or 0)
    inv_rows = [r for r in rows if r.get('Invoice_Details') != 'GST Release Note']
    gst_rows = [r for r in rows if r.get('Invoice_Details') == 'GST Release Note']

    total_inv   = sum(_fv(r, 'Final_Amount') for r in rows)
    paid        = sum(_row_paid(r) for r in rows)
    hold_sd     = sum(_fv(r, 'SD_Amount')     for r in inv_rows)
    hold_ht     = sum(_fv(r, 'Hydro_Testing') for r in inv_rows)
    # hold_amt finalized after custom_hold_totals is built below
    surplus     = round(total_inv - paid, 2)

    # Balance to Debit = sum from balance_to_debit table for matching contractors
    balance_to_debit = 0.0
    if contractor_ids:
        try:
            _conn2 = _cfg.get_db_connection()
            _cur2  = _conn2.cursor()
            _fmt   = ','.join(['%s'] * len(contractor_ids))
            _cur2.execute(
                f"SELECT COALESCE(SUM(balance_debit),0) FROM balance_to_debit "
                f"WHERE contractor_id IN ({_fmt})",
                contractor_ids
            )
            balance_to_debit = round(float(_cur2.fetchone()[0] or 0), 2)
            _cur2.close()
            _conn2.close()
        except Exception as _de:
            print(f"Balance to debit fetch error: {_de}")

    # GST Remaining = invoice GST_Amount total - GST already raised as release notes
    gst_amount_total  = round(sum(_fv(r, 'GST_Amount')   for r in inv_rows), 2)
    gst_release_final = round(sum(_fv(r, 'Final_Amount') for r in gst_rows), 2)
    gst_remaining     = round(gst_amount_total - gst_release_final, 2)
    custom_hold_totals = {}
    for ht in _hold_types:
        custom_hold_totals[ht['hold_type_id']] = round(
            sum(_hold_data.get(r.get('Invoice_Id'), {}).get(ht['hold_type_id'], 0) for r in inv_rows), 2)
    # Include only non-DPR custom holds in Hold total (include_in_hold=1), matching source Excel formula
    hold_custom_sum = sum(
        amt for ht, amt in zip(_hold_types, custom_hold_totals.values())
        if ht.get('include_in_hold', 1)
    )
    hold_amt = round(hold_sd + hold_ht + hold_custom_sum, 2)

    # ── Hold releases: subtract each release from the hold column it belongs to ──
    from model.HoldReleaseSummary import get_release_totals, sum_by_type, sum_fixed
    _pmc_set       = {str(r.get('PMC_No') or '').strip() for r in rows if r.get('PMC_No')}
    _rel           = get_release_totals(contractor_ids, pmc_nos=_pmc_set)
    rel_by_type    = sum_by_type(_rel)                       # {hold_type_id: released}
    rel_fixed      = sum_fixed(_rel)                         # {'SD_Amount': released, ...}
    rel_unassigned = round(sum(_rel['unassigned'].values()), 2)

    # Remaining (net) hold per custom hold type = gross - released
    remaining_by_type = {
        ht['hold_type_id']: round(custom_hold_totals.get(ht['hold_type_id'], 0)
                                  - rel_by_type.get(ht['hold_type_id'], 0), 2)
        for ht in _hold_types
    }
    hold_custom_net = sum(
        remaining_by_type[ht['hold_type_id']] for ht in _hold_types if ht.get('include_in_hold', 1)
    )
    # Hold = (SD + OC + HT + custom holds) - everything released
    hold_amt = round(
        (hold_sd - rel_fixed['SD_Amount'])
        + (hold_ht - rel_fixed['Hydro_Testing'])
        + hold_custom_net
        - rel_unassigned, 2)

    ws.append(["Summary"])
    ws[f'A{ws.max_row}'].font = bold_blue

    def _sum_row(label, val, bold=False, color=None):
        r_idx = ws.max_row + 1
        ws.append([label, val])
        ws[f'A{r_idx}'].font = Font(bold=bold, color="555555", size=10)
        ws[f'B{r_idx}'].font = Font(bold=bold, color="333333", size=10)
        if color:
            ws[f'B{r_idx}'].fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

    _sum_row("Balance to Debit", balance_to_debit)
    _sum_row("Advance/ Surplus", surplus,
             color="C6EFCE" if surplus >= 0 else "FFC7CE")
    _sum_row("GST Remaining",   gst_remaining)
    _sum_row("Total Hold",      hold_amt,    bold=True, color="FFE699")
    # Fixed hold columns: REMAINING hold (gross - released)
    for _lbl, _gross, _fx in (("SD_Amount", hold_sd, 'SD_Amount'),
                              ("Hydro_Testing", hold_ht, 'Hydro_Testing')):
        _rel_fx = rel_fixed.get(_fx, 0)
        if _gross or _rel_fx:
            _sum_row(_lbl, round(_gross - _rel_fx, 2))
            ws.cell(row=ws.max_row, column=3,
                    value=f"Gross {_gross:,.2f} - Released {_rel_fx:,.2f}").font = Font(italic=True, color="888888", size=9)
    # Custom hold types: REMAINING hold (gross - released), with the breakdown beside it
    for ht in _hold_types:
        gross    = custom_hold_totals.get(ht['hold_type_id'], 0)
        released = rel_by_type.get(ht['hold_type_id'], 0)
        if gross or released:
            _sum_row(ht['hold_type'], round(gross - released, 2))
            ws.cell(row=ws.max_row, column=3,
                    value=f"Gross {gross:,.2f} - Released {released:,.2f}").font = Font(italic=True, color="888888", size=9)
    if rel_unassigned:
        _sum_row("Unassigned hold release (set column in Hold Release page)", rel_unassigned, color="FFC7CE")
    ws.append([])

    # ── Table headers ─────────────────────────────────────────────────────
    base_headers = [
        "Contractor Name", "PMC No", "State", "District", "Block", "Village",
        "Invoice Date", "Invoice No", "Invoice Details",
        "Basic Amount", "Debit", "After Debit Amount", "GST Amount", "Amount",
        "TDS Amount", "SD Amount", "Hydro Testing",
        "GST SD Amount",
    ]
    hold_headers = [ht['hold_type'] for ht in _hold_types]
    end_headers  = ["Final Amount", "Paid Amount", "UTR", "Balance", "Village Wise Advance", "Status"]
    headers = base_headers + hold_headers + end_headers
    ws.append(headers)
    hdr_row = ws.max_row
    for cell in ws[hdr_row]:
        cell.font      = bold_white
        cell.fill      = blue_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[hdr_row].height = 20

    # ── Village Wise Advance per PMC group ───────────────────────────────
    from collections import Counter, defaultdict as _dd
    _pmc_final_map = _dd(float)
    _pmc_paid_map  = _dd(float)
    _pmc_last_idx  = {}
    for _i, _r in enumerate(rows):
        _p = str(_r.get('PMC_No') or '').strip()
        _pmc_final_map[_p] += float(_r.get('Final_Amount') or 0)
        _pmc_paid_map[_p]  += _row_paid(_r)
        _pmc_last_idx[_p] = _i
    _vwa_by_pmc = {p: round(_pmc_final_map[p] - _pmc_paid_map[p], 2) for p in _pmc_final_map}

    # ── Detect duplicate UTRs ─────────────────────────────────────────────
    _utr_counts = Counter(
        str(r.get('UTR') or '').strip()
        for r in rows if str(r.get('UTR') or '').strip()
    )
    _dup_utrs   = {u for u, c in _utr_counts.items() if c > 1}
    _dup_fill   = PatternFill(start_color="FF6600", end_color="FF6600", fill_type="solid")
    # UTR column index (1-based): 18 base cols + hold cols + Final + Paid + UTR
    _utr_col    = 18 + len(_hold_types) + 3

    # ── Data rows ─────────────────────────────────────────────────────────
    for i, r in enumerate(rows):
        def v(key):  return r.get(key) or ''
        def fv(key): return float(r.get(key) or 0)
        row_paid    = _row_paid(r)
        row_balance = fv('Final_Amount') - row_paid
        if row_balance < -0.01:   row_status = 'Excess'
        elif row_balance <= 0.01: row_status = 'Paid'
        elif row_paid > 0:        row_status = 'Partial'
        else:                     row_status = 'Pending'

        _pmc_key = str(r.get('PMC_No') or '').strip()
        data_row = [
            v('Contractor_Name'), v('PMC_No'), v('State_Name'), v('District_Name'),
            v('Block_Name'), v('Village_Name'), str(v('Invoice_Date')), v('Invoice_No'),
            v('Invoice_Details'),
            fv('Basic_Amount'), fv('Debit_Amount'), fv('After_Debit_Amount'),
            fv('GST_Amount'), fv('Amount'),
            fv('TDS_Amount'), fv('SD_Amount'), fv('Hydro_Testing'),
            fv('GST_SD_Amount'),
        ]
        inv_holds = _hold_data.get(r.get('Invoice_Id'), {})
        for ht in _hold_types:
            data_row.append(round(float(inv_holds.get(ht['hold_type_id'], 0) or 0), 2))
        vwa_val = _vwa_by_pmc.get(_pmc_key, '') if i == _pmc_last_idx.get(_pmc_key) else ''
        data_row += [fv('Final_Amount'), round(row_paid, 2), v('UTR'),
                     round(row_balance, 2), vwa_val, row_status]
        ws.append(data_row)

        dr = ws.max_row
        fill = alt_fill if i % 2 == 0 else None
        for cell in ws[dr]:
            if fill: cell.fill = fill
            cell.border = thin_bdr
            cell.font   = Font(size=10)

        # Highlight UTR cell orange if duplicate
        utr_val = str(r.get('UTR') or '').strip()
        if utr_val and utr_val in _dup_utrs:
            ws.cell(row=dr, column=_utr_col).fill = _dup_fill
            ws.cell(row=dr, column=_utr_col).font = Font(bold=True, size=10, color="FFFFFF")

    # ── Totals row ────────────────────────────────────────────────────────
    if rows:
        tot_fill_row = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        # 9 non-numeric leading columns: Contractor Name … Invoice Details
        tot_row = ["Total", "", "", "", "", "", "", "", ""]
        tot_row += [
            round(sum(float(r.get('Basic_Amount')        or 0) for r in rows), 2),
            round(sum(float(r.get('Debit_Amount')        or 0) for r in rows), 2),
            round(sum(float(r.get('After_Debit_Amount')  or 0) for r in rows), 2),
            round(sum(float(r.get('GST_Amount')          or 0) for r in rows), 2),
            round(sum(float(r.get('Amount')              or 0) for r in rows), 2),
            round(sum(float(r.get('TDS_Amount')          or 0) for r in rows), 2),
            round(sum(float(r.get('SD_Amount')           or 0) for r in rows), 2),
            round(sum(float(r.get('Hydro_Testing')       or 0) for r in rows), 2),
            round(sum(float(r.get('GST_SD_Amount')       or 0) for r in rows), 2),
        ]
        for ht in _hold_types:
            tot_row.append(round(
                sum(float(_hold_data.get(r.get('Invoice_Id'), {}).get(ht['hold_type_id'], 0) or 0) for r in rows), 2
            ))
        tot_row += [
            round(sum(float(r.get('Final_Amount') or 0) for r in rows), 2),
            round(sum(_row_paid(r) for r in rows), 2),
            "", "", "", "",  # UTR, Balance, Village Wise Advance, Status — not summed
        ]
        ws.append(tot_row)
        for cell in ws[ws.max_row]:
            cell.fill   = tot_fill_row
            cell.font   = Font(bold=True, size=10)
            cell.border = thin_bdr

    # Number format for amount columns
    amt_start = 10
    amt_end   = 10 + len(base_headers) - 9 + len(hold_headers) + 1  # through Final+Paid (excludes UTR)
    for row in ws.iter_rows(min_row=hdr_row + 1, max_row=ws.max_row,
                            min_col=amt_start, max_col=amt_end):
        for cell in row:
            cell.number_format = '#,##0.00'

    # Auto-fit column widths
    for col in ws.columns:
        max_len = max((len(str(cell.value)) for cell in col if cell.value), default=8)
        ws.column_dimensions[openpyxl.utils.get_column_letter(col[0].column)].width = min(max_len + 3, 40)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    _cname = request.form.get("subcontractor_name", "").strip()
    _safe  = re.sub(r'[\\/*?:"<>|]', '', _cname) if _cname else ""
    filename = f"{_safe}.xlsx" if _safe else f"contractor_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(
        buf, as_attachment=True, download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


# ---------------- Summary Dashboard ----------------
@report_bp.route('/summary_dashboard')
@login_required
def summary_dashboard():
    return render_template('summary_dashboard.html')


@report_bp.route('/api/summary_dashboard', methods=['POST'])
@login_required
def api_summary_dashboard():
    from model.SummaryDashboard import SummaryDashboard
    filters = {
        'subcontractor_name': request.form.get('subcontractor_name'),
        'state':              request.form.get('state'),
        'district':           request.form.get('district'),
        'block':              request.form.get('block'),
        'village':            request.form.get('village'),
    }
    try:
        rows, hold_types = SummaryDashboard.get_summary(filters)
        # JSON-safe
        for r in rows:
            for k, v in r.items():
                if hasattr(v, '__float__'):
                    r[k] = float(v)
        return jsonify({'rows': rows, 'hold_types': hold_types})
    except Exception as e:
        return jsonify({'rows': [], 'hold_types': [], 'error': str(e)})


# ---------------- Contractor Report by contractor id ----------------
@report_bp.route('/contractor_report/<int:contractor_id>')
@login_required
def contractor_report(contractor_id):
    data = UnifiedReportService.get_report(contractor_id=contractor_id)
    if not data:
        return render_template('subcontractor_report.html',
                               contractor_id=contractor_id,
                               info={}, invoices=[], payments=[],
                               credit_note=[], gst_rel=[], hold_types=[],
                               hold_data={}, credit_note_map={}, gst_release_map={},
                               total={k: 0 for k in [
                                   'sum_invo_basic_amt','sum_invo_debit_amt',
                                   'sum_invo_after_debit_amt','sum_invo_amt',
                                   'sum_invo_gst_amt','sum_invo_tds_amt',
                                   'sum_invo_ds_amt','sum_invo_on_commission',
                                   'sum_invo_hydro_test','sum_invo_gst_sd_amt',
                                   'sum_invo_final_amt','sum_invo_hold_amt',
                                   'sum_gst_basic_amt','sum_gst_final_amt',
                                   'sum_gst_total_amt','sum_gst_paid',
                                   'sum_pay_payment_amt',
                                   'sum_pay_tds_payment_amt','sum_pay_total_amt',
                                   'sum_credit_basic_amt','sum_credit_final_amt',
                                   'sum_credit_total_amt','sum_actual_paid','sum_balance',
                               ]})
    # DEBUG — printed to server console for verification
    print(f"[DEBUG] contractor_report contractor_id={contractor_id}")
    print(f"[DEBUG]   contractor_details_count = 1")
    print(f"[DEBUG]   invoice_count            = {len(data.get('invoices', []))}")
    print(f"[DEBUG]   payment_count            = {len(data.get('payments', []))}")
    print(f"[DEBUG]   credit_count             = {len(data.get('credit_note', []))}")
    print(f"[DEBUG]   gst_release_count        = {len(data.get('gst_rel', []))}")
    print(f"[DEBUG]   hold_types_count         = {len(data.get('hold_types', []))}")
    print(f"[DEBUG]   total_keys               = {list(data.get('total', {}).keys())}")
    return render_template('subcontractor_report.html', contractor_id=contractor_id, **data)


# ---------------- Contractor Download Report by contractor id ----------------
@report_bp.route('/download_report/<int:contractor_id>')
@login_required
def download_report(contractor_id):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    data = UnifiedReportService.get_report(contractor_id=contractor_id)
    if not data:
        return "Contractor not found", 404

    info      = data["info"]
    invoices  = data["invoices"]
    payments  = data["payments"]
    credit    = data["credit_note"]
    gst_rel   = data["gst_rel"]
    hold_types= data["hold_types"]
    hold_data = data["hold_data"]
    total     = data["total"]

    # ── Styles ──────────────────────────────────────────────────────────
    hdr_fill  = PatternFill(start_color="183B70", end_color="183B70", fill_type="solid")
    alt_fill  = PatternFill(start_color="F5F8FF", end_color="F5F8FF", fill_type="solid")
    tot_fill  = PatternFill(start_color="E8F0FE", end_color="E8F0FE", fill_type="solid")
    sec_fill  = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
    bold_w    = Font(bold=True, color="FFFFFF", size=11)
    bold_b    = Font(bold=True, color="183B70", size=11)
    bold_blk  = Font(bold=True, size=11)
    thin      = Side(style='thin', color="DDDDDD")
    thin_bdr  = Border(bottom=thin)
    center    = Alignment(horizontal='center', vertical='center')

    def _hdr_row(ws, cells):
        ws.append(cells)
        r = ws.max_row
        for c in ws[r]:
            c.font = bold_w; c.fill = hdr_fill; c.alignment = center
        ws.row_dimensions[r].height = 18
        return r

    def _tot_row(ws, cells):
        ws.append(cells)
        r = ws.max_row
        for c in ws[r]:
            c.font = bold_blk; c.fill = tot_fill; c.border = thin_bdr
        return r

    def _sec_row(ws, label):
        ws.append([label])
        r = ws.max_row
        ws[f'A{r}'].font = Font(bold=True, size=12, color="183B70")
        ws[f'A{r}'].fill = sec_fill
        ws.row_dimensions[r].height = 18

    def fv(v):
        return round(float(v or 0), 2)

    def txt(v):
        s = str(v).strip() if v is not None else ''
        return s if s and s not in ('-', '--', 'None', 'N/A', 'null') else 'Not provided'

    # NOTE: row_paid / row_status are PRE-COMPUTED in get_report() and stored on each row.
    # This function does NOT recalculate them — it reads what get_report() already set.

    wb  = openpyxl.Workbook()
    ws  = wb.active
    ws.title = "Contractor Report"

    # ── Title ────────────────────────────────────────────────────────────
    ws.merge_cells('A1:S1')
    ws['A1'] = "Payment Reconciliation — Contractor Full Report"
    ws['A1'].font = Font(bold=True, size=16, color="183B70")
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30
    ws['A2'] = f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')}"
    ws['A2'].font = Font(color="888888", size=10)
    ws.append([])

    # ── Report Statistics ─────────────────────────────────────────────────
    stats = [
        ("Invoice Records", len(invoices)),
        ("Payment Records", len(payments)),
        ("GST Releases",    len(gst_rel)),
    ]
    for lbl, val in stats:
        r_idx = ws.max_row + 1
        ws.append([lbl, val])
        ws[f'A{r_idx}'].font = Font(bold=True, color="555555", size=10)
        ws[f'B{r_idx}'].font = Font(color="183B70", size=10, bold=True)
    ws.append([])

    # ── 1. Contractor Details ─────────────────────────────────────────────
    _sec_row(ws, "1. CONTRACTOR DETAILS")
    fields = [
        ("Contractor Name",        info.get("Contractor_Name") or "Not provided"),
        ("PAN No",                 info.get("PAN_No")          or "Not provided"),
        ("Mobile",                 info.get("Mobile_No")       or "Not provided"),
        ("Email",                  info.get("Email")           or "Not provided"),
        ("GST Registration Type",  info.get("GST_Registration_Type") or "Not provided"),
        ("GST No",                 info.get("GST_No")          or "Not provided"),
        ("State",                  info.get("State_Name")      or "Not provided"),
        ("District",               info.get("District_Name")   or "Not provided"),
        ("Block",                  info.get("Block_Name")      or "Not provided"),
        ("Address",                info.get("Address")         or "Not provided"),
    ]
    for lbl, val in fields:
        ws.append([lbl, str(val)])
        r = ws.max_row
        ws[f'A{r}'].font = Font(bold=True, color="555555", size=10)
        ws[f'B{r}'].font = Font(color="333333", size=10)
    ws.append([])

    # ── 2. Invoice Details ────────────────────────────────────────────────
    _sec_row(ws, "2. INVOICE DETAILS")
    inv_hdrs = ["#", "PMC No", "Invoice Date", "Invoice No", "Village",
                "Invoice Details", "Basic Amt", "Debit", "After Debit",
                "GST", "Amount", "TDS", "SD", "Commission", "Hydro"]
    for ht in hold_types:
        inv_hdrs.append(ht['hold_type'])
    inv_hdrs += ["GST SD", "Final Amt", "Paid Amt", "UTR", "Status"]
    _hdr_row(ws, inv_hdrs)

    for idx, inv in enumerate(invoices, 1):
        # Use pre-computed row_paid / row_status from get_report() — single source of truth
        row = [idx, txt(inv.get('PMC_No')), str(inv.get('Invoice_Date') or ''),
               txt(inv.get('invoice_no')), txt(inv.get('Village_Name')),
               txt(inv.get('Invoice_Details')),
               fv(inv.get('Basic_Amount')), fv(inv.get('Debit_Amount')),
               fv(inv.get('After_Debit_Amount')), fv(inv.get('GST_Amount')),
               fv(inv.get('Amount')), fv(inv.get('TDS_Amount')),
               fv(inv.get('SD_Amount')), fv(inv.get('On_Commission')),
               fv(inv.get('Hydro_Testing'))]
        inv_holds = hold_data.get(inv['Invoice_Id'], {})
        for ht in hold_types:
            row.append(fv(inv_holds.get(ht['hold_type_id'], 0)))
        row += [fv(inv.get('GST_SD_Amount')), fv(inv.get('Final_Amount')),
                inv['row_paid'], txt(inv.get('UTR')), inv['row_status']]
        ws.append(row)
        dr = ws.max_row
        if idx % 2 == 0:
            for c in ws[dr]:
                c.fill = alt_fill
        for c in ws[dr]:
            c.border = thin_bdr; c.font = Font(size=10)

    # Compute per-hold-type totals from hold_data
    hold_totals = {ht['hold_type_id']: 0.0 for ht in hold_types}
    for inv in invoices:
        inv_holds = hold_data.get(inv['Invoice_Id'], {})
        for ht in hold_types:
            hold_totals[ht['hold_type_id']] += float(inv_holds.get(ht['hold_type_id'], 0) or 0)

    # Invoice totals row
    tot_row_data = ["", "Total", "", "", "", "",
                    total['sum_invo_basic_amt'], total['sum_invo_debit_amt'],
                    total['sum_invo_after_debit_amt'], total['sum_invo_gst_amt'],
                    total['sum_invo_amt'], total['sum_invo_tds_amt'],
                    total['sum_invo_ds_amt'], total['sum_invo_on_commission'],
                    total['sum_invo_hydro_test']]
    for ht in hold_types:
        tot_row_data.append(round(hold_totals.get(ht['hold_type_id'], 0), 2))
    tot_row_data += [total['sum_invo_gst_sd_amt'], total['sum_invo_final_amt'],
                     total['sum_actual_paid'], '', '']
    _tot_row(ws, tot_row_data)
    ws.append([])

    # ── 3. Payment Details ────────────────────────────────────────────────
    _sec_row(ws, "3. PAYMENT DETAILS")
    _hdr_row(ws, ["#", "PMC No", "Invoice No", "Invoice Date", "Invoice Details",
                  "Payment Amt", "TDS Payment", "Total Paid", "UTR"])
    for idx, pay in enumerate(payments, 1):
        # pay['row_paid'] pre-computed in get_report() — single source of truth
        ws.append([idx, txt(pay.get('PMC_No')), txt(pay.get('Invoice_No')),
                   str(pay.get('Invoice_Date') or ''), txt(pay.get('Invoice_Details')),
                   fv(pay.get('Payment_Amount')), fv(pay.get('TDS_Payment_Amount')),
                   pay['row_paid'], txt(pay.get('UTR'))])
        dr = ws.max_row
        if idx % 2 == 0:
            for c in ws[dr]: c.fill = alt_fill
        for c in ws[dr]:
            c.border = thin_bdr; c.font = Font(size=10)
    if payments:
        _tot_row(ws, ["", "Total", "", "", "",
                      total['sum_pay_payment_amt'], total['sum_pay_tds_payment_amt'],
                      total['sum_actual_paid'], ''])
    else:
        ws.append(["No payment records found."])
    ws.append([])

    # ── Credit Details (no section number — conditional) ─────────────────
    if credit:
        _sec_row(ws, "CREDIT / DEBIT DETAILS")
        _hdr_row(ws, ["#", "PMC No", "Invoice No", "Invoice Details",
                      "Basic Amt", "Debit", "After Debit", "GST", "Amount",
                      "Final Amt", "Payment Amt", "Total Paid", "UTR"])
        for idx, cn in enumerate(credit, 1):
            # cn['row_paid'] pre-computed in get_report() — single source of truth
            ws.append([idx, txt(cn.get('PMC_No')), txt(cn.get('invoice_no')),
                       txt(cn.get('Invoice_Details')),
                       fv(cn.get('Basic_Amount')), fv(cn.get('Debit_Amount')),
                       fv(cn.get('After_Debit_Amount')), fv(cn.get('GST_Amount')),
                       fv(cn.get('Amount')), fv(cn.get('Final_Amount')),
                       fv(cn.get('Payment_Amount')), cn['row_paid'],
                       txt(cn.get('UTR'))])
            dr = ws.max_row
            if idx % 2 == 0:
                for c in ws[dr]: c.fill = alt_fill
            for c in ws[dr]:
                c.border = thin_bdr; c.font = Font(size=10)
        _tot_row(ws, ["", "Total", "", "",
                      total['sum_credit_basic_amt'], '', '', '', '',
                      total['sum_credit_final_amt'], '', total['sum_credit_total_amt'], ''])
        ws.append([])

    # ── 4. GST Release Notes ─────────────────────────────────────────────
    if gst_rel:
        _sec_row(ws, "4. GST RELEASE NOTES")
        _hdr_row(ws, ["#", "PMC No", "Invoice No", "GST Date", "Basic Amt", "Final Amt",
                      "Total Paid", "UTR"])
        for idx, gst in enumerate(gst_rel, 1):
            ws.append([idx, txt(gst.get('PMC_No')), txt(gst.get('Invoice_No')),
                       str(gst.get('Invoice_Date') or ''),
                       fv(gst.get('Basic_Amount')), fv(gst.get('Final_Amount')),
                       fv(gst.get('Total_Amount')), txt(gst.get('UTR'))])
            dr = ws.max_row
            if idx % 2 == 0:
                for c in ws[dr]: c.fill = alt_fill
            for c in ws[dr]:
                c.border = thin_bdr; c.font = Font(size=10)
        _tot_row(ws, ["", "Total", "", "",
                      total['sum_gst_basic_amt'], total['sum_gst_final_amt'],
                      total['sum_gst_total_amt'], ''])
        ws.append([])

    # ── 5. Balance / Status Summary ───────────────────────────────────────
    _sec_row(ws, "5. BALANCE / STATUS SUMMARY")
    balance = total['sum_balance']
    if balance < -0.01:
        bal_label = "Excess / Advance Paid"
        bal_val   = abs(balance)
    elif balance > 0.01:
        bal_label = "Pending Amount"
        bal_val   = balance
    else:
        bal_label = "Status"
        bal_val   = "Fully Paid"

    # Fetch Balance to Debit for this contractor
    _btd_val = 0.0
    try:
        _btd_conn = _cfg.get_db_connection()
        _btd_cur  = _btd_conn.cursor()
        _btd_cur.execute(
            "SELECT COALESCE(SUM(balance_debit),0) FROM balance_to_debit WHERE contractor_id = %s",
            (contractor_id,)
        )
        _btd_val = round(float(_btd_cur.fetchone()[0] or 0), 2)
        _btd_cur.close()
        _btd_conn.close()
    except Exception:
        pass

    summary_rows = [
        ("Total Invoice Amount",   total['sum_invo_final_amt']),
        ("Total Paid",             total['sum_actual_paid']),
        (bal_label,                bal_val),
        ("Balance to Debit",       _btd_val),
        ("Total Hold Amount",      total['sum_invo_hold_amt']),
        ("GST Release Total",      total.get('sum_gst_paid', total['sum_gst_final_amt'])),
        ("Invoice Records",        len(invoices)),
        ("Payment Records",        len(payments)),
        ("GST Releases",           len(gst_rel)),
    ]
    for lbl, val in summary_rows:
        ws.append([lbl, val])
        r = ws.max_row
        ws[f'A{r}'].font = Font(bold=True, color="555555", size=10)
        ws[f'B{r}'].font = Font(color="183B70", size=11, bold=True)

    # ── Column widths ─────────────────────────────────────────────────────
    for col in ws.columns:
        max_len = 0
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    max_len = max(max_len, min(len(str(cell.value)), 50))
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = max(max_len + 3, 10)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    _cname = (info.get("Contractor_Name") or "").strip()
    _safe  = re.sub(r'[\\/*?:"<>|]', '', _cname) if _cname else ""
    fname  = f"{_safe}.xlsx" if _safe else f"contractor_{contractor_id}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(buf, as_attachment=True, download_name=fname,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')