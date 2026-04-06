from model.Utilities import RegEx, ResponseHandler, HtmlHelper, ItemCRUDType

from model.ItemCRUD import ItemCRUD, itemCRUDMapping


class Block:

    isSuccess = False
    resultMessage = ""

    def __init__(self):
        self.isSuccess = False
        self.resultMessage = ""

    # ----------------------------------------------------------
    # Add Block
    # ----------------------------------------------------------
    def AddBlock(self, request):

       block = ItemCRUD(itemType=ItemCRUDType.Block)

       district_id = request.form.get('district_Id')
       block_name = request.form.get('block_Name', '').strip()

       block.AddItem(request=request, parentid=district_id, childname=block_name,  storedprocfetch="GetBlockByNameAndDistrict", storedprocadd="SaveBlock" )   # Change GetBlockByNameAndDistricts to GetBlockByNameAndDistrict
       self.isSuccess = block.isSuccess
       self.resultMessage = block.resultMessage
       return

    # ----------------------------------------------------------
    # Get All Blocks
    # ----------------------------------------------------------            
    def GetAllBlocks(self, request):

        block = ItemCRUD(itemType=ItemCRUDType.Block)
        blocksdata = block.GetAllData(request=request, storedproc="GetAllBlock")

        self.isSuccess = block.isSuccess
        self.resultMessage = block.resultMessage
        return blocksdata

    # ----------------------------------------------------------
    # Check Block Exists
    # ----------------------------------------------------------
    def CheckBlock(self, request):
        block = ItemCRUD(itemType=ItemCRUDType.Block)
        data = request.get_json(silent=True) or request.form
        block_name = (data.get('block_Name') or '').strip()
        district_id = data.get('district_Id')

        result = block.CheckItem(
            request=request,
            parentid=district_id,
            childname=block_name,
            storedprocfetch="GetBlockByNameAndDistrict"
        )
        self.isSuccess = block.isSuccess
        self.resultMessage = block.resultMessage
        return result

    # ----------------------------------------------------------
    # Get Block By ID
    # ----------------------------------------------------------
    def GetBlockByID(self, id):

        block = ItemCRUD(itemType=ItemCRUDType.Block)

        blockdata = block.GetDataByID(
            id=id,
            storedproc="GetBlockDataByID"
        )

        self.isSuccess = block.isSuccess
        self.resultMessage = block.resultMessage

        return blockdata
    # ----------------------------------------------------------
    # Update Block
    # ----------------------------------------------------------
    def EditBlock(self, request, block_id):

        block = ItemCRUD(itemType=ItemCRUDType.Block)

        district_id = request.form.get('district_Id')
        block_name = request.form.get('block_Name', '').strip()

        block.EditItem(
            request=request,
            childid=block_id,
            parentid=district_id,
            childname=block_name,
            storedprocupdate="UpdateBlockById"
        )

        self.isSuccess = block.isSuccess
        self.resultMessage = block.resultMessage
        return 
  
    # ----------------------------------------------------------
    # Delete Block
    # ---------------------------------------------------------       
    def DeleteBlock(self,request, id):
        block = ItemCRUD(itemType=ItemCRUDType.Block)

        block.DeleteItem(request=request,itemID=id, storedprocDelete="DeleteBlock")
        self.isSuccess = block.isSuccess
        self.resultMessage = block.resultMessage
        return