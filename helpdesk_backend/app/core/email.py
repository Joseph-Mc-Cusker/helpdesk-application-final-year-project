from typing import Optional
import os

from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.models.ticket import TicketStatus

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@helpdesk.local")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5500")


async def send_email(to_email: str, subject: str, html_content: str) -> None:
  """Send email via SendGrid. If not configured, just log to console."""
  if not SENDGRID_API_KEY:
    print(f"[EMAIL] Would send to {to_email}: {subject}")
    return

  try:
    message = Mail(
      from_email=FROM_EMAIL,
      to_emails=to_email,
      subject=subject,
      html_content=html_content,
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(f"Email sent to {to_email}: {response.status_code}")
  except Exception as exc:  # noqa: BLE001
    print(f"Error sending email: {exc}")


async def send_ticket_created_email(user_email: str, user_name: str, ticket_id: str, ticket_title: str) -> None:
  subject = f"Helpdesk Ticket Created: {ticket_title}"
  html = f"""
  <h2>Ticket Created</h2>
  <p>Hello {user_name},</p>
  <p>Your helpdesk ticket has been created.</p>
  <p><strong>ID:</strong> {ticket_id}</p>
  <p><strong>Title:</strong> {ticket_title}</p>
  <p>View: <a href="{FRONTEND_ORIGIN}">{FRONTEND_ORIGIN}</a></p>
  """
  await send_email(user_email, subject, html)


async def send_ticket_status_email(
  user_email: str,
  user_name: str,
  ticket_id: str,
  ticket_title: str,
  new_status: TicketStatus,
  resolution_notes: Optional[str] = None,
) -> None:
  """Notify ticket creator when status changes. Uses resolved-specific email when status is resolved."""
  if new_status == TicketStatus.RESOLVED:
    await send_ticket_resolved_email(user_email, user_name, ticket_id, ticket_title, resolution_notes)
    return
  subject = f"Ticket Status Updated: {ticket_title}"
  html = f"""
  <h2>Ticket Status Updated</h2>
  <p>Hello {user_name},</p>
  <p>Your ticket status is now: <strong>{new_status.value.replace('_', ' ').title()}</strong></p>
  <p><strong>ID:</strong> {ticket_id}</p>
  <p><strong>Title:</strong> {ticket_title}</p>
  """
  if resolution_notes:
    html += f"<p><strong>Resolution notes:</strong> {resolution_notes}</p>"
  html += f'<p>View: <a href="{FRONTEND_ORIGIN}">{FRONTEND_ORIGIN}</a></p>'
  await send_email(user_email, subject, html)


async def send_ticket_resolved_email(
  user_email: str,
  user_name: str,
  ticket_id: str,
  ticket_title: str,
  resolution_notes: Optional[str] = None,
) -> None:
  """Notify the end user that their IT issue / ticket has been resolved."""
  subject = f"Your ticket has been resolved: {ticket_title}"
  html = f"""
  <h2>Your ticket has been resolved</h2>
  <p>Hello {user_name},</p>
  <p>The IT issue you reported has been resolved.</p>
  <p><strong>Ticket:</strong> {ticket_title}</p>
  <p><strong>Ticket ID:</strong> {ticket_id}</p>
  """
  if resolution_notes:
    html += f"<p><strong>Resolution notes from support:</strong></p><p>{resolution_notes}</p>"
  html += f"""
  <p>You can view your tickets and any further updates at: <a href="{FRONTEND_ORIGIN}">{FRONTEND_ORIGIN}</a></p>
  <p>Thank you for using the Helpdesk.</p>
  """
  await send_email(user_email, subject, html)

