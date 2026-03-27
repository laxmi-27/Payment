from model.ItemCRUD import ItemCRUD
from model.Utilities import ItemCRUDType

class GST:

    @staticmethod
    def get_unreleased_gst():
        # Use ItemCRUD for Invoices
        invoice_crud = ItemCRUD(itemType=ItemCRUDType.Invoice)
        invoices_rows = invoice_crud.GetAllData(storedproc="GetAllInvoicesBasic")

        if not invoice_crud.isSuccess:
            return []  # Could also log invoice_crud.resultMessage

        invoices = [
            dict(
                Invoice_No=row[1],
                GST_SD_Amount=float(row[2]) if row[2] is not None else 0
            )
            for row in invoices_rows
        ]

        # Use ItemCRUD for GST Releases
        gst_crud = ItemCRUD(itemType=ItemCRUDType.GSTRelease)
        gst_rows = gst_crud.GetAllData(storedproc="GetAllGSTReleasesBasic")

        if not gst_crud.isSuccess:
            return []  # Could also log gst_crud.resultMessage

        gst_invoice_nos = {
            g[2]  # Invoice_No is at index 2
            for g in gst_rows
            if g[2]
        }

        gst_basic_amounts = {
            float(g[3])  # Basic_Amount at index 3
            for g in gst_rows
            if g[3] is not None
        }

        # Filter unreleased invoices
        unreleased = []
        for inv in invoices:
            match_by_invoice = inv['Invoice_No'] in gst_invoice_nos
            match_by_gst_amount = inv['GST_SD_Amount'] in gst_basic_amounts

            if not (match_by_invoice or match_by_gst_amount):
                unreleased.append(inv)

        return unreleased