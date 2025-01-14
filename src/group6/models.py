from django.db import models
from datetime import date, timedelta

# Create your models here.

class Words(models.Model):
    word = models.CharField(max_length=100, verbose_name="Words")
    description = models.TextField()
    user_id = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.word


class LeitnerBox(models.Model):
    BOX_CHOICES = [
        (1, "Box 1"),
        (2, "Box 2"),
        (3, "Box 3"),
        (4, "Box 4"),
        (5, "Box 5"),
    ]

    word = models.OneToOneField(Words, on_delete=models.CASCADE, related_name="leitner")
    user_id = models.IntegerField()
    box_number = models.PositiveSmallIntegerField(choices=BOX_CHOICES, default=1)
    next_review_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.word.word} - Box {self.box_number}"

    def move_to_next_box(self):
        if self.box_number < 5:
            self.box_number += 1
        else:
            self.box_number = 5  # Already in the last box.

    def move_to_previous_box(self):
        if self.box_number > 1:
            self.box_number -= 1
        else:
            self.box_number = 1

class Tick8(models.Model):
    STAGE_CHOICES = [
        (1, "Stage 1"),
        (2, "Stage 2"),
        (3, "Stage 3"),
        (4, "Stage 4"),
        (5, "Stage 5"),
        (6, "Stage 6"),
        (7, "Stage 7"),
        (8, "Stage 8"),
    ]

    word = models.OneToOneField('Words', on_delete=models.CASCADE, related_name="tick8")
    user_id = models.IntegerField()
    current_stage = models.PositiveSmallIntegerField(choices=STAGE_CHOICES, default=1)
    next_review_date = models.DateField(blank=True, null=True)

    INTERVALS = [1, 2, 4, 7, 15, 30, 60, 120]  # روزهای فاصله بین هر مرحله

    def save(self, *args, **kwargs):
        # اگر next_review_date تنظیم نشده، مقدار اولیه بده
        if not self.next_review_date:
            self.next_review_date = date.today() + timedelta(days=self.INTERVALS[self.current_stage - 1])
        super().save(*args, **kwargs)

    def advance_stage(self):
        """به مرحله بعد بروید و تاریخ مرور را به‌روزرسانی کنید."""
        if self.current_stage < 8:
            self.current_stage += 1
            self.next_review_date = date.today() + timedelta(days=self.INTERVALS[self.current_stage - 1])
            self.save()

    def reset_stage(self):
        """بازگشت به مرحله اول."""
        self.current_stage = 1
        self.next_review_date = date.today() + timedelta(days=self.INTERVALS[0])
        self.save()

    def __str__(self):
        return f"{self.word.word} - Stage {self.current_stage}"

