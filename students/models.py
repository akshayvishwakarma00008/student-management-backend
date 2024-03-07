from django.db import models
from datetime import datetime
import uuid


class Class(models.Model):
    class_name = models.CharField(max_length=50)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.class_name

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE)
    age = models.IntegerField()
    registrationNo = models.CharField(max_length=100, unique=True, editable=False)
    email = models.CharField(max_length=100)
    course = models.CharField(max_length=50)
    phoneNumber = models.IntegerField()
    address = models.TextField()
    total_fees_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pen_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    enrollment_date = models.DateField(default=datetime.now)
    academic_year = models.CharField(max_length=9, default="2023-24")
    is_active = models.BooleanField(default=True,editable=True)

    def fees_paid(self):
        return self.total_fees_paid

    def pending_fees(self):
        return self.pen_fees

    def __str__(self):
        return self.fullname
    
    def save(self, *args, **kwargs):
        if not self.registrationNo:
            # Generate a unique registration number using a combination of prefix and UUID
            prefix = 'REG'
            user_prefix = self.fullname[:4].upper()
            unique_id = int(uuid.uuid4().int) % 100000
            self.registrationNo = f'{prefix}-{user_prefix}-{unique_id}'

        if not self.academic_year:
            current_date = datetime.now()
            if current_date.month >=3:
                self.academic_year = f'{current_date.year}-{str(current_date.year+1)[2:]}'
            else:
                self.academic_year = f'{current_date.year - 1}-{str(current_date.year)[2:]}'
        super().save(*args, **kwargs)
    


class FeePayment(models.Model):
    PAYMENT_TYPES =[
        ('monthly','monthly'),
        ('3months','3 months'),
        ('6months','6 months'),
        ('yearly', 'yearly'),
    ]

    student =  models.ForeignKey(Student,on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.student.total_fees_paid += self.amount
        self.student.pen_fees = self.student.class_enrolled.total_fees - self.student.total_fees_paid
        self.student.save()

class StudentEnrollmentHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9)
    total_fees_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pen_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.student.fullname} - {self.class_enrolled.class_name} - {self.student.enrollment_date}"