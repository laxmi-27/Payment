from flask_login import current_user
from model.Utilities import RegEx, ResponseHandler, HtmlHelper, ItemCRUDType
from model.Log import LogHelper

import config
import re
import mysql.connector

# ----------------------------------------------------------
# Mapping Class
# ----------------------------------------------------------
class itemCRUDMapping:

    def __init__(self, itemType):
        if itemType is ItemCRUDType.Village:
            self.name = "Village"
        elif itemType is ItemCRUDType.Block:
            self.name = "Block"
        elif itemType is ItemCRUDType.State:
            self.name = "State"
        elif itemType is ItemCRUDType.HoldType:
            self.name = "Hold Type"
        elif itemType is ItemCRUDType.Subcontractor:
            self.name = "Subcontractor"
        elif itemType.name == "GSTRelease":
            self.name = "GSTRelease"
        else:
            self.name = "Item"

# ----------------------------------------------------------
# Generic CRUD Class
# ----------------------------------------------------------
class ItemCRUD:

    def __init__(self, itemType):
        self.isSuccess = False
        self.resultMessage = ""
        self.itemCRUDType = itemType
        self.itemCRUDMapping = itemCRUDMapping(itemType)

    # ----------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------
    def DeleteItem(self, request, itemID, storedprocDelete):

        connection = config.get_db_connection()
        cursor = connection.cursor()

        LogHelper.log_action(
            f"Delete {self.itemCRUDMapping.name}",
            f"User {current_user.id} deleted {self.itemCRUDMapping.name} '{itemID}'"
        )

        try:
            cursor.callproc(storedprocDelete, (itemID,))
            connection.commit()

            self.isSuccess = True
            self.resultMessage = HtmlHelper.json_response(
                ResponseHandler.delete_success(self.itemCRUDMapping.name), 200
            )

        except mysql.connector.Error as e:
            print(f"Error deleting {self.itemCRUDMapping.name}: {e}")
            self.isSuccess = False
            self.resultMessage = HtmlHelper.json_response(
                ResponseHandler.delete_failure(self.itemCRUDMapping.name), 500
            )

        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # ADD
    # ----------------------------------------------------------
    def AddItem(self, request, parentid=None, childname=None, storedprocfetch=None, storedprocadd=None, data=None):

        connection = config.get_db_connection()
        if not connection:
            self.isSuccess = False
            self.resultMessage = HtmlHelper.json_response(
                ResponseHandler.db_connection_failure(), 500
            )
            return

        cursor = connection.cursor()

        LogHelper.log_action(
            f"Add {self.itemCRUDMapping.name}",
            f"User {current_user.id} adding '{childname if childname else (data.get('Contractor_Name') if data else '')}'"
        )

        try:
            # ======================================================
            # GSTRelease MULTI-FIELD
            # ======================================================
            if self.itemCRUDType.name == "GSTRelease" and data:

                # Duplicate check (PMC_No + Invoice_No)
                if storedprocfetch:
                    cursor.callproc(storedprocfetch, (data['PMC_No'], data['Invoice_No']))
                    existing_item = None
                    for rs in cursor.stored_results():
                        existing_item = rs.fetchone()
                    if existing_item:
                        self.isSuccess = False
                        self.resultMessage = HtmlHelper.json_response(
                            ResponseHandler.already_exists(self.itemCRUDMapping.name), 409
                        )
                        return

                # Insert GSTRelease
                cursor.callproc(storedprocadd, (
                    data['PMC_No'],
                    data['Invoice_No'],
                    data['Basic_Amount'],
                    data['Final_Amount'],
                    data['Total_Amount'],
                    data['UTR'],
                    data['Contractor_ID'],
                    0,  # sort_order
                    data.get('Invoice_Date')  # gst date
                ))
                connection.commit()

                self.isSuccess = True
                self.resultMessage = HtmlHelper.json_response(
                    ResponseHandler.add_success(self.itemCRUDMapping.name), 200
                )
                return

            # ======================================================
            # SUBCONTRACTOR MULTI-FIELD
            # ======================================================
            if self.itemCRUDType.name == "Subcontractor" and data:

                cursor.callproc(storedprocfetch, (data['Contractor_Name'],))
                existing_item = None
                for rs in cursor.stored_results():
                    existing_item = rs.fetchone()

                if existing_item:
                    self.isSuccess = False
                    self.resultMessage = HtmlHelper.json_response(
                        ResponseHandler.already_exists(self.itemCRUDMapping.name), 409
                    )
                    return

                cursor.callproc(storedprocadd, (
                    data['Contractor_Name'],
                    data['Address'],
                    data['Mobile_No'],
                    data['PAN_No'],
                    data['Email'],
                    data['Gender'],
                    data['GST_Registration_Type'],
                    data['GST_No'],
                    data['Contractor_password']
                ))
                connection.commit()
                self.isSuccess = True
                self.resultMessage = HtmlHelper.json_response(
                    ResponseHandler.add_success(self.itemCRUDMapping.name), 200
                )
                return
            

            # ======================================================
            # NORMAL SINGLE-FIELD (Village / Block / State)
            # ======================================================
            if not re.match(RegEx.allPattern, childname):
                self.isSuccess = False
                self.resultMessage = HtmlHelper.json_response(
                    ResponseHandler.invalid_name(self.itemCRUDMapping.name), 400
                )
                return

            if parentid is None:
                cursor.callproc(storedprocfetch, (childname,))
            else:
                cursor.callproc(storedprocfetch, (childname, parentid))

            existing_item = None
            for rs in cursor.stored_results():
                existing_item = rs.fetchone()

            if existing_item:
                self.isSuccess = False
                self.resultMessage = HtmlHelper.json_response(
                    ResponseHandler.already_exists(self.itemCRUDMapping.name), 409
                )
                return

            if parentid is None:
                cursor.callproc(storedprocadd, (childname,))
            else:
                cursor.callproc(storedprocadd, (childname, parentid))

            connection.commit()
            self.isSuccess = True
            self.resultMessage = HtmlHelper.json_response(
                ResponseHandler.add_success(self.itemCRUDMapping.name), 200
            )

        except mysql.connector.Error as e:
            print(f"Database Error: {e}")
            self.isSuccess = False
            self.resultMessage = HtmlHelper.json_response(
                ResponseHandler.add_failure(self.itemCRUDMapping.name), 500
            )

        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # EDIT
    # ----------------------------------------------------------
    def EditItem(self, request, childid, parentid=None, childname=None, storedprocupdate=None, data=None):

        connection = config.get_db_connection()
        cursor = connection.cursor()

        LogHelper.log_action(
            f"Edit {self.itemCRUDMapping.name}",
            f"User {current_user.id} edited '{childid}'"
        )

        try:
            # ======================================================
            # GSTRelease MULTI-FIELD
            # ======================================================
            if self.itemCRUDType.name == "GSTRelease" and data:

                cursor.callproc(storedprocupdate, (
                    data['p_pmc_no'],         # PMC_No
                    data['p_invoice_no'],     # Invoice_No
                    data['p_basic_amount'],   # Basic_Amount
                    data['p_final_amount'],   # Final_Amount
                    data['p_total_amount'],   # Total_Amount
                    data['p_utr'],            # UTR
                    data['p_gst_release_id'], # GST_Release_Id
                    data.get('p_invoice_date')# Invoice_Date
                ))
                connection.commit()

                self.isSuccess = True
                self.resultMessage = HtmlHelper.json_response(
                    ResponseHandler.update_success(self.itemCRUDMapping.name), 200
                )
                return

            # ======================================================
            # SUBCONTRACTOR MULTI-FIELD
            # ======================================================
            if self.itemCRUDType.name == "Subcontractor" and data:

                cursor.callproc(storedprocupdate, (
                    childid,
                    data['Contractor_Name'],
                    data['Address'],
                    data['Mobile_No'],
                    data['PAN_No'],
                    data['Email'],
                    data['Gender'],
                    data['GST_Registration_Type'],
                    data['GST_No'],
                    data['Contractor_password']
                ))
                connection.commit()
                self.isSuccess = True
                self.resultMessage = HtmlHelper.json_response(
                    ResponseHandler.update_success(self.itemCRUDMapping.name), 200
                )
                return

            # ======================================================
            # NORMAL SINGLE-FIELD
            # ======================================================
            if not re.match(RegEx.allPattern, childname):
                self.isSuccess = False
                self.resultMessage = ResponseHandler.update_failure(self.itemCRUDMapping.name)['message']
                return

            if parentid is None:
                cursor.callproc(storedprocupdate, (childid, childname))
            else:
                cursor.callproc(storedprocupdate, (childid, parentid, childname))

            connection.commit()
            self.isSuccess = True
            self.resultMessage = ResponseHandler.update_success(self.itemCRUDMapping.name)['message']

        except mysql.connector.Error as e:
            print(f"Error updating {self.itemCRUDMapping.name}: {e}")
            self.isSuccess = False
            self.resultMessage = HtmlHelper.json_response(
                ResponseHandler.update_failure(self.itemCRUDMapping.name), 500
            )

        finally:
            cursor.close()
            connection.close()

    # ----------------------------------------------------------
    # GET ALL
    # ----------------------------------------------------------
    def GetAllData(self, request, storedproc):

        data = []
        connection = config.get_db_connection()
        if not connection:
            return []

        cursor = connection.cursor()
        try:
            cursor.callproc(storedproc)
            for result in cursor.stored_results():
                data = result.fetchall()
            self.isSuccess = True
        except mysql.connector.Error as e:
            print(f"Error fetching {self.itemCRUDMapping.name}: {e}")
            self.isSuccess = False
            self.resultMessage = HtmlHelper.json_response(
                ResponseHandler.fetch_failure(self.itemCRUDMapping.name), 500
            )
            return []
        finally:
            cursor.close()
            connection.close()

        return data

    # ----------------------------------------------------------
    # GET BY ID
    # ----------------------------------------------------------
    def  GetDataByID(self, id, storedproc):

        data = None
        connection = config.get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.callproc(storedproc, (id,))
            for rs in cursor.stored_results():
                data = rs.fetchone()
        except mysql.connector.Error as e:
            print(f"Error fetching {self.itemCRUDMapping.name}: {e}")
        finally:
            cursor.close()
            connection.close()

        return data

    # ----------------------------------------------------------
    # CHECK ITEM
    # ----------------------------------------------------------
    def CheckItem(self, request, parentid, childname, storedprocfetch):

        connection = config.get_db_connection()
        cursor = connection.cursor()

        LogHelper.log_action(
            f"Check {self.itemCRUDMapping.name}",
            f"User {current_user.id} checked '{childname}'"
        )

        if not re.match(RegEx.allPattern, childname):
            return HtmlHelper.json_response(
                ResponseHandler.invalid_name(self.itemCRUDMapping.name), 400
            )

        try:
            if parentid is None:
                cursor.callproc(storedprocfetch, (childname,))
            else:
                cursor.callproc(storedprocfetch, (childname, parentid))

            existing_item = None
            for rs in cursor.stored_results():
                existing_item = rs.fetchone()

            if existing_item:
                return HtmlHelper.json_response(
                    ResponseHandler.already_exists(self.itemCRUDMapping.name), 409
                )

            return HtmlHelper.json_response(
                ResponseHandler.is_available(self.itemCRUDMapping.name), 200
            )

        except mysql.connector.Error as e:
            print(f"Error checking {self.itemCRUDMapping.name}: {e}")
            return HtmlHelper.json_response(
                ResponseHandler.fetch_failure(self.itemCRUDMapping.name), 500
            )
        finally:
            cursor.close()
            connection.close()