/* Interactive engraving: the approved image is fixed; ink responds to touch. */
const cards = [...document.querySelectorAll('.ac-art[data-engraving]')];
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const wide = matchMedia('(min-width: 801px)');
const fine = matchMedia('(hover: hover) and (pointer: fine)');
const states = [];
let runtime;
const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

function loadMotion() {
  if (!runtime) runtime = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = new URL('../../vendor/gsap-3.15.0/gsap.min.js', import.meta.url).href;
    script.onload = () => window.gsap ? resolve(window.gsap) : reject(new Error('Motion runtime unavailable'));
    script.onerror = () => reject(new Error('Motion runtime failed to load'));
    document.head.append(script);
  });
  return runtime;
}

function visible(s) {
  const route = s.card.closest('[data-route]');
  return (wide.matches || s.card.hasAttribute('data-art-preview')) && s.visible && !document.hidden && (!route || route.classList.contains('on'));
}

function hint(s) {
  const en = document.documentElement.lang === 'en';
  s.touch.querySelector('span').textContent = s.drag
    ? (en ? 'Release the wind ↗' : '松手，让风向上 ↗')
    : (en ? 'Hold & pull ↗' : '按住握手，向上牵引 ↗');
}

function labels(s) {
  const en = document.documentElement.lang === 'en';
  s.touch.hidden = !s.ready || reduced.matches;
  s.touch.setAttribute('aria-label', en ? 'Hold and drag the handshake, then release. Keyboard: hold Space or press Enter.' : '按住握手拖动，松手释放风。键盘：按住空格蓄力，回车轻触。');
  hint(s);
}

function cancelGrip(s) {
  const drag = s.drag;
  s.drag = null;
  s.card.dataset.gripping = 'false';
  s.card.dataset.charge = '0';
  if (drag?.id != null && s.touch.hasPointerCapture(drag.id)) s.touch.releasePointerCapture(drag.id);
  if (s.tethers) s.tethers.forEach(path => path.setAttribute('opacity', '0'));
  hint(s);
}

function rest(s) {
  cancelAnimationFrame(s.frame);
  s.frame = 0;
  s.activeUntil = 0;
  s.activity = 0;
  s.card.dataset.running = 'false';
  s.burst?.kill();
  s.gsap.killTweensOf(s);
  cancelGrip(s);
  s.trail.length = 0;
  s.pointer.inside = false;
  s.kick = 0;
  s.spring = { x: 0, y: 0, vx: 0, vy: 0 };
  s.light.style.opacity = '0';
  s.field.style.opacity = '.24';
  s.spark.forEach(path => path.style.opacity = '0');
  s.traces.forEach(path => path.setAttribute('d', ''));
  s.ribbons.forEach((path, i) => path.setAttribute('d', bandPath(s, i, false)));
  s.card.dataset.phase = 'idle';
}

// Each gesture owns a short animation window; the print rests between gestures.
function wake(s, duration = 1600) {
  if (!s.running) return;
  const now = performance.now();
  s.activeUntil = Math.max(s.activeUntil, now + duration);
  if (!s.frame) {
    s.card.dataset.running = 'true';
    s.last = now;
    s.frame = requestAnimationFrame(time => tick(s, time));
  }
}

function sync() {
  states.forEach(s => {
    const inView = visible(s);
    if (inView && !s.started && !reduced.matches) init(s);
    const formFocused = Boolean(s.card.parentElement.querySelector('.ac-main:focus-within'));
    const running = Boolean(inView && s.ready && !reduced.matches && !formFocused);
    const wasRunning = s.running;
    s.running = running;
    if (s.ready && !running && wasRunning) rest(s);
    labels(s);
  });
}

function point(s, event) {
  const rect = s.card.getBoundingClientRect();
  return { x: clamp((event.clientX - rect.left) / rect.width * 1024, -160, 1184),
    y: clamp((event.clientY - rect.top) / rect.height * 1536, -160, 1696) };
}

