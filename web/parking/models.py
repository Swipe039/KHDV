from django.db import models


from django.db import models


class Student(models.Model):
    student_code = models.CharField(max_length=30, primary_key=True)
    full_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = "student"

    def __str__(self):
        return f"{self.student_code} - {self.full_name}"