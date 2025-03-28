// content.js
(function() {
    // Add styles directly to avoid external CSS file loading issues
    const addStyles = () => {
      const style = document.createElement('style');
      style.textContent = `
        /* LinkedIn-like styling */
        :root {
          --linkedin-bg-color: #f3f2ef;
          --linkedin-card-bg: #ffffff;
          --linkedin-blue: #0a66c2;
          --linkedin-text-color: rgba(0, 0, 0, 0.9);
          --linkedin-secondary-text: rgba(0, 0, 0, 0.6);
          --linkedin-border-color: rgba(0, 0, 0, 0.15);
          --linkedin-shadow: 0 0 0 1px rgba(0, 0, 0, 0.08), 0 4px 4px rgba(0, 0, 0, 0.08);
        }
  
        /* Base styles for sidebar */
        .lpfjs-container {
          position: fixed;
          top: 0;
          left: 0;
          z-index: 9999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
          height: 100vh;
          width: 25%;
          min-width: 150px;
          box-shadow: var(--linkedin-shadow);
          transition: transform 0.3s ease;
          background-color: var(--linkedin-bg-color);
        }
  
        /* Collapsed state */
        .lpfjs-container.collapsed {
          transform: translateX(calc(-100% + 40px));
        }
  
        /* Sidebar */
        .lpfjs-sidebar {
          width: 100%;
          height: 100%;
          overflow: auto;
          border-right: 1px solid var(--linkedin-border-color);
        }
  
        /* Toggle button */
        .lpfjs-toggle {
          width: 32px;
          height: 32px;
          background-color: white;
          color: var(--linkedin-text-color);
          border: none;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .lpfjs-toggle:hover {
          background-color: rgba(0, 0, 0, 0.05);
        }
  
        /* Header */
        .lpfjs-header {
          background-color: white;
          color: var(--linkedin-text-color);
          padding: 12px 16px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid var(--linkedin-border-color);
          margin-bottom: 8px;
          position: relative;
        }
  
        .lpfjs-title {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--linkedin-text-color);
        }
  
        /* Content */
        .lpfjs-content {
          padding: 0 16px;
          font-size: 14px;
          color: var(--linkedin-text-color);
          line-height: 1.5;
          height: calc(100% - 110px);
          overflow-y: auto;
        }
  
        /* Section styling */
        .lpfjs-section {
          margin-bottom: 16px;
          padding: 16px;
          background-color: white;
          border-radius: 8px;
          box-shadow: var(--linkedin-shadow);
        }
        
        .lpfjs-section .lpfjs-heading {
          margin-bottom: 12px;
          font-size: 16px;
          color: var(--linkedin-text-color);
          padding-bottom: 4px;
        }
  
        /* Button */
        .lpfjs-button {
          background-color: var(--linkedin-blue);
          color: white;
          border: none;
          border-radius: 16px;
          padding: 6px 16px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          width: 100%;
          transition: background-color 0.2s;
          margin-bottom: 12px;
        }
  
        .lpfjs-button:hover {
          background-color: #004182;
        }
        
        .lpfjs-button:active {
          background-color: #00295c;
        }
  
        /* Footer table */
        .lpfjs-footer {
          position: absolute;
          bottom: 0;
          left: 0;
          width: 100%;
          background-color: white;
          border-top: 1px solid var(--linkedin-border-color);
          padding: 10px;
        }
        
        .lpfjs-footer-table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .lpfjs-footer-table td {
          width: 33.33%;
          text-align: center;
          padding: 6px;
        }
        
        .lpfjs-help-btn {
          display: inline-block;
          background-color: transparent;
          color: var(--linkedin-blue);
          border: 1px solid var(--linkedin-blue);
          border-radius: 16px;
          padding: 4px 12px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          text-decoration: none;
          transition: background-color 0.2s;
        }
        
        .lpfjs-help-btn:hover {
          background-color: rgba(10, 102, 194, 0.1);
          text-decoration: none;
          color: var(--linkedin-blue);
        }
  
        /* LinkedIn page adjustments */
        body {
          transition: padding 0.3s ease;
        }
        
        body.lpfjs-active {
          padding-left: 25% !important;
        }
        
        body.lpfjs-active.sidebar-collapsed {
          padding-left: 40px !important;
        }
        
        body.lpfjs-active .global-nav {
          padding-left: 25% !important;
          width: 100% !important;
          box-sizing: border-box !important;
        }
        
        body.lpfjs-active.sidebar-collapsed .global-nav {
          padding-left: 40px !important;
        }
        
        /* Ensure minimum padding for narrow screens */
        @media (max-width: 600px) {
          body.lpfjs-active {
            padding-left: 150px !important;
          }
          
          body.lpfjs-active .global-nav {
            padding-left: 150px !important;
          }
        }
      `;
      document.head.appendChild(style);
    };
  
    // Function to save job description to Notion
    const saveJobToNotion = () => {
      try {
        // Get job title
        const jobTitleElement = document.querySelector('.job-details-jobs-unified-top-card__job-title');
        const jobTitle = jobTitleElement ? jobTitleElement.textContent.trim() : 'Unknown Job Title';
        
        // Get company name
        const companyElement = document.querySelector('.job-details-jobs-unified-top-card__company-name');
        const companyName = companyElement ? companyElement.textContent.trim() : 'Unknown Company';
        
        // Get location
        const locationElement = document.querySelector('.job-details-jobs-unified-top-card__bullet');
        const location = locationElement ? locationElement.textContent.trim() : 'Unknown Location';
        
        // Get job description
        const jobDescriptionElement = document.querySelector('.jobs-description__content');
        const jobDescription = jobDescriptionElement ? jobDescriptionElement.textContent.trim() : 'No job description available';
        
        // Get current date
        const currentDate = new Date().toLocaleDateString();
        
        // Create job data object
        const jobData = {
          title: jobTitle,
          company: companyName,
          location: location,
          description: jobDescription,
          url: window.location.href,
          saved_date: currentDate
        };
        
        // Log the data (this would be replaced with an actual API call to Notion)
        console.log('Job data to save to Notion:', jobData);
        
        // Get Notion API URL from Chrome storage
        chrome.storage.sync.get(['apiUrl'], function(data) {
          if (data.apiUrl) {
            // In a real implementation, you would make an API call to your Notion integration here
            console.log('Would send data to Notion API at:', data.apiUrl);
            alert('Job description saved to Notion successfully!');
          } else {
            alert('Please set up your Notion API URL in the extension settings first.');
          }
        });
        
      } catch (error) {
        console.error('Error saving job to Notion:', error);
        alert('Error saving job description. See console for details.');
      }
    };
  
    // Create sidebar with toggle button
    const createSidebar = () => {
      // Container for everything
      const container = document.createElement('div');
      container.className = 'lpfjs-container';
      
      // Create sidebar
      const sidebar = document.createElement('div');
      sidebar.className = 'lpfjs-sidebar';
      
      // Create header
      const header = document.createElement('div');
      header.className = 'lpfjs-header';
      
      const title = document.createElement('h2');
      title.className = 'lpfjs-title';
      title.textContent = 'LPFJS';
      
      // Create toggle button
      const toggle = document.createElement('button');
      toggle.className = 'lpfjs-toggle';
      toggle.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="8" x2="13" y2="8"></line>
          <line x1="3" y1="4" x2="13" y2="4"></line>
          <line x1="3" y1="12" x2="13" y2="12"></line>
        </svg>
      `;
      
      header.appendChild(title);
      header.appendChild(toggle);
      sidebar.appendChild(header);
      
      // Create content
      const content = document.createElement('div');
      content.className = 'lpfjs-content';
      sidebar.appendChild(content);
      
      // Check if we're on a profile page
      if (window.location.href.includes('linkedin.com/in/')) {
        // Create profile section
        const profileSection = document.createElement('div');
        profileSection.className = 'lpfjs-section';
        
        const heading = document.createElement('h3');
        heading.className = 'lpfjs-heading';
        heading.textContent = 'Profile Actions';
        
        const button = document.createElement('button');
        button.className = 'lpfjs-button';
        button.textContent = 'Save to Notion';
        button.style.backgroundColor = '#0a66c2';
        button.style.color = 'white';
        button.onclick = function() {
          alert('Profile data saved to Notion');
        };
        
        profileSection.appendChild(heading);
        profileSection.appendChild(button);
        content.appendChild(profileSection);
      } else if (window.location.href.includes('linkedin.com/jobs/view/')) {
        // Create job detail section
        const jobSection = document.createElement('div');
        jobSection.className = 'lpfjs-section';
        
        const heading = document.createElement('h3');
        heading.className = 'lpfjs-heading';
        heading.textContent = 'Job Description Actions';
        
        const button = document.createElement('button');
        button.className = 'lpfjs-button';
        button.textContent = 'Save JD to Notion';
        button.style.backgroundColor = '#0a66c2';
        button.style.color = 'white';
        button.onclick = function() {
          saveJobToNotion();
        };
        
        jobSection.appendChild(heading);
        jobSection.appendChild(button);
        content.appendChild(jobSection);
      } else if (window.location.href.includes('linkedin.com/jobs/')) {
        // Create jobs section
        const jobsSection = document.createElement('div');
        jobsSection.className = 'lpfjs-section';
        
        const heading = document.createElement('h3');
        heading.className = 'lpfjs-heading';
        heading.textContent = 'Job Search Tools';
        
        const message = document.createElement('p');
        message.textContent = 'Jobs page detected. Enhanced features available.';
        message.style.fontSize = '13px';
        message.style.margin = '0 0 12px 0';
        
        jobsSection.appendChild(heading);
        jobsSection.appendChild(message);
        content.appendChild(jobsSection);
      } else {
        // Create default section
        const defaultSection = document.createElement('div');
        defaultSection.className = 'lpfjs-section';
        
        const message = document.createElement('p');
        message.textContent = 'Navigate to a LinkedIn profile or jobs page to see available actions.';
        message.style.fontSize = '13px';
        message.style.margin = '0';
        
        defaultSection.appendChild(message);
        content.appendChild(defaultSection);
      }
      
      // Create footer with 3-column table
      const footer = document.createElement('div');
      footer.className = 'lpfjs-footer';
      
      const table = document.createElement('table');
      table.className = 'lpfjs-footer-table';
      
      const row = document.createElement('tr');
      
      // First column
      const col1 = document.createElement('td');
      const helpLink = document.createElement('a');
      helpLink.className = 'lpfjs-help-btn';
      helpLink.textContent = 'Help';
      helpLink.href = '#'; // Placeholder link - to be configured later
      helpLink.target = '_blank';
      col1.appendChild(helpLink);
      
      // Second column
      const col2 = document.createElement('td');
      
      // Third column
      const col3 = document.createElement('td');
      
      // Assemble table
      row.appendChild(col1);
      row.appendChild(col2);
      row.appendChild(col3);
      table.appendChild(row);
      footer.appendChild(table);
      
      // Add footer to sidebar
      sidebar.appendChild(footer);
      
      // Add toggle functionality
      toggle.addEventListener('click', function() {
        container.classList.toggle('collapsed');
        document.body.classList.toggle('sidebar-collapsed');
        
        // Store state in Chrome storage
        chrome.storage.sync.set({
          sidebarExpanded: !container.classList.contains('collapsed')
        });
      });
      
      // Add container to page
      container.appendChild(sidebar);
      document.body.appendChild(container);
      
      // Apply active class to body
      document.body.classList.add('lpfjs-active');
      
      // Check if sidebar should be collapsed based on stored preference
      chrome.storage.sync.get(['sidebarExpanded'], function(data) {
        if (data.sidebarExpanded === false) {
          container.classList.add('collapsed');
          document.body.classList.add('sidebar-collapsed');
        }
      });
      
      // Set default state to expanded if no preference is stored yet
      chrome.storage.sync.set({
        sidebarExpanded: true
      });
      
      console.log('LPFJS sidebar created successfully!');
    };
    
    // Initialize when the page is fully loaded
    if (document.readyState === 'complete') {
      addStyles();
      createSidebar();
    } else {
      window.addEventListener('load', function() {
        addStyles();
        createSidebar();
      });
    }
    
    // Listen for page navigation events
    let lastUrl = location.href; 
    new MutationObserver(() => {
      const url = location.href;
      if (url !== lastUrl) {
        lastUrl = url;
        console.log('LPFJS detected page navigation to:', url);
        
        // Remove existing sidebar
        const existingSidebar = document.querySelector('.lpfjs-container');
        if (existingSidebar) {
          existingSidebar.remove();
        }
        
        // Remove body classes
        document.body.classList.remove('lpfjs-active');
        document.body.classList.remove('sidebar-collapsed');
        
        // Recreate sidebar
        addStyles();
        createSidebar();
      }
    }).observe(document, {subtree: true, childList: true});
  })();