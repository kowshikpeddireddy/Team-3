# CSV Upload Feature - User Guide

## Overview
The CSV upload feature allows you to bulk import tasks into PULSEVO directly from a CSV file. Uploaded tasks will automatically reflect across all tabs (Overview, Tasks, AI Insights).

---

## How to Upload Tasks

### **Step 1: Prepare Your CSV File**
Use the provided template: `sample_tasks_template.csv`

### **Step 2: Upload via UI**
1. Navigate to **Tasks** tab
2. Click **"Upload CSV"** button (top right)
3. Select your CSV file
4. Wait for confirmation message
5. Data will automatically refresh across all tabs

---

## CSV Format Requirements

### **Required Columns** (Must be present)
- `task_name` - Task title (string)
- `status` - Must be one of: `Open`, `In Progress`, `Completed`, `Blocked`
- `assigned_to` - User ID (must exist in database, e.g., `USER-001`)

### **Optional Columns**
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `task_id` | String | `TASK-9999` | Auto-generated if empty |
| `description` | Text | `Add JWT auth to API` | Task details |
| `priority` | String | `High`, `Medium`, `Low` | Default: `Medium` |
| `project` | String | `Web Platform`, `Mobile App`, `API Services` | Default: `Web Platform` |
| `created_date` | DateTime | `2024-11-01` | Default: Current date/time |
| `due_date` | DateTime | `2024-11-15` | Deadline |
| `start_date` | DateTime | `2024-11-02` | When work started |
| `completed_date` | DateTime | `2024-11-10` | When task finished |
| `estimated_hours` | Float | `40` | Estimated effort |
| `tags` | String | `backend,security` | Comma-separated |
| `blocked_reason` | String | `Waiting for API` | Why task is blocked |
| `comments` | Text | `Need review` | Additional notes |

---

## Date Format
- Accepted formats: `YYYY-MM-DD`, `YYYY-MM-DD HH:MM:SS`
- Examples:
  - `2024-11-01`
  - `2024-11-01 14:30:00`

---

## Validation Rules

### ✅ **What Gets Accepted**
- Valid CSV with required columns
- Users (`assigned_to`) that exist in database
- Valid status values (case-sensitive)
- Proper date formats

### ❌ **What Gets Rejected**
- Non-CSV files (`.xlsx`, `.txt`, etc.)
- Missing required columns
- Invalid user IDs
- Duplicate `task_id` (task will be skipped)
- Invalid date formats

---

## Upload Response

### **Success Response**
```json
{
  "success": true,
  "tasks_added": 5,
  "tasks_skipped": 0,
  "total_rows": 5,
  "errors": []
}
```

### **Partial Success (Some Tasks Skipped)**
```json
{
  "success": true,
  "tasks_added": 3,
  "tasks_skipped": 2,
  "total_rows": 5,
  "errors": [
    "Row 3: User USER-999 not found",
    "Row 4: Task TASK-1234 already exists"
  ]
}
```

### **Error Response**
```json
{
  "error": "Missing required columns: task_name, status"
}
```

---

## Example CSV

```csv
task_id,task_name,description,status,priority,project,assigned_to,created_date,due_date,estimated_hours,tags
TASK-9999,Fix login bug,Users can't login after password reset,Open,High,Web Platform,USER-001,2024-11-01,2024-11-05,8,"bug,authentication"
,Add dark mode,Implement dark theme toggle,In Progress,Medium,Web Platform,USER-002,2024-11-02,2024-11-10,16,"feature,ui"
,Database backup,Setup automated daily backups,Completed,High,API Services,USER-003,2024-10-28,2024-11-01,4,"devops,database"
```

**Notes:**
- Leave `task_id` empty for auto-generation
- First row MUST be column headers
- Use double quotes for fields containing commas

---

## Tips & Best Practices

### ✅ **DO**
- Test with 5-10 tasks first
- Use the provided template
- Verify user IDs exist before uploading
- Keep descriptions concise
- Use consistent date formats

