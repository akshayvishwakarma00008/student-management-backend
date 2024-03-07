from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import StudentSerializer,FeePaymentSerializer,StudentEnrollmentHistorySerializer
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Student,FeePayment

# Create your views here.

class StudentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        print("data",data)
        serialize = StudentSerializer(data=data)

        if serialize.is_valid(raise_exception=True):
            serialize.save()
            return JsonResponse("student created", safe=False)
        return JsonResponse("failed to insert", safe=False)
    
    def get(self, request,pk=None):
        if pk:
            student = get_object_or_404(Student,id=pk)
            serializer = StudentSerializer(student)
            # Include related FeePayment data
            data = serializer.data

            fee_payments = FeePayment.objects.filter(student_id=pk)
            fee_serializer = FeePaymentSerializer(fee_payments, many=True)
            data['fee_payments'] = fee_serializer.data
            return Response(data)
        try:
            student = Student.objects.all().order_by('id')
            serializer = StudentSerializer(student,many=True)
            
            return Response(serializer.data)
        except Exception as e:
            print(e )

    def put(self, request, pk=None):
        data = request.data
        student_to_update = Student.objects.get(id=pk)
        serialize = StudentSerializer(instance=student_to_update, data=data, partial=True)
        if serialize.is_valid():
            serialize.save()
            return Response({"message":"Record Updated", "data":serialize.data})
        else:
            return Response(serialize.errors, status=400)  # Bad request
        
    def delete(self, request, pk=None):
        student_to_delete = Student.objects.get(id=pk)
        if student_to_delete:
            student_to_delete.delete()
            return Response({"message":"Deleted Successfully!"},status=200)
        else:
            return Response({"message":"Student Doesnt Exist", "data":'null'},status=404)
        
class FeePaymentView(APIView):
    def get(self, request, studentId=None):
        print("StudentId",studentId)
        if studentId:
            feeDetails = FeePayment.objects.filter(student = studentId)
            print("FeeDetails",feeDetails)
            serialize = FeePaymentSerializer(feeDetails,many=True)
            return Response(serialize.data)
        else:
            fees = FeePayment.objects.all().order_by("-payment_date")
            serialize = FeePaymentSerializer(fees,many=True)
            return Response(serialize.data)
            

    def post(self, request):
        data = request.data
        print("data",data)
        serialize = FeePaymentSerializer(data=data)

        if serialize.is_valid(raise_exception=True):
            serialize.save()
            return JsonResponse("Fee Record Captured", safe=False)
        return JsonResponse("failed to insert", safe=False)
    

class UpdateAcadamicYearView(APIView):
    def post(self,request):
        try:
            with transaction.atomic():
                students = Student.objects.all()
                for student in students:
                    enrollment_data = {
                    'student': student.id,
                    'class_enrolled': student.class_enrolled_id,
                    'academic_year': student.academic_year,
                    'total_fees_paid': student.total_fees_paid,
                    'pen_fees': student.pen_fees,
                    }
                    enrollment_serializer = StudentEnrollmentHistorySerializer(data=enrollment_data)
                    if enrollment_serializer.is_valid() and student.is_active == True:
                        enrollment_serializer.save()
                        if student.class_enrolled_id == 12:
                            student.is_active = False
                        else:
                            student.class_enrolled_id += 1
                            student.total_fees_paid = 0
                            student.pen_fees = 0 
                            student.academic_year = increment_academic_year(student.academic_year)


                        student.save()
            return Response({"message":"Sucessfully updated academic year and class"},status=200)
            
        except Exception as e:
            print({"message":f"An error occurred: {str(e)}"})
            return Response({"message": f"An error occurred: {str(e)}"}, status=500)
        
def increment_academic_year(academic_year):
    current_year, current_suffix = academic_year.split('-')
    new_year = str(int(current_year) + 1)
    new_suffix = str(int(current_suffix) + 1)
    return f"{new_year}-{new_suffix.zfill(2)}"