// Privacy-friendly visitor counts via GoatCounter (no cookies, no personal data).
// To switch on: create a free account at goatcounter.com, then put its code below,
// e.g. var GOATCOUNTER_CODE = 'praxben';   (the part before .goatcounter.com)
var GOATCOUNTER_CODE = '';
(function () {
  if (!GOATCOUNTER_CODE || location.hostname === 'localhost') return;
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://gc.zgo.at/count.js';
  s.setAttribute('data-goatcounter', 'https://' + GOATCOUNTER_CODE + '.goatcounter.com/count');
  document.head.appendChild(s);
})();
