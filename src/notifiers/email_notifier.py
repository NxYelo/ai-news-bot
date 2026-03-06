"""
Email notification module using SMTP (Gmail or QQ Mail)
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from ..logger import setup_logger


logger = setup_logger(__name__)


class EmailNotifier:
    """Send email notifications with AI news digest using SMTP"""

    def __init__(
        self,
        gmail_address: Optional[str] = None,
        gmail_app_password: Optional[str] = None,
        email_to: Optional[str] = None,
    ):
        """
        Initialize EmailNotifier with SMTP.
        Supports Gmail and QQ Mail.

        Args:
            gmail_address: Your email address (Gmail or QQ Mail)
            gmail_app_password: App Password / Authorization Code
            email_to: Recipient email address

        All parameters default to environment variables if not provided.
        """
        self.email_address = gmail_address or os.getenv("GMAIL_ADDRESS")
        self.email_password = gmail_app_password or os.getenv("GMAIL_APP_PASSWORD")
        self.email_to = email_to or os.getenv("EMAIL_TO")

        # Detect email provider and set SMTP settings
        if self.email_address and "@qq.com" in self.email_address.lower():
            # QQ Mail settings
            self.smtp_server = "smtp.qq.com"
            self.smtp_port = 465
            self.use_ssl = True
            logger.info(f"EmailNotifier initialized with QQ Mail SMTP (from: {self.email_address})")
        else:
            # Gmail settings (default)
            self.smtp_server = "smtp.gmail.com"
            self.smtp_port = 587
            self.use_ssl = False
            logger.info(f"EmailNotifier initialized with Gmail SMTP (from: {self.email_address})")

        if not all([self.email_address, self.email_password, self.email_to]):
            logger.warning(
                "Email notifier not fully configured. "
                "Required: GMAIL_ADDRESS, GMAIL_APP_PASSWORD, EMAIL_TO"
            )

    def send(self, content: str, subject: Optional[str] = None, language: str = "en") -> bool:
        """
        Send email notification with news digest.

        Args:
            content: Email body content (news digest)
            subject: Email subject. If None, uses default with current date
            language: Language code to include in subject (e.g., 'en', 'zh', 'ja')

        Returns:
            True if email sent successfully, False otherwise
        """
        # Create default subject if not provided
        if subject is None:
            today = datetime.now().strftime("%Y-%m-%d")
            lang_suffix = f" [{language.upper()}]" if language != "en" else ""
            subject = f"🤖 AI日报 - {today}{lang_suffix}"

        if not all([self.email_address, self.email_password, self.email_to]):
            logger.error("Email notifier is not fully configured. Skipping email send.")
            return False

        try:
            # Create HTML email content
            html_content = self._create_html_email(content, subject)

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_address
            msg["To"] = self.email_to

            # Attach plain text and HTML versions
            part1 = MIMEText(content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")
            msg.attach(part1)
            msg.attach(part2)

            logger.info(f"Sending email via SMTP to {self.email_to}")

            # Connect and send based on provider
            if self.use_ssl:
                # QQ Mail uses SSL
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.email_address, self.email_password)
                    server.sendmail(self.email_address, self.email_to, msg.as_string())
            else:
                # Gmail uses STARTTLS
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.email_address, self.email_password)
                    server.sendmail(self.email_address, self.email_to, msg.as_string())

            logger.info("Email sent successfully")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(
                f"SMTP authentication failed: {str(e)}. "
                "For QQ Mail: Make sure you're using the Authorization Code (授权码), not your password. "
                "For Gmail: Make sure you're using an App Password."
            )
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return False

    def _create_html_email(self, content: str, subject: str) -> str:
        """
        Create HTML version of email with proper formatting.

        Args:
            content: Markdown formatted content
            subject: Email subject

        Returns:
            HTML formatted email
        """
        try:
            import markdown
            from markdown.extensions import nl2br, tables, fenced_code

            # Convert markdown to HTML with extensions
            html_content = markdown.markdown(
                content,
                extensions=[
                    'nl2br',      # Convert newlines to <br>
                    'tables',     # Support for tables
                    'fenced_code',# Support for code blocks
                    'sane_lists', # Better list handling
                ]
            )
        except ImportError:
            logger.warning("markdown library not installed, using basic HTML formatting")
            # Fallback to basic HTML escaping and line break conversion
            import html
            html_content = html.escape(content).replace('\n', '<br>\n')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', Helvetica, Arial, sans-serif;
                    line-height: 1.8;
                    color: #24292e;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f6f8fa;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 40px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .title {{
                    color: #0366d6;
                    font-size: 28px;
                    font-weight: 700;
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 3px solid #0366d6;
                    text-align: center;
                }}
                .content {{
                    margin-top: 30px;
                }}
                .content h1 {{
                    color: #0366d6;
                    font-size: 24px;
                    font-weight: 700;
                    margin-top: 30px;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #0366d6;
                }}
                .content h2 {{
                    color: #2c3e50;
                    font-size: 20px;
                    font-weight: 600;
                    margin-top: 25px;
                    margin-bottom: 12px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid #e1e4e8;
                }}
                .content h3 {{
                    color: #24292e;
                    font-size: 18px;
                    font-weight: 600;
                    margin-top: 20px;
                    margin-bottom: 10px;
                    padding-left: 10px;
                    border-left: 3px solid #0366d6;
                }}
                .content p {{
                    margin: 12px 0;
                    line-height: 1.8;
                    color: #24292e;
                }}
                .content ul, .content ol {{
                    margin: 12px 0;
                    padding-left: 25px;
                }}
                .content li {{
                    margin: 8px 0;
                    line-height: 1.7;
                }}
                .content strong {{
                    font-weight: 600;
                    color: #0366d6;
                }}
                .content a {{
                    color: #0366d6;
                    text-decoration: none;
                }}
                .content a:hover {{
                    text-decoration: underline;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 15px;
                    border-top: 1px solid #e1e4e8;
                    text-align: center;
                    color: #586069;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="title">{subject}</div>
                <div class="content">
                    {html_content}
                </div>
                <div class="footer">
                    Generated by AI News Bot | 通义千问驱动
                </div>
            </div>
        </body>
        </html>
        """
        return html