import config
import ast
import re
import openpyxl
from flask_login import current_user
from flask_login import login_required
from flask import Blueprint, request, render_template, redirect, url_for, jsonify

from model.Log import LogHelper
from model.FolderAndFile import FolderAndFile

excel_bp = Blueprint('excel', __name__)

# ---------------- Upload Excel File ----------------
@excel_bp.route('/upload_excel_file', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            filepath =FolderAndFile.get_upload_path(file.filename)

            file.save(filepath)

            LogHelper.log_action(
                "Upload Excel File",
                f"User {current_user.id} Upload Excel File '{file.filename}'"
            )
            return redirect(url_for('excel.show_table', filename=file.filename))
    
    return render_template('uploadExcelFile.html')


# ---------------- Show Excel Table ----------------
@excel_bp.route('/show_table/<filename>')
def show_table(filename):
        global data
        data = []

        filepath = FolderAndFile.get_upload_path(filename)
        wb = openpyxl.load_workbook(filepath, data_only=True)
        sheet = wb.active

        file_info = {
            "Subcontractor": sheet.cell(row=1, column=2).value,
            "State": sheet.cell(row=2, column=2).value,
            "District": sheet.cell(row=3, column=2).value,
            "Block": sheet.cell(row=4, column=2).value,
        }

        errors = []
        subcontractor_data = None
        state_data = None
        district_data = None
        block_data = None

        connection = config.get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)

                cursor.callproc('CheckStateExists', [file_info['State']])
                for result in cursor.stored_results():
                    state_data = result.fetchone()
                if not state_data:
                    errors.append(f"State '{file_info['State']}' is not valid. Please add it.")

                if state_data:
                    cursor.callproc('GetDistrictByNameAndState', [file_info['District'], state_data['State_Id']])     # Change GetDistrictByNameAndStates to GetDistrictByNameAndState
                    for result in cursor.stored_results():
                        district_data = result.fetchone()
                    if not district_data:
                        errors.append(f"District '{file_info['District']}' is not valid under state '{file_info['State']}'.")

                if district_data:
                    cursor.callproc('GetBlockByNameAndDistrict', [file_info['Block'], district_data['District_id']])       #Change District_ID to District_id  and GetBlockByNameAndDistricts to GetBlockByNameAndDistrict
                    for result in cursor.stored_results():
                        block_data = result.fetchone()
                    if not block_data:
                        errors.append(f"Block '{file_info['Block']}' is not valid under district '{file_info['District']}'.")

                cursor.callproc('GetSubcontractorByName', [file_info['Subcontractor']])
                for result in cursor.stored_results():
                    subcontractor_data = result.fetchone()

                if not subcontractor_data:
                    cursor.callproc('SaveContractor', [file_info.get('Subcontractor'),None,None,None,None,None,None,None,None])
                    connection.commit()
                    cursor.callproc('GetSubcontractorByName', [file_info['Subcontractor']])
                    for result in cursor.stored_results():
                        subcontractor_data = result.fetchone()

                cursor.callproc("GetAllHoldTypes")
                hold_types_data = []
                for ht in cursor.stored_results():
                    hold_types_data = ht.fetchall()
                hold_types_lookup = {row['hold_type'].lower(): row['hold_type_id'] for row in hold_types_data if row['hold_type']}

                cursor.close()
            except Exception as e:
                print(f"Database error: {e}")
                return f"Database operation failed: {e}", 500
            finally:
                connection.close()

        variables = {}
        hold_columns = []
        hold_counter = 0

        for j in range(1, sheet.max_column + 1):
            col_value = sheet.cell(row=5, column=j).value
            if col_value:
                variables[col_value] = j
                if 'hold' in str(col_value).lower():
                    hold_counter += 1
                    hold_type_key = str(col_value).lower().strip()
                    hold_type_id = hold_types_lookup.get(hold_type_key)
                    hold_columns.append({
                        'column_name': col_value,
                        'column_number': j,
                        'hold_type_id': hold_type_id
                    })

        for i in range(6, sheet.max_row + 1):
            row_data = {}
            if sheet.cell(row=i, column=1).value:
                row_data["Row Number"] = i
                for var_name, col_num in variables.items():
                    row_data[var_name] = sheet.cell(row=i, column=col_num).value
                if sum(1 for value in row_data.values() if value) >= 4:
                    data.append(row_data)

        for hold in hold_columns:
            if hold['hold_type_id']:
                print(f" if Column: {hold['column_name']}, Column Number: {hold['column_number']}, Hold Type ID: {hold['hold_type_id']}")
            else:
                errors.append(f"Hold Type not added ! Column name '{hold['column_name']}'.")
                print(f" else Column: {hold['column_name']}, Column Number: {hold['column_number']}, Hold Type ID: {hold['hold_type_id']}")

        return render_template(
            'show_excel_file.html',
            file_info=file_info,
            variables=variables,
            data=data,
            subcontractor_data=subcontractor_data,
            state_data=state_data,
            district_data=district_data,
            block_data=block_data,
            errors=errors,
            hold_columns=hold_columns,
            hold_counter=hold_counter
        )


 # save Excel data
