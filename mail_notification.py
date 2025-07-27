import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def send_email(to_email, subject, message, image_path=None):
    """
    Send a simple email using configured SMTP settings.

    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        message (str): Email body text
        image_path (str, optional): Path to image file to attach

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get email configuration from environment variables
        mail_host = os.getenv('MAIL_HOST')
        mail_port = int(os.getenv('MAIL_PORT'))
        mail_username = os.getenv('MAIL_USERNAME')
        mail_password = os.getenv('MAIL_PASSWORD')
        mail_from_address = os.getenv('MAIL_FROM_ADDRESS')
        mail_from_name = os.getenv('MAIL_FROM_NAME')

        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{mail_from_name} <{mail_from_address}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(message, 'plain'))

        # Add image attachment if provided
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data)
                image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                msg.attach(image)

        # Create SMTP session with STARTTLS (port 587)
        server = smtplib.SMTP(mail_host, mail_port)
        server.starttls()  # Enable TLS encryption
        server.login(mail_username, mail_password)

        # Send email
        text = msg.as_string()
        server.sendmail(mail_from_address, to_email, text)
        server.quit()

        print(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# Example usage
if __name__ == "__main__":
    send_email(
        to_email="ryanrasoarahona@gmail.com",
        subject="Backtest Results - IBM",
        message="Please find attached the backtest plot for IBM.",
        image_path="plots/backtest_plot_IBM_2025-07-27.png"
    )