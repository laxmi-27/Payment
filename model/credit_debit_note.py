import config


class CreditDebitNote:

    def __init__(self):
        self.isSuccess = False
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
                INSERT INTO credit_notes
                    (Note_Type, PMC_No, Invoice_No,
                     Basic_Amount, Debit_Amount, After_Debit_Amount,
                     GST_Amount, Final_Amount, Payment_Amount,
                     Total_Amount, UTR, Contractor_Id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                data['Note_Type'],          data['PMC_No'],            data['Invoice_No'],
                data['Basic_Amount'],       data['Debit_Amount'],      data['After_Debit_Amount'],
                data['GST_Amount'],         data['Final_Amount'],      data['Payment_Amount'],
                data['Total_Amount'],       data['UTR'],               data['Contractor_Id'],
            ))
            conn.commit()
            self.isSuccess      = True
            self.resultMessage  = "Credit/Debit Note added successfully."
        except Exception as e:
            print("ERROR in CreditDebitNote.add:", e)
            self.isSuccess     = False
            self.resultMessage = str(e)
        finally:
            if conn:
                try:
                    cursor.close()
                    conn.close()
                except Exception:
                    pass

    # ── Get All ────────────────────────────────────────────────────────
    def get_all(self):
        conn = None
        try:
            conn   = self._conn()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT cn.Credit_Note_Id, cn.Note_Type,
                       cn.PMC_No, cn.Invoice_No,
                       cn.Basic_Amount, cn.Debit_Amount, cn.After_Debit_Amount,
                       cn.GST_Amount, cn.Final_Amount, cn.Payment_Amount,
                       cn.Total_Amount, cn.UTR, cn.Contractor_Id,
                       COALESCE(s.Contractor_Name, '') AS Contractor_Name
                FROM credit_notes cn
                LEFT JOIN subcontractors s ON cn.Contractor_Id = s.Contractor_Id
                ORDER BY cn.Credit_Note_Id DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print("ERROR in CreditDebitNote.get_all:", e)
            return []
        finally:
            if conn:
                try:
                    cursor.close()
                    conn.close()
                except Exception:
                    pass

    # ── Get By ID ──────────────────────────────────────────────────────
    def get_by_id(self, note_id):
        conn = None
        try:
            conn   = self._conn()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT cn.Credit_Note_Id, cn.Note_Type,
                       cn.PMC_No, cn.Invoice_No,
                       cn.Basic_Amount, cn.Debit_Amount, cn.After_Debit_Amount,
                       cn.GST_Amount, cn.Final_Amount, cn.Payment_Amount,
                       cn.Total_Amount, cn.UTR, cn.Contractor_Id,
                       COALESCE(s.Contractor_Name, '') AS Contractor_Name
                FROM credit_notes cn
                LEFT JOIN subcontractors s ON cn.Contractor_Id = s.Contractor_Id
                WHERE cn.Credit_Note_Id = %s
            """, (note_id,))
            return cursor.fetchone()
        except Exception as e:
            print("ERROR in CreditDebitNote.get_by_id:", e)
            return None
        finally:
            if conn:
                try:
                    cursor.close()
                    conn.close()
                except Exception:
                    pass

    # ── Update ─────────────────────────────────────────────────────────
    def update(self, note_id, data):
        conn = None
        try:
            conn   = self._conn()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE credit_notes SET
                    Note_Type=%s, PMC_No=%s, Invoice_No=%s,
                    Basic_Amount=%s, Debit_Amount=%s, After_Debit_Amount=%s,
                    GST_Amount=%s, Final_Amount=%s, Payment_Amount=%s,
                    Total_Amount=%s, UTR=%s
                WHERE Credit_Note_Id=%s
            """, (
                data['Note_Type'],          data['PMC_No'],            data['Invoice_No'],
                data['Basic_Amount'],       data['Debit_Amount'],      data['After_Debit_Amount'],
                data['GST_Amount'],         data['Final_Amount'],      data['Payment_Amount'],
                data['Total_Amount'],       data['UTR'],               note_id,
            ))
            conn.commit()
            self.isSuccess     = True
            self.resultMessage = "Credit/Debit Note updated successfully."
        except Exception as e:
            print("ERROR in CreditDebitNote.update:", e)
            self.isSuccess     = False
            self.resultMessage = str(e)
        finally:
            if conn:
                try:
                    cursor.close()
                    conn.close()
                except Exception:
                    pass

    # ── Delete ─────────────────────────────────────────────────────────
    def delete(self, note_id):
        conn = None
        try:
            conn   = self._conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM credit_notes WHERE Credit_Note_Id = %s", (note_id,))
            conn.commit()
            self.isSuccess     = True
            self.resultMessage = "Deleted successfully."
        except Exception as e:
            print("ERROR in CreditDebitNote.delete:", e)
            self.isSuccess     = False
            self.resultMessage = str(e)
        finally:
            if conn:
                try:
                    cursor.close()
                    conn.close()
                except Exception:
                    pass
