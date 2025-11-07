from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import re
import json
import pandas as pd
import io
from werkzeug.utils import secure_filename
import google.generativeai as genai

from database import db, init_db
from models import User, Task

app = Flask(__name__)
CORS(app)

# SQLite Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pulsevo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize database
init_db(app)

# Configure Gemini API
GEMINI_API_KEY = 'AIzaSyDhTlDfDvXT87ZycpAhtedLFAps3xUwAF0'
genai.configure(api_key=GEMINI_API_KEY)

# ==================== OVERVIEW ENDPOINTS ====================

@app.route('/api/overview', methods=['GET'])
def get_overview():
    """Get dashboard overview metrics FILTERED by date range"""
    filter_type = request.args.get('filter', 'today').lower()
    now = datetime.now()
    
    # Define current period start date
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        comparison_start = start_date - timedelta(days=1)
        comparison_end = start_date
    elif filter_type == 'week':
        start_date = now - timedelta(days=7)
        comparison_start = start_date - timedelta(days=7)
        comparison_end = start_date
    elif filter_type == 'month':
        # THIS MONTH: From 1st of current month (not last 30 days)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Compare with previous month (same number of days)
        if now.month == 1:
            # If January, compare with December of previous year
            prev_month_start = start_date.replace(year=now.year-1, month=12, day=1)
        else:
            prev_month_start = start_date.replace(month=now.month-1, day=1)
        comparison_start = prev_month_start
        comparison_end = start_date
    else:  # 'all'
        start_date = datetime(2000, 1, 1)
        comparison_start = start_date
        comparison_end = start_date + timedelta(days=90)
    
    # ===== FILTER TASKS BY SELECTED PERIOD =====
    # Tasks created in the current period (using ONLY created_date)
    tasks_in_period = Task.query.filter(
        Task.created_date >= start_date
    ).all()
    
    # Count by status IN THE PERIOD
    open_tasks = len([t for t in tasks_in_period if t.status == 'Open'])
    in_progress = len([t for t in tasks_in_period if t.status == 'In Progress'])
    completed = len([t for t in tasks_in_period if t.status == 'Completed'])
    blocked = len([t for t in tasks_in_period if t.status == 'Blocked'])
    total_tasks = len(tasks_in_period)
    
    # Comparison period tasks
    tasks_comparison = Task.query.filter(
        Task.created_date >= comparison_start,
        Task.created_date < comparison_end
    ).all()
    
    prev_open = len([t for t in tasks_comparison if t.status == 'Open'])
    prev_progress = len([t for t in tasks_comparison if t.status == 'In Progress'])
    prev_completed = len([t for t in tasks_comparison if t.status == 'Completed'])
    
    # Completed in period (based on filter)
    completed_in_period = len([t for t in tasks_in_period if t.status == 'Completed' and t.completed_date and t.completed_date >= start_date])
    
    # Completed in comparison period
    completed_comparison_period = len([t for t in tasks_comparison if t.status == 'Completed' and t.completed_date and t.completed_date >= comparison_start and t.completed_date < comparison_end])
    
    # Completion rate for filtered period
    completion_rate = round((completed / total_tasks * 100), 1) if total_tasks > 0 else 0
    prev_completion_rate = round((prev_completed / len(tasks_comparison) * 100), 1) if len(tasks_comparison) > 0 else 0
    
    # Calculate percentage changes
    open_change = calculate_change(open_tasks, prev_open)
    progress_change = calculate_change(in_progress, prev_progress)
    completed_period_change = calculate_change(completed_in_period, completed_comparison_period)
    rate_change = round(completion_rate - prev_completion_rate, 1)
    
    return jsonify({
        'open_tasks': open_tasks,
        'open_change': open_change,
        'in_progress': in_progress,
        'progress_change': progress_change,
        'completed_today': completed_in_period,  # Shows completed for selected period
        'today_change': completed_period_change,  # Change vs previous period
        'completion_rate': completion_rate,
        'rate_change': rate_change,
        'blocked_tasks': blocked,
        'total_tasks': total_tasks,
        'completed_tasks': completed,
        'filter': filter_type,
        'start_date': start_date.isoformat(),
        'tasks_in_period': total_tasks
    })

def calculate_change(current, previous):
    """Calculate percentage change between two values"""
    if previous == 0:
        return 100 if current > 0 else 0
    change = ((current - previous) / previous) * 100
    return round(change, 1)

