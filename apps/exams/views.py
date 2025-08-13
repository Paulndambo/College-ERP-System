from apps.exams.filters import ExamDataFilterSet, TranscriptsFilter
from apps.schools.models import Course, ProgrammeCohort, Semester
from apps.students.models import Student
from apps.students.serializers import (
    MinimalStudentSerializer,
    StudentDetailSerialzer,
    StudentListSerializer,
)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from services.constants import ALL_ROLES, ROLE_STUDENT
from services.permissions import HasUserRole
from .models import ExamData
from .serializers import (
    ExamDataCreateSerializer,
    ExamDataListSerializer,
    MarkSerializer,
    MinimalSemesterSerializer,
    StudentExamDataSerializer,
)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
import io
import csv
from rest_framework.permissions import IsAuthenticated


class ExamDataCreateAPIView(generics.CreateAPIView):
    # queryset = ExamData.objects.all()
    serializer_class = ExamDataCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class BulkExamDataUploadAPIView(generics.CreateAPIView):
    """
    API endpoint for uploading multiple student exam marks via CSV or Excel file.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ExamDataCreateSerializer

    def post(self, request, *args, **kwargs):
        if "file" not in request.FILES:
            return Response(
                {"error": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        file_obj = request.FILES["file"]
        course_id = request.data.get("course")
        semester_id = request.data.get("semester")
        cohort_id = request.data.get("cohort")
        print("cohort_id from request:", cohort_id)

        file_extension = file_obj.name.split(".")[-1].lower()

        if file_extension not in ["csv", "CSV"]:
            raise CustomAPIException(
                "Unsupported file format. Please upload a CSV or Excel file.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:

            if file_extension == "csv":
                data = self._process_csv(file_obj)
            
            else:
                data = []

            if not data:
                raise CustomAPIException(
                    "File is empty or contains no valid data.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Verify required columns
            required_columns = [
                "registration_number",
                "cat_one",
                "cat_two",
                "exam_marks",
            ]
            for row in data:
                missing_columns = [col for col in required_columns if col not in row]
                if missing_columns:
                    raise CustomAPIException(
                        f"Missing required columns: {', '.join(missing_columns)}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

            result = self._process_data(
                data, course_id=course_id, semester_id=semester_id, cohort_id=cohort_id
            )

            if result["created"] == 0:
                raise CustomAPIException(
                    "Marks upload failed. Either all the marks already exist or invalid data was provided i.e invalid  registration number in the uploaded file.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "count": result["created"],
                    "failed_count": result["failed"],
                    "errors": result["errors"] if result["errors"] else None,
                },
                status=status.HTTP_201_CREATED,
            )

        except CustomAPIException as e:

            raise e
        except Exception as e:
            raise CustomAPIException(
                f"Error processing file: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _process_csv(self, file_obj):
        try:
            decoded_file = file_obj.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            return list(reader)
        except Exception as e:
            raise CustomAPIException(
                f"Error reading CSV file: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def _process_data(self, data, course_id, semester_id, cohort_id):

        try:
            course = Course.objects.get(id=int(course_id))

        except (Course.DoesNotExist,) as e:
            raise CustomAPIException(
                f"Invalid reference: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            semester = Semester.objects.get(id=int(semester_id))
        except (ValueError, Semester.DoesNotExist):
            raise CustomAPIException(
                f"Invalid cohort ID: {cohort_id}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            cohort = ProgrammeCohort.objects.get(id=int(cohort_id))
        except (ValueError, ProgrammeCohort.DoesNotExist):
            raise CustomAPIException(
                f"Invalid cohort ID: {cohort_id}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        created_count = 0
        errors = []

        for index, row in enumerate(data):
            try:

                if "registration_number" not in row or not row["registration_number"]:
                    raise ValueError(f"Missing registration number")

                try:
                    student = Student.objects.get(
                        registration_number=row["registration_number"]
                    )
                except Student.DoesNotExist:
                    raise ValueError(
                        f"Student with registration number {row['registration_number']} not found"
                    )

                marks_data = {
                    "student": student.id,
                    "semester": semester.id,
                    "course": course.id,
                    "cohort": cohort.id,
                    "cat_one": float(row.get("cat_one", 0)),
                    "cat_two": float(row.get("cat_two", 0)),
                    "exam_marks": float(row.get("exam_marks", 0)),
                }

                if ExamData.objects.filter(
                    student=student, semester=semester, course=course, cohort=cohort
                ).exists():
                    raise ValueError(
                        f"Marks for student {row['registration_number']} in this course and semester for given cohort/class already exist."
                    )

                with transaction.atomic():

                    serializer = self.get_serializer(data=marks_data)
                    serializer.is_valid(raise_exception=True)

                    serializer.save(recorded_by=self.request.user)

                created_count += 1

            except Exception as e:

                errors.append(
                    {
                        "row": index + 2,
                        "registration_number": row.get(
                            "registration_number", f"Row {index + 2}"
                        ),
                        "error": str(e),
                    }
                )

        return {"created": created_count, "failed": len(errors), "errors": errors}


class ExamDataListAPIView(generics.ListAPIView):
    queryset = ExamData.objects.all()
    permission_classes = [IsAuthenticated]
    # allowed_roles = ALL_ROLES
    serializer_class = ExamDataListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExamDataFilterSet
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        base_queryset = ExamData.objects.select_related(
            "student", "semester", "cohort", "course", "recorded_by"
        )
        # if user.role.name == ROLE_STUDENT:
        #     if user.role.name == ROLE_STUDENT:
        #         return base_queryset.filter(student=user)

        #     exam_data = base_queryset.order_by("-created_on")
        #     return exam_data

        exam_data = base_queryset.order_by("-created_on")
        return exam_data

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            filtered_queryset = self.filter_queryset(queryset)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_exam_data = paginator.paginate_queryset(
                    filtered_queryset, request
                )
                serializer = self.get_serializer(paginated_exam_data, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(filtered_queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExamDatapdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = ExamData.objects.all()
    serializer_class = ExamDataCreateSerializer
    http_method_names = ["patch", "put"]
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(recorded_by=self.request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TranscriptsDataView(generics.ListAPIView):
    queryset = ExamData.objects.all().select_related(
        "student",
        "student__user",
        "student__programme",
        "semester",
        "cohort",
        "course",
        "recorded_by",
    )
    serializer_class = StudentExamDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TranscriptsFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        base_queryset = ExamData.objects.select_related(
            "student",
            "student__user",
            "student__programme",
            "semester",
            "cohort",
            "course",
            "recorded_by",
        )

        programme_id = self.request.query_params.get("programme")
        semester_id = self.request.query_params.get("semester")
        cohort_id = self.request.query_params.get("cohort")
        reg_no = self.request.query_params.get("reg_no")
        if (
            not (programme_id and semester_id)
            and not (cohort_id and semester_id)
            and not (reg_no and semester_id)
        ):
            raise CustomAPIException(
                "You must provide either (programme and semester), or (cohort/class and semester), or (reg_no and semester).",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if programme_id and semester_id:
            base_queryset = base_queryset.filter(
                student__programme_id=programme_id, semester_id=semester_id
            )
        elif cohort_id and semester_id:
            base_queryset = base_queryset.filter(
                cohort_id=cohort_id, semester_id=semester_id
            )
        elif reg_no and semester_id:
            base_queryset = base_queryset.filter(
                student__registration_number=reg_no, semester_id=semester_id
            )

        return base_queryset.order_by("-created_on")

    def list(self, request, *args, **kwargs):
        """
        Override the default list method to structure the response with student, semester, and marks data.
        Each student will have semester info and their corresponding marks appended to their data.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())

            semester_id = self.request.query_params.get("semester")

            student_data = {}

            for exam in queryset:
                student_id = exam.student.id

                if student_id not in student_data:
                    student_serializer = StudentDetailSerialzer(exam.student)
                    semester_serializer = MinimalSemesterSerializer(exam.semester)

                    student_data[student_id] = {
                        "student": student_serializer.data,
                        "semester": semester_serializer.data,
                        "marks": [],
                    }

                mark_serializer = MarkSerializer(exam)
                student_data[student_id]["marks"].append(mark_serializer.data)

            response_data = list(student_data.values())

            page = request.query_params.get("page", None)
            if page:
                paginator = self.pagination_class()
                paginated_data = paginator.paginate_queryset(response_data, request)
                return paginator.get_paginated_response(paginated_data)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
