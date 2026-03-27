from model.Utilities import ItemCRUDType
from model.ItemCRUD import ItemCRUD


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
            "Address": request.form.get('Address', '').strip(),
            "Mobile_No": request.form.get('Mobile_No', '').strip(),
            "PAN_No": request.form.get('PAN_No', '').strip(),
            "Email": request.form.get('Email', '').strip(),
            "Gender": request.form.get('Gender', '').strip(),
            "GST_Registration_Type": request.form.get('GST_Registration_Type', '').strip(),
            "GST_No": request.form.get('GST_No', '').strip(),
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
        return

    # ----------------------------------------------------------
    # GET ALL
    # ----------------------------------------------------------
    def GetAllSubcontractors(self, request):

        subcontractor = ItemCRUD(itemType=ItemCRUDType.Subcontractor)

        data = subcontractor.GetAllData(
            request=request,
            storedproc="GetAllSubcontractors"
        )

        self.isSuccess = subcontractor.isSuccess
        self.resultMessage = subcontractor.resultMessage
        return data

    # ----------------------------------------------------------
    # GET BY ID
    # ----------------------------------------------------------
    def GetSubcontractorByID(self, id):

        subcontractor = ItemCRUD(itemType=ItemCRUDType.Subcontractor)

        data = subcontractor.GetDataByID(
            id=id,
            storedproc="GetSubcontractorById"
        )

        if data:
            self.isSuccess = True
        else:
            self.isSuccess = False
            self.resultMessage = "Subcontractor not found"

        return data

    # ----------------------------------------------------------
    # CHECK (Duplicate)
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
    # EDIT
    # ----------------------------------------------------------
    def EditSubcontractor(self, request, subcontractor_id):

        subcontractor = ItemCRUD(itemType=ItemCRUDType.Subcontractor)

        data = {
            "Contractor_Name": request.form.get('Contractor_Name', '').strip(),
            "Address": request.form.get('Address', '').strip(),
            "Mobile_No": request.form.get('Mobile_No', '').strip(),
            "PAN_No": request.form.get('PAN_No', '').strip(),
            "Email": request.form.get('Email', '').strip(),
            "Gender": request.form.get('Gender', '').strip(),
            "GST_Registration_Type": request.form.get('GST_Registration_Type', '').strip(),
            "GST_No": request.form.get('GST_No', '').strip(),
            "Contractor_password": request.form.get('Contractor_password', '').strip()
        }

        subcontractor.EditItem(
            request=request,
            childid=subcontractor_id,
            data=data,
            storedprocupdate="UpdateSubcontractor"
        )

        self.isSuccess = subcontractor.isSuccess
        self.resultMessage = subcontractor.resultMessage
        return

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
        return