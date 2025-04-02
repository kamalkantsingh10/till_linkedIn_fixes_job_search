// Create a namespace for UI functions
window.LPFJS_UI = (function() {
  // Add styles to the page
  const addStyles = function() {
    // Check if styles are already added
    if (document.getElementById('lpfjs-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'lpfjs-styles';
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

  // Create the sidebar base structure
  const createSidebar = function(pageType) {
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
    
    // Create content container (will be filled by specific modules)
    const content = document.createElement('div');
    content.className = 'lpfjs-content';
    sidebar.appendChild(content);
    
    // Create footer with help button
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
    helpLink.href = '#'; // Placeholder link
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
    
    // Check if sidebar should be collapsed based on stored preference
    chrome.storage.sync.get(['sidebarExpanded'], function(data) {
      if (data.sidebarExpanded === false) {
        container.classList.add('collapsed');
        document.body.classList.add('sidebar-collapsed');
      }
    });
    
    return sidebar; // Return sidebar element for modules to use
  };

  // Create a section for content
  const createSection = function(title) {
    const section = document.createElement('div');
    section.className = 'lpfjs-section';
    
    if (title) {
      const heading = document.createElement('h3');
      heading.className = 'lpfjs-heading';
      heading.textContent = title;
      section.appendChild(heading);
    }
    
    return section;
  };

  // Create a button
  const createButton = function(text, onClick) {
    const button = document.createElement('button');
    button.className = 'lpfjs-button';
    button.textContent = text;
    
    if (onClick) {
      button.addEventListener('click', onClick);
    }
    
    return button;
  };

  // Create a message element
  const createMessage = function(text) {
    const message = document.createElement('p');
    message.textContent = text;
    message.style.fontSize = '13px';
    message.style.margin = '0 0 12px 0';
    
    return message;
  };

  // Show a notification
  const showNotification = function(message, type = 'info') {
    // Get existing notification container or create a new one
    let container = document.querySelector('.lpfjs-notification-container');
    
    if (!container) {
      container = document.createElement('div');
      container.className = 'lpfjs-notification-container';
      container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        width: 300px;
      `;
      document.body.appendChild(container);
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `lpfjs-notification lpfjs-notification-${type}`;
    notification.style.cssText = `
      background-color: ${type === 'error' ? '#f8d7da' : '#d4edda'};
      color: ${type === 'error' ? '#721c24' : '#155724'};
      padding: 12px;
      margin-bottom: 10px;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      position: relative;
      animation: lpfjs-notification-fade-in 0.3s ease-out forwards;
    `;
    
    // Add animation if not exists
    if (!document.getElementById('lpfjs-notification-animations')) {
      const animations = document.createElement('style');
      animations.id = 'lpfjs-notification-animations';
      animations.textContent = `
        @keyframes lpfjs-notification-fade-in {
          from { opacity: 0; transform: translateY(-20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes lpfjs-notification-fade-out {
          from { opacity: 1; transform: translateY(0); }
          to { opacity: 0; transform: translateY(-20px); }
        }
      `;
      document.head.appendChild(animations);
    }
    
    // Add message
    notification.textContent = message;
    
    // Add close button
    const closeBtn = document.createElement('span');
    closeBtn.style.cssText = `
      position: absolute;
      top: 5px;
      right: 10px;
      cursor: pointer;
      font-size: 18px;
      font-weight: bold;
    `;
    closeBtn.textContent = '×';
    closeBtn.onclick = () => {
      notification.style.animation = 'lpfjs-notification-fade-out 0.3s ease-in forwards';
      setTimeout(() => {
        notification.remove();
      }, 300);
    };
    
    notification.appendChild(closeBtn);
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = 'lpfjs-notification-fade-out 0.3s ease-in forwards';
        setTimeout(() => {
          notification.remove();
        }, 300);
      }
    }, 5000);
  };
  
  // Return public functions
  return {
    addStyles: addStyles,
    createSidebar: createSidebar,
    createSection: createSection,
    createButton: createButton,
    createMessage: createMessage,
    showNotification: showNotification
  };
})();