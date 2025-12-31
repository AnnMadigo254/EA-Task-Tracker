from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import (
    User, Board, Column, Task, TaskHistory, Comment,
    Attachment, Report, Notification, SearchQuery
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced user admin"""
    list_display = ['username', 'email', 'full_name_display', 'employee_id', 'department', 'role', 'is_active']
    list_filter = ['role', 'department', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('EA Information', {
            'fields': ('employee_id', 'department', 'role')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('EA Information', {
            'fields': ('employee_id', 'department', 'role')
        }),
    )
    
    def full_name_display(self, obj):
        return obj.get_full_name() or '-'
    full_name_display.short_description = 'Full Name'


class ColumnInline(admin.TabularInline):
    model = Column
    extra = 0
    fields = ['name', 'color', 'position', 'task_count']
    readonly_fields = ['task_count']
    ordering = ['position']
    
    def task_count(self, obj):
        if obj.pk:
            return obj.tasks.count()
        return 0
    task_count.short_description = 'Tasks'


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner_link', 'task_count', 'created_at', 'updated_at']
    list_filter = ['owner', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at', 'task_count']
    inlines = [ColumnInline]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'owner', 'description']
        }),
        ('Statistics', {
            'fields': ['task_count', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def owner_link(self, obj):
        url = reverse('admin:tasks_user_change', args=[obj.owner.id])  # ✅ fixed
        return format_html('<a href="{}">{}</a>', url, obj.owner.username)
    owner_link.short_description = 'Owner'
    
    def task_count(self, obj):
        return Task.objects.filter(column__board=obj).count()
    task_count.short_description = 'Total Tasks'


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'color_display', 'position', 'task_count']
    list_filter = ['board']
    search_fields = ['name', 'board__name']
    ordering = ['board', 'position']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'
    
    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'


class TaskHistoryInline(admin.TabularInline):
    model = TaskHistory
    extra = 0
    readonly_fields = ['field_name', 'old_value', 'new_value', 'changed_by', 'changed_at', 'change_type']
    can_delete = False
    ordering = ['-changed_at']
    max_num = 10


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['user', 'created_at']
    fields = ['user', 'content', 'created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status_badge', 'priority_badge', 'owner_link', 
        'assigned_to_link', 'due_date_display', 'progress_display'
    ]
    list_filter = [
        'status', 'priority', 'task_type', 'column__board', 
        'owner', 'created_at', 'due_date'
    ]
    search_fields = [
        'title', 'description', 'project_name', 'task_name', 
        'stakeholder', 'bapm'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'completed_date', 
        'comments_count', 'attachments_count', 'history_count'
    ]
    date_hierarchy = 'created_at'
    inlines = [CommentInline, TaskHistoryInline]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['column', 'title', 'description', 'task_type']
        }),
        ('EA Project Details', {
            'fields': [
                'project_name', 'task_name', 
                ('design_status', 'dev_status', 'sit_status'),
                'progress_notes'
            ]
        }),
        ('Assignment & Priority', {
            'fields': [
                ('priority', 'status'),
                ('owner', 'assigned_to'),
                ('stakeholder', 'bapm')
            ]
        }),
        ('Dates', {
            'fields': [
                ('start_date', 'due_date'),
                'completed_date'
            ]
        }),
        ('Additional Info', {
            'fields': ['dependencies', 'comments', 'position'],
            'classes': ['collapse']
        }),
        ('Statistics', {
            'fields': [
                'comments_count', 'attachments_count', 'history_count',
                'created_at', 'updated_at'
            ],
            'classes': ['collapse']
        }),
    ]
    
    actions = [
        'mark_in_progress', 'mark_done', 'mark_high_priority',
        'export_as_csv', 'send_reminder'
    ]
    
    def status_badge(self, obj):
        colors = {
            'To Do': '#49C4E5',
            'In Progress': '#00A86B',
            'Done': '#00C853',
            'On Hold': '#E5534B',
        }
        color = colors.get(obj.status, '#828FA3')
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; color: white; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        colors = {
            'Critical': '#E5534B',
            'High': '#FF9898',
            'Medium': '#FFA500',
            'Low': '#828FA3',
        }
        color = colors.get(obj.priority, '#828FA3')
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; color: white; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.priority
        )
    priority_badge.short_description = 'Priority'
    
    def owner_link(self, obj):
        if obj.owner:
            url = reverse('admin:tasks_user_change', args=[obj.owner.id])  # ✅
            return format_html('<a href="{}">{}</a>', url, obj.owner.username)
        return '-'
    owner_link.short_description = 'Owner'
    
    def assigned_to_link(self, obj):
        if obj.assigned_to:
            url = reverse('admin:tasks_user_change', args=[obj.assigned_to.id])  # ✅
            return format_html('<a href="{}">{}</a>', url, obj.assigned_to.username)
        return '-'
    assigned_to_link.short_description = 'Assigned To'
    
    def due_date_display(self, obj):
        if obj.due_date:
            from django.utils import timezone
            if obj.due_date < timezone.now().date() and obj.status != 'Done':
                return format_html(
                    '<span style="color: red; font-weight: bold;">{}</span>',
                    obj.due_date
                )
            return obj.due_date
        return '-'
    due_date_display.short_description = 'Due Date'
    
    def progress_display(self, obj):
        statuses = [obj.design_status, obj.dev_status, obj.sit_status]
        completed = sum(1 for s in statuses if 'complete' in str(s).lower())
        total = len([s for s in statuses if s])
        
        if total > 0:
            percentage = (completed / total) * 100
            color = '#00C853' if percentage == 100 else '#00A86B' if percentage > 50 else '#FFA500'
            return format_html(
                '<div style="width: 100px; background: #E4EBFA; border-radius: 5px;">'
                '<div style="width: {}%; background: {}; height: 20px; border-radius: 5px; text-align: center; color: white; font-size: 10px; line-height: 20px;">'
                '{}%</div></div>',
                percentage, color, int(percentage)
            )
        return '-'
    progress_display.short_description = 'Progress'
    
    def comments_count(self, obj):
        return obj.task_comments.count()
    comments_count.short_description = 'Comments'
    
    def attachments_count(self, obj):
        return obj.attachments.count()
    attachments_count.short_description = 'Attachments'
    
    def history_count(self, obj):
        return obj.history.count()
    history_count.short_description = 'History'
    
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='In Progress')
        self.message_user(request, f'{updated} tasks marked as In Progress')
    mark_in_progress.short_description = 'Mark selected tasks as In Progress'
    
    def mark_done(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='Done', completed_date=timezone.now())
        self.message_user(request, f'{updated} tasks marked as Done')
    mark_done.short_description = 'Mark selected tasks as Done'
    
    def mark_high_priority(self, request, queryset):
        updated = queryset.update(priority='High')
        self.message_user(request, f'{updated} tasks marked as High priority')
    mark_high_priority.short_description = 'Mark as High priority'
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Title', 'Status', 'Priority', 'Owner', 'Due Date', 'Created'])
        
        for task in queryset:
            writer.writerow([
                task.title,
                task.status,
                task.priority,
                task.owner.username if task.owner else '',
                task.due_date,
                task.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    export_as_csv.short_description = 'Export selected as CSV'
    
    def send_reminder(self, request, queryset):
        count = 0
        for task in queryset:
            if task.assigned_to:
                Notification.objects.create(
                    user=task.assigned_to,
                    task=task,
                    notification_type='task_due',
                    title='Task Reminder',
                    message=f'Reminder: {task.title} is due on {task.due_date}'
                )
                count += 1
        self.message_user(request, f'Sent {count} reminders')
    send_reminder.short_description = 'Send reminder to assigned users'


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ['task_link', 'field_name', 'changed_by_link', 'change_type', 'changed_at']
    list_filter = ['change_type', 'changed_at', 'changed_by']
    search_fields = ['task__title', 'field_name', 'changed_by__username']
    readonly_fields = ['task', 'field_name', 'old_value', 'new_value', 'changed_by', 'changed_at', 'change_type']
    date_hierarchy = 'changed_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def task_link(self, obj):
        url = reverse('admin:tasks_task_change', args=[obj.task.id])  # ✅
        return format_html('<a href="{}">{}</a>', url, obj.task.title[:50])
    task_link.short_description = 'Task'
    
    def changed_by_link(self, obj):
        if obj.changed_by:
            url = reverse('admin:tasks_user_change', args=[obj.changed_by.id])  # ✅
            return format_html('<a href="{}">{}</a>', url, obj.changed_by.username)
        return '-'
    changed_by_link.short_description = 'Changed By'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['task_link', 'user_link', 'content_preview', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['content', 'task__title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def task_link(self, obj):
        url = reverse('admin:tasks_task_change', args=[obj.task.id])  # ✅
        return format_html('<a href="{}">{}</a>', url, obj.task.title[:50])
    task_link.short_description = 'Task'
    
    def user_link(self, obj):
        url = reverse('admin:tasks_user_change', args=[obj.user.id])  # ✅
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'task_link', 'uploaded_by_link', 'file_size_display', 'created_at']
    list_filter = ['file_type', 'created_at', 'uploaded_by']
    search_fields = ['filename', 'task__title']
    readonly_fields = ['created_at', 'file_size', 'file_type']
    
    def task_link(self, obj):
        url = reverse('admin:tasks_task_change', args=[obj.task.id])  # ✅
        return format_html('<a href="{}">{}</a>', url, obj.task.title[:50])
    task_link.short_description = 'Task'
    
    def uploaded_by_link(self, obj):
        url = reverse('admin:tasks_user_change', args=[obj.uploaded_by.id])  # ✅
        return format_html('<a href="{}">{}</a>', url, obj.uploaded_by.username)
    uploaded_by_link.short_description = 'Uploaded By'
    
    def file_size_display(self, obj):
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    file_size_display.short_description = 'File Size'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'format', 'generated_by_link', 'row_count', 'generated_at']
    list_filter = ['report_type', 'format', 'generated_at']
    search_fields = ['name']
    readonly_fields = ['generated_at', 'row_count']

    def generated_by_link(self, obj):
        url = reverse('admin:tasks_user_change', args=[obj.generated_by.id])  # ✅ already correct
        return format_html('<a href="{}">{}</a>', url, obj.generated_by.username)
    generated_by_link.short_description = 'Generated By'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user_link', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at']
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def user_link(self, obj):
        url = reverse('admin:tasks_user_change', args=[obj.user.id])  # ✅
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read')
    mark_as_read.short_description = 'Mark selected as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notifications marked as unread')
    mark_as_unread.short_description = 'Mark selected as unread'


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user_link', 'results_count', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['query']
    readonly_fields = ['created_at']
    
    def user_link(self, obj):
        url = reverse('admin:tasks_user_change', args=[obj.user.id])  # ✅
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'


    