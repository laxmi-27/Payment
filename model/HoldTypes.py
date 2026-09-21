import config

HOLD_CATEGORIES = [
    'Quality Hold',
    'DPR Hold',
    'Security Deposit Hold',
    'Material Recovery',
    'Penalty Hold',
    'Tax Related Hold',
    'Miscellaneous',
]

class HoldTypes:

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""

    # ------------------- Add Hold Type -------------------
    def AddHoldType(self, request):
        conn = cursor = None
        try:
            hold_name   = request.form.get('hold_type', '').strip()
            category    = request.form.get('hold_category', 'Miscellaneous').strip()
            description = request.form.get('description', '').strip() or None
            raw_pct     = request.form.get('default_hold_percentage', '').strip()
            default_pct = float(raw_pct) if raw_pct else None
            status      = request.form.get('status', 'Active').strip()

            if not hold_name:
                self.isSuccess = False
                self.resultMessage = "Hold Type Name is required."
                return

            conn   = config.get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT hold_type_id FROM hold_types WHERE LOWER(hold_type) = LOWER(%s)",
                (hold_name,)
            )
            if cursor.fetchone():
                self.isSuccess = False
                self.resultMessage = "A Hold Type with this name already exists."
                return

            cursor.execute("""
                INSERT INTO hold_types
                    (hold_type, hold_category, description, default_hold_percentage, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (hold_name, category, description, default_pct, status))
            conn.commit()

            self.isSuccess     = True
            self.resultMessage = "Hold Type added successfully."

        except Exception as e:
            print("ERROR AddHoldType:", e)
            self.isSuccess     = False
            self.resultMessage = str(e)
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    # ------------------- Edit Hold Type -------------------
    def EditHoldType(self, request, hold_type_id):
        conn = cursor = None
        try:
            hold_name   = request.form.get('hold_type', '').strip()
            category    = request.form.get('hold_category', 'Miscellaneous').strip()
            description = request.form.get('description', '').strip() or None
            raw_pct     = request.form.get('default_hold_percentage', '').strip()
            default_pct = float(raw_pct) if raw_pct else None
            status      = request.form.get('status', 'Active').strip()

            if not hold_name:
                self.isSuccess = False
                self.resultMessage = "Hold Type Name is required."
                return

            conn   = config.get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT hold_type_id FROM hold_types WHERE LOWER(hold_type) = LOWER(%s) AND hold_type_id != %s",
                (hold_name, hold_type_id)
            )
            if cursor.fetchone():
                self.isSuccess = False
                self.resultMessage = "Another Hold Type with this name already exists."
                return

            cursor.execute("""
                UPDATE hold_types
                SET hold_type = %s, hold_category = %s, description = %s,
                    default_hold_percentage = %s, status = %s
                WHERE hold_type_id = %s
            """, (hold_name, category, description, default_pct, status, hold_type_id))
            conn.commit()

            self.isSuccess     = True
            self.resultMessage = "Hold Type updated successfully."

        except Exception as e:
            print("ERROR EditHoldType:", e)
            self.isSuccess     = False
            self.resultMessage = str(e)
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    # ------------------- Delete Hold Type -------------------
    def DeleteHoldType(self, hold_type_id):
        conn = cursor = None
        try:
            conn   = config.get_db_connection()
            cursor = conn.cursor()
            cursor.callproc("DeleteHoldType", (hold_type_id,))
            conn.commit()
            self.isSuccess     = True
            self.resultMessage = "Hold Type deleted successfully."
        except Exception as e:
            print("ERROR DeleteHoldType:", e)
            self.isSuccess     = False
            self.resultMessage = str(e)
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    # ------------------- Get All Hold Types -------------------
    def GetAllHoldTypes(self):
        conn = cursor = None
        try:
            conn   = config.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT hold_type_id, hold_type, hold_category, description,
                       default_hold_percentage, status, created_date, last_updated_date
                FROM hold_types
                ORDER BY hold_type_id DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print("ERROR GetAllHoldTypes:", e)
            return []
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    # ------------------- Get Hold Type By ID -------------------
    def GetHoldTypeByID(self, hold_type_id):
        conn = cursor = None
        try:
            conn   = config.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT hold_type_id, hold_type, hold_category, description,
                       default_hold_percentage, status, created_date, last_updated_date
                FROM hold_types
                WHERE hold_type_id = %s
            """, (hold_type_id,))
            return cursor.fetchone()
        except Exception as e:
            print("ERROR GetHoldTypeByID:", e)
            return None
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
