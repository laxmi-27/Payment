from model.Utilities import ItemCRUDType
from model.ItemCRUD import ItemCRUD
import config
import mysql.connector


class Subcontractor:
    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""

    # ----------------------------------------------------------
    # ADD
    # ----------------------------------------------------------
    def AddSubcontractor(self, request):
        subcontractor = ItemCRUD(itemType=ItemCRUDType.Subcontractor)
        data = {
            "Contractor_Name": request.form.get('Contractor_Name', '').strip(),
            "Address":         request.form.get('Address', '').strip(),
            "Mobile_No":       request.form.get('Mobile_No', '').strip(),
            "PAN_No":          request.form.get('PAN_No', '').strip().upper(),
            "Email":           request.form.get('Email', '').strip(),
            "Gender":          request.form.get('Gender', '').strip(),
            "GST_Registration_Type": request.form.get('GST_Registration_Type', '').strip(),
            "GST_No":          request.form.get('GST_No', '').strip().upper(),
            "Contractor_password": request.form.get('Contractor_password', '').strip()
        }
        subcontractor.AddItem(
            request=request,
            data=data,
            storedprocfetch="GetSubcontractorByName",
            storedprocadd="SaveContractor"
        )
        self.isSuccess = subcontractor.isSuccess
        self.resultMessage = subcontractor.resultMessage

    # ----------------------------------------------------------
    # GET ALL
    # ----------------------------------------------------------
    def GetAllSubcontractors(self, request):
        subcontractor = ItemCRUD(itemType=ItemCRUDType.Subcontractor)
        data = subcontractor.GetAllData(request=request, storedproc="GetAllSubcontractors")
        self.isSuccess = subcontractor.isSuccess
        self.resultMessage = subcontractor.resultMessage
        return data

    # ----------------------------------------------------------
    # GET BY ID
    # ----------------------------------------------------------
    def GetSubcontractorByID(self, id):
        subcontractor = ItemCRUD(itemType=ItemCRUDType.Subcontractor)
        data = subcontractor.GetDataByID(id=id, storedproc="GetSubcontractorById")
        if data:
            self.isSuccess = True
        else:
            self.isSuccess = False
            self.resultMessage = "Subcontractor not found"
        return data

    # ----------------------------------------------------------
    # CHECK (Duplicate by name — kept for ItemCRUD compatibility)
    # ----------------------------------------------------------
    def CheckSubcontractor(self, request):
        subcontractor = ItemCRUD(itemType=ItemCRUDType.Subcontractor)
        name = request.form.get('Contractor_Name', '').strip()
        result = subcontractor.CheckItem(
            request=request,
            childname=name,
            storedprocfetch="GetSubcontractorByName"
        )
        self.isSuccess = subcontractor.isSuccess
        self.resultMessage = subcontractor.resultMessage
        return result

    # ----------------------------------------------------------
    # CHECK DUPLICATES (Mobile, PAN, Email, GST No)
    # Returns an error message string if duplicate found, else None.
    # ----------------------------------------------------------
    def CheckDuplicates(self, request, exclude_id=None):
        mobile  = request.form.get('Mobile_No', '').strip()
        pan     = request.form.get('PAN_No', '').strip().upper()
        email   = request.form.get('Email', '').strip()
        gst_no  = request.form.get('GST_No', '').strip().upper()

        checks = []
        if mobile:
            checks.append(('Mobile_No', mobile, f"Mobile number {mobile}"))
        if pan:
            checks.append(('PAN_No', pan, f"PAN number {pan}"))
        if email:
            checks.append(('Email', email, f"Email {email}"))
        if gst_no:
            checks.append(('GST_No', gst_no, f"GST number {gst_no}"))

        connection = config.get_db_connection()
        if not connection:
            return None
        cursor = connection.cursor()
        try:
            for field, value, label in checks:
                if exclude_id:
                    cursor.execute(
                        f"SELECT Contractor_Name FROM subcontractors WHERE `{field}` = %s AND Contractor_Id != %s",
                        (value, exclude_id)
                    )
                else:
                    cursor.execute(
                        f"SELECT Contractor_Name FROM subcontractors WHERE `{field}` = %s",
                        (value,)
                    )
                row = cursor.fetchone()
                if row:
                    return f"{label} is already registered under '{row[0]}'."
            return None
        except mysql.connector.Error as e:
            print(f"Duplicate check error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # EDIT
    # ----------------------------------------------------------
    def EditSubcontractor(self, request, subcontractor_id):
        subcontractor = ItemCRUD(itemType=ItemCRUDType.Subcontractor)
        new_password = request.form.get('Contractor_password', '').strip()
        if not new_password:
            existing = self.GetSubcontractorByID(subcontractor_id)
            new_password = existing[9] if existing and existing[9] else ''
        data = {
            "Contractor_Name": request.form.get('Contractor_Name', '').strip(),
            "Address":         request.form.get('Address', '').strip(),
            "Mobile_No":       request.form.get('Mobile_No', '').strip(),
            "PAN_No":          request.form.get('PAN_No', '').strip().upper(),
            "Email":           request.form.get('Email', '').strip(),
            "Gender":          request.form.get('Gender', '').strip(),
            "GST_Registration_Type": request.form.get('GST_Registration_Type', '').strip(),
            "GST_No":          request.form.get('GST_No', '').strip().upper(),
            "Contractor_password": new_password
        }
        subcontractor.EditItem(
            request=request,
            childid=subcontractor_id,
            data=data,
            storedprocupdate="UpdateSubcontractor"
        )
        self.isSuccess = subcontractor.isSuccess
        self.resultMessage = subcontractor.resultMessage

    # ----------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------
    def DeleteSubcontractor(self, request, subcontractor_id):
        subcontractor = ItemCRUD(itemType=ItemCRUDType.Subcontractor)
        subcontractor.DeleteItem(
            request=request,
            itemID=subcontractor_id,
            storedprocDelete="DeleteSubcontractor"
        )
        self.isSuccess = subcontractor.isSuccess
        self.resultMessage = subcontractor.resultMessage

    # ----------------------------------------------------------
    # SET STATUS  (Active / Inactive)
    # ----------------------------------------------------------
    def SetContractorStatus(self, contractor_id, new_status):
        connection = config.get_db_connection()
        if not connection:
            self.isSuccess = False
            return
        cursor = connection.cursor()
        try:
            cursor.callproc('SetContractorStatus', (contractor_id, new_status))
            connection.commit()
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error setting contractor status: {e}")
            self.isSuccess = False
        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # CHECK LINKED  (has assignments → block delete)
    # ----------------------------------------------------------
    def CheckContractorLinked(self, contractor_id):
        """Returns True if contractor has any work assignments."""
        connection = config.get_db_connection()
        if not connection:
            return False
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM assign_subcontractors WHERE Contractor_Id = %s",
                (contractor_id,)
            )
            row = cursor.fetchone()
            return bool(row and row[0] > 0)
        except mysql.connector.Error as e:
            print(f"Error checking contractor links: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
