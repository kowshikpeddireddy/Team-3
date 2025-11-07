from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random
from sqlalchemy import func as sa_func, case, and_ # <-- Added 'and_' import

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
#
# ----- UPDATED DYNAMIC AI FUNCTIONS START HERE -----
#

@app.route('/api/ai/summary', methods=['GET'])
def get_ai_summary():
    """AI-powered summary (DYNAMIC)"""
    now = datetime.now()
    
    # Completed in last 24h
    completed_24h = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date >= now - timedelta(hours=24)
    ).count()
    
    # Average closure time (using last 50 completed tasks)
    completed_tasks = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date.isnot(None),
        Task.created_date.isnot(None)
    ).order_by(Task.completed_date.desc()).limit(50).all()
    
    avg_closure = 0.0
    if completed_tasks:
        closure_times = []
        for task in completed_tasks:
            delta = task.completed_date - task.created_date
            hours = delta.total_seconds() / 3600
            closure_times.append(hours)
        if closure_times:
            avg_closure = round(sum(closure_times) / len(closure_times), 1)

    # Blocked tasks
    blocked = Task.query.filter_by(status='Blocked').count()
    
    # Velocity Change (Last 7 days vs. Previous 7 days)
    completed_last_week = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date >= now - timedelta(days=7)
    ).count()
    
    completed_prev_week = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date >= (now - timedelta(days=14)),
        Task.completed_date < (now - timedelta(days=7))
    ).count()
    
    velocity_change = 0.0
    if completed_prev_week > 0:
        velocity_change = round(((completed_last_week - completed_prev_week) / completed_prev_week * 100), 1)
    elif completed_last_week > 0:
        velocity_change = 100.0 # From 0 to >0 is 100% (or infinite) change
        
    # Build summary string
    summary = f"Over the last 24 hours, your team completed {completed_24h} tasks with an average closure time of {avg_closure} hours. "
    
    if velocity_change > 0:
        summary += f"Task completion velocity has increased by {velocity_change}%. "
    elif velocity_change < 0:
        summary += f"Task completion velocity has decreased by {abs(velocity_change)}%. "
    else:
        summary += "Task completion velocity is stable. "
        
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
    """Task closure performance metrics (DYNAMIC)"""
    
    # --- Current Period (Last 30 days) ---
    now = datetime.now()
    current_start = now - timedelta(days=30)
    
    completed_current = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date >= current_start,
        Task.created_date.isnot(None)
    ).all()
    
    current_avg_val = 0.0
    if completed_current:
        closure_times = [(t.completed_date - t.created_date).total_seconds() / 3600 for t in completed_current]
        if closure_times:
            current_avg_val = round(sum(closure_times) / len(closure_times), 1)

    # --- Previous Period (30-60 days ago) ---
    previous_start = now - timedelta(days=60)
    previous_end = current_start
    
    completed_previous = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date >= previous_start,
        Task.completed_date < previous_end,
        Task.created_date.isnot(None)
    ).all()

    previous_avg_val = 0.0
    if completed_previous:
        closure_times_prev = [(t.completed_date - t.created_date).total_seconds() / 3600 for t in completed_previous]
        if closure_times_prev:
            previous_avg_val = round(sum(closure_times_prev) / len(closure_times_prev), 1)

    # --- Blocked Stats ---
    blocked_count = Task.query.filter_by(status='Blocked').count()
    total_tasks = Task.query.count()
    blocked_perc = round((blocked_count / total_tasks * 100), 1) if total_tasks > 0 else 0
    
    return jsonify({
        'current_avg': current_avg_val,
        'previous_avg': previous_avg_val,
        'blocked_tasks': blocked_count,
        'blocked_percentage': blocked_perc
    })

@app.route('/api/ai/due-compliance', methods=['GET'])
def get_due_compliance():
    """Due date compliance metrics (DYNAMIC)"""
    now = datetime.now()
    
    # Overdue tasks (completed after due date)
    overdue_count = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date.isnot(None),
        Task.due_date.isnot(None),
        Task.completed_date > Task.due_date
    ).count()
    
    # On-time tasks (completed on or before due date)
    on_time_count = Task.query.filter(
        Task.status == 'Completed',
        Task.completed_date.isnot(None),
        Task.due_date.isnot(None),
        Task.completed_date <= Task.due_date
    ).count()
    
    # Active tasks and their average time
    active_tasks_list = Task.query.filter(
        Task.status == 'In Progress',
        Task.start_date.isnot(None)
    ).all()
    
    active_tasks_count = len(active_tasks_list)
    avg_active_time_val = 0.0
    
    if active_tasks_list:
        active_times = [(now - t.start_date).total_seconds() / 3600 for t in active_tasks_list]
        avg_active_time_val = round(sum(active_times) / len(active_times), 1)
    
    return jsonify({
        'overdue': overdue_count,
        'on_time': on_time_count,
        'active_tasks': active_tasks_count,
        'avg_active_time': avg_active_time_val
    })

