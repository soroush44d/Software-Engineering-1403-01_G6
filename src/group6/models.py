from django.db import models
from datetime import date, timedelta

# Create your models here.

class Words(models.Model):
    word = models.CharField(max_length=100, verbose_name="Words")
    description = models.TextField()
    user_id = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True)
    know = models.BooleanField(default=False, blank=True, null=True, verbose_name="Know")


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
            print("+1 box")
        else:
            self.box_number = 5  # Already in the last box.

    def move_to_previous_box(self):
        if self.box_number > 1:
            print('-1 box number')
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

    word = models.ForeignKey('Words', on_delete=models.CASCADE, related_name="tick8")
    user_id = models.IntegerField()
    current_stage = models.PositiveSmallIntegerField(choices=STAGE_CHOICES, default=1)
    next_review_date = models.DateField(blank=True, null=True)
    remmembered = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def is_clickable(self):
        """Check if the word is clickable based on the current date and stage."""
        days_elapsed = (date.today() - self.created_at).days
        return days_elapsed >= (self.current_stage - 1)

    def __str__(self):
        return f"{self.word.word} - Stage {self.current_stage}"

