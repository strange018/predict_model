## 🚀 QUICK START - VERIFY UI UPDATES ARE WORKING

This guide walks you through verifying that button clicks are updating the UI in real-time.

### ✅ SETUP (One-Time)

1. **Verify Backend is Running:**
   ```
   Open PowerShell and run:
   cd "c:\Users\HP\OneDrive\Desktop\hackathon project"
   python app.py
   
   You should see:
   "WARNING in app.run() ... (use TOOLS=werkzeug.serving.WSGIRequestHandler, ...)
   * Running on http://127.0.0.1:5000
   * Debugger is active!"
   ```

2. **Open Two Browser Tabs:**
   - **Tab 1 (Main UI):** http://127.0.0.1:5000
   - **Tab 2 (Debug Console):** http://127.0.0.1:5000/console-monitor
   
   This lets you see both the UI and the live console logs at the same time.

---

### 📊 VERIFY POLLING IS WORKING

**In Tab 2 (Console Monitor), you should see logs like:**

```
📈 Polling stats...
✓ Received 5 nodes: worker-01(taints:0), worker-02(taints:0), ...
🖥️  Polling nodes...
📦 Rendering 5 nodes...
  Current cards: 5, New nodes: 5
  → Updating existing cards
  ✓ Updated card 0: worker-01
  ✓ Updated card 1: worker-02
  ...
```

**If you see these logs every 1-2 seconds, polling is working correctly!**

If you DON'T see these logs:
- Check that the backend is running (see SETUP)
- Refresh the page (Ctrl+R)
- Check browser console (F12) for any errors

---

### 🧪 TEST BUTTON CLICK (The Real Test)

#### Before Click:

**In Tab 1 (Main UI):**
- Look at any node card (e.g., "worker-01")
- The "Taint" button should be **enabled** (not grayed out)
- The "Taint" badge should **NOT** be visible

#### Click Taint Button:

**In Tab 2 (Console Monitor), you should see:**

```
Tainting node: node-01
🔄 Fetching nodes...
✓ Taint response OK
📈 Polling stats...
✓ Received 5 nodes: worker-01(taints:1), ...
     ↑ NOTE: taints:1 means taint was applied!
```

#### After Click (1-2 seconds later):

**In Tab 1 (Main UI):**
- The node card should show a **taint badge**: `degradation=true:NoSchedule` (in orange/red)
- The "Taint" button should now be **disabled** (grayed out)
- The "Remove Taint" button should now be **enabled**
- The node status indicator (dot at top-left) should be **orange** instead of green

---

### ✨ SUCCESS INDICATORS

If all of these are happening, the system is working correctly:

- ✅ Console Monitor (Tab 2) shows polling logs every 1-2 seconds
- ✅ When you click "Taint", the console shows:
  - "Tainting node..."  
  - Taint response 200
  - Node count updated with "taints:1"
- ✅ In main UI (Tab 1), you see taint badge appear on the card
- ✅ In main UI, buttons update their enabled/disabled state

---

### 🔧 TROUBLESHOOTING

| What's Not Working | Fix |
|------------------|-----|
| No polling logs at all (Tab 2) | Backend not running; do: `python app.py` |
| Taint logs show, but no badge in UI | Refresh browser (Ctrl+R) to load new script.js |
| Badge appears but buttons don't update | Clear cache: Ctrl+Shift+Delete, then refresh |
| Console shows errors | Check backend is running; check app.py for syntax errors |
| One button is always disabled | The node state in backend may not match expectation |

---

### 🎯 WHAT EACH BUTTON DOES

**Taint:**
- Adds a scheduling prevention to the node
- Should disable the "Taint" button
- Should enable the "Remove Taint" button
- Should show orange taint badge with: `degradation=true:NoSchedule`
- Should change status indicator to orange

**Remove Taint:**
- Removes the scheduling prevention
- Should enable the "Taint" button
- Should disable the "Remove Taint" button  
- Should remove the taint badge
- Should change status indicator back to green

**Drain:**
- Simulates moving workloads off the node
- In the events list, you should see: "Simulated drain of X pods from node-XX"
- Might show 0 pods if demo mode doesn't have pods

---

### 📋 NEXT STEPS

Once you confirm:
1. ✅ Polling is working (see logs every 1-2 seconds)
2. ✅ Button clicks taint/untaint nodes
3. ✅ UI updates with badges and button states
4. ✅ Events list shows actions in real-time

Then you're ready to:
- Test with a real Kubernetes cluster (if available)
- Deploy with Docker/Compose
- Integrate with your infrastructure

---

### 🆘 HAVING ISSUES?

1. **Backend not responding?**
   ```
   netstat -ano | findstr :5000
   ```
   Should show: `TCP ... LISTENING 11380`
   
   If not, start it:
   ```
   cd "c:\Users\HP\OneDrive\Desktop\hackathon project"
   python app.py
   ```

2. **Still seeing "not updating"?**
   - Tab 1: Press **Ctrl+Shift+R** (hard refresh)
   - Tab 2: Press **Ctrl+Shift+R** (hard refresh)
   - Then test again

3. **Want to test without the UI?**
   ```
   python test_ui_updates.py
   ```
   This tests the backend API directly without the browser

4. **Check detailed debugging:**
   - See [DEBUG_GUIDE.md](DEBUG_GUIDE.md) for step-by-step console debugging
   - See [FILES_INDEX.md](FILES_INDEX.md) for an overview of all project files
