import './styles.css';
import 'iconify-icon';
import Lenis from 'lenis';
import 'lenis/dist/lenis.css';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let lenis = null;
let lastScroll = 0;
let loaderFinished = false;

function splitWords(element) {
  if (!element || element.dataset.splitReady === 'true') return;
  const text = element.textContent.trim();
  const parts = element.textContent.split(/(\s+)/);
  element.textContent = '';
  element.setAttribute('aria-label', text);
  parts.forEach((part) => {
    if (!part.trim()) {
      element.appendChild(document.createTextNode(part));
      return;
    }
    const mask = document.createElement('span');
    const word = document.createElement('span');
    mask.className = 'split-word-mask';
    word.className = 'split-word';
    word.textContent = part;
    word.setAttribute('aria-hidden', 'true');
    mask.appendChild(word);
    element.appendChild(mask);
  });
  element.dataset.splitReady = 'true';
}

function removeLoader() {
  if (loaderFinished) return;
  loaderFinished = true;
  document.querySelector('[data-preloader]')?.remove();
}

function runIntro() {
  const loader = document.querySelector('[data-preloader]');
  if (!loader || reduceMotion) {
    removeLoader();
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    const value = loader.querySelector('[data-loader-value]');
    const counter = { value: 0 };
    const tl = gsap.timeline({
      defaults: { ease: 'power3.out' },
      onComplete: () => {
        removeLoader();
        resolve();
      },
    });

    tl.to(counter, {
      value: 100,
      duration: 1.15,
      onUpdate: () => { value.textContent = String(Math.round(counter.value)).padStart(2, '0'); },
    }, 0)
      .to('[data-preloader-bar]', { scaleX: 1, duration: 1.15 }, 0)
      .to('.preloader__word', { yPercent: -8, opacity: .75, duration: .7 }, .72)
      .to(loader, { clipPath: 'inset(0 0 100% 0)', duration: .85, ease: 'power4.inOut' }, 1.22);
  });
}

function initSmoothScroll() {
  if (reduceMotion) return;
  lenis = new Lenis({ lerp: 0.085, smoothWheel: true, wheelMultiplier: .88 });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add(lenisRaf);
  gsap.ticker.lagSmoothing(0);
}

function lenisRaf(time) {
  lenis?.raf(time * 1000);
}

function initHeader() {
  const header = document.querySelector('[data-header]');
  const menuToggle = document.querySelector('.menu-toggle');
  const mobileNav = document.querySelector('.mobile-nav');

  const updateHeader = () => {
    const current = window.scrollY;
    header.classList.toggle('is-solid', current > 24);
    header.classList.toggle('is-hidden', current > lastScroll && current > 170 && !mobileNav.classList.contains('is-open'));
    lastScroll = current;
  };
  window.addEventListener('scroll', updateHeader, { passive: true });

  menuToggle.addEventListener('click', () => {
    const open = !mobileNav.classList.contains('is-open');
    mobileNav.classList.toggle('is-open', open);
    menuToggle.setAttribute('aria-expanded', String(open));
    header.classList.remove('is-hidden');
  });

  mobileNav.querySelectorAll('a, button').forEach((item) => item.addEventListener('click', () => {
    mobileNav.classList.remove('is-open');
    menuToggle.setAttribute('aria-expanded', 'false');
  }));
}

function initHeroMotion() {
  if (reduceMotion) return;
  const hero = document.querySelector('.hero');
  const image = document.querySelector('.hero__image');
  const media = document.querySelector('.hero__media');
  if (!hero || !image || !media) return;

  const intro = gsap.timeline({ defaults: { ease: 'power4.out' } });
  intro
    .fromTo('[data-hero-line]', { yPercent: 115 }, { yPercent: 0, duration: 1.15, stagger: .12 })
    .fromTo('[data-hero-item]', { y: 24, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: .85, stagger: .12 }, '-=.72');

  if (window.matchMedia('(pointer: fine)').matches) {
    const xTo = gsap.quickTo(image, 'x', { duration: 1.1, ease: 'power3.out' });
    const yTo = gsap.quickTo(image, 'y', { duration: 1.1, ease: 'power3.out' });
    const reset = () => { xTo(0); yTo(0); };
    hero.addEventListener('pointermove', (event) => {
      const rect = hero.getBoundingClientRect();
      xTo(((event.clientX - rect.left) / rect.width - .5) * -14);
      yTo(((event.clientY - rect.top) / rect.height - .5) * -9);
    });
    hero.addEventListener('pointerleave', reset);
    window.addEventListener('blur', reset);
    document.addEventListener('visibilitychange', () => { if (document.hidden) reset(); });
  }
}

function initSplitReveals() {
  document.querySelectorAll('[data-split-reveal]').forEach((element) => splitWords(element));
  if (reduceMotion) return;
  document.querySelectorAll('[data-split-reveal]').forEach((element) => {
    const words = element.querySelectorAll('.split-word');
    gsap.fromTo(words,
      { yPercent: 112, autoAlpha: 0, filter: 'blur(7px)' },
      { yPercent: 0, autoAlpha: 1, filter: 'blur(0px)', duration: .95, stagger: .035, ease: 'power4.out', scrollTrigger: { trigger: element, start: 'top 84%', once: true } },
    );
  });
}

