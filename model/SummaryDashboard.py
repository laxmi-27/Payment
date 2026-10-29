import config
from model.HoldReleaseSummary import get_release_totals


class SummaryDashboard:

    @staticmethod
    def get_summary(filters=None):
        """
        Returns (rows, hold_types) for the summary dashboard.
        Each row is one contractor with aggregated financial summary columns.
        """
        connection = config.get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            # ── Build location + name filter WHERE clause ──────────────────
            conditions = []
            params = []
            if filters:
                if filters.get('subcontractor_name'):
                    conditions.append("LOWER(s.Contractor_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
                    params.append(filters['subcontractor_name'])
                if filters.get('state'):
                    conditions.append("LOWER(st.State_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
                    params.append(filters['state'])
                if filters.get('district'):
                    conditions.append("LOWER(d.District_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
                    params.append(filters['district'])
                if filters.get('block'):
                    conditions.append("LOWER(b.Block_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
                    params.append(filters['block'])
                if filters.get('village'):
                    conditions.append("LOWER(v.Village_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
                    params.append(filters['village'])

            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            # ── Main per-contractor aggregation ────────────────────────────
            # Payments are pre-aggregated per invoice to avoid M×N row explosion.
            cursor.execute(f"""
                SELECT
                    s.Contractor_Id,
                    s.Contractor_Name,
                    GROUP_CONCAT(DISTINCT st.State_Name    ORDER BY st.State_Name    SEPARATOR ', ') AS states,
                    GROUP_CONCAT(DISTINCT d.District_Name  ORDER BY d.District_Name  SEPARATOR ', ') AS districts,
                    COALESCE(SUM(i.Basic_Amount),     0) AS total_basic,
                    COALESCE(SUM(i.Debit_Amount),     0) AS total_debit_col,
                    COALESCE(SUM(i.GST_Amount),       0) AS total_gst,
                    COALESCE(SUM(i.TDS_Amount),       0) AS total_tds,
                    COALESCE(SUM(i.SD_Amount),        0) AS total_sd,
                    COALESCE(SUM(i.On_Commission),    0) AS total_oc,
                    COALESCE(SUM(i.Hydro_Testing),    0) AS total_ht,
                    COALESCE(SUM(i.GST_SD_Amount),    0) AS total_gst_sd,
                    COALESCE(SUM(i.Final_Amount),     0) AS total_final,
                    COALESCE(SUM(inv_pay.paid),       0) AS total_paid
                FROM subcontractors s
                LEFT JOIN invoices i ON i.Subcontractor_Id = s.Contractor_Id
                LEFT JOIN (
                    SELECT Invoice_Id,
                           COALESCE(SUM(Amount_after_TDS_Deduction), 0) AS paid
                    FROM payment
                    GROUP BY Invoice_Id
                ) inv_pay ON inv_pay.Invoice_Id = i.Invoice_Id
                LEFT JOIN villages  v  ON i.Village_Id   = v.Village_Id
                LEFT JOIN blocks    b  ON v.Block_Id     = b.Block_Id
                LEFT JOIN districts d  ON b.District_id  = d.District_id
                LEFT JOIN states    st ON d.State_Id     = st.State_Id
                {where}
                GROUP BY s.Contractor_Id, s.Contractor_Name
                ORDER BY s.Contractor_Name
            """, params)
            contractors = cursor.fetchall()

            if not contractors:
                return [], []

            contractor_ids = [c['Contractor_Id'] for c in contractors]
            fmt = ','.join(['%s'] * len(contractor_ids))

            # ── GST releases per contractor ────────────────────────────────
            cursor.execute(f"""
                SELECT Contractor_ID AS Contractor_Id,
                       COALESCE(SUM(Final_Amount),  0) AS gst_final,
                       COALESCE(SUM(Total_Amount),  0) AS gst_paid
                FROM gst_releases
                WHERE Contractor_ID IN ({fmt})
                GROUP BY Contractor_ID
            """, contractor_ids)
            gst_map = {r['Contractor_Id']: r for r in cursor.fetchall()}

            # ── Debit note bills per contractor (credit_note with 'debit' in details) ──
            cursor.execute(f"""
                SELECT Contractor_Id,
                       COALESCE(SUM(
                         CASE WHEN LOWER(Invoice_Details) LIKE '%debit%'
                              THEN Final_Amount ELSE 0 END
                       ), 0) AS total_debit_notes
                FROM credit_note
                WHERE Contractor_Id IN ({fmt})
                GROUP BY Contractor_Id
            """, contractor_ids)
            credit_map = {r['Contractor_Id']: float(r['total_debit_notes'] or 0) for r in cursor.fetchall()}

            # ── Hold releases per contractor, split by hold column ─────────
            release = get_release_totals(contractor_ids)
            hold_release_map = {
                cid: round(sum(release['by_type'].get(cid, {}).values())
                           + sum(release['fixed'].get(cid, {}).values())
                           + release['unassigned'].get(cid, 0.0), 2)
                for cid in contractor_ids
            }

            # ── Custom holds (gross) per contractor per hold type ──────────
            cursor.execute(f"""
                SELECT ih.Contractor_Id,
                       ht.hold_type_id,
                       ht.hold_type,
                       ht.include_in_hold,
                       COALESCE(SUM(ih.hold_amount), 0) AS gross_hold
                FROM invoice_subcontractor_hold_join ih
                JOIN hold_types ht ON ht.hold_type_id = ih.hold_type_id
                WHERE ih.Contractor_Id IN ({fmt})
                GROUP BY ih.Contractor_Id, ht.hold_type_id, ht.hold_type, ht.include_in_hold
                ORDER BY ht.hold_type_id
            """, contractor_ids)
            custom_hold_rows = cursor.fetchall()

            # {hold_type_id: name/include}  and  {contractor_id: {hold_type_id: gross}}
            all_hold_types = {}
            hold_type_include = {}  # {hold_type_id: include_in_hold bool}
            custom_hold_gross_map = {}
            for h in custom_hold_rows:
                cid  = h['Contractor_Id']
                htid = h['hold_type_id']
                all_hold_types[htid] = h['hold_type']
                hold_type_include[htid] = bool(h.get('include_in_hold', 1))
                custom_hold_gross_map.setdefault(cid, {})[htid] = float(h['gross_hold'] or 0)

            sorted_hold_types = [
                {'hold_type_id': k, 'hold_type': v, 'include_in_hold': hold_type_include.get(k, True)}
                for k, v in sorted(all_hold_types.items())
            ]

            # ── Merge into result rows ─────────────────────────────────────
            result = []
            for c in contractors:
                cid = c['Contractor_Id']

                total_sd    = float(c.get('total_sd')    or 0)
                total_oc    = float(c.get('total_oc')    or 0)
                total_ht    = float(c.get('total_ht')    or 0)
                # Only include custom holds flagged include_in_hold=1 (excludes DPR-type holds)
                custom_hold_gross_total = sum(
                    amt for htid, amt in custom_hold_gross_map.get(cid, {}).items()
                    if hold_type_include.get(htid, True)
                )
                rel_t   = release['by_type'].get(cid, {})
                rel_f   = release['fixed'].get(cid, {})
                rel_u   = release['unassigned'].get(cid, 0.0)
                # custom holds that count toward Hold, net of their own releases
                custom_hold_net_total = sum(
                    amt - rel_t.get(htid, 0.0)
                    for htid, amt in custom_hold_gross_map.get(cid, {}).items()
                    if hold_type_include.get(htid, True)
                )
                # Hold = remaining (gross - released) of every column
                hold_amt = round(
                    (total_sd - rel_f.get('SD_Amount', 0.0))
                    + (total_ht - rel_f.get('Hydro_Testing', 0.0))
                    + custom_hold_net_total - rel_u, 2)

                total_final = float(c.get('total_final') or 0)
                total_paid  = float(c.get('total_paid')  or 0)

                gst         = gst_map.get(cid, {})
                gst_final   = float(gst.get('gst_final', 0) or 0)
                gst_paid    = float(gst.get('gst_paid',  0) or 0)
                total_gst_amt = float(c.get('total_gst') or 0)
                gst_remaining = round(total_gst_amt - gst_final, 2)

                debit_notes = credit_map.get(cid, 0.0)
                hold_released = hold_release_map.get(cid, 0.0)

                # Surplus = (Invoice Final + GST Final) - (Invoice Paid + GST Paid)
                surplus = round((total_final + gst_final) - (total_paid + gst_paid), 2)

                # Custom holds shown as REMAINING (gross - released)
                contractor_gross = custom_hold_gross_map.get(cid, {})
                custom_holds_gross = {
                    ht['hold_type_id']: round(contractor_gross.get(ht['hold_type_id'], 0.0)
                                              - rel_t.get(ht['hold_type_id'], 0.0), 2)
                    for ht in sorted_hold_types
                }
                custom_holds_released = {
                    ht['hold_type_id']: round(rel_t.get(ht['hold_type_id'], 0.0), 2)
                    for ht in sorted_hold_types
                }

                result.append({
                    'Contractor_Id':   cid,
                    'Contractor_Name': c['Contractor_Name'],
                    'states':          c.get('states')    or '',
                    'districts':       c.get('districts') or '',
                    'total_basic':     round(float(c.get('total_basic')    or 0), 2),
                    'total_debit_col': round(float(c.get('total_debit_col')or 0), 2),
                    'total_gst':       round(float(c.get('total_gst')      or 0), 2),
                    'total_tds':       round(float(c.get('total_tds')      or 0), 2),
                    'total_sd':        round(total_sd,  2),
                    'total_oc':        round(total_oc,  2),
                    'total_ht':        round(total_ht,  2),
                    'hold':            hold_amt,
                    'total_debit_notes': round(debit_notes, 2),
                    'surplus':         surplus,
                    'gst_remaining':   gst_remaining,
                    'total_final':     round(total_final, 2),
                    'gst_final':       round(gst_final,   2),
                    'total_paid':      round(total_paid,  2),
                    'gst_paid':        round(gst_paid,    2),
                    'custom_holds':    custom_holds_gross,          # remaining = gross - released
                    'custom_holds_released': custom_holds_released,
                    'hold_released':   round(hold_released, 2),
                })

            return result, sorted_hold_types

        finally:
            cursor.close()
            connection.close()