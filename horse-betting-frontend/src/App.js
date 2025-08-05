// App.js (Revised script)

import React, { useState, useEffect, useCallback } from 'react';
import { Users, Trophy, Calendar, Settings, Plus, RefreshCw, Save, Clock, Star, Download } from 'lucide-react';

const API_BASE = "https://horse-betting-backend.onrender.com/api"
//const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Debug: Log the API URL being used
console.log('API_BASE URL:', API_BASE);
console.log('Environment variable:', process.env.REACT_APP_API_URL);

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

  // State for confirmation modal
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmModalContent, setConfirmModalContent] = useState('');
  const [onConfirmAction, setOnConfirmAction] = useState(null);

  // Show message to user
  const showMessage = useCallback((msg, type = 'info') => {
    setMessage(msg);
    setTimeout(() => setMessage(''), 3000);
  }, []);

  // API calls (wrapped in useCallback for memoization)
  const fetchUsers = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/users`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setUsers(Array.isArray(data) ? data : []);
      setServerConnected(true);
    } catch (error) {
      console.error('Error fetching users:', error);
      showMessage('Error connecting to server', 'error');
      setUsers([]);
      setServerConnected(false);
    }
  }, [showMessage]);

  const fetchRaces = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/races`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setRaces(data);
      setServerConnected(true);
    } catch (error) {
      console.error('Error fetching races:', error);
      showMessage('Error fetching races', 'error');
      setRaces([]);
      setServerConnected(false);
    }
  }, [showMessage]);

  const fetchBets = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/bets`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setBets(data);
      setServerConnected(true);
    } catch (error) {
      console.error('Error fetching bets:', error);
      showMessage('Error fetching bets', 'error');
      setBets({});
      setServerConnected(false);
    }
  }, [showMessage]);

  const fetchBankers = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/bankers`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setBankers(data);
      setServerConnected(true);
    } catch (error) {
      console.error('Error fetching bankers:', error);
      showMessage('Error connecting to server', 'error');
      setBankers({});
      setServerConnected(false);
    }
  }, [showMessage]);

  // Load all data on component mount
  useEffect(() => {
    fetchUsers();
    fetchRaces();
    fetchBets();
    fetchBankers();
  }, [fetchUsers, fetchRaces, fetchBets, fetchBankers]);

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
        })
      });

      if (response.ok) {
        fetchBets();
        showMessage('Bet placed successfully!', 'success');
      } else {
        const errorData = await response.json();
        showMessage(`Error placing bet: ${errorData.error || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Bet placement error:', error);
      showMessage('Error connecting to server', 'error');
    }
  }, [fetchBets, isBettingAllowed, races, showMessage]);

  // Set banker
  const setBanker = useCallback(async (userId, raceId) => {
    // Check if user has bet on this race
    const userBets = bets[userId] || {};
    const hasBetOnRace = userBets.hasOwnProperty(raceId);
    
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
        })
      });

      if (response.ok) {
        fetchBankers();
        showMessage('Banker set successfully!', 'success');
      } else {
        showMessage('Error setting banker', 'error');
      }
    } catch (error) {
      showMessage('Error connecting to server', 'error');
    }
  }, [bets, fetchBankers, showMessage]);

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
        fetchUsers();
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
  }, [newUserName, fetchUsers, showMessage]);

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
      <div className="max-w-4xl mx-auto p-4">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6">
            <h1 className="text-3xl font-bold text-center">🐎 Family Horse Betting</h1>
            {loading && (
              <div className="text-center mt-2">
                <div className="inline-flex items-center gap-2 text-sm">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Processing...
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
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'leaderboard' && (
              <LeaderboardTab
                users={users}
                calculateUserScore={calculateUserScore}
                bankers={bankers}
                setActiveTab={setActiveTab}
              />
            )}
            {activeTab === 'races' && (
              <RaceDayTab
                races={races}
                isBettingAllowed={isBettingAllowed}
                setActiveTab={setActiveTab}
              />
            )}
            {activeTab === 'bets' && (
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
            )}
            {activeTab === 'admin' && (
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
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HorseBettingApp;