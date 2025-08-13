from decimal import Decimal, ROUND_HALF_UP

from apps.staff.models import OvertimeRecords, Payslip, Staff


def calculate_paye(taxable_income):
    personal_relief = Decimal("2400")
    taxable_income = Decimal(taxable_income).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    tax = Decimal("0")

    if taxable_income <= 24000:
        tax = taxable_income * Decimal("0.1")
    elif taxable_income <= 32333:
        tax = Decimal("24000") * Decimal("0.1") + (
            taxable_income - Decimal("24000")
        ) * Decimal("0.25")
    else:
        tax = (
            Decimal("24000") * Decimal("0.1")
            + (Decimal("32333") - Decimal("24000")) * Decimal("0.25")
            + (taxable_income - Decimal("32333")) * Decimal("0.3")
        )

    tax_after_relief = tax - personal_relief
    if tax_after_relief < 0:
        tax_after_relief = Decimal("0")
    return tax_after_relief.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def calculate_nhif(gross_salary):
    gross_salary = float(gross_salary)
    if gross_salary <= 5999:
        return Decimal("150")
    elif gross_salary <= 7999:
        return Decimal("300")
    elif gross_salary <= 11999:
        return Decimal("400")
    elif gross_salary <= 14999:
        return Decimal("500")
    elif gross_salary <= 19999:
        return Decimal("600")
    elif gross_salary <= 24999:
        return Decimal("750")
    elif gross_salary <= 29999:
        return Decimal("850")
    elif gross_salary <= 34999:
        return Decimal("900")
    elif gross_salary <= 39999:
        return Decimal("950")
    elif gross_salary <= 44999:
        return Decimal("1000")
    elif gross_salary <= 49999:
        return Decimal("1100")
    elif gross_salary <= 59999:
        return Decimal("1200")
    elif gross_salary <= 69999:
        return Decimal("1300")
    elif gross_salary <= 79999:
        return Decimal("1400")
    elif gross_salary <= 89999:
        return Decimal("1500")
    elif gross_salary <= 99999:
        return Decimal("1600")
    else:
        return Decimal("1700")


def calculate_nssf(gross_salary):
    gross_salary = Decimal(gross_salary)
    # 6% employee contribution
    nssf_contrib = gross_salary * Decimal("0.06")
    return nssf_contrib.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def process_payroll_monthly_period(payroll_period_start, payroll_period_end):
    from decimal import Decimal

    # Pre-fetch all active staff with their payroll data in one query
    active_staff = Staff.objects.select_related('staffpayroll').filter(status="Active")
    
    # Pre-fetch all overtime records for the period in one query
    overtime_records = OvertimeRecords.objects.filter(
        date__range=(payroll_period_start, payroll_period_end),
        approved=True
    ).select_related('staff')
    
    # Create a dictionary for quick overtime lookup
    overtime_by_staff = {}
    for record in overtime_records:
        if record.staff_id not in overtime_by_staff:
            overtime_by_staff[record.staff_id] = []
        overtime_by_staff[record.staff_id].append(record)

    payslips_to_create = []
    
    for staff in active_staff:
        payroll = staff.staffpayroll
        if not payroll:
            continue

        # Calculate overtime from pre-fetched data
        staff_overtime = overtime_by_staff.get(staff.id, [])
        total_overtime_pay = sum(
            (o.hours * o.rate_per_hour for o in staff_overtime), Decimal(0)
        )

        total_allowances = (
            payroll.house_allowance
            + payroll.transport_allowance
            + payroll.other_allowances
        )

        gross_pay = payroll.basic_salary + total_allowances + total_overtime_pay

        # Calculate deductions
        nssf = calculate_nssf(gross_pay)
        nhif = calculate_nhif(gross_pay)

        # Taxable income for PAYE = gross - NSSF (as NSSF is deductible before tax)
        taxable_income = gross_pay - nssf
        paye = calculate_paye(taxable_income)

        total_deductions = nssf + nhif + paye
        net_pay = gross_pay - total_deductions

        # Create payslip object (don't save yet)
        payslip = Payslip(
            staff=staff,
            payroll_period_start=payroll_period_start,
            payroll_period_end=payroll_period_end,
            basic_salary=payroll.basic_salary,
            total_allowances=total_allowances,
            total_overtime=total_overtime_pay,
            total_deductions=total_deductions,
            nssf=nssf,
            nhif=nhif,
            paye=paye,
            net_pay=net_pay,
        )
        payslips_to_create.append(payslip)

        print(
            f"Payslip for {staff} | Gross: {gross_pay} | NSSF: {nssf} | NHIF: {nhif} | PAYE: {paye} | Net Pay: {net_pay}"
        )

    # Bulk create all payslips in one operation
    if payslips_to_create:
        Payslip.objects.bulk_create(payslips_to_create)
        print(f"Successfully created {len(payslips_to_create)} payslips")
    else:
        print("No payslips to create")