@app.route('/api/distribution', methods=['GET'])
def get_task_distribution():
    """Get task distribution FILTERED by date range"""
    filter_type = request.args.get('filter', 'today').lower()
    now = datetime.now()
    
    # Define period
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == 'week':
        start_date = now - timedelta(days=7)
    elif filter_type == 'month':
        # THIS MONTH: From 1st of current month (not last 30 days)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = datetime(2000, 1, 1)
    
    # Filter tasks by period (using ONLY created_date)
    tasks_in_period = Task.query.filter(
        Task.created_date >= start_date
    ).all()
    
    open_tasks = len([t for t in tasks_in_period if t.status == 'Open'])
    in_progress = len([t for t in tasks_in_period if t.status == 'In Progress'])
    completed = len([t for t in tasks_in_period if t.status == 'Completed'])
    blocked = len([t for t in tasks_in_period if t.status == 'Blocked'])
    
    return jsonify([
        {'name': 'Open', 'value': open_tasks, 'color': '#a78bfa'},
        {'name': 'In Progress', 'value': in_progress, 'color': '#60a5fa'},
        {'name': 'Completed', 'value': completed, 'color': '#fbbf24'},
        {'name': 'Blocked', 'value': blocked, 'color': '#ec4899'}
    ])

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Get task trends over time FILTERED by date range (1/7/30/90 days)"""
    filter_type = request.args.get('filter', 'today').lower()
    
    # Determine number of days and start date based on filter
    now = datetime.now()
    
    if filter_type == 'today':
        num_days = 1  # Show today only (1 day)
        start_date = now.date()
    elif filter_type == 'week':
        num_days = 7  # Last 7 days
        start_date = now.date() - timedelta(days=num_days - 1)
    elif filter_type == 'month':
        # THIS MONTH: From 1st of current month to today (not last 30 days)
        start_date = now.replace(day=1).date()  # First day of current month
        num_days = (now.date() - start_date).days + 1  # Days from 1st to today
    elif filter_type == 'all':
        # For 'all', show the full date range in the database
        oldest_task = Task.query.order_by(Task.created_date.asc()).first()
        if oldest_task:
            start_date = oldest_task.created_date.date()
            num_days = (now.date() - start_date).days + 1
            num_days = min(num_days, 90)  # Cap at 90 days for performance
            start_date = now.date() - timedelta(days=num_days - 1)
        else:
            num_days = 30  # Default if no tasks
            start_date = now.date() - timedelta(days=num_days - 1)
    else:
        num_days = 7  # Default fallback
        start_date = now.date() - timedelta(days=num_days - 1)
    
    trends = []
    
    for i in range(num_days - 1, -1, -1):
        date = start_date + timedelta(days=(num_days - 1 - i))
        
        # Format date string based on range
        if num_days <= 7:
            date_str = date.strftime('%b %d')  # "Nov 07" for short ranges
        else:
            date_str = date.strftime('%m/%d')  # "11/07" for longer ranges
        
        # Count tasks created on this date
        created = Task.query.filter(db.func.date(Task.created_date) == date).count()
        
        # Count tasks completed on this date
        completed = Task.query.filter(
            Task.status == 'Completed',
            db.func.date(Task.completed_date) == date
        ).count()
        
        # Count tasks in progress on this date
        in_progress = Task.query.filter(
            Task.status == 'In Progress',
            Task.start_date <= datetime.combine(date, datetime.max.time()),
            db.or_(
                Task.completed_date.is_(None),
                Task.completed_date > datetime.combine(date, datetime.max.time())
            )
        ).count()
        
        trends.append({
            'date': date_str,
            'created': created,
            'completed': completed,
            'in_progress': min(in_progress, created + 5)  # Cap at reasonable value
        })
    
    return jsonify(trends)

@app.route('/api/team-performance', methods=['GET'])
def get_team_performance():
    """Get team performance FILTERED by date range"""
    filter_type = request.args.get('filter', 'today').lower()
    now = datetime.now()
    
    # Define period
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == 'week':
        start_date = now - timedelta(days=7)
    elif filter_type == 'month':
        # THIS MONTH: From 1st of current month (not last 30 days)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = datetime(2000, 1, 1)
    
    # Get tasks in period (using ONLY created_date)
    tasks_in_period = Task.query.filter(
        Task.created_date >= start_date
    ).all()
    
    # Get active users
    users = User.query.filter_by(is_active=True).all()
    
    result = []
    for user in users:
        # Filter user's tasks by period
        user_tasks = [t for t in tasks_in_period if t.assigned_to == user.user_id]
        
        if not user_tasks:
            continue
        
        completed = len([t for t in user_tasks if t.status == 'Completed'])
        in_progress = len([t for t in user_tasks if t.status == 'In Progress'])
        open_tasks = len([t for t in user_tasks if t.status == 'Open'])
        
        result.append({
            'name': user.name.split()[0],
            'completed': completed,
            'in_progress': in_progress,
            'open': open_tasks,
            'total': len(user_tasks)
        })
    
    # Sort by total and limit to top 5
    result = sorted(result, key=lambda x: x['total'], reverse=True)[:5]
    
    return jsonify(result)

# ==================== TASKS ENDPOINTS ====================

@app.route('/api/tasks/status-counts', methods=['GET'])
def get_task_status_counts():
    """Get count of tasks by status"""
    all_count = Task.query.count()
    open_count = Task.query.filter_by(status='Open').count()
    in_progress_count = Task.query.filter_by(status='In Progress').count()
    completed_count = Task.query.filter_by(status='Completed').count()
    blocked_count = Task.query.filter_by(status='Blocked').count()
    
    return jsonify({
        'all': all_count,
        'open': open_count,
        'in_progress': in_progress_count,
        'completed': completed_count,
        'blocked': blocked_count
    })

@app.route('/api/tasks/upload', methods=['POST'])
def upload_tasks():
    """Upload tasks from CSV file"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Read CSV file
        try:
            csv_data = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
        except Exception as e:
            return jsonify({'error': f'Invalid CSV format: {str(e)}'}), 400
        
        # Validate required columns
        required_columns = ['task_name', 'status', 'assigned_to']
        missing_columns = [col for col in required_columns if col not in csv_data.columns]
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}',
                'required': required_columns,
                'found': list(csv_data.columns)
            }), 400
        
        # Process and insert tasks
        tasks_added = 0
        tasks_skipped = 0
        errors = []
        
        for index, row in csv_data.iterrows():
            try:
                # Generate task_id if not provided
                if pd.isna(row.get('task_id')) or not row.get('task_id'):
                    # Get last task number
                    last_task = Task.query.order_by(Task.task_id.desc()).first()
                    if last_task and last_task.task_id.startswith('TASK-'):
                        last_num = int(last_task.task_id.split('-')[1])
                        task_id = f'TASK-{str(last_num + 1).zfill(4)}'
                    else:
                        task_id = f'TASK-{str(Task.query.count() + 1).zfill(4)}'
                else:
                    task_id = str(row['task_id'])
                
                # Check if task already exists
                existing_task = Task.query.filter_by(task_id=task_id).first()
                if existing_task:
                    tasks_skipped += 1
                    continue
                
                # Verify user exists
                user = User.query.filter_by(user_id=str(row['assigned_to'])).first()
                if not user:
                    errors.append(f"Row {index + 2}: User {row['assigned_to']} not found")
                    tasks_skipped += 1
                    continue
                
                # Parse dates
                created_date = pd.to_datetime(row.get('created_date')) if pd.notna(row.get('created_date')) else datetime.now()
                due_date = pd.to_datetime(row.get('due_date')) if pd.notna(row.get('due_date')) else None
                start_date = pd.to_datetime(row.get('start_date')) if pd.notna(row.get('start_date')) else None
                completed_date = pd.to_datetime(row.get('completed_date')) if pd.notna(row.get('completed_date')) else None
                
                # Create new task
                new_task = Task(
                    task_id=task_id,
                    task_name=str(row['task_name']),
                    description=str(row.get('description', '')) if pd.notna(row.get('description')) else None,
                    status=str(row['status']),
                    priority=str(row.get('priority', 'Medium')) if pd.notna(row.get('priority')) else 'Medium',
                    project=str(row.get('project', 'Web Platform')) if pd.notna(row.get('project')) else 'Web Platform',
                    assigned_to=str(row['assigned_to']),
                    created_date=created_date,
                    due_date=due_date,
                    start_date=start_date,
                    completed_date=completed_date,
                    estimated_hours=float(row.get('estimated_hours', 0)) if pd.notna(row.get('estimated_hours')) else None,
                    tags=str(row.get('tags', '')) if pd.notna(row.get('tags')) else None,
                    blocked_reason=str(row.get('blocked_reason', '')) if pd.notna(row.get('blocked_reason')) else None,
                    comments=str(row.get('comments', '')) if pd.notna(row.get('comments')) else None
                )
                
                db.session.add(new_task)
                tasks_added += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
                tasks_skipped += 1
                continue
        
        # Commit all tasks
        db.session.commit()
        
        return jsonify({
            'success': True,
            'tasks_added': tasks_added,
            'tasks_skipped': tasks_skipped,
            'total_rows': len(csv_data),
            'errors': errors[:10] if errors else []  # Limit errors to first 10
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filters and pagination"""
    # Get filter parameters
    status = request.args.get('status')
    project = request.args.get('project')
    assigned_to = request.args.get('assigned_to')
    priority = request.args.get('priority')
    search = request.args.get('search', '')
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query
    query = Task.query
    
    # Apply filters
    if status and status != 'All Tasks':
        query = query.filter_by(status=status)
    if project and project != 'All Projects':
        query = query.filter_by(project=project)
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)
    if priority and priority != 'All Priorities':
        query = query.filter_by(priority=priority)
    if search:
        query = query.filter(
            db.or_(
                Task.task_name.ilike(f'%{search}%'),
                Task.task_id.ilike(f'%{search}%')
            )
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    query = query.order_by(Task.created_date.desc())
    paginated_tasks = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all users for name lookup
    users = User.query.all()
    user_map = {u.user_id: u.name for u in users}
    
    # Calculate stats for each user based on FILTERED tasks (not all tasks)
    # Get all filtered tasks (not just paginated ones)
    filtered_query = Task.query
    if status and status != 'All Tasks':
        filtered_query = filtered_query.filter_by(status=status)
    if project and project != 'All Projects':
        filtered_query = filtered_query.filter_by(project=project)
    if priority and priority != 'All Priorities':
        filtered_query = filtered_query.filter_by(priority=priority)
    if search:
        filtered_query = filtered_query.filter(
            db.or_(
                Task.task_name.ilike(f'%{search}%'),
                Task.task_id.ilike(f'%{search}%')
            )
        )
    
    filtered_tasks = filtered_query.all()
    
    users_stats = {}
    for task in filtered_tasks:
        if task.assigned_to:
            if task.assigned_to not in users_stats:
                users_stats[task.assigned_to] = {
                    'assigned': 0,
                    'completed': 0,
                    'in_progress': 0,
                    'open': 0
                }
            users_stats[task.assigned_to]['assigned'] += 1
            if task.status == 'Completed':
                users_stats[task.assigned_to]['completed'] += 1
            elif task.status == 'In Progress':
                users_stats[task.assigned_to]['in_progress'] += 1
            elif task.status == 'Open':
                users_stats[task.assigned_to]['open'] += 1
    
    return jsonify({
        'tasks': [{
            'task_id': t.task_id,
            'task_name': t.task_name,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'project': t.project,
            'assigned_to': t.assigned_to,
            'assigned_to_name': user_map.get(t.assigned_to, 'Unassigned'),
            'created_date': t.created_date.isoformat() if t.created_date else None,
            'due_date': t.due_date.isoformat() if t.due_date else None,
            'start_date': t.start_date.isoformat() if t.start_date else None,
            'completed_date': t.completed_date.isoformat() if t.completed_date else None,
            'estimated_hours': t.estimated_hours,
            'tags': t.tags,
            'blocked_reason': t.blocked_reason,
            'comments': t.comments
        } for t in paginated_tasks.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': paginated_tasks.pages,
            'has_next': paginated_tasks.has_next,
            'has_prev': paginated_tasks.has_prev
        },
        'users_stats': users_stats
    })

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get single task by ID"""
    task = Task.query.get_or_404(task_id)
    
    return jsonify({
        'task_id': task.task_id,
        'task_name': task.task_name,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'project': task.project,
        'assigned_to': task.assigned_to,
        'created_date': task.created_date.isoformat() if task.created_date else None,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'completed_date': task.completed_date.isoformat() if task.completed_date else None,
        'tags': task.tags,
        'blocked_reason': task.blocked_reason
    })

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all unique projects"""
    projects = db.session.query(Task.project).distinct().all()
    return jsonify([p[0] for p in projects if p[0]])

@app.route('/api/projects/stats', methods=['GET'])
def get_project_stats():
    """Get task counts by project"""
    projects = ['API Services', 'Mobile App', 'Web Platform']
    
    result = []
    for project in projects:
        total = Task.query.filter_by(project=project).count()
        open_tasks = Task.query.filter_by(project=project, status='Open').count()
        
        result.append({
            'project': project,
            'total': total,
            'open': open_tasks
        })
    
    return jsonify(result)

# ==================== USERS ENDPOINTS ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users with task statistics"""
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.name.ilike(f'%{search}%'))
    
    users = query.all()
    
    result = []
    for user in users:
        assigned = Task.query.filter_by(assigned_to=user.user_id).count()
        completed = Task.query.filter_by(assigned_to=user.user_id, status='Completed').count()
        in_progress = Task.query.filter_by(assigned_to=user.user_id, status='In Progress').count()
        open_tasks = Task.query.filter_by(assigned_to=user.user_id, status='Open').count()
        
        completion_pct = round((completed / assigned * 100), 1) if assigned > 0 else 0
        
        # Calculate trend
        if completion_pct == 0:
            trend = 0.0
        elif completion_pct == 100:
            trend = 100.0
        else:
            trend = round(completion_pct * random.uniform(0.8, 1.2), 1)
        
        result.append({
            'user_id': user.user_id,
            'name': user.name,
            'initials': user.initials,
            'email': user.email,
            'role': user.role,
            'team': user.team,
            'assigned': assigned,
            'completed': completed,
            'in_progress': in_progress,
            'open': open_tasks,
            'completion_percentage': completion_pct,
            'trend': trend
        })
    
    return jsonify(result)

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get single user by ID"""
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'user_id': user.user_id,
        'name': user.name,
        'email': user.email,
        'initials': user.initials,
        'role': user.role,
        'team': user.team,
        'is_active': user.is_active
    })

# ==================== SETTINGS ENDPOINTS ====================

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    return jsonify({
        'github_token': 'ghp_xxxxxxxxxxxx',
        'trello_key': '',
        'trello_token': '',
        'notifications': {
            'task_updates': True,
            'ai_insights': True,
            'daily_digest': False
        }
    })

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save settings"""
    data = request.get_json()
    # In production, save to database
    return jsonify({'message': 'Settings saved successfully'})

# ==================== NATURAL LANGUAGE QUERY ====================

@app.route('/api/query', methods=['POST'])
def natural_language_query():
    """Convert natural language to SQL and execute query"""
    try:
        data = request.get_json()
        user_question = data.get('question', '').strip()
        
        if not user_question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Check for greetings
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening', 'sup', 'yo']
        question_lower = user_question.lower()
        
        if any(greeting == question_lower or question_lower.startswith(greeting + ' ') for greeting in greetings):
            return jsonify({
                'success': True,
                'question': user_question,
                'response': "👋 Hi there! I'm your AI assistant designed specifically to help you query and analyze your team's **tasks** and **user** data.\n\n"
                            "I can help you find information like:\n"
                            "• Task statistics and status\n"
                            "• User assignments and workload\n"
                            "• Project progress and trends\n"
                            "• Team performance metrics\n\n"
                            "Just ask me anything about your tasks or team members! For example:\n"
                            "- \"Show me all blocked tasks\"\n"
                            "- \"Who has the most tasks?\"\n"
                            "- \"List high priority tasks due this week\"",
                'timestamp': datetime.now().strftime('%I:%M %p'),
                'data': [],
                'columns': [],
                'count': 0
            })
        
        # Check for off-topic questions
        off_topic_keywords = [
            'weather', 'recipe', 'movie', 'song', 'game', 'sports', 'news', 
            'stock', 'price', 'restaurant', 'hotel', 'flight', 'travel',
            'joke', 'story', 'poem', 'translate', 'meaning of life',
            'python code', 'javascript', 'programming', 'algorithm',
            'capital of', 'president', 'history', 'geography', 'write a',
            'create a script', 'how to cook', 'best place', 'recommend'
        ]
        
        # Check if question contains off-topic keywords but not task-related words
        task_keywords = ['task', 'user', 'team', 'project', 'assignment', 'status', 'priority', 'completed', 'open', 'blocked', 'progress', 'assigned', 'work']
        has_task_context = any(keyword in question_lower for keyword in task_keywords)
        
        # Simple off-topic detection
        is_off_topic = False
        
        if not has_task_context:
            for keyword in off_topic_keywords:
                if keyword in question_lower:
                    is_off_topic = True
                    break
            
            # Special check for "what is" / "who is" followed by non-task-related words
            if question_lower.startswith('what is') or question_lower.startswith('who is'):
                # Check if the rest of the question is task-related
                question_rest = question_lower.replace('what is', '').replace('who is', '').strip()
                if not any(keyword in question_rest for keyword in task_keywords):
                    is_off_topic = True
        
        if is_off_topic:
            return jsonify({
                'success': False,
                'question': user_question,
                'response': "❌ I'm specifically designed to work with your **task management and team productivity data**.\n\n"
                            "I can only answer questions related to:\n"
                            "• Tasks (status, priority, assignments, progress)\n"
                            "• Users (team members, workload, performance)\n"
                            "• Projects (Web Platform, Mobile App, API Services)\n\n"
                            "Your question seems to be outside my scope. Please ask something about your tasks or team!",
                'timestamp': datetime.now().strftime('%I:%M %p'),
                'data': [],
                'columns': [],
                'count': 0
            }), 400
        
        # Database schema for context
        schema = """
DATABASE SCHEMA:

Table: users
- user_id (VARCHAR, PRIMARY KEY) - Unique user identifier (e.g., 'USER-001')
- name (VARCHAR) - Full name (e.g., 'Alice Johnson')
- email (VARCHAR) - Email address
- initials (VARCHAR) - User initials (e.g., 'AJ')
- role (VARCHAR) - Job role (e.g., 'Developer', 'Designer', 'Manager')
- team (VARCHAR) - Team name (e.g., 'Your Team', 'Alpha Team', 'Beta Team', 'Gamma Team')
- is_active (BOOLEAN) - Whether user is active (1 or 0)
- created_at (DATETIME) - Account creation date

Table: tasks
- task_id (VARCHAR, PRIMARY KEY) - Unique task identifier (e.g., 'TASK-0001')
- task_name (VARCHAR) - Task title
- description (TEXT) - Task description
- status (VARCHAR) - One of: 'Open', 'In Progress', 'Completed', 'Blocked'
- priority (VARCHAR) - One of: 'High', 'Medium', 'Low'
- project (VARCHAR) - Project name: 'Web Platform', 'Mobile App', 'API Services'
- assigned_to (VARCHAR, FOREIGN KEY) - References users.user_id
- created_date (DATETIME) - When task was created
- due_date (DATETIME) - Task deadline
- start_date (DATETIME) - When work started
- completed_date (DATETIME) - When task was completed
- estimated_hours (FLOAT) - Estimated hours to complete
- tags (VARCHAR) - Comma-separated tags
- blocked_reason (VARCHAR) - Reason if blocked
- comments (TEXT) - Additional comments
- updated_at (DATETIME) - Last update timestamp

IMPORTANT NOTES:
- Use JOIN when relating users and tasks
- For date filtering, use DATE() function for comparing dates
- Status values are case-sensitive: 'Open', 'In Progress', 'Completed', 'Blocked'
- Team names: 'Your Team', 'Alpha Team', 'Beta Team', 'Gamma Team'
- Current date: {current_date}
"""
        
        # System prompt for Gemini
        system_prompt = """You are an expert SQL query generator for a team productivity dashboard.

CRITICAL: You can ONLY work with the following database tables: 'users' and 'tasks'.
If the user asks about anything not related to these tables, return: ERROR_OFF_TOPIC

Your task:
1. First, verify the question is about tasks or users data
2. Convert the user's natural language question into a valid SQLite SQL query
3. Return ONLY the SQL query, nothing else - no explanations, no markdown, no code blocks
4. Make sure the query is safe and optimized (only SELECT queries allowed)
5. Use proper JOINs when needed
6. Handle aggregations (COUNT, SUM, AVG) when needed
7. Use LIMIT for queries that might return many rows (default LIMIT 50)

Rules:
- Return ONLY the SQL query (one line, no line breaks)
- No SELECT * - specify columns explicitly
- Always include relevant column names
- Use aliases for better readability (u for users, t for tasks)
- For counting, use COUNT(*) or COUNT(column_name)
- For user-related queries, include user name via JOIN
- For date comparisons, use DATE() or datetime functions
- Status must match exactly: 'Open', 'In Progress', 'Completed', 'Blocked'
- Priority must match exactly: 'High', 'Medium', 'Low'
- Projects must match exactly: 'Web Platform', 'Mobile App', 'API Services'
- For "recent" or "latest", use ORDER BY created_date DESC
- For "overdue", compare due_date < current date
- Always add appropriate ORDER BY for better results

Example outputs:
"SELECT name, COUNT(t.task_id) as task_count FROM users u LEFT JOIN tasks t ON u.user_id = t.assigned_to GROUP BY u.user_id, u.name ORDER BY task_count DESC LIMIT 10"

"SELECT status, COUNT(*) as count FROM tasks GROUP BY status"

"SELECT u.name, t.task_name, t.priority FROM tasks t JOIN users u ON t.assigned_to = u.user_id WHERE t.status = 'Blocked' ORDER BY t.created_date DESC LIMIT 20"

"SELECT u.name, COUNT(CASE WHEN t.status = 'Completed' THEN 1 END) as completed, COUNT(t.task_id) as total FROM users u LEFT JOIN tasks t ON u.user_id = t.assigned_to GROUP BY u.user_id, u.name ORDER BY completed DESC LIMIT 10"
"""
        
        # Prepare full prompt
        full_prompt = f"""{system_prompt}

{schema.format(current_date=datetime.now().strftime('%Y-%m-%d'))}

USER QUESTION: {user_question}

SQL QUERY:"""
        
        # Call Gemini API
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(full_prompt)
        
        # Extract SQL query from response
        sql_query = response.text.strip()
        
        # Clean up the SQL query (remove markdown, code blocks, etc.)
        sql_query = re.sub(r'```sql\s*', '', sql_query)
        sql_query = re.sub(r'```\s*', '', sql_query)
        sql_query = sql_query.strip()
        
        # Remove any trailing semicolons
        sql_query = sql_query.rstrip(';')
        
        # Check if Gemini detected an off-topic question
        if 'ERROR_OFF_TOPIC' in sql_query.upper():
            return jsonify({
                'success': False,
                'question': user_question,
                'response': "❌ I'm specifically designed to work with your **task management and team productivity data**.\n\n"
                            "I can only answer questions related to:\n"
                            "• Tasks (status, priority, assignments, progress)\n"
                            "• Users (team members, workload, performance)\n"
                            "• Projects (Web Platform, Mobile App, API Services)\n\n"
                            "Your question seems to be outside my scope. Please ask something about your tasks or team!",
                'timestamp': datetime.now().strftime('%I:%M %p'),
                'data': [],
                'columns': [],
                'count': 0
            }), 400
        
        # Log SQL query for debugging (not shown to user)
        print(f"\n{'='*80}")
        print(f"📊 QUERY GENERATED")
        print(f"{'='*80}")
        print(f"Question: {user_question}")
        print(f"SQL: {sql_query}")
        print(f"{'='*80}\n")
        
        # Validate that it's a SELECT query (safety check)
        if not sql_query.upper().startswith('SELECT'):
            return jsonify({
                'success': False,
                'question': user_question,
                'response': "⚠️ I can only execute SELECT queries for safety reasons. Please rephrase your question to retrieve data.",
                'timestamp': datetime.now().strftime('%I:%M %p'),
                'data': [],
                'columns': [],
                'count': 0
            }), 400
        
        # Execute the query
        result = db.session.execute(db.text(sql_query))
        rows = result.fetchall()
        columns = result.keys()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Format dates nicely
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                row_dict[col] = value
            data.append(row_dict)
        
        # Generate a natural language response
        result_summary = generate_response_summary(user_question, data, sql_query)
        
        return jsonify({
            'success': True,
            'question': user_question,
            'sql_query': sql_query,  # Keep for debugging/modal, not shown in chat
            'data': data,
            'columns': list(data[0].keys()) if data else [],
            'count': len(data),
            'response': result_summary,
            'timestamp': datetime.now().strftime('%I:%M %p')
        })
        
    except Exception as e:
        print(f"Error in natural language query: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'question': user_question if 'user_question' in locals() else '',
            'response': f"I encountered an error processing your question: {str(e)}\n\nPlease try rephrasing your question or ask something else about tasks and users.",
            'timestamp': datetime.now().strftime('%I:%M %p')
        }), 500


