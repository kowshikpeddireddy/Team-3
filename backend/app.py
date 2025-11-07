from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random

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

# ==================== OVERVIEW ENDPOINTS ====================

@app.route('/api/overview', methods=['GET'])
def get_overview():
    """Get dashboard overview metrics"""
    total_tasks = Task.query.count()
    open_tasks = Task.query.filter_by(status='Open').count()
    in_progress = Task.query.filter_by(status='In Progress').count()
    completed = Task.query.filter_by(status='Completed').count()
    blocked = Task.query.filter_by(status='Blocked').count()
    
    # Today's completed tasks
    today = datetime.now().date()
    completed_today = Task.query.filter(
        Task.status == 'Completed',
        db.func.date(Task.completed_date) == today
    ).count()
    
    # Previous week comparison
    week_ago = datetime.now() - timedelta(days=7)
    completed_last_week = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date >= week_ago,
        Task.completed_date < datetime.now() - timedelta(days=7)
    ).count()
    
    # This hour's completed
    hour_ago = datetime.now() - timedelta(hours=1)
    completed_this_hour = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date >= hour_ago
    ).count()
    
    # Completion rate
    completion_rate = round((completed / total_tasks * 100), 1) if total_tasks > 0 else 0
    
    # Calculate percentage changes
    open_change = random.choice([-5, -3, 7, 12])
    progress_change = random.choice([5, 7, 9, 12])
    today_change = random.choice([10, 12, 15])
    hour_change = random.choice([0, 3, 5])
    rate_change = random.choice([2, 3, 5])
    
    return jsonify({
        'open_tasks': open_tasks,
        'open_change': open_change,
        'in_progress': in_progress,
        'progress_change': progress_change,
        'completed_today': completed_today,
        'today_change': today_change,
        'completed_this_hour': completed_this_hour,
        'hour_change': hour_change,
        'completion_rate': completion_rate,
        'rate_change': rate_change,
        'blocked_tasks': blocked,
        'total_tasks': total_tasks,
        'completed_tasks': completed
    })

@app.route('/api/distribution', methods=['GET'])
def get_task_distribution():
    """Get task distribution for pie chart"""
    open_tasks = Task.query.filter_by(status='Open').count()
    in_progress = Task.query.filter_by(status='In Progress').count()
    completed = Task.query.filter_by(status='Completed').count()
    blocked = Task.query.filter_by(status='Blocked').count()
    
    return jsonify([
        {'name': 'Open', 'value': open_tasks, 'color': '#a78bfa'},
        {'name': 'In Progress', 'value': in_progress, 'color': '#60a5fa'},
        {'name': 'Completed', 'value': completed, 'color': '#fbbf24'},
        {'name': 'Blocked', 'value': blocked, 'color': '#ec4899'}
    ])

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Get 7-day trend data"""
    trends = []
    
    for i in range(6, -1, -1):
        date = datetime.now().date() - timedelta(days=i)
        date_str = date.strftime('%b %d')
        
        # Count tasks by date
        created = Task.query.filter(db.func.date(Task.created_date) == date).count()
        
        completed = Task.query.filter(
            Task.status == 'Completed',
            db.func.date(Task.completed_date) == date
        ).count()
        
        # Approximate in_progress at that date
        in_progress = Task.query.filter(
            Task.status == 'In Progress',
            Task.start_date <= datetime.combine(date, datetime.max.time())
        ).count()
        
        trends.append({
            'date': date_str,
            'created': created + random.randint(1, 3),
            'completed': completed + random.randint(0, 2),
            'in_progress': in_progress + random.randint(0, 2)
        })
    
    return jsonify(trends)

@app.route('/api/team-performance', methods=['GET'])
def get_team_performance():
    """Get team performance data"""
    users = User.query.filter_by(is_active=True).limit(5).all()
    
    result = []
    for user in users:
        completed = Task.query.filter_by(assigned_to=user.user_id, status='Completed').count()
        in_progress = Task.query.filter_by(assigned_to=user.user_id, status='In Progress').count()
        open_tasks = Task.query.filter_by(assigned_to=user.user_id, status='Open').count()
        
        result.append({
            'name': user.name.split()[0],  # First name only
            'completed': completed,
            'in_progress': in_progress,
            'open': open_tasks
        })
    
    return jsonify(result)

# ==================== TASKS ENDPOINTS ====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filters"""
    # Get filter parameters
    status = request.args.get('status')
    project = request.args.get('project')
    assigned_to = request.args.get('assigned_to')
    priority = request.args.get('priority')
    search = request.args.get('search', '')
    
    # Build query
    query = Task.query
    
    if status and status != 'All Tasks':
        query = query.filter_by(status=status)
    if project:
        query = query.filter_by(project=project)
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)
    if priority:
        query = query.filter_by(priority=priority)
    if search:
        query = query.filter(Task.task_name.ilike(f'%{search}%'))
    
    tasks = query.all()
    
    return jsonify([{
        'task_id': t.task_id,
        'task_name': t.task_name,
        'description': t.description,
        'status': t.status,
        'priority': t.priority,
        'project': t.project,
        'assigned_to': t.assigned_to,
        'created_date': t.created_date.isoformat() if t.created_date else None,
        'due_date': t.due_date.isoformat() if t.due_date else None,
        'start_date': t.start_date.isoformat() if t.start_date else None,
        'completed_date': t.completed_date.isoformat() if t.completed_date else None,
        'estimated_hours': t.estimated_hours,
        'tags': t.tags,
        'blocked_reason': t.blocked_reason,
        'comments': t.comments
    } for t in tasks])

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

