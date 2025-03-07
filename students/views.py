from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import (
    StudentSerializer,
    FeePaymentSerializer,
    StudentEnrollmentHistorySerializer,
    ClassViewSerializer,
)
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Student, FeePayment, Class

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from rest_framework import status

# Create your views here.


class StudentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        print("data", data)
        serialize = StudentSerializer(data=data)

        if serialize.is_valid(raise_exception=True):
            serialize.save()
            return JsonResponse("student created", safe=False)
        return JsonResponse("failed to insert", safe=False)

    def get(self, request, pk=None):
        if pk:
            student = get_object_or_404(Student, id=pk)
            serializer = StudentSerializer(student)
            # Include related FeePayment data
            data = serializer.data

            fee_payments = FeePayment.objects.filter(student_id=pk)
            fee_serializer = FeePaymentSerializer(fee_payments, many=True)
            data["fee_payments"] = fee_serializer.data
            return Response(data)
        try:
            student = Student.objects.all().order_by("-id")
            serializer = StudentSerializer(student, many=True)

            return Response(serializer.data)
        except Exception as e:
            print(e)

    def put(self, request, pk=None):
        data = request.data
        student_to_update = Student.objects.get(id=pk)
        serialize = StudentSerializer(
            instance=student_to_update, data=data, partial=True
        )
        if serialize.is_valid():
            serialize.save()
            return Response({"message": "Record Updated", "data": serialize.data})
        else:
            return Response(serialize.errors, status=400)  # Bad request

    def delete(self, request, pk=None):
        student_to_delete = Student.objects.get(id=pk)
        if student_to_delete:
            student_to_delete.delete()
            return Response({"message": "Deleted Successfully!"}, status=200)
        else:
            return Response(
                {"message": "Student Doesnt Exist", "data": "null"}, status=404
            )


class FeePaymentView(APIView):
    def get(self, request, studentId=None):
        print("StudentId", studentId)
        if studentId:
            feeDetails = FeePayment.objects.filter(student=studentId)
            print("FeeDetails", feeDetails)
            serialize = FeePaymentSerializer(feeDetails, many=True)
            return Response(serialize.data)
        else:
            fees = FeePayment.objects.all().order_by("-payment_date")
            serialize = FeePaymentSerializer(fees, many=True)
            return Response(serialize.data)

    def post(self, request):
        data = request.data
        print("data", data)
        serialize = FeePaymentSerializer(data=data)

        if serialize.is_valid(raise_exception=True):
            fee_record = serialize.save()
            return JsonResponse(serialize.data, status=status.HTTP_201_CREATED)
        return JsonResponse(
            {"error": "Failed to insert", "details": serialize.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UpdateAcadamicYearView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            with transaction.atomic():
                students = Student.objects.all()
                for student in students:
                    enrollment_data = {
                        "student": student.id,
                        "class_enrolled": student.class_enrolled_id,
                        "academic_year": student.academic_year,
                        "total_fees_paid": student.total_fees_paid,
                        "pen_fees": student.pen_fees,
                    }
                    enrollment_serializer = StudentEnrollmentHistorySerializer(
                        data=enrollment_data
                    )
                    if enrollment_serializer.is_valid() and student.is_active == True:
                        enrollment_serializer.save()
                        if student.class_enrolled_id == 12:
                            student.is_active = False
                        else:
                            student.class_enrolled_id += 1
                            student.total_fees_paid = 0
                            student.pen_fees = 0
                            student.academic_year = increment_academic_year(
                                student.academic_year
                            )

                        student.save()
            return Response(
                {"message": "Sucessfully updated academic year and class"}, status=200
            )

        except Exception as e:
            print({"message": f"An error occurred: {str(e)}"})
            return Response({"message": f"An error occurred: {str(e)}"}, status=500)


def increment_academic_year(academic_year):
    current_year, current_suffix = academic_year.split("-")
    new_year = str(int(current_year) + 1)
    new_suffix = str(int(current_suffix) + 1)
    return f"{new_year}-{new_suffix.zfill(2)}"


def generate_receipt_pdf(request, studentId, paymentId):
    student = Student.objects.get(id=studentId)
    payment = FeePayment.objects.get(id=paymentId)

    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="recepit_of_payment_{student.fullname}_{payment.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Institution Name (Title)
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 60, "🏫 ABC Institution")

    # Address
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, height - 80, "123 Main Street, City, Country")
    p.line(50, height - 90, width - 50, height - 90)  # Divider line

    # Receipt Title
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, height - 120, "Payment Receipt")

    # Receipt Table Data
    receipt_data = [
        ["Student Name:", student.fullname],
        ["Receipt No:", f"#{payment.id}"],
        ["Reg No:", student.registrationNo],
        ["Class:", student.class_enrolled.class_name],
        ["Date of Payment:", str(payment.payment_date)],
        ["Total Fees:", f"${student.class_enrolled.total_fees}"],
        ["Paid Fees:", f"${payment.amount}"],
    ]

    # Create the table with appropriate column widths
    table = Table(receipt_data, colWidths=[200, 300])

    # Styling the table
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("LEFTPADDING", (0, 0), (-1, -1), 15),
                ("RIGHTPADDING", (0, 0), (-1, -1), 15),
            ]
        )
    )

    # Positioning the table nicely on the page
    table.wrapOn(p, width, height)
    table.drawOn(p, 70, height - 300)

    # Footer message
    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(width / 2, height - 350, "Thank you for your payment!")

    # Signature section
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 400, "Authorized Signature:")
    p.line(180, height - 402, 350, height - 402)

    # Generate PDF
    p.showPage()
    p.save()

    return response


class classView(APIView):
    def get(self, request):
        classInfo = Class.objects.all()
        serialize = ClassViewSerializer(classInfo, many=True)
        return Response(serialize.data)

    def post(self, request):
        data = request.data
        serialize = ClassViewSerializer(data=data)

        if serialize.is_valid(raise_exception=True):
            class_record = serialize.save()
            return JsonResponse(serialize.data, status=status.HTTP_201_CREATED)
        return JsonResponse(
            {"error": "Failed to insert", "details": serialize.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk=None):
        try:
            class_instance = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return Response(
                {"error": "Class not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serialize = ClassViewSerializer(class_instance, data=request.data, partial=True)
        if serialize.is_valid(raise_exception=True):
            serialize.save()
            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "Update failed", "details": serialize.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


def run_cron_job(request):
    return JsonResponse({"message": "Cron job triggered successfully"})
