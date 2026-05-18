import pdfplumber, re

def clean(text):
    if not text:
        return ""
    text = text.replace("\n", " ").replace(",", "").replace("₹", "")

    return " ".join(text.split()).strip()

def find(patterns, text):
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return clean(m.group(1))
    return ""

def extract_invoice(pdf_path):
    text = ""
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                lines += page_text.split("\n")
    text = clean(text)

    vendor = ""
    vendor_patterns = ["TAX INVOICE","Invoice From","Seller","Vendor"]
    for i, line in enumerate(lines):
        for word in vendor_patterns:
            if word.lower() in line.lower():
                if i + 1 < len(lines):
                    vendor = clean(lines[i + 1])
                    break

    customer = ""
    customer_patterns = ["Bill To","Ship To","Customer","Buyer"]
    for i, line in enumerate(lines):
        for word in customer_patterns:
            if word.lower() in line.lower():
                if i + 1 < len(lines):
                    customer = clean(lines[i + 1])
                    break

    total = 0
    total_patterns = ["Grand Total","Total Amount","Amount Due","Net Payable","Payable Amount"]
    for line in lines:
        for word in total_patterns:
            if word.lower() in line.lower():
                m = re.search(r"([\d,]+(?:\.\d+)?)",line)
                if m:
                    total = float(m.group(1).replace(",", ""))
                    break

    gstins = re.findall(r"\b[0-9A-Z]{15}\b",text.upper())
    gstins = list(dict.fromkeys(gstins))

    
    invoice_number = find([
        r"Invoice\s*No[:\s\-]+([A-Z0-9\/\-]+)",
        r"Invoice\s*Number[:\s\-]+([A-Z0-9\/\-]+)",
        r"Inv\s*No[:\s\-]+([A-Z0-9\/\-]+)",
        r"Bill\s*No[:\s\-]+([A-Z0-9\/\-]+)"
    ], text)

    invoice_date = find([
        r"Invoice\s*Date[:\s\-]+([A-Za-z0-9\/\-]+)",
        r"Date\s*of\s*Invoice[:\s\-]+([A-Za-z0-9\/\-]+)",
        r"Bill\s*Date[:\s\-]+([A-Za-z0-9\/\-]+)",
        r"Date[:\s\-]+([A-Za-z0-9\/\-]+)"
    ], text)

    data = {
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "vendor_name": vendor,
        "customer_name": customer,
        "vendor_gstin": gstins[0] if len(gstins) > 0 else "",
        "customer_gstin": gstins[1] if len(gstins) > 1 else "",
        "grand_total": total
    }
    return data

result = extract_invoice("invoice.pdf")
print(result)