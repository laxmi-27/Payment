import config
import mysql.connector
from flask import request, redirect, url_for

from model.Utilities import ResponseHandler, HtmlHelper, ItemCRUDType
from model.ItemCRUD import ItemCRUD  


class State:

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""

    # ----------------------------------------------------------
    # ADD STATE (USING ITEM CRUD)
    # ----------------------------------------------------------
    def AddState(self, request):
        state_name = request.form['state_Name'].strip()

        crud = ItemCRUD(ItemCRUDType.State)

        crud.AddItem(
            request=request,
            childname=state_name,
            storedprocfetch="CheckStateExists",
            storedprocadd="SaveState"
        )

        self.isSuccess = crud.isSuccess
        self.resultMessage = crud.resultMessage

        return self.resultMessage


    # ----------------------------------------------------------
    # GET ALL STATES (NO CHANGE - THIS IS CORRECT)
    # ----------------------------------------------------------
    def GetAllStates(self, request):
        connection = config.get_db_connection()
        data = []

        if not connection:
            return []

        try:
            cursor = connection.cursor()
            cursor.callproc("GetAllStates")
            for res in cursor.stored_results():
                data = res.fetchall()

            self.isSuccess = True

        except mysql.connector.Error as e:
            print(f"Error fetching states: {e}")
            self.isSuccess = False
            self.resultMessage = HtmlHelper.json_response(
                ResponseHandler.fetch_failure("state"), 500
            )
            return []

        finally:
            cursor.close()
            connection.close()

        return data


    # ----------------------------------------------------------
    # CHECK STATE (USING ITEM CRUD)
    # ----------------------------------------------------------
    def CheckState(self, request):
        state_name = request.json.get('state_Name', '').strip()

        crud = ItemCRUD(ItemCRUDType.State)

        return crud.CheckItem(
            request=request,
            parentid=None,
            childname=state_name,
            storedprocfetch="CheckStateExists"
        )


    # ----------------------------------------------------------
    # DELETE STATE (USING ITEM CRUD)
    # ----------------------------------------------------------
    def DeleteState(self, request, id):
        crud = ItemCRUD(ItemCRUDType.State)

        crud.DeleteItem(
            request=request,
            itemID=id,
            storedprocDelete="DeleteState"
        )

        self.isSuccess = crud.isSuccess
        self.resultMessage = crud.resultMessage

        return self.resultMessage


    # ----------------------------------------------------------
    # EDIT STATE (USING ITEM CRUD)
    # ----------------------------------------------------------
    def EditState(self, request, id):
        state_name = request.form['state_Name'].strip()

        crud = ItemCRUD(ItemCRUDType.State)

        crud.EditItem(
            request=request,
            childid=id,
            parentid=None,
            childname=state_name,
            storedprocupdate="UpdateStateById"
        )

        self.isSuccess = crud.isSuccess
        self.resultMessage = crud.resultMessage

        return redirect(url_for('state.add_state'))


    # ----------------------------------------------------------
    # GET STATE BY ID (KEEP SAME)
    # ----------------------------------------------------------
    def GetStateByID(self, request, id):
        connection = config.get_db_connection()
        data = None

        if not connection:
            return None

        try:
            cursor = connection.cursor()
            cursor.callproc("GetStateByID", (id,))
            for res in cursor.stored_results():
                data = res.fetchone()

            if data:
                self.isSuccess = True
                self.resultMessage = "Success"
            else:
                self.isSuccess = False
                self.resultMessage = "Not Found"

        except mysql.connector.Error as e:
            print(f"Error fetching state: {e}")
            self.isSuccess = False

        finally:
            cursor.close()
            connection.close()

        return data