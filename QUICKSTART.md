# ⚡ PULSEVO - 2-Minute Quickstart

Get PULSEVO running in 2 minutes!

## 🚀 Terminal 1 - Backend

```bash
cd /Users/kowshik/Desktop/Hackathon/backend
pip3 install -r requirements.txt
python3 seed_data.py
python3 app.py
```

**Wait for:** `🚀 Server running on http://localhost:5000`

---

## 🎨 Terminal 2 - Frontend

Open a **NEW terminal** window:

```bash
cd /Users/kowshik/Desktop/Hackathon/frontend
npm install
npm start
```

**Wait for:** Browser opens automatically to `http://localhost:3000`

---

## ✅ Done!

Your dashboard should now be running with:
- 📊 Overview with real-time metrics
- ✅ Task management with 100 sample tasks
- 🤖 AI insights and predictions
- 💬 Conversational query interface
- ⚙️ Settings page

---

## 🎯 Quick Test

1. **Overview**: See metrics and charts
2. **Tasks**: Search for "Alice" in the search box
3. **AI Insights**: View team benchmarking
4. **Query**: Ask "How many bugs did we close?"
5. **Settings**: Toggle notification switches

---

## ⚠️ Troubleshooting

**Port 5000 busy?**
```bash
lsof -ti:5000 | xargs kill -9
python3 app.py
```

**npm install fails?**
```bash
npm install --legacy-peer-deps
```

---

## 📚 Need More Help?

- Full Setup: See `SETUP_GUIDE.md`
- Documentation: See `README.md`
- API Reference: See `README.md` → API Endpoints section

---

**Time: ~2 minutes** ⏱️

Happy coding! 🎉

