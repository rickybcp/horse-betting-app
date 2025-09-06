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

      const bankersRes = await fetch(`${API_BASE}/bankers`);
      const bankersData = await bankersRes.json();
      if (typeof bankersData === 'object' && bankersData !== null) setBankers(bankersData);

      const currentDayRes = await fetch(`${API_BASE}/race-days/current`);
      const currentDayData = await currentDayRes.json();
      setCurrentRaceDay(currentDayData.data);
      if (currentDayData.data && Array.isArray(currentDayData.data.races)) {
        setRaces(currentDayData.data.races);
      } else {
        setRaces([]);
      }
    } catch (error) {
      showMessage(`Connection to server failed: ${error.message}`, 'error');
      console.error('Error in fetchAllData:', error);
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
      const response = await fetch(`${API_BASE}/bets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: 1, raceId, horse: horseNumber })
      });
      const data = await response.json();
      if (data.success) {
        const updatedBets = bets.filter(bet => !(bet.userId === 1 && bet.raceId === raceId));
        setBets([...updatedBets, data.bet]);
        showMessage('Bet placed!', 'success');
      } else {
        showMessage(data.error, 'error');
      }
    } catch (error) {
      showMessage(`Error placing bet: ${error.message}`, 'error');
    }
  }, [bets, showMessage, setBets]);

  const handleSetBanker = useCallback(async (raceId) => {
    try {
      const response = await fetch(`${API_BASE}/bankers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: 1, raceId })
      });
      const data = await response.json();
      if (data.success) {
        setBankers(data.bankers);
        showMessage('Banker updated!', 'success');
      } else {
        showMessage(data.error, 'error');
      }
    } catch (error) {
      showMessage(`Error setting banker: ${error.message}`, 'error');
    }
  }, [setBankers, showMessage]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

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
              <RaceDayTab races={races} currentRaceDay={currentRaceDay} fetchAllData={fetchAllData} loading={loading} />
            )}

            {activeTab === 'bets' && (
              <UserBetsTab races={races} bets={bets} bankers={bankers} handleSetBet={handleSetBet} handleSetBanker={handleSetBanker} />
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