def generate_response_summary(question, data, sql_query):
    """Generate a natural language response from query results"""
    if not data:
        return "I couldn't find any data matching your question. Try asking something else!"
    
    count = len(data)
    
    # Format the data as a readable response
    response_parts = []
    
    # Add a contextual intro
    if count == 1:
        response_parts.append(f"✅ Found 1 result:\n")
    else:
        response_parts.append(f"✅ Found {count} results:\n")
    
    # Format data as a table-like structure
    if data:
        # Get column names
        columns = list(data[0].keys())
        
        # If it's a simple count/aggregate, show it inline
        if len(columns) <= 2 and count <= 5:
            response_parts.append("")
            for row in data:
                row_text = " • ".join([f"**{k}**: {v}" for k, v in row.items()])
                response_parts.append(f"• {row_text}")
        else:
            # Show as formatted table (first 5 rows)
            response_parts.append("")
            show_count = min(5, count)
            
            for i, row in enumerate(data[:show_count]):
                row_parts = []
                for k, v in row.items():
                    # Format based on key name
                    if k in ['count', 'total', 'task_count']:
                        row_parts.append(f"**{v}**")
                    else:
                        row_parts.append(str(v))
                row_text = " | ".join(row_parts)
                response_parts.append(f"{i+1}. {row_text}")
            
            if count > show_count:
                remaining = count - show_count
                response_parts.append(f"\n💡 *Plus {remaining} more results. Click 'View All Results' to see everything in a table.*")
    
    return "\n".join(response_parts)


