import smtplib
from email.message import EmailMessage


async def send_email(patient_email, pdf_path, hospital_email):
    
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Your Dermatology AI Scan Report'
        msg['From'] = hospital_email
        msg['To'] = patient_email
        msg.set_content('Please find attached your dermatology AI scan report.')

        with open(pdf_path, 'rb') as f:
            msg.add_attachment(
                f.read(),
                maintype='application',
                subtype='pdf',
                filename="scan_report.pdf"
            )

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.login(hospital_email, 'your_email_password')  # Replace with actual password or use environment variable
        server.send_message(msg)
        server.quit()
            
    except Exception as e:
        print(f"Error sending email: {e}")      
        raise e