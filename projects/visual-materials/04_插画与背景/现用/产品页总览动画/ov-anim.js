/* Native, dependency-free; supports multiple instances and direct file:// preview. */
(() => {
  'use strict';
  const scriptURL = document.currentScript.src;
  const defaultAssets = new URL('layers/', scriptURL).href;
  const NS = 'http://www.w3.org/2000/svg';
  const tiers = [
    { rim: 'M278 218 L577 51 L994 273 L697 436 Z', front: 'M278 242 L697 457 L994 295',
      hit: '278,218 529,80 626,30 743,86 743,132 994,273 994,295 697,457 278,242',
      down: ['M600 285 L600 331','M575 401 L575 450'], up: ['M617 298 L617 327','M604 414 L604 444'] },
    { rim: 'M278 478 L497 356 L699 460 L783 415 L992 533 L700 688 Z', front: 'M278 501 L700 709 L992 550',
      hit: '278,478 497,356 699,460 783,415 992,533 992,550 700,709 278,501',
      down: ['M584 541 L584 585','M577 659 L577 695'], up: ['M601 550 L601 592','M608 675 L608 705'] },
    { rim: 'M249 716 L461 602 L700 712 L776 672 L1004 805 L718 961 Z', front: 'M249 739 L718 981 L1004 826',
      hit: '249,716 461,602 700,712 776,672 1004,805 1004,826 718,981 249,739',
      down: ['M610 938 L610 984'], up: ['M638 937 L638 976'] },
    { rim: 'M223 971 L437 849 L718 984 L763 961 L1004 1095 L701 1232 Z', front: 'M223 995 L701 1250 L1004 1117',
      hit: '223,971 381,859 437,849 718,984 812,989 899,951 941,887 948,893 924,951 984,1036 974,1041 943,1017 1004,1095 1004,1117 701,1250 223,995',
      down: [], up: [] }
  ];
  // Visible centerlines traced on the supplied artwork, avoiding device faces.
  const circuits = [
    ['M452 235 L530 278 Q537 282 545 277 L563 267', 'M713 258 L785 299 Q793 304 801 299 L815 291', 'M632 320 L670 341'],
    ['M447 474 L493 499 Q500 504 507 499 L513 495', 'M683 500 L707 514 Q714 518 722 514 L767 489', 'M630 553 L690 587'],
    ['M616 704 L690 744 Q700 748 699 757', 'M622 785 L622 805 Q622 811 630 815 L660 831 Q667 835 674 830', 'M579 837 L630 865 L641 858 Q646 855 653 860 L685 879 Q693 885 701 880 L731 863'],
    ['M540 1021 L593 1051', 'M499 1068 L606 1127 Q614 1131 622 1126 L634 1119', 'M676 1115 L748 1156 Q756 1161 764 1156 L814 1128']
  ];
  const node = (tag, attrs = {}) => {
    const el = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
    return el;
  };
  function init(root) {
    if (root.ovAnimation) return;
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    const assets = root.dataset.assets ? new URL(root.dataset.assets.replace(/\/?$/, '/'), document.baseURI).href : defaultAssets;
    const scene = node('svg', { class: 'ov-scene', viewBox: '0 0 1254 1254', 'aria-hidden': 'true' });
    const groups = [];
    const loads = [];
    let active = 0, timer = null, hovered = null, destroyed = false;
    function select(layer, force = false) {
      if (active === layer && !force) return;
      active = layer;
      root.dataset.layer = String(layer);
      groups.forEach((g, i) => g.toggleAttribute('data-active', i === layer));
      root.dispatchEvent(new CustomEvent('ovlayer', { detail: { layer }, bubbles: true }));
    }
    function schedule() {
      clearTimeout(timer);
      if (destroyed || media.matches || hovered !== null || document.hidden) return;
      timer = setTimeout(() => { select((active + 1) % 4); schedule(); }, 2000);
    }
    function syncMotion() {
      if (root.hasAttribute('data-paused')) scene.pauseAnimations();
      else scene.unpauseAnimations();
    }
    function pause(layer) {
      if (media.matches) return;
      hovered = layer;
      root.dataset.paused = '';
      syncMotion();
      select(layer);
      schedule();
    }
    function resume() {
      hovered = null;
      root.toggleAttribute('data-paused', document.hidden);
      syncMotion();
      schedule();
    }
    // Paint from bottom to top so foreground pipes retain the original occlusion.
    for (let i = 3; i >= 0; i--) {
      const tier = tiers[i];
      const group = node('g', { class: 'ov-tier', 'data-tier': i, style: `--ov-index:${i}` });
      groups[i] = group;
      const url = new URL(`layer-${i}.webp`, assets).href;
      const preload = new Image();
      loads.push(new Promise((resolve, reject) => {
        preload.onload = resolve;
        preload.onerror = () => reject(new Error(`Cannot load overview layer: ${url}`));
        preload.src = url;
      }));
      group.append(node('path', { class: 'ov-halo', d: tier.rim }));
      group.append(node('image', { class: 'ov-art', href: url, width: 1254, height: 1254 }));
      group.append(node('path', { class: 'ov-rim', d: tier.front }));
      function spark(d, returning, circuit, delay) {
        const dot = node('g', { class: `ov-flow${returning ? ' ov-flow-return' : ''}${circuit ? ' ov-circuit' : ''}` });
        dot.append(node('circle', { class: 'ov-spark-glow', r: circuit ? 10 : 18 }));
        dot.append(node('circle', { class: 'ov-spark-core', r: circuit ? 4 : 7 }));
        dot.append(node('animateMotion', {
          path: d, dur: circuit ? '3.6s' : '2.4s', begin: `${-delay}s`,
          repeatCount: 'indefinite', calcMode: 'linear',
          keyPoints: returning ? '1;0' : '0;1', keyTimes: '0;1'
        }));
        group.append(dot);
      }
      for (const [paths, returning] of [[tier.down, false], [tier.up, true]]) {
        paths.forEach((d, index) => spark(d, returning, false, i * .55 + index * 1.2 + (returning ? .6 : 0)));
      }
      circuits[i].forEach((d, index) => spark(d, false, true, i * .65 + index * 1.2));
      const hit = node('polygon', { class: 'ov-hit', points: tier.hit });
      hit.addEventListener('pointerenter', e => { if (e.pointerType !== 'touch') pause(i); });
      hit.addEventListener('pointerleave', resume);
      group.append(hit);
      scene.append(group);
    }
    root.append(scene);
    function preference() {
      hovered = null;
      root.toggleAttribute('data-paused', media.matches || document.hidden);
      syncMotion();
      if (media.matches) select(0, true);
      schedule();
    }
    function visibility() {
      root.toggleAttribute('data-paused', document.hidden || hovered !== null || media.matches);
      syncMotion();
      schedule();
    }
    scene.addEventListener('pointerleave', resume);
    media.addEventListener('change', preference);
    document.addEventListener('visibilitychange', visibility);
    root.ovAnimation = {
      destroy() {
        destroyed = true;
        clearTimeout(timer);
        media.removeEventListener('change', preference);
        document.removeEventListener('visibilitychange', visibility);
        scene.removeEventListener('pointerleave', resume);
        scene.remove();
        delete root.dataset.ready;
        delete root.dataset.paused;
        delete root.ovAnimation;
      }
    };
    Promise.all(loads).then(() => {
      if (destroyed) return;
      root.dataset.ready = '';
      select(0, true);
      preference();
    }).catch(error => {
      console.error('[ov-anim]', error);
      root.ovAnimation?.destroy(); // Keep original PNG visible on any asset failure.
    });
  }
  window.OvAnimation = { init };
  function boot() { document.querySelectorAll('.ov-anim').forEach(init); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