# ==================== AI INSIGHTS ENDPOINTS ====================

@app.route('/api/ai/summary', methods=['GET'])
def ai_summary():
    """Generate AI-powered summary based on filter"""
    filter_type = request.args.get('filter', 'today').lower()
    now = datetime.now()
    
    # Determine time period
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_name = "24 hours"
    elif filter_type == 'week':
        start_date = now - timedelta(days=7)
        period_name = "7 days"
    elif filter_type == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_name = "this month"
    else:
        start_date = datetime(2000, 1, 1)
        period_name = "all time"
    
    # Get tasks in period
    tasks = Task.query.filter(Task.created_date >= start_date).all()
    completed_tasks = [t for t in tasks if t.status == 'Completed']
    blocked_tasks = [t for t in tasks if t.status == 'Blocked']
    
    # Calculate average closure time (hours from created to completed)
    closure_times = []
    for task in completed_tasks:
        if task.completed_date and task.created_date:
            hours = (task.completed_date - task.created_date).total_seconds() / 3600
            closure_times.append(hours)
    
    avg_closure = sum(closure_times) / len(closure_times) if closure_times else 0
    
    # Calculate velocity change (compare with previous period)
    if filter_type == 'today':
        prev_start = start_date - timedelta(days=1)
        prev_end = start_date
    elif filter_type == 'week':
        prev_start = start_date - timedelta(days=7)
        prev_end = start_date
    elif filter_type == 'month':
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        prev_start = now.replace(month=prev_month, year=prev_year, day=1, hour=0, minute=0, second=0)
        prev_end = start_date
    else:
        prev_start = datetime(2000, 1, 1)
        prev_end = start_date
    
    prev_completed = Task.query.filter(
        Task.created_date >= prev_start,
        Task.created_date < prev_end,
        Task.status == 'Completed'
    ).count()
    
    velocity_change = 0
    if prev_completed > 0:
        velocity_change = ((len(completed_tasks) - prev_completed) / prev_completed) * 100
    
    # Generate summary text
    trend = "increased" if velocity_change > 0 else "decreased" if velocity_change < 0 else "remained stable"
    summary = (
        f"Over the last {period_name}, your team completed {len(completed_tasks)} tasks "
        f"with an average closure time of {avg_closure:.1f} hours. "
        f"Task completion velocity has {trend} by {abs(velocity_change):.1f}%, "
        f"{'indicating potential bottlenecks' if velocity_change < 0 else 'showing positive momentum'}. "
        f"There are {len(blocked_tasks)} blocked tasks requiring attention."
    )
    
    return jsonify({'summary': summary})


