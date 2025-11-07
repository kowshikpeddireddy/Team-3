import React, { useState, useEffect } from 'react';
import './Settings.css';
import { getSettings, saveSettings } from '../api/client';
import { Key, Bell, Save } from 'lucide-react';
import { motion } from 'framer-motion';

const fade = { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.3, ease: 'easeOut' } };

function Settings() {
  const [settings, setSettings] = useState({
    github_token: '',
    trello_key: '',
    trello_token: '',
    notifications: { task_updates: true, ai_insights: true, daily_digest: false }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await getSettings();
        setSettings(res.data);
      } catch (e) {
        console.error('Settings load error:', e);
      } finally { setLoading(false); }
    })();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await saveSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (e) {
      console.error('Settings save error:', e);
    } finally { setSaving(false); }
  };

  const toggle = (k) => setSettings(prev => ({ ...prev, notifications: { ...prev.notifications, [k]: !prev.notifications[k] }}));

  if (loading) return <div className="loading">Loading settings...</div>;

  return (
    <div className="settings-page holo-bg">
      <h1 className="page-title">Settings</h1>
      <p className="page-subtitle">Configure API connections and preferences</p>

      <motion.div className="settings-card holo-border" {...fade}>
        <div className="card-header"><Key size={24} color="#3b82f6" /><h3>API Configuration</h3></div>
        <div className="settings-form">
          <div className="form-group">
            <label>GitHub Personal Access Token</label>
            <input type="password" placeholder="ghp_xxxxxxxxxxxx" value={settings.github_token} onChange={(e) => setSettings(prev => ({ ...prev, github_token: e.target.value }))} />
            <p className="form-hint">Needed to fetch GitHub Issues</p>
          </div>
          <div className="form-group">
            <label>Trello API key</label>
            <input type="text" placeholder="Enter your Trello API Key" value={settings.trello_key} onChange={(e) => setSettings(prev => ({ ...prev, trello_key: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>Trello Token</label>
            <input type="text" placeholder="Enter your Trello token" value={settings.trello_token} onChange={(e) => setSettings(prev => ({ ...prev, trello_token: e.target.value }))} />
          </div>
          <motion.button className="save-button" onClick={handleSave} disabled={saving} whileTap={{ scale: 0.98 }}>
            <Save size={18} /> <span>{saving ? 'Saving...' : saved ? 'Saved!' : 'Save API Keys'}</span>
          </motion.button>
        </div>
      </motion.div>

      <motion.div className="settings-card holo-border" {...fade} transition={{ ...fade.transition, delay: 0.05 }}>
        <div className="card-header"><Bell size={24} color="#8b5cf6" /><h3>Notifications</h3></div>
        <div className="notifications-list">
          {[
            { key: 'task_updates', title: 'Task Updates', desc: 'Notify on task status changes' },
            { key: 'ai_insights', title: 'AI Insights', desc: 'Receive AI-generated summaries' },
            { key: 'daily_digest', title: 'Daily Digest', desc: 'Get daily productivity reports' },
          ].map((n) => (
            <div key={n.key} className="notification-item">
              <div><h4>{n.title}</h4><p>{n.desc}</p></div>
              <label className="toggle-switch">
                <input type="checkbox" checked={settings.notifications[n.key]} onChange={() => toggle(n.key)} />
                <span className="toggle-slider"></span>
              </label>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

export default Settings;