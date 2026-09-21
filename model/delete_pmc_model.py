# -------------------- model/delete_pmc_model.py --------------------

import config
import mysql.connector


class DeletePMCModel:

    # ---------------- DB CONNECTION ----------------
    @staticmethod
    def get_connection():

        connection = config.get_db_connection()

        if not connection:
            return None

        return connection

    # ---------------- DELETE MULTIPLE PMC ----------------
    @staticmethod
    def delete_multiple_pmc_records(pmc_numbers):

        connection = DeletePMCModel.get_connection()

        if not connection:

            print("DB CONNECTION FAILED")

            return False

        cursor = None

        try:

            cursor = connection.cursor()

            for pmc in pmc_numbers:

                pmc = int(pmc)

                print("Deleting PMC:", pmc)

                # CALL PROCEDURE
                cursor.callproc(
                    'DeletePMCRecords',
                    [pmc]
                )

                # IMPORTANT
                for result in cursor.stored_results():
                    result.fetchall()

            # COMMIT
            connection.commit()

            print("PMC RECORDS DELETED SUCCESSFULLY")

            return True

        except mysql.connector.Error as e:

            print("DELETE PMC ERROR:", e)

            if connection:
                connection.rollback()

            return False

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()
