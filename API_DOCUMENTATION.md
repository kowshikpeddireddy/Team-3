# PULSEVO API Documentation

Complete API reference for all endpoints.

## Base URL
```
http://localhost:5000/api
```

---

## 📊 Overview Endpoints

### GET /api/overview
Get dashboard overview metrics.

**Response:**
```json
{
  "open_tasks": 38,
  "open_change": -5,
  "in_progress": 24,
  "progress_change": 7,
  "completed_today": 5,
  "today_change": 12,
  "completed_this_hour": 0,
  "hour_change": 3,
  "completion_rate": 26.0,
  "rate_change": 3,
  "blocked_tasks": 12,
  "total_tasks": 100,
  "completed_tasks": 26
}
```

### GET /api/distribution
Get task distribution for pie chart.

**Response:**
```json
[
  { "name": "Open", "value": 38, "color": "#a78bfa" },
  { "name": "In Progress", "value": 24, "color": "#60a5fa" },
  { "name": "Completed", "value": 26, "color": "#fbbf24" },
  { "name": "Blocked", "value": 12, "color": "#ec4899" }
]
```

### GET /api/trends
Get 7-day trend data.

**Response:**
```json
[
  {
    "date": "Nov 01",
    "created": 5,
    "completed": 3,
    "in_progress": 8
  },
  ...
]
```

### GET /api/team-performance
Get team performance data.

**Response:**
```json
[
  {
    "name": "Alice",
    "completed": 10,
    "in_progress": 5,
    "open": 6
  },
  ...
]
```

---

## ✅ Tasks Endpoints

### GET /api/tasks
Get all tasks with optional filters.

**Query Parameters:**
- `status` (optional): Open | In Progress | Completed | Blocked
- `project` (optional): Web Platform | Mobile App | API Services
- `assigned_to` (optional): user_id
- `priority` (optional): High | Medium | Low
- `search` (optional): Search term for task name

**Example:**
```
GET /api/tasks?status=In%20Progress&project=Web%20Platform
```

**Response:**
```json
[
  {
    "task_id": "TASK-001",
    "task_name": "Implement user authentication flow",
    "description": "Detailed description...",
    "status": "In Progress",
    "priority": "High",
    "project": "Web Platform",
    "assigned_to": "USER-001",
    "created_date": "2025-10-22T14:30:00",
    "due_date": "2025-11-15T23:59:59",
    "start_date": "2025-10-23T09:00:00",
    "completed_date": null,
    "estimated_hours": 8.0,
    "tags": "authentication,security",
    "blocked_reason": null,
    "comments": "Initial discussion..."
  },
  ...
]
```

### GET /api/tasks/:task_id
Get single task by ID.

**Example:**
```
GET /api/tasks/TASK-001
```

**Response:**
```json
{
  "task_id": "TASK-001",
  "task_name": "Implement user authentication flow",
  "status": "In Progress",
  ...
}
```

### GET /api/projects
Get all unique projects.

**Response:**
```json
[
  "Web Platform",
  "Mobile App",
  "API Services"
]
```

### GET /api/projects/stats
Get task counts by project.

**Response:**
```json
[
  {
    "project": "API Services",
    "total": 40,
    "open": 40
  },
  {
    "project": "Mobile App",
    "total": 32,
    "open": 10
  },
  {
    "project": "Web Platform",
    "total": 28,
    "open": 3
  }
]
```

---

## 👥 Users Endpoints

### GET /api/users
Get all users with task statistics.

**Query Parameters:**
- `search` (optional): Search term for user name

**Example:**
```
GET /api/users?search=Alice
```

**Response:**
```json
[
  {
    "user_id": "USER-001",
    "name": "Alice Johnson",
    "initials": "AJ",
    "email": "alice.johnson@company.com",
    "role": "Frontend Developer",
    "team": "Your Team",
    "assigned": 21,
    "completed": 10,
    "in_progress": 5,
    "open": 6,
    "completion_percentage": 50.0,
    "trend": 60.5
  },
  ...
]
```

### GET /api/users/:user_id
Get single user by ID.

**Example:**
```
GET /api/users/USER-001
```

**Response:**
```json
{
  "user_id": "USER-001",
  "name": "Alice Johnson",
  "email": "alice.johnson@company.com",
  "initials": "AJ",
  "role": "Frontend Developer",
  "team": "Your Team",
  "is_active": true
}
```

---

## 🤖 AI Insights Endpoints

### GET /api/ai/summary
Get AI-powered productivity summary.