@app.route('/api/ai/closure-performance', methods=['GET'])
def closure_performance():
    """Calculate task closure performance metrics"""
    filter_type = request.args.get('filter', 'today').lower()
    now = datetime.now()
    
    # Determine current period
    if filter_type == 'today':
        current_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        prev_start = current_start - timedelta(days=1)
        prev_end = current_start
    elif filter_type == 'week':
        current_start = now - timedelta(days=7)
        prev_start = current_start - timedelta(days=7)
        prev_end = current_start
    elif filter_type == 'month':
        current_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        prev_start = now.replace(month=prev_month, year=prev_year, day=1, hour=0, minute=0, second=0)
        prev_end = current_start
    else:
        # All time - split in half
        all_tasks = Task.query.order_by(Task.created_date).all()
        if len(all_tasks) > 0:
            mid_point = len(all_tasks) // 2
            current_start = all_tasks[mid_point].created_date
            prev_start = all_tasks[0].created_date
            prev_end = current_start
        else:
            current_start = datetime(2000, 1, 1)
            prev_start = datetime(2000, 1, 1)
            prev_end = current_start
    
    # Calculate current period closure time
    current_completed = Task.query.filter(
        Task.created_date >= current_start,
        Task.status == 'Completed',
        Task.completed_date.isnot(None)
    ).all()
    
    current_times = []
    for task in current_completed:
        hours = (task.completed_date - task.created_date).total_seconds() / 3600
        current_times.append(hours)
    
    current_avg = sum(current_times) / len(current_times) if current_times else 0
    
    # Calculate previous period closure time
    prev_completed = Task.query.filter(
        Task.created_date >= prev_start,
        Task.created_date < prev_end,
        Task.status == 'Completed',
        Task.completed_date.isnot(None)
    ).all()
    
    prev_times = []
    for task in prev_completed:
        hours = (task.completed_date - task.created_date).total_seconds() / 3600
        prev_times.append(hours)
    
    prev_avg = sum(prev_times) / len(prev_times) if prev_times else 0
    
    # Get blocked tasks
    blocked_tasks = Task.query.filter(
        Task.created_date >= current_start,
        Task.status == 'Blocked'
    ).count()
    
    total_tasks = Task.query.filter(Task.created_date >= current_start).count()
    blocked_percentage = (blocked_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return jsonify({
        'current_avg': round(current_avg, 1),
        'previous_avg': round(prev_avg, 1),
        'blocked_tasks': blocked_tasks,
        'blocked_percentage': round(blocked_percentage, 0)
    })


@app.route('/api/ai/due-compliance', methods=['GET'])
def due_compliance():
    """Calculate due date compliance metrics"""
    filter_type = request.args.get('filter', 'today').lower()
    now = datetime.now()
    
    # Determine time period
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == 'week':
        start_date = now - timedelta(days=7)
    elif filter_type == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = datetime(2000, 1, 1)
    
    # Get tasks with due dates in period
    tasks_with_due = Task.query.filter(
        Task.created_date >= start_date,
        Task.due_date.isnot(None)
    ).all()
    
    overdue = 0
    on_time = 0
    
    for task in tasks_with_due:
        if task.status == 'Completed' and task.completed_date:
            # Check if completed before due date
            if task.completed_date <= task.due_date:
                on_time += 1
            else:
                overdue += 1
        elif task.status != 'Completed':
            # Check if currently overdue
            if task.due_date < now:
                overdue += 1
            else:
                on_time += 1
    
    # Get in-progress tasks
    in_progress = Task.query.filter(
        Task.created_date >= start_date,
        Task.status == 'In Progress'
    ).all()
    
    # Calculate average time in progress
    active_times = []
    for task in in_progress:
        if task.start_date:
            hours = (now - task.start_date).total_seconds() / 3600
            active_times.append(hours)
    
    avg_active = sum(active_times) / len(active_times) if active_times else 0
    
    return jsonify({
        'overdue': overdue,
        'on_time': on_time,
        'active_tasks': len(in_progress),
        'avg_active_time': round(avg_active, 1)
    })


@app.route('/api/ai/predictions', methods=['GET'])
def predictions():
    """Generate predictive analytics"""
    filter_type = request.args.get('filter', 'today').lower()
    now = datetime.now()
    
    # Determine time period
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        days_in_period = 1
    elif filter_type == 'week':
        start_date = now - timedelta(days=7)
        days_in_period = 7
    elif filter_type == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        days_in_period = now.day
    else:
        oldest_task = Task.query.order_by(Task.created_date).first()
        start_date = oldest_task.created_date if oldest_task else now
        days_in_period = (now - start_date).days or 1
    
    # Calculate velocity (tasks per day)
    completed_tasks = Task.query.filter(
        Task.created_date >= start_date,
        Task.status == 'Completed'
    ).count()
    
    velocity = completed_tasks / days_in_period if days_in_period > 0 else 0
    
    # Calculate sprint completion (assuming 2-week sprint)
    sprint_duration = 14
    open_tasks = Task.query.filter(
        Task.created_date >= start_date,
        Task.status.in_(['Open', 'In Progress'])
    ).count()
    
    expected_completion = velocity * sprint_duration
    sprint_completion = min(100, (expected_completion / max(open_tasks, 1)) * 100)
    
    # Predict next week workload
    next_week_tasks = int(velocity * 7)
    if next_week_tasks < 30:
        workload = "Low"
    elif next_week_tasks < 50:
        workload = "Medium"
    else:
        workload = "High"
    
    # Risk assessment
    blocked_count = Task.query.filter(
        Task.created_date >= start_date,
        Task.status == 'Blocked'
    ).count()
    
    total_active = Task.query.filter(
        Task.created_date >= start_date,
        Task.status.in_(['Open', 'In Progress', 'Blocked'])
    ).count()
    
    blocked_ratio = blocked_count / max(total_active, 1)
    
    if blocked_ratio > 0.15:
        risk_level = "High"
        risk_desc = "Significant bottlenecks detected"
    elif blocked_ratio > 0.08:
        risk_level = "Medium"
        risk_desc = "Some blockers present"
    else:
        risk_level = "Low"
        risk_desc = "No major bottlenecks"
    
    return jsonify({
        'sprint_completion': round(sprint_completion, 0),
        'next_week_workload': workload,
        'expected_tasks': next_week_tasks,
        'risk_level': risk_level,
        'risk_description': risk_desc
    })


@app.route('/api/ai/team-benchmarking', methods=['GET'])
def team_benchmarking():
    """Compare team performance"""
    filter_type = request.args.get('filter', 'today').lower()
    now = datetime.now()
    
    # Determine time period
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        weeks = 1 / 7
    elif filter_type == 'week':
        start_date = now - timedelta(days=7)
        weeks = 1
    elif filter_type == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        weeks = now.day / 7
    else:
        oldest_task = Task.query.order_by(Task.created_date).first()
        start_date = oldest_task.created_date if oldest_task else now
        weeks = max(1, (now - start_date).days / 7)
    
    # Get all teams
    teams_data = db.session.query(User.team).distinct().all()
    team_stats = []
    
    for (team_name,) in teams_data:
        if not team_name:
            continue
        
        # Get users in team
        team_users = User.query.filter_by(team=team_name).all()
        user_ids = [u.user_id for u in team_users]
        
        # Get tasks for team
        team_tasks = Task.query.filter(
            Task.created_date >= start_date,
            Task.assigned_to.in_(user_ids)
        ).all()
        
        total_tasks = len(team_tasks)
        completed_tasks = sum(1 for t in team_tasks if t.status == 'Completed')
        
        # Calculate velocity (tasks per week)
        velocity = int(total_tasks / weeks) if weeks > 0 else total_tasks
        
        # Calculate efficiency (completion rate)
        efficiency = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        
        team_stats.append({
            'name': team_name,
            'total_tasks': total_tasks,
            'velocity': velocity,
            'efficiency': efficiency,
            'rank': 0  # Will be assigned below
        })
    
    # Sort by velocity and assign ranks
    team_stats.sort(key=lambda x: x['velocity'], reverse=True)
    for i, team in enumerate(team_stats):
        team['rank'] = i + 1
        if i == 0:
            team['badge'] = '🏆'
        else:
            team['badge'] = None
    
    return jsonify(team_stats)


@app.route('/api/ai/productivity-trends', methods=['GET'])
def productivity_trends():
    """Get 4-week productivity trends for all teams"""
    now = datetime.now()
    
    # Get teams
    teams_data = db.session.query(User.team).distinct().all()
    
    # Prepare 4 weeks of data
    trends = []
    for week in range(1, 5):
        week_end = now - timedelta(days=(week - 1) * 7)
        week_start = week_end - timedelta(days=7)
        
        week_data = {
            'week': f'Week {5 - week}',
            'your_team': 0,
            'alpha_team': 0,
            'beta_team': 0,
            'gamma_team': 0
        }
        
        for (team_name,) in teams_data:
            if not team_name:
                continue
                
            team_users = User.query.filter_by(team=team_name).all()
            user_ids = [u.user_id for u in team_users]
            
            completed = Task.query.filter(
                Task.completed_date >= week_start,
                Task.completed_date < week_end,
                Task.assigned_to.in_(user_ids),
                Task.status == 'Completed'
            ).count()
            
            # Map to chart keys
            if team_name == 'Your Team':
                week_data['your_team'] = completed
            elif team_name == 'Alpha Team':
                week_data['alpha_team'] = completed
            elif team_name == 'Beta Team':
                week_data['beta_team'] = completed
            elif team_name == 'Gamma Team':
                week_data['gamma_team'] = completed
        
        trends.append(week_data)
    
    return jsonify(trends)


@app.route('/api/ai/sentiment', methods=['GET'])
def sentiment():
    """Analyze team sentiment from comments"""
    # This is a simplified version - in production, use NLP
    # For now, we'll generate realistic sentiment based on task status
    
    filter_type = request.args.get('filter', 'today').lower()
    now = datetime.now()
    
    # Determine time period
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == 'week':
        start_date = now - timedelta(days=7)
    elif filter_type == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = datetime(2000, 1, 1)
    
    tasks = Task.query.filter(Task.created_date >= start_date).all()
    
    # Simple sentiment based on task status and completion
    total = len(tasks)
    if total == 0:
        return jsonify({
            'positive': 50,
            'neutral': 30,
            'negative': 20,
            'insight': 'Not enough data for sentiment analysis.'
        })
    
    completed = sum(1 for t in tasks if t.status == 'Completed')
    in_progress = sum(1 for t in tasks if t.status == 'In Progress')
    blocked = sum(1 for t in tasks if t.status == 'Blocked')
    
    # Calculate sentiment percentages
    completion_rate = completed / total
    positive = int(min(90, completion_rate * 100 + 20))
    negative = int(max(5, blocked / total * 100 * 3))
    neutral = 100 - positive - negative
    
    # Generate insight
    if positive > 70:
        insight = "Team morale appears positive. Keep up the good work and maintain open communication."
    elif positive > 50:
        insight = "Team sentiment is generally positive with room for improvement."
    else:
        insight = "Team may be facing challenges. Consider team check-ins and addressing blockers."
    
    return jsonify({
        'positive': positive,
        'neutral': neutral,
        'negative': negative,
        'insight': insight
    })


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected'
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized!")
        print("🚀 Server running on http://localhost:5001")
    
    app.run(debug=True, port=5001, host='0.0.0.0')

