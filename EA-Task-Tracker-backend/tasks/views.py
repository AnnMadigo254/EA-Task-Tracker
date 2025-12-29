from django.shortcuts import render

# Create your views here.


"""
EA Task Tracker - DRF Views
Features: Search, filtering, reports, historical tracking
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
import csv
import io

from .models import (
    User, Board, Column, Task, TaskHistory, Comment,
    Attachment, Report, Notification, SearchQuery
)
from .serializers import (
    UserSerializer, BoardSerializer, ColumnSerializer,
    TaskSerializer, TaskDetailSerializer, TaskHistorySerializer,
    CommentSerializer, AttachmentSerializer, ReportSerializer,
    NotificationSerializer, SearchQuerySerializer,
    TaskReportSerializer, TeamPerformanceSerializer,
    ProjectStatusSerializer, TaskMoveSerializer,
    BulkTaskUpdateSerializer, TaskSearchSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """User management"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    ordering_fields = ['username', 'department', 'role']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def architects(self, request):
        """Get all architects"""
        architects = User.objects.filter(role='architect')
        serializer = self.get_serializer(architects, many=True)
        return Response(serializer.data)


class BoardViewSet(viewsets.ModelViewSet):
    """Board management with statistics"""
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'owner__username']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def get_queryset(self):
        """Filter boards by user role"""
        user = self.request.user
        if user.role == 'admin':
            return Board.objects.all()
        return Board.objects.filter(owner=user)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export board data as JSON"""
        board = self.get_object()
        serializer = self.get_serializer(board)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get detailed board statistics"""
        board = self.get_object()
        tasks = Task.objects.filter(column__board=board)
        
        stats = {
            'total_tasks': tasks.count(),
            'by_status': dict(tasks.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'by_priority': dict(tasks.values('priority').annotate(count=Count('id')).values_list('priority', 'count')),
            'by_type': dict(tasks.values('task_type').annotate(count=Count('id')).values_list('task_type', 'count')),
            'overdue': tasks.filter(due_date__lt=timezone.now().date(), status__in=['To Do', 'In Progress']).count(),
            'completed_this_week': tasks.filter(completed_date__gte=timezone.now() - timedelta(days=7)).count(),
            'completed_this_month': tasks.filter(completed_date__gte=timezone.now() - timedelta(days=30)).count(),
        }
        
        return Response(stats)


class ColumnViewSet(viewsets.ModelViewSet):
    """Column management"""
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by board if specified"""
        queryset = Column.objects.all()
        board_id = self.request.query_params.get('board')
        if board_id:
            queryset = queryset.filter(board_id=board_id)
        return queryset


class TaskViewSet(viewsets.ModelViewSet):
    """Task management with advanced search and filtering"""
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'project_name', 'task_name', 'stakeholder']
    ordering_fields = ['priority', 'due_date', 'created_at', 'updated_at', 'position']
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve"""
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer
    
    def get_queryset(self):
        """Advanced filtering"""
        queryset = Task.objects.all().select_related('owner', 'assigned_to', 'column', 'column__board')
        
        # Filter by query params
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        owner = self.request.query_params.get('owner')
        if owner:
            queryset = queryset.filter(owner_id=owner)
        
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        board = self.request.query_params.get('board')
        if board:
            queryset = queryset.filter(column__board_id=board)
        
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(project_name__icontains=project)
        
        # Date filters
        due_from = self.request.query_params.get('due_from')
        if due_from:
            queryset = queryset.filter(due_date__gte=due_from)
        
        due_to = self.request.query_params.get('due_to')
        if due_to:
            queryset = queryset.filter(due_date__lte=due_to)
        
        # Overdue tasks
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now().date(),
                status__in=['To Do', 'In Progress']
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Create task and log history"""
        task = serializer.save()
        TaskHistory.objects.create(
            task=task,
            field_name='created',
            new_value=task.title,
            changed_by=self.request.user,
            change_type='created'
        )
    
    def perform_update(self, serializer):
        """Update task and log history"""
        old_task = self.get_object()
        task = serializer.save()
        
        # Log changed fields
        for field in ['title', 'status', 'priority', 'assigned_to', 'due_date']:
            old_value = getattr(old_task, field)
            new_value = getattr(task, field)
            if old_value != new_value:
                TaskHistory.objects.create(
                    task=task,
                    field_name=field,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    changed_by=self.request.user,
                    change_type='updated'
                )
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Move task to different column"""
        task = self.get_object()
        serializer = TaskMoveSerializer(data=request.data)
        
        if serializer.is_valid():
            column_id = serializer.validated_data['column_id']
            position = serializer.validated_data.get('position', 0)
            
            old_column = task.column
            task.column_id = column_id
            task.position = position
            task.save()
            
            # Log move
            TaskHistory.objects.create(
                task=task,
                field_name='column',
                old_value=old_column.name,
                new_value=task.column.name,
                changed_by=request.user,
                change_type='moved'
            )
            
            return Response({'status': 'moved'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as complete"""
        task = self.get_object()
        task.status = 'Done'
        task.completed_date = timezone.now()
        task.save()
        
        TaskHistory.objects.create(
            task=task,
            field_name='status',
            old_value=task.status,
            new_value='Done',
            changed_by=request.user,
            change_type='completed'
        )
        
        return Response({'status': 'completed'})
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update tasks"""
        serializer = BulkTaskUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            task_ids = serializer.validated_data['task_ids']
            updates = serializer.validated_data['updates']
            
            tasks = Task.objects.filter(id__in=task_ids)
            count = tasks.update(**updates)
            
            return Response({'updated': count})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks for current user"""
        tasks = Task.objects.filter(
            Q(owner=request.user) | Q(assigned_to=request.user)
        ).select_related('column', 'owner', 'assigned_to')
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def due_soon(self, request):
        """Get tasks due in next 7 days"""
        due_date = timezone.now().date() + timedelta(days=7)
        tasks = Task.objects.filter(
            due_date__lte=due_date,
            status__in=['To Do', 'In Progress']
        ).select_related('column', 'owner')
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search with multiple filters"""
        serializer = TaskSearchSerializer(data=request.data)
        
        if serializer.is_valid():
            queryset = Task.objects.all()
            
            # Text search
            query = serializer.validated_data.get('query')
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(project_name__icontains=query) |
                    Q(task_name__icontains=query) |
                    Q(stakeholder__icontains=query)
                )
            
            # Status filter
            status_list = serializer.validated_data.get('status')
            if status_list:
                queryset = queryset.filter(status__in=status_list)
            
            # Priority filter
            priority_list = serializer.validated_data.get('priority')
            if priority_list:
                queryset = queryset.filter(priority__in=priority_list)
            
            # Task type filter
            task_type_list = serializer.validated_data.get('task_type')
            if task_type_list:
                queryset = queryset.filter(task_type__in=task_type_list)
            
            # Owner filter
            owner = serializer.validated_data.get('owner')
            if owner:
                queryset = queryset.filter(owner_id=owner)
            
            # Date filters
            start_from = serializer.validated_data.get('start_date_from')
            if start_from:
                queryset = queryset.filter(start_date__gte=start_from)
            
            start_to = serializer.validated_data.get('start_date_to')
            if start_to:
                queryset = queryset.filter(start_date__lte=start_to)
            
            due_from = serializer.validated_data.get('due_date_from')
            if due_from:
                queryset = queryset.filter(due_date__gte=due_from)
            
            due_to = serializer.validated_data.get('due_date_to')
            if due_to:
                queryset = queryset.filter(due_date__lte=due_to)
            
            # Project filter
            project = serializer.validated_data.get('project_name')
            if project:
                queryset = queryset.filter(project_name__icontains=project)
            
            # Log search
            SearchQuery.objects.create(
                user=request.user,
                query=query or '',
                filters=serializer.validated_data,
                results_count=queryset.count()
            )
            
            # Return results
            results = self.get_serializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': results.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Task history (read-only)"""
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by task if specified"""
        queryset = TaskHistory.objects.all().select_related('task', 'changed_by')
        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    """Comments on tasks"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by task if specified"""
        queryset = Comment.objects.all().select_related('user', 'task')
        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset
    
    def perform_create(self, serializer):
        """Create comment and notify"""
        comment = serializer.save(user=self.request.user)
        
        # Create notification for task owner
        if comment.task.owner != self.request.user:
            Notification.objects.create(
                user=comment.task.owner,
                task=comment.task,
                notification_type='task_comment',
                title='New Comment',
                message=f'{self.request.user.username} commented on {comment.task.title}'
            )


class AttachmentViewSet(viewsets.ModelViewSet):
    """File attachments"""
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Upload file with metadata"""
        file = self.request.FILES.get('file')
        serializer.save(
            uploaded_by=self.request.user,
            filename=file.name,
            file_size=file.size,
            file_type=file.content_type
        )


class ReportViewSet(viewsets.ModelViewSet):
    """Report generation and management"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate_task_summary(self, request):
        """Generate task summary report"""
        format_type = request.data.get('format', 'csv')
        filters = request.data.get('filters', {})
        
        # Get tasks with filters
        tasks = Task.objects.all()
        if filters:
            # Apply filters similar to search
            pass
        
        # Generate file based on format
        if format_type == 'csv':
            return self._generate_csv_report(tasks, request.user)
        elif format_type == 'xlsx':
            return self._generate_excel_report(tasks, request.user)
        
        return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_csv_report(self, tasks, user):
        """Generate CSV report"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="ea_tasks_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Board', 'Column', 'Title', 'Project', 'Task Type', 'Priority', 'Status',
            'Owner', 'Assigned To', 'Stakeholder', 'BA/PM',
            'Design Status', 'Dev Status', 'SIT Status',
            'Start Date', 'Due Date', 'Completed Date',
            'Progress Notes', 'Dependencies', 'Created', 'Updated'
        ])
        
        for task in tasks:
            writer.writerow([
                task.column.board.name,
                task.column.name,
                task.title,
                task.project_name,
                task.task_type,
                task.priority,
                task.status,
                task.owner.username if task.owner else '',
                task.assigned_to.username if task.assigned_to else '',
                task.stakeholder,
                task.bapm,
                task.design_status,
                task.dev_status,
                task.sit_status,
                task.start_date,
                task.due_date,
                task.completed_date,
                task.progress_notes,
                task.dependencies,
                task.created_at.strftime('%Y-%m-%d %H:%M'),
                task.updated_at.strftime('%Y-%m-%d %H:%M'),
            ])
        
        # Save report record
        Report.objects.create(
            name=f'Task Summary {timezone.now().strftime("%Y-%m-%d")}',
            report_type='task_summary',
            format='csv',
            generated_by=user,
            row_count=tasks.count()
        )
        
        return response
    
    @action(detail=False, methods=['post'])
    def generate_team_performance(self, request):
        """Generate team performance report"""
        # Implementation for team performance metrics
        pass
    
    @action(detail=False, methods=['post'])
    def generate_project_status(self, request):
        """Generate project status report"""
        # Implementation for project status
        pass


class NotificationViewSet(viewsets.ModelViewSet):
    """User notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for current user"""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True)
        return Response({'marked': count})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'count': count})





