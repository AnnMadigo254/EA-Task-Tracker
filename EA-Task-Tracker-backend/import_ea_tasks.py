"""
Import EA Tasks from Excel to MySQL Database
Handles grouped assignee format where assignee appears once for multiple tasks
"""
import os
import django
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tasktracker_backend.settings')
django.setup()


from tasks.models import User, Board, Column, Task

# Read the Excel file - header is in row 1 (0-indexed)
# file_path = r"C:\Users\amadigo\tasktracker\kanban-task-management\EA_Tasks.xlsx"
file_path = '/app/EA_Tasks.xlsx'

# Read Excel with header in row 1
df = pd.read_excel(file_path, header=1)

print("🚀 Starting EA Tasks Import...\n")

# Clean column names (remove trailing spaces)
df.columns = df.columns.str.strip()

# Forward fill the Assignee column (carry down the assignee name)
df['Assignee'] = df['Assignee'].fillna(method='ffill')

print(f"📋 Found {len(df)} rows to import\n")

# Define column mapping
column_mapping = {
    'To Do': {'name': 'To Do', 'color': '#49C4E5'},
    'In Progress': {'name': 'In Progress', 'color': '#00A86B'},
    'Done': {'name': 'Done', 'color': '#00C853'},
}

# Get unique assignees (skip NaN values and clean)
assignees = df['Assignee'].dropna().unique()
assignees = [str(a).strip() for a in assignees if str(a).strip() and str(a) != 'nan']

print(f"👥 Found {len(assignees)} architects:")
for assignee in assignees:
    print(f"   - {assignee}")
print()

# Create users and boards
for assignee in assignees:
    # Clean assignee name
    assignee_str = str(assignee).strip()
    name_parts = assignee_str.split()
    first_name = name_parts[0] if len(name_parts) > 0 else 'Unknown'
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
    # Create username
    username = assignee_str.replace(' ', '').lower()
    email = f"{username}@coopbank.co.ke"
    
    # Create or get user
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'role': 'architect',
            'department': 'Enterprise Architecture'
        }
    )
    
    if created:
        user.set_password('coopbank2025')
        user.save()
        print(f"✅ Created user: {assignee_str}")
    else:
        print(f"   User exists: {assignee_str}")
    
    # Create board for user
    board, created = Board.objects.get_or_create(
        name=f"{assignee_str}'s Board",
        owner=user,
        defaults={'description': f'EA Projects for {assignee_str}'}
    )
    
    if created:
        print(f"   ✅ Created board: {board.name}")
    
    # Create columns for this board
    for idx, (col_key, col_data) in enumerate(column_mapping.items()):
        column, created = Column.objects.get_or_create(
            board=board,
            name=col_data['name'],
            defaults={
                'color': col_data['color'],
                'position': idx
            }
        )
        if created:
            print(f"      ✅ Created column: {col_data['name']}")

print("\n📊 Importing tasks...\n")

# Import tasks
task_count = 0
skipped = 0

