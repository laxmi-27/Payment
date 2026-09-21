import config
import mysql.connector
from flask import jsonify
from model.Utilities import ResponseHandler, ItemCRUDType
from model.ItemCRUD import ItemCRUD


class Village:

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""
        self.response = {}
        self.village = ItemCRUD(itemType=ItemCRUDType.Village)

    def _set_status(self, village):
        self.isSuccess = village.isSuccess
        if hasattr(village, "response"):
            self.response = village.response
            self.resultMessage = village.response.get("message", "")
        else:
            self.resultMessage = village.resultMessage

    def _get_form_data(self, request):
        block_id = request.form.get('block_Id')
        village_name = request.form.get('Village_Name', '').strip()
        return block_id, village_name

    def AddVillage(self, request):
        block_id = request.form.get('block_Id')
        village_name = request.form.get('Village_Name', '').strip()
        status = request.form.get('village_Status', 'Active')

        if not village_name or not block_id:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': 'Village name and block are required.'}), 400
            return

        conn = config.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc('GetVillageByNameAndBlock', (village_name, block_id))
            existing = None
            for rs in cursor.stored_results():
                existing = rs.fetchone()
            if existing:
                self.isSuccess = False
                self.resultMessage = jsonify({'status': 'exists', 'message': 'Village already exists!'}), 409
                return
            cursor.execute(
                "INSERT INTO villages (Village_Name, Block_Id, status) VALUES (%s, %s, %s)",
                (village_name, block_id, status)
            )
            conn.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'Village added successfully!'}), 200
        except mysql.connector.Error as e:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    def GetAllVillages(self, request=None):
        conn = config.get_db_connection()
        data = []
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT v.Village_Id, v.Village_Name, b.Block_Name, d.District_Name, s.State_Name, "
                "COALESCE(v.status,'Active'), "
                "COALESCE(v.updated_at, NOW()) "
                "FROM villages v "
                "JOIN blocks b ON v.Block_Id = b.Block_Id "
                "JOIN districts d ON b.District_id = d.District_id "
                "JOIN states s ON d.State_Id = s.State_Id "
                "ORDER BY v.Village_Name"
            )
            data = cursor.fetchall()
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error fetching villages: {e}")
            self.isSuccess = False
        finally:
            cursor.close()
            conn.close()
        return data

    def CheckVillage(self, request):
        block_id, village_name = self._get_form_data(request)
        if not village_name:
            self.response = ResponseHandler.invalid_name("village")
            self.resultMessage = self.response["message"]
            self.isSuccess = False
            return None
        try:
            result = self.village.CheckItem(
                request=request, parentid=block_id, childname=village_name,
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
                request=request, itemID=village_id, storedprocDelete="DeleteVillage"
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
                request=request, childid=village_id, parentid=block_id,
                childname=village_name, storedprocupdate="UpdateVillage"
            )
            self._set_status(self.village)
        except Exception as e:
            self.isSuccess = False
            self.resultMessage = str(e)

    def GetVillageByID(self, id):
        try:
            villagedetailsdata = self.village.GetDataByID(
                id=id, storedproc="GetVillageDetailsById"
            )
            self.isSuccess = villagedetailsdata is not None
            if not self.isSuccess:
                self.resultMessage = "Village not found"
            return villagedetailsdata
        except Exception as e:
            self.isSuccess = False
            self.resultMessage = str(e)
            return None

    def GetAllBlocks(self):
        conn = config.get_db_connection()
        blocks = []
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.callproc('GetAllBlock')
            for rs in cursor.stored_results():
                blocks.extend(rs.fetchall())
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error fetching blocks: {e}")
            self.isSuccess = False
        finally:
            conn.close()
        return blocks

    def ActivateVillage(self, village_id):
        conn = config.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE villages SET status='Active' WHERE Village_Id=%s", (village_id,))
            conn.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'Village activated successfully.'}), 200
        except mysql.connector.Error as e:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
        return self.resultMessage

    def DeactivateVillage(self, village_id):
        conn = config.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE villages SET status='Inactive' WHERE Village_Id=%s", (village_id,))
            conn.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'Village deactivated successfully.'}), 200
        except mysql.connector.Error as e:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
        return self.resultMessage
