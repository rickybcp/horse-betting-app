// App.js (Revised script)

import React, { useState, useEffect, useCallback } from 'react';
import { Users, Trophy, Calendar, Settings, Plus, RefreshCw, Clock, Star, Download, AlertCircle } from 'lucide-react';

const API_BASE = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:5000/api'
  : "https://horse-betting-backend.onrender.com/api";

// Debug: Log the API URL being used
console.log('NODE_ENV:', process.env.NODE_ENV);
console.log('API_BASE URL:', API_BASE);
console.log('Environment variable:', process.env.REACT_APP_API_URL);

// --- Loading Skeleton Components ---
const SkeletonCard = () => (
  <div className="bg-white p-4 rounded-lg shadow animate-pulse">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
  </div>
);

const SkeletonLeaderboard = () => (
  <div className="space-y-4">
    <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white p-6 rounded-lg">
      <h2 className="text-2xl font-bold flex items-center gap-2">
        <Trophy className="w-6 h-6" />
        Leaderboard
      </h2>
    </div>
    {[1, 2, 3, 4, 5].map(i => (
      <div key={i} className="bg-white p-4 rounded-lg shadow flex justify-between items-center animate-pulse">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
          <div className="h-4 bg-gray-200 rounded w-24"></div>
        </div>
        <div className="h-4 bg-gray-200 rounded w-16"></div>
      </div>
    ))}
  </div>
);

const SkeletonRaces = () => (
  <div className="space-y-4">
    <div className="bg-gradient-to-r from-green-400 to-green-600 text-white p-6 rounded-lg">
      <h2 className="text-2xl font-bold flex items-center gap-2">
        <Calendar className="w-6 h-6" />
        Today's Races
      </h2>
    </div>
    {[1, 2, 3].map(i => (
      <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
        <div className="h-5 bg-gray-200 rounded w-32 mb-3"></div>
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map(j => (
            <div key={j} className="text-center">
              <div className="h-4 bg-gray-200 rounded w-16 mx-auto mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-12 mx-auto mb-1"></div>
              <div className="h-3 bg-gray-200 rounded w-8 mx-auto"></div>
            </div>
          ))}
        </div>
      </div>
    ))}
  </div>
);

// --- Reusable Confirmation Modal Component ---
const ConfirmationModal = ({ show, message, onConfirm, onCancel }) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-sm w-full">
        <p className="text-lg font-semibold mb-4">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};

// --- Message Display Component ---
const MessageDisplay = ({ message }) => {
  if (!message) return null;
  
  const messageType = message.includes('Error') || message.includes('failed') ? 'error' : 
                      message.includes('Success') || message.includes('successfully') ? 'success' : 'info';
  
  const bgColor = messageType === 'error' ? 'bg-red-100 text-red-800 border-red-200' :
                  messageType === 'success' ? 'bg-green-100 text-green-800 border-green-200' :
                  'bg-blue-100 text-blue-800 border-blue-200';

  return (
    <div className={`fixed top-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 border ${bgColor}`}>
      {message}
    </div>
  );
};

