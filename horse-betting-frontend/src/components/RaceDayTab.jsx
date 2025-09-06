import React from 'react';
import { Calendar, RefreshCw } from 'lucide-react';

const SkeletonCard = () => (
  <div className="bg-white p-4 rounded-lg shadow animate-pulse">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
  </div>
);

const RaceDayTab = ({ races, currentRaceDay, fetchAllData, loading }) => {
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-b-lg shadow-lg">
        <p className="text-center text-gray-500 py-10">Loading races...</p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-b-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-indigo-700">
        <Calendar className="w-6 h-6" />
        Race Day: {currentRaceDay?.date || 'N/A'}
        <button onClick={fetchAllData} className="ml-auto p-2 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors duration-200">
          <RefreshCw className="w-4 h-4 text-gray-600" />
        </button>
      </h2>
      {races.length > 0 ? (
        <ul className="space-y-4">
          {races.map(race => (
            <li key={race.id} className="bg-gray-50 p-4 rounded-lg shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-lg text-indigo-600">Race {race.id}</span>
                <span className={`text-sm font-semibold px-2 py-1 rounded-full ${race.status === 'completed' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'}`}>
                  {race.status}
                </span>
              </div>
              <div className="text-sm text-gray-600">Time: {race.time} | Track: {race.track}</div>
              <div className="mt-4">
                <h4 className="font-semibold text-gray-700 mb-2">Horses</h4>
                <ul className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {race.horses.map(horse => (
                    <li key={horse.number} className="p-2 rounded-md bg-gray-100 hover:bg-indigo-100 transition-colors cursor-pointer">
                      <div className="font-medium text-gray-800">Horse #{horse.number}</div>
                      <div className="text-sm text-gray-600">{horse.name}</div>
                    </li>
                  ))}
                </ul>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-center text-gray-500">No races available. Please go to the Admin tab to scrape new races.</p>
      )}
    </div>
  );
};

export default RaceDayTab;
