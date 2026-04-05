from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import uuid

async def generate_pdf_report(patient, detections, image_path) -> (str | None):

    try:
        pdf_path = f"reports/{uuid.uuid4()}.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        y=750
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, 800, "Dermatology AI Scan Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Patient Name: {patient.name}")
        y -= 20
        c.drawString(50, y, f"Patient Age: {patient.age}")
        y -= 20
        c.drawString(50, y, f"Patient Gender: {patient.gender}")
        y -= 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Detection Results:")
        y -= 20
        c.setFont("Helvetica", 12)
        for d in detections:
            c.drawString(
                50,
                y,
                f"Disease: {d["disease_name"]}"
            )
            y -= 20
            c.drawString(
                70,
                y,
                f"Confidence: {d["confidence"]:.2f}%"
            )
            y -= 30
        c.drawString(50, y, "Scanned Image:")
        c.drawImage(image_path, 50, y-200, width=200, height=200)
        c.save()
        return pdf_path

    except Exception as e:
        print(f"Error generating PDF report: {e}")
        return None