function bandPath(s, index, moving = true) {
  const points = [];
  for (let j = 0; j <= 38; j++) {
    const t = j / 38, x = -100 + t * 1224;
    const base = 1228 - 374 * t * t + 37 * Math.sin(t * Math.PI * 3.5) + index * 12;
    const gripWeight = Math.exp(-Math.pow((t - .57) * 3.2, 2));
    const distance = Math.hypot(x - s.pointer.x, base - s.pointer.y);
    const brush = moving && s.pointer.inside ? Math.exp(-distance * distance / 85000) * Math.sin(t * 10 + s.clock * 2) * 20 * s.activity : 0;
    const wave = moving ? Math.exp(-Math.pow((t - s.wave) * 7, 2)) * Math.sin((t - s.wave) * 19 - index * .13) * s.kick * 90 : 0;
    const y = base + (moving ? s.spring.y * gripWeight + Math.sin(s.clock * .7 + t * 5 + index * .25) * 3 * s.activity : 0) + brush + wave;
    points.push(`${(x + (moving ? s.spring.x * gripWeight : 0)).toFixed(1)},${y.toFixed(1)}`);
  }
  return 'M' + points.join(' L');
}

function tick(s, time) {
  s.frame = 0;
  if (!s.running) return;
  if (!s.drag && time >= s.activeUntil) { rest(s); return; }
  s.activity = s.drag ? 1 : clamp((s.activeUntil - time) / 750, 0, 1);
  const dt = Math.min((time - s.last) / 1000, .035);
  s.last = time; s.clock += dt;
  let targetX = 0, targetY = 0;
  if (s.drag) {
    const dx = s.pointer.x - s.drag.x, dy = s.pointer.y - s.drag.y;
    s.charge = clamp((time - s.drag.time) / 1800 + Math.hypot(dx, dy) / 350, 0, 1);
    targetX = clamp(dx * .65, -125, 125);
    targetY = clamp(dy * .7 - s.charge * 58, -190, 130);
    s.card.dataset.charge = String(Math.round(s.charge * 10));
    s.tethers.forEach((path, i) => {
      path.setAttribute('d', `M${s.drag.x} ${s.drag.y} Q${(s.drag.x + s.pointer.x) / 2 + (i - 1) * 14} ${(s.drag.y + s.pointer.y) / 2 - 28 - s.charge * 42} ${s.pointer.x} ${s.pointer.y}`);
      path.setAttribute('opacity', String(.38 + s.charge * .35));
    });
  } else if (s.pointer.inside) {
    targetX = (s.pointer.x - 512) * .045 * s.activity;
    targetY = (s.pointer.y - 768) * .035 * s.activity;
  }
  const k = s.spring;
  k.vx += ((targetX - k.x) * 72 - k.vx * 10) * dt;
  k.vy += ((targetY - k.y) * 72 - k.vy * 10) * dt;
  k.x += k.vx * dt; k.y += k.vy * dt;
  s.ribbons.forEach((path, i) => {
    path.setAttribute('d', bandPath(s, i));
    path.style.strokeDashoffset = String(i * 44 - s.clock * 35);
  });
  s.spark.forEach((path, i) => path.setAttribute('d', bandPath(s, i * 3)));
  s.field.style.opacity = String(s.drag ? .5 + s.charge * .4 : .24 + .12 * s.activity + s.kick * .3);
  s.light.style.opacity = String(s.drag ? .2 + s.charge * .6 : (s.pointer.inside ? .14 * s.activity : 0) + s.kick * .3);
  s.trail = s.trail.filter(p => time - p.time < 950);
  const d = s.trail.length > 1 ? 'M' + s.trail.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' L') : '';
  const age = s.trail.length ? time - s.trail[s.trail.length - 1].time : 950;
  s.traces.forEach((path, i) => {
    path.setAttribute('d', d);
    path.setAttribute('opacity', String((1 - age / 950) * (.75 - i * .16)));
  });
  s.frame = requestAnimationFrame(t => tick(s, t));
}

