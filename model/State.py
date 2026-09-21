import config
import mysql.connector
from flask import jsonify, redirect, url_for
from model.Utilities import ItemCRUDType
from model.ItemCRUD import ItemCRUD


class State:

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""

    def AddState(self, request):
        state_name = request.form.get('state_Name', '').strip()
        status = request.form.get('status', 'Active').strip()

        connection = config.get_db_connection()
        if not connection:
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
            return self.resultMessage

        try:
            cursor = connection.cursor()
            cursor.callproc('SaveStateWithStatus', (state_name, status))
            connection.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'State added successfully!'}), 200
        except mysql.connector.Error as e:
            print(f"Error adding state: {e}")
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': 'Failed to add state.'}), 500
        finally:
            cursor.close()
            connection.close()

        return self.resultMessage

    def GetAllStates(self, request=None):
        connection = config.get_db_connection()
        data = []
        if not connection:
            return []
        try:
            cursor = connection.cursor()
            cursor.callproc('GetAllStates')
            for res in cursor.stored_results():
                data = res.fetchall()
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error fetching states: {e}")
            self.isSuccess = False
            return []
        finally:
            cursor.close()
            connection.close()
        return data

    def GetActiveStates(self):
        connection = config.get_db_connection()
        data = []
        if not connection:
            return []
        try:
            cursor = connection.cursor()
            cursor.callproc('GetActiveStates')
            for res in cursor.stored_results():
                data = res.fetchall()
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error fetching active states: {e}")
            self.isSuccess = False
            return []
        finally:
            cursor.close()
            connection.close()
        return data

    def CheckStateWithStatus(self, request):
        state_name = request.json.get('state_Name', '').strip()
        if not state_name:
            return jsonify({'status': 'error', 'message': 'State name is required.'}), 400

        connection = config.get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.callproc('CheckStateExists', (state_name,))
            row = None
            for rs in cursor.stored_results():
                row = rs.fetchone()

            if row is None:
                return jsonify({'status': 'available', 'message': 'This state is not added yet. You can add it now.'}), 200

            state_id, state_name_db, state_status, _ = row
            if state_status == 'Active':
                return jsonify({
                    'status': 'active_exists',
                    'message': 'This state is already active in the system.',
                    'state_id': state_id,
                    'state_name': state_name_db
                }), 200
            else:
                return jsonify({
                    'status': 'inactive_exists',
                    'message': 'This state already exists but is inactive.',
                    'state_id': state_id,
                    'state_name': state_name_db
                }), 200

        except mysql.connector.Error as e:
            print(f"Error checking state: {e}")
            return jsonify({'status': 'error', 'message': 'Database error during check.'}), 500
        finally:
            cursor.close()
            connection.close()

    def CheckState(self, request):
        state_name = request.json.get('state_Name', '').strip()
        crud = ItemCRUD(ItemCRUDType.State)
        return crud.CheckItem(
            request=request,
            parentid=None,
            childname=state_name,
            storedprocfetch='CheckStateExists'
        )

    def DeleteState(self, request, id):
        crud = ItemCRUD(ItemCRUDType.State)
        crud.DeleteItem(request=request, itemID=id, storedprocDelete='DeleteState')
        self.isSuccess = crud.isSuccess
        self.resultMessage = crud.resultMessage
        return self.resultMessage

    def EditState(self, request, id):
        state_name = request.form['state_Name'].strip()
        crud = ItemCRUD(ItemCRUDType.State)
        crud.EditItem(
            request=request,
            childid=id,
            parentid=None,
            childname=state_name,
            storedprocupdate='UpdateStateById'
        )
        self.isSuccess = crud.isSuccess
        self.resultMessage = crud.resultMessage
        return redirect(url_for('state.add_state'))

    def GetStateByID(self, request, id):
        connection = config.get_db_connection()
        data = None
        if not connection:
            return None
        try:
            cursor = connection.cursor()
            cursor.callproc('GetStateById', (id,))
            for res in cursor.stored_results():
                data = res.fetchone()
            self.isSuccess = data is not None
            self.resultMessage = 'Success' if data else 'Not Found'
        except mysql.connector.Error as e:
            print(f"Error fetching state: {e}")
            self.isSuccess = False
        finally:
            cursor.close()
            connection.close()
        return data

    def ActivateState(self, id):
        connection = config.get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.callproc('ActivateState', (id,))
            connection.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'State activated successfully.'}), 200
        except mysql.connector.Error as e:
            print(f"Error activating state: {e}")
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': 'Failed to activate state.'}), 500
        finally:
            cursor.close()
            connection.close()
        return self.resultMessage

    def DeactivateState(self, id):
        connection = config.get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.callproc('DeactivateState', (id,))
            connection.commit()
            self.isSuccess = True
            self.resultMessage = jsonify({'status': 'success', 'message': 'State deactivated successfully.'}), 200
        except mysql.connector.Error as e:
            print(f"Error deactivating state: {e}")
            self.isSuccess = False
            self.resultMessage = jsonify({'status': 'error', 'message': 'Failed to deactivate state.'}), 500
        finally:
            cursor.close()
            connection.close()
        return self.resultMessage

    def CheckStateHasDistricts(self, id):
        connection = config.get_db_connection()
        count = 0
        try:
            cursor = connection.cursor()
            cursor.callproc('CheckStateHasDistricts', (id,))
            for rs in cursor.stored_results():
                row = rs.fetchone()
                if row:
                    count = row[0]
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error checking state districts: {e}")
            self.isSuccess = False
        finally:
            cursor.close()
            connection.close()
        return count

    def GetDistrictsByState(self, state_id):
        connection = config.get_db_connection()
        data = []
        try:
            cursor = connection.cursor()
            cursor.callproc('GetDistrictsByStateId', (state_id,))
            for rs in cursor.stored_results():
                data = rs.fetchall()
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error fetching districts for state: {e}")
            self.isSuccess = False
        finally:
            cursor.close()
            connection.close()
        return data
