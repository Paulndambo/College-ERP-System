from typing import List, Dict, Any, Tuple
from django.db import transaction
from apps.students.models import Student, SemesterReporting
from apps.schools.models import Semester, ProgrammeCohort
from apps.finance.models import FeeStructure
from apps.student_finance.mixins import StudentInvoicingMixin
from apps.students.reporting.serializers import CreateSemesterReportingSerializer
from apps.students.reporting.usecases.promote_students import promote_students_to_next_semester

class SemesterReportingService:
    """Service class to handle semester reporting business logic"""
    
    @staticmethod
    def create_student_invoice(student, semester):
        """
        Create invoice for a single student
        
        Args:
            student: Student instance
            semester: Semester instance
            
        Returns:
            bool: True if invoice created successfully, False otherwise
        """
        fee_structure = FeeStructure.objects.filter(
            programme=student.programme,
            semester__name=semester.name,
        ).first()

        if not fee_structure:
            print(f"No fee structure found for programme {student.programme} and semester {semester.name}")
            return False

        semester_total_fees = fee_structure.total_amount()

        try:
            success = StudentInvoicingMixin(
                student=student,
                semester=semester,
                transaction_type="Standard Invoice",
                amount=semester_total_fees,
            ).run()
            
            print(f"Invoice creation for student {student.id}: {'Success' if success else 'Failed'}")
            return success
            
        except Exception as e:
            print(f"Error creating invoice for student {student.id}: {str(e)}")
            return False

    @staticmethod
    def create_invoices_for_students(students, semester):
        """
        Create invoices for multiple students and return results
        
        Args:
            students: List of Student instances
            semester: Semester instance
            
        Returns:
            List of dictionaries containing invoice creation results
        """
        results = []
        
        for student in students:
            try:
                success = SemesterReportingService.create_student_invoice(student, semester)
                results.append({
                    'student_id': student.id,
                    'student_name': str(student),
                    'success': success,
                    'error': None if success else 'Invoice creation failed'
                })
            except Exception as e:
                results.append({
                    'student_id': student.id,
                    'student_name': str(student),
                    'success': False,
                    'error': str(e)
                })
        
        return results

    @staticmethod
    def get_fee_structure(student, semester):
        """
        Get fee structure for a student and semester
        
        Args:
            student: Student instance
            semester: Semester instance
            
        Returns:
            FeeStructure instance or None
        """
        return FeeStructure.objects.filter(
            programme=student.programme,
            semester__name=semester.name,
        ).first()

    @staticmethod
    def validate_semester_for_reporting(semester):
        """
        Validate if a semester is valid for reporting
        
        Args:
            semester: Semester instance
            
        Returns:
            Dictionary with validation result
        """
        if semester.status == "Closed":
            return {
                'is_valid': False,
                'error': 'Cannot report to a closed semester.'
            }
        
        return {'is_valid': True, 'error': None}

    @staticmethod
    def get_invoice_summary(invoice_results):
        """
        Generate summary of invoice creation results
        
        Args:
            invoice_results: List of invoice creation results
            
        Returns:
            Dictionary with summary statistics
        """
        successful_invoices = sum(1 for result in invoice_results if result['success'])
        failed_invoices = len(invoice_results) - successful_invoices
        
        summary = {
            'total_students': len(invoice_results),
            'successful_invoices': successful_invoices,
            'failed_invoices': failed_invoices,
            'success_rate': (successful_invoices / len(invoice_results)) * 100 if invoice_results else 0
        }
        
        if failed_invoices > 0:
            summary['failed_invoice_details'] = [
                result for result in invoice_results if not result['success']
            ]
        
        return summary

    @staticmethod
    @transaction.atomic
    def handle_individual_reporting(semester, request_data):
        """
        Handle individual student semester reporting with invoicing
        
        Args:
            semester: Semester object from database
            request_data: Dictionary containing request data
            
        Returns:
            Tuple of (success, response_data, status_code)
        """
        # Validate semester first
        semester_validation = SemesterReportingService.validate_semester_for_reporting(semester)
        if not semester_validation['is_valid']:
            return False, {"error": semester_validation['error']}, 400
        
        serializer = CreateSemesterReportingSerializer(data=request_data)

        if not serializer.is_valid():
            return False, serializer.errors, 400

        reporting = serializer.save()
        
        invoice_success = SemesterReportingService.create_student_invoice(
            reporting.student, 
            semester  
        )
        
        if invoice_success:
            return True, {"message": "Student reporting created and invoice generated successfully"}, 201
        else:
            return False, {"error": "Student reporting created but invoice generation failed"}, 207

    @staticmethod
    @transaction.atomic
    def handle_cohort_promotion(cohort, next_semester):
        """
        Handle cohort promotion with automatic invoicing for all students
        
        Args:
            cohort: ProgrammeCohort object from database
            next_semester: Semester object from database
            
        Returns:
            Tuple of (success, response_data, status_code)
        """
        # Validate semester
        semester_validation = SemesterReportingService.validate_semester_for_reporting(next_semester)
        if not semester_validation['is_valid']:
            return False, {"error": semester_validation['error']}, 400

        try:
            # Promote students to next semester (this creates SemesterReporting records)
            skipped_students = promote_students_to_next_semester(cohort, next_semester)
            # Get the promoted students from the created SemesterReporting records
            promoted_reporting = SemesterReporting.objects.filter(
                cohort=cohort,
                semester=next_semester
            ).select_related('student')
            
            promoted_students = [reporting.student for reporting in promoted_reporting]
            
            # Create invoices for all promoted students
            invoice_results = SemesterReportingService.create_invoices_for_students(
                promoted_students, 
                next_semester
            )
            
            # Get summary of invoice results
            summary = SemesterReportingService.get_invoice_summary(invoice_results)
            
            response_data = {
                "message": "Students promoted successfully",
                **summary 
            }
            if skipped_students:
                response_data["skipped_students"] = {
                    "count": len(skipped_students),
                    "reason": f"Missing fee structure for semester '{next_semester.name}' in cohort '{cohort.name}'"
                }
            return True, response_data, 200
            
        except ValueError as e:
            return False, {"error": str(e)}, 400
        except Exception as e:
            return False, {"error": f"An unexpected error occurred: {str(e)}"}, 500