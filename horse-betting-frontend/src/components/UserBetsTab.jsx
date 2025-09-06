import React from 'react';
import { Star, Calendar, ChevronDown, Trophy, User } from 'lucide-react';

const UserBetsTab = ({ races, bets, bankers, users, selectedUserId, setSelectedUserId, availableRaceDays, selectedRaceDay, fetchRaceDayData, handleSetBet, handleSetBanker }) => {
  return (
    <div className="bg-white p-6 rounded-b-lg shadow-lg">
      {/* Header with selectors */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2 text-indigo-700 mb-4">
          <Star className="w-6 h-6" />
          Betting
        </h2>
        
        {/* Mobile-friendly selectors */}
        <div className="space-y-4">
          {/* User Selector */}
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select User
            </label>
            <select 
              value={selectedUserId || ''} 
              onChange={(e) => {
                const newUserId = e.target.value;
                setSelectedUserId(newUserId);
              }}
              className="w-full appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 text-base focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 min-h-[48px]"
            >
              <option value="">Choose a user...</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>{user.name}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
          </div>
          
          {/* Race Day Selector */}
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Race Day
            </label>
            <select 
              value={selectedRaceDay || ''} 
              onChange={(e) => fetchRaceDayData(e.target.value)}
              className="w-full appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 text-base focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 min-h-[48px]"
            >
              <option value="">Choose a race day...</option>
              {availableRaceDays.map(day => (
                <option key={day} value={day}>{day}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="text-blue-800 text-sm">
          <p className="mb-2">
            <span className="font-semibold">How to manage bets:</span>
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li><strong>Place/Change Bet:</strong> Click on any horse to place or change the bet (disabled for completed races)</li>
            <li><strong>Set Banker:</strong> Click the <Star className="w-4 h-4 inline mx-1" /> to set/remove banker (2x multiplier for daily score)</li>
            <li><strong>Current Bets:</strong> Selected horses are highlighted in blue</li>
            <li><strong>Winners:</strong> Winning bets show in green with "WON!" text</li>
            <li><strong>Completed Races:</strong> Betting is disabled for completed races</li>
          </ul>
        </div>
      </div>

      {/* Current user and race day indicator */}
      {(selectedUserId || selectedRaceDay) && (
        <div className="mb-4 p-3 bg-indigo-50 rounded-lg border border-indigo-200">
          <div className="flex items-center gap-4 text-indigo-800 font-medium">
            {selectedUserId && (
              <div className="flex items-center gap-2">
                <User className="w-4 h-4" />
                <span>User: <span className="font-bold">{users.find(u => u.id === selectedUserId)?.name || 'Unknown'}</span></span>
              </div>
            )}
            {selectedRaceDay && (
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                <span>Race Day: <span className="font-bold">{selectedRaceDay}</span></span>
              </div>
            )}
          </div>
        </div>
      )}

      {!selectedUserId ? (
        <div className="text-center py-10">
          <User className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-2">Please select a user to view their bets</p>
          <p className="text-sm text-gray-400">Choose a user from the dropdown above</p>
        </div>
      ) : races.length > 0 ? (
        <div className="space-y-6">
          {races.map(race => {
            const userBet = bets.find(bet => 
              String(bet.userId) === String(selectedUserId) && bet.raceId === race.id
            );
            const isBanker = bankers && selectedUserId && bankers[String(selectedUserId)] === race.id;
            
            return (
              <div key={race.id} className="bg-gray-50 p-4 rounded-lg shadow-sm">
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-bold text-lg text-indigo-600">Race {race.raceNumber || race.id}</h3>
                      {race.winner && (
                        <div className="flex items-center gap-1 text-yellow-600">
                          <Trophy className="w-4 h-4" />
                          <span className="text-xs font-medium">Winner: #{race.winner}</span>
                        </div>
                      )}
                    </div>
                    {race.name && (
                      <p className="text-sm text-gray-600 mt-1">{race.name}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {race.time && (
                      <span className="text-sm text-gray-600 bg-white px-2 py-1 rounded">{race.time}</span>
                    )}
                    <button
                      onClick={() => handleSetBanker(race.id)}
                      disabled={!selectedUserId || race.status === 'completed'}
                      className={`p-3 rounded-full transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-[48px] min-w-[48px] ${
                        isBanker ? 'text-yellow-500 bg-yellow-100' : 'text-gray-400 hover:text-yellow-500'
                      }`}
                      title={race.status === 'completed' ? 'Cannot set banker on completed race' : (isBanker ? 'Remove banker' : 'Set as banker (2x multiplier for daily score)')}
                    >
                      <Star className={`w-6 h-6 ${isBanker ? 'fill-yellow-500' : ''} transition-colors duration-200`} />
                    </button>
                    <span className={`text-sm font-semibold px-2 py-1 rounded-full ${
                      race.status === 'completed' ? 'bg-green-200 text-green-800' : 
                      race.status === 'in_progress' ? 'bg-blue-200 text-blue-800' :
                      'bg-yellow-200 text-yellow-800'
                    }`}>
                      {race.status}
                    </span>
                  </div>
                </div>

                {/* Horses displayed vertically */}
                <div className="space-y-2">
                  {race.horses.map(horse => {
                    const isSelected = userBet && userBet.horse === horse.number;
                    const isWinner = race.winner === horse.number;
                    const wonBet = isSelected && isWinner;
                    
                    return (
                      <button
                        key={horse.number}
                        onClick={() => handleSetBet(race.id, horse.number)}
                        disabled={!selectedUserId || race.status === 'completed'}
                        className={`w-full p-4 rounded-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transform hover:scale-[1.02] min-h-[60px] ${
                          wonBet
                            ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg border-2 border-green-400 hover:from-green-600 hover:to-green-700'
                            : isWinner
                            ? 'bg-gradient-to-r from-yellow-100 to-yellow-50 border-2 border-yellow-300 text-yellow-900 hover:from-yellow-200 hover:to-yellow-100'
                            : isSelected 
                            ? 'bg-indigo-600 text-white shadow-md hover:bg-indigo-700' 
                            : 'bg-white hover:bg-indigo-100 border border-gray-200 hover:border-indigo-300 hover:shadow-md'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <span className={`font-bold w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                              wonBet
                                ? 'bg-white text-green-600'
                                : isWinner
                                ? 'bg-yellow-400 text-yellow-900'
                                : isSelected 
                                ? 'bg-white text-indigo-600' 
                                : 'bg-indigo-100 text-indigo-600'
                            }`}>
                              {horse.number}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-left">{horse.name}</span>
                              {isSelected && race.status !== 'completed' && (
                                <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded">
                                  Current Bet
                                </span>
                              )}
                              {wonBet && (
                                <div className="flex items-center gap-1">
                                  <Trophy className="w-4 h-4" />
                                  <span className="text-xs font-bold">WON!</span>
                                </div>
                              )}
                              {isWinner && !isSelected && (
                                <div className="flex items-center gap-1">
                                  <Trophy className="w-4 h-4 text-yellow-600" />
                                  <span className="text-xs font-bold">WINNER</span>
                                </div>
                              )}
                              {!isSelected && selectedUserId && (
                                <span className={`text-xs ${race.status === 'completed' ? 'text-red-500' : 'text-gray-500'}`}>
                                  {race.status === 'completed' ? 'Betting disabled' : 'Click to bet'}
                                </span>
                              )}
                            </div>
                          </div>
                          {horse.odds && (
                            <span className={`text-sm px-2 py-1 rounded ${
                              wonBet
                                ? 'bg-white text-green-600'
                                : isWinner
                                ? 'bg-yellow-200 text-yellow-800'
                                : isSelected 
                                ? 'bg-white text-indigo-600' 
                                : 'bg-gray-100 text-gray-600'
                            }`}>
                              {horse.odds}
                            </span>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-10">
          <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-2">No races available for betting</p>
          <p className="text-sm text-gray-400">Select a race day to start betting</p>
        </div>
      )}
    </div>
  );
};

export default UserBetsTab;