function burst(s, strength) {
  if (!s.running) return;
  wake(s, 2800);
  s.burst?.kill();
  s.card.dataset.phase = 'release';
  s.card.dataset.interactions = String(Number(s.card.dataset.interactions || 0) + 1);
  s.card.dataset.lastStrength = strength.toFixed(2);
  s.spring.vy -= 270 * strength;
  s.burst = s.gsap.timeline({ onComplete: () => { if (!s.drag) s.card.dataset.phase = 'idle'; } });
  s.burst.fromTo(s, { wave: -.2, kick: strength }, { wave: 1.3, duration: 2.1, ease: 'none' }, 0)
    .to(s, { kick: 0, duration: 1.4, ease: 'power2.out' }, .9)
    .fromTo(s.spark, { opacity: .9, strokeDashoffset: 1300 }, { opacity: .65, strokeDashoffset: -1600, duration: 2.3, stagger: .08, ease: 'power1.out' }, 0)
    .to(s.spark, { opacity: 0, duration: .3 }, 2);
}

function beginGrip(s, p, id = null) {
  if (!s.running || s.drag) return;
  s.burst?.kill();
  s.kick = 0;
  s.spark.forEach(path => path.style.opacity = '0');
  s.drag = { ...p, id, time: performance.now() };
  s.pointer = { ...p, inside: true };
  s.charge = 0;
  s.card.dataset.gripping = 'true';
  s.card.dataset.phase = 'hold';
  if (id != null) s.touch.setPointerCapture(id);
  wake(s);
  hint(s);
}

function releaseGrip(s) {
  if (!s.drag) return;
  const age = (performance.now() - s.drag.time) / 1800;
  const distance = Math.hypot(s.pointer.x - s.drag.x, s.pointer.y - s.drag.y) / 350;
  const strength = .35 + clamp(age + distance, 0, 1) * .9;
  cancelGrip(s);
  s.pointer.inside = false;
  burst(s, strength);
}

async function init(s) {
  s.started = true;
  try {
    const gsap = await loadMotion();
    const id = `engraving-cutout-${states.indexOf(s)}`;
    s.layer.innerHTML = `<svg class="ac-wind" viewBox="0 0 1024 1536" aria-hidden="true">
      <defs><mask id="${id}" maskUnits="userSpaceOnUse" x="-180" y="0" width="1400" height="1536">
        <rect x="-180" width="1400" height="1536" fill="white"/>
        <rect x="40" y="80" width="330" height="96" fill="black"/>
        <rect x="35" y="183" width="730" height="266" fill="black"/>
        <rect x="35" y="480" width="540" height="247" fill="black"/>
        <path d="M0 1295 L110 1240 342 1010 453 883 463 810 522 739 677 638 737 461 801 326 1024 0 1100 0 1100 458 909 650 817 769 785 930 771 1047 726 1157 645 1211 557 1241 459 1328 325 1482 314 1570 -50 1570Z" fill="black"/>
      </mask></defs>
      <g mask="url(#${id})">
        <g class="ac-wind-field">${Array.from({ length: 9 }, (_, i) => `<path class="ac-ribbon" style="--flow-color:${i % 3 === 0 ? '#4E3F66' : '#2F63B8'}"/>`).join('')}</g>
        ${[0, 1, 2].map(() => '<path class="ac-spark" pathLength="1600"/>').join('')}
        ${[0, 1, 2].map((i) => `<path class="ac-ink-trace" transform="translate(${i * 3},${i * 5})" style="--flow-color:${i === 1 ? '#4E3F66' : '#2F63B8'}"/>`).join('')}
      </g>
      <g class="ac-tethers">${[0, 1, 2].map(() => '<path class="ac-tether" opacity="0"/>').join('')}</g>
      </svg><div class="ac-ink-light"></div>`;
    Object.assign(s, {
      gsap, field: s.layer.querySelector('.ac-wind-field'),
      light: s.layer.querySelector('.ac-ink-light'),
      spark: [...s.layer.querySelectorAll('.ac-spark')],
      ribbons: [...s.layer.querySelectorAll('.ac-ribbon')],
      traces: [...s.layer.querySelectorAll('.ac-ink-trace')],
      tethers: [...s.layer.querySelectorAll('.ac-tether')]
    });
    s.ribbons.forEach((path, i) => {
      path.setAttribute('d', bandPath(s, i, false));
      path.style.strokeDashoffset = String(i * 44);
    });
    s.ready = true; s.card.dataset.ready = 'true';
    sync();
  } catch (error) {
    console.warn('Engraved artwork stays static:', error.message);
    s.layer.replaceChildren();
  }
}