for index, row in df.iterrows():
    try:
        # Get assignee (now forward-filled)
        assignee = row.get('Assignee')
        
        # Skip if no assignee
        if pd.isna(assignee) or str(assignee).strip() == '':
            skipped += 1
            continue
        
        assignee_str = str(assignee).strip()
        
        # Get user and board
        username = assignee_str.replace(' ', '').lower()
        try:
            user = User.objects.get(username=username)
            board = Board.objects.get(owner=user)
        except Exception as e:
            print(f"❌ User not found for: {assignee_str}")
            skipped += 1
            continue
        
        # Get task fields
        project_name = str(row.get('Project Name', '')).strip() if pd.notna(row.get('Project Name')) else ''
        task_name = str(row.get('Task name', '')).strip() if pd.notna(row.get('Task name')) else ''
        
        # Skip if both are empty
        if not project_name and not task_name:
            skipped += 1
            continue
        
        # Determine status and column based on Dev Status and SIT Status
        design_status = str(row.get('Design Status', '')).strip() if pd.notna(row.get('Design Status')) else ''
        dev_status = str(row.get('Dev Status', '')).strip() if pd.notna(row.get('Dev Status')) else ''
        sit_status = str(row.get('SIT Status', '')).strip() if pd.notna(row.get('SIT Status')) else ''
        
        # Logic to determine which column
        if sit_status and 'complete' in sit_status.lower():
            status = 'Done'
        elif dev_status and 'complete' in dev_status.lower() and sit_status and 'complete' in sit_status.lower():
            status = 'Done'
        elif dev_status and 'progress' in dev_status.lower():
            status = 'In Progress'
        elif sit_status and 'progress' in sit_status.lower():
            status = 'In Progress'
        elif design_status and 'complete' in design_status.lower() and not dev_status:
            status = 'In Progress'
        elif 'on-hold' in design_status.lower() or 'pending' in str(row.get('Dev Status', '')).lower():
            status = 'To Do'
        else:
            status = 'In Progress'  # Default to In Progress
        
        # Get column
        try:
            column = Column.objects.get(board=board, name=status)
        except:
            # Default to In Progress if column not found
            column = Column.objects.get(board=board, name='In Progress')
        
        # Create title - prefer task name, fall back to project name
        title = task_name if task_name else project_name
        if len(title) > 500:
            title = title[:497] + "..."
        
        # Get description
        description = str(row.get('Project Desctrption', '')).strip() if pd.notna(row.get('Project Desctrption')) else ''
        
        # Get priority
        priority_raw = str(row.get('Priority', 'Medium')).strip().lower() if pd.notna(row.get('Priority')) else 'medium'
        if 'high' in priority_raw or 'critical' in priority_raw:
            priority = 'High'
        elif 'low' in priority_raw:
            priority = 'Low'
        else:
            priority = 'Medium'
        
        # Get other fields
        progress_notes = str(row.get('Progress Notes updates', '')).strip() if pd.notna(row.get('Progress Notes updates')) else ''
        bapm = str(row.get('BA/PM', '')).strip() if pd.notna(row.get('BA/PM')) else ''
        comments = str(row.get('Comments', '')).strip() if pd.notna(row.get('Comments')) else ''
        dependencies = str(row.get('Dependencies', '')).strip() if pd.notna(row.get('Dependencies')) else ''
        
        # Create task
        task = Task.objects.create(
            column=column,
            title=title,
            description=description,
            project_name=project_name,
            task_name=task_name,
            design_status=design_status,
            dev_status=dev_status,
            sit_status=sit_status,
            priority=priority,
            status=status,
            owner=user,
            bapm=bapm,
            progress_notes=progress_notes,
            comments=comments,
            dependencies=dependencies,
            position=task_count
        )
        
        task_count += 1
        
        # Show progress every 10 tasks
        if task_count % 10 == 0:
            print(f"   ✅ Imported {task_count} tasks...")
        
    except Exception as e:
        print(f"❌ Error on row {index + 2}: {str(e)}")
        skipped += 1
        continue


print(f"\n🎉 Import Complete!")
print(f"\n📊 Summary:")
print(f"   Users: {User.objects.filter(role='architect').count()}")
print(f"   Boards: {Board.objects.count()}")
print(f"   Columns: {Column.objects.count()}")
print(f"   Tasks Imported: {task_count}")
print(f"   Rows Skipped: {skipped}")



# Show task distribution
print(f"\n📋 Tasks by Architect:")
from django.db.models import Count
for user in User.objects.filter(role='architect').order_by('first_name'):
    count = Task.objects.filter(owner=user).count()
    if count > 0:
        print(f"   {user.first_name} {user.last_name}: {count} tasks")

print(f"\n📊 Tasks by Status:")
for status in ['To Do', 'In Progress', 'Done']:
    count = Task.objects.filter(status=status).count()
    print(f"   {status}: {count} tasks")

print(f"\n📊 Tasks by Priority:")
for priority in ['Critical', 'High', 'Medium', 'Low']:
    count = Task.objects.filter(priority=priority).count()
    if count > 0:
        print(f"   {priority}: {count} tasks")


print(f"\n✅ All EA tasks imported successfully!")
print(f"\n🌐 Access your data at:")
print(f"   Admin: http://127.0.0.1:8000/admin/")
print(f"   API: http://127.0.0.1:8000/api/tasks/")










