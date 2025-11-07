"""
Export database data to Excel file
"""
from app import app, db
from models import User, Task
import pandas as pd
from datetime import datetime
import os

def export_to_excel():
    """Export all users and tasks to Excel file"""
    
    with app.app_context():
        print("📊 Exporting database to Excel...")
        print("=" * 50)
        
        # Get all users
        users = User.query.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'User ID': user.user_id,
                'Name': user.name,
                'Email': user.email,
                'Initials': user.initials,
                'Role': user.role,
                'Team': user.team,
                'Is Active': user.is_active,
                'Created At': user.created_at
            })
        
        print(f"✅ Found {len(users_data)} users")
        
        # Get all tasks
        tasks = Task.query.all()
        tasks_data = []
        
        for task in tasks:
            # Get assigned user name
            assigned_user = User.query.get(task.assigned_to)
            assigned_name = assigned_user.name if assigned_user else 'Unassigned'
            
            tasks_data.append({
                'Task ID': task.task_id,
                'Task Name': task.task_name,
                'Description': task.description,
                'Status': task.status,
                'Priority': task.priority,
                'Project': task.project,
                'Assigned To': task.assigned_to,
                'Assigned Name': assigned_name,
                'Created Date': task.created_date,
                'Due Date': task.due_date,
                'Start Date': task.start_date,
                'Completed Date': task.completed_date,
                'Estimated Hours': task.estimated_hours,
                'Tags': task.tags,
                'Blocked Reason': task.blocked_reason,
                'Comments': task.comments,
                'Updated At': task.updated_at
            })
        
        print(f"✅ Found {len(tasks_data)} tasks")
        
        # Create DataFrames
        users_df = pd.DataFrame(users_data)
        tasks_df = pd.DataFrame(tasks_data)
        
        # Create Excel file with multiple sheets
        output_file = '/Users/kowshik/Desktop/Hackathon/database_export.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            users_df.to_excel(writer, sheet_name='Users', index=False)
            tasks_df.to_excel(writer, sheet_name='Tasks', index=False)
            
            # Create a summary sheet
            summary_data = {
                'Metric': [
                    'Total Users',
                    'Total Tasks',
                    'Open Tasks',
                    'In Progress Tasks',
                    'Completed Tasks',
                    'Blocked Tasks',
                    'Export Date'
                ],
                'Value': [
                    len(users_data),
                    len(tasks_data),
                    len([t for t in tasks if t.status == 'Open']),
                    len([t for t in tasks if t.status == 'In Progress']),
                    len([t for t in tasks if t.status == 'Completed']),
                    len([t for t in tasks if t.status == 'Blocked']),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Tasks by status
            status_data = {
                'Status': ['Open', 'In Progress', 'Completed', 'Blocked'],
                'Count': [
                    len([t for t in tasks if t.status == 'Open']),
                    len([t for t in tasks if t.status == 'In Progress']),
                    len([t for t in tasks if t.status == 'Completed']),
                    len([t for t in tasks if t.status == 'Blocked'])
                ]
            }
            status_df = pd.DataFrame(status_data)
            status_df.to_excel(writer, sheet_name='Tasks by Status', index=False)
            
            # Tasks by project
            projects = ['Web Platform', 'Mobile App', 'API Services']
            project_data = {
                'Project': projects,
                'Total Tasks': [len([t for t in tasks if t.project == p]) for p in projects],
                'Open': [len([t for t in tasks if t.project == p and t.status == 'Open']) for p in projects],
                'In Progress': [len([t for t in tasks if t.project == p and t.status == 'In Progress']) for p in projects],
                'Completed': [len([t for t in tasks if t.project == p and t.status == 'Completed']) for p in projects],
                'Blocked': [len([t for t in tasks if t.project == p and t.status == 'Blocked']) for p in projects]
            }
            project_df = pd.DataFrame(project_data)
            project_df.to_excel(writer, sheet_name='Tasks by Project', index=False)
            
            # Users by team
            teams = ['Your Team', 'Alpha Team', 'Beta Team', 'Gamma Team']
            team_data = {
                'Team': teams,
                'Members': [len([u for u in users if u.team == t]) for t in teams],
                'Total Tasks': [
                    sum([1 for t in tasks if any(u.user_id == t.assigned_to and u.team == team for u in users)])
                    for team in teams
                ]
            }
            team_df = pd.DataFrame(team_data)
            team_df.to_excel(writer, sheet_name='Users by Team', index=False)
        
        print("=" * 50)
        print(f"✅ Export completed successfully!")
        print(f"📁 File saved: {output_file}")
        print(f"\n📊 Summary:")
        print(f"   • Users Sheet: {len(users_data)} rows")
        print(f"   • Tasks Sheet: {len(tasks_data)} rows")
        print(f"   • Summary Sheet: Database statistics")
        print(f"   • Tasks by Status: Breakdown by status")
        print(f"   • Tasks by Project: Breakdown by project")
        print(f"   • Users by Team: Team distribution")
        print("\n✨ Open the file to view all data!")

if __name__ == '__main__':
    try:
        export_to_excel()
    except ImportError:
        print("❌ Error: pandas and openpyxl are required")
        print("Install them with: pip3 install pandas openpyxl")
    except Exception as e:
        print(f"❌ Error: {e}")

