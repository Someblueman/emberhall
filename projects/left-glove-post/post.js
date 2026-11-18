"use strict";
(() => {
  const W=GloveWorld,$=id=>document.getElementById(id);
  let state=W.start(),route=null,remaining=0;
  const svg="http://www.w3.org/2000/svg";
  const path=[];
  function speech(who,line,aside){$("speaker").textContent=who;$("line").textContent=line;$("aside").textContent=aside;}
  function map() {
    const g=$("map-drawing");g.replaceChildren();
    const draw=(tag,attrs)=>{const n=document.createElementNS(svg,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);g.append(n);return n;};
    for(let n=0;n<5;n++) {
      draw("path",{d:`M35 ${35+n*70}H315M${35+n*70} 35V315`,stroke:"#b6a786","stroke-width":2,fill:"none"});
    }
    draw("path",{d:"M8 8V342M342 8V342",stroke:"#b44e3b","stroke-width":3,"stroke-dasharray":"6 5",fill:"none"});
    for(const p of path)draw("circle",{cx:35+p.x*70,cy:35+p.y*70,r:5,fill:"#b44e3b",opacity:.35});
    draw("rect",{x:164,y:164,width:22,height:22,fill:"#f4e9ce",stroke:"#263b3d","stroke-width":2});
    draw("path",{d:"M162 164l13-11 13 11",fill:"none",stroke:"#263b3d","stroke-width":2});
    draw("path",{d:"M-8 10V-10H7M-8 0H2",transform:`translate(${35+state.x*70} ${35+state.y*70}) scale(${state.turned?-1:1} 1)`,stroke:"#497c91","stroke-width":5,fill:"none"});
    $("coordinates").textContent=`Courier: (${state.x}, ${state.y}). Carried frame: ${state.turned?"reversed":"original"}. Counter and waiting customer: (2, 2), original frame.`;
  }
  function render() {
    const home=W.atCounter(state),delivered=state.delivered;
    $("courier-carried").setAttribute("transform",`scale(${state.turned?-1:1} 1)`);
    $("courier-position").setAttribute("transform",home?"translate(316 287)":`translate(${140+state.x*125} ${260+state.y*15})`);
    $("parcel-close").setAttribute("transform",`translate(292 430) scale(${state.turned?-.7:.7} .7)`);
    $("office").style.opacity=home?"1":".35";
    $("carried-glove").style.display=delivered?"none":"";
    $("worn-glove").style.display=delivered?"":"none";
    $("postmark").style.display=delivered?"":"none";
    if(delivered){$("worn-glove").removeAttribute("hidden");$("postmark").removeAttribute("hidden");}
    else{$("worn-glove").setAttribute("hidden","");$("postmark").setAttribute("hidden","");}
    $("parcel-label").textContent=state.turned?"Right. After all that left.":"Left. Quite definitely left.";
    $("place").textContent=`${home?"At the same counter":"On the town's streets"} · ${state.steps} ${state.steps===1?"step":"steps"} taken${remaining?` · ${remaining} to finish this road`:""}`;
    $("scene-title").textContent=delivered?"A right glove delivered at last":state.turned?"The courier and glove have returned reversed":"A left glove and a bare right hand";
    $("scene-desc").textContent=`${home?"The same clerk and waiting customer are at the counter.":"The courier walks through the town; the customer remains at the counter."} The courier, badge and glove are ${state.turned?"all reversed":"in their original orientation"}.${delivered?" The customer now wears the fitting glove and a red postal stamp says right at last.":""}`;
    $("next").disabled=!remaining||delivered;
    $("offer").disabled=delivered;
    for(const id of ["river","lane"])$(id).disabled=delivered||!home||remaining>0;
    for(const button of document.querySelectorAll("[data-step]"))button.disabled=delivered;
    $("route-note").textContent=delivered?"The post office has made an exception. It will not be putting this in writing.":remaining?`Walk ${remaining} more ${route==="east"?"east":"north"} ${remaining===1?"step":"steps"}. Next step or an arrow button will do.`:home?"A road loops back to this very counter in five steps. The river road has a twist. Try it.":"Keep walking. Five steps in the same direction make a circuit; the map remembers where you are.";
    map();
  }
  function walk(direction) {
    if(state.delivered)return;
    const before=state;state=W.move(state,direction);path.push({x:state.x,y:state.y});
    if(remaining&&direction===route)remaining--;else{remaining=0;route=null;}
    if(state.turned!==before.turned)speech("The courier","“Funny. The badge is on the other side.”","The glove changed with you. The customer didn't go anywhere.");
    else if(W.atCounter(state))speech("The customer",state.turned?"“May I try that one?”":"“Still the other hand, I'm afraid.”",state.turned?"The same counter. The same person. Something you carried is different.":"A whole journey. A very familiar problem.");
    else speech("The courier",direction==="north"?"“Lovely weather for going in circles.”":"“The post must get through.”",remaining?`${remaining} more ${remaining===1?"step":"steps"} along this road.`:"The customer is waiting back at the counter.");
    render();
  }
  function offer() {
    if(!W.atCounter(state)){speech("The courier","“I should probably find the customer first.”","The counter is the little house on the unfolded map.");return;}
    const next=W.deliver(state);
    if(next.delivered){state=next;speech("The clerk","“Right. Well. We have never had a right glove.”","The customer puts it on. The clerk stamps the receipt very, very hard.");}
    else speech("The customer","“It's a lovely glove. I have the other hand.”","The clerk looks at the sign. The courier looks at the road. There may be a way around this.");
    render();
    if(state.delivered)$("reset").focus({preventScroll:true});
  }
  function beginRoute(direction) {
    if(!W.atCounter(state)||state.delivered)return;
    route=direction;remaining=5;
    speech("The courier",direction==="east"?"“I'll take the river road.”":"“Perhaps the ordinary lane will help.”","One step at a time. You can inspect every still, or walk with the arrow buttons.");
    render();$("next").focus();
  }
  $("offer").addEventListener("click",offer);
  $("river").addEventListener("click",()=>beginRoute("east"));
  $("lane").addEventListener("click",()=>beginRoute("north"));
  $("next").addEventListener("click",()=>{if(route&&remaining){walk(route);if(!remaining)$("offer").focus();}});
  for(const button of document.querySelectorAll("[data-step]"))button.addEventListener("click",()=>walk(button.dataset.step));
  $("play").addEventListener("keydown",event=>{
    const keys={ArrowUp:"north",ArrowDown:"south",ArrowLeft:"west",ArrowRight:"east"};
    const target=event.target;
    if(!Object.hasOwn(keys,event.key)||!(target===$("play")||target.hasAttribute("data-step")))return;
    event.preventDefault();walk(keys[event.key]);
  });
  $("reset").addEventListener("click",()=>{
    state=W.start();route=null;remaining=0;path.length=0;
    speech("The clerk","“Left gloves only. Says so above the window.”","The customer has brought no other parcel. Just a cold hand, and a little hope.");
    render();$("offer").focus();
  });
  render();
})();
