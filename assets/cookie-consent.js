(function () {
  'use strict';
  var KEY = 'edd_cookie_consent';
  if (localStorage.getItem(KEY)) return;

  var css =
    '#edd-cb{position:fixed;bottom:0;left:0;right:0;background:#0E1218;' +
    'border-top:1px solid rgba(184,147,90,0.3);z-index:9999;' +
    'padding:1rem 1.5rem;box-shadow:0 -4px 20px rgba(0,0,0,0.35);}' +
    '#edd-cb-inner{max-width:1200px;margin:0 auto;display:flex;' +
    'align-items:center;justify-content:space-between;gap:1.5rem;flex-wrap:wrap;}' +
    '#edd-cb-text{font-family:system-ui,sans-serif;font-size:0.8125rem;' +
    'color:rgba(255,255,255,0.65);line-height:1.5;flex:1;min-width:200px;}' +
    '#edd-cb-text a{color:#B8935A;text-decoration:underline;text-underline-offset:2px;}' +
    '#edd-cb-btns{display:flex;gap:0.75rem;flex-shrink:0;}' +
    '#edd-cb-accept,#edd-cb-reject{font-family:system-ui,sans-serif;font-size:0.8125rem;' +
    'font-weight:500;border-radius:2px;cursor:pointer;padding:0.5rem 1.25rem;' +
    'letter-spacing:0.04em;white-space:nowrap;transition:all 0.2s;line-height:1.4;}' +
    '#edd-cb-accept{background:#B8935A;color:#fff;border:1px solid #B8935A;}' +
    '#edd-cb-accept:hover{background:#a07d4a;border-color:#a07d4a;}' +
    '#edd-cb-reject{background:transparent;color:rgba(255,255,255,0.55);' +
    'border:1px solid rgba(255,255,255,0.2);}' +
    '#edd-cb-reject:hover{border-color:rgba(255,255,255,0.5);color:#fff;}' +
    '@media(max-width:768px){#edd-cb{bottom:4.5rem;}' +
    '#edd-cb-inner{flex-direction:column;align-items:flex-start;}' +
    '#edd-cb-btns{width:100%;}' +
    '#edd-cb-accept,#edd-cb-reject{flex:1;text-align:center;}}';

  var styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  var banner = document.createElement('div');
  banner.id = 'edd-cb';
  banner.setAttribute('role', 'dialog');
  banner.setAttribute('aria-modal', 'false');
  banner.setAttribute('aria-label', 'Consentimento de cookies');
  banner.innerHTML =
    '<div id="edd-cb-inner">' +
      '<p id="edd-cb-text">Utilizamos cookies técnicos para o correto funcionamento do site. ' +
      'Consulte a nossa <a href="/politica-privacidade.html">Política de Privacidade</a>.</p>' +
      '<div id="edd-cb-btns">' +
        '<button id="edd-cb-reject">Rejeitar não essenciais</button>' +
        '<button id="edd-cb-accept">Aceitar</button>' +
      '</div>' +
    '</div>';

  function dismiss(value) {
    localStorage.setItem(KEY, value);
    banner.style.transition = 'opacity 0.3s';
    banner.style.opacity = '0';
    setTimeout(function () {
      if (banner.parentNode) banner.parentNode.removeChild(banner);
      if (styleEl.parentNode) styleEl.parentNode.removeChild(styleEl);
    }, 320);
  }

  function attach() {
    document.body.appendChild(banner);
    document.getElementById('edd-cb-accept').addEventListener('click', function () {
      dismiss('accepted');
    });
    document.getElementById('edd-cb-reject').addEventListener('click', function () {
      dismiss('rejected');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attach);
  } else {
    attach();
  }
})();
