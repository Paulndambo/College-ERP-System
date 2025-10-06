from apps.core.models import Campus
from apps.core.serializers import CampusListSerializer
from apps.hostels.serializers import HostelRoomListSerializer
from apps.schools.models import Programme, ProgrammeCohort
from apps.users.serializers import UserSerializer
from rest_framework import serializers
from .models import *
from apps.schools.serializers import (
    ProgrammeCohortListSerializer,
    ProgrammeListSerializer,
    SemesterListSerializer,
)


class StudentCreateSerializer(serializers.ModelSerializer):
    programme = serializers.PrimaryKeyRelatedField(
        queryset=Programme.objects.all(), required=False
    )
    cohort = serializers.PrimaryKeyRelatedField(
        queryset=ProgrammeCohort.objects.all(), required=False
    )
    campus = serializers.PrimaryKeyRelatedField(
        queryset=Campus.objects.all(), required=False
    )

    # role = serializers.IntegerField(write_only=True, required=True)
    class Meta:
        model = Student
        fields = [
            "user",
            "registration_number",
            "guardian_name",
            "guardian_phone_number",
            "guardian_relationship",
            "guardian_email",
            "status",
            "programme",
            "cohort",
            "hostel_room",
            "campus",
            # "role",
        ]
        extra_kwargs = {
            "user": {"required": False},
            "cohort": {"required": False},
            "campus": {"required": False},
            "hostel_room": {"required": False},
        }


class MinimalStudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    programme = ProgrammeListSerializer()
    cohort  = ProgrammeCohortListSerializer()
    hostel_room_number = serializers.CharField(
        source="hostel_room.room_number", read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "registration_number",
            "guardian_name",
            "guardian_phone_number",
            "guardian_relationship",
            "guardian_email",
            "status",
            "cohort",
            "programme",
            "hostel_room_number",
        ]


class StudentListSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    programme_name = serializers.CharField(source="programme.name", read_only=True)
    cohort_name = serializers.CharField(source="cohort.name", read_only=True)
    hostel_room_number = serializers.CharField(
        source="hostel_room.room_number", read_only=True
    )
    campus_name = serializers.CharField(source="campus.name", read_only=True)
    current_semester = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "registration_number",
            "guardian_name",
            "guardian_phone_number",
            "guardian_relationship",
            "guardian_email",
            "status",
            "programme_name",
            "cohort_name",
            "hostel_room_number",
            "campus_name",
            "current_semester",
        ]

    def get_current_semester(self, obj):
        if obj.cohort and obj.cohort.current_semester:
            # from apps.schools.serializers import SemesterListSerializer  # Local import to avoid circular import
            return SemesterListSerializer(obj.cohort.current_semester).data
        return None


class StudentDetailSerialzer(serializers.ModelSerializer):
    user = UserSerializer()
    programme = ProgrammeListSerializer()
    hostel_room = HostelRoomListSerializer()
    campus = CampusListSerializer()
    cohort = ProgrammeCohortListSerializer()

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "registration_number",
            "guardian_name",
            "guardian_phone_number",
            "guardian_relationship",
            "guardian_email",
            "status",
            "programme",
            "hostel_room",
            "campus",
            "cohort",
            "created_on",
            "updated_on",
        ]


class StudentEducationHistoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEducationHistory
        fields = "__all__"


class StudentEducationHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEducationHistory
        fields = "__all__"


class StudentDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = "__all__"


class StudentDocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = "__all__"


class MealCardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealCard
        fields = "__all__"


class MealCardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealCard
        fields = "__all__"


class StudentProgrammeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProgramme
        fields = "__all__"


class StudentProgrammeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProgramme
        fields = "__all__"


class StudentAttendanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = "__all__"


class StudentAttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = "__all__"


class StudentCheckInCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCheckIn
        fields = "__all__"


class StudentCheckInListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCheckIn
        fields = "__all__"
