"""
Generate realistic sample data for PULSEVO dashboard
"""
from app import app, db
from models import User, Task
from datetime import datetime, timedelta
import random

def clear_data():
    """Clear existing data"""
    with app.app_context():
        Task.query.delete()
        User.query.delete()
        db.session.commit()
        print("✅ Cleared existing data")

def generate_users():
    """Generate sample users"""
    users_data = [
        {'name': 'Alice Johnson', 'role': 'Frontend Developer', 'team': 'Your Team'},
        {'name': 'Bob Smith', 'role': 'Backend Developer', 'team': 'Your Team'},
        {'name': 'Carol Davis', 'role': 'UX Designer', 'team': 'Your Team'},
        {'name': 'David Lee', 'role': 'Full Stack Developer', 'team': 'Your Team'},
        {'name': 'Emma Wilson', 'role': 'DevOps Engineer', 'team': 'Your Team'},
        {'name': 'Frank Martinez', 'role': 'QA Engineer', 'team': 'Your Team'},
        {'name': 'Grace Chen', 'role': 'Product Manager', 'team': 'Alpha Team'},
        {'name': 'Henry Taylor', 'role': 'Backend Developer', 'team': 'Alpha Team'},
        {'name': 'Iris Anderson', 'role': 'Frontend Developer', 'team': 'Beta Team'},
        {'name': 'Shane Williams', 'role': 'Full Stack Developer', 'team': 'Beta Team'},
        {'name': 'Georgia Lopez', 'role': 'DevOps Engineer', 'team': 'Gamma Team'},
    ]
    
    users = []
    with app.app_context():
        for idx, user_data in enumerate(users_data, 1):
            # Create initials
            name_parts = user_data['name'].split()
            initials = ''.join([part[0] for part in name_parts])
            
            user = User(
                user_id=f'USER-{idx:03d}',
                name=user_data['name'],
                email=f"{user_data['name'].lower().replace(' ', '.')}@company.com",
                initials=initials,
                role=user_data['role'],
                team=user_data['team'],
                is_active=True
            )
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        print(f"✅ Created {len(users)} users")
        return users

