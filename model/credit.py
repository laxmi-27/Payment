import config
import mysql.connector


class creditmodel:

    # ---------------- DB ----------------
    @staticmethod
    def get_connection():
        return config.get_db_connection()

    # ---------------- FETCH ALL ----------------
    @staticmethod
    def fetch_all_credit_notes():
        connection = creditmodel.get_connection()
        data = []

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT cn.*, s.Contractor_Name
                FROM credit_note cn
                LEFT JOIN subcontractors s ON cn.Contractor_Id = s.Contractor_Id
                ORDER BY cn.Credit_Note_Id DESC
            """)
            data = cursor.fetchall()

        except Exception as e:
            print("Fetch Error:", e)

        finally:
            cursor.close()
            connection.close()

        return data

    # ---------------- FETCH BY ID ----------------

    @staticmethod
    def fetch_credit_by_id(cid):
        connection = creditmodel.get_connection()
        data = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('GetCreditNoteById', [cid])

            for result in cursor.stored_results():
                data = result.fetchone()

        except Exception as e:
            print("Fetch By ID Error:", e)

        finally:
            cursor.close()
            connection.close()

        return data

    # ---------------- INSERT ----------------

    @staticmethod
    def insert_credit_note(
        subcontractor_id,
        pmc_no,
        note_type,
        invoice_no,
        basic,
        debit,
        after_debit,
        gst,
        final,
        payment,
        total,
        utr
    ):
        connection = creditmodel.get_connection()

        try:
            cursor = connection.cursor()

            subcontractor_id = int(subcontractor_id) if subcontractor_id else None
            pmc_no = int(pmc_no) if pmc_no else None

            basic = float(basic) if basic else 0
            debit = float(debit) if debit else 0
            after_debit = float(after_debit) if after_debit else 0
            gst = float(gst) if gst else 0
            final = float(final) if final else 0
            payment = float(payment) if payment else 0
            total = float(total) if total else 0

            cursor.callproc(
                'InsertCreditNote',
                [
                    subcontractor_id,
                    pmc_no,
                    note_type,
                    invoice_no,
                    basic,
                    debit,
                    after_debit,
                    gst,
                    final,
                    payment,
                    total,
                    utr
                ]
            )

            connection.commit()
            return True

        except Exception as e:
            print("Insert Error:", e)
            return False

        finally:
            cursor.close()
            connection.close()

    # ---------------- UPDATE ----------------
    @staticmethod
    def update_credit(
        cid,
        pmc_no,
        note_type,
        invoice_no,
        basic,
        debit,
        after_debit,
        gst,
        final,
        payment,
        total,
        utr
    ):
        connection = creditmodel.get_connection()

        try:
            cursor = connection.cursor()

            cid = int(cid)
            pmc_no = int(pmc_no) if pmc_no else None

            basic = float(basic) if basic else 0
            debit = float(debit) if debit else 0
            after_debit = float(after_debit) if after_debit else 0
            gst = float(gst) if gst else 0
            final = float(final) if final else 0
            payment = float(payment) if payment else 0
            total = float(total) if total else 0

            invoice_no = invoice_no.strip() if invoice_no else None
            utr = utr.strip() if utr else None

            cursor.callproc(
                'UpdateCreditNote',
                [
                    cid,
                    pmc_no,
                    note_type,
                    invoice_no,
                    basic,
                    debit,
                    after_debit,
                    gst,
                    final,
                    payment,
                    total,
                    utr
                ]
            )

            connection.commit()

            return True

        except Exception as e:
            print("Update Error:", e)
            return False

        finally:
            cursor.close()
            connection.close()

    # ---------------- DELETE ----------------
    @staticmethod
    def delete_credit(cid):
        connection = creditmodel.get_connection()

        try:
            cursor = connection.cursor()
            cursor.callproc('DeleteCreditNote', [cid])
            connection.commit()
            return True

        except Exception as e:
            print("Delete Error:", e)
            return False

        finally:
            cursor.close()
            connection.close()
