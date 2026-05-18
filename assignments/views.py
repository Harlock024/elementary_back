from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from assignments.application.dtos.assignments_dto import (
    CreateAssignmentCommand,
    UpdateAssignmentCommand,
)
from assignments.domain.exceptions.assignments_exception import (
    AssignmentsAlreadyExistsError,
    AssignmentsNotFoundError,
    ClassRoomNotFoundError,
    StudentNotFoundForAssignmentsError,
)
from assignments.interfaces.http.assignment_use_case_factory import (
    build_create_assignment_use_case,
    build_delete_assignment_use_case,
    build_list_assignments_use_case,
    build_update_assignment_use_case,
)

# Create your views here.


class AssignmentView(APIView):
    def get(self, request, class_id=None, student_id=None):
        use_case = build_list_assignments_use_case()
        assignment_data = use_case.execute(
            class_id=str(class_id) if class_id else None,
            student_id=str(student_id) if student_id else None,
        )
        return Response(assignment_data, status=200)

    def post(self, request, class_id=None):
        if not class_id:
            return Response({"error": "Class ID is required"}, status=400)

        subject_id = request.data.get("subject_id")
        grading_criteria_id = request.data.get("grading_criteria_id")
        print(grading_criteria_id)
        title = request.data.get("title")
        description = request.data.get("description")
        due_date = request.data.get("due_date")
        max_score = request.data.get("max_score")

        if (
            not subject_id
            or not grading_criteria_id
            or not title
            or not due_date
            or not max_score
        ):
            return Response(
                {
                    "error": "subject_id  , grading_criteria_id, title, due_date and max_score are required"
                },
                status=400,
            )
        use_case = build_create_assignment_use_case()
        try:
            command = CreateAssignmentCommand(
                class_id=str(class_id),
                subject_id=str(subject_id),
                grading_criteria_id=str(grading_criteria_id),
                title=title,
                description=description,
                due_date=datetime.fromisoformat(due_date),
                max_score=int(max_score),
            )
            data = use_case.execute(command)
            return Response(data, status=201)
        except ValueError:
            return Response({"error": "Invalid date format for due_date"}, status=400)
        except AssignmentsAlreadyExistsError as exc:
            return Response({"error": str(exc)}, status=400)
        except StudentNotFoundForAssignmentsError as exc:
            return Response({"error": str(exc)}, status=400)
        except ClassRoomNotFoundError as exc:
            return Response({"error": str(exc)}, status=400)

    def delete(self, request, id=None):
        if not id:
            return Response({"error": "Assignment ID is required"}, status=400)
        try:
            build_delete_assignment_use_case().execute(str(id))
        except AssignmentsNotFoundError:
            return Response({"error": "Assignment not found"}, status=404)
        return Response(status=204)

    def patch(self, request, id=None):
        if not id:
            return Response({"error": "Assignment ID is required"}, status=400)

        subject_id = request.data.get("subject_id")
        grading_criteria_id = request.data.get("grading_criteria_id")
        title = request.data.get("title")
        description = request.data.get("description")
        due_date = request.data.get("due_date")
        max_score = request.data.get("max_score")

        update_use_case = build_update_assignment_use_case()
        try:
            command = UpdateAssignmentCommand(
                assignment_id=str(id),
                subject_id=str(subject_id) if subject_id else None,
                grading_criteria_id=str(grading_criteria_id)
                if grading_criteria_id
                else None,
                title=title if title else None,
                description=description if description else None,
                due_date=datetime.fromisoformat(due_date) if due_date else None,
                max_score=int(max_score) if max_score else None,
            )
            data = update_use_case.execute(command)
            return Response(data, status=200)
        except ValueError:
            return Response({"error": "Invalid date format for due_date"}, status=400)
        except AssignmentsNotFoundError as exc:
            return Response({"error": str(exc)}, status=404)
        except StudentNotFoundForAssignmentsError as exc:
            return Response({"error": str(exc)}, status=400)
        except ClassRoomNotFoundError as exc:
            return Response({"error": str(exc)}, status=400)
