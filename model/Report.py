import config
from datetime import datetime
from flask import send_file
import openpyxl
from openpyxl.styles import Font, PatternFill
from model.excel import excel

from model.FolderAndFile import FolderAndFile

class ReportHelper:
    isSuccess = False
    resultMessage = ""
    data=[]

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""
        self.data = []

    @staticmethod
    def execute_sp(cursor, proc_name, params=[], fetch_one=False):
        cursor.callproc(proc_name, params)
        return (
            ReportHelper.fetch_one_result(cursor)
            if fetch_one else
            ReportHelper.fetch_all_results(cursor)
        )

    @staticmethod
    def fetch_all_results(cursor):
        data = []
        for result in cursor.stored_results():
            data = result.fetchall()
        return data


    @staticmethod
    def fetch_one_result(cursor):
        data = None
        for result in cursor.stored_results():
            data = result.fetchone()
        return data


    @staticmethod
    def search_contractor(request):
        subcontractor_name = request.form.get("subcontractor_name")
        pmc_no = request.form.get("pmc_no")
        state = request.form.get("state")
        district = request.form.get("district")
        block = request.form.get("block")
        village = request.form.get("village")
        year_from = request.form.get("year_from")
        year_to = request.form.get("year_to")

        connection = config.get_db_connection()
        if not connection:
            return []

        cursor = connection.cursor(dictionary=True)

        try:
            data = ReportHelper.execute_sp(
                cursor,
                "search_contractor_info",
                [
                    subcontractor_name or None,
                    pmc_no or None,
                    state or None,
                    district or None,
                    block or None,
                    village or None,
                    year_from or None,
                    year_to or None
                ]
            )

        except Exception as e:
            print(f"Error in search_contractor: {e}")
            data = []

        finally:
            cursor.close()
            connection.close()

        return data

    
    
    @staticmethod
    def get_contractor_info(contractor_id):
        from model.ContractorInfo import ContractorInfo
        contractor = ContractorInfo(contractor_id)
        return contractor.contInfo if contractor.contInfo else None


    