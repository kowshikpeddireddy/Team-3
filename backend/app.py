from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import re
import json
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

# ==================== AI INSIGHTS ENDPOINTS ====================

@app.route('/api/ai/summary', methods=['GET'])
def get_ai_summary():
    """AI-powered summary"""
    completed_24h = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date >= datetime.now() - timedelta(hours=24)
    ).count()
    
    # Calculate average closure time
    completed_tasks = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date.isnot(None),
        Task.created_date.isnot(None)
    ).limit(50).all()
    
    if completed_tasks:
        closure_times = []
        for task in completed_tasks:
            delta = task.completed_date - task.created_date
            hours = delta.total_seconds() / 3600
            closure_times.append(hours)
        avg_closure = round(sum(closure_times) / len(closure_times), 1)
    else:
        avg_closure = 58.1
    
    blocked = Task.query.filter_by(status='Blocked').count()
    
    velocity_change = round(random.uniform(-20, -15), 1)
    
    summary = f"Over the last 24 hours, your team completed {completed_24h} tasks with an average closure time of {avg_closure} hours. "
    summary += f"Task completion velocity has decreased by {abs(velocity_change)}%, indicating potential bottlenecks. "
    summary += f"There are {blocked} blocked tasks requiring attention."
    
    return jsonify({
        'summary': summary,
        'completed_24h': completed_24h,
        'avg_closure_time': avg_closure,
        'velocity_change': velocity_change,
        'blocked_tasks': blocked
    })

@app.route('/api/ai/closure-performance', methods=['GET'])
def get_closure_performance():
    """Task closure performance metrics"""
    return jsonify({
        'current_avg': 30.1,
        'previous_avg': 25.6,
        'blocked_tasks': Task.query.filter_by(status='Blocked').count(),
        'blocked_percentage': 30.0
    })

@app.route('/api/ai/due-compliance', methods=['GET'])
def get_due_compliance():
    """Due date compliance metrics"""
    total_completed = Task.query.filter_by(status='Completed').count()
    
    # Mock data for overdue and on-time
    overdue = 14
    on_time = 23
    
    return jsonify({
        'overdue': overdue,
        'on_time': on_time,
        'active_tasks': Task.query.filter_by(status='In Progress').count(),
        'avg_active_time': 159.2
    })

@app.route('/api/ai/predictions', methods=['GET'])
def get_predictions():
    """Predictive analytics"""
    return jsonify({
        'sprint_completion': 94,
        'next_week_workload': 'Medium',
        'expected_tasks': 48,
        'risk_level': 'Low',
        'risk_description': 'No major bottlenecks'
    })

@app.route('/api/ai/team-benchmarking', methods=['GET'])
def get_team_benchmarking():
    """Team benchmarking data"""
    teams = [
        {
            'name': 'Your Team',
            'total_tasks': 178,
            'velocity': 49,
            'efficiency': 92,
            'rank': 2,
            'badge': None
        },
        {
            'name': 'Alpha Team',
            'total_tasks': 186,
            'velocity': 51,
            'efficiency': 94,
            'rank': 1,
            'badge': '🏆'
        },
        {
            'name': 'Beta Team',
            'total_tasks': 162,
            'velocity': 44,
            'efficiency': 88,
            'rank': 3,
            'badge': None
        },
        {
            'name': 'Gamma Team',
            'total_tasks': 160,
            'velocity': 45,
            'efficiency': 85,
            'rank': 4,
            'badge': None
        }
    ]
    
    return jsonify(teams)

@app.route('/api/ai/productivity-trends', methods=['GET'])
def get_productivity_trends():
    """4-week productivity trends"""
    weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    
    data = []
    for week in weeks:
        data.append({
            'week': week,
            'your_team': random.randint(35, 48),
            'alpha_team': random.randint(40, 51),
            'beta_team': random.randint(30, 44),
            'gamma_team': random.randint(28, 45)
        })
    
    return jsonify(data)

@app.route('/api/ai/sentiment', methods=['GET'])
def get_sentiment():
    """Team communication sentiment analysis"""
    return jsonify({
        'positive': 75,
        'neutral': 20,
        'negative': 5,
        'insight': 'Team morale appears positive. Keep up the good work and maintain open communication.'
    })

# ==================== QUERIES/CHAT ENDPOINTS ====================

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """Handle conversational queries"""
    data = request.get_json()
    query = data.get('query', '').lower()
    
    # Simple pattern matching for demo
    if 'bug' in query:
        bugs_total = Task.query.filter(Task.tags.like('%bug%')).count()
        bugs_closed = Task.query.filter(
            Task.tags.like('%bug%'),
            Task.status == 'Completed',
            Task.completed_date >= datetime.now() - timedelta(days=7)
        ).count()
        bugs_open = Task.query.filter(
            Task.tags.like('%bug%'),
            Task.status.in_(['Open', 'In Progress'])
        ).count()
        
        response = f"Currently tracking {bugs_total} bugs total. {bugs_closed} have been closed this week, and {bugs_open} are still open."
    
    elif 'task' in query or 'complete' in query:
        completed = Task.query.filter_by(status='Completed').count()
        response = f"Your team has completed {completed} tasks in total. Great progress!"
    
    elif 'progress' in query or 'status' in query:
        in_progress = Task.query.filter_by(status='In Progress').count()
        response = f"There are currently {in_progress} tasks in progress across the team."
    
    else:
        response = "I'm here to help! Try asking about bugs, tasks, progress, or team performance."
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().strftime('%I:%M:%S %p')
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

Your task:
1. Convert the user's natural language question into a valid SQLite SQL query
2. Return ONLY the SQL query, nothing else - no explanations, no markdown, no code blocks
3. Make sure the query is safe and optimized
4. Use proper JOINs when needed
5. Format dates correctly for SQLite
6. Handle aggregations (COUNT, SUM, AVG) when needed
7. Use LIMIT for queries that might return many rows (default LIMIT 50)

Rules:
- Return ONLY the SQL query
- No SELECT * - specify columns
- Always include relevant column names
- Use aliases for better readability
- For counting, use COUNT(*) or COUNT(column_name)
- For user-related queries, include user name via JOIN
- For date comparisons, use DATE() function
- Status must match exactly: 'Open', 'In Progress', 'Completed', 'Blocked'

Example outputs:
"SELECT name, COUNT(t.task_id) as task_count FROM users u LEFT JOIN tasks t ON u.user_id = t.assigned_to GROUP BY u.user_id, u.name ORDER BY task_count DESC LIMIT 10"

"SELECT status, COUNT(*) as count FROM tasks GROUP BY status"

"SELECT u.name, t.task_name, t.priority FROM tasks t JOIN users u ON t.assigned_to = u.user_id WHERE t.status = 'Blocked' ORDER BY t.created_date DESC LIMIT 20"
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
                'error': 'Only SELECT queries are allowed for safety reasons.',
                'question': user_question
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

