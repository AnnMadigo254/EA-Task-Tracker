"""
EA Task Tracker - DRF Serializers
Features: Nested data, validation, report serialization, quarter filtering
"""
from rest_framework import serializers
from .models import (
    User, Board, Column, Task, TaskHistory, Comment, 
    Attachment, Report, Notification, SearchQuery
)


class UserSerializer(serializers.ModelSerializer):
    """User serializer with role information"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'full_name', 'employee_id', 'department', 'role']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class TaskHistorySerializer(serializers.ModelSerializer):
    """Task history for audit trail"""
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = TaskHistory
        fields = '__all__'
        read_only_fields = ['id', 'changed_at']


class CommentSerializer(serializers.ModelSerializer):
    """Comment with user info"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'task', 'user', 'user_name', 'user_full_name', 
                  'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttachmentSerializer(serializers.ModelSerializer):
    """File attachment serializer"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = ['id', 'task', 'uploaded_by', 'uploaded_by_name', 
                  'file', 'file_url', 'filename', 'file_size', 'file_type', 'created_at']
        read_only_fields = ['id', 'created_at', 'file_size', 'file_type']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class TaskSerializer(serializers.ModelSerializer):
    """Main task serializer with nested data"""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    comments_count = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    history_count = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_in_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'column', 'title', 'description', 'task_type',
            'quarter',  # Add quarter field
            'project_name', 'task_name', 'design_status', 'dev_status', 'sit_status',
            'progress_notes', 'priority', 'status', 'owner', 'owner_name',
            'assigned_to', 'assigned_to_name', 'stakeholder', 'bapm',
            'start_date', 'due_date', 'completed_date', 'position',
            'dependencies', 'comments', 'created_at', 'updated_at',
            'comments_count', 'attachments_count', 'history_count',
            'is_overdue', 'days_in_progress'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_date']
    
    def get_comments_count(self, obj):
        return obj.task_comments.count()
    
    def get_attachments_count(self, obj):
        return obj.attachments.count()
    
    def get_history_count(self, obj):
        return obj.history.count()
    
    def get_is_overdue(self, obj):
        if obj.due_date and obj.status != 'Done':
            from django.utils import timezone
            return obj.due_date < timezone.now().date()
        return False
    
    def get_days_in_progress(self, obj):
        from django.utils import timezone
        if obj.status == 'In Progress':
            delta = timezone.now() - obj.created_at
            return delta.days
        return 0


class TaskDetailSerializer(TaskSerializer):
    """Detailed task with all nested data"""
    comments = CommentSerializer(source='task_comments', many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    history = TaskHistorySerializer(many=True, read_only=True)
    
    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['comments', 'attachments', 'history']


class ColumnSerializer(serializers.ModelSerializer):
    """Column with task counts"""
    tasks = TaskSerializer(many=True, read_only=True)
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Column
        fields = ['id', 'board', 'name', 'color', 'position', 
                  'task_count', 'tasks', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()


class BoardSerializer(serializers.ModelSerializer):
    """Board with columns and statistics"""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    columns = ColumnSerializer(many=True, read_only=True)
    total_tasks = serializers.SerializerMethodField()
    tasks_by_status = serializers.SerializerMethodField()
    tasks_by_priority = serializers.SerializerMethodField()
    tasks_by_quarter = serializers.SerializerMethodField()  # Add quarter stats
    
    class Meta:
        model = Board
        fields = ['id', 'name', 'owner', 'owner_name', 'description', 
                  'columns', 'total_tasks', 'tasks_by_status', 'tasks_by_priority',
                  'tasks_by_quarter',  # Add quarter field
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_tasks(self, obj):
        return Task.objects.filter(column__board=obj).count()
    
    def get_tasks_by_status(self, obj):
        from django.db.models import Count
        tasks = Task.objects.filter(column__board=obj)
        return dict(tasks.values_list('status').annotate(count=Count('id')))
    
    def get_tasks_by_priority(self, obj):
        from django.db.models import Count
        tasks = Task.objects.filter(column__board=obj)
        return dict(tasks.values_list('priority').annotate(count=Count('id')))
    
    def get_tasks_by_quarter(self, obj):
        from django.db.models import Count
        tasks = Task.objects.filter(column__board=obj)
        return dict(tasks.values_list('quarter').annotate(count=Count('id')))


class ReportSerializer(serializers.ModelSerializer):
    """Report serializer"""
    generated_by_name = serializers.CharField(source='generated_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = ['id', 'name', 'report_type', 'filters', 'file', 'file_url',
                  'format', 'generated_by', 'generated_by_name', 'generated_at',
                  'row_count', 'file_size']
        read_only_fields = ['id', 'generated_at', 'row_count', 'file_size']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_size(self, obj):
        if obj.file:
            return obj.file.size
        return 0


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'task', 'task_title', 'notification_type',
                  'title', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class SearchQuerySerializer(serializers.ModelSerializer):
    """Search query tracking"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SearchQuery
        fields = ['id', 'user', 'user_name', 'query', 'filters', 
                  'results_count', 'created_at']
        read_only_fields = ['id', 'created_at']