cards.forEach(card => {
  const s = {
    card, layer: card.querySelector('.ac-engraving-effects'),
    touch: card.querySelector('.ac-touch'),
    started: false, ready: false, visible: false, running: false, frame: 0, clock: 0, activeUntil: 0, activity: 0,
    pointer: { x: 600, y: 930, inside: false }, spring: { x: 0, y: 0, vx: 0, vy: 0 },
    trail: [], drag: null, wave: 0, kick: 0, charge: 0
  };
  states.push(s);
  new IntersectionObserver(entries => { s.visible = entries[0].isIntersecting; sync(); }, { threshold: .06 }).observe(card);
  card.addEventListener('pointerenter', event => {
    if (!s.running || !fine.matches) return;
    s.pointer = { ...point(s, event), inside: true };
    wake(s);
  });
  card.addEventListener('pointermove', event => {
    if (!s.running || (!fine.matches && !s.drag)) return;
    const p = point(s, event), now = performance.now();
    const last = s.trail[s.trail.length - 1];
    if (!s.drag && (!last || Math.hypot(p.x - last.x, p.y - last.y) > 6)) {
      s.trail.push({ ...p, time: now });
      if (s.trail.length > 40) s.trail.shift();
    }
    s.pointer = { ...p, inside: true };
    wake(s);
  }, { passive: true });
  card.addEventListener('pointerleave', () => {
    if (!s.drag) { s.pointer.inside = false; wake(s); }
  });
  s.touch.addEventListener('pointerdown', event => {
    if (event.button !== 0 || !s.running) return;
    event.preventDefault();
    card.dataset.input = 'pointer';
    s.touch.focus({ preventScroll: true });
    beginGrip(s, point(s, event), event.pointerId);
  });
  s.touch.addEventListener('pointerup', event => {
    if (s.drag?.id !== event.pointerId) return;
    s.pointer = { ...point(s, event), inside: true };
    releaseGrip(s);
  });
  s.touch.addEventListener('pointercancel', () => { cancelGrip(s); s.card.dataset.phase = 'idle'; });
  s.touch.addEventListener('lostpointercapture', () => {
    if (s.drag) { cancelGrip(s); s.card.dataset.phase = 'idle'; }
  });
  s.touch.addEventListener('keydown', event => {
    if (!s.running) return;
    card.dataset.input = 'keyboard';
    if (event.code === 'Space') {
      event.preventDefault();
      if (!event.repeat) beginGrip(s, { x: 600, y: 930 });
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (!event.repeat) burst(s, .7);
    } else if (event.key === 'Escape') {
      cancelGrip(s); s.card.dataset.phase = 'idle';
    }
  });
  s.touch.addEventListener('keyup', event => {
    if (event.code === 'Space') { event.preventDefault(); releaseGrip(s); }
  });
  s.touch.addEventListener('blur', () => {
    if (s.drag?.id === null) { cancelGrip(s); s.card.dataset.phase = 'idle'; }
  });
  // Assistive technologies can activate the button without pointer or key events.
  s.touch.addEventListener('click', event => {
    if (event.detail === 0 && !s.drag) burst(s, .7);
  });
  card.parentElement.addEventListener('focusin', sync);
  card.parentElement.addEventListener('focusout', () => queueMicrotask(sync));
  const route = card.closest('[data-route]');
  if (route) new MutationObserver(sync).observe(route, { attributes: true, attributeFilter: ['class'] });
});
[reduced, wide].forEach(query => query.addEventListener('change', sync));
document.addEventListener('visibilitychange', sync);
document.addEventListener('keydown', event => {
  if (event.key === 'Tab') states.forEach(s => { s.card.dataset.input = 'keyboard'; });
});
window.addEventListener('hashchange', sync);
new MutationObserver(sync).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
sync();
