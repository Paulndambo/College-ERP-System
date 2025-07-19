from django.core.mail import EmailMessage
from io import BytesIO
from django.template.loader import render_to_string
from weasyprint import HTML


def send_payslip_email(payslip):
    html_string = render_to_string(
        "payroll/payslip_template.html", {"payslip": payslip}
    )
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)
    pdf_file.seek(0)

    email = EmailMessage(
        subject=f"Your Payslip for period {payslip.payroll_period_start} to {payslip.payroll_period_end}",
        body="Please find your payslip attached.",
        to=[payslip.staff.user.email],
    )
    email.attach(
        f"Payslip_{payslip.payroll_period_start}_{payslip.payroll_period_end}.pdf",
        pdf_file.read(),
        "application/pdf",
    )
    email.send()
