from sqlalchemy import Column, Integer, String, Float
from database import Base  

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String)
    invoice_date = Column(String)
    vendor_name = Column(String)
    customer_name = Column(String)
    vendor_gstin = Column(String)
    customer_gstin = Column(String)
    grand_total = Column(Float)