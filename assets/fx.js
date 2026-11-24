/* PraxBen site effects: scroll reveals, poster-number counters, header state, hero lamplight.
   Everything here is decoration: the page reads fine without it. */
(function(){
var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;

// Header darkens once you scroll
var header=document.querySelector('header');
function onScroll(){if(header)header.classList.toggle('scrolled',window.scrollY>12)}
onScroll();window.addEventListener('scroll',onScroll,{passive:true});

// Poster numbers count up when they come into view
function countUp(el){
var to=parseInt(el.getAttribute('data-count'),10);if(isNaN(to))return;
if(reduce){el.textContent=to;return}
var t0=null,dur=1600;
function step(t){if(!t0)t0=t;var p=Math.min(1,(t-t0)/dur),e=1-Math.pow(1-p,4);el.textContent=Math.round(to*e);if(p<1)requestAnimationFrame(step)}
requestAnimationFrame(step);
setTimeout(function(){el.textContent=to},dur+200); // land on the real number even if frames are throttled
}
window.pbSetCount=function(el,n){el.setAttribute('data-count',n);if(el.dataset.seen)countUp(el);else el.textContent=n};

// Reveal on scroll, staggering siblings that reveal together
var els=[].slice.call(document.querySelectorAll('[data-reveal],[data-count],.quote'));
if(!('IntersectionObserver' in window)||reduce){
els.forEach(function(el){el.classList.add('in');if(el.hasAttribute('data-count'))el.textContent=el.getAttribute('data-count')});
}else{
var io=new IntersectionObserver(function(entries){
var batch=0;
entries.forEach(function(en){
if(!en.isIntersecting)return;
var el=en.target;io.unobserve(el);
if(el.hasAttribute('data-reveal')&&!el.style.getPropertyValue('--d'))el.style.setProperty('--d',(batch++*0.08)+'s');
el.classList.add('in');
if(el.hasAttribute('data-count')){el.dataset.seen=1;countUp(el)}
});
},{rootMargin:'0px 0px -8% 0px',threshold:.12});
els.forEach(function(el){io.observe(el)});
}

// Reveal items the page adds later (feed, press list)
window.pbReveal=function(root){
if(!root)return;
var kids=[].slice.call(root.children);
kids.forEach(function(k,i){k.setAttribute('data-reveal','');k.style.setProperty('--d',Math.min(i,8)*0.06+'s');
if(reduce||!io){k.classList.add('in')}else io.observe(k)});
};

// Hero: a lamp pool follows the pointer
var hero=document.querySelector('.hero');
if(hero&&!reduce&&matchMedia('(pointer:fine)').matches){
var raf=0,x=68,y=42;
hero.addEventListener('pointermove',function(e){
var r=hero.getBoundingClientRect();x=(e.clientX-r.left)/r.width*100;y=(e.clientY-r.top)/r.height*100;
if(!raf)raf=requestAnimationFrame(function(){hero.style.setProperty('--mx',x+'%');hero.style.setProperty('--my',y+'%');raf=0});
});
}
})();
