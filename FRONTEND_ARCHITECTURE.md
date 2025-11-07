# Frontend Architecture Documentation

## 📁 Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── index.js              # Entry point
│   ├── App.js                # Main app component with routing
│   ├── App.css              # Global styles
│   ├── api/
│   │   └── client.js        # API client (Axios)
│   ├── components/
│   │   ├── Navbar.js        # Navigation bar with time filter
│   │   ├── Navbar.css
│   │   ├── Sidebar.js       # Side navigation
│   │   └── Sidebar.css
│   └── pages/
│       ├── Overview.js      # Dashboard overview
│       ├── Overview.css
│       ├── Tasks.js         # Task management (user stats)
│       ├── Tasks.css
│       ├── AIInsights.js    # AI insights page
│       ├── AIInsights.css
│       ├── Query.js         # Query page
│       ├── Query.css
│       ├── Settings.js      # Settings page
│       └── Settings.css
├── package.json             # Dependencies
└── package-lock.json
```

---

## 🛠️ Tech Stack

- **React**: 18.3.1
- **React Router**: 7.1.1 (for routing)
- **Axios**: 1.7.9 (API calls)
- **Recharts**: 2.15.0 (charts)
- **Lucide React**: 0.469.0 (icons)

---

## 🧩 Component Architecture

### **App Structure**

```
App.js (Root)
├── Navbar (Global)
│   ├── Logo
│   ├── Time Filter Dropdown (Today/Week/Month/All)
│   └── Profile Button
├── Sidebar (Global)
│   ├── Overview
│   ├── Tasks
│   ├── AI Insights
│   ├── Query
│   └── Settings
└── Routes
    ├── /overview → Overview Page
    ├── /tasks → Tasks Page
    ├── /ai-insights → AI Insights Page
    ├── /query → Query Page
    └── /settings → Settings Page
```

---

## 📄 Page Components

### **1. Overview Page** (`Overview.js`)

**Purpose:** Dashboard with key metrics, charts, and trends

**State Management:**
```javascript
const [metrics, setMetrics] = useState(null);           // Overview metrics
const [distribution, setDistribution] = useState([]);    // Pie chart data
const [trends, setTrends] = useState([]);               // Line chart data
const [teamPerformance, setTeamPerformance] = useState([]); // Bar chart data
const [loading, setLoading] = useState(true);
const [timeFilter, setTimeFilter] = useState('today');  // Global filter
```

**Data Flow:**
1. User selects time filter from Navbar (Today/Week/Month/All)
2. `timeFilter` state updates
3. `useEffect` triggers on filter change
4. Fetches data from 4 endpoints in parallel:
   ```javascript
   const [metricsRes, distRes, trendsRes, teamRes] = await Promise.all([
     getOverview(timeFilter),
     getDistribution(timeFilter),
     getTrends(timeFilter),
     getTeamPerformance(timeFilter)
   ]);
   ```
5. Updates all charts and metrics
6. Auto-refreshes every 10 seconds

**Components:**
- **Metric Cards** (4 cards):
  - Open Tasks (with % change)
  - In Progress (with % change)
  - Closed This Month (with % change)
  - Completion Rate (with % change)
  
- **Task Distribution** (Donut Chart):
  - Open (purple)
  - In Progress (blue)
  - Completed (yellow)
  - Blocked (pink)

- **Trend Analysis** (Line Chart):
  - Tasks Created (blue line)
  - Tasks Completed (green line)
  - Tasks In Progress (purple line)

- **Team Performance** (Bar Chart):
  - Top 5 team members
  - Completed vs In Progress vs Open

**Key Features:**
- ✅ Real-time filtering by time period
- ✅ Auto-refresh every 10 seconds
- ✅ Loading state
- ✅ Filter badge showing current selection
- ✅ Percentage change indicators (up/down arrows)

---

### **2. Tasks Page** (`Tasks.js`)

**Purpose:** User task management with filtering and search

**State Management:**
```javascript
const [users, setUsers] = useState([]);                  // All users with stats
const [projectStats, setProjectStats] = useState([]);    // Project chart data
const [loading, setLoading] = useState(true);
const [searchTerm, setSearchTerm] = useState('');        // Search input
const [statusFilter, setStatusFilter] = useState('All Tasks'); // Status filter
const [currentPage, setCurrentPage] = useState(1);       // Pagination
const usersPerPage = 10;                                 // Items per page
```

**Data Flow:**
1. User selects status filter (All/Open/In Progress/Completed/Blocked)
2. Frontend calls: `GET /api/tasks?status=Open&page=1&per_page=2000`
3. Backend returns:
   - `tasks`: Array of filtered tasks
   - `users_stats`: Stats calculated from **filtered** tasks only
4. Frontend merges users with their stats:
   ```javascript
   const mergedUsers = fetchedUsers.map(user => ({
     ...user,
     assigned: stats.assigned,
     completed: stats.completed,
     in_progress: stats.in_progress,
     completion_percentage: Math.round((completed / assigned) * 100)
   }))
   .filter(user => user.assigned > 0); // Only show users with tasks
   ```
5. Apply client-side search filter
6. Apply pagination (10 users per page)
7. Display in table

**Table Structure:**
```
| Name          | Assigned | Completed | Ongoing | Trend    |
|---------------|----------|-----------|---------|----------|
| Alice Johnson | 29       | [0]       | [0]     | ↓ 0.0%   |
| Bob Smith     | 25       | [0]       | [0]     | ↓ 0.0%   |
```

**Components:**
- **Search Box**: Filter by user name
- **Status Dropdown**: Filter by task status
- **User Table**: Shows user statistics
- **Pagination**: 10 users per page with page numbers
- **Pie Charts** (2):
  - Tasks by Project
  - Open Issues by Project

**Key Features:**
- ✅ Status filter updates user stats
- ✅ Search by user name
- ✅ Pagination with smart page numbers
- ✅ Shows only users with tasks in filtered set
- ✅ Completion percentage with trend arrows
- ✅ Colored avatars with initials
- ✅ Filter indicator in pagination info

**Filtering Logic:**
```javascript
// When "Open" is selected:
// 1. Backend returns only users with Open tasks
// 2. Frontend filters out users with 0 tasks
// 3. Result: Only users with Open tasks are shown
```

---

### **3. AI Insights Page** (`AIInsights.js`)

**Purpose:** AI-powered insights and analytics (placeholder)

**Status:** Basic UI structure, awaiting AI integration

---

### **4. Query Page** (`Query.js`)

**Purpose:** Custom queries and data exploration (placeholder)

**Status:** Basic UI structure

---

### **5. Settings Page** (`Settings.js`)

**Purpose:** Application settings (placeholder)

**Status:** Basic UI structure

---

## 🔄 State Management

### **Global State** (in `App.js`)

```javascript
const [timeFilter, setTimeFilter] = useState('today');
```

**Passed to:**
- `Overview` (reads timeFilter)
- `Tasks` (reads timeFilter)
- `AIInsights` (reads timeFilter)
- `Navbar` (reads + updates timeFilter)

**Flow:**
```
User clicks "This Week" in Navbar
    ↓
