# Horse Betting Frontend

A React-based frontend for the Family Horse Betting application with optimized loading and performance features.

## Performance Improvements

### 🚀 Loading Optimizations
- **Progressive Loading**: Data is loaded sequentially to avoid overwhelming the server
- **Individual Loading States**: Each data type (users, races, bets, bankers) has its own loading state
- **Skeleton Screens**: Beautiful loading placeholders while data is being fetched
- **Request Timeouts**: 15-second timeout for all API requests to prevent hanging

### 💾 Caching System
- **Smart Caching**: API responses are cached for 5 minutes to reduce server load
- **Cache Validation**: Automatic cache invalidation and refresh
- **Force Refresh**: Manual refresh option to bypass cache when needed

### 🔄 Retry Mechanism
- **Automatic Retries**: Failed requests are automatically retried up to 2 times
- **Progressive Delays**: 2-second delay between retry attempts
- **Smart Error Handling**: Different error messages for timeouts vs. connection issues

### 📱 User Experience
- **Loading Progress Bar**: Visual progress indicator for data loading
- **Connection Status**: Real-time server connection status display
- **Offline State**: Graceful handling when server is unavailable
- **Loading Indicators**: Spinning indicators in tabs and buttons during operations

### 🎯 Performance Features
- **Request Batching**: Related requests are grouped to reduce server load
- **Debounced Updates**: Prevents excessive API calls during rapid interactions
- **Memory Management**: Efficient state management and cleanup

## Usage

### Loading States
The app shows different loading states for each section:
- **Leaderboard**: Shows skeleton cards while users load
- **Races**: Shows skeleton race cards while race data loads
- **User Bets**: Shows loading spinner with specific loading messages
- **Admin Panel**: Shows loading spinner with detailed status

### Cache Management
- Cache automatically expires after 5 minutes
- Use the refresh button to force a fresh data fetch
- Cache status is displayed in the header

### Connection Handling
- Green indicator when connected
- Red indicator when disconnected
- Automatic retry on connection loss
- Manual retry button available

## Technical Details

### API Endpoints
- Users: `/api/users`
- Races: `/api/races`
- Bets: `/api/bets`
- Bankers: `/api/bankers`

### Timeout Configuration
- Request timeout: 15 seconds
- Retry attempts: 2
- Retry delay: 2 seconds
- Cache duration: 5 minutes

### Error Handling
- Network timeouts
- Server errors (4xx, 5xx)
- Connection failures
- Data validation errors

## Development

### Prerequisites
- Node.js 14+
- npm or yarn

### Installation
```bash
cd horse-betting-frontend
npm install
```

### Running
```bash
npm start
```

### Building
```bash
npm run build
```

## Performance Monitoring

The app includes built-in performance monitoring:
- Loading progress tracking
- Cache hit/miss statistics
- Connection status monitoring
- Request timing information

## Troubleshooting

### Slow Loading
1. Check server status in the header
2. Use the refresh button to force reload
3. Check network connectivity
4. Verify backend server is running

### Connection Issues
1. Look for red connection indicator
2. Click retry button
3. Check backend server logs
4. Verify API endpoint accessibility

### Data Not Updating
1. Check cache status in header
2. Use force refresh button
3. Verify backend data changes
4. Check browser console for errors
