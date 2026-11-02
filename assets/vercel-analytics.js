(function () {
  'use strict';
  
  // Vercel Web Analytics
  // This script enables Vercel Web Analytics for the site
  // Documentation: https://vercel.com/docs/analytics/quickstart
  
  window.va = window.va || function () { 
    (window.vaq = window.vaq || []).push(arguments); 
  };
  
  // Load the Vercel Analytics script
  var script = document.createElement('script');
  script.defer = true;
  script.src = '/_vercel/insights/script.js';
  document.head.appendChild(script);
})();
