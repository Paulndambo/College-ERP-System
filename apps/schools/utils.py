from apps.admissions.models import Intake
from apps.schools.models import ProgrammeCohort


class AcademicYearUtils:
    """Utility class for academic year operations"""
    @staticmethod
    def get_current_academic_year():
        """Get current academic year based on today's date"""
        from datetime import date
        today = date.today()
        
        if today.month >= 9:
            return f"{today.year}/{today.year + 1}"
        else:
            return f"{today.year - 1}/{today.year}"
    
    @staticmethod
    def get_active_intakes():
        """Get currently active intakes"""
        return Intake.objects.filter(closed=False)
    
    @staticmethod
    def get_cohorts_by_academic_year(academic_year):
        """Get all cohorts for a specific academic year"""
        return ProgrammeCohort.objects.filter(
            intake__start_date__year=int(academic_year.split('/')[0])
        )