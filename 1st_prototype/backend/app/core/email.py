from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv
from typing import Optional
from app.models.ticket import TicketStatus

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@helpdesk.local")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")


async def send_email(to_email: str, subject: str, html_content: str):
    """Send email using SendGrid"""
    if not SENDGRID_API_KEY:
        print(f"[EMAIL] Would send to {to_email}: {subject}")
        print(f"[EMAIL] Content: {html_content}")
        return
    
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {to_email}: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")


async def send_ticket_created_email(user_email: str, user_name: str, ticket_id: str, ticket_title: str):
    """Send email when a new ticket is created"""
    subject = f"Helpdesk Ticket Created: {ticket_title}"
    html_content = f"""
    <html>
        <body>
            <h2>Ticket Created Successfully</h2>
            <p>Hello {user_name},</p>
            <p>Your helpdesk ticket has been created successfully.</p>
            <p><strong>Ticket ID:</strong> {ticket_id}</p>
            <p><strong>Title:</strong> {ticket_title}</p>
            <p>You can view your ticket at: <a href="{FRONTEND_URL}/tickets/{ticket_id}">{FRONTEND_URL}/tickets/{ticket_id}</a></p>
            <p>Thank you for using our helpdesk system.</p>
        </body>
    </html>
    """
    await send_email(user_email, subject, html_content)


async def send_ticket_assigned_email(support_email: str, support_name: str, ticket_id: str, ticket_title: str, created_by: str):
    """Send email to support staff when ticket is assigned"""
    subject = f"New Ticket Assigned: {ticket_title}"
    html_content = f"""
    <html>
        <body>
            <h2>New Ticket Assigned</h2>
            <p>Hello {support_name},</p>
            <p>A new helpdesk ticket has been assigned to you.</p>
            <p><strong>Ticket ID:</strong> {ticket_id}</p>
            <p><strong>Title:</strong> {ticket_title}</p>
            <p><strong>Created by:</strong> {created_by}</p>
            <p>You can view and manage this ticket at: <a href="{FRONTEND_URL}/tickets/{ticket_id}">{FRONTEND_URL}/tickets/{ticket_id}</a></p>
        </body>
    </html>
    """
    await send_email(support_email, subject, html_content)


async def send_ticket_status_update_email(user_email: str, user_name: str, ticket_id: str, ticket_title: str, new_status: TicketStatus, resolution_notes: Optional[str] = None):
    """Send email when ticket status is updated"""
    status_messages = {
        TicketStatus.OPEN: "Your ticket is now open",
        TicketStatus.IN_PROGRESS: "Your ticket is now being worked on",
        TicketStatus.RESOLVED: "Your ticket has been resolved",
        TicketStatus.CLOSED: "Your ticket has been closed"
    }
    
    subject = f"Ticket Status Update: {ticket_title}"
    html_content = f"""
    <html>
        <body>
            <h2>Ticket Status Updated</h2>
            <p>Hello {user_name},</p>
            <p>{status_messages.get(new_status, 'Your ticket status has been updated')}.</p>
            <p><strong>Ticket ID:</strong> {ticket_id}</p>
            <p><strong>Title:</strong> {ticket_title}</p>
            <p><strong>New Status:</strong> {new_status.value.replace('_', ' ').title()}</p>
            {f'<p><strong>Resolution Notes:</strong> {resolution_notes}</p>' if resolution_notes else ''}
            <p>You can view your ticket at: <a href="{FRONTEND_URL}/tickets/{ticket_id}">{FRONTEND_URL}/tickets/{ticket_id}</a></p>
        </body>
    </html>
    """
    await send_email(user_email, subject, html_content)

