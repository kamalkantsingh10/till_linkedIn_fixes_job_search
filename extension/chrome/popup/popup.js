// popup.js - Logic for extension popup

// Function to check API connection
const checkApiConnection = async () => {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    try {
      // Get the API URL from storage
      const { apiUrl } = await new Promise(resolve => {
        chrome.storage.sync.get(['apiUrl'], resolve);
      });
      
      if (!apiUrl) {
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'API not configured';
        return;
      }
      
      // Construct the ping URL
      const url = apiUrl.endsWith('/') 
        ? apiUrl + 'ping'
        : apiUrl + '/ping';
      
      // Try to connect to the API
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      // Check if the request was successful
      if (response.ok) {
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Connected to API';
      } else {
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'API error: ' + response.status;
      }
    } catch (error) {
      statusIndicator.classList.remove('connected');
      statusText.textContent = 'Cannot connect to API';
      console.error('API connection error:', error);
    }
  };
  
  // Function to toggle sidebar on the active tab
  const toggleSidebar = async () => {
    try {
      // Query for the active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Check if we're on a LinkedIn page
      if (!tab.url.includes('linkedin.com')) {
        alert('This extension only works on LinkedIn pages');
        return;
      }
      
      // Send message to the content script to toggle sidebar
      chrome.tabs.sendMessage(tab.id, { action: 'toggle_sidebar' });
    } catch (error) {
      console.error('Error toggling sidebar:', error);
    }
  };
  
  // Function to check the current page type
  const checkCurrentPage = async () => {
    try {
      // Query for the active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Check if we're on a LinkedIn page
      if (!tab.url.includes('linkedin.com')) {
        alert('This extension only works on LinkedIn pages');
        return;
      }
      
      // Send message to the content script to get the page type
      chrome.tabs.sendMessage(tab.id, { action: 'get_page_type' }, response => {
        if (response && response.pageType) {
          alert(`Current page type: ${response.pageType}`);
        } else {
          alert('Could not determine page type');
        }
      });
    } catch (error) {
      console.error('Error checking page type:', error);
      alert('Error checking page type');
    }
  };
  
  // Function to navigate to a specific LinkedIn section
  const navigateTo = (section) => {
    let url = '';
    
    switch (section) {
      case 'jobs':
        url = 'https://www.linkedin.com/jobs/';
        break;
      case 'connections':
        url = 'https://www.linkedin.com/mynetwork/invite-connect/connections/';
        break;
      default:
        return;
    }
    
    // Open the URL in the current tab
    chrome.tabs.update({ url });
    
    // Close the popup
    window.close();
  };
  
  // Function to open a new tab with a specific backend route
  const openBackendRoute = async (route) => {
    try {
      // Get the API URL from storage
      const { apiUrl } = await new Promise(resolve => {
        chrome.storage.sync.get(['apiUrl'], resolve);
      });
      
      if (!apiUrl) {
        alert('API URL not configured. Please check settings.');
        return;
      }
      
      // Construct the full URL
      const url = apiUrl.endsWith('/') 
        ? apiUrl + route.replace(/^\//, '')
        : apiUrl + route;
      
      // Open in a new tab
      chrome.tabs.create({ url });
    } catch (error) {
      console.error('Error opening backend route:', error);
      alert('Error opening backend route');
    }
  };
  
  // Function to open extension settings
  const openSettings = () => {
    chrome.runtime.openOptionsPage();
  };
  
  // Add event listeners when the popup loads
  document.addEventListener('DOMContentLoaded', () => {
    // Check API connection
    checkApiConnection();
    
    // Add listeners to buttons
    document.getElementById('toggle-sidebar').addEventListener('click', toggleSidebar);
    document.getElementById('check-page').addEventListener('click', checkCurrentPage);
    document.getElementById('go-to-jobs').addEventListener('click', () => navigateTo('jobs'));
    document.getElementById('go-to-connections').addEventListener('click', () => navigateTo('connections'));
    document.getElementById('view-saved-jobs').addEventListener('click', () => openBackendRoute('/dashboard/jobs'));
    document.getElementById('view-analytics').addEventListener('click', () => openBackendRoute('/dashboard/analytics'));
    document.getElementById('open-settings').addEventListener('click', openSettings);
    
    // Get and display version number
    const version = chrome.runtime.getManifest().version;
    document.getElementById('version').textContent = `v${version}`;
  });