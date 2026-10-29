"""
Shared helper: how much of each hold column has been released.

Used by report_controller.py, SummaryDashboard.py and excel.py so that
Hold and every hold-type row in the Summary show  Gross - Released = Remaining.
"""
import config

FIXED_HOLDS = ('SD_Amount', 'Hydro_Testing')


def get_release_totals(contractor_ids, pmc_nos=None):
    """
    Returns dict:
      by_type    : {contractor_id: {hold_type_id: released_amount}}
      fixed      : {contractor_id: {'SD_Amount': amt, 'Hydro_Testing': amt}}
      unassigned : {contractor_id: amount}   (releases with no column chosen)
      notes      : {(pmc, invoice_no): column_name}  -> "Hold Released From" report column
    """
    out = {'by_type': {}, 'fixed': {}, 'unassigned': {}, 'notes': {}}
    if not contractor_ids:
        return out

    conn = config.get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        fmt = ','.join(['%s'] * len(contractor_ids))
        sql = f"""
            SELECT hr.Contractor_Id, hr.PMC_No, hr.Invoice_No, hr.Final_Amount,
                   hr.hold_type_id, hr.fixed_hold, ht.hold_type
            FROM hold_release hr
            LEFT JOIN hold_types ht ON ht.hold_type_id = hr.hold_type_id
            WHERE hr.Contractor_Id IN ({fmt})
        """
        params = list(contractor_ids)
        if pmc_nos:                       # report filtered by PMC -> only that PMC's releases
            sql += f" AND hr.PMC_No IN ({','.join(['%s'] * len(pmc_nos))})"
            params += list(pmc_nos)
        cur.execute(sql, params)
        for r in cur.fetchall():
            cid = r['Contractor_Id']
            amt = float(r['Final_Amount'] or 0)
            if r['hold_type_id']:
                d = out['by_type'].setdefault(cid, {})
                d[r['hold_type_id']] = round(d.get(r['hold_type_id'], 0.0) + amt, 2)
                col = r['hold_type']
            elif r['fixed_hold']:
                d = out['fixed'].setdefault(cid, {})
                d[r['fixed_hold']] = round(d.get(r['fixed_hold'], 0.0) + amt, 2)
                col = r['fixed_hold']
            else:
                out['unassigned'][cid] = round(out['unassigned'].get(cid, 0.0) + amt, 2)
                col = 'Unassigned'
            _pmc = str(r['PMC_No'] or '').strip()
            _inv = str(r['Invoice_No'] or '').strip()
            out['notes'][(_pmc, _inv)] = col                    # old key (kept for other reports)
            out['notes'][(_pmc, _inv, f"{amt:.2f}")] = col      # exact key: pmc + invoice + amount
        cur.close()
    finally:
        conn.close()
    return out


def sum_by_type(release, contractor_ids=None):
    """{hold_type_id: total released across the given contractors}"""
    total = {}
    for cid, d in release['by_type'].items():
        if contractor_ids is not None and cid not in contractor_ids:
            continue
        for tid, amt in d.items():
            total[tid] = round(total.get(tid, 0.0) + amt, 2)
    return total


def sum_fixed(release, contractor_ids=None):
    total = {k: 0.0 for k in FIXED_HOLDS}
    for cid, d in release['fixed'].items():
        if contractor_ids is not None and cid not in contractor_ids:
            continue
        for k, amt in d.items():
            total[k] = round(total.get(k, 0.0) + amt, 2)
    return total


def infer_target(cursor, contractor_id, pmc_no, invoice_no, amount):
    """
    Used by Excel upload when the sheet has no 'Hold_Column'.
    Returns (hold_type_id, fixed_hold) or (None, None).

    1. Exact amount match against ONE hold on the same invoice (works for 4,5,6,7).
    2. Otherwise the hold type this contractor has released most often
       (part payments such as '8 - Part 1', '8 - Part 2').
    """
    base_inv = str(invoice_no or '').split('-')[0].strip()
    try:
        cursor.execute("""
            SELECT i.Invoice_Id, i.SD_Amount, i.Hydro_Testing
            FROM invoices i
            WHERE i.Subcontractor_Id = %s AND i.PMC_No = %s AND i.Invoice_No = %s
              AND i.Invoice_Details NOT LIKE '%%Release%%'
            LIMIT 1
        """, (contractor_id, pmc_no, base_inv))
        inv = cursor.fetchone()
        if inv:
            cands = [('fixed', k, float(v or 0)) for k, v in
                     zip(FIXED_HOLDS, (inv[1], inv[2]))]
            cursor.execute("SELECT hold_type_id, hold_amount FROM invoice_subcontractor_hold_join "
                           "WHERE Invoice_Id = %s", (inv[0],))
            cands += [('type', int(t), float(a or 0)) for t, a in cursor.fetchall()]
            exact = [c for c in cands if abs(c[2] - float(amount or 0)) < 0.01 and c[2] > 0]
            if len(exact) == 1:
                return (exact[0][1], None) if exact[0][0] == 'type' else (None, exact[0][1])
            if len(exact) > 1:
                # Same amount matches several holds (e.g. SD 5% and Hydro 5% are equal).
                # Do not guess: leave it unassigned so it is flagged in the report.
                return None, None

        cursor.execute("""
            SELECT hold_type_id, COUNT(*) c FROM hold_release
            WHERE Contractor_Id = %s AND hold_type_id IS NOT NULL
            GROUP BY hold_type_id ORDER BY c DESC LIMIT 1
        """, (contractor_id,))
        row = cursor.fetchone()
        if row:
            return row[0], None
    except Exception as e:
        print("infer_target error:", e)
    return None, None