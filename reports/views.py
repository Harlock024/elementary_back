from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
import xml.etree.ElementTree as ET
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


from attendance.models import Attendance
from grades.models import StudentGrade

# Create your views here.
@api_view(['GET'])
def ExportAttendace(request,class_id=None):
    if class_id is None:
        return Response({'error': 'class_id parameter is required.'}, status=400)
    attendances = Attendance.objects.filter(class_room__id=class_id).select_related('student', 'state_code') 

    if not attendances.exists():
        return Response({'error': 'No attendance records found for the given class_id.'}, status=404)

    data = []
    for attendance in attendances:

        full_name = f"{attendance.student.first_name} {attendance.student.second_name or ''}".strip()

        data.append({
            'Matricula': attendance.student.enrollment_number,
            'Nombres': full_name,
            'Apellidos': attendance.student.last_name,
            'Fecha': attendance.date,
            "Estado": attendance.state_code.code,
        })
    df = pd.DataFrame(data)


    df_pivot = df.pivot(
            index=['Matricula', 'Nombres', 'Apellidos'],
            columns='Fecha',
            values='Estado'
            ).reset_index()
        
    df_pivot.columns.fillna('-')
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="asistencias_clase.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df_pivot.to_excel(writer, index=False, sheet_name='Attendance')
    return response

@api_view(['GET'])
def ExportGrades(request,class_id=None):
    if class_id is None:
        return Response({'error': 'class_id parameter is required.'}, status=400)
    grades = StudentGrade.objects.filter(class_room__id=class_id).select_related('student', 'type_code', 'subject')
    if not grades.exists():
        return Response({'error': 'No grade records found for the given class_id.'}, status=404)
    data = []
    for grade in grades:
        full_name = f"{grade.student.first_name} {grade.student.second_name or ''}".strip()
        data.append({
            'Matricula': grade.student.enrollment_number,
            'Nombres': full_name,
            'Apellidos': grade.student.last_name,
            'Materia': grade.subject.name,
            'Tipo de Nota': grade.type_code.code,
            'Valor de Nota': grade.score or 0,
            'Maximo de Nota': grade.max_score,
            'Fecha': grade.date,
            'Descripcion': grade.description or '',
        })
    df = pd.DataFrame(data)
    df_pivot = df.pivot(
            index=['Matricula', 'Nombres', 'Apellidos', 'Materia'],
            columns='Tipo de Nota',
            values='Valor de Nota'
            ).reset_index()
    df_pivot.columns.fillna('-')
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="notas_clase.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df_pivot.to_excel(writer, index=False, sheet_name='Grades')
    return response


