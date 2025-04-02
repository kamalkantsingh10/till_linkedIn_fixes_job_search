// Create a namespace for API functions
window.LPFJS_API = (function() {
  // Send data to the Flask backend
  const sendToFlask = async function(endpoint, data) {
    try {
      // Get the base API URL from storage
      const { apiUrl } = await new Promise((resolve) => {
        chrome.storage.sync.get(['apiUrl'], resolve);
      });
      
      if (!apiUrl) {
        throw new Error('API URL not configured');
      }
      
      // Construct the full URL
      const url = apiUrl.endsWith('/') 
        ? apiUrl + endpoint.replace(/^\//, '')
        : apiUrl + endpoint;
      
      // Send the data to the backend
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });
      
      // Check if the request was successful
      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }
      
      // Parse and return the response
      return await response.json();
    } catch (error) {
      console.error('API error:', error);
      throw error;
    }
  };

  // Function to check if the API is reachable
  const checkApiConnection = async function() {
    try {
      // Get the base API URL from storage
      const { apiUrl } = await new Promise((resolve) => {
        chrome.storage.sync.get(['apiUrl'], resolve);
      });
      
      if (!apiUrl) {
        return { connected: false, message: 'API URL not configured' };
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
        return { connected: true };
      } else {
        return { 
          connected: false, 
          message: `Server responded with status: ${response.status}` 
        };
      }
    } catch (error) {
      return { 
        connected: false, 
        message: error.message || 'Failed to connect to API' 
      };
    }
  };
  
  // Return public functions
  return {
    sendToFlask: sendToFlask,
    checkApiConnection: checkApiConnection
  };
})();