"""
Reports API Endpoints
Handles PDF report generation and download
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from supabase import Client
import io

from app.config import get_supabase_client
from app.services.pdf_service import PDFReportService

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/pdf")
async def download_pdf_report(
    city: str = Query(..., description="City name"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Generate and download PDF report.

    Creates a comprehensive PDF report including:
    - Air quality statistics table (PM2.5, PM10, NO2 averages/min/max)
    - PM2.5 time series chart
    - Weather conditions charts (temperature, humidity)
    - Date range and generation timestamp

    **Parameters:**
    - **city**: City name (Paris, Lyon, Marseille)
    - **start_date**: Report start date in YYYY-MM-DD format
    - **end_date**: Report end date in YYYY-MM-DD format

    **Returns:** PDF file download
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        # Validate date range
        if start > end:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date"
            )

        date_diff = (end - start).days
        if date_diff > 90:
            raise HTTPException(
                status_code=400,
                detail="Date range cannot exceed 90 days"
            )

        # Generate PDF
        pdf_service = PDFReportService(supabase)
        pdf_bytes = await pdf_service.generate_report(city, start, end)

        # Create filename
        filename = f"rapport_{city.lower()}_{start_date}_to_{end_date}.pdf"

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )
