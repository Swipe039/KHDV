



from django.shortcuts import render
from .models import Student

def student_list(request):
    students = Student.objects.using("parking_data").all()[:100]
    return render(request, "parking/students.html", {
        "students": students,
    })