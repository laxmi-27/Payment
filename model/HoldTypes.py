from flask import request
from model.ItemCRUD import ItemCRUD
from model.Utilities import ItemCRUDType

class HoldTypes:
    """CRUD operations for Hold Types using ItemCRUD"""

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""

    # ------------------- Add Hold Type -------------------
    def AddHoldType(self, request):
        hold = ItemCRUD(itemType=ItemCRUDType.HoldType)
        hold_name = request.form.get('hold_type', '').strip()

        hold.AddItem(
            request=request,
            parentid=None,
            childname=hold_name,
            storedprocfetch="CheckHoldTypeExists",
            storedprocadd="SaveHoldType"
        )

        self.isSuccess = hold.isSuccess
        self.resultMessage = hold.resultMessage

    # ------------------- Get All Hold Types -------------------
    def GetAllHoldTypes(self, request=None):
        hold = ItemCRUD(itemType=ItemCRUDType.HoldType)
        rows = hold.GetAllData(request=request, storedproc="GetAllHoldTypes")

        self.isSuccess = hold.isSuccess
        self.resultMessage = hold.resultMessage

        # ✅ Convert tuple → dictionary
        data = []
        for row in rows:
            data.append({
                "hold_type_id": row[0],
                "hold_type": row[1]
            })

        return data

    # ------------------- Get Hold Type By ID -------------------
    def GetHoldTypeByID(self, hold_type_id):
        hold = ItemCRUD(itemType=ItemCRUDType.HoldType)
        row = hold.GetDataByID(hold_type_id, storedproc="GetHoldTypesById")

        self.isSuccess = hold.isSuccess
        self.resultMessage = hold.resultMessage

        # ✅ Convert tuple → dictionary
        if row:
            return {
                "hold_type_id": row[0],
                "hold_type": row[1]
            }

        return None

    # ------------------- Update Hold Type -------------------
    def EditHoldType(self, request, hold_type_id):
        hold = ItemCRUD(itemType=ItemCRUDType.HoldType)
        hold_name = request.form.get('hold_type', '').strip()

        hold.EditItem(
            request=request,
            childid=hold_type_id,
            parentid=None,
            childname=hold_name,
            storedprocupdate="UpdateHoldTypeById"
        )

        self.isSuccess = hold.isSuccess
        self.resultMessage = hold.resultMessage

    # ------------------- Delete Hold Type -------------------
    def DeleteHoldType(self, request, hold_type_id):
        hold = ItemCRUD(itemType=ItemCRUDType.HoldType)

        hold.DeleteItem(
            request=request,
            itemID=hold_type_id,
            storedprocDelete="DeleteHoldType"
        )

        self.isSuccess = hold.isSuccess
        self.resultMessage = hold.resultMessage