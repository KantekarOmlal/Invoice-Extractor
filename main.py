import os
from fastapi import FastAPI, UploadFile, File, Depends, Body
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
from models import Invoice
from extractor import extract_invoice

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CREATE TABLES
Base.metadata.create_all(bind=engine)

# DATABASE
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# UPLOAD INVOICE
@app.post("/upload")
async def upload_invoice(file: UploadFile = File(...),db: Session = Depends(get_db)):
    os.makedirs("uploads", exist_ok=True)
    path = f"uploads/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())
    data = extract_invoice(path)
    invoice = Invoice(**data)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

# GET ALL INVOICES
@app.get("/invoices")
def get_invoices(db: Session = Depends(get_db)):
    result = db.execute(select(Invoice))
    invoices = result.scalars().all()

    data = []
    for i in invoices:
        data.append({
            "id": i.id,
            "invoice_number": i.invoice_number,
            "invoice_date": i.invoice_date,
            "vendor_name": i.vendor_name,
            "vendor_gstin": i.vendor_gstin,
            "customer_name": i.customer_name,
            "customer_gstin": i.customer_gstin,
            "grand_total": i.grand_total
        })
    return data

@app.put("/invoice/{invoice_id}")
def update_invoice(invoice_id: int,data: dict = Body(...),db: Session = Depends(get_db)):

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id
    ).first()

    if not invoice:
        return {"message": "Invoice not found"}

    invoice.vendor_name = data["vendor_name"]
    invoice.customer_name = data["customer_name"]
    db.commit()
    db.refresh(invoice)
    return invoice