(function () {
  'use strict';
  var GA_ID = 'G-BQZEQC5T49';
  var KEY = 'edd_cookie_consent';

  // 1. Inicializa dataLayer e função gtag
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;

  // 2. Consent Mode v2 — negado por defeito (RGPD)
  gtag('consent', 'default', {
    analytics_storage: 'denied',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    wait_for_update: 500
  });

  // 3. Carrega gtag.js de forma assíncrona
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
  document.head.appendChild(s);

  // 4. Configura GA4 (sem page_view automático — enviamos manualmente)
  gtag('js', new Date());
  gtag('config', GA_ID, { send_page_view: false });

  // 5. Se o utilizador já aceitou anteriormente, activa imediatamente
  if (localStorage.getItem(KEY) === 'accepted') {
    gtag('consent', 'update', { analytics_storage: 'granted' });
    gtag('event', 'page_view');
  }

  // 6. Quando o utilizador aceitar no banner, activa o tracking
  document.addEventListener('edd:consent-accepted', function () {
    gtag('consent', 'update', { analytics_storage: 'granted' });
    gtag('event', 'page_view');
  });
})();
