(() => {
  const root=document.getElementById('lune');
  const scroll=root.querySelector('.scroll'),stage=root.querySelector('.stage'),win=root.querySelector('.window');
  const hero=root.querySelector('.hero'),learn=root.querySelector('.learn'),pages=root.querySelector('.pages');
  const sidebar=root.querySelector('.browser-sidebar'),sidebarToggle=root.querySelector('.sidebar-toggle');
  const demoCursor=root.querySelector('.demo-cursor'),demoClick=root.querySelector('.demo-click');
  let demoStart=0,demoDistance=320,sidebarOverride=null;
  const dock=root.querySelector('.dock'),items=[...dock.querySelectorAll('.dock-item')];
  const reduce=matchMedia('(prefers-reduced-motion:reduce)'), fine=matchMedia('(hover:hover) and (pointer:fine)');
  const nativeTimeline=CSS.supports('animation-timeline:scroll()');
  const clamp=x=>Math.max(0,Math.min(1,x));
  let opening=0,readingStart=182,launchAt=96,pageHeight=0,reading=0,queued=false,base=48,launched=false,appVisible=false,showTimer=0;
  function measure() {
    const style = getComputedStyle(root);
    opening = parseFloat(style.getPropertyValue('--opening'));
    readingStart = parseFloat(style.getPropertyValue('--reading-start'));
    launchAt = parseFloat(style.getPropertyValue('--launch-at'));
    pageHeight = root.querySelector('.viewport').clientHeight;
    const sidebarWidth = parseFloat(style.getPropertyValue('--sidebar-width'));
    const compact = matchMedia('(max-width:540px)').matches;
    root.style.setProperty('--story-width', `${Math.min(840, win.clientWidth - 16 - (compact ? 0 : sidebarWidth))}px`);
    const minimal = root.querySelector('.minimal-story');
    demoStart = readingStart + minimal.offsetTop - pageHeight * .4;
    demoDistance = Math.min(340, pageHeight * .48);
    root.style.setProperty('--demo-start', `${demoStart}px`);
    root.style.setProperty('--demo-end', `${demoStart + demoDistance}px`);
    win.style.setProperty('--cursor-path', `path("M ${win.clientWidth + 28} ${pageHeight * .68} C ${win.clientWidth * .44} ${pageHeight * .88}, 18 167, 102 27")`);
    reading = Math.max(0, pages.scrollHeight - pageHeight);
    root.style.setProperty('--reading', `${reading}px`);
    root.style.setProperty('--thumb-size', `${pageHeight / pages.scrollHeight * 100}%`);
    root.style.setProperty('--thumb-travel', `${reading / pageHeight * 100}%`);
    base = parseFloat(getComputedStyle(items[0]).width);
    update();
  }
  function update(){
    queued=false;const y=scroll.scrollTop;if(y>launchAt&&pointer!==null){pointer=null;startMagnify();}if(y<=launchAt)close();else {launch();if(y>=readingStart)reveal(true);}const p=clamp(y/opening),r=reading ? clamp((y-readingStart)/reading) : 0;
    hero.inert=appVisible||y>=opening;learn.inert=appVisible||y>=opening;
    win.inert=!appVisible;win.setAttribute('aria-hidden',String(!appVisible));win.style.pointerEvents=appVisible?'auto':'none';
    root.dataset.phase=appVisible?'reading':launched?'launching':'closed';root.dataset.progress=p.toFixed(3);
    updateSidebar(y);
    pages.querySelectorAll('.story-section').forEach(section=>{const top=section.offsetTop-r*reading;const offscreen=!appVisible||top>=pageHeight-.5||top+section.offsetHeight<=.5;section.inert=offscreen;section.setAttribute('aria-hidden',String(offscreen));});
    if(!nativeTimeline){
      const fade=1-clamp((p-.18)/.82);hero.style.translate=learn.style.translate=`0 ${-Math.min(y,opening)}px`;hero.style.opacity=learn.style.opacity=fade;
      pages.style.transform=`translateY(${-r*reading}px)`;
      root.querySelector('.reading-thumb').style.translate=`0 ${r*reading/pageHeight*100}%`;
    }
  }
  scroll.addEventListener('scroll',()=>{sidebarOverride=null;delete win.dataset.sidebarOverride;if(nativeTimeline&&!reduce.matches)win.style.removeProperty('--sidebar-fold');if(!queued){queued=true;requestAnimationFrame(update);}},{passive:true});
  function updateSidebar(y) {
    const progress = clamp((y - demoStart) / demoDistance);
    const animatedFold = reduce.matches ? Number(progress >= .6) : clamp((progress - .6) / .3);
    const fold = sidebarOverride ?? animatedFold;
    if (!nativeTimeline || reduce.matches || sidebarOverride !== null) win.style.setProperty('--sidebar-fold', fold);
    const collapsed = fold >= .95;
    sidebar.inert = collapsed;
    sidebar.setAttribute('aria-hidden', String(collapsed));
    sidebarToggle.setAttribute('aria-expanded', String(!collapsed));
    sidebarToggle.setAttribute('aria-label', collapsed ? 'Expand sidebar' : 'Collapse sidebar');
    win.dataset.sidebar = collapsed ? 'collapsed' : 'expanded';
    if (!nativeTimeline) {
      demoCursor.style.offsetDistance = `${clamp(progress / .52) * 100}%`;
      demoCursor.style.opacity = Math.min(clamp(progress / .08), 1 - clamp((progress - .66) / .14));
      const press = progress <= .6 ? clamp((progress - .56) / .04) : 1 - clamp((progress - .6) / .06);
      demoCursor.style.transform = `scale(${1 - .16 * press})`;
      const click = clamp((progress - .56) / .22);
      demoClick.style.opacity = click > 0 && click < 1 ? .7 * Math.sin(Math.PI * click) : 0;
      demoClick.style.transform = `scale(${.5 + click * 1.2})`;
    }
  }
  sidebarToggle.addEventListener('click', () => {
    sidebarOverride = sidebarToggle.getAttribute('aria-expanded') === 'true' ? 1 : 0;
    win.dataset.sidebarOverride = String(sidebarOverride);
    updateSidebar(scroll.scrollTop);
  });
  function launch(){
    if(launched)return;launched=true;
    if(!reduce.matches)root.querySelector('.lune').classList.add('launching');
    // The 660ms bounce reaches its apex at 297ms; reveal just into its return.
    showTimer=setTimeout(()=>{if(!launched)return;reveal();update();},reduce.matches?0:320);
  }
  function reveal(immediate=false){
    // At the reading boundary, finish even an in-flight fade so fast scrolling never hides the first screen.
    clearTimeout(showTimer);appVisible=true;
    if(immediate)root.classList.add('app-fast');
    root.classList.add('app-open');
  }
  function close(){
    if(!launched&&!appVisible)return;clearTimeout(showTimer);launched=false;appVisible=false;
    root.classList.remove('app-open','app-fast');root.querySelector('.lune').classList.remove('launching');
  }
  root.querySelectorAll('[data-open]').forEach(el=>el.addEventListener('click',()=>{scroll.scrollTo({top:opening,behavior:reduce.matches?'instant':'smooth'});}));
  root.querySelectorAll('[data-close]').forEach(button => {
    button.addEventListener('click', () => {
      scroll.scrollTo({top: 0, behavior: reduce.matches ? 'instant' : 'smooth'});
      scroll.focus({preventScroll: true});
    });
  });
  const downloadChoices = [...root.querySelectorAll('.download-choices')];
  root.querySelectorAll('[popovertarget]').forEach(button => {
    const choices = document.getElementById(button.getAttribute('popovertarget'));
    choices.addEventListener('beforetoggle', event => {
      if (event.newState !== 'open') return;
      const rect = button.getBoundingClientRect();
      const width = Math.min(260, innerWidth - 24);
      choices.style.left = `${Math.max(12, Math.min(rect.left, innerWidth - width - 12))}px`;
      const above = rect.bottom + 170 > innerHeight;
      choices.style.top = above ? 'auto' : `${rect.bottom + 8}px`;
      choices.style.bottom = above ? `${innerHeight - rect.top + 8}px` : 'auto';
    });
  });
  // Dismiss before the animated story moves a trigger away from its chooser.
  function dismissDownloads() {
    downloadChoices.forEach(choices => {
      if (choices.matches(':popover-open')) choices.hidePopover();
    });
  }
  scroll.addEventListener('scroll', dismissDownloads, {passive: true});
  window.addEventListener('resize', dismissDownloads);
  async function detectDownloadArchitecture() {
    // MacIntel and the legacy user-agent string also occur on Apple silicon.
    // Only use explicit architecture hints; unsupported or withheld hints keep the chooser.
    const ua = navigator.userAgentData;
    if (ua?.platform !== 'macOS' || ua.mobile || !ua.getHighEntropyValues) return;
    try {
      const {architecture} = await ua.getHighEntropyValues(['architecture']);
      const build = architecture === 'arm' ? 'arm64' : architecture === 'x86' ? 'x86_64' : null;
      if (!build) return;
      const label = build === 'arm64' ? 'Apple silicon' : 'Intel';
      dismissDownloads();
      root.querySelectorAll('.action.download').forEach(button => {
        button.dataset.architecture = build;
        button.removeAttribute('popovertarget');
        button.querySelector('.download-chevron').remove();
        button.setAttribute('aria-label', `Download for ${label} — coming soon`);
        button.title = `Download for ${label} — coming soon`;
        // Enable and link the selected build only after public releases are validated.
        button.disabled = true;
      });
    } catch {
      // Privacy settings can deny high-entropy hints. Leave the explicit choices available.
    }
  }
  detectDownloadArchitecture();
  const fullscreenButton = root.querySelector('[data-fullscreen]');
  fullscreenButton.disabled = !document.fullscreenEnabled;
  fullscreenButton.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      fullscreenButton.disabled = true;
      fullscreenButton.setAttribute('aria-label', 'Full screen unavailable');
    }
  });
  document.addEventListener('fullscreenchange', () => {
    const active = Boolean(document.fullscreenElement);
    fullscreenButton.setAttribute('aria-pressed', String(active));
    fullscreenButton.setAttribute('aria-label', active ? 'Exit full screen' : 'Enter full screen');
  });
  // A continuous falloff enlarges adjacent icons as in Dock magnification.
  // CSS owns the visual transitions; JavaScript coordinates launch timing and scroll state.
  let pointer=null,hoverFrame=0;const widths=items.map(()=>48);
  function magnify(){
    const centers=items.map(el=>{const rect=el.getBoundingClientRect();return rect.left+rect.width/2;});
    let moving=false;
    items.forEach((el,i)=>{
      const virtualCenter=centers[i];
      const d=pointer===null?1:Math.min(1,Math.abs(pointer-virtualCenter)/(base*1.6));
      const desired=base*(1+.4*(.5+.5*Math.cos(Math.PI*d)));
      widths[i]+=(desired-widths[i])*.24;
      if(Math.abs(desired-widths[i])>.08)moving=true;else widths[i]=desired;
      el.style.width=`${widths[i]}px`;el.style.setProperty('--rendered-icon',`${widths[i]}px`);
    });
    hoverFrame=moving?requestAnimationFrame(magnify):0;
  }
  function startMagnify(){if(!hoverFrame)hoverFrame=requestAnimationFrame(magnify);}
  dock.addEventListener('pointermove',e=>{if(!fine.matches||reduce.matches)return;pointer=e.clientX;startMagnify();});
  dock.addEventListener('pointerleave',()=>{pointer=null;startMagnify();});
  new ResizeObserver(()=>{if(pointer===null){items.forEach(el=>{el.style.width='';el.style.height='';el.style.removeProperty('--rendered-icon');});measure();widths.fill(base);}}).observe(stage);
  reduce.addEventListener('change',()=>{if(nativeTimeline&&!reduce.matches&&sidebarOverride===null)win.style.removeProperty('--sidebar-fold');pointer=null;items.forEach(el=>{el.style.width='';el.style.height='';el.style.removeProperty('--rendered-icon');});measure();widths.fill(base);});
  let measuredContentHeight = 0;
  new ResizeObserver(entries => {
    const height = entries[0].contentRect.height;
    if (Math.abs(height - measuredContentHeight) > .5) {
      measuredContentHeight = height;
      measure();
    }
  }).observe(pages);
  measure();widths.fill(base);
})();
