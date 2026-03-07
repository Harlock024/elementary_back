from decimal import Decimal

from rest_framework.response import Response
from rest_framework.views import APIView

from grades.application.dto.grade_dto import CreateGradeCommand, UpdateGradeCommand
from grades.domain.exceptions.grade_exceptions import (
    CatalogTypeNotFoundError,
    ClassRoomNotFoundForGradeError,
    GradeNotFoundError,
    StudentNotFoundForGradeError,
    SubjectNotFoundForGradeError,
)
from grades.interfaces.http.grade_use_case_factory import (
    build_create_grade_use_case,
    build_delete_grade_use_case,
    build_get_grade_use_case,
    build_list_grades_use_case,
    build_update_grade_use_case,
)
from .models import CatalogTypeGrade
from .serializer import CatalogTypeGradeSerializer


class GradeViewSet(APIView):
    def get(self, request, class_room_id=None, pk=None):
        get_grade_use_case = build_get_grade_use_case()
        list_grades_use_case = build_list_grades_use_case()

        if pk:
            try:
                grade = get_grade_use_case.execute(pk)
            except GradeNotFoundError:
                return Response({"error": "Grade not found"}, status=404)
            return Response(grade)
        elif class_room_id:
            return Response(list_grades_use_case.execute(class_room_id=str(class_room_id)))
        else:
            return Response(list_grades_use_case.execute())

    def post(self, request):
        required_fields = ["student", "class_room", "type_code", "subject", "score", "max_score"]
        for field in required_fields:
            if request.data.get(field) is None:
                return Response({"error": f"{field} is required"}, status=400)

        use_case = build_create_grade_use_case()
        try:
            command = CreateGradeCommand(
                student_id=str(request.data.get("student")),
                class_room_id=str(request.data.get("class_room")),
                type_code_id=str(request.data.get("type_code")),
                subject_id=str(request.data.get("subject")),
                score=Decimal(str(request.data.get("score"))),
                max_score=Decimal(str(request.data.get("max_score"))),
                description=request.data.get("description"),
            )
            data = use_case.execute(command)
            return Response(data, status=201)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        except StudentNotFoundForGradeError:
            return Response({"error": "Student not found"}, status=404)
        except ClassRoomNotFoundForGradeError:
            return Response({"error": "ClassRoom not found"}, status=404)
        except CatalogTypeNotFoundError:
            return Response({"error": "Catalog Type not found"}, status=404)
        except SubjectNotFoundForGradeError:
            return Response({"error": "Subject not found in the specified ClassRoom"}, status=404)

    def put(self, request, pk):
        if pk is None:
            return Response({"error": "Grade ID is required for update"}, status=400)

        update_use_case = build_update_grade_use_case()

        try:
            score = request.data.get("score")
            max_score = request.data.get("max_score")
            command = UpdateGradeCommand(
                grade_id=pk,
                score=Decimal(str(score)) if score is not None else None,
                max_score=Decimal(str(max_score)) if max_score is not None else None,
                description=request.data.get("description"),
                type_code_id=str(request.data.get("type_code")) if request.data.get("type_code") else None,
            )
            data = update_use_case.execute(command)
        except GradeNotFoundError:
            return Response({"error": "Grade not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)

    def delete(self, request, pk):
        delete_use_case = build_delete_grade_use_case()

        try:
            delete_use_case.execute(pk)
        except GradeNotFoundError:
            return Response({"error": "Grade not found"}, status=404)
        return Response(status=204)



class GradeCatalogViewSet(APIView):
    def get(self, request):

        catalog_types = CatalogTypeGrade.objects.all()
        serializer = CatalogTypeGradeSerializer(catalog_types, many=True)
        return Response(serializer.data)

    def post(self, request):

        serializer = CatalogTypeGradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):

        try:
            catalog_type = CatalogTypeGrade.objects.get(pk=pk)
        except CatalogTypeGrade.DoesNotExist:
            return Response({"error": "Catalog Type not found"}, status=404)
        serializer = CatalogTypeGradeSerializer(catalog_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        from .models import CatalogTypeGrade

        try:
            catalog_type = CatalogTypeGrade.objects.get(pk=pk)
        except CatalogTypeGrade.DoesNotExist:
            return Response({"error": "Catalog Type not found"}, status=404)
        catalog_type.delete()
        return Response(status=204)


