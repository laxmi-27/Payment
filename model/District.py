from model.Utilities import ItemCRUDType
from model.ItemCRUD import ItemCRUD

class District:

    isSuccess = False
    resultMessage = ""

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""

    # edit district 
    def EditDistrict(self, request, district_id):
        district = ItemCRUD(itemType=ItemCRUDType.District)

        district_name = request.form['district_Name'].strip()
        state_id = request.form['state_Id']

        district.EditItem(request=request, childid=district_id, parentid=state_id, childname=district_name,storedprocupdate="UpdateDistrict" )
        self.isSuccess = district.isSuccess
        self.resultMessage = district.resultMessage
        return
            
    # add district
    def AddDistrict(self, request): 

       district = ItemCRUD(ItemCRUDType.District)

       district_name = request.form['district_Name'].strip()
       state_id = request.form['state_Id']

       district.AddItem(request=request, parentid=state_id, childname=district_name,  storedprocfetch="GetDistrictByNameAndState", storedprocadd="SaveDistrict" )
       self.isSuccess = district.isSuccess
       self.resultMessage = district.resultMessage
       return
 
 
    # get all district data
    def GetAllDistricts(self, request):
        district = ItemCRUD(itemType=ItemCRUDType.District)
        districtsdata = district.GetAllData(request=request, storedproc="GetAllDistricts")
        self.isSuccess = district.isSuccess
        self.resultMessage = district.resultMessage
        return districtsdata

    # check district validation
    def CheckDistrict(self, request):
        district = ItemCRUD(itemType=ItemCRUDType.District)
        district_name = request.json.get('district_Name', '').strip()
        state_id = request.json.get('state_Id', '')
        result = district.CheckItem(request=request, parentid=state_id, childname=district_name, storedprocfetch="GetDistrictByNameAndState")
        self.isSuccess = district.isSuccess
        self.resultMessage = district.resultMessage
        return result

    # get district by district id
    def GetDistrictByID(self, request, district_id):
        district = ItemCRUD(itemType=ItemCRUDType.District)

        districtdata = district.GetDataByID(
            id=district_id,
            storedproc="GetDistrictDataByID"
        )

        if districtdata:
            self.isSuccess = True
        else:
            self.isSuccess = False
            self.resultMessage = "District not found"

        return districtdata
        

    # Delete District by district id
    def DeleteDistrict(self, request, district_id):
        district = ItemCRUD(itemType=ItemCRUDType.District)
        district.DeleteItem(request=request,itemID=district_id,storedprocDelete="DeleteDistrict")
        self.isSuccess = district.isSuccess
        self.resultMessage = str(district.resultMessage) 