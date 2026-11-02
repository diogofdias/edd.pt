(function () {
  'use strict';
  var GA_ID = 'G-BQZEQC5T49';
  var KEY = 'edd_cookie_consent';

  // 0. Vercel Web Analytics — sem cookies, conta todas as visitas (não depende do banner).
  //    Fica primeiro para não ser afetado por erros mais abaixo (ex.: localStorage bloqueado).
  //    Não carrega em localhost nem em ficheiros locais.
  var host = location.hostname;
  if (location.protocol !== 'file:' && host !== 'localhost' && host !== '127.0.0.1') {
    window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    var vs = document.createElement('script');
    vs.async = true;
    vs.src = '/_vercel/insights/script.js';
    document.head.appendChild(vs);
  }

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

  // 7. Rastreia cliques em telefone / WhatsApp
  document.addEventListener('click', function (e) {
    var el = e.target.closest('a[href]');
    if (!el) return;
    var href = el.getAttribute('href');
    if (href.startsWith('tel:') || href.indexOf('wa.me') !== -1) {
      gtag('event', 'phone_click', { link_url: href });
    }
    if (href.indexOf('buy.stripe.com') !== -1 || el.hasAttribute('data-checkout-cta')) {
      gtag('event', 'checkout_start', { link_url: href });
    }
  });

  // 8. Rastreia submissão de formulários de contacto
  document.addEventListener('submit', function (e) {
    var form = e.target;
    gtag('event', 'form_submit', {
      form_id: form.id || form.getAttribute('name') || 'contact'
    });
  });
})();
