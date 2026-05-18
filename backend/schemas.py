from pydantic import BaseModel

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str = None
    invoice_date: str = None
    vendor_name: str = None
    customer_name: str = None
    vendor_gstin: str = None
    customer_gstin: str = None
    grand_total: float = None

    class Config:
        from_attributes = True