from datetime import date
from decimal import Decimal, InvalidOperation

from rest_framework.response import Response
from rest_framework.views import APIView

from grades.application.dto.grade_dto import CreateGradeCommand, UpdateGradeCommand
from grades.application.dto.grading_criteria_dto import CreateGradingCriteriaCommand, UpdateGradingCriteriaCommand
from grades.domain.exceptions.grade_exceptions import (
    AssignmentNotFoundForGradeError,
    ClassRoomNotFoundForGradeError,
    GradeNotFoundError,
    StudentNotFoundForGradeError,
    SubjectNotFoundForGradeError,
)
from grades.domain.exceptions.grading_criteria_exceptions import GradingCriteriaNotFoundError
from grades.interfaces.http.grade_use_case_factory import (
    build_create_grade_use_case,
    build_delete_grade_use_case,
    build_get_grade_use_case,
    build_list_grades_use_case,
    build_update_grade_use_case,
)
from grades.interfaces.http.grading_criteria_use_case_factory import (
    build_create_grading_criteria_use_case,
    build_delete_grading_criteria_use_case,
    build_get_grading_criteria_use_case,
    build_list_grading_criteria_use_case,
    build_update_grading_criteria_use_case,
)


class GradeViewSet(APIView):
    def get(self, request, class_room_id=None, pk=None):
        if pk:
            try:
                grade = build_get_grade_use_case().execute(pk)
            except GradeNotFoundError:
                return Response({"error": "Grade not found"}, status=404)
            return Response(grade)
        return Response(build_list_grades_use_case().execute(
            class_room_id=str(class_room_id) if class_room_id else None
        ))

    def post(self, request):
        required_fields = ["student", "class_room", "assignment", "subject", "score", "date"]
        for field in required_fields:
            if request.data.get(field) is None:
                return Response({"error": f"{field} is required"}, status=400)

        try:
            command = CreateGradeCommand(
                student_id=str(request.data.get("student")),
                class_room_id=str(request.data.get("class_room")),
                assignment_id=str(request.data.get("assignment")),
                subject_id=str(request.data.get("subject")),
                score=Decimal(str(request.data.get("score"))),
                date=date.fromisoformat(request.data.get("date")),
                description=request.data.get("description"),
            )
            data = build_create_grade_use_case().execute(command)
            return Response(data, status=201)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        except StudentNotFoundForGradeError:
            return Response({"error": "Student not found"}, status=404)
        except ClassRoomNotFoundForGradeError:
            return Response({"error": "ClassRoom not found"}, status=404)
        except AssignmentNotFoundForGradeError:
            return Response({"error": "Assignment not found"}, status=404)
        except SubjectNotFoundForGradeError:
            return Response({"error": "Subject not found"}, status=404)

    def put(self, request, pk):
        if pk is None:
            return Response({"error": "Grade ID is required"}, status=400)

        try:
            score = request.data.get("score")
            command = UpdateGradeCommand(
                grade_id=pk,
                score=Decimal(str(score)) if score is not None else None,
                description=request.data.get("description"),
            )
            data = build_update_grade_use_case().execute(command)
        except GradeNotFoundError:
            return Response({"error": "Grade not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)

    def delete(self, request, pk):
        try:
            build_delete_grade_use_case().execute(pk)
        except GradeNotFoundError:
            return Response({"error": "Grade not found"}, status=404)
        return Response(status=204)


class GradingCriteriaViewSet(APIView):
    def get(self, request, class_room_id=None, pk=None):
        if pk:
            try:
                criteria = build_get_grading_criteria_use_case().execute(str(pk))
            except GradingCriteriaNotFoundError:
                return Response({"error": "Grading criteria not found"}, status=404)
            return Response(criteria)
        return Response(build_list_grading_criteria_use_case().execute(
            class_room_id=str(class_room_id) if class_room_id else None
        ))

    def post(self, request):
        required_fields = ["name", "class_room", "percentage"]
        for field in required_fields:
            if request.data.get(field) is None:
                return Response({"error": f"{field} is required"}, status=400)

        try:
            command = CreateGradingCriteriaCommand(
                name=request.data["name"],
                class_room_id=str(request.data["class_room"]),
                percentage=Decimal(str(request.data["percentage"])),
                is_attendance_based=bool(request.data.get("is_attendance_based", False)),
            )
            data = build_create_grading_criteria_use_case().execute(command)
            return Response(data, status=201)
        except (ValueError, InvalidOperation):
            return Response({"error": "Invalid request payload"}, status=400)

    def put(self, request, pk=None):
        if pk is None:
            return Response({"error": "Grading criteria ID is required"}, status=400)

        try:
            percentage = request.data.get("percentage")
            command = UpdateGradingCriteriaCommand(
                grading_criteria_id=str(pk),
                name=request.data.get("name"),
                class_room_id=str(request.data["class_room"]) if request.data.get("class_room") else None,
                percentage=Decimal(str(percentage)) if percentage is not None else None,
                is_attendance_based=request.data.get("is_attendance_based"),
            )
            data = build_update_grading_criteria_use_case().execute(command)
        except GradingCriteriaNotFoundError:
            return Response({"error": "Grading criteria not found"}, status=404)
        except (ValueError, InvalidOperation):
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)

    def delete(self, request, pk=None):
        if pk is None:
            return Response({"error": "Grading criteria ID is required"}, status=400)
        try:
            build_delete_grading_criteria_use_case().execute(str(pk))
        except GradingCriteriaNotFoundError:
            return Response({"error": "Grading criteria not found"}, status=404)
        return Response(status=204)
