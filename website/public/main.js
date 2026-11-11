(() => {
  const root=document.getElementById('lune');
  const scroll=root.querySelector('.scroll'),stage=root.querySelector('.stage'),win=root.querySelector('.window');
  const hero=root.querySelector('.hero'),learn=root.querySelector('.learn'),pages=root.querySelector('.pages');
  const windowControls=root.querySelector('.window-controls');
  const sidebar=root.querySelector('.browser-sidebar'),sidebarToggle=root.querySelector('.sidebar-toggle');
  const currentTab=sidebar.querySelector('.browser-tab.selected');
  const demoCursor=root.querySelector('.demo-cursor'),demoClick=root.querySelector('.demo-click');
  const sidebarRegion=root.querySelector('.sidebar-region'),sidebarRail=root.querySelector('.sidebar-rail');
  const toolbarRegion=root.querySelector('.toolbar-region'),toolbarRail=root.querySelector('.toolbar-rail'),toolbar=root.querySelector('.browser-toolbar');
  const commandDemo=root.querySelector('.command-demo'),commandQuery=commandDemo.querySelector('.command-demo-query'),commandScope=commandDemo.querySelector('.command-demo-scope');
  const commandHint=commandDemo.querySelector('.command-demo-hint'),commandPlaceholder=commandDemo.querySelector('.command-demo-placeholder');
  let commandStart=0,bangStart=0,commandComplete=0,commandDismiss=0,commandEnd=0,bangStartedAt=null,commandFrame=0;
  let panelPointer=null,cursorPath=null,cursorPathLength=0,browserScale=1;
  const panelDismissDistance=48;
  let demoStart=0,demoDistance=460,toolbarStop=25,cursorStop=65,sidebarOverride=null,sidebarHovered=false,demoToolbarActive=false;
  const dock=root.querySelector('.dock'),items=[...dock.querySelectorAll('.dock-item')];
  const reduce=matchMedia('(prefers-reduced-motion:reduce)'), fine=matchMedia('(hover:hover) and (pointer:fine)');
  const nativeTimeline=CSS.supports('animation-timeline:scroll()');
  const clamp=x=>Math.max(0,Math.min(1,x));
  let opening=0,readingStart=180,launchAt=96,pageHeight=0,reading=0,queued=false,base=48,launched=false,appVisible=false,showTimer=0;
  function svg(tag,attrs={}) {
    const element=document.createElementNS('http://www.w3.org/2000/svg',tag);
    Object.entries(attrs).forEach(([key,value])=>element.setAttribute(key,value));
    return element;
  }
  function random(seed) {
    let state=seed>>>0;
    return ()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return (state>>>0)/4294967296;};
  }
  // One-dimensional gradient noise with Perlin's quintic interpolation.
  // Four spatial octaves provide terrain detail without a repeating wave.
  function noise(x,seed=71) {
    const lattice=Math.floor(x),t=x-lattice,fade=t*t*t*(t*(t*6-15)+10);
    const gradient=i=>{let h=Math.imul(i^seed,0x45d9f3b);h=Math.imul(h^(h>>>16),0x45d9f3b);h^=h>>>16;return (h&1?1:-1)*(.5+((h>>>1)&1023)/1023);};
    const a=gradient(lattice)*t,b=gradient(lattice+1)*(t-1);
    return (a+(b-a)*fade)*2;
  }
  function smoothPath(points,closed=false) {
    let d=`M ${points[0].x} ${points[0].y}`;
    for(let i=0;i<points.length-1;i++) {
      const a=points[Math.max(0,i-1)],b=points[i],c=points[i+1],e=points[Math.min(points.length-1,i+2)];
      d+=` C ${b.x+(c.x-a.x)/6} ${b.y+(c.y-a.y)/6}, ${c.x-(e.x-b.x)/6} ${c.y-(e.y-b.y)/6}, ${c.x} ${c.y}`;
    }
    return d+(closed?' Z':'');
  }
  function leaf(seed,main=false) {
    const rng=random(seed),length=main?64+rng()*16:32+rng()*14;
    const width=main?10+rng()*5:5+rng()*3,lean=main?-16-rng()*12:(rng()-.5)*5;
    const stem=main?11+rng()*4:7+rng()*3,stemX=main?-3-rng()*2:0,bend=(rng()-.5)*(main?5:3);
    const spine=t=>({x:stemX+lean*t+bend*Math.sin(Math.PI*t),y:-stem-length*t});
    const bias=.88+rng()*.18;
    const edge=(t,side)=>{
      const center=spine(t),profile=Math.pow(Math.sin(Math.PI*t),1.2)*(.8+.2*t);
      const wave=1+noise(t*3+seed*.01,seed)*.035;
      return {x:center.x+side*width*profile*wave*(side<0?1:bias),y:center.y};
    };
    const outline=[];
    for(let i=1;i<=16;i++)outline.push(edge(i/16,-1));
    for(let i=15;i>=1;i--)outline.push(edge(i/16,1));
    // The petiole is part of the filled silhouette, so there is no separate seam.
    const stemHalf=main?.8:.9,first=outline[0];
    let body=`M ${-stemHalf} 0 Q ${stemX-stemHalf} ${-stem*.6}, ${stemX-stemHalf} ${-stem} L ${first.x} ${first.y}`;
    body+=smoothPath(outline).replace(/^M [^C]+/, '');
    body+=` L ${stemX+stemHalf} ${-stem} Q ${stemX+stemHalf} ${-stem*.6}, ${stemHalf} 0 Z`;
    const specimen=svg('g',{'data-specimen-seed':seed}),ink=svg('g',{filter:'url(#cyanotype-grain)'});
    ink.append(svg('path',{d:body,fill:'var(--botanical-ink)',opacity:.75}));
    ink.append(svg('path',{d:smoothPath(outline,true),fill:'url(#leaf-ink)',opacity:.9+rng()*.1}));
    const mid=[];for(let i=0;i<=8;i++)mid.push(spine(i/8));
    let veins=smoothPath(mid);
    const count=main?5+Math.floor(rng()*3):3+Math.floor(rng()*2);
    for(let i=1;i<count;i++) {
      const t=i/(count+1),from=spine(t);
      for(const side of [-1,1]) {
        const to=edge(Math.min(.96,t+.12+rng()*.05),side);
        veins+=` M ${from.x} ${from.y} Q ${from.x+(to.x-from.x)*.65} ${from.y-2}, ${to.x} ${to.y}`;
      }
    }
    ink.append(svg('path',{d:veins,fill:'none',stroke:'var(--botanical-vein)','stroke-width':main?.65:.6,opacity:.62}));
    specimen.append(ink);
    return specimen;
  }
  function introEase(x) {
    // Match setup's cubic-bezier(.2,.8,.2,1) in the no-timeline fallback.
    let low=0,high=1,t=x;
    for(let i=0;i<12;i++){t=(low+high)/2;const bx=3*(1-t)*(1-t)*t*.2+3*(1-t)*t*t*.2+t*t*t;if(bx<x)low=t;else high=t;}
    return 3*(1-t)*(1-t)*t*.8+3*(1-t)*t*t+t*t*t;
  }
  const points = [...pages.querySelectorAll('.flow-point')];
  const introLogo=pages.querySelector('.setup-logo'),introCircles=[...introLogo.querySelectorAll('circle')];
  const vine = pages.querySelector('.story-vine'), vineGrowth = vine.querySelector('.vine-growth');
  const sprigs = vine.querySelector('.vine-sprigs'), flowerBloom = pages.querySelector('.flower-bloom');
  const soil=vine.querySelector('.vine-soil'),roots=vine.querySelector('.vine-roots');
  const petals=[...flowerBloom.querySelectorAll('.petal')], stamens=flowerBloom.querySelector('.flower-stamens');
  // A seeded fan of fine filaments gives the upward-facing flower depth.
  const stamenRng=random(887),filaments=svg('path',{fill:'none',stroke:'var(--pollen-stalk)','stroke-width':.55,'stroke-linecap':'round'});
  const halos=svg('g',{fill:'var(--pollen)',filter:'url(#stamen-light)',opacity:.55}),anthers=svg('g',{fill:'var(--pollen)'});
  let filamentPath='';
  for(let i=0;i<19;i++) {
    const fan=(i/18-.5)*2,x=fan*21+(stamenRng()-.5)*4,y=-27-stamenRng()*15-Math.cos(fan*Math.PI/2)*3;
    const baseX=(stamenRng()-.5)*7,rx=1+stamenRng()*.65,ry=.55+stamenRng()*.4;
    filamentPath+=`M ${baseX} -2 Q ${x*.45+(stamenRng()-.5)*5} ${y*.52}, ${x} ${y}`;
    halos.append(svg('ellipse',{cx:x,cy:y,rx:rx*1.8,ry:ry*1.9}));
    anthers.append(svg('ellipse',{cx:x,cy:y,rx,ry,opacity:.65+stamenRng()*.35,transform:`rotate(${fan*25} ${x} ${y})`}));
  }
  filaments.setAttribute('d',filamentPath);stamens.replaceChildren(filaments,halos,anthers);
  // Persistent seeded motes keep their idle phase when layout is measured again.
  const moteRng=random(2147),moteLayer=vine.querySelector('.vine-motes');
  const motes=Array.from({length:17},(_,index)=>{
    const group=svg('g',{class:'mote-position',opacity:0}),floating=svg('g',{class:'mote-float'});
    const duration=26+moteRng()*16,radius=.95+moteRng()*.65;
    floating.style.setProperty('--mote-duration',`${duration}s`);
    const phase=-moteRng()*duration;
    floating.style.setProperty('--mote-phase',`${phase}s`);
    const inkOpacity=.7+moteRng()*.3;
    function dot(parent,size,opacity) {
      parent.append(svg('circle',{r:size*2.3,fill:'var(--pollen)',filter:'url(#stamen-light)',opacity:.55}),svg('circle',{r:size,fill:'var(--pollen)',opacity}));
    }
    dot(floating,radius,inkOpacity);
    group.append(floating);
    // Each companion floats independently around a slightly offset origin.
    // Keep the seeded sequence intact so the existing motes stay in place.
    if(index===3||index===10) {
      const origin=svg('g',{class:'mote-companion',transform:`translate(${index===3?20:-18} ${index===3?-12:14})`}),companion=svg('g',{class:'mote-float'});
      companion.style.setProperty('--mote-duration',`${duration*(index===3?1.08:.94)}s`);
      companion.style.setProperty('--mote-phase',`${phase-duration*.09}s`);
      companion.style.setProperty('--mote-path',"path('M0 0 C12 -16 24 -16 24 0 C24 16 12 16 0 0 C-12 -16 -24 -16 -24 0 C-24 16 -12 16 0 0')");
      dot(companion,radius*.85,inkOpacity);
      origin.append(companion);group.append(origin);
    }
    if(index>=14)group.classList.add('mote-at-base');
    moteLayer.append(group);
    return {group,fraction:index<14?.025+(index+.2+moteRng()*.5)/14*.9:0,crownDistance:index<14?0:48+(index-14)*24,side:index%2?1:-1,gap:14+moteRng()*18,reach:65+moteRng()*55,x:0,y:0};
  });
  let vineStart=0, vineEnd=1, flowerStart=0, flowerEnd=1,introStart=0,introEnd=1;
  let rootWave=null,sprigRanges=[],textRanges=[];
  const leafRanges=[];
  points.forEach((point, index) => {
    point.style.setProperty('--flow-offset', Math.sin(index / (points.length - 1) * 2 * Math.PI).toFixed(5));
    const right=index>0 && index%2===0;
    point.dataset.leafSide=index===0?'flower':right?'right':'left';
    if(index>0) {
      const specimen=point.querySelector('.generated-specimen');
      if(right)specimen.setAttribute('transform','translate(80 0) scale(-1 1)');
      const generated=leaf(419+index*103,true);generated.setAttribute('transform','translate(64 86)');specimen.append(generated);
    }
    const bullet=point.querySelector('.botanical-bullet'),sway=svg('g',{class:'botanical-sway'});
    sway.append(...bullet.childNodes);bullet.append(sway);
    point.pivotX=index===0?40:right?16:64;
    // Reserve the same optical clearance from each painted specimen, rather
    // than treating its transparent 80px SVG box as the edge of the branch.
    const ink=sway.getBBox();
    // The flower is still opening at its reading position, so its full bloom
    // envelope would reserve too much empty space beside this first sentence.
    point.style.setProperty('--copy-gap',`${index===0?40:Math.max(4,ink.x+ink.width+44-80)}px`);
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
    introStart=readingStart;
    introEnd=readingStart+pageHeight*.22;
    root.style.setProperty('--intro-start',`${introStart}px`);
    root.style.setProperty('--intro-end',`${introEnd}px`);
    textRanges=[...pages.querySelectorAll('.prelude-note p')].map(text=>({text,start:introStart+(introEnd-introStart)*.75}));
    const coda=pages.querySelector('.coda'),codaContent=coda.querySelector('.coda-content'),thanks=coda.querySelector('.upstream-thanks'),byline=coda.querySelector('.byline');
    const actionsBottom=pageHeight/2+codaContent.offsetHeight/2;
    coda.style.setProperty('--thanks-top',`${(actionsBottom+byline.offsetTop)/2-thanks.offsetHeight/2}px`);
    measureBotany();
    const toolbarStory=root.querySelector('.toolbar-story'),minimal=root.querySelector('.minimal-story');
    const textCenter=section=>section.offsetTop+section.querySelector('.flow-point').offsetHeight/2-10;
    // The two holds meet their own sentence at the same reading height.
    demoDistance=Math.max(1,(textCenter(minimal)-textCenter(toolbarStory))/.38);
    demoStart=readingStart+textCenter(toolbarStory)-pageHeight*.58-demoDistance*.30;
    commandStart=readingStart+textCenter(root.querySelector('.command-menu'))-pageHeight*.70;
    bangStart=readingStart+textCenter(root.querySelector('.bangs'))-pageHeight*.70;
    commandComplete=bangStart+pageHeight*.14;
    commandDismiss=Math.max(commandComplete+pageHeight*.20,demoStart+pageHeight*.08);
    commandEnd=commandDismiss+pageHeight*.04;
    root.style.setProperty('--command-start',`${commandStart}px`);
    root.style.setProperty('--command-complete',`${commandComplete}px`);
    root.style.setProperty('--command-dismiss',`${commandDismiss}px`);
    root.style.setProperty('--demo-start', `${demoStart}px`);
    root.style.setProperty('--demo-end', `${demoStart + demoDistance}px`);
    // Keep the path in window coordinates, but render the cursor on the desktop
    // so it can cross the actual screen edges without the window clipping it.
    const originX = win.offsetLeft - win.offsetWidth * browserScale / 2;
    const originY = win.offsetTop;
    const toggleX = (sidebarWidth - 22) * browserScale;
    const toggleY = 26 * browserScale;
    const toolbarX=Math.max(sidebarWidth+24,win.clientWidth/3)*browserScale,toolbarY=4*browserScale;
    demoCursor.style.setProperty('--cursor-origin-x', `${originX}px`);
    demoCursor.style.setProperty('--cursor-origin-y', `${originY}px`);
    const incoming = `M ${-originX - 28} ${pageHeight * .38 * browserScale} C ${toolbarX*.35} ${pageHeight*.38*browserScale}, ${toolbarX*.8} ${toolbarY}, ${toolbarX} ${toolbarY}`;
    const toToggle=` C ${toolbarX*.8} ${toolbarY}, ${toggleX+48*browserScale} ${toggleY}, ${toggleX} ${toggleY}`;
    // Arc above the browser, then leave the left edge of the desktop.
    const exitX = -originX - 32, exitY = -48 * browserScale;
    const outgoing = ` C ${toggleX - 30 * browserScale} ${-42 * browserScale}, ${exitX + 100 * browserScale} ${exitY - 20 * browserScale}, ${exitX} ${exitY}`;
    // Pause precisely at the toggle, regardless of viewport or curve length.
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', incoming);
    const toolbarLength=path.getTotalLength();
    path.setAttribute('d',incoming+toToggle);
    const incomingLength = path.getTotalLength();
    path.setAttribute('d', incoming + toToggle + outgoing);
    cursorPath = path;
    cursorPathLength = path.getTotalLength();
    cursorStop = incomingLength / cursorPathLength * 100;
    toolbarStop=toolbarLength/cursorPathLength*100;
    demoCursor.style.setProperty('--cursor-toolbar-stop',`${toolbarStop}%`);
    demoCursor.style.setProperty('--cursor-stop', `${cursorStop}%`);
    demoCursor.style.setProperty('--cursor-path', `path("${incoming + toToggle + outgoing}")`);
    reading = Math.max(0, pages.scrollHeight - pageHeight);
    root.style.setProperty('--reading', `${reading}px`);
    root.style.setProperty('--thumb-size', `${pageHeight / pages.scrollHeight * 100}%`);
    root.style.setProperty('--thumb-travel', `${reading / pageHeight * 100}%`);
    base = parseFloat(getComputedStyle(items[0]).width);
    update();
  }
  function measureBotany() {
    // Use the stable flex row boxes, not the overflow-visible SVG graphics bounds.
    // Safari can report their painted bounds before the first settled layout.
    const pageBox=pages.getBoundingClientRect(),scale=pageBox.width/pages.clientWidth;
    const nodes=points.map(point=>{
      const box=point.getBoundingClientRect();
      const bulletHeight=Number(point.querySelector('.botanical-bullet').getAttribute('height'));
      return {x:(box.left-pageBox.left)/scale+point.pivotX,y:(box.top-pageBox.top)/scale+(box.height/scale-bulletHeight)/2+86};
    });
    const first=nodes[0],last=nodes[nodes.length-1],coda=pages.querySelector('.coda');
    const groundY=coda.offsetTop+pageHeight*.15, rootX=last.x-8,rootDepth=Math.min(180,pageHeight*.25);
    const botanicalHeight=coda.offsetTop+pageHeight;
    vine.setAttribute('viewBox',`0 0 ${pages.clientWidth} ${botanicalHeight}`);
    vine.style.height=`${botanicalHeight}px`;
    let d=`M ${first.x} ${first.y}`,stemLength=0;
    const attachments=[0],sprigAttachments=[];
    const growth=document.createDocumentFragment();
    function specimen(at,angle,scale,opacity,seed,parent=growth) {
      const generated=leaf(seed);
      generated.setAttribute('transform',`translate(${at.x} ${at.y}) rotate(${angle}) scale(${scale})`);
      generated.setAttribute('opacity',opacity);parent.append(generated);
    }
    function shoot(at,side,variant,distance) {
      const group=svg('g',{class:'sprig-opening'});
      growth.append(group);sprigAttachments.push({group,at,side,distance});
      const reach=20+(variant%4)*5,rise=17+(variant%3)*7;
      const tip={x:at.x+side*reach,y:at.y-rise};
      const branch=svg('path',{class:'vine-tendril',d:`M ${at.x} ${at.y} Q ${at.x+side*reach*.7} ${at.y-3}, ${tip.x} ${tip.y}`});
      group.append(branch);
      const length=branch.getTotalLength(),beforeTip=branch.getPointAtLength(Math.max(0,length-1));
      const angle=Math.atan2(tip.x-beforeTip.x,-(tip.y-beforeTip.y))*180/Math.PI;
      specimen(tip,angle,.6+variant%5*.06,.8+variant%3*.06,173+variant*79,group);
      // Secondary leaves attach to a measured point on the branch, never a guessed offset.
      if(variant%3!==1) {
        const distance=length*.52,middle=branch.getPointAtLength(distance);
        const before=branch.getPointAtLength(distance-1),after=branch.getPointAtLength(distance+1);
        const tangent=Math.atan2(after.x-before.x,-(after.y-before.y))*180/Math.PI;
        specimen(middle,tangent-side*(38+variant%3*9),.48+variant%3*.04,.82,983+variant*43,group);
      }
    }
    nodes.slice(1).forEach((node,index)=>{
      const previous=nodes[index],dy=node.y-previous.y;
      const curve=`C ${index===0?previous.x:previous.x-28-index%3*6} ${previous.y+dy*.32}, ${node.x+24} ${node.y-dy*.38}, ${node.x} ${node.y}`;
      d+=` ${curve}`;
      const segment=svg('path',{d:`M ${previous.x} ${previous.y} ${curve}`}),length=segment.getTotalLength();
      const positions=[[.32,.7],[.26,.58,.83],[.44],[.29,.68]][index%4];
      positions.forEach((progress,j)=>shoot(segment.getPointAtLength(length*progress),(index+j)%2?1:-1,index*3+j,stemLength+length*progress));
      if(index%3!==1) {
        const at=segment.getPointAtLength(length*(index%2?.78:.86)),side=index%2?1:-1,reach=22+index%3*5;
        const group=svg('g',{class:'sprig-opening'});
        group.append(svg('path',{class:'vine-tendril',d:`M ${at.x} ${at.y} C ${at.x+side*16} ${at.y-14}, ${at.x+side*(reach+14)} ${at.y+4}, ${at.x+side*reach} ${at.y+17} C ${at.x+side*(reach-11)} ${at.y+25}, ${at.x+side*(reach-17)} ${at.y+6}, ${at.x+side*(reach-7)} ${at.y+9}`}));
        growth.append(group);sprigAttachments.push({group,at,side,distance:stemLength+length*(index%2?.78:.86)});
      }
      stemLength+=length;attachments.push(stemLength);
    });
    d+=` C ${last.x-24} ${last.y+(groundY-last.y)*.3}, ${rootX+18} ${groundY-(groundY-last.y)*.3}, ${rootX} ${groundY}`;
    vine.querySelectorAll('.vine-base,.vine-growth').forEach(path=>path.setAttribute('d',d));
    stemLength=vineGrowth.getTotalLength();
    motes.forEach(mote=>{
      const at=vineGrowth.getPointAtLength(mote.crownDistance?Math.max(0,stemLength-mote.crownDistance):stemLength*mote.fraction);
      mote.x=at.x;mote.y=at.y;
    });
    sprigs.replaceChildren(growth);
    // Layered Perlin gradient noise: rolling contour, smaller bumps, fine grain.
    const terrain=x=>noise(x/260+4.3,19)*18+noise(x/88+13.1,37)*6+noise(x/31+9.7,73)*2.2+noise(x/10+2.5,113)*.6;
    const floorPoints=[];
    for(let x=0;x<pages.clientWidth;x+=8)floorPoints.push({x,y:groundY+terrain(x)-terrain(rootX)});
    floorPoints.push({x:rootX,y:groundY},{x:pages.clientWidth,y:groundY+terrain(pages.clientWidth)-terrain(rootX)});
    floorPoints.sort((a,b)=>a.x-b.x);
    const contour=smoothPath(floorPoints);
    soil.setAttribute('d',`${contour} L ${pages.clientWidth} ${botanicalHeight} L 0 ${botanicalHeight} Z`);
    const rootWidth=Math.min(420,pages.clientWidth*.54);
    measureRoots(rootX,groundY,rootDepth,rootWidth);
    flowerStart=Math.max(readingStart,readingStart+first.y-pageHeight*.85);
    flowerEnd=flowerStart+pageHeight*.45;
    vineStart=Math.max(0,readingStart+first.y-pageHeight*.8,flowerStart+(flowerEnd-flowerStart)*.35);
    vineEnd=readingStart+groundY-pageHeight*.6;
    rootWave.start=vineEnd;rootWave.end=vineEnd+pageHeight*.27;
    roots.style.setProperty('--root-start',`${rootWave.start}px`);
    roots.style.setProperty('--root-end',`${rootWave.end}px`);
    root.style.setProperty('--vine-start',`${vineStart}px`);
    root.style.setProperty('--vine-end',`${vineEnd}px`);
    root.style.setProperty('--flower-start',`${flowerStart}px`);
    root.style.setProperty('--flower-end',`${flowerEnd}px`);
    const lightRange=distance=>{
      const start=vineStart+(vineEnd-vineStart)*distance/stemLength;
      return {lightStart:start,lightEnd:start+pageHeight*.12};
    };
    sprigRanges=sprigAttachments.map(attachment=>({...attachment,...lightRange(attachment.distance)}));
    points.forEach((point,index)=>{
      const start=Math.max(0,readingStart+nodes[index].y-pageHeight),end=readingStart+nodes[index].y+pageHeight*.25;
      leafRanges[index]={start,end,...lightRange(attachments[index])};
      point.style.setProperty('--leaf-start',`${start}px`);
      point.style.setProperty('--leaf-end',`${end}px`);
      const text=point.querySelector('p'),box=point.getBoundingClientRect();
      const center=(box.top-pageBox.top)/scale+point.offsetHeight/2-(index===0?22:10);
      textRanges.push({text,start:readingStart+center-pageHeight*.85});
    });
  }
  function measureRoots(rootX,groundY,rootDepth,rootWidth) {
    // Cache the complete silhouettes until layout changes. Only two radial
    // fronts animate, instead of a pair of centerline masks for every branch.
    const key=[rootX,groundY,rootDepth,rootWidth,pages.clientWidth].join(',');
    if(rootWave?.key===key)return;
    const rootGrowth=document.createDocumentFragment(),rootMasks=svg('defs');
    const gradient=svg('radialGradient',{id:'root-reveal',cx:0,cy:0,r:1,gradientUnits:'userSpaceOnUse'});
    gradient.append(svg('stop',{offset:'.9','stop-color':'white'}),svg('stop',{offset:1,'stop-color':'white','stop-opacity':0}));
    rootMasks.append(gradient);rootGrowth.append(rootMasks);
    const base=svg('g',{class:'root-base',mask:'url(#root-base-mask)'});
    const light=svg('g',{class:'root-light',mask:'url(#root-light-mask)'});
    rootGrowth.append(base,light);
    let reach=0;
    function rootBranch(start,angle,length,width,order,seed) {
      const local=random(seed),curve=[start],steps=Math.max(8,Math.ceil(length/6));
      let x=start.x,y=start.y,heading=angle;
      for(let i=1;i<=steps;i++) {
        const t=i/steps,down=order===0?.28:.12;
        const target=angle*(1-down*t)+noise(t*2.3+seed*.13,seed)*.7+noise(t*7.1+seed,seed+31)*.22;
        heading+=(target-heading)*.48;
        x+=Math.sin(heading)*length/steps;
        y+=Math.max(.16,Math.cos(heading))*length/steps;
        if(x<8||x>pages.clientWidth-8||Math.abs(x-rootX)>rootWidth/2||y>groundY+rootDepth)break;
        curve.push({x,y});
      }
      if(curve.length<4)return;
      const center=svg('path',{d:smoothPath(curve)});
      const distance=center.getTotalLength(),left=[],right=[];
      curve.forEach((at,i)=>{
        const before=curve[Math.max(0,i-1)],after=curve[Math.min(curve.length-1,i+1)],dx=after.x-before.x,dy=after.y-before.y,norm=Math.hypot(dx,dy)||1;
        const taper=Math.pow(1-i/(curve.length-1),.85),radius=width/2*taper*(1+noise(i*.42+seed,seed)*.12);
        left.push({x:at.x-dy/norm*radius,y:at.y+dx/norm*radius});
        right.push({x:at.x+dy/norm*radius,y:at.y-dx/norm*radius});
        reach=Math.max(reach,Math.hypot(at.x-rootX,at.y-groundY)+radius);
      });
      const outline=smoothPath([...left,...right.reverse()],true),opacity=order===0?.95:.72+local()*.25;
      base.append(svg('path',{d:outline,class:'root-outline',fill:'var(--botanical-ink)',stroke:'none',opacity:opacity*.5,'data-root-order':order}));
      light.append(svg('path',{d:outline,stroke:'none',opacity:opacity*.9}));
      if(order>=3)return center;
      const count=order===0?5+Math.floor(local()*3):order===1?1+Math.floor(local()*3):2+Math.floor(local()*3);
      let side=local()<.5?-1:1;
      for(let i=0;i<count;i++) {
        const fraction=(order===2?.25:.14)+(i+.15+local()*.65)/count*(order===2?.52:.66),at=center.getPointAtLength(distance*fraction);
        const before=center.getPointAtLength(Math.max(0,distance*fraction-1)),after=center.getPointAtLength(Math.min(distance,distance*fraction+1));
        const tangent=Math.atan2(after.x-before.x,after.y-before.y);
        if(local()<.72)side*=-1;
        const childLength=order===2?7+local()*13:distance*(order===0?.26+local()*.3:.23+local()*.27)*(1-fraction*.35);
        rootBranch(at,tangent+side*(.5+local()*.65),childLength,Math.max(.38,width*(order===0?.34+local()*.14:order===1?.4:.65)),order+1,seed*7+i+1);
      }
      return center;
    }
    const taproot=rootBranch({x:rootX,y:groundY},-.1,rootDepth*.99,3.3,0,113);
    rootBranch(taproot.getPointAtLength(9),-1.2,rootDepth*1.5,2.7,0,239);
    rootBranch(taproot.getPointAtLength(23),1.04,rootDepth*1.28,2.45,0,419);
    // The final opaque plateau covers every outline, including its stroke
    // width. Keep each mask tightly bounded to the small root illustration.
    const radius=(reach+2)/.9;
    function front(kind) {
      const mask=svg('mask',{id:`root-${kind}-mask`,maskUnits:'userSpaceOnUse',x:rootX-rootWidth/2-8,y:groundY-8,width:rootWidth+16,height:rootDepth+16,style:'mask-type:alpha'});
      const origin=svg('g',{transform:`translate(${rootX} ${groundY})`});
      const circle=svg('circle',{class:`root-${kind}-front`,r:1,fill:'url(#root-reveal)'});
      origin.append(circle);mask.append(origin);rootMasks.append(mask);
      circle.style.setProperty('--root-radius',radius);
      return circle;
    }
    rootWave={key,base:front('base'),light:front('light'),radius,progress:null};
    roots.replaceChildren(rootGrowth);
  }
  function updateBotany(y) {
    // Scroll chooses a settled state; CSS transitions own the elapsed-time motion.
    textRanges.forEach(({text,start})=>{
      const state=reduce.matches||y>=start?'visible':'before';
      if(text.dataset.textState!==state)text.dataset.textState=state;
    });
    const readingOffset=Math.max(0,y-readingStart);
    motes.forEach(mote=>{
      const screenY=mote.y-readingOffset;
      const progress=reduce.matches?0:clamp((pageHeight*.9-screenY)/(pageHeight*.9));
      // Cubic separation keeps the lower view calm and opens up near the top.
      const drift=progress*progress*progress;
      mote.group.setAttribute('transform',`translate(${mote.x+mote.side*(mote.gap+mote.reach*drift)} ${mote.y-18*drift})`);
      mote.group.setAttribute('opacity',reduce.matches?.8:clamp((pageHeight*1.08-screenY)/(pageHeight*.18))*clamp((screenY+pageHeight*.12)/(pageHeight*.18)));
      mote.group.toggleAttribute('data-visible',screenY>-80&&screenY<pageHeight+80&&!reduce.matches);
    });
    points.forEach((point,index)=>{
      const {start,end,lightStart,lightEnd}=leafRanges[index],t=clamp((y-start)/(end-start));
      const opening=reduce.matches?1:introEase(clamp((y-lightStart)/(lightEnd-lightStart)));
      const angle=index===0?0:(index%2?7:-5)+(reduce.matches?0:Math.sin(t*Math.PI*2-Math.PI/2)*3)+(index%2?-6:6)*opening;
      point.querySelector('.botanical-sway').setAttribute('transform',`rotate(${angle} ${point.pivotX} 86)`);
    });
    sprigRanges.forEach(({group,at,side,lightStart,lightEnd})=>{
      const opening=reduce.matches?1:introEase(clamp((y-lightStart)/(lightEnd-lightStart)));
      group.setAttribute('transform',`rotate(${side*7*opening} ${at.x} ${at.y})`);
    });
    if(!nativeTimeline||reduce.matches) {
      const progress=reduce.matches?1:clamp((y-rootWave.start)/(rootWave.end-rootWave.start));
      if(progress!==rootWave.progress) {
        rootWave.base.style.transform=`scale(${rootWave.radius*(.7+.3*progress)})`;
        rootWave.light.style.transform=`scale(${rootWave.radius*progress})`;
        rootWave.progress=progress;
      }
    }
    if(nativeTimeline||reduce.matches)return;
    const introProgress=clamp((y-introStart)/(introEnd-introStart)),intro=introEase(introProgress);
    introLogo.style.opacity=clamp((introProgress-.03)/.05);
    introCircles.forEach(circle=>{
      const shift=parseFloat(circle.style.getPropertyValue('--shift'));
      circle.style.transform=`translateX(${shift*intro}px)`;
      if(circle.classList.contains('setup-cutout'))circle.style.r=`${111+1.725508*intro}px`;
    });
    introLogo.style.transform=`scale(${1.2-.2*intro})`;
    vineGrowth.style.strokeDasharray='1';
    vineGrowth.style.strokeDashoffset=1-clamp((y-vineStart)/(vineEnd-vineStart));
    const bloom=clamp((y-flowerStart)/(flowerEnd-flowerStart));
    flowerBloom.style.transform=`rotate(${-2+4*bloom}deg)`;
    petals[0].style.transform=`scaleX(${.6+.4*bloom})`;
    petals[1].style.transform=`rotate(${18-40*bloom}deg)`;
    petals[2].style.transform=`rotate(${-18+42*bloom}deg)`;
    petals[3].style.transform=`scale(${.62+.46*bloom},${1.14-.42*bloom})`;
    stamens.style.transform=`translateY(${5-5*bloom}px) scale(${.16+.84*bloom},${.72+.28*bloom})`;
    stamens.style.opacity=.6+.4*bloom;
  }
  function updateCommandDemo(y) {
    const active=appVisible&&!reduce.matches&&y>=commandStart&&y<commandEnd;
    if(!active||y<bangStart) {
      if(commandFrame)cancelAnimationFrame(commandFrame);
      commandFrame=0;bangStartedAt=null;
      renderCommandDemo(active?'open':'closed','',false,false);
      return;
    }
    if(y>=commandDismiss) {
      if(commandFrame)cancelAnimationFrame(commandFrame);
      commandFrame=0;
      renderCommandDemo('closed','',false,false);
      return;
    }
    // Like the prose reveals, typing completes in elapsed time when scrolling
    // pauses. Leaving this section cancels it; reversing above !bangs resets it.
    if(bangStartedAt===null)bangStartedAt=performance.now();
    const elapsed=Math.max(performance.now()-bangStartedAt,clamp((y-bangStart)/(commandComplete-bangStart))*1100);
    const typed='!wiki'.slice(0,Math.max(0,Math.min(5,Math.floor((elapsed-200)/120))));
    if(elapsed<1100)renderCommandDemo(typed?'typing':'open',typed,false,false);
    else renderCommandDemo('scoped','',true,true);
    if(elapsed<1100&&!commandFrame)commandFrame=requestAnimationFrame(()=>{commandFrame=0;updateCommandDemo(scroll.scrollTop);});
  }
  function renderCommandDemo(state,query,scoped,hint) {
    if(commandDemo.dataset.commandState!==state)commandDemo.dataset.commandState=state;
    // Fade the whole pane away at its current size, without collapsing its row.
    if(state==='closed')return;
    if(commandQuery.textContent!==query)commandQuery.textContent=query;
    if(commandScope.hidden===scoped)commandScope.hidden=!scoped;
    if(commandHint.hidden===hint)commandHint.hidden=!hint;
    const placeholderHidden=scoped||Boolean(query);
    if(commandPlaceholder.hidden!==placeholderHidden)commandPlaceholder.hidden=placeholderHidden;
  }
  function update(){
    queued=false;const y=scroll.scrollTop;if(y>launchAt&&pointer!==null){pointer=null;startMagnify();}if(y<=launchAt)close();else {launch();if(y>=readingStart&&y>opening)reveal(true);}const p=clamp(y/opening),r=reading ? clamp((y-readingStart)/reading) : 0;
    hero.inert=appVisible||y>=opening;learn.inert=appVisible||y>=opening;
    win.inert=!appVisible;win.setAttribute('aria-hidden',String(!appVisible));win.style.pointerEvents=appVisible?'auto':'none';
    root.dataset.phase=appVisible?'reading':launched?'launching':'closed';root.dataset.progress=p.toFixed(3);
    updateSidebar(y);
    updateBotany(y);
    updateCommandDemo(y);
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
    const animatedFold = Number(progress >= .68);
    const fold = sidebarOverride ?? animatedFold;
    if (!nativeTimeline || reduce.matches || sidebarOverride !== null) win.style.setProperty('--sidebar-fold', fold);
    const floating = sidebarOverride !== null ? Boolean(sidebarOverride) : progress >= .68;
    const cursorDistance=progress<=.18?clamp(progress/.18)*toolbarStop:
      progress<=.42?toolbarStop:
      progress<=.62?toolbarStop+clamp((progress-.42)/.20)*(cursorStop-toolbarStop):
      progress<=.76?cursorStop:cursorStop+clamp((progress-.76)/.24)*(100-cursorStop);
    const cursorPoint = cursorPath.getPointAtLength(cursorDistance / 100 * cursorPathLength);
    const cursorInsideWindow=cursorPoint.x>=0&&cursorPoint.x<=win.clientWidth*browserScale&&
      cursorPoint.y>=0&&cursorPoint.y<=win.clientHeight*browserScale;
    const demoHolding = sidebarOverride === null && (progress < .68 || cursorInsideWindow);
    const keyboardFocus = Boolean(sidebarRegion.querySelector(':focus-visible'));
    const visible = !floating || demoHolding || sidebarHovered || keyboardFocus;
    sidebar.inert = !visible;
    sidebar.setAttribute('aria-hidden', String(!visible));
    sidebarRail.setAttribute('aria-expanded', String(visible));
    sidebarToggle.setAttribute('aria-pressed', String(!floating));
    sidebarToggle.setAttribute('aria-label', floating ? 'Pin sidebar' : 'Unpin sidebar');
    win.dataset.sidebar = !floating ? 'pinned' : visible ? 'floating' : 'hidden';
    updateWindowControls('sidebar');
    const wasDemoToolbarActive=demoToolbarActive;
    demoToolbarActive=!reduce.matches&&sidebarOverride===null&&progress>=.18&&progress<1&&cursorInsideWindow;
    if(demoToolbarActive)showToolbar();
    else if(wasDemoToolbarActive) {
      if(panelPointer)dismissDistantPanels();
      else if(!toolbarRegion.contains(document.activeElement)&&!windowControls.contains(document.activeElement))hideToolbar();
    }
    if (!nativeTimeline || browserScale !== 1) {
      demoCursor.style.opacity = Math.min(clamp(progress / .06), 1 - clamp((progress - .94) / .06));
      const press = progress <= .68 ? clamp((progress - .64) / .04) : 1 - clamp((progress - .68) / .04);
      if(browserScale !== 1) {
        // Drive phone motion with ordinary transforms, independently of native
        // scroll-timeline interpolation of motion-path offset-distance.
        demoCursor.style.transform = `translate3d(${cursorPoint.x-2*browserScale}px,${cursorPoint.y-1.5*browserScale}px,0) scale(${1-.16*press})`;
      } else {
        demoCursor.style.offsetDistance = `${cursorDistance}%`;
        demoCursor.style.transform = `scale(${1 - .16 * press})`;
      }
      const click = clamp((progress - .64) / .12);
      demoClick.style.opacity = progress <= .68 ? .7 * clamp((progress - .64) / .04) : .7 * (1 - clamp((progress - .68) / .08));
      demoClick.style.transform = `scale(${.5 + click * 1.2})`;
    } else if(demoCursor.style.transform) {
      ['transform','opacity','offset-distance'].forEach(property=>demoCursor.style.removeProperty(property));
      ['transform','opacity'].forEach(property=>demoClick.style.removeProperty(property));
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
    if(demoToolbarActive)return;
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
    if (!demoToolbarActive && toolbarRegion.hasAttribute('data-open') && !toolbarRegion.contains(document.activeElement) &&
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
    if(!launched&&!appVisible)return;sidebarHovered=false;panelPointer=null;demoToolbarActive=false;hideToolbar();clearTimeout(showTimer);launched=false;appVisible=false;
    root.classList.remove('app-open','app-fast');root.querySelector('.lune').classList.remove('launching');
  }
  function returnToDesktop() {
    scroll.scrollTo({top:0,behavior:reduce.matches?'instant':'smooth'});
    scroll.focus({preventScroll:true});
  }
  sidebar.querySelectorAll('.tab-close').forEach(button => {
    button.addEventListener('click', () => {
      const tab=button.closest('.browser-tab');
      const next=tab.nextElementSibling??tab.previousElementSibling;
      if(tab===currentTab) {
        scroll.scrollTo({top:0,behavior:'instant'});
        scroll.focus({preventScroll:true});
      } else {
        if(tab.contains(document.activeElement))
          (next?.querySelector('.tab-target')??sidebar.querySelector('.sidebar-new-tab')).focus({preventScroll:true});
        tab.remove();
      }
    });
  });
  root.querySelectorAll('[data-open]').forEach(el=>el.addEventListener('click',()=>{scroll.scrollTo({top:opening,behavior:reduce.matches?'instant':'smooth'});}));
  root.querySelectorAll('[data-close]').forEach(button => {
    button.addEventListener('click', returnToDesktop);
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
    const platform = navigator.userAgentData?.platform || navigator.platform || '';
    const agent = navigator.userAgent || '';
    // iPadOS can use a desktop Mac identity, but still reports multiple touch points.
    const iPad = /Mac/i.test(platform + agent) && navigator.maxTouchPoints > 1;
    const unsupported = /^(Windows|Android|iOS|Linux|Chrome OS|Chromium OS)$/i.test(platform)
      || /^(Win|Linux|iPhone|iPad|iPod)/i.test(platform)
      || /Windows|Android|iPhone|iPad|iPod|Linux|CrOS/i.test(agent)
      || iPad;
    if (unsupported) {
      root.querySelectorAll('.action.download').forEach(button => {
        button.disabled = true;
        button.querySelector('.download-chevron').remove();
        button.title = 'Available for macOS only';
      });
      return;
    }
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
  let measureFrame=0;
  function scheduleMeasure() {
    if(measureFrame)return;
    measureFrame=requestAnimationFrame(()=>{
      measureFrame=0;
      if(pointer===null)items.forEach(el=>{el.style.width='';el.style.height='';el.style.removeProperty('--rendered-icon');});
      measure();
      if(pointer===null)widths.fill(base);
    });
  }
  const geometryObserver=new ResizeObserver(scheduleMeasure);
  [stage,pages,root.querySelector('.viewport'),...points].forEach(element=>geometryObserver.observe(element));
  reduce.addEventListener('change',()=>{introCircles.forEach(circle=>{circle.style.removeProperty('transform');circle.style.removeProperty('r');});introLogo.style.removeProperty('transform');introLogo.style.removeProperty('opacity');[rootWave.base,rootWave.light].forEach(front=>front.style.removeProperty('transform'));rootWave.progress=null;vineGrowth.style.removeProperty('stroke-dasharray');vineGrowth.style.removeProperty('stroke-dashoffset');flowerBloom.style.removeProperty('transform');petals.forEach(petal=>petal.style.removeProperty('transform'));stamens.style.removeProperty('transform');stamens.style.removeProperty('opacity');if(nativeTimeline&&!reduce.matches&&sidebarOverride===null)win.style.removeProperty('--sidebar-fold');pointer=null;items.forEach(el=>{el.style.width='';el.style.height='';el.style.removeProperty('--rendered-icon');});measure();widths.fill(base);});
  measure();widths.fill(base);
  scheduleMeasure();
  document.fonts.ready.then(scheduleMeasure);
  window.addEventListener('load',scheduleMeasure,{once:true});
  window.addEventListener('pageshow',scheduleMeasure);
})();
