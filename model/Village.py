

from model.Utilities import ResponseHandler, HtmlHelper, ItemCRUDType
import config
import mysql.connector
from model.ItemCRUD import ItemCRUD

 
class Village:
    isSuccess = False
    resultMessage = ""

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""
        self.response = {}
        self.village = ItemCRUD(itemType=ItemCRUDType.Village)

    # 🔹 Helper: sync status
    def _set_status(self, village):
        self.isSuccess = village.isSuccess

        #  UPDATED (safe handling)
        if hasattr(village, "response"):
            self.response = village.response
            self.resultMessage = village.response.get("message", "")
        else:
            self.resultMessage = village.resultMessage

    # 🔹 Helper: get request data
    def _get_form_data(self, request):
        block_id = request.form.get('block_Id')
        village_name = request.form.get('Village_Name', '').strip()
        return block_id, village_name

    def AddVillage(self, request):
        block_id, village_name = self._get_form_data(request)

        if not village_name:
            self.response = ResponseHandler.invalid_name("village")  # ✅ UPDATED
            self.resultMessage = self.response["message"]
            self.isSuccess = False
            return

        try:
            self.village.AddItem(
                request=request,
                parentid=block_id,
                childname=village_name,
                storedprocfetch="GetVillageByNameAndBlock",
                storedprocadd="SaveVillage"
            )
            self._set_status(self.village)

        except Exception as e:
            self.isSuccess = False
            self.resultMessage = str(e)

    def GetAllVillages(self, request):

        try:
            villagesdata = self.village.GetAllData(
                request=request,
                storedproc="GetAllVillages"
            )
            self._set_status(self.village)
            return villagesdata

        except Exception as e:
            self.isSuccess = False
            self.resultMessage = str(e)
            return []

    def CheckVillage(self, request):
        block_id, village_name = self._get_form_data(request)

        if not village_name:
            self.response = ResponseHandler.invalid_name("village")
            self.resultMessage = self.response["message"]
            self.isSuccess = False
            return None

        try:
            result = self.village.CheckItem(
                request=request,
                parentid=block_id,
                childname=village_name,
                storedprocfetch="GetVillageByNameAndBlock"
            )
            self._set_status(self.village)
            return result

        except Exception as e:
            self.isSuccess = False
            self.resultMessage = str(e)
            return None

    def DeleteVillage(self, request, village_id):

        try:
            self.village.DeleteItem(
                request=request,
                itemID=village_id,
                storedprocDelete="DeleteVillage"
            )
            self._set_status(self.village)

        except Exception as e:
            self.isSuccess = False
            self.resultMessage = str(e)

    def EditVillage(self, request, village_id):
        block_id, village_name = self._get_form_data(request)

        if not village_name:
            self.response = ResponseHandler.invalid_name("village") 
            self.resultMessage = self.response["message"]
            self.isSuccess = False
            return

        try:
            self.village.EditItem(
                request=request,
                childid=village_id,
                parentid=block_id,
                childname=village_name,
                storedprocupdate="UpdateVillage"
            )
            self._set_status(self.village)

        except Exception as e:
            self.isSuccess = False
            self.resultMessage = str(e)

    def GetVillageByID(self, id):

        try:
            villagedetailsdata = self.village.GetDataByID(
                id=id,
                storedproc="GetVillageDetailsById"
            )

            if villagedetailsdata:
                self.isSuccess = True
            else:
                self.isSuccess = False
                self.resultMessage = "Village not found"

            return villagedetailsdata

        except Exception as e:
            self.isSuccess = False
            self.resultMessage = str(e)
            return None

    def GetAllBlocks(self):
        blocks = []
        self.isSuccess = False
        self.resultMessage = ""

        connection = config.get_db_connection()
        if not connection:
            return []

        try:
            with connection.cursor() as cursor:
                cursor.callproc('GetAllBlock')

                for result in cursor.stored_results():
                    blocks.extend(result.fetchall())

            self.isSuccess = True
            return blocks

        except mysql.connector.Error as e:
            print(f"Error fetching blocks: {e}")
            self.isSuccess = False

            self.response = ResponseHandler.fetch_failure("block")
            self.resultMessage = self.response["message"]

            return []

        finally:
            connection.close()