// --- Connection Status Component ---
const ConnectionStatus = ({ serverConnected, retryConnection }) => (
  <div className={`fixed top-4 left-4 px-4 py-2 rounded-lg shadow-lg z-50 border ${
    serverConnected 
      ? 'bg-green-100 text-green-800 border-green-200' 
      : 'bg-red-100 text-red-800 border-red-200'
  }`}>
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${serverConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
      <span className="text-sm font-medium">
        {serverConnected ? 'Connected' : 'Disconnected'}
      </span>
      {!serverConnected && (
        <button
          onClick={retryConnection}
          className="ml-2 px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600 transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  </div>
);

// --- Leaderboard Tab Component ---
const LeaderboardTab = ({ users, calculateUserScore, bankers, setActiveTab }) => (
  <div className="space-y-4">
    <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white p-6 rounded-lg">
      <h2 className="text-2xl font-bold flex items-center gap-2">
        <Trophy className="w-6 h-6" />
        Leaderboard
      </h2>
    </div>
    
    {users.length === 0 ? (
      <div className="bg-white p-6 rounded-lg shadow text-center">
        <div className="text-gray-400 mb-4">
          <Users className="w-16 h-16 mx-auto mb-2" />
        </div>
        <h3 className="text-lg font-semibold text-gray-600 mb-2">No Users Yet</h3>
        <p className="text-gray-500 mb-4">
          Get started by adding family members in the Admin panel.
        </p>
        <button
          onClick={() => setActiveTab('admin')}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Go to Admin Panel
        </button>
      </div>
    ) : (
      <div className="space-y-2">
        {users
          .map(user => ({
            ...user,
            dailyScore: calculateUserScore(user.id)
          }))
          .sort((a, b) => (b.totalScore + b.dailyScore) - (a.totalScore + a.dailyScore))
          .map((user, index) => (
            <div key={user.id} className="bg-white p-4 rounded-lg shadow flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                  index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-yellow-600' : 'bg-gray-300'
                }`}>
                  {index + 1}
                </div>
                <span className="font-semibold">{user.name}</span>
              </div>
              <div className="text-right">
                <div className="font-bold text-lg">{user.totalScore + user.dailyScore} pts</div>
                <div className="text-sm text-gray-500">
                  Total: {user.totalScore} + Today: {user.dailyScore}
                  {bankers[user.id] && <Star className="w-4 h-4 inline ml-1 text-yellow-500" />}
                </div>
              </div>
            </div>
          ))}
      </div>
    )}
  </div>
);

// --- Race Day Tab Component ---
const RaceDayTab = ({ races, isBettingAllowed, setActiveTab }) => (
  <div className="space-y-4">
    <div className="bg-gradient-to-r from-blue-500 to-blue-700 text-white p-6 rounded-lg">
      <h2 className="text-2xl font-bold flex items-center gap-2">
        <Calendar className="w-6 h-6" />
        Today's Races
      </h2>
    </div>

    {races.length === 0 ? (
      <div className="bg-white p-6 rounded-lg shadow text-center">
        <p className="text-gray-500 mb-4">No races loaded. Use the Admin panel to scrape races.</p>
        <button
          onClick={() => setActiveTab('admin')}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Go to Admin Panel
        </button>
      </div>
    ) : (
      races.map(race => (
        <div key={race.id} className="bg-white p-4 rounded-lg shadow">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold">{race.name}</h3>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span className={`px-2 py-1 rounded text-sm ${
                isBettingAllowed(race.time) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {race.time} {isBettingAllowed(race.time) ? '(Open)' : '(Closed)'}
              </span>
            </div>
          </div>

          <div className="grid gap-2">
            {race.horses.map(horse => (
              <div key={horse.number} className={`p-3 border rounded flex justify-between items-center ${
                race.winner === horse.number ? 'bg-green-100 border-green-500' : 'border-gray-200'
              }`}>
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center font-bold">
                    {horse.number}
                  </span>
                  <span className="font-medium">{horse.name}</span>
                  {race.winner === horse.number && <Trophy className="w-5 h-5 text-green-600" />}
                </div>
                <div className="text-right">
                  <div className="font-bold">{horse.odds.toFixed(1)}</div>
                  <div className="text-sm text-gray-500">{horse.points} pts</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))
    )}
  </div>
);

// --- User Bets Tab Component ---
const UserBetsTab = ({ users, selectedUser, setSelectedUser, races, bets, bankers, placeBet, setBanker, showMessage, isBettingAllowed, calculateUserScore, setActiveTab }) => (
  <div className="space-y-4">
    <div className="bg-gradient-to-r from-green-500 to-green-700 text-white p-6 rounded-lg">
      <h2 className="text-2xl font-bold flex items-center gap-2">
        <Users className="w-6 h-6" />
        Place Your Bets
      </h2>
    </div>

    <div className="bg-white p-4 rounded-lg shadow">
      <label className="block text-sm font-medium mb-2">Select User:</label>
      <select
        value={selectedUser}
        onChange={(e) => setSelectedUser(e.target.value)}
        className="w-full p-2 border rounded-lg"
      >
        <option value="">Choose your name...</option>
        {users.map(user => (
          <option key={user.id} value={user.id}>{user.name}</option>
        ))}
      </select>
    </div>

    {selectedUser && races.length > 0 ? (
      <>
        {races.map(race => {
          const userBet = bets[selectedUser]?.[race.id];
          const isBankerRace = bankers[selectedUser] === race.id;
          
          return (
            <div key={race.id} className="bg-white p-4 rounded-lg shadow">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-semibold">{race.name}</h3>
                <span className={`px-2 py-1 rounded text-sm ${
                  isBettingAllowed(race.time) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {race.time}
                </span>
              </div>

              <div className="grid gap-2">
                {race.horses.map(horse => {
                  const isSelected = userBet === horse.number;
                  
                  return (
                    <button
                      key={horse.number}
                      onClick={() => placeBet(selectedUser, race.id, horse.number)}
                      disabled={!isBettingAllowed(race.time)}
                      className={`p-3 border rounded flex justify-between items-center transition-colors ${
                        isSelected ? 'bg-blue-100 border-blue-500' : 'border-gray-200 hover:bg-gray-50'
                      } ${!isBettingAllowed(race.time) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center font-bold">
                          {horse.number}
                        </span>
                        <span className="font-medium">{horse.name}</span>
                        {isSelected && isBankerRace && <Star className="w-5 h-5 text-yellow-500 fill-current" />}
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{horse.odds.toFixed(1)}</div>
                        <div className="text-sm text-gray-500">{horse.points} pts</div>
                      </div>
                    </button>
                  );
                })}
              </div>

              {userBet && (
                <div className="mt-2 text-center">
                  <button
                    onClick={() => setBanker(selectedUser, race.id)}
                    disabled={isBankerRace}
                    className={`px-4 py-2 rounded transition-colors ${
                      isBankerRace
                        ? 'bg-yellow-200 text-yellow-800 cursor-not-allowed'
                        : 'bg-yellow-500 text-white hover:bg-yellow-600'
                    }`}
                  >
                    {isBankerRace
                      ? 'This is your Banker Race ⭐' 
                      : 'Set this Race as Banker (Double Points)'}
                  </button>
                </div>
              )}
            </div>
          );
        })}

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">Your Bets Summary:</h3>
          {races.length === 0 ? (
            <p className="text-gray-500">No races available</p>
          ) : (
            races.map(race => {
              const userBet = bets[selectedUser]?.[race.id];
              const horse = race.horses.find(h => h.number === userBet);
              const isBankerRace = bankers[selectedUser] === race.id;
              
              return (
                <div key={race.id} className="flex justify-between py-1">
                  <span>{race.name}:</span>
                  <span>
                    {horse ? `#${horse.number} ${horse.name}` : 'No bet'}
                    {isBankerRace && <Star className="w-4 h-4 inline ml-1 text-yellow-500 fill-current" />}
                  </span>
                </div>
              );
            })
          )}
          <div className="mt-3 pt-2 border-t">
            <div className="flex justify-between font-semibold">
              <span>Expected Daily Score:</span>
              <span>{calculateUserScore(selectedUser)} pts</span>
            </div>
          </div>
        </div>
      </>
    ) : selectedUser && races.length === 0 ? (
      <div className="bg-white p-6 rounded-lg shadow text-center">
        <p className="text-gray-500 mb-4">No races available. Ask an admin to scrape today's races.</p>
        <button
          onClick={() => setActiveTab('admin')}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Go to Admin Panel
        </button>
      </div>
    ) : (
      <div className="bg-white p-6 rounded-lg shadow text-center">
        <p className="text-gray-500">Please select your name to start betting!</p>
      </div>
    )}
  </div>
);

// --- Admin Tab Component ---
const AdminTab = ({ newUserName, setNewUserName, addUser, loading, scrapeRaces, scrapeResults, resetForNewDay, races, setRaceResult, users, bets, bankers, serverConnected }) => {
  // Helper to calculate score for display in admin panel if needed
  const calculatePoints = useCallback((odds) => {
    if (odds > 10) return 3;
    if (odds > 5) return 2;
    return 1;
  }, []);

  const calculateUserScoreForAdmin = useCallback((userId) => {
    let dailyScore = 0;
    if (Array.isArray(races)) {
      races.forEach(race => {
        if (race.winner && bets[userId] && bets[userId][race.id]) {
          const userBet = bets[userId][race.id];
          if (userBet === race.winner) {
            const horse = race.horses.find(h => h.number === race.winner);
            if (horse) {
              dailyScore += calculatePoints(horse.odds);
            }
          }
        }
      });

      // Apply banker bonus
      if (bankers[userId]) {
        const bankerRace = races.find(race => race.id === bankers[userId]);
        if (bankerRace && bets[userId]?.[bankerRace.id] === bankerRace.winner) {
          dailyScore *= 2;
        }
      }
    } else {
      console.warn("Races data is not an array in calculateUserScoreForAdmin:", races);
    }
    return dailyScore;
  }, [races, bets, bankers, calculatePoints]);

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-purple-500 to-purple-700 text-white p-6 rounded-lg">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Settings className="w-6 h-6" />
          Admin Panel
        </h2>
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="font-semibold mb-2">Add New User:</h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={newUserName}
            onChange={(e) => setNewUserName(e.target.value)}
            placeholder="Enter name..."
            className="flex-1 p-2 border rounded-lg"
            onKeyPress={(e) => e.key === 'Enter' && addUser()}
          />
          <button
            onClick={addUser}
            disabled={!newUserName.trim()}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="w-4 h-4" />
            Add
          </button>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="font-semibold mb-3">Race Management:</h3>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={scrapeRaces}
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Scrape New Races
          </button>
          <button
            onClick={scrapeResults}
            disabled={loading}
            className="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            Scrape Results
          </button>
          <button
            onClick={resetForNewDay}
            disabled={loading}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50"
          >
            Reset for New Day
          </button>
        </div>
        {loading && (
          <div className="mt-2 text-sm text-gray-600">
            Processing... This may take a few moments.
          </div>
        )}
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="font-semibold mb-3">Manual Race Results:</h3>
        {races.length === 0 ? (
          <p className="text-gray-500">No races loaded. Scrape races first.</p>
        ) : (
          races.map(race => (
            <div key={race.id} className="mb-4 p-3 border rounded">
              <h4 className="font-medium mb-2 flex items-center gap-2">
                {race.name} - {race.time}
                {race.winner && <Trophy className="w-4 h-4 text-green-600" />}
                {race.status === 'completed' && (
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                    Completed
                  </span>
                )}
              </h4>
              <div className="flex gap-2 flex-wrap">
                {race.horses.map(horse => (
                  <button
                    key={horse.number}
                    onClick={() => setRaceResult(race.id, horse.number)}
                    className={`px-3 py-1 rounded text-sm transition-colors ${
                      race.winner === horse.number
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                  >
                    #{horse.number} {horse.name}
                  </button>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="font-semibold mb-2">Current Status:</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Users:</span> {users.length}
          </div>
          <div>
            <span className="text-gray-600">Races:</span> {races.length}
          </div>
          <div>
            <span className="text-gray-600">Total Bets:</span> {Object.values(bets).reduce((sum, userBets) => sum + Object.keys(userBets).length, 0)}
          </div>
          <div>
            <span className="text-gray-600">Bankers Set:</span> {Object.keys(bankers).length}
          </div>
          <div>
            <span className="text-gray-600">Completed Races:</span> {races.filter(r => r.winner).length}
          </div>
          <div>
            <span className="text-gray-600">Server Status:</span> 
            <span className={`ml-1 ${serverConnected ? 'text-green-600' : 'text-red-600'}`}>
              {serverConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 p-4 rounded-lg">
        <h4 className="font-semibold text-blue-800 mb-2">Quick Start Guide:</h4>
        <ol className="text-sm text-blue-700 space-y-1">
          <li>1. Click "Scrape New Races" to load today's races</li>
          <li>2. Family members can then place bets in the "User Bets" tab</li>
          <li>3. Use "Scrape Results" or manually set winners when races finish</li>
          <li>4. Check the leaderboard to see scores</li>
          <li>5. Click "Reset for New Day" to start fresh (saves current scores)</li>
        </ol>
      </div>
    </div>
  );
};

// --- Main HorseBettingApp Component ---
const HorseBettingApp = () => {
  const [activeTab, setActiveTab] = useState('leaderboard');
  const [users, setUsers] = useState([]);
  const [races, setRaces] = useState([]);
  const [bets, setBets] = useState({});
  const [bankers, setBankers] = useState({});
  const [selectedUser, setSelectedUser] = useState('');
  const [newUserName, setNewUserName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [serverConnected, setServerConnected] = useState(true);
  
  // Race Day Management State
  const [raceDays, setRaceDays] = useState([]);
  const [currentRaceDay, setCurrentRaceDay] = useState('');
  const [loadingRaceDays, setLoadingRaceDays] = useState(false);

  // Individual loading states for better UX
  const [loadingStates, setLoadingStates] = useState({
    users: false,
    races: false,
    bets: false,
    bankers: false
  });

  // Cache for API responses to reduce unnecessary calls
  const [dataCache, setDataCache] = useState({
    users: { data: null, timestamp: 0 },
    races: { data: null, timestamp: 0 },
    bets: { data: null, timestamp: 0 },
    bankers: { data: null, timestamp: 0 }
  });

  // Cache duration in milliseconds (5 minutes)
  const CACHE_DURATION = 5 * 60 * 1000;

  // Check if cached data is still valid
  const isCacheValid = useCallback((cacheKey) => {
    const cache = dataCache[cacheKey];
    return cache && (Date.now() - cache.timestamp) < CACHE_DURATION;
  }, [dataCache]);

  // Get cached data if valid
  const getCachedData = useCallback((cacheKey) => {
    const cache = dataCache[cacheKey];
    return isCacheValid(cacheKey) ? cache.data : null;
  }, [dataCache, isCacheValid]);

  // Update cache with new data
  const updateCache = useCallback((cacheKey, data) => {
    setDataCache(prev => ({
      ...prev,
      [cacheKey]: { data, timestamp: Date.now() }
    }));
  }, []);

  // State for confirmation modal
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmModalContent, setConfirmModalContent] = useState('');
  const [onConfirmAction, setOnConfirmAction] = useState(null);

  // Show message to user
  const showMessage = useCallback((msg, type = 'info') => {
    setMessage(msg);
    setTimeout(() => setMessage(''), 3000);
  }, []);

  // Update individual loading state
  const setLoadingState = useCallback((key, value) => {
    setLoadingStates(prev => ({ ...prev, [key]: value }));
  }, []);

  // API calls with individual loading states, retry logic, and caching
  const fetchUsers = useCallback(async (retryCount = 0, forceRefresh = false) => {
    // Check cache first
    if (!forceRefresh) {
      const cachedData = getCachedData('users');
      if (cachedData) {
        setUsers(cachedData);
        setServerConnected(true);
        return;
      }
    }

    setLoadingState('users', true);
    try {
      const response = await fetch(`${API_BASE}/users`, {
        signal: AbortSignal.timeout(15000) // 15 second timeout
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const usersData = Array.isArray(data) ? data : [];
      setUsers(usersData);
      updateCache('users', usersData);
      setServerConnected(true);
    } catch (error) {
      console.error('Error fetching users:', error);
      if (retryCount < 2 && error.name !== 'AbortError') {
        // Retry after 2 seconds
        setTimeout(() => fetchUsers(retryCount + 1, forceRefresh), 2000);
        return;
      }
      showMessage('Error connecting to server', 'error');
      setUsers([]);
      setServerConnected(false);
    } finally {
      setLoadingState('users', false);
    }
  }, [showMessage, setLoadingState, getCachedData, updateCache]);

  const fetchRaces = useCallback(async (retryCount = 0, forceRefresh = false) => {
    // Check cache first
    if (!forceRefresh) {
      const cachedData = getCachedData('races');
      if (cachedData) {
        setRaces(cachedData);
        setServerConnected(true);
        return;
      }
    }

    setLoadingState('races', true);
    try {
      const response = await fetch(`${API_BASE}/races`, {
        signal: AbortSignal.timeout(15000) // 15 second timeout
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setRaces(data);
      updateCache('races', data);
      setServerConnected(true);
    } catch (error) {
      console.error('Error fetching races:', error);
      if (retryCount < 2 && error.name !== 'AbortError') {
        // Retry after 2 seconds
        setTimeout(() => fetchRaces(retryCount + 1, forceRefresh), 2000);
        return;
      }
      showMessage('Error fetching races', 'error');
      setRaces([]);
      setServerConnected(false);
    } finally {
      setLoadingState('races', false);
    }
  }, [showMessage, setLoadingState, getCachedData, updateCache]);

  const fetchBets = useCallback(async (retryCount = 0, forceRefresh = false) => {
    // Check cache first
    if (!forceRefresh) {
      const cachedData = getCachedData('bets');
      if (cachedData) {
        setBets(cachedData);
        setServerConnected(true);
        return;
      }
    }

    setLoadingState('bets', true);
    try {
      const response = await fetch(`${API_BASE}/bets`, {
        signal: AbortSignal.timeout(15000) // 15 second timeout
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setBets(data);
      updateCache('bets', data);
      setServerConnected(true);
    } catch (error) {
      console.error('Error fetching bets:', error);
      if (retryCount < 2 && error.name !== 'AbortError') {
        // Retry after 2 seconds
        setTimeout(() => fetchBets(retryCount + 1, forceRefresh), 2000);
        return;
      }
      showMessage('Error fetching bets', 'error');
      setBets({});
      setServerConnected(false);
    } finally {
      setLoadingState('bets', false);
    }
  }, [showMessage, setLoadingState, getCachedData, updateCache]);

  const fetchBankers = useCallback(async (retryCount = 0, forceRefresh = false) => {
    // Check cache first
    if (!forceRefresh) {
      const cachedData = getCachedData('bankers');
      if (cachedData) {
        setBankers(cachedData);
        setServerConnected(true);
        return;
      }
    }

    setLoadingState('bankers', true);
    try {
      const response = await fetch(`${API_BASE}/bankers`, {
        signal: AbortSignal.timeout(15000) // 15 second timeout
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setBankers(data);
      updateCache('bankers', data);
      setServerConnected(true);
    } catch (error) {
      console.error('Error fetching bankers:', error);
      if (retryCount < 2 && error.name !== 'AbortError') {
        // Retry after 2 seconds
        setTimeout(() => fetchBankers(retryCount + 1, forceRefresh), 2000);
        return;
      }
      showMessage('Error connecting to server', 'error');
      setBankers({});
      setServerConnected(false);
    } finally {
      setLoadingState('bankers', false);
    }
  }, [showMessage, setLoadingState, getCachedData, updateCache]);



  // Progressive loading - load data in sequence to avoid overwhelming the server
  const loadAllData = useCallback(async (forceRefresh = false) => {
    setLoading(true);
    try {
      // Load users first (most important for UI)
      await fetchUsers(0, forceRefresh);
      
      // Then load races
      await fetchRaces(0, forceRefresh);
      
      // Finally load bets and bankers
      await Promise.all([fetchBets(0, forceRefresh), fetchBankers(0, forceRefresh)]);
      
      setServerConnected(true);
      if (forceRefresh) {
        showMessage('Data refreshed successfully!', 'success');
      } else {
        showMessage('Data loaded successfully!', 'success');
      }
    } catch (error) {
      console.error('Error loading data:', error);
      setServerConnected(false);
      showMessage('Failed to load some data. Check connection and try again.', 'error');
    } finally {
      setLoading(false);
    }
  }, [fetchUsers, fetchRaces, fetchBets, fetchBankers, showMessage]);

  // Force refresh all data (bypass cache)
  const forceRefreshAllData = useCallback(() => {
    loadAllData(true);
  }, [loadAllData]);

  // Calculate overall loading progress
  const loadingProgress = useCallback(() => {
    const total = 4; // users, races, bets, bankers
    const loaded = Object.values(loadingStates).filter(state => !state).length;
    return Math.round((loaded / total) * 100);
  }, [loadingStates]);

  // Check if any data is still loading
  const isAnyDataLoading = useCallback(() => {
    return Object.values(loadingStates).some(state => state);
  }, [loadingStates]);

  // Race Day Management Functions
  const fetchRaceDays = useCallback(async () => {
    setLoadingRaceDays(true);
    try {
      const response = await fetch(`${API_BASE}/race-days`, {
        signal: AbortSignal.timeout(15000)
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setRaceDays(data.race_days);
      setCurrentRaceDay(data.current_race_day);
      setServerConnected(true);
    } catch (error) {
      console.error('Error fetching race days:', error);
      showMessage('Error loading race days', 'error');
      setServerConnected(false);
    } finally {
      setLoadingRaceDays(false);
    }
  }, [showMessage]);

  const switchRaceDay = useCallback(async (raceDay) => {
    setLoadingRaceDays(true);
    try {
      const response = await fetch(`${API_BASE}/race-days/current`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ race_day: raceDay }),
        signal: AbortSignal.timeout(15000)
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setCurrentRaceDay(raceDay);
      
      // Refresh all data after switching race day
      loadAllData(true);
      
      showMessage(`Switched to race day: ${raceDay}`, 'success');
    } catch (error) {
      console.error('Error switching race day:', error);
      showMessage('Error switching race day', 'error');
    } finally {
      setLoadingRaceDays(false);
    }
  }, [showMessage, loadAllData]);

  const createDummyRaceDays = useCallback(async () => {
    setLoadingRaceDays(true);
    try {
      const response = await fetch(`${API_BASE}/race-days/create-dummy`, {
        method: 'POST',
        signal: AbortSignal.timeout(15000)
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      showMessage(`Created ${data.created_days.length} dummy race days`, 'success');
      
      // Refresh race days list
      await fetchRaceDays();
    } catch (error) {
      console.error('Error creating dummy race days:', error);
      showMessage('Error creating dummy race days', 'error');
    } finally {
      setLoadingRaceDays(false);
    }
  }, [showMessage, fetchRaceDays]);

  // Load all data on component mount
  useEffect(() => {
    loadAllData();
    fetchRaceDays(); // Also load race days on mount
  }, [loadAllData, fetchRaceDays]);

  // Check if betting is still allowed for a race
  const isBettingAllowed = useCallback((raceTime) => {
    // For testing: always allow betting regardless of time
    return true;
  }, []);

  // Calculate points based on odds
  const calculatePoints = useCallback((odds) => {
    if (odds > 10) return 3;
    if (odds > 5) return 2;
    return 1;
  }, []);

  // Calculate user's daily score
  const calculateUserScore = useCallback((userId) => {
    let dailyScore = 0;
    if (Array.isArray(races)) {
      races.forEach(race => {
        if (race.winner && bets[userId] && bets[userId][race.id]) {
          const userBet = bets[userId][race.id];
          if (userBet === race.winner) {
            const horse = race.horses.find(h => h.number === race.winner);
            if (horse) {
              dailyScore += calculatePoints(horse.odds);
            }
          }
        }
      });

      // Apply banker bonus
      if (bankers[userId]) {
        const bankerRace = races.find(race => race.id === bankers[userId]);
        if (bankerRace && bets[userId]?.[bankerRace.id] === bankerRace.winner) {
          dailyScore *= 2;
        }
      }
    } else {
      console.warn("Races data is not an array in calculateUserScore:", races);
    }
    return dailyScore;
  }, [races, bets, bankers, calculatePoints]);

  // Place a bet
  const placeBet = useCallback(async (userId, raceId, horseNumber) => {
    if (!isBettingAllowed(races.find(r => r.id === raceId)?.time)) {
      showMessage('Betting is closed for this race!', 'error');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/bets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: String(userId),
          raceId: String(raceId),
          horseNumber: Number(horseNumber)
        }),
        signal: AbortSignal.timeout(15000) // 15 second timeout
      });

      if (response.ok) {
        // Optimistic update: update state and cache immediately
        setBets(prevBets => {
          const userKey = String(userId);
          const raceKey = String(raceId);
          const nextBets = {
            ...prevBets,
            [userKey]: { ...(prevBets[userKey] || {}), [raceKey]: Number(horseNumber) }
          };
          updateCache('bets', nextBets);
          return nextBets;
        });
        showMessage('Bet placed successfully!', 'success');
        // Optionally reconcile with server in background without harming perceived responsiveness
        // fetchBets(0, true);
      } else {
        const errorData = await response.json();
        showMessage(`Error placing bet: ${errorData.error || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Bet placement error:', error);
      if (error.name === 'AbortError') {
        showMessage('Request timed out. Please try again.', 'error');
      } else {
        showMessage('Error connecting to server', 'error');
      }
    }
  }, [isBettingAllowed, races, showMessage, updateCache]);

  // Set banker
  const setBanker = useCallback(async (userId, raceId) => {
    // Check if user has bet on this race
    const userBets = bets[userId] || {};
    const hasBetOnRace = userBets.hasOwnProperty(String(raceId));
    
    if (!hasBetOnRace) {
      showMessage('You can only select a banker from races you have bet on!', 'error');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/bankers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          raceId
        }),
        signal: AbortSignal.timeout(15000) // 15 second timeout
      });

      if (response.ok) {
        // Optimistic update: update state and cache immediately
        setBankers(prevBankers => {
          const nextBankers = { ...prevBankers, [String(userId)]: String(raceId) };
          updateCache('bankers', nextBankers);
          return nextBankers;
        });
        showMessage('Banker set successfully!', 'success');
        // Optionally reconcile with server in background
        // fetchBankers(0, true);
      } else {
        showMessage('Error setting banker', 'error');
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        showMessage('Request timed out. Please try again.', 'error');
      } else {
        showMessage('Error connecting to server', 'error');
      }
    }
  }, [bets, showMessage, updateCache]);

  // Add new user
  const addUser = useCallback(async () => {
    if (!newUserName.trim()) return;
    
    try {
      const response = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newUserName.trim()
        })
      });

      if (response.ok) {
        const createdUser = await response.json();
        setUsers(prevUsers => {
          const nextUsers = [...prevUsers, createdUser];
          updateCache('users', nextUsers);
          return nextUsers;
        });
        setNewUserName('');
        showMessage('User added successfully!', 'success');
        setServerConnected(true);
      } else {
        showMessage('Error adding user', 'error');
      }
    } catch (error) {
      showMessage('Error connecting to server', 'error');
      setServerConnected(false);
    }
  }, [newUserName, showMessage, updateCache]);

  // Set race result
  const setRaceResult = useCallback(async (raceId, winnerNumber) => {
    try {
      const response = await fetch(`${API_BASE}/races/${raceId}/result`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          winner: winnerNumber
        })
      });

      if (response.ok) {
        fetchRaces();
        showMessage('Race result updated!', 'success');
        setServerConnected(true);
      } else {
        showMessage('Error updating race result', 'error');
      }
    } catch (error) {
      showMessage('Error connecting to server', 'error');
      setServerConnected(false);
    }
  }, [fetchRaces, showMessage]);

  // Scrape new races
  const scrapeRaces = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/races/scrape`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        fetchRaces();
        showMessage(`Successfully scraped ${data.races.length} races!`, 'success');
        setServerConnected(true);
      } else {
        showMessage(`Scraping failed: ${data.error}`, 'error');
      }
    } catch (error) {
      showMessage('Error scraping races - check if server is running', 'error');
      setServerConnected(false);
    } finally {
      setLoading(false);
    }
  }, [fetchRaces, showMessage]);

  // Scrape results
  const scrapeResults = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/races/results`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        fetchRaces();
        const resultCount = Object.keys(data.results).length;
        showMessage(`Results scraped successfully! ${resultCount} races updated.`, 'success');
        setServerConnected(true);
      } else {
        showMessage(`Results scraping failed: ${data.error}`, 'error');
      }
    } catch (error) {
      showMessage('Error scraping results - check if server is running', 'error');
      setServerConnected(false);
    } finally {
      setLoading(false);
    }
  }, [fetchRaces, showMessage]);

  // Reset for new day
  const handleResetForNewDay = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/reset`, {
        method: 'POST'
      });

      if (response.ok) {
        fetchUsers();
        fetchRaces();
        fetchBets();
        fetchBankers();
        showMessage('Successfully reset for new day!', 'success');
        setServerConnected(true);
      } else {
        showMessage('Error resetting day', 'error');
      }
    } catch (error) {
      showMessage('Error connecting to server', 'error');
      setServerConnected(false);
    } finally {
      setLoading(false);
    }
  }, [fetchUsers, fetchRaces, fetchBets, fetchBankers, showMessage]);

  const resetForNewDay = useCallback(() => {
    setConfirmModalContent('Reset all bets and start a new racing day? This will save current scores to user totals.');
    setOnConfirmAction(() => handleResetForNewDay);
    setShowConfirmModal(true);
  }, [handleResetForNewDay]);

  return (
    <div className="min-h-screen bg-gray-100">
      <MessageDisplay message={message} />
      <ConfirmationModal
        show={showConfirmModal}
        message={confirmModalContent}
        onConfirm={() => {
          if (onConfirmAction) {
            onConfirmAction();
          }
          setShowConfirmModal(false);
          setOnConfirmAction(null);
        }}
        onCancel={() => {
          setShowConfirmModal(false);
          setOnConfirmAction(null);
        }}
      />
      <ConnectionStatus serverConnected={serverConnected} retryConnection={() => {
        setServerConnected(false);
        fetchUsers(); // Attempt to re-establish connection by fetching users
      }} />
      <div className="max-w-4xl mx-auto p-4">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6">
            <h1 className="text-3xl font-bold text-center">🐎 Family Horse Betting</h1>
            
            {/* Race Day Selector */}
            <div className="mt-4 text-center">
              <div className="inline-flex items-center gap-4 bg-white bg-opacity-10 px-4 py-2 rounded-lg">
                <span className="text-sm font-medium">Race Day:</span>
                <select
                  value={currentRaceDay}
                  onChange={(e) => switchRaceDay(e.target.value)}
                  disabled={loadingRaceDays}
                  className="bg-white bg-opacity-20 border border-white border-opacity-30 rounded px-3 py-1 text-white text-sm focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
                >
                  {raceDays.map(day => (
                    <option key={day.date} value={day.date} className="text-black">
                      {day.date} {day.completed ? '(Completed)' : ''} ({day.race_count} races)
                    </option>
                  ))}
                </select>
                {loadingRaceDays && <RefreshCw className="w-4 h-4 animate-spin" />}
                
                {/* Admin buttons for race day management */}
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={createDummyRaceDays}
                    disabled={loadingRaceDays}
                    className="px-3 py-1 bg-yellow-500 bg-opacity-80 hover:bg-opacity-100 rounded text-xs font-medium transition-colors disabled:opacity-50"
                    title="Create dummy race days for testing"
                  >
                    Create Test Days
                  </button>
                  <button
                    onClick={fetchRaceDays}
                    disabled={loadingRaceDays}
                    className="px-3 py-1 bg-white bg-opacity-20 hover:bg-opacity-30 rounded text-xs font-medium transition-colors disabled:opacity-50"
                    title="Refresh race days"
                  >
                    Refresh Days
                  </button>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-center gap-4 mt-4">
              {loading && (
                <div className="flex items-center gap-2 text-sm">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Loading data...</span>
                </div>
              )}
              {!loading && !serverConnected && (
                <div className="flex items-center gap-2 text-sm bg-red-500 bg-opacity-20 px-3 py-1 rounded-full">
                  <AlertCircle className="w-4 h-4" />
                  <span>Server disconnected</span>
                </div>
              )}
              {!loading && serverConnected && (
                <div className="flex items-center gap-2 text-sm bg-green-500 bg-opacity-20 px-3 py-1 rounded-full">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>Connected</span>
                </div>
              )}
              <button
                onClick={forceRefreshAllData}
                disabled={loading}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  loading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-white bg-opacity-20 hover:bg-opacity-30 text-white'
                }`}
              >
                <RefreshCw className={`w-4 h-4 inline mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
            
            {/* Loading Progress Bar */}
            {isAnyDataLoading() && (
              <div className="mt-4">
                <div className="flex justify-between text-xs mb-1">
                  <span>Loading progress</span>
                  <span>{loadingProgress()}%</span>
                </div>
                <div className="w-full bg-white bg-opacity-20 rounded-full h-2">
                  <div 
                    className="bg-white h-2 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${loadingProgress()}%` }}
                  ></div>
                </div>
                <div className="flex justify-center gap-4 mt-2 text-xs">
                  <span className={`${loadingStates.users ? 'text-yellow-200' : 'text-green-200'}`}>
                    {loadingStates.users ? '⏳' : '✅'} Users
                  </span>
                  <span className={`${loadingStates.races ? 'text-yellow-200' : 'text-green-200'}`}>
                    {loadingStates.races ? '⏳' : '✅'} Races
                  </span>
                  <span className={`${loadingStates.bets ? 'text-yellow-200' : 'text-green-200'}`}>
                    {loadingStates.bets ? '⏳' : '✅'} Bets
                  </span>
                  <span className={`${loadingStates.bankers ? 'text-yellow-200' : 'text-green-200'}`}>
                    {loadingStates.bankers ? '⏳' : '✅'} Bankers
                  </span>
                </div>
              </div>
            )}

            {/* Cache Status */}
            {!isAnyDataLoading() && serverConnected && (
              <div className="mt-4 text-center">
                <div className="inline-flex items-center gap-2 text-xs bg-white bg-opacity-10 px-3 py-1 rounded-full">
                  <span>💾</span>
                  <span>Cache: {Object.values(dataCache).filter(cache => isCacheValid(Object.keys(dataCache).find(key => dataCache[key] === cache))).length}/4 valid</span>
                  <button
                    onClick={forceRefreshAllData}
                    className="ml-2 px-2 py-1 bg-white bg-opacity-20 hover:bg-opacity-30 rounded text-xs transition-colors"
                    title="Force refresh all data"
                  >
                    🔄
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Tab Navigation */}
          <div className="border-b">
            <div className="flex">
              {[
                { id: 'leaderboard', label: 'Leaderboard', icon: Trophy },
                { id: 'races', label: 'Race Day', icon: Calendar },
                { id: 'bets', label: 'User Bets', icon: Users },
                { id: 'admin', label: 'Admin', icon: Settings }
              ].map(tab => {
                const Icon = tab.icon;
                // Show loading indicator for tabs that depend on specific data
                let loadingIndicator = null;
                if (tab.id === 'leaderboard' && loadingStates.users) {
                  loadingIndicator = <RefreshCw className="w-3 h-3 animate-spin ml-1" />;
                } else if (tab.id === 'races' && loadingStates.races) {
                  loadingIndicator = <RefreshCw className="w-3 h-3 animate-spin ml-1" />;
                } else if (tab.id === 'bets' && (loadingStates.users || loadingStates.races || loadingStates.bets)) {
                  loadingIndicator = <RefreshCw className="w-3 h-3 animate-spin ml-1" />;
                } else if (tab.id === 'admin' && (loadingStates.users || loadingStates.races || loadingStates.bets || loadingStates.bankers)) {
                  loadingIndicator = <RefreshCw className="w-3 h-3 animate-spin ml-1" />;
                }
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 px-4 py-3 text-center font-medium transition-colors flex items-center justify-center gap-2 ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{tab.label}</span>
                    {loadingIndicator}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {!serverConnected && !isAnyDataLoading() ? (
              // Show offline state when server is disconnected and no data is loading
              <div className="text-center py-12">
                <div className="text-gray-400 mb-6">
                  <AlertCircle className="w-24 h-24 mx-auto mb-4" />
                </div>
                <h2 className="text-2xl font-semibold text-gray-600 mb-4">Server Connection Lost</h2>
                <p className="text-gray-500 mb-6 max-w-md mx-auto">
                  Unable to connect to the server. This could be due to:
                </p>
                <ul className="text-gray-500 mb-8 text-left max-w-md mx-auto space-y-2">
                  <li>• Server is starting up (common with free hosting services)</li>
                  <li>• Network connectivity issues</li>
                  <li>• Server maintenance or downtime</li>
                </ul>
                <div className="space-x-4">
                  <button
                    onClick={forceRefreshAllData}
                    className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
                  >
                    <RefreshCw className="w-5 h-5 inline mr-2" />
                    Try Again
                  </button>
                  <button
                    onClick={() => window.location.reload()}
                    className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium"
                  >
                    Reload Page
                  </button>
                </div>
              </div>
            ) : (
              <>
                {activeTab === 'leaderboard' && (
                  loadingStates.users ? <SkeletonLeaderboard /> : <LeaderboardTab
                    users={users}
                    calculateUserScore={calculateUserScore}
                    bankers={bankers}
                    setActiveTab={setActiveTab}
                  />
                )}
                {activeTab === 'races' && (
                  loadingStates.races ? <SkeletonRaces /> : <RaceDayTab
                    races={races}
                    isBettingAllowed={isBettingAllowed}
                    setActiveTab={setActiveTab}
                  />
                )}
                {activeTab === 'bets' && (
                  (loadingStates.users || loadingStates.races || loadingStates.bets) ? (
                    <div className="space-y-4">
                      <div className="bg-gradient-to-r from-blue-400 to-blue-600 text-white p-6 rounded-lg">
                        <h2 className="text-2xl font-bold flex items-center gap-2">
                          <Users className="w-6 h-6" />
                          User Bets
                        </h2>
                      </div>
                      <div className="bg-white p-6 rounded-lg shadow text-center">
                        <div className="text-gray-400 mb-4">
                          <RefreshCw className="w-16 h-16 mx-auto mb-2 animate-spin" />
                        </div>
                        <h3 className="text-lg font-semibold text-gray-600 mb-2">Loading User Bets</h3>
                        <p className="text-gray-500">
                          {loadingStates.users ? 'Loading users...' : 
                           loadingStates.races ? 'Loading races...' : 
                           loadingStates.bets ? 'Loading bets...' : 'Loading...'}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <UserBetsTab
                      users={users}
                      selectedUser={selectedUser}
                      setSelectedUser={setSelectedUser}
                      races={races}
                      bets={bets}
                      bankers={bankers}
                      placeBet={placeBet}
                      setBanker={setBanker}
                      showMessage={showMessage}
                      isBettingAllowed={isBettingAllowed}
                      calculateUserScore={calculateUserScore}
                      setActiveTab={setActiveTab}
                    />
                  )
                )}
                {activeTab === 'admin' && (
                  (loadingStates.users || loadingStates.races || loadingStates.bets || loadingStates.bankers) ? (
                    <div className="space-y-4">
                      <div className="bg-gradient-to-r from-purple-400 to-purple-600 text-white p-6 rounded-lg">
                        <h2 className="text-2xl font-bold flex items-center gap-2">
                          <Settings className="w-6 h-6" />
                          Admin Panel
                        </h2>
                      </div>
                      <div className="bg-white p-6 rounded-lg shadow text-center">
                        <div className="text-gray-400 mb-4">
                          <RefreshCw className="w-16 h-16 mx-auto mb-2 animate-spin" />
                        </div>
                        <h3 className="text-lg font-semibold text-gray-600 mb-2">Loading Admin Panel</h3>
                        <p className="text-gray-500">
                          {loadingStates.users ? 'Loading users...' : 
                           loadingStates.races ? 'Loading races...' : 
                           loadingStates.bets ? 'Loading bets...' : 
                           loadingStates.bankers ? 'Loading bankers...' : 'Loading...'}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <AdminTab
                      newUserName={newUserName}
                      setNewUserName={setNewUserName}
                      addUser={addUser}
                      loading={loading}
                      scrapeRaces={scrapeRaces}
                      scrapeResults={scrapeResults}
                      resetForNewDay={resetForNewDay}
                      races={races}
                      setRaceResult={setRaceResult}
                      users={users}
                      bets={bets}
                      bankers={bankers}
                      serverConnected={serverConnected}
                    />
                  )
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HorseBettingApp;