(() => {
  const root=document.getElementById('lune');
  const scroll=root.querySelector('.scroll'),stage=root.querySelector('.stage'),win=root.querySelector('.window');
  const hero=root.querySelector('.hero'),learn=root.querySelector('.learn'),pages=root.querySelector('.pages');
  const windowControls=root.querySelector('.window-controls');
  const sidebar=root.querySelector('.browser-sidebar'),sidebarToggle=root.querySelector('.sidebar-toggle');
  const demoCursor=root.querySelector('.demo-cursor'),demoClick=root.querySelector('.demo-click');
  const sidebarRegion=root.querySelector('.sidebar-region'),sidebarRail=root.querySelector('.sidebar-rail');
  const toolbarRegion=root.querySelector('.toolbar-region'),toolbarRail=root.querySelector('.toolbar-rail'),toolbar=root.querySelector('.browser-toolbar');
  let panelPointer=null,cursorPath=null,cursorPathLength=0,browserScale=1;
  const panelDismissDistance=48;
  let demoStart=0,demoDistance=460,cursorStop=50,sidebarOverride=null,sidebarHovered=false;
  const dock=root.querySelector('.dock'),items=[...dock.querySelectorAll('.dock-item')];
  const reduce=matchMedia('(prefers-reduced-motion:reduce)'), fine=matchMedia('(hover:hover) and (pointer:fine)');
  const nativeTimeline=CSS.supports('animation-timeline:scroll()');
  const clamp=x=>Math.max(0,Math.min(1,x));
  let opening=0,readingStart=182,launchAt=96,pageHeight=0,reading=0,queued=false,base=48,launched=false,appVisible=false,showTimer=0;
  const points = [...pages.querySelectorAll('.flow-point')];
  const vine = pages.querySelector('.story-vine'), vineGrowth = vine.querySelector('.vine-growth');
  const sprigs = vine.querySelector('.vine-sprigs'), flowerBloom = pages.querySelector('.flower-bloom');
  let vineStart=0, vineEnd=1, flowerEnd=1;
  const leafRanges=[];
  points.forEach((point, index) => {
    point.style.setProperty('--flow-offset', Math.sin(index / (points.length - 1) * 2 * Math.PI).toFixed(5));
    point.style.setProperty('--leaf-angle', `${index === 0 ? 0 : index % 2 ? 7 : -5}deg`);
  });
  function measure() {
    const style = getComputedStyle(root);
    opening = parseFloat(style.getPropertyValue('--opening'));
    readingStart = parseFloat(style.getPropertyValue('--reading-start'));
    launchAt = parseFloat(style.getPropertyValue('--launch-at'));
    pageHeight = root.querySelector('.viewport').clientHeight;
    const sidebarWidth = parseFloat(style.getPropertyValue('--sidebar-width'));
    browserScale = parseFloat(style.getPropertyValue('--browser-scale'));
    root.style.setProperty('--hairline', `${1 / (devicePixelRatio * browserScale)}px`);
    root.style.setProperty('--story-width', `${Math.min(840, win.clientWidth - 2 * parseFloat(style.getPropertyValue('--rail')) - sidebarWidth)}px`);
    measureBotany();
    const minimal = root.querySelector('.minimal-story');
    demoStart = readingStart + minimal.offsetTop - pageHeight * .7;
    demoDistance = Math.min(460, pageHeight * .65);
    root.style.setProperty('--demo-start', `${demoStart}px`);
    root.style.setProperty('--demo-end', `${demoStart + demoDistance}px`);
    // Keep the path in window coordinates, but render the cursor on the desktop
    // so it can cross the actual screen edges without the window clipping it.
    const originX = win.offsetLeft - win.offsetWidth * browserScale / 2;
    const originY = win.offsetTop;
    const toggleX = (sidebarWidth - 22) * browserScale;
    const toggleY = 26 * browserScale;
    demoCursor.style.setProperty('--cursor-origin-x', `${originX}px`);
    demoCursor.style.setProperty('--cursor-origin-y', `${originY}px`);
    const incoming = `M ${-originX - 28} ${pageHeight * .38 * browserScale} C ${toggleX * .7} ${pageHeight * .38 * browserScale}, ${toggleX + 48 * browserScale} ${100 * browserScale}, ${toggleX} ${toggleY}`;
    const outgoing = ` C ${toggleX - 32} -24, ${toggleX + 96} ${-originY + 12}, ${toggleX + 140} ${-originY - 36}`;
    // Pause precisely at the toggle, regardless of viewport or curve length.
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', incoming);
    const incomingLength = path.getTotalLength();
    path.setAttribute('d', incoming + outgoing);
    cursorPath = path;
    cursorPathLength = path.getTotalLength();
    cursorStop = incomingLength / cursorPathLength * 100;
    demoCursor.style.setProperty('--cursor-stop', `${cursorStop}%`);
    demoCursor.style.setProperty('--cursor-path', `path("${incoming + outgoing}")`);
    reading = Math.max(0, pages.scrollHeight - pageHeight);
    root.style.setProperty('--reading', `${reading}px`);
    root.style.setProperty('--thumb-size', `${pageHeight / pages.scrollHeight * 100}%`);
    root.style.setProperty('--thumb-travel', `${reading / pageHeight * 100}%`);
    base = parseFloat(getComputedStyle(items[0]).width);
    update();
  }
  function measureBotany() {
    // Use resting layout coordinates: each petiole is the leaf's rotation pivot.
    // Text is centered beside the body of the specimen, above its petiole.
    const nodes = points.map((point,index) => ({x:point.offsetLeft + (index ? 64 : 40),y:point.offsetTop + (point.clientHeight - 100) / 2 + 86}));
    const first=nodes[0],last=nodes[nodes.length-1],height=last.y+92;
    vine.setAttribute('viewBox', `0 0 ${pages.clientWidth} ${height}`);
    vine.style.height=`${height}px`;
    let d=`M ${first.x} ${first.y}`;
    const growth=document.createDocumentFragment();
    function svg(tag,attrs) {
      const element=document.createElementNS('http://www.w3.org/2000/svg',tag);
      Object.entries(attrs).forEach(([key,value])=>element.setAttribute(key,value));
      return element;
    }
    nodes.slice(1).forEach((node,index) => {
      const previous=nodes[index],dy=node.y-previous.y;
      const curve=`C ${previous.x-36-index%3*5} ${previous.y+dy*.32}, ${node.x+28} ${node.y-dy*.38}, ${node.x} ${node.y}`;
      d+=` ${curve}`;
      const segment=svg('path',{d:`M ${previous.x} ${previous.y} ${curve}`});
      const length=segment.getTotalLength();
      // Alternating shoots and curled tendrils give this a pressed-plant silhouette.
      [.28,.64].forEach((progress,j)=>{
        const at=segment.getPointAtLength(length*progress),side=(index+j)%2?1:-1;
        const end={x:at.x+side*(26+j*6),y:at.y-20-j*5};
        growth.append(svg('path',{class:'vine-tendril',d:`M ${at.x} ${at.y} Q ${at.x+side*14} ${at.y-4}, ${end.x} ${end.y}`}));
        growth.append(svg('use',{href:'#cyanotype-lance',x:-14,y:-48,width:28,height:48,transform:`translate(${end.x} ${end.y}) rotate(${side*(38+index%3*8)}) scale(${.72+j*.13})`,opacity:.7+j*.12}));
        growth.append(svg('use',{href:'#cyanotype-lance',x:-14,y:-48,width:28,height:48,transform:`translate(${at.x+side*12} ${at.y-7}) rotate(${-side*32}) scale(.48)`,opacity:.6}));
      });
      if(index%2===0) {
        const at=segment.getPointAtLength(length*.83);
        growth.append(svg('path',{class:'vine-tendril',d:`M ${at.x} ${at.y} C ${at.x-20} ${at.y-12}, ${at.x-46} ${at.y+14}, ${at.x-32} ${at.y+25} C ${at.x-19} ${at.y+34}, ${at.x-16} ${at.y+13}, ${at.x-28} ${at.y+17}`}));
      }
    });
    d+=` C ${last.x-15} ${last.y+32}, ${last.x+12} ${last.y+64}, ${last.x-8} ${last.y+80}`;
    vine.querySelectorAll(':scope > path').forEach(path=>path.setAttribute('d',d));
    sprigs.replaceChildren(growth);
    vineStart=Math.max(0,readingStart+first.y-pageHeight*.8);
    vineEnd=readingStart+last.y-pageHeight*.15;
    flowerEnd=readingStart+first.y+pageHeight*.2;
    root.style.setProperty('--vine-start',`${vineStart}px`);
    root.style.setProperty('--vine-end',`${vineEnd}px`);
    root.style.setProperty('--flower-end',`${flowerEnd}px`);
    points.forEach((point,index)=>{
      const start=Math.max(0,readingStart+nodes[index].y-pageHeight),end=readingStart+nodes[index].y+pageHeight*.25;
      leafRanges[index]={start,end};
      point.style.setProperty('--leaf-start',`${start}px`);
      point.style.setProperty('--leaf-end',`${end}px`);
    });
  }
  function updateBotany(y) {
    if (nativeTimeline || reduce.matches) return;
    vineGrowth.style.strokeDasharray='1';
    vineGrowth.style.strokeDashoffset=1-clamp((y-vineStart)/(vineEnd-vineStart));
    points.forEach((point,index)=>{
      const {start,end}=leafRanges[index],t=clamp((y-start)/(end-start));
      const angle=(index===0?0:index%2?7:-5)+Math.sin(t*Math.PI*2-Math.PI/2)*3;
      point.querySelector('.botanical-bullet').style.transform=`rotate(${angle}deg)`;
    });
    const bloom=clamp((y-vineStart)/(flowerEnd-vineStart));
    flowerBloom.style.transform=`rotate(${-3+6*bloom}deg) scale(${.96+.04*bloom})`;
  }
  function update(){
    queued=false;const y=scroll.scrollTop;if(y>launchAt&&pointer!==null){pointer=null;startMagnify();}if(y<=launchAt)close();else {launch();if(y>=readingStart)reveal(true);}const p=clamp(y/opening),r=reading ? clamp((y-readingStart)/reading) : 0;
    hero.inert=appVisible||y>=opening;learn.inert=appVisible||y>=opening;
    win.inert=!appVisible;win.setAttribute('aria-hidden',String(!appVisible));win.style.pointerEvents=appVisible?'auto':'none';
    root.dataset.phase=appVisible?'reading':launched?'launching':'closed';root.dataset.progress=p.toFixed(3);
    updateSidebar(y);
    updateBotany(y);
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
    const animatedFold = Number(progress >= .5);
    const fold = sidebarOverride ?? animatedFold;
    if (!nativeTimeline || reduce.matches || sidebarOverride !== null) win.style.setProperty('--sidebar-fold', fold);
    const floating = sidebarOverride !== null ? Boolean(sidebarOverride) : progress >= .5;
    const cursorDistance = progress <= .44 ? clamp(progress / .44) * cursorStop : cursorStop + clamp((progress - .64) / .36) * (100 - cursorStop);
    const cursorPoint = cursorPath.getPointAtLength(cursorDistance / 100 * cursorPathLength);
    const demoHolding = sidebarOverride === null && (progress < .5 || distanceFromPanel({x:cursorPoint.x / browserScale,y:cursorPoint.y / browserScale},
      {left:0,right:sidebar.offsetWidth,top:0,bottom:win.clientHeight}) <= panelDismissDistance);
    const keyboardFocus = Boolean(sidebarRegion.querySelector(':focus-visible'));
    const visible = !floating || demoHolding || sidebarHovered || keyboardFocus;
    sidebar.inert = !visible;
    sidebar.setAttribute('aria-hidden', String(!visible));
    sidebarRail.setAttribute('aria-expanded', String(visible));
    sidebarToggle.setAttribute('aria-pressed', String(!floating));
    sidebarToggle.setAttribute('aria-label', floating ? 'Pin sidebar' : 'Unpin sidebar');
    win.dataset.sidebar = !floating ? 'pinned' : visible ? 'floating' : 'hidden';
    updateWindowControls('sidebar');
    if (!nativeTimeline) {
      demoCursor.style.offsetDistance = `${cursorDistance}%`;
      demoCursor.style.opacity = Math.min(clamp(progress / .06), 1 - clamp((progress - .94) / .06));
      const press = progress <= .5 ? clamp((progress - .46) / .04) : 1 - clamp((progress - .5) / .06);
      demoCursor.style.transform = `scale(${1 - .16 * press})`;
      const click = clamp((progress - .46) / .18);
      demoClick.style.opacity = progress <= .5 ? .7 * clamp((progress - .46) / .04) : .7 * (1 - clamp((progress - .5) / .14));
      demoClick.style.transform = `scale(${.5 + click * 1.2})`;
    }
  }
  sidebarToggle.addEventListener('click', () => {
    sidebarOverride = sidebarToggle.getAttribute('aria-pressed') === 'true' ? 1 : 0;
    win.dataset.sidebarOverride = String(sidebarOverride);
    updateSidebar(scroll.scrollTop);
  });
  sidebarRegion.addEventListener('pointerenter', event => {
    if (event.pointerType === 'touch') return;
    sidebarHovered = true;
    updateSidebar(scroll.scrollTop);
  });
  sidebarRegion.addEventListener('pointerleave', trackPanelPointer);
  sidebarRail.addEventListener('click', () => {
    sidebarHovered = true;
    updateSidebar(scroll.scrollTop);
  });
  sidebarRegion.addEventListener('focusin', () => updateSidebar(scroll.scrollTop));
  sidebarRegion.addEventListener('focusout', () => queueMicrotask(() => { dismissDistantPanels();updateSidebar(scroll.scrollTop); }));
  sidebarRegion.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    sidebarHovered = false;
    scroll.focus({preventScroll:true});
    updateSidebar(scroll.scrollTop);
  });
  win.addEventListener('pointerdown', event => {
    if (sidebarRegion.contains(event.target) || windowControls.contains(event.target)) return;
    if (event.pointerType === 'touch') sidebarHovered = false;
    if (sidebarRegion.contains(document.activeElement)) scroll.focus({preventScroll:true});
    updateSidebar(scroll.scrollTop);
  });
  function updateWindowControls(motion) {
    const visible = win.dataset.sidebar !== 'hidden' || toolbarRegion.hasAttribute('data-open');
    const wasVisible = win.hasAttribute('data-controls-visible');
    if (visible !== wasVisible) {
      // A fully hidden group starts from the edge of the panel revealing it.
      const reset = visible && win.dataset.controlsMotion !== motion &&
        getComputedStyle(windowControls).visibility === 'hidden';
      if (reset) windowControls.style.transition = 'none';
      win.dataset.controlsMotion = motion;
      if (reset) {
        windowControls.getBoundingClientRect();
        windowControls.style.removeProperty('transition');
      }
    }
    win.toggleAttribute('data-controls-visible', visible);
    windowControls.inert = !visible;
    windowControls.setAttribute('aria-hidden', String(!visible));
  }
  function revealFromWindowControls() {
    sidebarHovered = true;
    updateSidebar(scroll.scrollTop);
    showToolbar();
  }
  windowControls.addEventListener('pointerenter', revealFromWindowControls);
  windowControls.addEventListener('focusin', revealFromWindowControls);
  windowControls.addEventListener('focusout', () => queueMicrotask(dismissDistantPanels));
  function showToolbar() {
    if (!appVisible) return;
    toolbarRegion.dataset.open = '';
    win.dataset.toolbarOpen = '';
    toolbar.inert = false;
    toolbar.setAttribute('aria-hidden', 'false');
    toolbarRail.setAttribute('aria-expanded', 'true');
    updateWindowControls('toolbar');
  }
  function hideToolbar() {
    delete toolbarRegion.dataset.open;
    delete win.dataset.toolbarOpen;
    toolbar.inert = true;
    toolbar.setAttribute('aria-hidden', 'true');
    toolbarRail.setAttribute('aria-expanded', 'false');
    updateWindowControls('toolbar');
  }
  function distanceFromPanel(point, rect) {
    const dx = Math.max(rect.left - point.x, 0, point.x - rect.right);
    const dy = Math.max(rect.top - point.y, 0, point.y - rect.bottom);
    return Math.hypot(dx, dy);
  }
  function dismissDistantPanels() {
    if (!panelPointer) return;
    const sidebarArea = sidebarRegion.getBoundingClientRect();
    const sidebarBounds = {left:sidebarArea.left + sidebar.offsetLeft * browserScale,right:sidebarArea.left + (sidebar.offsetLeft + sidebar.offsetWidth) * browserScale,
      top:sidebarArea.top + sidebar.offsetTop * browserScale,bottom:sidebarArea.top + (sidebar.offsetTop + sidebar.offsetHeight) * browserScale};
    if (sidebarHovered && !sidebarRegion.querySelector(':focus-visible') &&
        distanceFromPanel(panelPointer, sidebarBounds) > panelDismissDistance) {
      sidebarHovered = false;
      updateSidebar(scroll.scrollTop);
    }
    // Like the native header, retain the whole top strip across capsule gaps
    // and the sidebar header, down to 48px below the glass.
    const frame = win.getBoundingClientRect();
    // Measure resting bounds, independently of the sidebar slide.
    // Treat its capsules and the gaps between them as one floating top bar.
    const area = toolbarRegion.getBoundingClientRect();
    const rect = {left:frame.left,right:frame.right,top:area.top,bottom:area.top + 44 * browserScale};
    const controlsRect = windowControls.getBoundingClientRect();
    if (toolbarRegion.hasAttribute('data-open') && !toolbarRegion.contains(document.activeElement) &&
        !windowControls.contains(document.activeElement) &&
        Math.min(distanceFromPanel(panelPointer, rect), distanceFromPanel(panelPointer, controlsRect)) > panelDismissDistance) hideToolbar();
  }
  function trackPanelPointer(event) {
    if (event.pointerType === 'touch') return;
    panelPointer = {x:event.clientX,y:event.clientY};
    const bounds = sidebar.getBoundingClientRect();
    if (win.dataset.sidebar !== 'hidden' && panelPointer.x >= bounds.left && panelPointer.x <= bounds.right &&
        panelPointer.y >= bounds.top && panelPointer.y <= bounds.top + 52 * browserScale) showToolbar();
    dismissDistantPanels();
  }
  document.addEventListener('pointermove', trackPanelPointer, {passive:true});
  document.documentElement.addEventListener('pointerleave', () => {
    panelPointer = null;
    sidebarHovered = false;
    updateSidebar(scroll.scrollTop);
    hideToolbar();
  });
  toolbarRegion.addEventListener('pointerenter', event => {
    if (event.pointerType === 'touch') return;
    panelPointer = {x:event.clientX,y:event.clientY};
    showToolbar();
  });
  toolbarRegion.addEventListener('pointerleave', trackPanelPointer);
  toolbarRail.addEventListener('click', showToolbar);
  const headerShield = root.querySelector('.header-shield');
  headerShield.addEventListener('pointerenter', showToolbar);
  toolbarRegion.addEventListener('focusin', showToolbar);
  toolbarRegion.addEventListener('focusout', () => queueMicrotask(dismissDistantPanels));
  toolbarRegion.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    scroll.focus({preventScroll:true});
    hideToolbar();
  });
  win.addEventListener('pointerdown', event => {
    if (toolbarRegion.contains(event.target) || windowControls.contains(event.target)) return;
    if (toolbarRegion.contains(document.activeElement)) scroll.focus({preventScroll:true});
    if (event.pointerType === 'touch') hideToolbar();
    else trackPanelPointer(event);
  });
  window.addEventListener('blur', () => { panelPointer=null;sidebarHovered=false;updateSidebar(scroll.scrollTop);hideToolbar(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) hideToolbar(); });
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
    if(!launched&&!appVisible)return;sidebarHovered=false;panelPointer=null;hideToolbar();clearTimeout(showTimer);launched=false;appVisible=false;
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
        button.setAttribute('aria-label', `Download for ${label}`);
        button.title = `Download for ${label}`;
        const url = `https://github.com/leebyron/lune-browser/releases/latest/download/Lune-macos-${build}.dmg`;
        button.addEventListener('click', () => { window.location.assign(url); });
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
  reduce.addEventListener('change',()=>{vineGrowth.style.removeProperty('stroke-dasharray');vineGrowth.style.removeProperty('stroke-dashoffset');flowerBloom.style.removeProperty('transform');points.forEach(point=>point.querySelector('.botanical-bullet').style.removeProperty('transform'));if(nativeTimeline&&!reduce.matches&&sidebarOverride===null)win.style.removeProperty('--sidebar-fold');pointer=null;items.forEach(el=>{el.style.width='';el.style.height='';el.style.removeProperty('--rendered-icon');});measure();widths.fill(base);});
  let measuredContentHeight = 0, measuredContentWidth = 0;
  new ResizeObserver(entries => {
    const {height,width} = entries[0].contentRect;
    if (Math.abs(height - measuredContentHeight) > .5 || Math.abs(width - measuredContentWidth) > .5) {
      measuredContentHeight = height;
      measuredContentWidth = width;
      measure();
    }
  }).observe(pages);
  measure();widths.fill(base);
  document.fonts.ready.then(measure);
})();
