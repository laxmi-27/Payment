import config
import mysql.connector
from flask import jsonify
from model.Utilities import ItemCRUDType
from model.ItemCRUD import ItemCRUD


class Block:

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""

    def AddBlock(self, request):
        block_name = request.form.get('block_Name', '').strip()
        district_id = request.form.get('district_Id')
        status = request.form.get('block_Status', 'Active')

        if not block_name or not district_id:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': 'Block name and district are required.'}), 400
            return

        conn = config.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc('GetBlockByNameAndDistrict', (block_name, district_id))
            existing = None
            for rs in cursor.stored_results():
                existing = rs.fetchone()
            if existing:
                self.isSuccess = False
                self.resultMessage = jsonify({'status': 'exists', 'message': 'Block already exists!'}), 409
                return
            cursor.execute(
                "INSERT INTO blocks (Block_Name, District_id, status) VALUES (%s, %s, %s)",
                (block_name, district_id, status)
            )
            conn.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'Block added successfully!'}), 200
        except mysql.connector.Error as e:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    def GetAllBlocks(self, request=None):
        conn = config.get_db_connection()
        data = []
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT b.Block_Id, b.Block_Name, d.District_Name, s.State_Name, "
                "COALESCE(b.status,'Active'), "
                "COALESCE(b.updated_at, NOW()) "
                "FROM blocks b "
                "JOIN districts d ON b.District_id = d.District_id "
                "JOIN states s ON d.State_Id = s.State_Id "
                "ORDER BY b.Block_Name"
            )
            data = cursor.fetchall()
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error fetching blocks: {e}")
            self.isSuccess = False
        finally:
            cursor.close()
            conn.close()
        return data

    def CheckBlock(self, request):
        block = ItemCRUD(itemType=ItemCRUDType.Block)
        data = request.get_json(silent=True) or request.form
        block_name = (data.get('block_Name') or '').strip()
        district_id = data.get('district_Id')
        result = block.CheckItem(
            request=request, parentid=district_id, childname=block_name,
            storedprocfetch="GetBlockByNameAndDistrict"
        )
        self.isSuccess = block.isSuccess
        self.resultMessage = block.resultMessage
        return result

    def GetBlockByID(self, id):
        block = ItemCRUD(itemType=ItemCRUDType.Block)
        blockdata = block.GetDataByID(id=id, storedproc="GetBlockDataByID")
        self.isSuccess = block.isSuccess
        self.resultMessage = block.resultMessage
        return blockdata

    def EditBlock(self, request, block_id):
        block = ItemCRUD(itemType=ItemCRUDType.Block)
        district_id = request.form.get('district_Id')
        block_name = request.form.get('block_Name', '').strip()
        block.EditItem(
            request=request, childid=block_id, parentid=district_id,
            childname=block_name, storedprocupdate="UpdateBlockById"
        )
        self.isSuccess = block.isSuccess
        self.resultMessage = block.resultMessage

    def DeleteBlock(self, request, id):
        block = ItemCRUD(itemType=ItemCRUDType.Block)
        block.DeleteItem(request=request, itemID=id, storedprocDelete="DeleteBlock")
        self.isSuccess = block.isSuccess
        self.resultMessage = block.resultMessage

    def CheckBlockHasVillages(self, block_id):
        conn = config.get_db_connection()
        count = 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM villages WHERE Block_Id=%s", (block_id,))
            row = cursor.fetchone()
            count = row[0] if row else 0
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error checking villages for block: {e}")
            self.isSuccess = False
        finally:
            cursor.close()
            conn.close()
        return count

    def ActivateBlock(self, block_id):
        conn = config.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE blocks SET status='Active' WHERE Block_Id=%s", (block_id,))
            conn.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'Block activated successfully.'}), 200
        except mysql.connector.Error as e:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
        return self.resultMessage

    def DeactivateBlock(self, block_id):
        conn = config.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE blocks SET status='Inactive' WHERE Block_Id=%s", (block_id,))
            conn.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'Block deactivated successfully.'}), 200
        except mysql.connector.Error as e:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
        return self.resultMessage
