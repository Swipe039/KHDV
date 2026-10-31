"""Đặt trong <django_app>/models.py; Django quản lý tài khoản bằng auth.User.

Giữ CSDL đồng bộ: với dự án Django thực tế, tạo các bảng bằng migrations
(`python manage.py makemigrations` và `python manage.py migrate`).
File schema.sql đi kèm dành cho thử nghiệm SQLite độc lập.
"""
from django.db import models
from django.db.models import Q


class Student(models.Model):
    student_code = models.CharField(max_length=30, primary_key=True)
    full_name = models.CharField(max_length=150)

    class Meta:
        db_table = 'student'

    def __str__(self):
        return f'{self.student_code} - {self.full_name}'


class Session(models.Model):
    weekday = models.PositiveSmallIntegerField()  # 1=Thứ Hai, ..., 7=Chủ Nhật
    order_in_day = models.PositiveSmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'session'
        constraints = [
            models.UniqueConstraint(fields=['weekday', 'order_in_day'], name='unique_weekday_order'),
            models.CheckConstraint(condition=Q(weekday__gte=1, weekday__lte=7), name='valid_weekday'),
            models.CheckConstraint(condition=Q(order_in_day__gte=1), name='positive_order'),
            models.CheckConstraint(condition=Q(start_time__lt=models.F('end_time')), name='session_time_order'),
        ]


class TimetableEntry(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_code')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    class Meta:
        db_table = 'timetable_entry'
        constraints = [models.UniqueConstraint(fields=['student', 'session'], name='unique_student_session')]


class SessionBlock(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_code')
    start_session = models.ForeignKey(Session, on_delete=models.PROTECT, related_name='blocks_starting')
    end_session = models.ForeignKey(Session, on_delete=models.PROTECT, related_name='blocks_ending')
    length = models.PositiveIntegerField()

    class Meta:
        db_table = 'session_block'
        constraints = [
            models.UniqueConstraint(fields=['student', 'start_session', 'end_session'], name='unique_student_block'),
            models.CheckConstraint(condition=Q(length__gte=1), name='positive_block_length'),
        ]


class ParkingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Chưa xếp'
        GRANTED = 'granted', 'Được phép'
        DENIED = 'denied', 'Không được phép'

    session_block = models.OneToOneField(SessionBlock, on_delete=models.CASCADE)
    wants_motorbike = models.BooleanField(default=False)
    permit_status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField(blank=True, default='')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parking_request'
        constraints = [
            models.CheckConstraint(condition=Q(wants_motorbike=True) | ~Q(permit_status='granted'), name='grant_requires_request'),
        ]


class Config(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    capacity = models.PositiveIntegerField()
    registration_deadline = models.DateTimeField()
    random_seed = models.IntegerField(default=42)

    class Meta:
        db_table = 'config'
        constraints = [
            models.CheckConstraint(condition=Q(id=1), name='singleton_config'),
        ]
