import React, { useState, useEffect, useCallback } from 'react';
import { Trophy, Calendar, Settings, Star, Activity } from 'lucide-react';

import RaceDayTab from './components/RaceDayTab.jsx';
import UserBetsTab from './components/UserBetsTab.jsx';
import LeaderboardTab from './components/LeaderboardTab.jsx';
import AdminTab from './components/AdminTab.jsx';

const API_BASE = process.env.NODE_ENV === 'development'
  ? 'http://localhost:5000/api'
  : "https://horse-betting-backend.onrender.com/api";

const HorseBettingApp = () => {
  const [activeTab, setActiveTab] = useState('races');
  const [users, setUsers] = useState([]);
  const [bets, setBets] = useState([]);
  const [bankers, setBankers] = useState({});
  const [races, setRaces] = useState([]);
  const [newUserName, setNewUserName] = useState('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [showMessageBox, setShowMessageBox] = useState(false);
  const [currentRaceDay, setCurrentRaceDay] = useState(null);
  const [availableRaceDays, setAvailableRaceDays] = useState([]);
  const [selectedRaceDay, setSelectedRaceDay] = useState(null);
  const [selectedUserId, setSelectedUserId] = useState(null); // Start with no user selected

  // Admin tab state
  const [backendFiles, setBackendFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [editingContent, setEditingContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [loadingFile, setLoadingFile] = useState(false);
  const [savingFile, setSavingFile] = useState(false);

  const showMessage = useCallback((text, type = 'info') => {
    setMessage({ text, type });
    setShowMessageBox(true);
    setTimeout(() => {
      setShowMessageBox(false);
    }, 5000);
  }, []);

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      const usersRes = await fetch(`${API_BASE}/users`);
      const usersData = await usersRes.json();
      if (Array.isArray(usersData)) setUsers(usersData);

      const betsRes = await fetch(`${API_BASE}/bets`);
      const betsData = await betsRes.json();
      if (Array.isArray(betsData)) setBets(betsData);

      // Fetch bankers for current race day if available
      const bankersUrl = selectedRaceDay 
        ? `${API_BASE}/bankers?race_date=${selectedRaceDay}`
        : `${API_BASE}/bankers`;
      const bankersRes = await fetch(bankersUrl);
      const bankersData = await bankersRes.json();
      if (typeof bankersData === 'object' && bankersData !== null) setBankers(bankersData);

      // Fetch available race days
      const raceDaysRes = await fetch(`${API_BASE}/race-days/index`);
      const raceDaysData = await raceDaysRes.json();
      if (raceDaysData.raceDays && Array.isArray(raceDaysData.raceDays)) {
        setAvailableRaceDays(raceDaysData.raceDays.map(day => day.date));
      }

      const currentDayRes = await fetch(`${API_BASE}/race-days/current`);
      const currentDayData = await currentDayRes.json();
      setCurrentRaceDay(currentDayData.data);
      
      // Only set races and selected race day if no specific race day is already selected
      if (!selectedRaceDay) {
        if (currentDayData.data) {
          setSelectedRaceDay(currentDayData.data.date);
          if (Array.isArray(currentDayData.data.races)) {
            setRaces(currentDayData.data.races);
          }
        } else {
          setRaces([]);
        }
      }
    } catch (error) {
      showMessage(`Connection to server failed: ${error.message}`, 'error');
      console.error('Error in fetchAllData:', error);
    } finally {
      setLoading(false);
    }
  }, [showMessage, selectedRaceDay]);

  const fetchRaceDayData = useCallback(async (raceDate) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/race-days/${raceDate}`);
      const data = await response.json();
      
      if (data && data.races && Array.isArray(data.races)) {
        setRaces(data.races);
        setSelectedRaceDay(raceDate);
        
        // Fetch bankers for this specific race date
        const bankersRes = await fetch(`${API_BASE}/bankers?race_date=${raceDate}`);
        const bankersData = await bankersRes.json();
        if (typeof bankersData === 'object' && bankersData !== null) setBankers(bankersData);
      } else {
        setRaces([]);
        showMessage('No races found for this date', 'info');
      }
    } catch (error) {
      showMessage(`Error fetching race day: ${error.message}`, 'error');
      console.error('Error in fetchRaceDayData:', error);
    } finally {
      setLoading(false);
    }
  }, [showMessage]);

  const handleAddUser = useCallback(async () => {
    if (!newUserName.trim()) {
      showMessage('Please enter a user name.', 'info');
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newUserName })
      });
      const data = await response.json();
      if (data.success) {
        setUsers(prevUsers => [...prevUsers, data.user]);
        setNewUserName('');
        showMessage('User added successfully!', 'success');
      } else {
        showMessage(data.error, 'error');
      }
    } catch (error) {
      showMessage(`Error adding user: ${error.message}`, 'error');
    }
  }, [newUserName, setUsers, setNewUserName, showMessage]);

  const clearAllUserData = useCallback(async () => {
    if (window.confirm("Are you sure you want to delete ALL user data (bets, bankers, users)? This cannot be undone!")) {
      try {
        const res = await fetch(`${API_BASE}/admin/reset-data`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showMessage("All user data has been cleared.", "success");
          fetchAllData();
        } else {
          showMessage(data.error, "error");
        }
      } catch (error) {
        showMessage(`Failed to clear data: ${error.message}`, "error");
      }
    }
  }, [showMessage, fetchAllData]);

  const handleSetBet = useCallback(async (raceId, horseNumber) => {
    try {
      const response = await fetch(`${API_BASE}/bet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: String(selectedUserId), raceId, horseNumber })
      });
      const data = await response.json();
      if (data.success) {
        // Refresh bets data to get updated state
        const betsRes = await fetch(`${API_BASE}/bets`);
        const betsData = await betsRes.json();
        if (Array.isArray(betsData)) setBets(betsData);
        
        showMessage('Bet updated!', 'success');
      } else {
        showMessage(data.error, 'error');
      }
    } catch (error) {
      showMessage(`Error placing bet: ${error.message}`, 'error');
    }
  }, [selectedUserId, showMessage, setBets]);

  const handleSetBanker = useCallback(async (raceId) => {
    try {
      // Check if user already has a banker bet for this race
      const currentBet = bets.find(bet => String(bet.userId) === String(selectedUserId) && bet.raceId === raceId);
      
      if (currentBet) {
        // If there's already a bet, make it a banker bet
        const response = await fetch(`${API_BASE}/banker`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ userId: String(selectedUserId), raceId, horseNumber: currentBet.horse })
        });
        const data = await response.json();
        if (data.success) {
          // Refresh bets and bankers data
          const betsRes = await fetch(`${API_BASE}/bets`);
          const betsData = await betsRes.json();
          if (Array.isArray(betsData)) setBets(betsData);
          
          const bankersUrl = selectedRaceDay 
            ? `${API_BASE}/bankers?race_date=${selectedRaceDay}`
            : `${API_BASE}/bankers`;
          const bankersRes = await fetch(bankersUrl);
          const bankersData = await bankersRes.json();
          if (typeof bankersData === 'object' && bankersData !== null) setBankers(bankersData);
          
          showMessage('Banker updated!', 'success');
        } else {
          showMessage(data.error, 'error');
        }
      } else {
        showMessage('Please place a bet first before setting as banker', 'info');
      }
    } catch (error) {
      showMessage(`Error setting banker: ${error.message}`, 'error');
    }
  }, [selectedUserId, bets, setBets, setBankers, showMessage]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Auto-select first user when users are loaded
  useEffect(() => {
    if (users.length > 0 && !selectedUserId) {
      setSelectedUserId(users[0].id);
    }
  }, [users, selectedUserId]);

  const MessageBox = ({ text, type }) => {
    const bgColor = type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green-500' : 'bg-blue-500';
    return (
      <div className={`fixed bottom-4 left-1/2 -translate-x-1/2 ${bgColor} text-white p-4 rounded-lg shadow-xl transition-all duration-300 transform ${showMessageBox ? 'scale-100 opacity-100' : 'scale-90 opacity-0'}`}>
        {text}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100 font-sans antialiased text-gray-800">
      <div className="container mx-auto p-4 sm:p-8">
        <h1 className="text-4xl font-extrabold text-center text-indigo-800 mb-8 tracking-tight">Horse Betting</h1>
        <div className="flex flex-col lg:flex-row gap-8">
          <div className="flex-1">
            <div className="flex justify-center mb-6 overflow-x-auto whitespace-nowrap">
              <button onClick={() => setActiveTab('races')} className={`py-3 px-6 rounded-t-lg transition-colors duration-200 font-semibold ${activeTab === 'races' ? 'bg-white text-indigo-700 shadow-md' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'}`}>
                <Activity className="inline-block w-5 h-5 mr-2" />
                Races
              </button>
              <button onClick={() => setActiveTab('bets')} className={`py-3 px-6 rounded-t-lg transition-colors duration-200 font-semibold ${activeTab === 'bets' ? 'bg-white text-indigo-700 shadow-md' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'}`}>
                <Star className="inline-block w-5 h-5 mr-2" />
                Your Bets
              </button>
              <button onClick={() => setActiveTab('leaderboard')} className={`py-3 px-6 rounded-t-lg transition-colors duration-200 font-semibold ${activeTab === 'leaderboard' ? 'bg-white text-indigo-700 shadow-md' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'}`}>
                <Trophy className="inline-block w-5 h-5 mr-2" />
                Leaderboard
              </button>
              <button onClick={() => setActiveTab('admin')} className={`py-3 px-6 rounded-t-lg transition-colors duration-200 font-semibold ${activeTab === 'admin' ? 'bg-white text-indigo-700 shadow-md' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'}`}>
                <Settings className="inline-block w-5 h-5 mr-2" />
                Admin
              </button>
            </div>

            {activeTab === 'races' && (
              <RaceDayTab 
                races={races} 
                currentRaceDay={currentRaceDay} 
                availableRaceDays={availableRaceDays}
                selectedRaceDay={selectedRaceDay}
                fetchAllData={fetchAllData} 
                fetchRaceDayData={fetchRaceDayData}
                loading={loading} 
              />
            )}

            {activeTab === 'bets' && (
              <UserBetsTab 
                races={races} 
                bets={bets} 
                bankers={bankers} 
                users={users}
                selectedUserId={selectedUserId}
                setSelectedUserId={setSelectedUserId}
                availableRaceDays={availableRaceDays}
                selectedRaceDay={selectedRaceDay}
                fetchRaceDayData={fetchRaceDayData}
                handleSetBet={handleSetBet} 
                handleSetBanker={handleSetBanker} 
              />
            )}

            {activeTab === 'leaderboard' && (
              <LeaderboardTab users={users} showMessage={showMessage} />
            )}

            {activeTab === 'admin' && (
              <AdminTab
                newUserName={newUserName}
                setNewUserName={setNewUserName}
                handleAddUser={handleAddUser}
                clearAllUserData={clearAllUserData}
                backendFiles={backendFiles}
                setBackendFiles={setBackendFiles}
                selectedFile={selectedFile}
                setSelectedFile={setSelectedFile}
                fileContent={fileContent}
                setFileContent={setFileContent}
                editingContent={editingContent}
                setEditingContent={setEditingContent}
                isEditing={isEditing}
                setIsEditing={setIsEditing}
                loadingFiles={loadingFiles}
                setLoadingFiles={setLoadingFiles}
                loadingFile={loadingFile}
                setLoadingFile={setLoadingFile}
                savingFile={savingFile}
                setSavingFile={setSavingFile}
                showMessage={showMessage}
                fetchAllData={fetchAllData}
              />
            )}
          </div>
        </div>
      </div>
      <MessageBox text={message.text} type={message.type} />
    </div>
  );
};

export default HorseBettingApp;
