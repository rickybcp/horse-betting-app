import React from 'react';
import { Star } from 'lucide-react';

const UserBetsTab = ({ races, bets, bankers, handleSetBet, handleSetBanker }) => {
  return (
    <div className="bg-white p-6 rounded-b-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-indigo-700">
        <Star className="w-6 h-6" />
        Your Bets
      </h2>
      <p className="text-gray-600 mb-4">Select your winning horse for each race. Select a star to make a horse your banker for that race. <span className="font-semibold">Bankers get a 1.5x score multiplier if they win!</span></p>
      <div className="space-y-6">
        {races.map(race => {
          const userBet = bets.find(bet => bet.userId === 1 && bet.raceId === race.id);
          const isBanker = bankers[1] === race.id;
          return (
            <div key={race.id} className="bg-gray-50 p-4 rounded-lg shadow-sm">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-bold text-lg text-indigo-600">Race {race.id}</h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleSetBanker(race.id)}
                    className={`p-1 rounded-full ${isBanker ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'} transition-colors duration-200`}
                  >
                    <Star className={`w-6 h-6 fill-current ${isBanker ? 'animate-bounce' : ''}`} />
                  </button>
                  <span className={`text-sm font-semibold px-2 py-1 rounded-full ${race.status === 'completed' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'}`}>
                    {race.status}
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-4">
                {race.horses.map(horse => (
                  <button
                    key={horse.number}
                    onClick={() => handleSetBet(race.id, horse.number)}
                    disabled={race.status === 'completed'}
                    className={`p-2 rounded-md transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
                      userBet && userBet.horse === horse.number ? 'bg-indigo-600 text-white shadow-md' : 'bg-gray-200 hover:bg-indigo-500 hover:text-white'
                    }`}
                  >
                    <div className="font-medium">Horse #{horse.number}</div>
                    <div className="text-sm">{horse.name}</div>
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default UserBetsTab;