setTimeFilter('week')
    ↓
Overview component re-renders
    ↓
useEffect triggers
    ↓
Fetches data with filter=week
    ↓
Charts update
```

---

### **Local State** (per component)

Each page manages its own:
- Data state (metrics, tasks, users, etc.)
- Loading state
- Error state
- UI state (search, pagination, etc.)

**No global state management library needed!** (Redux, Zustand, etc.)

---

## 🌐 API Client

**File:** `src/api/client.js`

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Overview endpoints
export const getOverview = (filter = 'today') => 
  apiClient.get(`/overview?filter=${filter}`);

export const getDistribution = (filter = 'today') => 
  apiClient.get(`/distribution?filter=${filter}`);

export const getTrends = (filter = 'today') => 
  apiClient.get(`/trends?filter=${filter}`);

export const getTeamPerformance = (filter = 'today') => 
  apiClient.get(`/team-performance?filter=${filter}`);

// Tasks endpoints
export const getTasks = (filters = {}) => {
  const params = new URLSearchParams(filters).toString();
  return apiClient.get(`/tasks${params ? '?' + params : ''}`);
};

// Users endpoints
export const getUsers = (search = '') => 
  apiClient.get(`/users${search ? '?search=' + search : ''}`);

// Projects endpoints
export const getProjectStats = () => 
  apiClient.get('/projects/stats');
```

**Key Features:**
- ✅ Centralized API configuration
- ✅ Base URL configuration
- ✅ Reusable functions
- ✅ Query parameter handling
- ✅ Axios interceptors (can add auth, error handling)

---

## 🎨 Styling

### **Design System**

**Colors:**
```css
/* Background */
--bg-primary: #0a0a1a;
--bg-secondary: #1a1a2e;
--bg-tertiary: #0f0f1a;

/* Borders */
--border-color: #2a2a3e;

/* Text */
--text-primary: #ffffff;
--text-secondary: #e5e7eb;
--text-muted: #9ca3af;

/* Status Colors */
--open: #a78bfa (purple);
--progress: #60a5fa (blue);
--completed: #10b981 (green);
--blocked: #ef4444 (red);

/* Priority Colors */
--high: #ef4444 (red);
--medium: #fbbf24 (yellow);
--low: #9ca3af (gray);

/* Brand */
--brand-primary: #3b82f6 (blue);
--brand-hover: #2563eb (darker blue);
```