# Report Generation Serializers
class TaskReportSerializer(serializers.ModelSerializer):
    """Simplified task serializer for reports"""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    column_name = serializers.CharField(source='column.name', read_only=True)
    board_name = serializers.CharField(source='column.board.name', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'board_name', 'column_name', 'title', 'project_name',
            'task_name', 'task_type', 'quarter',  # Add quarter
            'priority', 'status',
            'owner_name', 'assigned_to_name', 'stakeholder', 'bapm',
            'design_status', 'dev_status', 'sit_status',
            'start_date', 'due_date', 'completed_date',
            'progress_notes', 'dependencies', 'comments',
            'created_at', 'updated_at'
        ]


class TeamPerformanceSerializer(serializers.Serializer):
    """Team performance metrics for reports"""
    architect = serializers.CharField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    avg_completion_time = serializers.FloatField()
    completion_rate = serializers.FloatField()


class ProjectStatusSerializer(serializers.Serializer):
    """Project status for reports"""
    project_name = serializers.CharField()
    quarter = serializers.CharField()  # Add quarter
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    status = serializers.CharField()
    progress_percentage = serializers.FloatField()
    last_updated = serializers.DateTimeField()


# Bulk Operations Serializers
class TaskMoveSerializer(serializers.Serializer):
    """Move task to different column"""
    task_id = serializers.UUIDField()
    column_id = serializers.UUIDField()
    position = serializers.IntegerField(required=False)


class BulkTaskUpdateSerializer(serializers.Serializer):
    """Bulk update tasks"""
    task_ids = serializers.ListField(child=serializers.UUIDField())
    updates = serializers.DictField()


class TaskSearchSerializer(serializers.Serializer):
    """Search parameters"""
    query = serializers.CharField(required=False, allow_blank=True)
    status = serializers.MultipleChoiceField(
        choices=Task.STATUS_CHOICES, 
        required=False
    )
    priority = serializers.MultipleChoiceField(
        choices=Task.PRIORITY_CHOICES,
        required=False
    )
    task_type = serializers.MultipleChoiceField(
        choices=Task.TASK_TYPE_CHOICES,
        required=False
    )
    quarter = serializers.MultipleChoiceField(  # Add quarter filter
        choices=Task.QUARTER_CHOICES,
        required=False
    )
    owner = serializers.UUIDField(required=False)
    assigned_to = serializers.UUIDField(required=False)
    start_date_from = serializers.DateField(required=False)
    start_date_to = serializers.DateField(required=False)
    due_date_from = serializers.DateField(required=False)
    due_date_to = serializers.DateField(required=False)
    project_name = serializers.CharField(required=False, allow_blank=True)


class QuarterSummarySerializer(serializers.Serializer):
    """Quarter summary statistics"""
    quarter = serializers.CharField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    todo_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    high_priority_count = serializers.IntegerField()
    overdue_count = serializers.IntegerField()