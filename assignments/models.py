from django.db import models
import uuid
# Create your models here.
class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    class_room = models.ForeignKey(
        'academics.ClassRoom',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    grading_criteria = models.ForeignKey(
        'grades.GradingCriteria',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assignments"

    def __str__(self):        
        return f"{self.title} - {self.class_room} - {self.subject}"
    

