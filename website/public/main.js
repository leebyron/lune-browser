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
    ink.append(svg('path',{d:body,fill:'url(#leaf-ink)',opacity:.9+rng()*.1}));
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
  const ground=vine.querySelector('.vine-ground'),soil=vine.querySelector('.vine-soil'),roots=vine.querySelector('.vine-roots');
  const petals=[...flowerBloom.querySelectorAll('.petal')], stamens=flowerBloom.querySelector('.flower-stamens');
  // A seeded fan of fine filaments gives the upward-facing flower depth.
  const stamenRng=random(887),filaments=svg('path',{fill:'none',stroke:'var(--biolume-stalk)','stroke-width':.55,'stroke-linecap':'round'});
  const halos=svg('g',{fill:'var(--biolume)',filter:'url(#stamen-light)',opacity:.55}),anthers=svg('g',{fill:'var(--biolume)'});
  let filamentPath='';
  for(let i=0;i<19;i++) {
    const fan=(i/18-.5)*2,x=fan*21+(stamenRng()-.5)*4,y=-27-stamenRng()*15-Math.cos(fan*Math.PI/2)*3;
    const baseX=(stamenRng()-.5)*7,rx=1+stamenRng()*.65,ry=.55+stamenRng()*.4;
    filamentPath+=`M ${baseX} -2 Q ${x*.45+(stamenRng()-.5)*5} ${y*.52}, ${x} ${y}`;
    halos.append(svg('ellipse',{cx:x,cy:y,rx:rx*1.8,ry:ry*1.9}));
    anthers.append(svg('ellipse',{cx:x,cy:y,rx,ry,opacity:.65+stamenRng()*.35,transform:`rotate(${fan*25} ${x} ${y})`}));
  }
  filaments.setAttribute('d',filamentPath);stamens.replaceChildren(filaments,halos,anthers);
  let vineStart=0, vineEnd=1, flowerStart=0, flowerEnd=1,introStart=0,introEnd=1;
  let rootRanges=[];
  const leafRanges=[];
  points.forEach((point, index) => {
    point.style.setProperty('--flow-offset', Math.sin(index / (points.length - 1) * 2 * Math.PI).toFixed(5));
    point.style.setProperty('--leaf-angle', `${index === 0 ? 0 : index % 2 ? 7 : -5}deg`);
    const right=index>0 && index%2===0;
    point.dataset.leafSide=index===0?'flower':right?'right':'left';
    point.style.setProperty('--petiole-x',`${index===0?50:right?20:80}%`);
    if(index>0) {
      const specimen=point.querySelector('.generated-specimen');
      if(right)specimen.setAttribute('transform','translate(80 0) scale(-1 1)');
      const generated=leaf(419+index*103,true);generated.setAttribute('transform','translate(64 86)');specimen.append(generated);
    }
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
    const coda=pages.querySelector('.coda'),codaContent=coda.querySelector('.coda-content'),thanks=coda.querySelector('.upstream-thanks'),byline=coda.querySelector('.byline');
    const actionsBottom=pageHeight/2+codaContent.offsetHeight/2;
    coda.style.setProperty('--thanks-top',`${(actionsBottom+byline.offsetTop)/2-thanks.offsetHeight/2}px`);
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
    // Resting layout coordinates share the exact pivot of each mirrored petiole.
    const nodes=points.map((point,index)=>({x:point.offsetLeft+(index===0?40:index%2?64:16),y:point.offsetTop+(point.clientHeight-100)/2+86}));
    const first=nodes[0],last=nodes[nodes.length-1],coda=pages.querySelector('.coda');
    const groundY=coda.offsetTop+pageHeight*.15, rootX=last.x-8,rootDepth=Math.min(180,pageHeight*.25);
    const botanicalHeight=coda.offsetTop+pageHeight;
    vine.setAttribute('viewBox',`0 0 ${pages.clientWidth} ${botanicalHeight}`);
    vine.style.height=`${botanicalHeight}px`;
    let d=`M ${first.x} ${first.y}`;
    const growth=document.createDocumentFragment();
    function specimen(at,angle,scale,opacity,seed) {
      const generated=leaf(seed);
      generated.setAttribute('transform',`translate(${at.x} ${at.y}) rotate(${angle}) scale(${scale})`);
      generated.setAttribute('opacity',opacity);growth.append(generated);
    }
    function shoot(at,side,variant) {
      const reach=20+(variant%4)*5,rise=17+(variant%3)*7;
      const tip={x:at.x+side*reach,y:at.y-rise};
      const branch=svg('path',{class:'vine-tendril',d:`M ${at.x} ${at.y} Q ${at.x+side*reach*.7} ${at.y-3}, ${tip.x} ${tip.y}`});
      growth.append(branch);
      const length=branch.getTotalLength(),beforeTip=branch.getPointAtLength(Math.max(0,length-1));
      const angle=Math.atan2(tip.x-beforeTip.x,-(tip.y-beforeTip.y))*180/Math.PI;
      specimen(tip,angle,.6+variant%5*.06,.8+variant%3*.06,173+variant*79);
      // Secondary leaves attach to a measured point on the branch, never a guessed offset.
      if(variant%3!==1) {
        const distance=length*.52,middle=branch.getPointAtLength(distance);
        const before=branch.getPointAtLength(distance-1),after=branch.getPointAtLength(distance+1);
        const tangent=Math.atan2(after.x-before.x,-(after.y-before.y))*180/Math.PI;
        specimen(middle,tangent-side*(38+variant%3*9),.48+variant%3*.04,.82,983+variant*43);
      }
    }
    nodes.slice(1).forEach((node,index)=>{
      const previous=nodes[index],dy=node.y-previous.y;
      const curve=`C ${previous.x-28-index%3*6} ${previous.y+dy*.32}, ${node.x+24} ${node.y-dy*.38}, ${node.x} ${node.y}`;
      d+=` ${curve}`;
      const segment=svg('path',{d:`M ${previous.x} ${previous.y} ${curve}`}),length=segment.getTotalLength();
      const positions=[[.32,.7],[.26,.58,.83],[.44],[.29,.68]][index%4];
      positions.forEach((progress,j)=>shoot(segment.getPointAtLength(length*progress),(index+j)%2?1:-1,index*3+j));
      if(index%3!==1) {
        const at=segment.getPointAtLength(length*(index%2?.78:.86)),side=index%2?1:-1,reach=22+index%3*5;
        growth.append(svg('path',{class:'vine-tendril',d:`M ${at.x} ${at.y} C ${at.x+side*16} ${at.y-14}, ${at.x+side*(reach+14)} ${at.y+4}, ${at.x+side*reach} ${at.y+17} C ${at.x+side*(reach-11)} ${at.y+25}, ${at.x+side*(reach-17)} ${at.y+6}, ${at.x+side*(reach-7)} ${at.y+9}`}));
      }
    });
    d+=` C ${last.x-24} ${last.y+(groundY-last.y)*.3}, ${rootX+18} ${groundY-(groundY-last.y)*.3}, ${rootX} ${groundY}`;
    vine.querySelectorAll('.vine-base,.vine-growth').forEach(path=>path.setAttribute('d',d));
    sprigs.replaceChildren(growth);
    // Layered Perlin gradient noise: rolling contour, smaller bumps, fine grain.
    const terrain=x=>noise(x/260+4.3,19)*18+noise(x/88+13.1,37)*6+noise(x/31+9.7,73)*2.2+noise(x/10+2.5,113)*.6;
    const floorPoints=[];
    for(let x=0;x<pages.clientWidth;x+=8)floorPoints.push({x,y:groundY+terrain(x)-terrain(rootX)});
    floorPoints.push({x:rootX,y:groundY},{x:pages.clientWidth,y:groundY+terrain(pages.clientWidth)-terrain(rootX)});
    floorPoints.sort((a,b)=>a.x-b.x);
    const contour=smoothPath(floorPoints);ground.setAttribute('d',contour);
    soil.setAttribute('d',`${contour} L ${pages.clientWidth} ${botanicalHeight} L 0 ${botanicalHeight} Z`);
    // A few wandering structural roots carry uneven lateral roots and fine rootlets.
    // Each filled outline tapers to a point; a centerline mask extends only its last fifth.
    const rootGrowth=document.createDocumentFragment(),rootMasks=svg('defs'),branches=[],rng=random(2207);
    rootGrowth.append(rootMasks);
    const rootWidth=Math.min(420,pages.clientWidth*.54);
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
      const center=svg('path',{d:smoothPath(curve),class:'root-growth',fill:'none',stroke:'white','stroke-width':width+2,'stroke-linecap':'round',pathLength:1});
      const distance=center.getTotalLength(),left=[],right=[];
      curve.forEach((at,i)=>{
        const before=curve[Math.max(0,i-1)],after=curve[Math.min(curve.length-1,i+1)],dx=after.x-before.x,dy=after.y-before.y,norm=Math.hypot(dx,dy)||1;
        const taper=Math.pow(1-i/(curve.length-1),.85),radius=width/2*taper*(1+noise(i*.42+seed,seed)*.12);
        left.push({x:at.x-dy/norm*radius,y:at.y+dx/norm*radius});
        right.push({x:at.x+dy/norm*radius,y:at.y-dx/norm*radius});
      });
      const id=`story-root-${branches.length}`,mask=svg('mask',{id,maskUnits:'userSpaceOnUse',x:0,y:groundY-8,width:pages.clientWidth,height:rootDepth+16});
      mask.append(center);rootMasks.append(mask);
      rootGrowth.append(svg('path',{d:smoothPath([...left,...right.reverse()],true),class:'root-outline',fill:'var(--botanical-ink)',stroke:'none',mask:`url(#${id})`,opacity:order===0?.95:.72+local()*.25,'data-root-order':order}));
      branches.push({path:center,order});
      if(order>=2)return center;
      const count=order===0?5+Math.floor(local()*3):1+Math.floor(local()*3);
      let side=local()<.5?-1:1;
      for(let i=0;i<count;i++) {
        const fraction=.14+(i+.15+local()*.65)/count*.66,at=center.getPointAtLength(distance*fraction);
        const before=center.getPointAtLength(Math.max(0,distance*fraction-1)),after=center.getPointAtLength(Math.min(distance,distance*fraction+1));
        const tangent=Math.atan2(after.x-before.x,after.y-before.y);
        if(local()<.72)side*=-1;
        const childLength=distance*(order===0?.26+local()*.3:.23+local()*.27)*(1-fraction*.35);
        rootBranch(at,tangent+side*(.5+local()*.65),childLength,width*(order===0?.34+local()*.14:.4),order+1,seed*7+i+1);
      }
      return center;
    }
    const taproot=rootBranch({x:rootX,y:groundY},-.1,rootDepth*.99,3.3,0,113);
    rootBranch(taproot.getPointAtLength(9),-1.2,rootDepth*1.5,2.7,0,239);
    rootBranch(taproot.getPointAtLength(23),1.04,rootDepth*1.28,2.45,0,419);
    roots.replaceChildren(rootGrowth);
    const rootsStart=readingStart+groundY-pageHeight*.92,rootsEnd=readingStart+coda.offsetTop;
    rootRanges=branches.map(({path,order})=>{
      const start=rootsStart+(rootsEnd-rootsStart)*(order*.06+rng()*.12),end=rootsEnd;
      path.style.setProperty('--root-start',`${start}px`);path.style.setProperty('--root-end',`${end}px`);
      return {path,start,end};
    });
    vineStart=Math.max(0,readingStart+first.y-pageHeight*.8);
    vineEnd=readingStart+groundY-pageHeight*.15;
    flowerStart=Math.max(readingStart,readingStart+first.y-pageHeight*.85);
    flowerEnd=flowerStart+pageHeight*.45;
    root.style.setProperty('--vine-start',`${vineStart}px`);
    root.style.setProperty('--vine-end',`${vineEnd}px`);
    root.style.setProperty('--flower-start',`${flowerStart}px`);
    root.style.setProperty('--flower-end',`${flowerEnd}px`);
    points.forEach((point,index)=>{
      const start=Math.max(0,readingStart+nodes[index].y-pageHeight),end=readingStart+nodes[index].y+pageHeight*.25;
      leafRanges[index]={start,end};
      point.style.setProperty('--leaf-start',`${start}px`);
      point.style.setProperty('--leaf-end',`${end}px`);
    });
  }
  function updateBotany(y) {
    if(nativeTimeline||reduce.matches)return;
    const intro=introEase(clamp((y-introStart)/(introEnd-introStart)));
    introCircles.forEach(circle=>{
      const shift=parseFloat(circle.style.getPropertyValue('--shift'));
      circle.style.transform=`translateX(${shift*intro}px)`;
      if(circle.classList.contains('setup-cutout'))circle.style.r=`${111+1.725508*intro}px`;
    });
    introLogo.style.transform=`scale(${1.2-.2*intro})`;
    rootRanges.forEach(({path,start,end})=>{
      const progress=clamp((y-start)/(end-start));path.style.strokeDasharray='1';path.style.strokeDashoffset=.2*(1-progress);
    });
    vineGrowth.style.strokeDasharray='1';
    vineGrowth.style.strokeDashoffset=1-clamp((y-vineStart)/(vineEnd-vineStart));
    points.forEach((point,index)=>{
      const {start,end}=leafRanges[index],t=clamp((y-start)/(end-start));
      const angle=(index===0?0:index%2?7:-5)+Math.sin(t*Math.PI*2-Math.PI/2)*3;
      point.querySelector('.botanical-bullet').style.transform=`rotate(${angle}deg)`;
    });
    const bloom=clamp((y-flowerStart)/(flowerEnd-flowerStart));
    flowerBloom.style.transform=`rotate(${-2+4*bloom}deg)`;
    petals[0].style.transform=`scaleX(${.6+.4*bloom})`;
    petals[1].style.transform=`rotate(${18-40*bloom}deg)`;
    petals[2].style.transform=`rotate(${-18+42*bloom}deg)`;
    petals[3].style.transform=`scale(${.62+.46*bloom},${1.14-.42*bloom})`;
    stamens.style.transform=`translateY(${5-5*bloom}px) scale(${.16+.84*bloom},${.72+.28*bloom})`;
    stamens.style.opacity=.6+.4*bloom;
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
    const demoHolding = sidebarOverride === null && browserScale === 1 && (progress < .5 || distanceFromPanel({x:cursorPoint.x / browserScale,y:cursorPoint.y / browserScale},
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
  reduce.addEventListener('change',()=>{introCircles.forEach(circle=>{circle.style.removeProperty('transform');circle.style.removeProperty('r');});introLogo.style.removeProperty('transform');rootRanges.forEach(({path})=>{path.style.removeProperty('stroke-dasharray');path.style.removeProperty('stroke-dashoffset');path.style.removeProperty('opacity');});vineGrowth.style.removeProperty('stroke-dasharray');vineGrowth.style.removeProperty('stroke-dashoffset');flowerBloom.style.removeProperty('transform');petals.forEach(petal=>petal.style.removeProperty('transform'));stamens.style.removeProperty('transform');stamens.style.removeProperty('opacity');points.forEach(point=>point.querySelector('.botanical-bullet').style.removeProperty('transform'));if(nativeTimeline&&!reduce.matches&&sidebarOverride===null)win.style.removeProperty('--sidebar-fold');pointer=null;items.forEach(el=>{el.style.width='';el.style.height='';el.style.removeProperty('--rendered-icon');});measure();widths.fill(base);});
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
