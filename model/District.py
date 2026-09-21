import config
import mysql.connector
from flask import jsonify
from model.Utilities import ItemCRUDType
from model.ItemCRUD import ItemCRUD


class District:

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""

    def AddDistrict(self, request):
        district_name = request.form.get('district_Name', '').strip()
        state_id = request.form.get('state_Id')
        status = request.form.get('district_Status', 'Active')

        if not district_name or not state_id:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': 'District name and state are required.'}), 400
            return

        conn = config.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc('GetDistrictByNameAndState', (district_name, state_id))
            existing = None
            for rs in cursor.stored_results():
                existing = rs.fetchone()
            if existing:
                self.isSuccess = False
                self.resultMessage = jsonify({'status': 'exists', 'message': 'District already exists!'}), 409
                return
            cursor.execute(
                "INSERT INTO districts (District_Name, State_Id, status) VALUES (%s, %s, %s)",
                (district_name, state_id, status)
            )
            conn.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'District added successfully!'}), 200
        except mysql.connector.Error as e:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    def EditDistrict(self, request, district_id):
        district = ItemCRUD(itemType=ItemCRUDType.District)
        district_name = request.form['district_Name'].strip()
        state_id = request.form['state_Id']
        district.EditItem(
            request=request, childid=district_id, parentid=state_id,
            childname=district_name, storedprocupdate="UpdateDistrict"
        )
        self.isSuccess = district.isSuccess
        self.resultMessage = district.resultMessage

    def GetAllDistricts(self, request=None):
        conn = config.get_db_connection()
        data = []
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT d.District_id, d.District_Name, s.State_Name, "
                "COALESCE(d.status,'Active'), "
                "COALESCE(d.updated_at, NOW()) "
                "FROM districts d "
                "JOIN states s ON d.State_Id = s.State_Id "
                "ORDER BY d.District_Name"
            )
            data = cursor.fetchall()
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error fetching districts: {e}")
            self.isSuccess = False
        finally:
            cursor.close()
            conn.close()
        return data

    def CheckDistrict(self, request):
        district = ItemCRUD(itemType=ItemCRUDType.District)
        district_name = request.json.get('district_Name', '').strip()
        state_id = request.json.get('state_Id', '')
        result = district.CheckItem(
            request=request, parentid=state_id, childname=district_name,
            storedprocfetch="GetDistrictByNameAndState"
        )
        self.isSuccess = district.isSuccess
        self.resultMessage = district.resultMessage
        return result

    def GetDistrictByID(self, request, district_id):
        district = ItemCRUD(itemType=ItemCRUDType.District)
        districtdata = district.GetDataByID(id=district_id, storedproc="GetDistrictDataByID")
        self.isSuccess = districtdata is not None
        self.resultMessage = "District not found" if not districtdata else "Success"
        return districtdata

    def DeleteDistrict(self, request, district_id):
        district = ItemCRUD(itemType=ItemCRUDType.District)
        district.DeleteItem(request=request, itemID=district_id, storedprocDelete="DeleteDistrict")
        self.isSuccess = district.isSuccess
        self.resultMessage = str(district.resultMessage)

    def CheckDistrictHasBlocks(self, district_id):
        conn = config.get_db_connection()
        count = 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM blocks WHERE District_id=%s", (district_id,))
            row = cursor.fetchone()
            count = row[0] if row else 0
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error checking blocks for district: {e}")
            self.isSuccess = False
        finally:
            cursor.close()
            conn.close()
        return count

    def ActivateDistrict(self, district_id):
        conn = config.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE districts SET status='Active' WHERE District_id=%s", (district_id,))
            conn.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'District activated successfully.'}), 200
        except mysql.connector.Error as e:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
        return self.resultMessage

    def DeactivateDistrict(self, district_id):
        conn = config.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE districts SET status='Inactive' WHERE District_id=%s", (district_id,))
            conn.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'District deactivated successfully.'}), 200
        except mysql.connector.Error as e:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
        return self.resultMessage
