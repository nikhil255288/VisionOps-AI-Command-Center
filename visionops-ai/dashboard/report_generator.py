from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf_report(session_name, total_events, unique_visitors, avg_dwell, max_dwell):
    file_path = f"data/exports/{session_name}_report.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, height - 60, "VisionOps AI Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 95, f"Generated At: {datetime.now()}")
    c.drawString(50, height - 125, f"Video Session: {session_name}")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 170, "Analytics Summary")

    c.setFont("Helvetica", 13)
    c.drawString(70, height - 210, f"Total Events: {total_events}")
    c.drawString(70, height - 235, f"Unique Visitors: {unique_visitors}")
    c.drawString(70, height - 260, f"Average Dwell Time: {avg_dwell}s")
    c.drawString(70, height - 285, f"Maximum Dwell Time: {max_dwell}s")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 340, "AI Recommendation")

    c.setFont("Helvetica", 12)
    c.drawString(70, height - 370, "Monitor high-footfall zones and allocate staff during peak activity.")

    c.save()
    return file_path