import config


class ReportHelper:
    isSuccess = False
    resultMessage = ""
    data = []

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
        """
        Returns one row per invoice with all financial columns.
        Replaces the search_contractor_info SP which only returned location data.
        """
        subcontractor_name = request.form.get("subcontractor_name") or None
        subcontractor_id   = request.form.get("subcontractor_id")   or None
        pmc_no             = request.form.get("pmc_no")             or None
        state              = request.form.get("state")              or None
        district           = request.form.get("district")           or None
        block              = request.form.get("block")              or None
        village            = request.form.get("village")            or None
        year_from          = request.form.get("year_from")          or None
        year_to            = request.form.get("year_to")            or None

        connection = config.get_db_connection()
        if not connection:
            return []

        cursor = connection.cursor(dictionary=True)

        conditions, params = [], []

        if subcontractor_id:
            # Exact match by ID takes priority over name search
            conditions.append("s.Contractor_Id = %s")
            params.append(int(subcontractor_id))
        elif subcontractor_name:
            conditions.append("LOWER(s.Contractor_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
            params.append(subcontractor_name)
        if pmc_no:
            conditions.append("i.PMC_No = %s")
            params.append(pmc_no)
        if state:
            conditions.append("LOWER(st.State_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
            params.append(state)
        if district:
            conditions.append("LOWER(d.District_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
            params.append(district)
        if block:
            conditions.append("LOWER(b.Block_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
            params.append(block)
        if village:
            conditions.append("LOWER(v.Village_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
            params.append(village)
        if year_from and year_to:
            conditions.append("i.Invoice_Date BETWEEN %s AND %s")
            params += [year_from, year_to]
        elif year_from:
            conditions.append("i.Invoice_Date >= %s")
            params.append(year_from)
        elif year_to:
            conditions.append("i.Invoice_Date <= %s")
            params.append(year_to)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        # Build GST-specific conditions (gst_releases has no location/date columns)
        gst_conditions = []
        gst_params_list = []
        if subcontractor_id:
            gst_conditions.append("s.Contractor_Id = %s")
            gst_params_list.append(int(subcontractor_id))
        elif subcontractor_name:
            gst_conditions.append("LOWER(s.Contractor_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
            gst_params_list.append(subcontractor_name)
        if pmc_no:
            gst_conditions.append("g.PMC_No = %s")
            gst_params_list.append(pmc_no)
        gst_where = ("WHERE " + " AND ".join(gst_conditions)) if gst_conditions else ""

        # Build credit/debit note conditions (credit_note has no location/date columns)
        cdn_conditions = []
        debit_params_list = []
        if subcontractor_id:
            cdn_conditions.append("s.Contractor_Id = %s")
            debit_params_list.append(int(subcontractor_id))
        elif subcontractor_name:
            cdn_conditions.append("LOWER(s.Contractor_Name) LIKE LOWER(CONCAT('%',%s,'%'))")
            debit_params_list.append(subcontractor_name)
        if pmc_no:
            cdn_conditions.append("cn.PMC_No = %s")
            debit_params_list.append(pmc_no)
        debit_where = ("WHERE " + " AND ".join(cdn_conditions)) if cdn_conditions else ""

        # UNION invoices + GST releases + credit/debit notes, ordered by sort_order
        # so source Excel row sequence is preserved across all three tables.
        sql = f"""
            SELECT
                s.Contractor_Id,
                MAX(s.Contractor_Name)                      AS Contractor_Name,
                i.PMC_No,
                MAX(st.State_Name)                          AS State_Name,
                MAX(d.District_Name)                        AS District_Name,
                MAX(b.Block_Name)                           AS Block_Name,
                MAX(v.Village_Name)                         AS Village_Name,
                i.Invoice_Id,
                MAX(i.Invoice_Date)                         AS Invoice_Date,
                MAX(i.Invoice_No)                           AS Invoice_No,
                MAX(i.Invoice_Details)                      AS Invoice_Details,
                COALESCE(MAX(i.Basic_Amount),     0)        AS Basic_Amount,
                COALESCE(MAX(i.Debit_Amount),    0)         AS Debit_Amount,
                COALESCE(MAX(i.After_Debit_Amount), 0)      AS After_Debit_Amount,
                COALESCE(MAX(i.Amount),          0)         AS Amount,
                COALESCE(MAX(i.GST_Amount),      0)         AS GST_Amount,
                COALESCE(MAX(i.TDS_Amount),      0)         AS TDS_Amount,
                COALESCE(MAX(i.SD_Amount),       0)         AS SD_Amount,
                COALESCE(MAX(i.On_Commission),   0)         AS On_Commission,
                COALESCE(MAX(i.Hydro_Testing),   0)         AS Hydro_Testing,
                COALESCE(MAX(i.GST_SD_Amount),   0)         AS GST_SD_Amount,
                COALESCE(MAX(i.Final_Amount),    0)         AS Final_Amount,
                COALESCE(SUM(p.Amount_with_TDS),             0) AS Payment_Amount,
                COALESCE(SUM(p.TDS_Payment_Amount),          0) AS TDS_Payment_Amount,
                COALESCE(SUM(p.Amount_after_TDS_Deduction),  0) AS Total_Amount,
                GROUP_CONCAT(DISTINCT p.UTR ORDER BY p.Payment_Id SEPARATOR ' | ') AS UTR,
                COALESCE(i.sort_order, i.Invoice_Id)        AS _sort_key
            FROM subcontractors s
            INNER JOIN invoices  i  ON i.Subcontractor_Id = s.Contractor_Id
            LEFT  JOIN villages  v  ON i.Village_Id       = v.Village_Id
            LEFT  JOIN blocks    b  ON v.Block_Id         = b.Block_Id
            LEFT  JOIN districts d  ON b.District_id      = d.District_id
            LEFT  JOIN states    st ON d.State_Id         = st.State_Id
            LEFT  JOIN payment   p  ON p.Invoice_Id       = i.Invoice_Id
            {where}
            GROUP BY i.Invoice_Id, s.Contractor_Id, i.PMC_No

            UNION ALL

            SELECT
                s.Contractor_Id,
                s.Contractor_Name                           AS Contractor_Name,
                g.PMC_No,
                NULL                                        AS State_Name,
                NULL                                        AS District_Name,
                NULL                                        AS Block_Name,
                NULL                                        AS Village_Name,
                NULL                                        AS Invoice_Id,
                g.Invoice_Date                              AS Invoice_Date,
                g.Invoice_No                                AS Invoice_No,
                'GST Release Note'                          AS Invoice_Details,
                COALESCE(g.Basic_Amount,  0)                AS Basic_Amount,
                0                                           AS Debit_Amount,
                0                                           AS After_Debit_Amount,
                0                                           AS Amount,
                0                                           AS GST_Amount,
                0                                           AS TDS_Amount,
                0                                           AS SD_Amount,
                0                                           AS On_Commission,
                0                                           AS Hydro_Testing,
                0                                           AS GST_SD_Amount,
                COALESCE(g.Final_Amount,  0)                AS Final_Amount,
                0                                           AS Payment_Amount,
                0                                           AS TDS_Payment_Amount,
                COALESCE(g.Total_Amount,  0)                AS Total_Amount,
                g.UTR                                       AS UTR,
                COALESCE(g.sort_order, g.GST_Release_Id)    AS _sort_key
            FROM gst_releases g
            INNER JOIN subcontractors s ON s.Contractor_Id = g.Contractor_ID
            {gst_where}

            UNION ALL

            SELECT
                s.Contractor_Id,
                s.Contractor_Name                           AS Contractor_Name,
                cn.PMC_No,
                NULL                                        AS State_Name,
                NULL                                        AS District_Name,
                NULL                                        AS Block_Name,
                NULL                                        AS Village_Name,
                NULL                                        AS Invoice_Id,
                NULL                                        AS Invoice_Date,
                cn.invoice_no                               AS Invoice_No,
                cn.Invoice_Details                          AS Invoice_Details,
                COALESCE(cn.Basic_Amount,       0)          AS Basic_Amount,
                COALESCE(cn.Debit_Amount,       0)          AS Debit_Amount,
                COALESCE(cn.After_Debit_Amount, 0)          AS After_Debit_Amount,
                COALESCE(cn.Amount,             0)          AS Amount,
                COALESCE(cn.GST_Amount,         0)          AS GST_Amount,
                0                                           AS TDS_Amount,
                0                                           AS SD_Amount,
                0                                           AS On_Commission,
                0                                           AS Hydro_Testing,
                0                                           AS GST_SD_Amount,
                COALESCE(cn.Final_Amount,       0)          AS Final_Amount,
                COALESCE(cn.Payment_Amount,     0)          AS Payment_Amount,
                0                                           AS TDS_Payment_Amount,
                COALESCE(cn.Total_Amount,       0)          AS Total_Amount,
                cn.UTR                                      AS UTR,
                cn.Credit_Note_Id                           AS _sort_key
            FROM credit_note cn
            INNER JOIN subcontractors s ON s.Contractor_Id = cn.Contractor_Id
            {debit_where}

            ORDER BY Contractor_Id ASC, _sort_key ASC
        """

        # Merge params: invoice conditions, then GST conditions, then debit conditions
        all_params = params + gst_params_list + debit_params_list

        try:
            cursor.execute(sql, all_params)
            data = cursor.fetchall()
            # Remove internal sort key from returned dicts
            for row in data:
                row.pop('_sort_key', None)
        except Exception as e:
            print(f"Error in search_contractor: {e}")
            data = []
        finally:
            cursor.close()
            connection.close()

        return data

    @staticmethod
    def get_payment_total(invoice_ids):
        """Return total paid (Payment_Amount + TDS_Payment_Amount) for invoice IDs."""
        if not invoice_ids:
            return 0.0
        connection = config.get_db_connection()
        if not connection:
            return 0.0
        cursor = connection.cursor(dictionary=True)
        try:
            placeholders = ','.join(['%s'] * len(invoice_ids))
            cursor.execute(
                f"SELECT COALESCE(SUM(Payment_Amount),0) + COALESCE(SUM(TDS_Payment_Amount),0) AS total_paid "
                f"FROM payment WHERE Invoice_Id IN ({placeholders})",
                invoice_ids
            )
            row = cursor.fetchone()
            return float(row['total_paid']) if row else 0.0
        except Exception as e:
            print(f"Error in get_payment_total: {e}")
            return 0.0
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_contractor_info(contractor_id):
        from model.ContractorInfo import ContractorInfo
        contractor = ContractorInfo(contractor_id)
        return contractor.contInfo if contractor.contInfo else None
