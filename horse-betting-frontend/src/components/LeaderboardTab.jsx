import React, { useState, useEffect } from 'react';
import { Trophy, Clock, Star, Users } from 'lucide-react';

const API_BASE = process.env.NODE_ENV === 'development'
  ? 'http://localhost:5000/api'
  : "https://horse-betting-backend.onrender.com/api";

const LeaderboardTab = ({ users, showMessage }) => {
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [activeLeaderboardTab, setActiveLeaderboardTab] = useState('overall');
  const [historicalDays, setHistoricalDays] = useState([]);
  const [loading, setLoading] = useState(true);

  // Helper to get user name from user ID
  const getUserName = (userId) => {
    const user = users.find(u => u.id === userId);
    return user ? user.name : `User ${userId}`;
  };

  // Fetch leaderboard data
  const fetchLeaderboardData = async () => {
    setLoading(true);
    try {
      if (activeLeaderboardTab === 'overall') {
        const response = await fetch(`${API_BASE}/race-days/leaderboard`);
        const data = await response.json();
        if (data && data.success) {
          const list = Array.isArray(data.leaderboard) ? data.leaderboard : [];
          setLeaderboardData(list);
        } else {
          setLeaderboardData([]);
          if (data && data.error) showMessage(data.error, 'error');
        }
      } else if (activeLeaderboardTab === 'current') {
        const response = await fetch(`${API_BASE}/race-days/leaderboard/current`);
        const data = await response.json();
        if (data && data.success) {
          const scores = Array.isArray(data.scores) ? data.scores : [];
          // Join with user names
          const scoresWithNames = scores.map(score => ({
            ...score,
            userName: getUserName(score.userId),
            totalScore: score.dailyScore // Rename for consistent display
          }));
          // Sort by score
          scoresWithNames.sort((a, b) => b.dailyScore - a.dailyScore);
          setLeaderboardData(scoresWithNames);
        } else {
          setLeaderboardData([]);
          if (data && data.error) showMessage(data.error, 'error');
        }
      }
    } catch (error) {
      showMessage(`Error fetching leaderboard data: ${error.message}`, 'error');
      console.error('Error fetching leaderboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalDays = async () => {
    try {
      const response = await fetch(`${API_BASE}/race-days/historical`);
      const data = await response.json();
      if (data.success) {
        setHistoricalDays(data.historical_race_days);
      }
    } catch (error) {
      console.error('Error fetching historical days:', error);
    }
  };

  useEffect(() => {
    fetchLeaderboardData();
  }, [activeLeaderboardTab, users]);

  useEffect(() => {
    fetchHistoricalDays();
  }, []);

  // Skeleton component for loading state
  const SkeletonLeaderboard = () => (
    <div className="space-y-4">
      <div className="bg-white p-6 rounded-lg shadow-md animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="flex items-center space-x-4">
          <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="flex items-center space-x-4">
          <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-center space-x-4 text-sm font-semibold text-gray-600">
        <button
          onClick={() => setActiveLeaderboardTab('overall')}
          className={`py-2 px-4 rounded-full transition-colors duration-200 ${
            activeLeaderboardTab === 'overall' ? 'bg-indigo-500 text-white shadow-lg' : 'bg-gray-200 hover:bg-gray-300'
          }`}
        >
          Overall
        </button>
        <button
          onClick={() => setActiveLeaderboardTab('current')}
          className={`py-2 px-4 rounded-full transition-colors duration-200 ${
            activeLeaderboardTab === 'current' ? 'bg-indigo-500 text-white shadow-lg' : 'bg-gray-200 hover:bg-gray-300'
          }`}
        >
          Today's Scores
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-indigo-700">
          <Trophy className="w-6 h-6" />
          {activeLeaderboardTab === 'overall' ? 'Overall Leaderboard' : "Today's Scores"}
        </h2>
        {loading ? (
          <SkeletonLeaderboard />
        ) : (
          <ul className="space-y-4">
            {Array.isArray(leaderboardData) && leaderboardData.length > 0 ? (
              leaderboardData.map((entry, index) => (
                <li key={index} className={`flex items-center p-4 rounded-xl shadow transition-all duration-300 transform hover:scale-105 ${
                  index === 0 ? 'bg-yellow-100' : index === 1 ? 'bg-gray-100' : index === 2 ? 'bg-amber-100' : 'bg-white'
                }`}>
                  <span className={`font-bold text-xl mr-4 ${
                    index === 0 ? 'text-yellow-500' : index === 1 ? 'text-gray-500' : index === 2 ? 'text-amber-500' : 'text-gray-400'
                  }`}>
                    {index + 1}.
                  </span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Users className="w-5 h-5 text-gray-500" />
                      <span className="font-semibold text-gray-800">{entry.userName || getUserName(entry.userId)}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-xl text-indigo-600">{Math.round(entry.totalScore)}</span>
                    <span className="text-sm text-gray-500 ml-1">pts</span>
                  </div>
                </li>
              ))
            ) : (
              <p className="text-center text-gray-500 italic">No scores available yet.</p>
            )}
          </ul>
        )}
      </div>

      {activeLeaderboardTab === 'overall' && Array.isArray(historicalDays) && historicalDays.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-indigo-700">
            <Clock className="w-6 h-6" />
            Historical Race Days
          </h2>
          <ul className="space-y-2">
            {historicalDays.map((day, index) => (
              <li key={index} className="p-3 bg-gray-50 rounded-lg flex justify-between items-center text-gray-700">
                <span>{day.date}</span>
                <span className="text-sm text-gray-500">{day.status}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default LeaderboardTab;
