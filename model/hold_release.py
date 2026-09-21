import config


class HoldRelease:

    def __init__(self):
        self.isSuccess     = False
        self.resultMessage = ""

    def _conn(self):
        return config.get_db_connection()

    # ── Add ────────────────────────────────────────────────────────────
    def add(self, data):
        conn = None
        try:
            conn   = self._conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO hold_release
                    (PMC_No, invoice_no, Invoice_Details,
                     Basic_Amount, Final_Amount, Total_Amount,
                     UTR, Contractor_Id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['PMC_No'],        data['invoice_no'],    data['Invoice_Details'],
                data['Basic_Amount'],  data['Final_Amount'],  data['Total_Amount'],
                data['UTR'],           data['Contractor_Id'],
            ))
            conn.commit()
            self.isSuccess     = True
            self.resultMessage = "Hold Release added successfully."
        except Exception as e:
            err = str(e)
            if "Duplicate entry" in err and "UTR" in err:
                self.resultMessage = "A Hold Release with this UTR already exists."
            else:
                self.resultMessage = err
            self.isSuccess = False
            print("ERROR in HoldRelease.add:", e)
        finally:
            if conn:
                try:
                    cursor.close(); conn.close()
                except Exception:
                    pass

    # ── Get All (with contractor name) ─────────────────────────────────
    def get_all(self):
        conn = None
        try:
            conn   = self._conn()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT hr.Hold_Release_Id,
                       hr.PMC_No, hr.invoice_no, hr.Invoice_Details,
                       hr.Basic_Amount, hr.Final_Amount, hr.Total_Amount,
                       hr.UTR, hr.Contractor_Id,
                       COALESCE(s.Contractor_Name, '') AS Contractor_Name
                FROM hold_release hr
                LEFT JOIN subcontractors s ON hr.Contractor_Id = s.Contractor_Id
                ORDER BY hr.Hold_Release_Id DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print("ERROR in HoldRelease.get_all:", e)
            return []
        finally:
            if conn:
                try:
                    cursor.close(); conn.close()
                except Exception:
                    pass

    # ── Get By ID ──────────────────────────────────────────────────────
    def get_by_id(self, hr_id):
        conn = None
        try:
            conn   = self._conn()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT hr.Hold_Release_Id,
                       hr.PMC_No, hr.invoice_no, hr.Invoice_Details,
                       hr.Basic_Amount, hr.Final_Amount, hr.Total_Amount,
                       hr.UTR, hr.Contractor_Id,
                       COALESCE(s.Contractor_Name, '') AS Contractor_Name
                FROM hold_release hr
                LEFT JOIN subcontractors s ON hr.Contractor_Id = s.Contractor_Id
                WHERE hr.Hold_Release_Id = %s
            """, (hr_id,))
            return cursor.fetchone()
        except Exception as e:
            print("ERROR in HoldRelease.get_by_id:", e)
            return None
        finally:
            if conn:
                try:
                    cursor.close(); conn.close()
                except Exception:
                    pass

    # ── Update ─────────────────────────────────────────────────────────
    def update(self, hr_id, data):
        conn = None
        try:
            conn   = self._conn()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE hold_release SET
                    PMC_No=%s, invoice_no=%s, Invoice_Details=%s,
                    Basic_Amount=%s, Final_Amount=%s, Total_Amount=%s,
                    UTR=%s
                WHERE Hold_Release_Id=%s
            """, (
                data['PMC_No'],       data['invoice_no'],   data['Invoice_Details'],
                data['Basic_Amount'], data['Final_Amount'], data['Total_Amount'],
                data['UTR'],          hr_id,
            ))
            conn.commit()
            self.isSuccess     = True
            self.resultMessage = "Hold Release updated successfully."
        except Exception as e:
            err = str(e)
            if "Duplicate entry" in err and "UTR" in err:
                self.resultMessage = "A Hold Release with this UTR already exists."
            else:
                self.resultMessage = err
            self.isSuccess = False
            print("ERROR in HoldRelease.update:", e)
        finally:
            if conn:
                try:
                    cursor.close(); conn.close()
                except Exception:
                    pass

    # ── Delete ─────────────────────────────────────────────────────────
    def delete(self, hr_id):
        conn = None
        try:
            conn   = self._conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM hold_release WHERE Hold_Release_Id = %s", (hr_id,))
            conn.commit()
            self.isSuccess     = True
            self.resultMessage = "Hold Release deleted successfully."
        except Exception as e:
            print("ERROR in HoldRelease.delete:", e)
            self.isSuccess     = False
            self.resultMessage = str(e)
        finally:
            if conn:
                try:
                    cursor.close(); conn.close()
                except Exception:
                    pass