@excel_bp.route('/save_data', methods=['POST'])
def save_data():
    # Extract form data
    subcontractor_id = request.form.get("subcontractor_data")
    state_id = request.form.get("state_data")
    district_id = request.form.get("district_data")
    block_id = request.form.get("block_data")
    variables = request.form.getlist('variables[]')
    hold_columns = request.form.get("hold_columns")
    hold_counter = request.form.get("hold_counter")
    if not data:
        return jsonify({"error": "No data provided to save"}), 400
    if data:
        connection = config.get_db_connection()
        cursor = connection.cursor()
        try:
            for entry in data:
                save_data = {
                    "PMC_No": entry.get("PMC_No"),
                    "Invoice_Details": entry.get("Invoice_Details", ''),
                    "Work_Type": 'none',
                    "Invoice_Date": entry.get("Invoice_Date").strftime('%Y-%m-%d') if entry.get(
                    "Invoice_Date") else None,
                    "Invoice_No": entry.get("Invoice_No", ''),
                    "Basic_Amount": entry.get("Basic_Amount", 0.00),
                    "Debit_Amount": entry.get("Debit_Amount", 0.00),
                    "After_Debit_Amount": entry.get("After_Debit_Amount", 0.00),
                    "Amount": entry.get("Amount", 0.00),
                    "GST_Amount": entry.get("GST_Amount", 0.00),
                    "TDS_Amount": entry.get("TDS_Amount", 0.00),
                    "SD_Amount": entry.get("SD_Amount", 0.00),
                    "On_Commission": entry.get("On_Commission", 0.00),
                    "Hydro_Testing": entry.get("Hydro_Testing", 0.00),
                    "Hold_Amount": entry.get("Hold_Amount", 0.00),   # change
                    "GST_SD_Amount": entry.get("GST_SD_Amount", 0.00),
                    "Final_Amount": entry.get("Final_Amount", 0.00),
                    "Payment_Amount": entry.get("Payment_Amount", 0.00),
                    "Total_Amount": entry.get("Total_Amount", 0.00),
                    "TDS_Payment_Amount": entry.get("TDS_Payment_Amount", 0.00),
                    "UTR": entry.get("UTR", ''),
                }
                village_name, work_type = None, None
                village_id = 0
                LogHelper.log_action("Data saved", f"User {current_user.id} Data saved'{  village_name}'")
                PMC_No = save_data.get('PMC_No')
                Invoice_Details = save_data.get('Invoice_Details')
                Invoice_Date = save_data.get('Invoice_Date')
                Invoice_No = save_data.get('Invoice_No')
                Basic_Amount = save_data.get('Basic_Amount')
                Debit_Amount = save_data.get('Debit_Amount')
                After_Debit_Amount = save_data.get('After_Debit_Amount')
                Amount = save_data.get('Amount')
                GST_Amount = save_data.get('GST_Amount')
                TDS_Amount = save_data.get('TDS_Amount')
                SD_Amount = save_data.get('SD_Amount')
                On_Commission = save_data.get('On_Commission')
                Hydro_Testing = save_data.get('Hydro_Testing')
                GST_SD_Amount = save_data.get('GST_SD_Amount')
                Final_Amount = save_data.get('Final_Amount')
                Payment_Amount = save_data.get('Payment_Amount')
                Total_Amount = save_data.get('Total_Amount')
                TDS_Payment_Amount = save_data.get('TDS_Payment_Amount')
                UTR = save_data.get('UTR')
                
                if Invoice_Details:
                    words = Invoice_Details.lower().split()
                    if 'village' in words:
                        village_pos = words.index('village')
                        village_name = " ".join(words[:village_pos])
                    if 'work' in words:
                        work_pos = words.index('work')
                        if village_name:
                            work_type = " ".join(words[village_pos + 1:work_pos + 1])
                        else:
                            work_type = " ".join(words[:work_pos + 1])
                    if Invoice_Details and 'village' in Invoice_Details.lower() and 'work' in Invoice_Details.lower():
                        # print("village_name ::", village_name, "|| work_type ::", work_type)
                        if block_id and village_name:
                            village_id = None
                            cursor.callproc("GetVillageId", (block_id, village_name))
                            for result in cursor.stored_results():
                                result = result.fetchone()
                            village_id = result[0] if result else None
                            if not village_id:
                                cursor.callproc("SaveVillage", (village_name, block_id))
                                cursor.callproc("GetVillageId", (block_id, village_name))
                                for result in cursor.stored_results():
                                    result = result.fetchone()
                                village_id = result[0] if result else None
                        
                        args = (
                            PMC_No, village_id, work_type, Invoice_Details, Invoice_Date, Invoice_No,
                            Basic_Amount, Debit_Amount, After_Debit_Amount, Amount, GST_Amount, TDS_Amount,
                            SD_Amount, On_Commission, Hydro_Testing, GST_SD_Amount, Final_Amount,
                            subcontractor_id, 0
                        )

                        
                        # add subcontarctor id in invoice table
                        results = cursor.callproc('SaveInvoice', args)
                        invoice_id = results[-1]

                        cursor.callproc(
                            "SavePayment",
                            (
                                PMC_No,
                                Invoice_No,            
                                Payment_Amount,
                                TDS_Payment_Amount,
                                Total_Amount,
                                UTR,
                                invoice_id             
                            )
                        )
                        
                       
                        if isinstance(hold_columns, str):
                            hold_columns = ast.literal_eval(hold_columns)
                        if isinstance(hold_columns, list) and all(isinstance(hold, dict) for hold in hold_columns):
                            for hold in hold_columns:
                                # print(f"Processing hold: {hold}")
                                hold_column_name = hold.get('column_name')  # Get column name
                                hold_type_id = hold.get('hold_type_id')  # Get hold_type_id
                                if hold_column_name:
                                    hold_amount = entry.get(
                                        hold_column_name)  # Get the value for that specific hold column
                                    if hold_amount is not None:
                                       
                                        hold_join_data = {
                                            "Contractor_Id": subcontractor_id,
                                            "Invoice_Id": invoice_id,
                                            "hold_type_id": hold_type_id,
                                            "hold_amount": hold_amount
                                        }
                                        cursor.callproc('InsertHoldJoinData', [
                                            hold_join_data['Contractor_Id'], hold_join_data['Invoice_Id'],
                                            hold_join_data['hold_type_id'], hold_join_data['hold_amount']
                                        ])
                                        connection.commit()
                                        print(f"Inserted hold join data: {hold_join_data}")
                                else:
                                    print(f"Invalid hold entry: {hold}")
                        else:
                            print("Hold columns data is not a valid list of dictionaries.")
                    #-----------------------------------Credit Note----------------------------------------------------------------
                    # elif any(keyword in Invoice_Details.lower() for keyword in ['credit', 'logging report']):
                    elif any(keyword in Invoice_Details.lower() for keyword in ['credit','debit', 'logging report']):    
    
                        cursor.callproc(
                            'AddCreditNoteFromExcel',
                            [
                                PMC_No, Invoice_Details, Basic_Amount, Debit_Amount, After_Debit_Amount, 
                                GST_Amount, Amount, Final_Amount, Payment_Amount, Total_Amount, UTR, 
                                subcontractor_id, Invoice_No
                            ]
                        )
                    #---------------------------------------Hold Amount-----------------------------------------------------------
                    # Step 1: Normalize Invoice_Details: lowercase, trim, remove extra spaces
                    normalized_details = re.sub(r'\s+', ' ', Invoice_Details.strip()).lower()
                    # Step 2: Define lowercase keywords
                    keywords = [
                        'excess hold',
                        'ht',
                        'hold release amount',
                        'dpr excess hold amount',
                        'excess hold amount',
                        'Multi to Single layer bill',
                        'hold amount',
                        'logging report'
                    ]
                    # Step 3: Matching condition
                    if any(kw in normalized_details for kw in keywords):
                        cursor.callproc(
                            'AddHoldReleaseFromExcel',
                            [PMC_No, Invoice_No, Invoice_Details, Basic_Amount, Final_Amount, UTR, subcontractor_id])
                        connection.commit() 
                    #------------------------------------------------------------------------------------------------------------------
                    elif Invoice_Details and any(
                            keyword in Invoice_Details.lower() for keyword in ['gst', 'release', 'gst release note']):
                        cursor.callproc(
                            'AddGSTReleaseFromExcel',
                            [PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount, UTR, subcontractor_id]
                        )

                # --------------------------------------
                # If no village/work detected, only PMC/Payment
                if not (Invoice_Details and 'village' in Invoice_Details.lower() and 'work' in Invoice_Details.lower()):                        
                    # ---------- Only PMC / Payment rows ----------
                    if PMC_No and  not Invoice_No and  UTR :
                        cursor.callproc("insertExtrapaymet",(PMC_No, subcontractor_id))
                        for result in cursor.stored_results():
                            row = result.fetchone()
                            invoice_id = row[0] if row else None
                        # insert payment
                        cursor.callproc(
                            "SavePayment",
                            (
                                PMC_No,
                                Invoice_No,            
                                Payment_Amount,
                                TDS_Payment_Amount,
                                Total_Amount,
                                UTR,
                                invoice_id 
                            )
                        )
                   
            connection.commit()
            return jsonify({"success": "Data saved successfully!"}), 200
        except Exception as e:
            connection.rollback()
            return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
        finally:
            cursor.close()
            connection.close()
    return render_template('index.html')