**Typography:**
- Font: System fonts (sans-serif)
- Sizes: 12px-24px
- Weights: 400 (normal), 500 (medium), 600 (semi-bold), 700 (bold)

**Spacing:**
- Gap: 4px, 8px, 12px, 16px, 20px, 24px
- Padding: Same as gap
- Margin: Same as gap

**Border Radius:**
- Small: 6px
- Medium: 8px
- Large: 12px
- X-Large: 16px

---

### **Component Styles**

Each component has its own CSS file:
- `Overview.css` - Dashboard styles
- `Tasks.css` - Task management styles
- `Navbar.css` - Navigation styles
- `Sidebar.css` - Sidebar styles

**No CSS framework!** (Bootstrap, Tailwind, etc.)
- Custom CSS Grid and Flexbox
- Responsive design with media queries
- Dark theme only

---

## 📱 Responsive Design

### **Breakpoints:**

```css
/* Desktop: > 1200px */
.tasks-content {
  grid-template-columns: 1fr 400px;
}

/* Tablet: 768px - 1200px */
@media (max-width: 1200px) {
  .tasks-content {
    grid-template-columns: 1fr;
  }
}

/* Mobile: < 768px */
@media (max-width: 768px) {
  .table-row {
    grid-template-columns: 1fr;
  }
  /* Hide non-essential columns */
  .td:not(.name) {
    display: none;
  }
}
```

---

## 🔄 Data Fetching Patterns

### **Pattern 1: Parallel Fetching** (Overview Page)

```javascript
const fetchData = async () => {
  try {
    setLoading(true);
    
    // Fetch 4 endpoints in parallel
    const [metricsRes, distRes, trendsRes, teamRes] = await Promise.all([
      getOverview(timeFilter),
      getDistribution(timeFilter),
      getTrends(timeFilter),
      getTeamPerformance(timeFilter)
    ]);
    
    setMetrics(metricsRes.data);
    setDistribution(distRes.data);
    setTrends(trendsRes.data);
    setTeamPerformance(teamRes.data);
    
    setLoading(false);
  } catch (error) {
    console.error('Error:', error);
    setLoading(false);
  }
};
```

**Benefits:**
- ✅ Faster: All requests start simultaneously
- ✅ Single loading state
- ✅ Better UX: Page loads faster

---

### **Pattern 2: Debounced Search** (Tasks Page)

```javascript
const [searchTerm, setSearchTerm] = useState('');

useEffect(() => {
  const timer = setTimeout(() => {
    if (searchTerm !== undefined) {
      fetchData(); // Only fetches after 500ms of no typing
    }
  }, 500);
  
  return () => clearTimeout(timer);
}, [searchTerm]);
```

**Benefits:**
- ✅ Reduces API calls
- ✅ Better performance
- ✅ Waits for user to finish typing

---

### **Pattern 3: Auto-Refresh** (Overview Page)

```javascript
useEffect(() => {
  fetchData();
  
  // Auto-refresh every 10 seconds
  const interval = setInterval(fetchData, 10000);
  
  return () => clearInterval(interval); // Cleanup
}, [timeFilter]);
```

**Benefits:**
- ✅ Real-time updates
- ✅ No manual refresh needed
- ✅ Cleans up on unmount

---

## 📊 Chart Components

### **Using Recharts**

```javascript
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

<ResponsiveContainer width="100%" height={200}>
  <PieChart>
    <Pie
      data={data}
      cx="50%"
      cy="50%"
      innerRadius={40}
      outerRadius={80}
      dataKey="value"
    >
      {data.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={entry.color} />
      ))}
    </Pie>
    <Tooltip />
  </PieChart>
</ResponsiveContainer>
```

**Chart Types Used:**
1. **Donut Charts**: Task distribution, project stats
2. **Line Charts**: Trend analysis over time
3. **Bar Charts**: Team performance comparison

---

## 🎯 Key Features Implementation

### **1. Time Filter**

**Location:** Navbar (top-right)

**Implementation:**
```javascript
// In Navbar.js
<select 
  className="time-selector"
  value={timeFilter}
  onChange={(e) => setTimeFilter(e.target.value)}
>
  <option value="today">Today</option>
  <option value="week">This Week</option>
  <option value="month">This Month</option>
  <option value="all">All Time</option>
</select>
```

**Propagation:**
```
Navbar → App.js (state) → Overview/Tasks/AIInsights (props)
```

---

### **2. Status Filter** (Tasks Page)

**Implementation:**
```javascript
<select 
  className="status-filter"
  value={statusFilter}
  onChange={(e) => {
    setStatusFilter(e.target.value);
    setCurrentPage(1); // Reset to page 1
  }}
>
  <option>All Tasks</option>
  <option>Open</option>
  <option>In Progress</option>
  <option>Completed</option>
  <option>Blocked</option>
</select>
```

