from django.contrib import admin
from django.urls import path

from .views import StudentView,FeePaymentView,UpdateAcadamicYearView

urlpatterns = [
    path("students/",StudentView.as_view()),
    path("students/<int:pk>/",StudentView.as_view()),
    path("fee-payment/",FeePaymentView.as_view()),
    path("fee-payment/<int:studentId>/",FeePaymentView.as_view()),
    path("update-academic-year/",UpdateAcadamicYearView.as_view()),
]

