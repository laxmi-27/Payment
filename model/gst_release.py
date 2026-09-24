# model/gst_release.py

from flask import jsonify
from model.ItemCRUD import ItemCRUD
from model.Utilities import ItemCRUDType
import config


class GSTRelease:

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""


    # ============================================================
    # ADD GST RELEASE
    # ============================================================
    def AddGSTRelease(self, request):

        try:

            gst = ItemCRUD(
                itemType=ItemCRUDType.GSTRelease
            )

            data = {
                "PMC_No": request.form.get(
                    "PMC_No",
                    ""
                ).strip(),

                "Invoice_No": request.form.get(
                    "Invoice_No",
                    ""
                ).strip(),

                "Invoice_Date": (
                    request.form.get(
                        "Invoice_Date",
                        ""
                    ) or None
                ),

                "Basic_Amount": float(
                    request.form.get(
                        "Basic_Amount",
                        0
                    ) or 0
                ),

                "Final_Amount": float(
                    request.form.get(
                        "Final_Amount",
                        0
                    ) or 0
                ),

                "Total_Amount": float(
                    request.form.get(
                        "Total_Amount",
                        0
                    ) or 0
                ),

                # ------------------------------------------------
                # GST RELEASE DOES NOT USE UTR
                # Keep empty value only because the existing
                # database stored procedure still has a UTR
                # parameter.
                # ------------------------------------------------
                "UTR": "",

                "Contractor_ID": int(
                    request.form.get(
                        "Contractor_ID",
                        0
                    ) or 0
                )
            }

            gst.AddItem(
                request=request,
                data=data,
                storedprocfetch="CheckGSTReleaseExists",
                storedprocadd="AddGSTReleaseFromExcel"
            )

            self.isSuccess = gst.isSuccess
            self.resultMessage = str(
                gst.resultMessage
            )

        except Exception as e:

            print(
                "ERROR in AddGSTRelease:",
                e
            )

            self.isSuccess = False
            self.resultMessage = str(e)

        return jsonify({
            "success": self.isSuccess,
            "message": self.resultMessage
        })


    # ============================================================
    # EDIT GST RELEASE
    # ============================================================
    def EditGSTRelease(
        self,
        request,
        gst_release_id
    ):

        try:

            gst = ItemCRUD(
                itemType=ItemCRUDType.GSTRelease
            )

            data = {

                "p_pmc_no": request.form.get(
                    "PMC_No",
                    ""
                ).strip(),

                "p_invoice_no": request.form.get(
                    "invoice_no",
                    ""
                ).strip(),

                "p_basic_amount": float(
                    request.form.get(
                        "Basic_Amount",
                        0
                    ) or 0
                ),

                "p_final_amount": float(
                    request.form.get(
                        "Final_Amount",
                        0
                    ) or 0
                ),

                "p_total_amount": float(
                    request.form.get(
                        "Total_Amount",
                        0
                    ) or 0
                ),

                # ------------------------------------------------
                # GST RELEASE DOES NOT USE UTR.
                # Send empty value to the existing stored procedure
                # so old database procedure remains compatible.
                # ------------------------------------------------
                "p_utr": "",

                "p_gst_release_id": gst_release_id,

                "p_invoice_date": (
                    request.form.get(
                        "Invoice_Date",
                        ""
                    ) or None
                )
            }

            gst.EditItem(
                request=request,
                childid=gst_release_id,
                data=data,
                storedprocupdate="UpdateGSTRelease"
            )

            self.isSuccess = gst.isSuccess
            self.resultMessage = str(
                gst.resultMessage
            )

        except Exception as e:

            print(
                "ERROR in EditGSTRelease:",
                e
            )

            self.isSuccess = False
            self.resultMessage = str(e)


    # ============================================================
    # DELETE GST RELEASE
    # ============================================================
    def DeleteGSTRelease(
        self,
        gst_release_id
    ):

        try:

            gst = ItemCRUD(
                itemType=ItemCRUDType.GSTRelease
            )

            gst.DeleteItem(
                request=None,
                itemID=gst_release_id,
                storedprocDelete="DeleteGSTReleaseById"
            )

            self.isSuccess = gst.isSuccess
            self.resultMessage = str(
                gst.resultMessage
            )

        except Exception as e:

            print(
                "ERROR in DeleteGSTRelease:",
                e
            )

            self.isSuccess = False
            self.resultMessage = str(e)

        return jsonify({
            "success": self.isSuccess,
            "message": self.resultMessage
        })


    # ============================================================
    # GET ALL GST RELEASES
    # ============================================================
    def GetAllGSTReleases(self):

        try:

            gst = ItemCRUD(
                itemType=ItemCRUDType.GSTRelease
            )

            rows = gst.GetAllData(
                None,
                "GetAllGSTReleases"
            )

            data = []

            for row in rows:

                data.append({

                    "gst_release_id": row[0],

                    "pmc_no": row[1],

                    "invoice_no": row[2],

                    "basic_amount": row[3],

                    "final_amount": row[4],

                    "total_amount": row[5],

                    # Legacy database column.
                    # Not used by GST Release UI.
                    "utr": row[6],

                    "contractor_id": row[7]
                })

            return data

        except Exception as e:

            print(
                "ERROR in GetAllGSTReleases:",
                e
            )

            return []


    # ============================================================
    # GET GST RELEASE BY ID
    # ============================================================
    def GetGSTReleaseByID(
        self,
        gst_release_id
    ):

        try:

            gst = ItemCRUD(
                itemType=ItemCRUDType.GSTRelease
            )

            row = gst.GetDataByID(
                gst_release_id,
                "GetGSTReleaseById"
            )

            if row:

                return {

                    "gst_release_id": row[0],

                    "pmc_no": row[1],

                    "invoice_no": row[2],

                    "basic_amount": row[3],

                    "final_amount": row[4],

                    "total_amount": row[5],

                    # Legacy field.
                    # GST Release no longer displays/uses UTR.
                    "utr": row[6],

                    "contractor_id": row[7],

                    "invoice_date": row[8]
                }

            return None

        except Exception as e:

            print(
                "ERROR in GetGSTReleaseByID:",
                e
            )

            return None


    # ============================================================
    # GET ALL GST RELEASES WITH CONTRACTOR NAMES
    # ============================================================
    def GetAllGSTReleasesWithNames(self):

        connection = None
        cursor = None

        try:

            connection = config.get_db_connection()

            if not connection:
                return []

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute("""
                SELECT
                    g.GST_Release_Id,
                    g.PMC_No,
                    g.Invoice_No,
                    g.Basic_Amount,
                    g.Final_Amount,
                    g.Total_Amount,
                    g.Contractor_ID,
                    g.Invoice_Date,
                    COALESCE(
                        s.Contractor_Name,
                        ''
                    ) AS Contractor_Name

                FROM gst_releases g

                LEFT JOIN subcontractors s
                    ON g.Contractor_ID = s.Contractor_Id

                ORDER BY
                    g.GST_Release_Id DESC
            """)

            return cursor.fetchall()

        except Exception as e:

            print(
                "ERROR in GetAllGSTReleasesWithNames:",
                e
            )

            return []

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


    # ============================================================
    # GET GST RELEASE BY ID WITH CONTRACTOR NAME
    # ============================================================
    def GetGSTReleaseByIDWithName(
        self,
        gst_release_id
    ):

        connection = None
        cursor = None

        try:

            connection = config.get_db_connection()

            if not connection:
                return None

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute("""
                SELECT
                    g.GST_Release_Id,
                    g.PMC_No,
                    g.Invoice_No,
                    g.Basic_Amount,
                    g.Final_Amount,
                    g.Total_Amount,
                    g.Contractor_ID,
                    g.Invoice_Date,
                    COALESCE(
                        s.Contractor_Name,
                        ''
                    ) AS Contractor_Name

                FROM gst_releases g

                LEFT JOIN subcontractors s
                    ON g.Contractor_ID = s.Contractor_Id

                WHERE
                    g.GST_Release_Id = %s

            """, (gst_release_id,))

            return cursor.fetchone()

        except Exception as e:

            print(
                "ERROR in GetGSTReleaseByIDWithName:",
                e
            )

            return None

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()