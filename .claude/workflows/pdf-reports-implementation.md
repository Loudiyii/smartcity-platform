# Workflow: PDF Reports

## Objectif
Génération rapports PDF (Air, Mobilité, Combiné).

## Référence
- **User Story:** US-014
- **Skills:** `backend-api`

## Étapes

### 1. Install ReportLab
```bash
pip install reportlab matplotlib
```

### 2. PDF Generation
```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_air_quality_report(data):
    pdf = canvas.Canvas("report.pdf", pagesize=A4)
    pdf.drawString(100, 800, "Air Quality Report")
    # Add data, charts
    pdf.save()
    return "report.pdf"
```

### 3. Endpoint
```python
@router.get("/reports/air-quality/pdf")
async def download_report():
    pdf_path = generate_air_quality_report(data)
    return FileResponse(pdf_path, filename="report.pdf")
```

## Critères
- [ ] PDF généré
- [ ] Charts inclus
- [ ] Download fonctionnel