**Response:**
```json
{
  "summary": "Over the last 24 hours, your team completed 5 tasks with an average closure time of 58.1 hours...",
  "completed_24h": 5,
  "avg_closure_time": 58.1,
  "velocity_change": -17.6,
  "blocked_tasks": 12
}
```

### GET /api/ai/closure-performance
Get task closure performance metrics.

**Response:**
```json
{
  "current_avg": 30.1,
  "previous_avg": 25.6,
  "blocked_tasks": 12,
  "blocked_percentage": 30.0
}
```

### GET /api/ai/due-compliance
Get due date compliance metrics.

**Response:**
```json
{
  "overdue": 14,
  "on_time": 23,
  "active_tasks": 24,
  "avg_active_time": 159.2
}
```

### GET /api/ai/predictions
Get predictive analytics.

**Response:**
```json
{
  "sprint_completion": 94,
  "next_week_workload": "Medium",
  "expected_tasks": 48,
  "risk_level": "Low",
  "risk_description": "No major bottlenecks"
}
```

### GET /api/ai/team-benchmarking
Get team benchmarking data.

**Response:**
```json
[
  {
    "name": "Your Team",
    "total_tasks": 178,
    "velocity": 49,
    "efficiency": 92,
    "rank": 2,
    "badge": null
  },
  {
    "name": "Alpha Team",
    "total_tasks": 186,
    "velocity": 51,
    "efficiency": 94,
    "rank": 1,
    "badge": "🏆"
  },
  ...
]
```

### GET /api/ai/productivity-trends
Get 4-week productivity trends.

**Response:**
```json
[
  {
    "week": "Week 1",
    "your_team": 35,
    "alpha_team": 40,
    "beta_team": 30,
    "gamma_team": 28
  },
  ...
]
```

### GET /api/ai/sentiment
Get team communication sentiment analysis.

**Response:**
```json
{
  "positive": 75,
  "neutral": 20,
  "negative": 5,
  "insight": "Team morale appears positive. Keep up the good work..."
}
```

---

## 💬 Chat Endpoint

### POST /api/chat
Handle conversational queries.

**Request Body:**
```json
{
  "query": "How many bugs did we close this sprint?"
}
```

**Response:**
```json
{
  "response": "Currently tracking 15 bugs total. 5 have been closed this week, and 10 are still open.",
  "timestamp": "02:09:09 PM"
}
```

**Supported Query Patterns:**
- Questions about bugs: "How many bugs...", "Show me bugs..."
- Task queries: "How many tasks...", "What's completed..."
- Progress inquiries: "Show progress...", "What's the status..."

---

## ⚙️ Settings Endpoints

### GET /api/settings
Get current settings.

**Response:**
```json
{
  "github_token": "ghp_xxxxxxxxxxxx",
  "trello_key": "",
  "trello_token": "",
  "notifications": {
    "task_updates": true,
    "ai_insights": true,
    "daily_digest": false
  }
}
```

### POST /api/settings
Save settings.

**Request Body:**
```json
{
  "github_token": "ghp_new_token",
  "trello_key": "trello_key_here",
  "trello_token": "trello_token_here",
  "notifications": {
    "task_updates": true,
    "ai_insights": false,
    "daily_digest": true
  }
}
```

**Response:**
```json
{
  "message": "Settings saved successfully"
}
```

---

## 🏥 Health Check

### GET /api/health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T15:30:00",
  "database": "connected"
}
```

---

## 📝 Response Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## 🔒 CORS

All endpoints support CORS and can be called from:
- http://localhost:3000
- http://localhost:3001
- Any origin (in development mode)

---

## 🧪 Testing with cURL

### Get Overview
```bash
curl http://localhost:5000/api/overview
```

### Get Tasks with Filter
```bash
curl "http://localhost:5000/api/tasks?status=Completed"
```

### Send Chat Query
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How many bugs did we close?"}'
```

---

## 📊 Rate Limiting

Currently no rate limiting implemented. In production, consider:
- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## 🔄 Auto-Refresh Recommendations

For real-time dashboards, recommended polling intervals:
- Overview metrics: Every 10 seconds
- Task list: Every 30 seconds
- AI insights: Every 60 seconds
- Chat: On-demand only

---

## 🛠️ Extending the API

To add new endpoints, edit `backend/app.py`:

```python
@app.route('/api/your-endpoint', methods=['GET'])
def your_endpoint():
    # Your logic here
    return jsonify({'data': 'value'})
```

Then add to `frontend/src/api/client.js`:

```javascript
export const yourEndpoint = () => apiClient.get('/your-endpoint');
```

---

For more information, see the main README.md file.

