# model/gst_release.py
from flask import request, jsonify
from model.ItemCRUD import ItemCRUD
from model.Utilities import ItemCRUDType
import config

class GSTRelease:

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""
 
    # ------------------- Add GST Release -------------------
    def AddGSTRelease(self, request):
        try:
            gst = ItemCRUD(itemType=ItemCRUDType.GSTRelease)

            data = {
                "PMC_No": request.form.get("PMC_No", "").strip(),
                "Invoice_No": request.form.get("Invoice_No", "").strip(),
                "Invoice_Date": request.form.get("Invoice_Date", "") or None,
                "Basic_Amount": float(request.form.get("Basic_Amount", 0) or 0),
                "Final_Amount": float(request.form.get("Final_Amount", 0) or 0),
                "Total_Amount": float(request.form.get("Total_Amount", 0) or 0),
                "UTR": request.form.get("UTR", "").strip(),
                "Contractor_ID": int(request.form.get("Contractor_ID", 0) or 0)
            }

            # Add GST Release
            gst.AddItem(
                request=request,
                data=data,
                storedprocfetch="CheckGSTReleaseExists",
                storedprocadd="AddGSTReleaseFromExcel"
            )

            self.isSuccess = gst.isSuccess
            self.resultMessage = str(gst.resultMessage)

        except Exception as e:
            print("ERROR in AddGSTRelease:", e)
            self.isSuccess = False
            self.resultMessage = str(e)

        return jsonify({"success": self.isSuccess, "message": self.resultMessage})

    def EditGSTRelease(self, request, gst_release_id):
        try:
            gst = ItemCRUD(itemType=ItemCRUDType.GSTRelease)

            # Map form inputs to stored procedure parameters
            data = {
                "p_pmc_no": request.form.get("PMC_No", "").strip(),
                "p_invoice_no": request.form.get("invoice_no", "").strip(),
                "p_basic_amount": float(request.form.get("Basic_Amount", 0) or 0),
                "p_final_amount": float(request.form.get("Final_Amount", 0) or 0),
                "p_total_amount": float(request.form.get("Total_Amount", 0) or 0),
                "p_utr": request.form.get("UTR", "").strip(),
                "p_gst_release_id": gst_release_id,
                "p_invoice_date": request.form.get("Invoice_Date", "") or None
            }

            # Call your stored procedure
            gst.EditItem(
                request=request,
                childid=gst_release_id,
                data=data,
                storedprocupdate="UpdateGSTRelease"
            )

            self.isSuccess = gst.isSuccess
            self.resultMessage = str(gst.resultMessage)

        except Exception as e:
            print("ERROR in EditGSTRelease:", e)
            self.isSuccess = False
            self.resultMessage = str(e)

    # ------------------- Delete GST Release -------------------
    def DeleteGSTRelease(self, gst_release_id):
        try:
            gst = ItemCRUD(itemType=ItemCRUDType.GSTRelease)

            gst.DeleteItem(
                request=None,
                itemID=gst_release_id,
                storedprocDelete="DeleteGSTReleaseById"
            )

            self.isSuccess = gst.isSuccess
            self.resultMessage = str(gst.resultMessage)

        except Exception as e:
            print("ERROR in DeleteGSTRelease:", e)
            self.isSuccess = False
            self.resultMessage = str(e)

        return jsonify({"success": self.isSuccess, "message": self.resultMessage})

    # ------------------- Get All GST Releases -------------------
    def GetAllGSTReleases(self):
        try:
            gst = ItemCRUD(itemType=ItemCRUDType.GSTRelease)
            rows = gst.GetAllData(None, "GetAllGSTReleases")

            data = []
            for row in rows:
                data.append({
                    "gst_release_id": row[0],
                    "pmc_no": row[1],
                    "invoice_no": row[2],
                    "basic_amount": row[3],
                    "final_amount": row[4],
                    "total_amount": row[5],
                    "utr": row[6],
                    "contractor_id": row[7]
                })

            return data

        except Exception as e:
            print("ERROR in GetAllGSTReleases:", e)
            return []

    # ------------------- Get GST Release By ID -------------------
    def GetGSTReleaseByID(self, gst_release_id):
        try:
            gst = ItemCRUD(itemType=ItemCRUDType.GSTRelease)
            row = gst.GetDataByID(gst_release_id, "GetGSTReleaseById")

            if row:
                return {
                    "gst_release_id": row[0],
                    "pmc_no": row[1],
                    "invoice_no": row[2],
                    "basic_amount": row[3],
                    "final_amount": row[4],
                    "total_amount": row[5],
                    "utr": row[6],
                    "contractor_id": row[7],
                    "invoice_date": row[8]
                }

            return None

        except Exception as e:
            print("ERROR in GetGSTReleaseByID:", e)
            return None

    # ------------------- Get All GST Releases With Contractor Names -------------------
    def GetAllGSTReleasesWithNames(self):
        try:
            connection = config.get_db_connection()
            if not connection:
                return []
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT g.GST_Release_Id, g.PMC_No, g.Invoice_No,
                       g.Basic_Amount, g.Final_Amount, g.Total_Amount,
                       g.UTR, g.Contractor_ID, g.Invoice_Date,
                       COALESCE(s.Contractor_Name, '') AS Contractor_Name
                FROM gst_releases g
                LEFT JOIN subcontractors s ON g.Contractor_ID = s.Contractor_Id
                WHERE g.UTR IS NOT NULL AND g.UTR != ''
                ORDER BY g.GST_Release_Id DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print("ERROR in GetAllGSTReleasesWithNames:", e)
            return []
        finally:
            cursor.close()
            connection.close()

    # ------------------- Get GST Release By ID With Contractor Name -------------------
    def GetGSTReleaseByIDWithName(self, gst_release_id):
        try:
            connection = config.get_db_connection()
            if not connection:
                return None
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT g.GST_Release_Id, g.PMC_No, g.Invoice_No,
                       g.Basic_Amount, g.Final_Amount, g.Total_Amount,
                       g.UTR, g.Contractor_ID, g.Invoice_Date,
                       COALESCE(s.Contractor_Name, '') AS Contractor_Name
                FROM gst_releases g
                LEFT JOIN subcontractors s ON g.Contractor_ID = s.Contractor_Id
                WHERE g.GST_Release_Id = %s
            """, (gst_release_id,))
            return cursor.fetchone()
        except Exception as e:
            print("ERROR in GetGSTReleaseByIDWithName:", e)
            return None
        finally:
            cursor.close()
            connection.close()