function initSectionReveals() {
  if (reduceMotion) return;
  document.querySelectorAll('[data-story-section]').forEach((section) => {
    const items = section.querySelectorAll('[data-reveal-item]');
    if (!items.length) return;
    gsap.fromTo(items,
      { y: 34, autoAlpha: 0, filter: 'blur(7px)' },
      { y: 0, autoAlpha: 1, filter: 'blur(0px)', duration: 1, stagger: .09, ease: 'power4.out', scrollTrigger: { trigger: section, start: 'top 82%', once: true } },
    );
  });
}

function initParallax() {
  if (reduceMotion || window.innerWidth < 720) return;
  document.querySelectorAll('[data-parallax-layer]').forEach((layer) => {
    const speed = Number(layer.dataset.speed || -.08);
    const section = layer.closest('[data-parallax-section]') || layer;
    gsap.to(layer, {
      y: () => window.innerHeight * speed,
      ease: 'none',
      scrollTrigger: { trigger: section, start: 'top bottom', end: 'bottom top', scrub: 1, invalidateOnRefresh: true },
    });
  });
}

function initStickyCards() {
  if (reduceMotion || window.innerWidth < 700) return;
  document.querySelectorAll('[data-sticky-stack]').forEach((stack) => {
    const cards = [...stack.querySelectorAll('[data-stack-card]')];
    cards.forEach((card, index) => {
      const next = cards[index + 1];
      if (!next) return;
      gsap.to(card, {
        scale: .93 + index * .015,
        autoAlpha: .7,
        y: -22,
        ease: 'none',
        scrollTrigger: { trigger: next, start: 'top 80%', end: 'top 20%', scrub: 1, invalidateOnRefresh: true },
      });
    });
  });
}

function initFooterReveal() {
  if (reduceMotion) return;
  const closing = document.querySelector('[data-footer-parallax]');
  gsap.fromTo(closing, { yPercent: -5 }, { yPercent: 0, ease: 'none', scrollTrigger: { trigger: closing, start: 'top bottom', end: 'top 30%', scrub: 1 } });
  gsap.to('.closing__glow', { rotate: 18, scale: 1.08, ease: 'none', scrollTrigger: { trigger: closing, start: 'top bottom', end: 'bottom bottom', scrub: 1.2 } });
}

function initChat() {
  const panel = document.querySelector('.chat-panel');
  const fab = document.querySelector('.chat-fab');
  const close = document.querySelector('.chat-close');
  const form = document.querySelector('.composer');
  const input = document.querySelector('#chat-input');
  const send = form.querySelector('button');
  const messages = document.querySelector('.messages');
  let previouslyFocused = null;

  const setOpen = (open) => {
    if (open) previouslyFocused = document.activeElement;
    panel.classList.toggle('is-open', open);
    panel.setAttribute('aria-hidden', String(!open));
    fab.setAttribute('aria-expanded', String(open));
    fab.style.opacity = open ? '0' : '1';
    fab.style.pointerEvents = open ? 'none' : '';
    if (open) window.setTimeout(() => input.focus(), 120);
    else previouslyFocused?.focus?.();
  };

  const addMessage = (text, role, urgent = false) => {
    const article = document.createElement('article');
    article.className = `message message--${role}${urgent ? ' message--urgent' : ''}`;
    const label = document.createElement('span');
    label.textContent = role === 'user' ? 'YOU' : 'STRIDE / PRIVATE LINE';
    const body = document.createElement('p');
    body.textContent = text;
    article.append(label, body);
    messages.append(article);
    messages.scrollTop = messages.scrollHeight;
  };

  const sendMessage = async (message) => {
    setOpen(true);
    addMessage(message, 'user');
    input.value = '';
    send.disabled = true;
    const typing = document.createElement('p');
    typing.className = 'typing';
    typing.textContent = 'Stride is considering your question…';
    messages.append(typing);
    messages.scrollTop = messages.scrollHeight;
    try {
      const response = await fetch(`${(import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      if (!response.ok) throw new Error('Request failed');
      const data = await response.json();
      addMessage(data.final_response, 'assistant', data.urgent === true);
    } catch {
      addMessage('The private line is temporarily unavailable. Please try again shortly. For urgent symptoms, seek immediate medical care.', 'assistant', true);
    } finally {
      typing.remove();
      send.disabled = false;
      input.focus();
    }
  };

  fab.addEventListener('click', () => setOpen(true));
  close.addEventListener('click', () => setOpen(false));
  document.querySelectorAll('.open-chat').forEach((button) => button.addEventListener('click', (event) => { event.preventDefault(); setOpen(true); }));
  document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => sendMessage(button.dataset.prompt)));
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (message) sendMessage(message);
  });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && panel.classList.contains('is-open')) setOpen(false); });
}

async function init() {
  initHeader();
  initChat();
  initSmoothScroll();
  await runIntro();
  initHeroMotion();
  initSplitReveals();
  initSectionReveals();
  initParallax();
  initStickyCards();
  initFooterReveal();
  window.setTimeout(() => ScrollTrigger.refresh(), 180);
}

window.addEventListener('load', init, { once: true });
window.setTimeout(removeLoader, 5000);

window.addEventListener('pagehide', () => {
  lenis?.destroy();
  gsap.ticker.remove(lenisRaf);
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
});
