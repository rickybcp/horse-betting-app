# Local Testing Guide

This guide will help you test the Horse Betting application locally before deploying to production.

## Prerequisites

Make sure you have the following installed:
- **Python 3.7+** with pip
- **Node.js 14+** with npm
- **Git** (for version control)

## Quick Start (Windows)

### Option 1: Using the Batch Script
1. Double-click `start-local.bat`
2. Wait for both servers to start
3. Open http://localhost:3000 in your browser

### Option 2: Using PowerShell
1. Right-click `start-local.ps1` and select "Run with PowerShell"
2. Wait for both servers to start
3. Open http://localhost:3000 in your browser

## Manual Setup

### 1. Start the Backend Server
```bash
# In the root directory (where server.py is located)
python server.py
```

You should see:
```
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://[your-ip]:5000
```

### 2. Test the Backend
```bash
# In a new terminal, run the test script
python test-backend.py
```

Expected output:
```
Testing Horse Betting Backend API
========================================

✓ GET /users: 200
  Data: 0 items

✓ GET /races: 200
  Data: 0 items

✓ GET /bets: 200
  Data: 0 keys

✓ GET /bankers: 200
  Data: 0 keys

Testing POST endpoints...
✓ POST /users: 200
  Data: 1 keys

========================================
Test Results: 5/5 endpoints working
🎉 All tests passed! Backend is ready.
```

### 3. Start the Frontend
```bash
# In a new terminal, navigate to the frontend directory
cd horse-betting-frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm start
```

You should see:
```
Compiled successfully!

You can now view horse-betting-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

## Testing the Performance Improvements

### 1. **Loading States**
- Open http://localhost:3000
- Watch for skeleton screens and loading indicators
- Notice the progressive loading (users → races → bets → bankers)

### 2. **Caching System**
- Refresh the page multiple times
- Check the browser console for cache hits
- Use the refresh button to force fresh data

### 3. **Connection Status**
- Look for the green connection indicator
- Check the loading progress bar
- Monitor the cache status display

### 4. **Error Handling**
- Stop the backend server temporarily
- Watch the frontend show offline state
- Restart backend and see reconnection

### 5. **Performance Testing**
- Open browser DevTools (F12)
- Go to Network tab
- Refresh the page and observe:
  - Sequential API calls
  - Response times
  - Cache effectiveness

## Expected Behavior

### ✅ **What You Should See:**
- **Immediate Loading**: Skeleton screens appear instantly
- **Progressive Loading**: Data loads in sequence, not all at once
- **Smart Caching**: Subsequent page loads are faster
- **Connection Status**: Clear indicators of server state
- **Error Recovery**: Automatic retries and graceful fallbacks

### 🔍 **Performance Indicators:**
- **First Load**: 2-5 seconds (depending on backend speed)
- **Cached Load**: Under 1 second
- **API Response Times**: Under 2 seconds for local backend
- **Memory Usage**: Stable, no memory leaks

## Troubleshooting

### Backend Won't Start
```bash
# Check if port 5000 is in use
netstat -an | findstr :5000

# Kill process using port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Frontend Won't Start
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues
```bash
# Test backend directly
curl http://localhost:5000/api/users

# Check CORS settings in server.py
# Verify API_BASE in App.js
```

### Performance Issues
- Check browser console for errors
- Monitor Network tab in DevTools
- Verify backend response times
- Check for memory leaks in React DevTools

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] API endpoints respond correctly
- [ ] Skeleton screens appear immediately
- [ ] Progressive loading works
- [ ] Caching system functions
- [ ] Connection status updates
- [ ] Error handling works
- [ ] Performance is acceptable
- [ ] No console errors
- [ ] All tabs load correctly

## Next Steps

Once local testing passes:
1. **Deploy Backend**: Update your Render deployment
2. **Deploy Frontend**: Build and deploy to your hosting service
3. **Monitor**: Watch for any production issues
4. **Optimize**: Use production metrics to further improve performance

## Support

If you encounter issues:
1. Check the browser console for errors
2. Verify both servers are running
3. Test API endpoints directly
4. Check the troubleshooting section above
5. Review the README.md for additional details 