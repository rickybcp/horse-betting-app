import React from 'react';
import { Settings, Users, Plus, Calendar, Database, FileText, Folder } from 'lucide-react';

const API_BASE = process.env.NODE_ENV === 'development'
  ? 'http://localhost:5000/api'
  : "https://horse-betting-backend.onrender.com/api";

const AdminTab = ({ newUserName, setNewUserName, handleAddUser, clearAllUserData,
  backendFiles, setBackendFiles, selectedFile, setSelectedFile,
  editingContent, setEditingContent, isEditing, setIsEditing, loadingFiles, setLoadingFiles,
  loadingFile, setLoadingFile, savingFile, setSavingFile, showMessage, fetchAllData }) => {

  const handleLoadFiles = async () => {
    setLoadingFiles(true);
    try {
      const res = await fetch(`${API_BASE}/admin/files`);
      const data = await res.json();
      if (data.success) {
        setBackendFiles(data.files);
        showMessage("File list loaded.", "success");
      } else {
        showMessage(data.error, "error");
      }
    } catch (error) {
      showMessage(`Failed to load file list: ${error.message}`, "error");
    } finally {
      setLoadingFiles(false);
    }
  };

  const handleLoadFileContent = async () => {
    if (!selectedFile) return;
    setLoadingFile(true);
    try {
      const res = await fetch(`${API_BASE}/admin/files/${selectedFile}`);
      const data = await res.json();
      if (data.success) {
        setEditingContent(JSON.stringify(data.content, null, 2));
        setIsEditing(true);
        showMessage("File loaded for editing.", "success");
      } else {
        showMessage(data.error, "error");
      }
    } catch (error) {
      showMessage(`Failed to load file content: ${error.message}`, "error");
    } finally {
      setLoadingFile(false);
    }
  };

  const handleSaveFileContent = async () => {
    if (!selectedFile || !isEditing) return;
    setSavingFile(true);
    try {
      const res = await fetch(`${API_BASE}/admin/files/${selectedFile}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: editingContent
      });
      const data = await res.json();
      if (data.success) {
        showMessage("File saved successfully!", "success");
        setIsEditing(false); // Exit edit mode
      } else {
        showMessage(data.error, "error");
      }
    } catch (error) {
      showMessage(`Failed to save file: ${error.message}`, "error");
    } finally {
      setSavingFile(false);
    }
  };

  const handleScrapeRaces = async () => {
    try {
      const res = await fetch(`${API_BASE}/races/scrape`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showMessage("Scraped new race day!", "success");
        fetchAllData();
      } else {
        showMessage(data.error, "error");
      }
    } catch (error) {
      showMessage(`Failed to scrape races: ${error.message}`, "error");
    }
  };

  const handleScrapeResults = async () => {
    try {
      const res = await fetch(`${API_BASE}/races/results`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showMessage("Scraped race results!", "success");
        fetchAllData();
      } else {
        showMessage(data.error, "error");
      }
    } catch (error) {
      showMessage(`Failed to scrape results: ${error.message}`, "error");
    }
  };

  return (
    <div className="bg-white p-6 rounded-b-lg shadow-lg space-y-6">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-indigo-700">
        <Settings className="w-6 h-6" />
        Admin Panel
      </h2>
      <div className="bg-gray-100 p-4 rounded-lg space-y-4">
        <h3 className="font-bold text-lg flex items-center gap-2 text-indigo-600">
          <Users className="w-5 h-5" />
          User Management
        </h3>
        <div className="flex items-center gap-4">
          <input
            type="text"
            className="flex-1 p-2 border rounded-md"
            placeholder="New User Name"
            value={newUserName}
            onChange={(e) => setNewUserName(e.target.value)}
          />
          <button onClick={handleAddUser} className="bg-green-500 text-white p-2 rounded-md hover:bg-green-600 transition-colors">
            <Plus className="w-5 h-5" />
          </button>
        </div>
        <button onClick={clearAllUserData} className="w-full bg-red-500 text-white p-2 rounded-md hover:bg-red-600 transition-colors">
          Clear ALL User Data
        </button>
      </div>

      <div className="bg-gray-100 p-4 rounded-lg space-y-4">
        <h3 className="font-bold text-lg flex items-center gap-2 text-indigo-600">
          <Calendar className="w-5 h-5" />
          Race Day Management
        </h3>
        <button onClick={handleScrapeRaces} className="w-full bg-indigo-500 text-white p-2 rounded-md hover:bg-indigo-600 transition-colors">
          Scrape New Races
        </button>
        <button onClick={handleScrapeResults} className="w-full bg-indigo-500 text-white p-2 rounded-md hover:bg-indigo-600 transition-colors">
          Scrape Results
        </button>
      </div>

      <div className="bg-gray-100 p-4 rounded-lg space-y-4">
        <h3 className="font-bold text-lg flex items-center gap-2 text-indigo-600">
          <Database className="w-5 h-5" />
          File Management
        </h3>
        <button onClick={handleLoadFiles} className="w-full bg-gray-500 text-white p-2 rounded-md hover:bg-gray-600 transition-colors">
          {loadingFiles ? "Loading..." : "Load Files"}
        </button>
        {backendFiles.length > 0 && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Select a file to view:</label>
            <select
              className="w-full p-2 border rounded-md"
              value={selectedFile || ''}
              onChange={(e) => {
                setSelectedFile(e.target.value);
                setIsEditing(false); // Reset edit mode on file change
              }}
            >
              <option value="">-- Select a file --</option>
              {backendFiles.map(file => (
                <option key={file.path} value={file.path}>{file.path}</option>
              ))}
            </select>
            <div className="flex gap-2 mt-2">
              <button onClick={handleLoadFileContent} className="flex-1 bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 transition-colors" disabled={loadingFile || !selectedFile}>
                {loadingFile ? "Loading..." : "Load File"}
              </button>
              <button onClick={handleSaveFileContent} className="flex-1 bg-green-500 text-white p-2 rounded-md hover:bg-green-600 transition-colors" disabled={savingFile || !isEditing}>
                {savingFile ? "Saving..." : "Save File"}
              </button>
            </div>
            {isEditing && (
              <textarea
                className="w-full h-64 p-2 border rounded-md font-mono text-sm mt-4"
                value={editingContent}
                onChange={(e) => setEditingContent(e.target.value)}
              ></textarea>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminTab;
