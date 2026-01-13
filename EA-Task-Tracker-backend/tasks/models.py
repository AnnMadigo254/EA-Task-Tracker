from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Extended user model for EA architects"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, default='Enterprise Architecture')
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'),
        ('architect', 'Architect'),
        ('manager', 'Manager'),
        ('viewer', 'Viewer'),
    ], default='architect')
    
    class Meta:
        db_table = 'users'
        ordering = ['username']
        
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class Board(models.Model):
    """Board for each architect"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'boards'
        ordering = ['name']
        indexes = [
            models.Index(fields=['owner', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.owner.username}"


class Column(models.Model):
    """Workflow columns: To Do, In Progress, Done"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#00A86B')  # Hex color
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'columns'
        ordering = ['board', 'position']
        unique_together = ['board', 'name']
    
    def __str__(self):
        return f"{self.board.name} - {self.name}"


class Task(models.Model):
    """EA Tasks with full tracking"""
    
    PRIORITY_CHOICES = [
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('On Hold', 'On Hold'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('Solution Design', 'Solution Design'),
        ('BRD Review', 'BRD Review'),
        ('Service Documentation', 'Service Documentation'),
        ('Architecture Review', 'Architecture Review'),
        ('Roadmap Design', 'Roadmap Design'),
        ('EA SME Support', 'EA SME Support'),
        ('Other', 'Other'),
    ]
    
    QUARTER_CHOICES = [
        ('Q3_2025', 'Q3 2025'),
        ('Q4_2025', 'Q4 2025'),
        ('Q1_2026', 'Q1 2026'),
        ('Q2_2026', 'Q2 2026'),
        ('Q3_2026', 'Q3 2026'),
        ('Q4_2026', 'Q4 2026'),
        ('Q1_2027', 'Q1 2027'),
        ('Q2_2027', 'Q2 2027'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='tasks')
    
    # Basic info
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=100, choices=TASK_TYPE_CHOICES, default='Solution Design')
    
    # Quarter tracking
    quarter = models.CharField(max_length=10, choices=QUARTER_CHOICES, default='Q1_2026', db_index=True)
    
    # EA specific fields
    project_name = models.CharField(max_length=300, blank=True)
    task_name = models.CharField(max_length=300, blank=True)
    design_status = models.CharField(max_length=100, blank=True)
    dev_status = models.CharField(max_length=100, blank=True)
    sit_status = models.CharField(max_length=100, blank=True)
    progress_notes = models.TextField(blank=True)
    
    # Assignment & tracking
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='To Do')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    stakeholder = models.CharField(max_length=200, blank=True)
    bapm = models.CharField(max_length=200, blank=True)  # BA/PM
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    position = models.IntegerField(default=0)
    dependencies = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Search
    search_vector = models.TextField(blank=True)  # For full-text search
    
    class Meta:
        db_table = 'tasks'
        ordering = ['column', 'position']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['created_at']),
            models.Index(fields=['project_name']),
            models.Index(fields=['quarter']),
        ]
    
    def save(self, *args, **kwargs):
        # Update search vector
        self.search_vector = f"{self.title} {self.description} {self.project_name} {self.task_name} {self.stakeholder}".lower()
        
        # Set completed date if status changed to Done
        if self.status == 'Done' and not self.completed_date:
            self.completed_date = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.status}"


class TaskHistory(models.Model):
    """Historical tracking of all task changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
    
    # Changed fields
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    
    # Who & When
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    # Context
    change_type = models.CharField(max_length=50, choices=[
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('moved', 'Moved'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('reopened', 'Reopened'),
    ])
    
    class Meta:
        db_table = 'task_history'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['task', '-changed_at']),
            models.Index(fields=['changed_by', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.task.title} - {self.field_name} changed by {self.changed_by}"


class Comment(models.Model):
    """Comments on tasks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"


class Attachment(models.Model):
    """File attachments for tasks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()  # bytes
    file_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attachments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} - {self.task.title}"


class Report(models.Model):
    """Generated reports"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=[
        ('task_summary', 'Task Summary'),
        ('team_performance', 'Team Performance'),
        ('project_status', 'Project Status'),
        ('historical_trend', 'Historical Trend'),
        ('custom', 'Custom Report'),
    ])
    
    # Filters used
    filters = models.JSONField(default=dict)
    
    # Generated file
    file = models.FileField(upload_to='reports/%Y/%m/', null=True, blank=True)
    format = models.CharField(max_length=10, choices=[
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('pdf', 'PDF'),
    ])
    
    # Metadata
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} - {self.format} ({self.generated_at.strftime('%Y-%m-%d')})"


class SearchQuery(models.Model):
    """Track search queries for analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict)
    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]


class Notification(models.Model):
    """User notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    
    notification_type = models.CharField(max_length=50, choices=[
        ('task_assigned', 'Task Assigned'),
        ('task_updated', 'Task Updated'),
        ('task_comment', 'New Comment'),
        ('task_due', 'Task Due Soon'),
        ('mention', 'Mentioned'),
    ])
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"