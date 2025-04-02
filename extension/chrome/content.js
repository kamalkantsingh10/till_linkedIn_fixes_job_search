// Main content script and router
(function() {
    // Page type constants
    const PAGE_TYPES = {
      PROFILE: 'profile',
      JOB: 'job',
      OTHER: 'other'
    };
  
    // Detect the type of LinkedIn page we're on
    const detectPageType = function() {
      const url = window.location.href;
      
      if (url.includes('linkedin.com/in/')) {
        return PAGE_TYPES.PROFILE;
      } else if (url.includes('linkedin.com/jobs/view/')) {
        return PAGE_TYPES.JOB;
      } else {
        return PAGE_TYPES.OTHER;
      }
    };
  
    // Route to the appropriate module based on page type
    const routeToModule = function(pageType) {
      console.log('LPFJS routing to page type:', pageType);
      
      // Clear previous sidebar content if exists
      const existingSidebar = document.querySelector('.lpfjs-container');
      if (existingSidebar) {
        existingSidebar.remove();
      }
      
      // Initialize UI with base styles and sidebar
      LPFJS_UI.addStyles();
      const sidebar = LPFJS_UI.createSidebar(pageType);
      
      // Route to specific module based on page type
      switch (pageType) {
        case PAGE_TYPES.PROFILE:
          LPFJS_Profile.initProfilePage(sidebar);
          break;
        case PAGE_TYPES.JOB:
          LPFJS_Job.initJobPage(sidebar);
          break;
        default:
          // Add default content for other pages
          const content = sidebar.querySelector('.lpfjs-content');
          const message = document.createElement('p');
          message.textContent = 'Navigate to a LinkedIn profile or job listing to use the extension.';
          message.style.padding = '16px';
          content.appendChild(message);
      }
      
      // Apply active class to body
      document.body.classList.add('lpfjs-active');
    };
  
    // Handle initial page load
    const initializeLPFJS = function() {
      // Detect current page type and route to appropriate module
      const pageType = detectPageType();
      routeToModule(pageType);
      
      console.log('LPFJS initialized successfully!');
    };
  
    // Handle page navigation with MutationObserver
    const setupNavigationObserver = function() {
      let lastUrl = location.href;
      
      const observer = new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
          lastUrl = url;
          console.log('LPFJS detected page navigation to:', url);
          
          // Remove body classes
          document.body.classList.remove('lpfjs-active');
          document.body.classList.remove('sidebar-collapsed');
          
          // Re-initialize on page change
          const pageType = detectPageType();
          routeToModule(pageType);
        }
      });
      
      observer.observe(document, {subtree: true, childList: true});
    };
  
    // Handle messages from popup or background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.action === 'toggle_sidebar') {
        // Toggle sidebar visibility
        const container = document.querySelector('.lpfjs-container');
        if (container) {
          container.classList.toggle('collapsed');
          document.body.classList.toggle('sidebar-collapsed');
          
          // Store state in Chrome storage
          chrome.storage.sync.set({
            sidebarExpanded: !container.classList.contains('collapsed')
          });
          
          sendResponse({ success: true });
        } else {
          sendResponse({ success: false, error: 'Sidebar not initialized' });
        }
        return true;
      } 
      
      if (message.action === 'get_page_type') {
        // Return the current page type
        sendResponse({ success: true, pageType: detectPageType() });
        return true;
      }
      
      return false;
    });
  
    // Initialize when the page is fully loaded
    if (document.readyState === 'complete') {
      initializeLPFJS();
      setupNavigationObserver();
    } else {
      window.addEventListener('load', function() {
        initializeLPFJS();
        setupNavigationObserver();
      });
    }
  })();