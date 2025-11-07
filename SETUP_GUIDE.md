# PULSEVO - Complete Setup Guide

This guide will walk you through setting up PULSEVO from scratch.

## 📋 Prerequisites Check

Before starting, ensure you have the following installed:

### Check Python
```bash
python3 --version
# Should show: Python 3.8 or higher
```

If not installed, download from: https://www.python.org/downloads/

### Check Node.js
```bash
node --version
# Should show: v16.0 or higher

npm --version
# Should show: 8.0 or higher
```

If not installed, download from: https://nodejs.org/

## 🎯 Step-by-Step Setup

### Step 1: Backend Setup (5 minutes)

#### 1.1 Open Terminal and navigate to backend
```bash
cd /Users/kowshik/Desktop/Hackathon/backend
```

#### 1.2 Install Python packages
```bash
pip3 install -r requirements.txt
```

Expected output:
```
Successfully installed Flask-3.0.0 Flask-SQLAlchemy-3.1.1 Flask-CORS-4.0.0 ...
```

#### 1.3 Generate sample data
```bash
python3 seed_data.py
```

Expected output:
```
🌱 Starting database seeding...
==================================================
✅ Cleared existing data
✅ Created 11 users
✅ Created 100 tasks

📊 Task Statistics:
   Open: 38
   In Progress: 24
   Completed: 26
   Blocked: 12
   Total: 100
==================================================
✅ Database seeding completed successfully!
🚀 You can now start the Flask server
```

#### 1.4 Start Flask server
```bash
python3 app.py
```

Expected output:
```
✅ Database tables created successfully!
✅ Database initialized!
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

✅ **Backend is now running!** Keep this terminal open.

---

### Step 2: Frontend Setup (5 minutes)

#### 2.1 Open a NEW terminal window

#### 2.2 Navigate to frontend directory
```bash
cd /Users/kowshik/Desktop/Hackathon/frontend
```

#### 2.3 Install Node packages
```bash
npm install
```

This will take 2-3 minutes. Expected output:
```
added 1500+ packages in 120s
```

#### 2.4 Start React development server
```bash
npm start
```

Expected output:
```
Compiled successfully!

You can now view pulsevo-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

✅ **Frontend is now running!** Your browser should automatically open to http://localhost:3000

---

## 🎉 Verification

After both servers are running, you should see:

### Backend Terminal
```
✅ Database initialized!
🚀 Server running on http://localhost:5000
 * Running on http://0.0.0.0:5000
```

### Frontend Terminal
```
Compiled successfully!
webpack compiled with 0 warnings
```

### Browser
- URL: http://localhost:3000
- You should see the **PULSEVO** dashboard
- Navigation: Overview, Tasks, AI Insights, Query, Settings

---

## 🧪 Testing the Application

### 1. Test Overview Page
- Open http://localhost:3000
- You should see:
  - 4 metric cards (Open Tasks, In Progress, etc.)
  - Task distribution pie chart
  - 7-day trend line chart
  - Team performance bar chart

### 2. Test Tasks Page
- Click "Tasks" in sidebar
- You should see:
  - Table with 11 users and their task statistics
  - Search box (try searching "Alice")
  - Status filter dropdown
  - Project pie charts on the right

### 3. Test AI Insights Page
- Click "AI Insights" in sidebar
- You should see:
  - AI-powered summary
  - Performance metrics
  - Team benchmarking
  - Sentiment analysis

### 4. Test Queries Page
- Click "Query" in sidebar
- Type: "How many bugs did we close this sprint?"
- Press Send
- You should get an AI response

### 5. Test Settings Page
- Click "Settings" in sidebar
- Toggle notification switches
- Click "Save API Keys"

---

## 🔧 Common Issues and Solutions

### Issue 1: Port 5000 already in use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or change port in backend/app.py:
app.run(debug=True, port=5001)
# Then update frontend/src/api/client.js:
const API_BASE_URL = 'http://localhost:5001/api';
```

### Issue 2: Module not found errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
cd /Users/kowshik/Desktop/Hackathon/backend
pip3 install --upgrade -r requirements.txt
```

### Issue 3: npm install fails

**Symptoms:**
```
npm ERR! code ERESOLVE
```

**Solution:**
```bash
cd /Users/kowshik/Desktop/Hackathon/frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Issue 4: CORS errors in browser

**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
- Ensure backend is running
- Check Flask-CORS is installed:
```bash
pip3 install flask-cors
```

### Issue 5: Database file not found

**Symptoms:**
```
sqlite3.OperationalError: unable to open database file
```

**Solution:**
```bash
cd /Users/kowshik/Desktop/Hackathon/backend
python3 seed_data.py
```

### Issue 6: React not starting

**Symptoms:**
```
Error: ENOSPC: System limit for number of file watchers reached
```

**Solution (macOS/Linux):**
```bash
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## 🎨 Customization

### Change Backend Port
Edit `backend/app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')  # Changed port
```

Update `frontend/src/api/client.js`:
```javascript
const API_BASE_URL = 'http://localhost:5001/api';  // Match backend port
```

### Change Frontend Port
Create `.env` file in `frontend/`:
```
PORT=3001
```

### Modify Sample Data
Edit `backend/seed_data.py`:
- Change number of users/tasks
- Modify status distribution
- Add new projects

Then regenerate:
```bash
python3 seed_data.py
```

---

## 📱 Accessing from Other Devices

### Find your local IP
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr IPv4
```

### Access from phone/tablet
```
http://YOUR_IP:3000
# Example: http://192.168.1.100:3000
```

Make sure both devices are on the same WiFi network.

---

## 🚀 Production Deployment

### Backend (Flask)
```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend (React)
```bash
npm run build
# Serve build/ folder with nginx or Apache
```

---

## 📊 Understanding the Data

### Users
- 11 sample users across 4 teams
- Each user has tasks assigned
- Teams: Your Team, Alpha Team, Beta Team, Gamma Team

### Tasks
- 100 sample tasks across 3 projects
- Projects: Web Platform, Mobile App, API Services
- Statuses: Open, In Progress, Completed, Blocked
- Priorities: High, Medium, Low

### Auto-Generated Timestamps
- Tasks created within last 30 days
- Completed tasks have realistic closure times
- Blocked tasks have blocking reasons

---

## 🎓 Learning Resources

### Flask
- Official Docs: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/

### React
- Official Docs: https://react.dev/
- Recharts: https://recharts.org/

---

## ✅ Final Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend dependencies installed (`pip3 install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Sample data generated (`python3 seed_data.py`)
- [ ] Backend running on port 5000
- [ ] Frontend running on port 3000
- [ ] Browser opens to http://localhost:3000
- [ ] All 5 pages working (Overview, Tasks, AI Insights, Query, Settings)

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check both terminal windows for error messages
2. Ensure both servers are running simultaneously
3. Try restarting both servers
4. Clear browser cache (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
5. Check the main README.md for additional troubleshooting

---

## 🎉 Success!

If everything is working, you should now have:
- ✅ A fully functional dashboard
- ✅ Real-time data updates
- ✅ Interactive charts
- ✅ AI-powered insights
- ✅ Task management system

**Congratulations! You're ready to demo PULSEVO!** 🚀

---

**Time to complete setup: ~10 minutes**

Happy hacking! 💻

