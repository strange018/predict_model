## DEBUG GUIDE: UI NOT UPDATING

This guide helps diagnose why the buttons might not be updating the UI in real-time.

### Step 1: Verify Backend is Running
```
Open PowerShell and run:
  netstat -ano | findstr :5000

Should show:
  TCP    127.0.0.1:5000    LISTENING    [PID]
```

If NOT showing, start the backend:
```
cd "c:\Users\HP\OneDrive\Desktop\hackathon project"
python app.py
```

### Step 2: Open Browser Console
1. **Open Browser** → Go to http://127.0.0.1:5000
2. **Press F12** to open Developer Tools
3. **Click the "Console" tab** at the top
4. You should see logs starting with:
   ```
   ✓ Connected to backend API
   📊 Starting monitoring...
   ```

### Step 3: Watch for Polling Activity
Keep the console open and **watch for the polling logs** every ~1 second:
```
📈 Polling stats...
✓ Received 5 nodes: worker-01(taints:0), worker-02(taints:0), ...
🖥️  Polling nodes...
📦 Rendering 5 nodes...
```

If you see these logs, the polling is working correctly.

### Step 4: Test Button Click
1. In the browser, **click the "Taint" button** on any node card
2. Watch the console - you should see:
   ```
   Tainting node: node-01
   🔄 Fetching nodes...
   ✓ Taint response OK
   ✓ Received 5 nodes: worker-01(taints:1), ...  ← TAINT COUNT CHANGED!
   📦 Rendering 5 nodes...
     Current cards: 5, New nodes: 5
     → Updating existing cards
     ✓ Updated card 0: worker-01
   ```

3. **Look at the node card in the browser** - it should now:
   - Show a red/orange taint badge: `degradation=true:NoSchedule`
   - Have the "Taint" button DISABLED (grayed out)
   - Have the "Remove Taint" button ENABLED

### Step 5: If Updates Are NOT Showing

**If the console shows the correct data but the UI isn't updating:**

1. **Try a browser refresh** (Ctrl+R or Cmd+R)
   - This reloads the latest script.js with all fixes

2. **Check if CSS is hiding the updates:**
   - Right-click on a node card → "Inspect" (or press F12)
   - Look for a `<span class="taint-badge">...</span>` element
   - If it exists but isn't visible, CSS might be hiding it

3. **Clear browser cache** (in DevTools):
   - Press Ctrl+Shift+Delete
   - Select "Cached images and files"
   - Click "Clear now"
   - Refresh the page

### Step 6: If Everything Looks Good

Once you see:
- ✓ Backend responding (health check)
- ✓ Polling logs every second
- ✓ Node data changing on button click (in console)
- ✓ UI showing taint badges and disabled buttons

Then the system is working correctly!

## Testing Commands

If you want to manually test without the browser UI, run:
```
cd "c:\Users\HP\OneDrive\Desktop\hackathon project"
python test_ui_updates.py
```

This will test:
- ✓ Backend health
- ✓ Taint action (should apply and show in return data)
- ✓ Remove-taint action (should remove and show in return data)  
- ✓ Drain action (should reduce pod count)

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Tainting..." text never disappears | Button not re-enabling | Refresh browser to load new script.js |
| Taint badge doesn't appear | Script not loaded | Ctrl+R to refresh |
| Logs not showing in console | Old page still loaded | Ctrl+Shift+R (force refresh) |
| Buttons disabled/enabled wrong | Old data cached | Clear cache (Ctrl+Shift+Delete) |
| No polling logs at all | Page not connected to backend | Check backend is running on port 5000 |

## What Should Happen (Step by Step)

**BEFORE clicking Taint:**
```
Node: worker-01
- Taint button: ENABLED
- Remove Taint button: DISABLED
- No taint badges visible
```

**AFTER clicking Taint:**
```
Node: worker-01
- Taint button: DISABLED (shows "Tainting..." briefly, then "Taint")
- Remove Taint button: ENABLED
- Taint badge visible: "degradation=true:NoSchedule"
- Status indicator: ORANGE (tainted)
```

**AFTER clicking Remove Taint:**
```
Node: worker-01
- Taint button: ENABLED
- Remove Taint button: DISABLED
- No taint badges visible
- Status indicator: GREEN (healthy) or appropriate color
```

## Next Steps

Once updates are working:
1. Test all three buttons (Taint, Remove Taint, Drain)
2. Watch events list update in real-time
3. Monitor stats counters at top
4. Consider connecting to real Kubernetes cluster (if ready)
