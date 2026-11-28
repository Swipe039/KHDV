from django.db import models


class Student(models.Model):
    student_code = models.CharField(max_length=30, primary_key=True)
    full_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = "student"

    def __str__(self):
        return f"{self.student_code} - {self.full_name}"


class Session(models.Model):
    id = models.AutoField(primary_key=True)
    weekday = models.IntegerField()
    order_in_day = models.IntegerField()
    start_time = models.TextField()
    end_time = models.TextField()

    class Meta:
        managed = False
        db_table = "session"


class TimetableEntry(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.DO_NOTHING,
        db_column="student_code",
        related_name="timetable_entries",
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.DO_NOTHING,
        related_name="timetable_entries",
    )

    class Meta:
        managed = False
        db_table = "timetable_entry"


class SessionBlock(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.DO_NOTHING,
        db_column="student_code",
        related_name="session_blocks",
    )
    start_session = models.ForeignKey(
        Session,
        on_delete=models.DO_NOTHING,
        related_name="blocks_starting",
    )
    end_session = models.ForeignKey(
        Session,
        on_delete=models.DO_NOTHING,
        related_name="blocks_ending",
    )
    length = models.IntegerField()

    class Meta:
        managed = False
        db_table = "session_block"


class ParkingRequest(models.Model):
    id = models.AutoField(primary_key=True)
    session_block = models.OneToOneField(
        SessionBlock,
        on_delete=models.DO_NOTHING,
        related_name="parking_request",
    )
    wants_motorbike = models.BooleanField(default=False)
    permit_status = models.TextField(default="pending")
    reason = models.TextField(blank=True, default="")
    submitted_at = models.TextField()

    class Meta:
        managed = False
        db_table = "parking_request"


class Config(models.Model):
    id = models.IntegerField(primary_key=True)
    capacity = models.IntegerField()
    registration_deadline = models.TextField()
    random_seed = models.IntegerField(default=42)

    class Meta:
        managed = False
        db_table = "config"