@app.route('/api/ai/predictions', methods=['GET'])
def get_predictions():
    """Predictive analytics (Data-driven mock)"""
    now = datetime.now()
    
    # --- Sprint Completion (e.g., tasks due in last 2 weeks) ---
    sprint_start = now - timedelta(days=14)
    sprint_tasks_query = Task.query.filter(Task.due_date >= sprint_start, Task.due_date <= now)
    
    total_sprint_tasks = sprint_tasks_query.count()
    completed_sprint_tasks = sprint_tasks_query.filter(Task.status == 'Completed').count()
    
    sprint_completion_perc = 0
    if total_sprint_tasks > 0:
        sprint_completion_perc = round((completed_sprint_tasks / total_sprint_tasks * 100))

    # --- Next Week Workload (based on new tasks created) ---
    tasks_created_last_week = Task.query.filter(Task.created_date >= (now - timedelta(days=7))).count()
    
    workload = 'Low'
    expected_tasks = 20
    if tasks_created_last_week > 15: # Adjust these thresholds
        workload = 'Medium'
        expected_tasks = 35
    if tasks_created_last_week > 30:
        workload = 'High'
        expected_tasks = 50 # <-- FIXED SYNTAX ERROR HERE (was 50+)

    # --- Risk Level (based on blocked tasks) ---
    blocked_tasks_count = Task.query.filter_by(status='Blocked').count()
    risk = 'Low'
    risk_desc = 'No major bottlenecks'
    if blocked_tasks_count > 5:
        risk = 'Medium'
        risk_desc = f'{blocked_tasks_count} tasks are blocked, investigate.'
    if blocked_tasks_count > 10:
        risk = 'High'
        risk_desc = f'High number of blocked tasks ({blocked_tasks_count})!'
    
    return jsonify({
        'sprint_completion': sprint_completion_perc,
        'next_week_workload': workload,
        'expected_tasks': expected_tasks,
        'risk_level': risk,
        'risk_description': risk_desc
    })

@app.route('/api/ai/team-benchmarking', methods=['GET'])
def get_team_benchmarking():
    """Team benchmarking data (DYNAMIC)"""
    now = datetime.now()
    four_weeks_ago = now - timedelta(weeks=4)
    
    # Join User and Task, group by team, and calculate aggregates
    team_stats = db.session.query(
        User.team,
        sa_func.count(Task.task_id).label('total_tasks'),
        
        sa_func.sum(
            case((Task.status == 'Completed', 1), else_=0)
        ).label('total_completed'),
        
        # --- FIXED VALUEERROR HERE ---
        # Used and_() to combine conditions into one tuple: (condition, result)
        sa_func.sum(
            case(
                (and_(Task.status == 'Completed', Task.completed_date >= four_weeks_ago), 1),
                else_=0
            )
        ).label('velocity_tasks'),
        
        # --- FIXED VALUEERROR HERE ---
        # Used and_() and added check for due_date to prevent errors
        sa_func.sum(
            case(
                (and_(Task.status == 'Completed', Task.due_date.isnot(None), Task.completed_date <= Task.due_date), 1),
                else_=0
            )
        ).label('on_time_tasks')
        
    ).join(Task, User.user_id == Task.assigned_to).filter(User.team.isnot(None)).group_by(User.team).all()
    
    result = []
    for stat in team_stats:
        velocity = round(stat.velocity_tasks / 4, 1) # Tasks per week
        # Check for zero division error
        efficiency = round((stat.on_time_tasks / stat.total_completed * 100), 1) if stat.total_completed > 0 else 0
        
        result.append({
            'name': stat.team,
            'total_tasks': stat.total_tasks,
            'velocity': velocity,
            'efficiency': efficiency,
            'badge': None
        })
    
    # Sort by velocity to determine rank
    result_sorted = sorted(result, key=lambda x: x['velocity'], reverse=True)
    
    final_teams = []
    for i, team in enumerate(result_sorted, 1):
        team['rank'] = i
        if i == 1:
            team['badge'] = '🏆'
        final_teams.append(team)
        
    return jsonify(final_teams)

@app.route('/api/ai/productivity-trends', methods=['GET'])
def get_productivity_trends():
    """4-week productivity trends (DYNAMIC)"""
    now = datetime.now()
    
    # Define the 4 weeks
    weeks = {
        'Week 4': (now - timedelta(weeks=1), now), # Last 7 days
        'Week 3': (now - timedelta(weeks=2), now - timedelta(weeks=1)),
        'Week 2': (now - timedelta(weeks=3), now - timedelta(weeks=2)),
        'Week 1': (now - timedelta(weeks=4), now - timedelta(weeks=3)),
    }
    
    # Frontend keys are hardcoded, so we must map them
    key_mapping = {
        'Your Team': 'your_team',
        'Alpha Team': 'alpha_team',
        'Beta Team': 'beta_team',
        'Gamma Team': 'gamma_team'
    }
    
    # Initialize data structure
    trends_data = {}
    for week_name in weeks.keys():
        trends_data[week_name] = {'week': week_name}
        for fe_key in key_mapping.values():
            trends_data[week_name][fe_key] = 0

    # Query the database for each week
    for week_name, (start_date, end_date) in weeks.items():
        tasks_in_week = db.session.query(
            User.team,
            sa_func.count(Task.task_id).label('completed_count')
        ).join(Task, User.user_id == Task.assigned_to).filter(
            Task.status == 'Completed',
            Task.completed_date >= start_date,
            Task.completed_date < end_date,
            User.team.in_(key_mapping.keys())
        ).group_by(User.team).all()
        
        for team_result in tasks_in_week:
            fe_key = key_mapping.get(team_result.team)
            if fe_key:
                trends_data[week_name][fe_key] = team_result.completed_count
    
    # Convert dict to the list format the frontend expects
    final_trends = [trends_data['Week 1'], trends_data['Week 2'], trends_data['Week 3'], trends_data['Week 4']]
            
    return jsonify(final_trends)

@app.route('/api/ai/sentiment', methods=['GET'])
def get_sentiment():
    """Team communication sentiment analysis (MOCK)"""
    # NOTE: Real sentiment analysis requires a Natural Language Processing (NLP)
    # library (like NLTK or spaCy) to analyze task comments.
    # This remains a placeholder mock.
    return jsonify({
        'positive': 75,
        'neutral': 20,
        'negative': 5,
        'insight': 'Team morale appears positive. Keep up the good work and maintain open communication.'
    })

#
# ----- UPDATED DYNAMIC AI FUNCTIONS END HERE -----
#
# =========================================================


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