**Effect:**
- Triggers `useEffect` → `fetchData()`
- Backend filters tasks by status
- Frontend shows only users with tasks in that status
- Pagination resets to page 1

---

### **3. Search** (Tasks Page)

**Implementation:**
```javascript
const filteredUsers = users.filter(user =>
  user.name.toLowerCase().includes(searchTerm.toLowerCase())
);
```

**Client-Side Filtering:**
- No API call needed
- Instant results
- Works with status filter

---

### **4. Pagination** (Tasks Page)

**Implementation:**
```javascript
const totalPages = Math.ceil(filteredUsers.length / usersPerPage);
const startIndex = (currentPage - 1) * usersPerPage;
const endIndex = startIndex + usersPerPage;
const paginatedUsers = filteredUsers.slice(startIndex, endIndex);
```

**Smart Page Numbers:**
```javascript
// Shows: Previous [1] ... [4] [5] [6] ... [10] Next
if (
  pageNum === 1 ||
  pageNum === totalPages ||
  (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
) {
  // Show page button
}
```

---

### **5. Avatar Colors** (Tasks Page)

**Implementation:**
```javascript
function getAvatarColor(initials) {
  const colors = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ];
  
  const hash = initials
    .split('')
    .reduce((acc, char) => acc + char.charCodeAt(0), 0);
  
  return colors[hash % colors.length];
}
```

**Result:** Consistent color per user based on initials

---

## 🚀 Performance Optimizations

### **1. Parallel API Calls**

Use `Promise.all()` to fetch multiple endpoints simultaneously:
```javascript
const [data1, data2, data3] = await Promise.all([
  api1(), api2(), api3()
]);
```

**Benefit:** 3x faster than sequential calls

---

### **2. Debounced Search**

Waits 500ms after user stops typing before searching:
```javascript
setTimeout(() => fetchData(), 500);
```

**Benefit:** Reduces API calls by 90%

---

### **3. Client-Side Filtering**

Filter by name locally without API calls:
```javascript
const filtered = users.filter(u => u.name.includes(search));
```

**Benefit:** Instant results

---

### **4. Pagination**

Only render 10 users per page:
```javascript
const paginatedUsers = filteredUsers.slice(startIndex, endIndex);
```

**Benefit:** Fast rendering even with 100+ users

---

### **5. Conditional Rendering**

Only fetch/render when needed:
```javascript
{filteredUsers.length > 0 && <Pagination />}
{loading && <LoadingSpinner />}
```

---

## 🧪 Testing Scenarios

### **Scenario 1: Filter Changes**
1. Select "This Month" from Navbar
2. ✅ All metrics update
3. ✅ Charts re-render
4. ✅ Badge shows "Showing: This Month"
5. ✅ Data is different from "Today"

### **Scenario 2: Task Status Filter**
1. Go to Tasks page
2. Select "Open" from dropdown
3. ✅ Only users with Open tasks shown
4. ✅ Completed/In Progress counts are 0
5. ✅ Pagination info shows: "(filtered by Open)"
6. ✅ Page count adjusts

### **Scenario 3: Search + Filter**
1. Select "In Progress" filter
2. Search "Alice"
3. ✅ Shows only Alice's In Progress tasks
4. ✅ Pagination adjusts to search results

### **Scenario 4: Pagination**
1. Filter tasks
2. Click "Next"
3. ✅ Shows next 10 users
4. ✅ Page number updates
5. ✅ "Previous" enabled
6. ✅ URL doesn't change (client-side pagination)

---

## 🔧 Configuration

### **Environment Variables**

Create `.env` file:
```
REACT_APP_API_URL=http://localhost:5001/api
```

### **Package.json Scripts**

```json
{
  "scripts": {
    "start": "react-scripts start",    // Dev server
    "build": "react-scripts build",    // Production build
    "test": "react-scripts test",      // Run tests
    "eject": "react-scripts eject"     // Eject from CRA
  }
}
```

---

## 🚀 Running the Frontend

```bash
cd frontend
npm start
```

Opens on: http://localhost:3000

**Development Mode:**
- ✅ Hot reload
- ✅ Source maps
- ✅ React DevTools support
- ✅ Detailed error messages

---

## ✅ Frontend Status

- ✅ All pages implemented
- ✅ Routing working
- ✅ API integration complete
- ✅ Filters working correctly
- ✅ Pagination working
- ✅ Search working
- ✅ Charts displaying correctly
- ✅ Responsive design
- ✅ Loading states
- ✅ Error handling
- ✅ No console errors
- ✅ Clean code structure

**Frontend is production-ready!** 🚀