def generate_tasks():
    """Generate sample tasks"""
    
    task_templates = [
        # Web Platform tasks
        {'name': 'Implement user authentication flow', 'project': 'Web Platform', 'priority': 'High', 'tags': 'authentication,security'},
        {'name': 'Fix responsive design on mobile', 'project': 'Web Platform', 'priority': 'High', 'tags': 'bug,ui,mobile'},
        {'name': 'Add dark mode support', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'feature,ui'},
        {'name': 'Optimize image loading performance', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'performance,optimization'},
        {'name': 'Update homepage hero section', 'project': 'Web Platform', 'priority': 'Low', 'tags': 'ui,content'},
        {'name': 'Integrate analytics tracking', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'analytics,feature'},
        {'name': 'Fix navigation menu bug', 'project': 'Web Platform', 'priority': 'High', 'tags': 'bug,navigation'},
        {'name': 'Add email notifications', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'feature,notifications'},
        {'name': 'Implement search functionality', 'project': 'Web Platform', 'priority': 'High', 'tags': 'feature,search'},
        {'name': 'Update terms of service page', 'project': 'Web Platform', 'priority': 'Low', 'tags': 'content,legal'},
        
        # Mobile App tasks
        {'name': 'Fix crash on iOS 16', 'project': 'Mobile App', 'priority': 'High', 'tags': 'bug,ios,crash'},
        {'name': 'Implement push notifications', 'project': 'Mobile App', 'priority': 'High', 'tags': 'feature,notifications'},
        {'name': 'Add biometric authentication', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'feature,security'},
        {'name': 'Optimize battery usage', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'performance,optimization'},
        {'name': 'Update app icon and splash screen', 'project': 'Mobile App', 'priority': 'Low', 'tags': 'ui,branding'},
        {'name': 'Fix camera permission issue', 'project': 'Mobile App', 'priority': 'High', 'tags': 'bug,permissions'},
        {'name': 'Add offline mode support', 'project': 'Mobile App', 'priority': 'High', 'tags': 'feature,offline'},
        {'name': 'Implement in-app purchases', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'feature,monetization'},
        {'name': 'Update to latest React Native', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'maintenance,upgrade'},
        {'name': 'Add social media sharing', 'project': 'Mobile App', 'priority': 'Low', 'tags': 'feature,social'},
        
        # API Services tasks
        {'name': 'Fix memory leak in user service', 'project': 'API Services', 'priority': 'High', 'tags': 'bug,performance'},
        {'name': 'Implement rate limiting', 'project': 'API Services', 'priority': 'High', 'tags': 'feature,security'},
        {'name': 'Add API versioning', 'project': 'API Services', 'priority': 'Medium', 'tags': 'feature,api'},
        {'name': 'Update database indexes', 'project': 'API Services', 'priority': 'Medium', 'tags': 'performance,database'},
        {'name': 'Write API documentation', 'project': 'API Services', 'priority': 'Medium', 'tags': 'documentation'},
        {'name': 'Fix authentication token expiry', 'project': 'API Services', 'priority': 'High', 'tags': 'bug,authentication'},
        {'name': 'Implement caching layer', 'project': 'API Services', 'priority': 'High', 'tags': 'feature,performance'},
        {'name': 'Add error tracking integration', 'project': 'API Services', 'priority': 'Medium', 'tags': 'monitoring,feature'},
        {'name': 'Optimize SQL queries', 'project': 'API Services', 'priority': 'Medium', 'tags': 'performance,database'},
        {'name': 'Set up CI/CD pipeline', 'project': 'API Services', 'priority': 'High', 'tags': 'devops,automation'},
    ]
    
    # Additional generic tasks
    generic_tasks = [
        {'name': 'Code review for PR #234', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'review'},
        {'name': 'Update dependencies to latest versions', 'project': 'Mobile App', 'priority': 'Low', 'tags': 'maintenance'},
        {'name': 'Fix security vulnerability CVE-2024-1234', 'project': 'API Services', 'priority': 'High', 'tags': 'bug,security'},
        {'name': 'Refactor authentication middleware', 'project': 'API Services', 'priority': 'Medium', 'tags': 'refactor'},
        {'name': 'Add unit tests for new features', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'testing'},
        {'name': 'Design new onboarding flow', 'project': 'Mobile App', 'priority': 'High', 'tags': 'design,ux'},
        {'name': 'Setup monitoring dashboard', 'project': 'API Services', 'priority': 'Medium', 'tags': 'monitoring,devops'},
        {'name': 'Conduct user testing session', 'project': 'Web Platform', 'priority': 'High', 'tags': 'research,ux'},
        {'name': 'Optimize Docker images', 'project': 'API Services', 'priority': 'Low', 'tags': 'devops,optimization'},
        {'name': 'Update color scheme for accessibility', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'ui,accessibility'},
    ]
    
    all_tasks = task_templates + generic_tasks
    
    # Status distribution: ~38% Open, ~24% In Progress, ~26% Completed, ~12% Blocked
    statuses = ['Open'] * 38 + ['In Progress'] * 24 + ['Completed'] * 26 + ['Blocked'] * 12
    
    with app.app_context():
        users = User.query.all()
        user_ids = [user.user_id for user in users]
        
        tasks = []
        for idx, task_template in enumerate(all_tasks, 1):
            status = random.choice(statuses)
            
            # Generate dates based on status
            created_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            start_date = None
            completed_date = None
            blocked_reason = None
            
            if status in ['In Progress', 'Completed']:
                start_date = created_date + timedelta(days=random.randint(0, 3))
            
            if status == 'Completed':
                completed_date = start_date + timedelta(hours=random.randint(8, 120))
            
            if status == 'Blocked':
                blocked_reason = random.choice([
                    'Waiting for API access',
                    'Dependency on another task',
                    'Waiting for client approval',
                    'Technical blocker - need architecture decision',
                    'Waiting for design assets'
                ])
            
            task = Task(
                task_id=f'TASK-{idx:03d}',
                task_name=task_template['name'],
                description=f"Detailed description for {task_template['name']}. This task requires attention and proper implementation.",
                status=status,
                priority=task_template['priority'],
                project=task_template['project'],
                assigned_to=random.choice(user_ids),
                created_date=created_date,
                due_date=created_date + timedelta(days=random.randint(7, 21)),
                start_date=start_date,
                completed_date=completed_date,
                estimated_hours=random.choice([2, 4, 8, 16, 24, 40]),
                tags=task_template['tags'],
                blocked_reason=blocked_reason,
                comments=f"Initial discussion about {task_template['name']}."
            )
            db.session.add(task)
            tasks.append(task)
        
        db.session.commit()
        print(f"✅ Created {len(tasks)} tasks")
        
        # Print statistics
        print("\n📊 Task Statistics:")
        print(f"   Open: {Task.query.filter_by(status='Open').count()}")
        print(f"   In Progress: {Task.query.filter_by(status='In Progress').count()}")
        print(f"   Completed: {Task.query.filter_by(status='Completed').count()}")
        print(f"   Blocked: {Task.query.filter_by(status='Blocked').count()}")
        print(f"   Total: {Task.query.count()}")

def seed_all():
    """Run all seed functions"""
    print("🌱 Starting database seeding...")
    print("="*50)
    
    clear_data()
    generate_users()
    generate_tasks()
    
    print("="*50)
    print("✅ Database seeding completed successfully!")
    print("🚀 You can now start the Flask server")

if __name__ == '__main__':
    seed_all()

