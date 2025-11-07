import React, { useState, useEffect } from 'react';
import './Settings.css';
import { getSettings, saveSettings } from '../api/client';
import { Key, Bell, Save } from 'lucide-react';

function Settings() {
  const [settings, setSettings] = useState({
    github_token: '',
    trello_key: '',
    trello_token: '',
    notifications: {
      task_updates: true,
      ai_insights: true,
      daily_digest: false
    }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await getSettings();
      setSettings(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching settings:', error);
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await saveSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleNotificationToggle = (key) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: !prev.notifications[key]
      }
    }));
  };

  if (loading) {
    return <div className="loading">Loading settings...</div>;
  }

  return (
    <div className="settings-page">
      <h1 className="page-title">Settings</h1>
      <p className="page-subtitle">Configure API connections and preferences</p>

      {/* API Configuration */}
      <div className="settings-card">
        <div className="card-header">
          <Key size={24} color="#3b82f6" />
          <h3>API Configuration</h3>
        </div>

        <div className="settings-form">
          <div className="form-group">
            <label>GitHub Personal Access Token</label>
            <input
              type="password"
              placeholder="ghp_xxxxxxxxxxxx"
              value={settings.github_token}
              onChange={(e) => setSettings(prev => ({ ...prev, github_token: e.target.value }))}
            />
            <p className="form-hint">Required for fetching GitHub Issues data</p>
          </div>

          <div className="form-group">
            <label>Trello API key</label>
            <input
              type="text"
              placeholder="Enter your Trello API Key"
              value={settings.trello_key}
              onChange={(e) => setSettings(prev => ({ ...prev, trello_key: e.target.value }))}
            />
          </div>

          <div className="form-group">
            <label>Trello Token</label>
            <input
              type="text"
              placeholder="Enter your Trello token"
              value={settings.trello_token}
              onChange={(e) => setSettings(prev => ({ ...prev, trello_token: e.target.value }))}
            />
          </div>

          <button className="save-button" onClick={handleSave} disabled={saving}>
            <Save size={18} />
            <span>{saving ? 'Saving...' : saved ? 'Saved!' : 'Save API Keys'}</span>
          </button>
        </div>
      </div>

      {/* Notifications */}
      <div className="settings-card">
        <div className="card-header">
          <Bell size={24} color="#8b5cf6" />
          <h3>Notifications</h3>
        </div>

        <div className="notifications-list">
          <div className="notification-item">
            <div>
              <h4>Task Updates</h4>
              <p>Notify on task status changes</p>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={settings.notifications.task_updates}
                onChange={() => handleNotificationToggle('task_updates')}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="notification-item">
            <div>
              <h4>AI Insights</h4>
              <p>Receive AI-generated summaries</p>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={settings.notifications.ai_insights}
                onChange={() => handleNotificationToggle('ai_insights')}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="notification-item">
            <div>
              <h4>Daily Digest</h4>
              <p>Get daily productivity reports</p>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={settings.notifications.daily_digest}
                onChange={() => handleNotificationToggle('daily_digest')}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;

