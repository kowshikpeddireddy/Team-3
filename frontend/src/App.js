import React, { useState } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import './App.css';
import Navbar from './components/Navbar';
import Overview from './pages/Overview';
import Tasks from './pages/Tasks';
import AIInsights from './pages/AIInsights';
import Queries from './pages/Queries';
import Settings from './pages/Settings';

function App() {
  const [activePage, setActivePage] = useState('overview');
  const [timeFilter, setTimeFilter] = useState('today');

  const renderPage = () => {
    switch (activePage) {
      case 'overview':
        return <Overview timeFilter={timeFilter} />;
      case 'tasks':
        return <Tasks timeFilter={timeFilter} />;
      case 'ai-insights':
        return <AIInsights timeFilter={timeFilter} />;
      case 'queries':
        return <Queries />;
      case 'settings':
        return <Settings />;
      default:
        return <Overview timeFilter={timeFilter} />;
    }
  };

  return (
    <Router>
      <div className="App">
        <Navbar 
          timeFilter={timeFilter} 
          setTimeFilter={setTimeFilter}
          activePage={activePage}
          setActivePage={setActivePage}
        />
        <div className="app-container">
          <main className="main-content">
            {renderPage()}
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;