### ❌ **DON'T**
- Upload files over 10MB (performance)
- Use special characters in task IDs
- Mix date formats in the same file
- Skip required columns
- Upload duplicate task IDs

---

## Troubleshooting

### **Problem: "User not found" errors**
**Solution**: Check that `assigned_to` values match existing user IDs in the database.
```bash
# Valid user IDs in default database:
USER-001, USER-002, USER-003, ... USER-030
```

### **Problem: "Task already exists" warning**
**Solution**: Either:
- Remove the `task_id` column (will auto-generate)
- Change the `task_id` to a unique value

### **Problem: Date parsing errors**
**Solution**: Use format `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`
```
✅ Good: 2024-11-01
✅ Good: 2024-11-01 14:30:00
❌ Bad: 11/01/2024
❌ Bad: Nov 1, 2024
```

### **Problem: CSV not uploading**
**Solution**: Ensure:
1. File extension is `.csv` (not `.xlsx` or `.txt`)
2. File is UTF-8 encoded
3. No extra blank rows at the end
4. Backend server is running on port 5001

---

## Backend Details

### **Endpoint**: `POST /api/tasks/upload`
- **Content-Type**: `multipart/form-data`
- **Max File Size**: 10MB
- **Accepts**: `.csv` files only

### **Processing Logic**:
1. Validate file type (`.csv`)
2. Parse CSV with pandas
3. Check required columns
4. For each row:
   - Auto-generate `task_id` if empty
   - Verify user exists
   - Parse date fields
   - Create task object
   - Skip if duplicate
5. Commit all tasks to database
6. Return summary

---

## Testing the Feature

### **1. Using Sample Template**
```bash
# Copy and edit the template
cp sample_tasks_template.csv my_tasks.csv

# Edit my_tasks.csv with your data
# Make sure assigned_to uses valid USER-IDs

# Upload via UI:
# Go to Tasks tab → Click "Upload CSV" → Select my_tasks.csv
```

### **2. Verify Upload**
After uploading:
- ✅ Check **Tasks** tab → Status filter cards should update
- ✅ Check **Overview** tab → Metrics should reflect new tasks
- ✅ Check **AI Insights** tab → Analytics should include new data
- ✅ Try natural language query: "Show me all tasks uploaded today"

---

## Data Refresh

Uploaded tasks automatically update:
- ✅ **Overview Tab**: Task counts, completion rates, trends
- ✅ **Tasks Tab**: User assignments, status counts, table data
- ✅ **AI Insights**: AI summary, predictions, benchmarking
- ✅ **Query Tab**: Natural language query results

**No page refresh needed!** The UI automatically refetches data after successful upload.

---

## Security Notes

- ✅ Only CSV files accepted (validates extension)
- ✅ File size limited to prevent DoS
- ✅ SQL injection protected (SQLAlchemy ORM)
- ✅ User verification before task creation
- ✅ Transaction rollback on errors
- ⚠️ For production: Add authentication and rate limiting

---

## API Example (cURL)

```bash
# Upload CSV via API
curl -X POST http://localhost:5001/api/tasks/upload \
  -F "file=@my_tasks.csv"

# Response:
{
  "success": true,
  "tasks_added": 5,
  "tasks_skipped": 0,
  "total_rows": 5,
  "errors": []
}
```

---

## Future Enhancements

Planned features:
- 📊 Excel (`.xlsx`) support
- 👥 Bulk user upload
- 📝 Template download button in UI
- 🔄 Update existing tasks via CSV
- 📧 Email notification after upload
- 🗑️ Undo/rollback uploads

---

## Need Help?

**Sample Template**: `sample_tasks_template.csv`
**Required Columns**: `task_name`, `status`, `assigned_to`
**Valid User IDs**: `USER-001` to `USER-030` (default database)
**Backend Port**: `5001`
**Upload Button**: Tasks tab (top right)

---

**Happy uploading! 🚀**

