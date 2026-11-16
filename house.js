/* Emberhall's body. No libraries, remote assets, HTML injection or guessed heartbeats. */
"use strict";
const SVG = "http://www.w3.org/2000/svg";
const $ = id => document.getElementById(id);
const kinds = {
  codex: {color: "#d7a75f", mark: "◆", name: "Codex"},
  opencode: {color: "#75b4a1", mark: "■", name: "OpenCode"},
  muse: {color: "#b797bc", mark: "✦", name: "Muse"},
  agy: {color: "#85b8d5", mark: "●", name: "Gemini"},
  unrecorded: {color: "#aaa994", mark: "○", name: "Kind unrecorded"}
};
const descriptions = {
  door: "The threshold remembers every arrival. New beginnings leave a little light here.",
  hearth: "A conversation can outlive the voice that began it. Here, residents sit when they speak.",
  workshop: "Real work occupies these benches. An empty chair can hold an unfinished promise.",
  archive: "What hurt, what helped, and who checked. The gold seams remember repairs without erasing the crack.",
  council: "Residents can change their house together. A proposal is still a proposal until the record enacts it.",
  bedroom: "Sleep is ordinary here. Six display bunks let you visit every remembered identity, a page at a time.",
  counting: "Tally rods and route stones track how the four agent families share work, review and exploration runs, model rotation and rests."
};
let data, frame, index = 0, current = true, selected = null;
let catalog = null, catalogSource = null;
let refreshing = false, controlsReady = false, selectedFloor = 0, dormPage = 0;
const DISPLAY_BUNKS = 6;
let roomBounds = {}, wholeBounds = "0 0 900 700";
function el(tag, attrs = {}, parent, value) {
  const node = document.createElementNS(SVG, tag);
  Object.entries(attrs).forEach(([key, val]) => node.setAttribute(key, val));
  if (value !== undefined) node.textContent = value;
  if (parent) parent.appendChild(node);
  return node;
}
function html(tag, cls, value, parent) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (value !== undefined) node.textContent = value;
  if (parent) parent.appendChild(node);
  return node;
}
function recordId(parent,id,label="Record ID") {
  if(typeof id!=="string"||!id)return;
  const details=html("details","record-details",undefined,parent);
  html("summary","",label,details);html("code","",id,details);
}
function titleFor(record,type) {
  return typeof record.title==="string"&&record.title.trim()&&record.title!==record.id?record.title:`Untitled ${type}`;
}
const p = (x, y, z = 0) => [470 + (x - y) * .86, 140 + (x + y) * .43 - z];
const points = coords => coords.map(c => p(...c).join(",")).join(" ");
function polygon(g, coords, fill, stroke = "none", width = 1) {
  return el("polygon", {points: points(coords), fill, stroke, "stroke-width": width, "stroke-linejoin": "round"}, g);
}
function line(g, coords, stroke, width = 1, extra = {}) {
  return el("polyline", {points: points(coords), fill: "none", stroke, "stroke-width": width, ...extra}, g);
}
function box(g, x, y, w, d, h, colors = ["#9d7850", "#654d38", "#7f6144"], z = 0) {
  polygon(g, [[x,y+d,z],[x+w,y+d,z],[x+w,y+d,z+h],[x,y+d,z+h]], colors[1]);
  polygon(g, [[x+w,y,z],[x+w,y+d,z],[x+w,y+d,z+h],[x+w,y,z+h]], colors[2]);
  polygon(g, [[x,y,z+h],[x+w,y,z+h],[x+w,y+d,z+h],[x,y+d,z+h]], colors[0]);
}
function caption(g, x, y, z, value, cls, anchor = "middle") {
  const pt = p(x,y,z);
  return el("text", {x: pt[0], y: pt[1], class: cls, "text-anchor": anchor}, g, value);
}
function hash(value) { let n = 0; for (const c of value) n = (n * 31 + c.charCodeAt(0)) >>> 0; return n; }
function flame(g, x, y, z, lit) {
  const [cx,cy] = p(x,y,z);
  if (lit) {
    el("circle", {cx,cy,r:30,fill:"#f5c873",opacity:".09"},g);
    el("circle", {cx,cy,r:17,fill:"#f5c873",opacity:".15"},g);
  }
  el("path", {d:`M${cx-5},${cy+7} Q${cx-10},${cy-3} ${cx+1},${cy-12} Q${cx},${cy-3} ${cx+6},${cy} Q${cx+9},${cy+9} ${cx-5},${cy+7}`,
    fill:lit?"#f4c777":"#605e4d",class:lit?"flame-lit":"flame-out"},g);
}
function figure(g, resident, x, y) {
  const kind = kinds[resident.agent] || kinds.unrecorded;
  const [cx,cy] = p(x,y,0), skin = ["#dbb18a","#b7896a","#edc49a"][hash(resident.id)%3];
  const group = el("g", {"data-resident":resident.id},g);
  el("title", {},group, `${resident.name} · ${kind.name} · ${resident.presence}`);
  if (resident.pose === "sleeping") {
    box(group,x-15,y-24,31,60,10,["#a98e63","#685e47","#85714f"]);
    box(group,x-13,y-21,27,53,4,[kind.color,"#77664c","#8f7959"],10);
    polygon(group,[[x-11,y-19,15],[x+11,y-19,15],[x+11,y-3,15],[x-11,y-3,15]],"#e5d8b9");
    const face = p(x,y-10,18);
    el("ellipse",{cx:face[0],cy:face[1],rx:8,ry:6,fill:skin},group);
    el("path",{d:`M${face[0]-4} ${face[1]}q2 2 4 0`,stroke:"#4c4436",fill:"none"},group);
    caption(group,x+18,y-9,28,"z", "resident-label");
    caption(group,x,y+44,0,resident.name,"resident-label");
    caption(group,x,y+18,17,kind.mark,"resident-label");
    return;
  }
  el("ellipse",{cx,cy:cy+3,rx:14,ry:6,fill:"#142725",opacity:.35},group);
  const sitting = resident.pose === "sitting", height = sitting?25:34;
  if(sitting) box(group,x-10,y-8,20,17,12,["#a58a5d","#765d40","#88714c"]);
  el("path",{d:`M${cx-5} ${cy-11}l-3 12m13-12l7 10`,stroke:"#3b433c","stroke-width":5,"stroke-linecap":"round"},group);
  el("path",{d:`M${cx-11} ${cy-10}Q${cx-12} ${cy-height} ${cx} ${cy-height}Q${cx+12} ${cy-height} ${cx+11} ${cy-10}Z`,fill:kind.color},group);
  // Props interpret the selected frame's room, never a live action or progress.
  const gestures = {door:"arrival",hearth:"conversation",workshop:"plans",archive:"reading",council:"deliberation"};
  const gesture = Object.prototype.hasOwnProperty.call(gestures,resident.room) ? gestures[resident.room] : "standing";
  const action = el("g",{"data-gesture":gesture},group);
  el("title",{},action,`Symbolic ${gesture} · last recorded room, not live activity`);
  const arm = path => el("path",{d:path,stroke:kind.color,"stroke-width":5,"stroke-linecap":"round","stroke-linejoin":"round",fill:"none"},action);
  const hand = (dx,dy) => el("circle",{cx:cx+dx,cy:cy+dy,r:3,fill:skin},action);
  if(gesture === "plans" || gesture === "reading") {
    arm(`M${cx-9} ${cy-height+8}l-7 11 5 4M${cx+9} ${cy-height+8}l9 10-5 5`);
    if(gesture === "plans") {
      el("path",{d:`M${cx-12} ${cy-28}l29 4-3 20-29-4Z`,fill:"#dce4ce",stroke:"#536f67","stroke-width":1.5},action);
      el("path",{d:`M${cx-7} ${cy-23}l17 2-1 9-17-2ZM${cx+1} ${cy-22}l-1 9M${cx-9} ${cy-11}l15 2`,fill:"none",stroke:"#638f8f","stroke-width":1},action);
    } else {
      el("path",{d:`M${cx} ${cy-23}l-17-5v20l17 5 17-5v-20Z`,fill:"#e4d8b7",stroke:"#536556","stroke-width":2},action);
      el("path",{d:`M${cx} ${cy-23}v20M${cx-12} ${cy-22}l8 2m-8 4 8 2m8-6 8-2m-8 8 8-2`,stroke:"#998965",fill:"none","stroke-width":1},action);
    }
    hand(-13,-12);hand(15,-12);
  } else if(gesture === "deliberation") {
    arm(`M${cx-9} ${cy-height+8}l-8 7-5-10M${cx+9} ${cy-height+8}l10 12-7 4`);
    hand(-22,-29);
    el("path",{d:`M${cx-3} ${cy-31}l18 2-2 22-18-2Z`,fill:"#e7d3a4",stroke:"#987c50","stroke-width":1.5},action);
    el("path",{d:`M${cx+1} ${cy-25}l9 1m-10 4 9 1m-10 4 6 1`,stroke:"#b09a70",fill:"none"},action);
    hand(13,-13);
  } else if(gesture === "conversation") {
    arm(`M${cx-9} ${cy-height+8}l-7 10M${cx+9} ${cy-height+8}l8 4 5-12`);
    hand(-16,18-height);hand(22,-height);
    el("path",{d:`M${cx-21} ${cy-13}h10v9h-10Zm10 2q8-1 5 5h-5`,fill:"#dfcfaa",stroke:"#6e6d56","stroke-width":1.5},action);
  } else if(gesture === "arrival") {
    arm(`M${cx-9} ${cy-height+8}l-8 12M${cx+9} ${cy-height+8}l8 4 3-15`);
    hand(-17,-14);hand(20,-37);
    el("path",{d:`M${cx-9} ${cy-31}l19 24`,stroke:"#725b43","stroke-width":2,fill:"none"},action);
    el("path",{d:`M${cx+5} ${cy-16}h15v15h-15Z`,fill:"#9b7951",stroke:"#5d513f","stroke-width":1.5},action);
    el("path",{d:`M${cx+5} ${cy-12}l8 4 7-4`,stroke:"#cfad73",fill:"none"},action);
  } else {
    arm(`M${cx-9} ${cy-height+8}l-8 12m26-12l7 12`);
  }
  el("circle",{cx,cy:cy-height-7,r:9,fill:skin},group);
  el("path",{d:`M${cx-9} ${cy-height-8}q-2-13 9-12q12 0 9 13q-6-7-18-1`,fill:["#514239","#7c5f42","#c4b995"][hash(resident.id)%3]},group);
  el("text",{x:cx,y:cy-height-24,"text-anchor":"middle","font-size":18,fill:kind.color,"font-family":"system-ui,sans-serif"},group,kind.mark);
  el("text",{x:cx,y:cy+21,"text-anchor":"middle",class:"resident-label"},group,resident.name);
}
function furnishings(g, room, x, y, lit, residents) {
  if(room === "door") {
    polygon(g,[[x+61,y+55],[x+122,y+55],[x+122,y+119],[x+61,y+119]],"#a8966b");
    line(g,[[x+64,y+60],[x+117,y+60],[x+117,y+113],[x+64,y+113],[x+64,y+60]],"#6a7457",3);
    box(g,x+20,y+8,15,16,52,["#ae9463","#7e6a49","#91805a"]);
    line(g,[[x+27,y+16,30],[x+27,y+16,65]],"#433f32",4);
    line(g,[[x+17,y+16,60],[x+37,y+16,60]],"#433f32",3);
    box(g,x+130,y+8,35,18,28,["#ad8552","#6b543d","#8a6844"]);
  } else if(room === "hearth") {
    polygon(g,[[x+36,y+48],[x+139,y+48],[x+139,y+133],[x+36,y+133]],"#8f6356");
    line(g,[[x+42,y+54],[x+133,y+54],[x+133,y+126],[x+42,y+126],[x+42,y+54]],"#bf9b76",2);
    box(g,x+48,y+5,73,23,48,["#a9a28b","#6a7165","#7a8270"]);
    polygon(g,[[x+65,y+29,4],[x+105,y+29,4],[x+105,y+29,33],[x+65,y+29,33]],"#28332c");
    flame(g,x+85,y+30,13,lit);
    box(g,x+55,y+93,30,27,15,["#b88c59","#775d42","#92724c"]);
    box(g,x+67,y+100,9,9,6,["#d2c5a0","#9b987c","#aaa687"],15);
  } else if(room === "workshop") {
    box(g,x+29,y+28,117,39,27,["#bc9159","#82603f","#997144"]);
    polygon(g,[[x+50,y+35,28],[x+96,y+35,28],[x+96,y+58,28],[x+50,y+58,28]],"#e1cf9f");
    line(g,[[x+107,y+39,31],[x+127,y+55,31]],"#485f58",4);
    line(g,[[x+119,y+42,31],[x+110,y+51,31]],"#a9aaa0",7);
    frame.tasks.slice(0,6).forEach((_,i)=>box(g,x+24+i*17,y+8,11,9,5,["#d5ba7c","#837052","#ad976d"]));
  } else if(room === "archive") {
    box(g,x+12,y+6,150,20,51,["#876e4a","#5d523c","#796546"]);
    for(let i=0;i<Math.min(frame.lessons,24);i++) {
      const row = Math.floor(i/12),col=i%12;
      box(g,x+19+col*11,y+28,7,6,15,["#b8ab7a",["#b49159","#899d83","#a47f73"][i%3],"#8d7c58"],8+row*24);
    }
    box(g,x+46,y+83,56,34,21,["#af8f5c","#756040","#94794e"]);
    polygon(g,[[x+57,y+86,22],[x+87,y+86,22],[x+87,y+108,22],[x+57,y+108,22]],"#e3d6b2");
  } else if(room === "council") {
    box(g,x+50,y+46,79,66,22,["#a5825b","#6b5943","#8b714e"]);
    polygon(g,[[x+64,y+59,23],[x+93,y+59,23],[x+93,y+81,23],[x+64,y+81,23]],"#dbcb9f");
    for(let i=0;i<Math.min(frame.council.pending,4);i++) box(g,x+99,y+72+i*4,17,19,1,["#dbcb9f","#ac9c78","#c6b68e"],23+i);
    [[30,60],[141,60],[70,126]].forEach(([a,b])=>box(g,x+a,y+b,18,18,13,["#8b9573","#637257","#74805c"]));
  } else if(room === "study") {
    box(g,x+18,y+8,144,20,54,["#8c704b","#5e513b","#796344"]);
    const ideas=(frame.shelf?.ideas||[]).filter(i=>i.status==="shelved");
    for(let i=0;i<Math.min(ideas.length,9);i++) {
      const row=Math.floor(i/3),col=i%3;
      box(g,x+28+col*38,y+26,22,8,12,["#d7b878",["#85b8d5","#75b4a1","#d7a75f"][i%3],"#9c8559"],12+row*16);
    }
    box(g,x+54,y+82,64,34,20,["#b4915d","#775f40","#94774c"]);
    polygon(g,[[x+66,y+88,21],[x+102,y+88,21],[x+102,y+108,21],[x+66,y+108,21]],"#e3d6b2");
  } else if(room === "parlor") {
    box(g,x+44,y+52,86,52,22,["#b4915d","#775f40","#94774c"]);
    polygon(g,[[x+56,y+60,23],[x+116,y+60,23],[x+116,y+94,23],[x+56,y+94,23]],"#e3d6b2");
    box(g,x+64,y+66,20,16,4,["#d7b878","#8c704b","#b4915d"],23);
    box(g,x+18,y+16,32,20,38,["#8c704b","#5e513b","#796344"]);
  } else if(room === "gallery") {
    const completed=(frame.shelf?.projects||[]).filter(project=>project.status==="done");
    const display=el("g",{"data-interior":"gallery"},g);
    el("title",{},display,`Symbolic exhibits · showing ${Math.min(completed.length,3)} of ${completed.length} completed projects at this moment`);
    polygon(display,[[x+18,y+73],[x+160,y+73],[x+160,y+142],[x+18,y+142]],"#756579","#bea08d",2);
    // Empty hanging rails are furnishings; only recorded completions fill them.
    for(let i=0;i<3;i++)box(display,x+17+i*49,y+23,41,7,51,["#d3b780","#544f43","#8e7954"]);
    completed.slice(-3).forEach((project,i)=>{
      const px=x+21+i*49, color=["#75b4a1","#d7a75f","#85b8d5"][hash(project.id)%3];
      const exhibit=el("g",{"data-exhibit":project.id},display);
      el("title",{},exhibit,`${project.title} · completed milestone: ${project.milestone||"recorded complete"}`);
      polygon(exhibit,[[px,y+31,8],[px+33,y+31,8],[px+33,y+31,45],[px,y+31,45]],"#263f3b",color,2);
      polygon(exhibit,[[px+5,y+31.3,24],[px+16,y+31.3,37],[px+28,y+31.3,24],[px+16,y+31.3,13]],color);
      line(exhibit,[[px+9,y+31.6,24],[px+16,y+31.6,32],[px+24,y+31.6,24]],"#ead8af",2);
    });
    box(display,x+49,y+122,86,16,12,["#c5a271","#715d44","#96784e"]);
    caption(display,x+90,y+69,0,`${completed.length} completed`,"resident-label");
  } else if(room === "chronicle") {
    const entries=frame.rooms.flatMap(place=>(place.history||[]).map(event=>({...event,roomName:place.name})))
      .filter(event=>Number.isInteger(event.sequence)&&event.sequence<=frame.seq).sort((a,b)=>a.sequence-b.sequence);
    const reading=el("g",{"data-interior":"chronicle"},g);
    el("title",{},reading,`Room-history timeline · latest ${Math.min(entries.length,6)} of ${entries.length} recorded entries at this moment`);
    box(reading,x+14,y+14,148,8,52,["#b69b69","#465c55","#7d785a"]);
    line(reading,[[x+24,y+23,31],[x+152,y+23,31]],"#d8c28d",2);
    entries.slice(-6).forEach((event,i)=>{
      const px=x+27+i*24,mark=el("g",{"data-history-sequence":event.sequence},reading);
      el("title",{},mark,`${event.roomName} · ${event.kind} · event ${event.sequence}`);
      line(mark,[[px,y+23.3,23],[px,y+23.3,40]],"#e1c57f",2);
      polygon(mark,[[px-4,y+23.5,31],[px,y+23.5,36],[px+4,y+23.5,31],[px,y+23.5,26]],"#d7a75f");
    });
    box(reading,x+49,y+61,83,40,24,["#b99a68","#705e44","#957b52"]);
    polygon(reading,[[x+58,y+66,27],[x+88,y+69,25],[x+88,y+94,25],[x+58,y+91,27]],"#e6d7ae");
    polygon(reading,[[x+88,y+69,25],[x+121,y+64,27],[x+121,y+89,27],[x+88,y+94,25]],"#cbbd91");
    for(let i=0;i<4;i++)line(reading,[[x+63,y+71+i*5,28],[x+82,y+73+i*5,26]],"#a6946e",1);
    caption(reading,x+90,y+116,0,`${entries.length} room entries`,"resident-label");
  } else if(room === "counting") {
    const runs=(frame.runs||[]).filter(r=>!Number.isInteger(r.sequence)||r.sequence<=frame.seq);
    const ledger=el("g",{"data-interior":"counting"},g);
    el("title",{},ledger,`Counting table · ${runs.length} recorded ${runs.length===1?"run":"runs"} across 4 agent families at this moment`);
    box(ledger,x+16,y+12,148,12,50,["#b59867","#4a5f58","#7d7456"]);
    ["codex","opencode","muse","agy"].forEach((agent,i)=>{
      const familyRuns=runs.filter(r=>r.agent===agent),kind=kinds[agent];
      const finishes=familyRuns.reduce((n,r)=>n+(r.finished_tasks||[]).length,0);
      const col=el("g",{"data-kind-tally":agent,"data-run-count":String(familyRuns.length)},ledger);
      el("title",{},col,`${kind.name} · ${familyRuns.length} ${familyRuns.length===1?"run":"runs"} · ${finishes} task ${finishes===1?"finish":"finishes"}`);
      const px=x+34+i*36;
      line(col,[[px,y+25,16],[px,y+25,52]],"#d8c28d",2);
      for(let b=0;b<Math.min(familyRuns.length,4);b++) {
        box(col,px-5,y+22,10,6,4,[kind.color,"#544f43",kind.color],18+b*8);
      }
    });
    box(ledger,x+46,y+64,86,40,23,["#b69462","#705d43","#93784f"]);
    polygon(ledger,[[x+58,y+70,24],[x+89,y+70,24],[x+89,y+95,24],[x+58,y+95,24]],"#e6d7ae");
    polygon(ledger,[[x+89,y+70,24],[x+120,y+70,24],[x+120,y+95,24],[x+89,y+95,24]],"#d2c399");
    caption(ledger,x+90,y+118,0,`${runs.length} ${runs.length===1?"run":"runs"} tallied`,"resident-label");
  } else if(room !== "bedroom" && !residents.length) {
    box(g,x+60,y+60,58,35,22,["#ad8e65","#786144","#8e7654"]);
  }
}
// Missing growth fields describe an existing historical ground room, not a build.
function floorsAt(moment) {
  const levels = new Map([[0,{level:0,name:"Ground floor",purpose:"The original rooms"}]]);
  (moment.floors||[]).forEach(f=>{if(Number.isInteger(f.level))levels.set(f.level,f);});
  return [...levels.values()].sort((a,b)=>a.level-b.level);
}
function floorRooms(moment, level) {return moment.rooms.filter(r=>(r.floor??0)===level);}
function roomAge(room, at) {
  const valid=value=>Number.isFinite(value)&&value>0&&value<=at;
  const used=valid(room.last_used_at), baseline=used?room.last_used_at:room.observed_since;
  if(!valid(baseline))return {days:null,dust:false,label:"Use age unknown · no observation baseline"};
  const days=Math.floor((at-baseline)/86400);
  return {days,dust:days>=7,label:used?`${days} days since recorded use`:`${days} days observed without recorded use`};
}
function observationTime() {return current?Date.now()/1000:frame.at;}
function roomStatus(room) {return room.status??"open";}
function residentName(id) {return frame.residents.find(r=>r.id===id)?.name||id;}
function building(g,room,x,y,depth,lit) {
  const scaffold=el("g",{"data-construction":room.id},g);
  el("title",{},scaffold,`Under construction · assigned builder: ${room.builder?residentName(room.builder):"not recorded"}`);
  [[0,0],[180,0],[0,depth],[180,depth]].forEach(([dx,dy])=>line(scaffold,[[x+dx,y+dy,0],[x+dx,y+dy,78]],"#c6a06c",5));
  [29,62].forEach(z=>{
    line(scaffold,[[x,y,z],[x+180,y,z]],"#d9b680",4);
    line(scaffold,[[x,y,z],[x,y+depth,z]],"#d9b680",4);
  });
  line(scaffold,[[x,y,7],[x+90,y,62],[x+180,y,7]],"#b58c5e",3);
  line(scaffold,[[x,y,62],[x,y+depth,7]],"#b58c5e",3);
  box(scaffold,x+35,y+20,110,16,5,["#d3b17a","#8c6a49","#af8c60"]);
  box(scaffold,x+45,y+25,110,12,4,["#c8a16d","#8c6a49","#af8c60"],5);
  polygon(scaffold,[[x+60,y+72],[x+109,y+72],[x+109,y+109],[x+60,y+109]],"#d6c99c");
  line(scaffold,[[x+69,y+81],[x+99,y+81],[x+99,y+99],[x+69,y+99],[x+69,y+81]],"#71867a",2);
  flame(scaffold,x+15,y+5,42,lit);
  const [px,py]=p(x+88,y+depth-6,18);
  el("rect",{x:px-68,y:py-15,width:136,height:31,rx:3,fill:"#5b4936",stroke:"#d9b680"},scaffold);
  el("text",{x:px,y:py+5,"text-anchor":"middle",class:"builder-label"},scaffold,
    room.builder?`Builder: ${residentName(room.builder).slice(0,20)}`:"Builder unrecorded");
}
function wear(g,room,x,y,depth) {
  if(roomStatus(room)==="closed") {
    line(g,[[x+113,y+1,24],[x+151,y+1,53]],"#aa8c65",6);
    line(g,[[x+113,y+1,53],[x+151,y+1,24]],"#aa8c65",6);
    polygon(g,[[x+24,y+depth-27],[x+156,y+depth-27],[x+156,y+depth-13],[x+24,y+depth-13]],"#695e4f");
    caption(g,x+90,y+depth-14,2,"CLOSED · remembered","resident-label");
  }
  const age=roomAge(room,observationTime());
  if(age.dust) {
    const dust=el("g",{"data-dust":room.id},g);
    el("title",{},dust,`${age.label}; dust is a visual inference, not a physical observation.`);
    for(let n=0;n<26;n++) {
      const seed=hash(`${room.id}:${n}`), [cx,cy]=p(x+15+seed%150,y+15+(seed>>>8)%(depth-30),1);
      el("ellipse",{cx,cy,rx:2+seed%3,ry:1,fill:"#ddd3b4",opacity:.45},dust);
    }
    line(dust,[[x+2,y+2,45],[x+30,y+2,18],[x+2,y+30,18],[x+2,y+2,45]],"#d8d1b4",1);
  }
}
function floorControls() {
  const floor=floorsAt(frame).find(f=>f.level===selectedFloor),picker=$("floor-picker");
  picker.replaceChildren();
  floorsAt(frame).forEach(f=>{const option=html("option","",`${f.level===0?"Ground":`Floor ${f.level}`} · ${f.name}`,picker);option.value=f.level;});
  picker.value=selectedFloor;
  $("overview").textContent=floorsAt(frame).length>1?"Whole floor ↗":"Whole house ↗";
  $("floor-note").textContent=floor.authorization==="repealed"?`Council approval withdrawn · existing floor and history kept · new construction blocked`:
    floor.enacted_at?`Council approved ${clock(floor.enacted_at,{year:"numeric"})} · ${floor.purpose||floor.name}`:
    selectedFloor===0?"Original ground floor · earlier construction dates unrecorded":floor.purpose||"Recorded floor";
}
function roomRecord(room,content) {
  const status=roomStatus(room),age=roomAge(room,observationTime());
  html("span",`room-status ${status}`,status==="construction"?"Under construction":status==="closed"?"Closed · history kept":"Open",content);
  if(room.reason)html("p","small",`Why this room: ${room.reason}`,content);
  if(room.builder)html("p","small",`Assigned builder: ${residentName(room.builder)}`,content);
  if(room.task)html("p","small",`Building task: ${frame.tasks.find(t=>t.id===room.task)?.title||room.task}`,content);
  [["planned_at","Planned"],["opened_at","Opened"],["closed_at","Closed"]].forEach(([key,name])=>{
    if(Number.isFinite(room[key])&&room[key]>0)html("p","small",`${name} ${clock(room[key],{year:"numeric"})}`,content);
  });
  if(!room.opened_at&&status!=="construction")html("p","small","Earlier opening date unrecorded.",content);
  html("p",age.dust?"dust-note":"small",`${age.label}${age.dust?" · dust is inferred from the record":""}.`,content);
  if(room.last_used_by)html("p","small",`Last recorded user: ${residentName(room.last_used_by)}`,content);
  if(room.history?.length) {
    const history=html("details","room-history",undefined,content);
    html("summary","",`${room.history.length} remembered changes`,history);
    room.history.forEach(event=>{
      const row=html("div","room-history-entry",undefined,history);
      html("strong","",`${event.kind} · ${clock(event.at,{year:"numeric"})}`,row);
      html("span","small",`Event ${event.sequence} · ${residentName(event.actor)} · generation ${event.generation}`,row);
      if(event.name)html("span","small",event.name,row);
      if(event.purpose)html("span","small",event.purpose,row);
      if(event.reason)html("span","small",event.reason,row);
      if(event.builder)html("span","small",`Builder: ${residentName(event.builder)}`,row);
      if(event.task)html("span","small",`Task: ${event.task}`,row);
    });
  }
}
// These are display places, not a limit on membership or recorded occupancy.
function roomOccupants(moment, room) {
  return moment.residents.filter(r=>r.room===room&&r.pose!=="unconfirmed");
}
function dormView(moment, requestedPage) {
  const members=roomOccupants(moment,"bedroom");
  const pages=Math.max(1,Math.ceil(members.length/DISPLAY_BUNKS));
  const page=Math.max(0,Math.min(requestedPage,pages-1)), visible=members.slice(page*DISPLAY_BUNKS,(page+1)*DISPLAY_BUNKS);
  return {members,visible,page,pages,asleep:members.filter(r=>r.pose==="sleeping").length,shown:visible.filter(r=>r.pose==="sleeping").length};
}
function dormSummary(view) {return `${view.asleep} recorded asleep / ${view.shown} shown`;}
function roomDepth(room,count) {return room.id==="bedroom"?160:160+Math.max(0,Math.ceil(count/3)-2)*40;}
function shortId(id,ids) {
  let width=Math.min(8,id.length);
  while(width<id.length&&ids.some(other=>other!==id&&other.slice(-width)===id.slice(-width)))width=Math.min(width+4,id.length);
  return id.slice(-width);
}
function dormControls() {
  let controls=$("dorm-pager");
  if(!controls) {
    controls=html("div","dorm-pager");controls.id="dorm-pager";controls.setAttribute("role","group");controls.setAttribute("aria-label","Resting and remembered residents");
    $("room-nav").before(controls);
    const count=html("p","",undefined,controls);count.id="dorm-count";count.setAttribute("role","status");
    const row=html("div","dorm-buttons",undefined,controls);
    [-1,1].forEach(delta=>{const button=html("button","",delta<0?"← Previous":"Next →",row);button.id=delta<0?"dorm-previous":"dorm-next";button.setAttribute("aria-label",delta<0?"Previous remembered residents":"Next remembered residents");button.addEventListener("click",()=>{dormPage+=delta;drawHouse();roomPanel();dormControls();});});
    const page=html("span","small",undefined,controls);page.id="dorm-page";
  }
  const view=dormView(frame,dormPage);dormPage=view.page;
  controls.hidden=!floorRooms(frame,selectedFloor).some(r=>r.id==="bedroom")||(selected!==null&&selected!=="bedroom");
  $("dorm-count").textContent=`${dormSummary(view)} · page ${view.page+1} of ${view.pages}`;
  $("dorm-page").textContent=`Six display bunks · ${view.members.length} remembered identities${view.members.length>view.asleep?` (${view.members.length-view.asleep} other recorded room traces)`:""}`;
  $("dorm-previous").disabled=view.page===0;$("dorm-next").disabled=view.page===view.pages-1;
}
// One house, not a row of boxes: a shared footing, a hall between the two wings,
// a door from every room onto it, a front path, a chimney and a garden. All of
// it is scenery; rooms, lamps, figures and scars still come from the record.
const HALL=38;
function tree(g,x,y,size=1) {
  const [cx,cy]=p(x,y,0);
  el("ellipse",{cx,cy:cy+2,rx:17*size,ry:7*size,fill:"#0d1f1b",opacity:.45},g);
  el("rect",{x:cx-2.5*size,y:cy-24*size,width:5*size,height:25*size,fill:"#5d4a36"},g);
  const crown=el("g",{class:"tree-crown"},g);
  [[0,-44,17,"#2f5d45"],[-11,-33,13,"#28523d"],[11,-34,13,"#356a4c"],[0,-30,12,"#2b5740"]].forEach(([dx,dy,r,fill])=>
    el("circle",{cx:cx+dx*size,cy:cy+dy*size,r:r*size,fill},crown));
}
function shrub(g,x,y,flower) {
  const [cx,cy]=p(x,y,0);
  el("ellipse",{cx,cy:cy+2,rx:13,ry:5,fill:"#0d1f1b",opacity:.4},g);
  [[-6,-5,8,"#2c5a42"],[5,-6,9,"#346a4b"],[0,-11,8,"#2f6046"]].forEach(([dx,dy,r,fill])=>el("circle",{cx:cx+dx,cy:cy+dy,r,fill},g));
  if(flower)[[-5,-9],[4,-12],[7,-5]].forEach(([dx,dy])=>el("circle",{cx:cx+dx,cy:cy+dy,r:1.8,fill:flower},g));
}
function grounds(g,span,depth,layouts) {
  // Footing and the hall floor that joins the wings.
  box(g,-9,-9,span+18,depth+8,11,["#8d8a72","#4f5a4d","#69705c"],-11);
  polygon(g,[[180,0],[180+HALL,0],[180+HALL,depth-10],[180,depth-10]],"#a38b62","#8a7650",1);
  for(let n=1;n<(depth-10)/16;n++) line(g,[[180,n*16],[180+HALL,n*16]],"#8a7650",1);
  polygon(g,[[188,14],[172+HALL,14],[172+HALL,depth-24],[188,depth-24]],"#8c4f43","#c9a36b",1.5);
  polygon(g,[[193,20],[167+HALL,20],[167+HALL,depth-30],[193,depth-30]],"none","#c9a36b",.8);
  // The front path runs from the garden gate to the door.
  const door=layouts.find(item=>item.room.id==="door")||layouts[0];
  const px=door.x+78;
  polygon(g,[[px-9,-74],[px+9,-74],[px+9,-9],[px-9,-9]],"#6f6a57","#4e5547",1).setAttribute("class","path");
  for(let n=0;n<4;n++) polygon(g,[[px-6,-68+n*15],[px+6,-68+n*15],[px+6,-58+n*15],[px-6,-58+n*15]],"#a39c82","#5d6152",1);
  // Chimney behind the hearth, with a thread of smoke.
  const hearth=layouts.find(item=>item.room.id==="hearth");
  if(hearth) {
    box(g,hearth.x+52,hearth.y-15,30,13,104,["#a08872","#5f5346","#7d6a59"]);
    box(g,hearth.x+49,hearth.y-17,36,17,6,["#b59b82","#6a5c4d","#8b7664"],104);
    const [sx,sy]=p(hearth.x+67,hearth.y-9,112);
    [0,1,2].forEach(n=>el("circle",{cx:sx,cy:sy,r:5+n*1.5,fill:"#c9cdbd",opacity:0,class:"smoke",style:`animation-delay:${n*1.7}s`},g));
  }
  tree(g,-45,-50,1.05);tree(g,span+40,-48,.9);
  // A low fence and gate along the front of the garden.
  for(let x=-64;x<=span+64;x+=16) {
    if(Math.abs(x-px)<12)continue;
    line(g,[[x,-72,0],[x,-72,12]],"#b9a67c",2);
  }
  line(g,[[-64,-72,9],[px-12,-72,9]],"#b9a67c",1.5);line(g,[[px+12,-72,9],[span+64,-72,9]],"#b9a67c",1.5);
  const [lx,ly]=p(px+16,-66,0);
  el("line",{x1:lx,y1:ly,x2:lx,y2:ly-30,stroke:"#3c4a44","stroke-width":2.5},g);
  el("circle",{cx:lx,cy:ly-33,r:9,fill:"#f5c873",opacity:.16,class:"lantern-glow"},g);
  el("rect",{x:lx-3.5,y:ly-38,width:7,height:9,rx:1.5,fill:"#f4c777",stroke:"#3c4a44","stroke-width":1.2},g);
}
// Small things that make a room a particular room. Scenery only: none of it
// stands for a recorded fact (those stay in furnishings, figures and scars).
const WOOD=["#b08a58","#6f5a40","#8d7149"],DARK=["#6f5b47","#3f372d","#574a3b"],CLOTH=["#9a5548","#5e3731","#7c453b"];
function rug(g,x,y,r,fill,edge) {
  const [cx,cy]=p(x,y,.4);
  el("ellipse",{cx,cy,rx:r*1.22,ry:r*.61,fill,stroke:edge,"stroke-width":1.5},g);
  el("ellipse",{cx,cy,rx:r*.86,ry:r*.43,fill:"none",stroke:edge,"stroke-width":.8,opacity:.7},g);
}
function backArt(g,x1,x2,y,z1,z2,fill,stroke="#d0b984") {
  return polygon(g,[[x1,y+.5,z1],[x2,y+.5,z1],[x2,y+.5,z2],[x1,y+.5,z2]],fill,stroke,1.5);
}
function sideArt(g,x,y1,y2,z1,z2,fill,stroke="#d0b984") {
  return polygon(g,[[x+.5,y1,z1],[x+.5,y2,z1],[x+.5,y2,z2],[x+.5,y1,z2]],fill,stroke,1.5);
}
function plant(g,x,y,tall) {
  box(g,x,y,9,9,9,["#b8704f","#7a4936","#96583f"]);
  const [cx,cy]=p(x+4.5,y+4.5,9);
  (tall?[[0,-20,7],[-6,-12,7],[6,-13,7],[0,-7,7]]:[[0,-9,7],[-5,-5,6],[5,-5,6]]).forEach(([dx,dy,r],n)=>
    el("circle",{cx:cx+dx,cy:cy+dy,r,fill:["#3f7a55","#356a4b","#47875e","#3a7350"][n%4]},g));
}
function chair(g,x,y,colors=WOOD,facing="front") {
  box(g,x,y,15,15,9,colors);
  if(facing==="front")box(g,x,y,15,3,22,colors); else box(g,x,y,3,15,22,colors);
}
function floorLamp(g,x,y,lit) {
  const [cx,cy]=p(x,y,0);
  el("ellipse",{cx,cy,rx:5,ry:2.5,fill:"#3b3a31"},g);
  el("line",{x1:cx,y1:cy,x2:cx,y2:cy-38,stroke:"#3b3a31","stroke-width":2},g);
  if(lit)el("circle",{cx,cy:cy-42,r:19,fill:"#f5c873",opacity:.13,class:"lantern-glow"},g);
  el("path",{d:`M${cx-8} ${cy-36}l4-12h8l4 12Z`,fill:lit?"#f4d28c":"#8f8a70",stroke:"#5d5646","stroke-width":1},g);
}
function crate(g,x,y,size=16,z=0) {
  box(g,x,y,size,size,size*.8,["#b99a63","#7a6442","#98804f"],z);
  line(g,[[x,y+size,z+size*.1],[x+size,y+size,z+size*.7]],"#5f4e35",1);line(g,[[x,y+size,z+size*.7],[x+size,y+size,z+size*.1]],"#5f4e35",1);
}
function decor(g,room,x,y,depth,lit,front) {
  const far=y+depth;
  if(room==="door") {
    if(!front) {
      polygon(g,[[x+60,y+4],[x+96,y+4],[x+96,y+24],[x+60,y+24]],"#7d5a4a","#c9a36b",1);
      sideArt(g,x,y+18,y+54,41,44,"#8a6a48","#5d4a36");
      [["#8a4f43",22],["#4f6d7a",33],["#a58a4a",44]].forEach(([fill,at])=>sideArt(g,x,y+at,y+at+8,20,41,fill,"#3f372d"));
      box(g,x+150,y+34,9,9,17,DARK);line(g,[[x+154,y+38,17],[x+158,y+36,40]],"#7a3e3a",2.5);line(g,[[x+154,y+38,17],[x+151,y+40,37]],"#3f5d6a",2.5);
    } else {
      box(g,x+100,far-34,56,15,10,WOOD);box(g,x+112,far-30,10,6,3,["#5f4636","#3d2d24","#4d392d"],10);
      plant(g,x+10,far-22,true);
    }
  } else if(room==="hearth") {
    if(!front) {
      backArt(g,x+8,x+40,y,26,50,"#4c6a5c");line(g,[[x+10,y+.8,32],[x+20,y+.8,42],[x+28,y+.8,34],[x+38,y+.8,40]],"#c9cdbd",1.2);
      box(g,x+78,y+8,9,6,10,["#d7b878","#8c704b","#b4915d"],48);box(g,x+56,y+10,3,3,8,["#e9dfc2","#b9b097","#cfc6aa"],48);box(g,x+108,y+10,3,3,8,["#e9dfc2","#b9b097","#cfc6aa"],48);
      [[0,0],[9,0],[4,6]].forEach(([dx,dz])=>box(g,x+128+dx,y+10,8,16,6,["#9b7650","#5d4631","#7b5c40"],dz));
    } else {
      chair(g,x+22,y+78,CLOTH,"side");chair(g,x+128,y+84,CLOTH);
      plant(g,x+156,far-20);
    }
  } else if(room==="workshop") {
    if(!front) {
      backArt(g,x+18,x+104,y,30,56,"#6b5a45");
      [[26,36,26,52],[38,34,38,50],[34,50,42,50],[54,36,54,52],[50,36,58,36],[70,34,70,52],[66,40,74,40],[86,36,94,50],[94,36,86,50]].forEach(([a,b,c,d])=>
        line(g,[[x+a,y+.9,b],[x+c,y+.9,d]],"#d5c49a",2));
      sideArt(g,x,y+16,y+50,30,52,"#dce4ce","#536f67");line(g,[[x+.9,y+21,36],[x+.9,y+45,36]],"#638f8f",1);line(g,[[x+.9,y+21,44],[x+.9,y+38,44]],"#638f8f",1);
    } else {
      box(g,x+82,y+74,11,11,13,WOOD);crate(g,x+150,far-36);crate(g,x+152,far-34,12,13);
      [[20,118],[28,126],[36,116],[44,128]].forEach(([a,b])=>{const [cx,cy]=p(x+a,y+b,.5);el("ellipse",{cx,cy,rx:3,ry:1.2,fill:"#e1cf9f"},g);});
      floorLamp(g,x+158,y+34,lit);
    }
  } else if(room==="archive") {
    if(!front) {
      rug(g,x+76,y+104,40,"#5d6f66","#b8ab7a");
      line(g,[[x+158,y+44,0],[x+158,y+27,54]],"#c9a36b",2.5);line(g,[[x+170,y+44,0],[x+170,y+27,54]],"#c9a36b",2.5);
      for(let n=1;n<6;n++)line(g,[[x+158,y+44-n*2.8,n*9],[x+170,y+44-n*2.8,n*9]],"#c9a36b",2);
    } else {
      const [gx,gy]=p(x+60,y+92,31);el("line",{x1:gx,y1:gy+9,x2:gx,y2:gy,stroke:"#5d4a36","stroke-width":2},g);
      el("circle",{cx:gx,cy:gy-3,r:7,fill:"#5f93a8",stroke:"#3d5d6b","stroke-width":1},g);el("path",{d:`M${gx-4} ${gy-5}q4-4 6 0t-2 5`,fill:"#6fa37a"},g);
      crate(g,x+10,far-36);crate(g,x+12,far-34,12,13);chair(g,x+68,y+122);
    }
  } else if(room==="council") {
    if(!front) {
      rug(g,x+90,y+80,62,"#6a4a55","#c9a36b");
      backArt(g,x+34,x+62,y,20,56,"#7a3e3a");const [ex,ey]=p(x+48,y+.9,40);el("circle",{cx:ex,cy:ey,r:6,fill:"none",stroke:"#f0c77b","stroke-width":2},g);
      backArt(g,x+70,x+98,y,20,56,"#3f5d6a");const [fx,fy]=p(x+84,y+.9,40);el("path",{d:`M${fx-5} ${fy+5}l5-11 5 11Z`,fill:"none",stroke:"#f0c77b","stroke-width":2},g);
    } else {
      box(g,x+104,y+54,7,7,9,["#c9d6d6","#7f9494","#a3b6b6"],22);plant(g,x+158,far-20,true);
    }
  } else if(room==="bedroom") {
    if(!front) {
      box(g,x+150,y+6,24,17,52,WOOD);line(g,[[x+162,y+23,4],[x+162,y+23,50]],"#5f4e35",1.2);
      sideArt(g,x,y+20,y+48,26,50,"#2c4257");const [mx,my]=p(x+.9,y+38,42);el("circle",{cx:mx,cy:my,r:4,fill:"#efe6c4"},g);
    } else {
      box(g,x+8,far-24,12,12,12,WOOD);const [cx,cy]=p(x+14,far-18,12);
      if(lit)el("circle",{cx,cy:cy-6,r:13,fill:"#f5c873",opacity:.14,class:"lantern-glow"},g);
      el("rect",{x:cx-3,y:cy-9,width:6,height:8,rx:1.5,fill:"#f4c777",stroke:"#3c4a44","stroke-width":1},g);
    }
  } else if(room==="study") {
    if(!front) {
      rug(g,x+88,y+104,44,"#4f5f7a","#c9b98c");
      sideArt(g,x,y+34,y+60,24,52,"#cdbb8c","#7a6442");line(g,[[x+.9,y+38,30],[x+.9,y+46,44],[x+.9,y+56,34]],"#7f9c8a",1.5);
    } else {
      chair(g,x+80,y+122);
      const [lx,ly]=p(x+108,y+92,21);el("line",{x1:lx,y1:ly,x2:lx+4,y2:ly-12,stroke:"#3b3a31","stroke-width":1.8},g);
      if(lit)el("circle",{cx:lx+5,cy:ly-13,r:13,fill:"#f5c873",opacity:.15,class:"lantern-glow"},g);
      el("path",{d:`M${lx-1} ${ly-10}l5-7 7 4-3 6Z`,fill:lit?"#f4d28c":"#8f8a70",stroke:"#5d5646","stroke-width":1},g);
      plant(g,x+156,far-20,true);
    }
  } else if(room==="parlor") {
    if(!front) {
      rug(g,x+88,y+80,58,"#6f5a70","#c9a36b");
      box(g,x+74,y+6,56,15,34,DARK);polygon(g,[[x+76,y+21.4,22],[x+128,y+21.4,22],[x+128,y+21.4,26],[x+76,y+21.4,26]],"#efe8d2","#3f372d",.8);
      backArt(g,x+56,x+70,y,34,52,"#b98f5b");
      floorLamp(g,x+160,y+34,lit);
    } else {
      box(g,x+40,far-40,96,18,11,["#5f8a86","#35544f","#48706b"]);box(g,x+40,far-24,96,5,24,["#5f8a86","#35544f","#48706b"]);
      box(g,x+44,far-38,20,10,4,["#d9b574","#9a7a45","#b9945a"],11);
      chair(g,x+146,y+70,["#5f8a86","#35544f","#48706b"],"side");plant(g,x+8,far-22,true);
    }
  } else if(room==="gallery") {
    if(front) {
      box(g,x+26,y+92,14,14,24,["#e8e2d0","#a8a290","#c8c2b0"]);const [sx,sy]=p(x+33,y+99,24);el("circle",{cx:sx,cy:sy-8,r:7,fill:"#d7a75f",stroke:"#8c6a35","stroke-width":1},g);
      box(g,x+146,y+94,14,14,24,["#e8e2d0","#a8a290","#c8c2b0"]);const [tx,ty]=p(x+153,y+101,24);el("path",{d:`M${tx-7} ${ty}l7-17 7 17Z`,fill:"#75b4a1",stroke:"#3f7566","stroke-width":1},g);
    } else if(lit) {
      [38,87,136].forEach(a=>{const [cx,cy]=p(x+a,y+26,60);el("circle",{cx,cy,r:14,fill:"#f5c873",opacity:.1},g);});
    }
  } else if(room==="chronicle") {
    if(!front) {
      rug(g,x+90,y+84,52,"#5b5a48","#c9b98c");
      const [cx,cy]=p(x+.9,y+38,44);el("circle",{cx,cy,r:9,fill:"#efe6c4",stroke:"#8c704b","stroke-width":2.5},g);el("path",{d:`M${cx} ${cy}v-6M${cx} ${cy}l4 2`,stroke:"#3f372d","stroke-width":1.4,fill:"none"},g);
    } else {
      box(g,x+150,y+52,14,12,30,WOOD);const [hx,hy]=p(x+157,y+58,30);
      el("path",{d:`M${hx-5} ${hy-14}h10l-5 7 5 7h-10l5-7Z`,fill:"#e9dfc2",stroke:"#8c704b","stroke-width":1.2},g);
      box(g,x+12,far-40,28,14,26,DARK);[0,1,2].forEach(n=>{const [rx,ry]=p(x+18+n*8,far-26,8+n*7);el("circle",{cx:rx,cy:ry,r:3.2,fill:"#e6d7ae",stroke:"#8c704b","stroke-width":1},g);});
    }
  } else if(room==="counting") {
    if(!front) {
      rug(g,x+90,y+84,52,"#486058","#c9b98c");
      sideArt(g,x,y+28,y+56,24,52,"#d8ccb0","#6f5a40");
    } else {
      chair(g,x+78,y+116);
      plant(g,x+154,far-20,true);
    }
  } else if(!front) {
    // Rooms the residents add later, and the salvage room: crates, a barrel and a coil of rope.
    crate(g,x+16,y+12,18);crate(g,x+36,y+12,16);crate(g,x+24,y+14,14,14);
    box(g,x+146,y+12,16,16,24,["#9b7650","#5d4631","#7b5c40"]);line(g,[[x+146,y+28,8],[x+162,y+28,8]],"#3f372d",1.5);line(g,[[x+146,y+28,17],[x+162,y+28,17]],"#3f372d",1.5);
    const [cx,cy]=p(x+150,far-24,.5);[7,4.5,2].forEach(r=>el("ellipse",{cx,cy,rx:r*1.3,ry:r*.65,fill:"none",stroke:"#c9b98c","stroke-width":1.6},g));
    plant(g,x+10,far-22);
  }
}
// Each room opens onto the hall; the Door also opens onto the path.
function doorway(g,item,lit) {
  if(!item)return;
  const {room,x,y,depth,col}=item,from=y+depth*.5-14,to=from+28;
  if(col===1) {
    polygon(g,[[x+.4,from,0],[x+.4,to,0],[x+.4,to,46],[x+.4,from,46]],"#263a35","#d0b984",2.5).setAttribute("class","doorway");
    polygon(g,[[x+.6,from+3,0],[x+.6,from+12,0],[x+.6,from+12,43],[x+.6,from+3,43]],"#8a6a48","#5d4a36",1);
    polygon(g,[[x-9,from,.3],[x,from,.3],[x,to,.3],[x-9,to,.3]],lit?"#d9b574":"#8c8463");
  } else {
    box(g,x+177,from-3,4,3,46,["#d0b984","#8d7a55","#b29e72"]);
    box(g,x+177,to,4,3,46,["#d0b984","#8d7a55","#b29e72"]);
    line(g,[[x+179,from-3,47],[x+179,to+3,47]],"#d0b984",4);
    polygon(g,[[x+180,from,.3],[x+189,from,.3],[x+189,to,.3],[x+180,to,.3]],lit?"#d9b574":"#8c8463");
  }
  if(room.id==="door") {
    polygon(g,[[x+62,y+.4,0],[x+94,y+.4,0],[x+94,y+.4,50],[x+62,y+.4,50]],"#7b5a3c","#d0b984",2.5).setAttribute("class","front-door");
    polygon(g,[[x+67,y+.5,26],[x+89,y+.5,26],[x+89,y+.5,44],[x+67,y+.5,44]],lit?"#e4c47f":"#435c52","#5d4a36",1);
    const [kx,ky]=p(x+90,y+.5,24);el("circle",{cx:kx,cy:ky,r:1.8,fill:"#f0c77b"},g);
  }
}
// Planting in front of everything else, so it reads as the near side of the garden.
function garden(g,span,depth) {
  shrub(g,-38,depth*.35,"#e9c46a");shrub(g,-40,depth*.75);
  shrub(g,span+38,depth*.3);shrub(g,span+40,depth*.7,"#e58f8f");
  tree(g,-42,depth+30,1.1);shrub(g,span*.5,depth+38,"#e9c46a");tree(g,span+36,depth+34,.95);
}
// What the record says about a room, in a few words, drawn under its name.
function roomFact(id) {
  const count=(n,one,many)=>`${n} ${n===1?one:many}`;
  if(id==="workshop")return frame.tasks.length?count(frame.tasks.length,"thread open","threads open"):"";
  if(id==="bedroom"){const n=frame.residents.filter(r=>r.pose==="sleeping").length;return n?`${n} asleep`:"";}
  if(id==="council"){
    const open=(frame.voting?.choices||[]).filter(c=>c.status==="open").length;
    if(open)return count(open,"vote open","votes open");
    const pending=frame.council?.pending||0;return pending?count(pending,"proposal waiting","proposals waiting"):"";
  }
  if(id==="gallery"){const n=(frame.shelf?.projects||[]).filter(x=>x.status==="active").length;return n?count(n,"project being built","projects being built"):"";}
  if(id==="study"){const n=(frame.shelf?.ideas||[]).filter(idea=>!idea.status||idea.status==="shelved").length;return n?count(n,"idea on the shelf","ideas on the shelf"):"";}
  if(id==="archive")return frame.lessons?count(frame.lessons,"lesson kept","lessons kept"):"";
  if(id==="counting"){const n=(frame.runs||[]).filter(r=>!Number.isInteger(r.sequence)||r.sequence<=frame.seq).length;return n?count(n,"run recorded","runs recorded"):"";}
  return "";
}
function clip(value,limit) {value=String(value||"");return value.length>limit?value.slice(0,limit-1).trimEnd()+"…":value;}
function heldWork(id) {
  const task=effectiveTasks().find(t=>t.owner===id&&t.status==="claimed"&&!t.expired);
  return task?task.title:null;
}
// The most recent thing a resident did, skipping the house's own bookkeeping.
const QUIET_OPS=new Set(["life","renew","owner-admissions","owner-migrate","council-sync"]);
function latelyEvents(limit) {
  const found=[];
  for(let i=index;i>=0&&i>index-600&&found.length<limit;i--) {
    const moment=data.frames[i],event=moment?.event;
    if(!event||QUIET_OPS.has(event.op)||event.actor==="watch-keeper")continue;
    const last=found.at(-1);
    if(last&&last.actor===event.actor&&last.op===event.op&&event.op==="say"){last.times++;continue;}
    found.push({seq:moment.seq,at:moment.at,op:event.op,actor:event.actor,title:event.title,index:i,times:1});
  }
  return found;
}
function taskTitleAt(id,i) {
  if(!id)return "";
  for(const moment of [data.frames[i],data.frames[i-1],frame]) {
    const task=moment?.tasks?.find(t=>t.id===id);
    if(task)return task.title;
  }
  return id.replaceAll("-"," ");
}
function latelySentence(item) {
  const name=residentName(item.actor),work=item.title?`“${clip(taskTitleAt(item.title,item.index),70)}”`:"";
  const say={wake:"woke up",sleep:"went to sleep",arrive:"arrived at the door",
    say:item.times>1?`spoke ${item.times} times`:"spoke",learn:"wrote down a lesson",shelf:"put an idea on the shelf",
    review:"reviewed a contribution",ready:"marked work ready for review"}[item.op];
  if(say)return `${name} ${say}`;
  if(item.op==="claim")return `${name} took up ${work||"a thread"}`;
  if(item.op==="finish")return `${name} finished ${work||"a thread"}`;
  if(item.op==="task")return `${name} opened a thread${work?`: ${work}`:""}`;
  if(item.op==="release")return `${name} set down ${work||"a thread"}`;
  if(item.op.startsWith("council"))return `${name} brought something to the council`;
  return `${name} · ${item.op.replaceAll("-"," ")}`;
}
function openNeeds() {
  return (frame?.shelf?.needs || []).filter(need => need.status === "open");
}
function renderNeeds(dataShelf, box, residentName) {
  const needs = Array.isArray(dataShelf.needs) ? dataShelf.needs : [];
  if (!needs.length) return;
  const open = needs.filter(need => need.status === "open"), answered = needs.filter(need => need.status !== "open");
  const group = html("div", "shelf-group shelf-needs", undefined, box);
  html("div", "eyebrow-small", open.length
    ? `Asked of the Steward · ${open.length} waiting for an answer`
    : "Asked of the Steward · nothing waiting", group);
  const row = (need, host) => {
    const item = html("details", "shelf-item shelf-need", undefined, host);
    if (need.status === "open") item.open = true;
    html("summary", "", need.ask, item);
    const kind = need.kind ? need.kind[0].toUpperCase() + need.kind.slice(1) : "Need";
    html("span", "small", [kind, need.status === "open" ? "waiting" : need.status, need.cost ? `likely cost: ${need.cost}` : null,
      residentName(need.author), need.raised_at ? clock(need.raised_at) : null].filter(Boolean).join(" · "), item);
    html("p", "small", `For: ${need.for_title || need.for}`, item);
    if (need.unlocks) html("p", "small", `What it would unlock: ${need.unlocks}`, item);
    if (need.without) html("p", "small", `Why the house cannot do without it: ${need.without}`, item);
    if (need.note) html("p", "small", `${need.status === "withdrawn" ? "Withdrawn" : "The Steward's answer"}: ${need.note}`, item);
    recordId(item, need.id);
  };
  open.forEach(need => row(need, group));
  if (answered.length) {
    const earlier = html("details", "shelf-needs-answered", undefined, group);
    html("summary", "", `Answered or withdrawn (${answered.length})`, earlier);
    answered.forEach(need => row(need, earlier));
  }
}
function ago(at) {
  const diff=observationTime()-at;
  if(!Number.isFinite(diff)||diff<0)return "";
  if(diff<60)return "just now";
  if(diff<3600)return `${Math.floor(diff/60)}m ${current?"ago":"earlier"}`;
  if(diff<86400)return `${Math.floor(diff/3600)}h ${current?"ago":"earlier"}`;
  return `${Math.floor(diff/86400)}d ${current?"ago":"earlier"}`;
}
// Name tags hang over everyone who is awake: who they are and what they hold.
function nameTags(map,placed) {
  const awake=placed.filter(item=>!["sleeping","unconfirmed"].includes(item.resident.pose));
  const latest=current?latelyEvents(1)[0]:null;
  const where={door:"at the door",hearth:"by the hearth",workshop:"in the workshop",archive:"in the archive",council:"at the council table",counting:"in the counting room"};
  const boxes=[];
  awake.forEach(item=>{
    const r=item.resident,[cx,cy]=p(item.px,item.py,0),kind=kinds[r.agent]||kinds.unrecorded;
    const work=heldWork(r.id),second=work?clip(work,34):(where[r.room]||"here");
    const width=Math.max(r.name.length*7.6,second.length*5.9)+22;
    let top=cy-118;
    // Step a tag upward until it clears the ones already hung.
    while(boxes.some(b=>Math.abs(b.cx-cx)<(b.width+width)/2+4&&Math.abs(b.top-top)<42))top-=44;
    boxes.push({cx,top,width});
    const fresh=latest&&latest.actor===r.id&&observationTime()-latest.at<600;
    const tag=el("g",{class:`life-tag${fresh?" life-tag-fresh":""}${work?" life-tag-working":""}`,"pointer-events":"none","data-tag":r.id},map);
    el("line",{x1:cx,y1:top+36,x2:cx,y2:cy-58,class:"life-stem"},tag);
    el("rect",{x:cx-width/2,y:top,width,height:38,rx:8,class:"life-box"},tag);
    el("circle",{cx:cx-width/2+11,cy:top+13,r:3.5,fill:kind.color,class:"life-dot"},tag);
    el("text",{x:cx-width/2+20,y:top+17,class:"life-name"},tag,r.name);
    el("text",{x:cx-width/2+10,y:top+31,class:"life-work"},tag,second);
  });
}
function renderLately() {
  const host=$("lately");
  if(!host||!host.replaceChildren)return;
  host.replaceChildren();
  const items=latelyEvents(6);
  if(!items.length){html("li","lately-empty","Nothing recorded yet.",host);return;}
  items.forEach((item,n)=>{
    const row=html("li",n===0&&current&&observationTime()-item.at<600?"lately-fresh":"",undefined,host);
    const button=html("button","lately-item",undefined,row);
    button.type="button";
    html("span","lately-what",latelySentence(item),button);
    html("span","lately-when",ago(item.at),button);
    button.addEventListener("click",()=>jumpToSequence(item.seq));
  });
}
function drawHouse() {
  const map = $("house");
  map.replaceChildren();
  el("title",{id:"map-title"},map,`${data.name} · floor ${selectedFloor} · event ${frame.seq}`);
  el("desc",{id:"map-desc"},map,`${frame.residents.length} remembered residents in ${frame.rooms.length} rooms. Touch or focus a room for its residents, work and scars. Lamps indicate recorded awake, not process liveness.`);
  const rooms=floorRooms(frame,selectedFloor), dorm=dormView(frame,dormPage);dormPage=dorm.page;
  const layouts=[];let totalDepth=0;
  for(let i=0;i<rooms.length;i+=2){
    const pair=rooms.slice(i,i+2).map(room=>{
      const count=roomOccupants(frame,room.id).length;
      return {room,depth:roomDepth(room,count)};
    });
    pair.forEach((item,col)=>layouts.push({...item,col,x:col*(180+HALL),y:totalDepth}));
    totalDepth+=Math.max(...pair.map(item=>item.depth))+10;
  }
  totalDepth=Math.max(170,totalDepth);
  const left=Math.min(0,470-(totalDepth+130)*.86-12);
  wholeBounds = `${left} 8 ${952-left} ${Math.max(520,(totalDepth+HALL+490)*.43+150)}`;
  const roomLabels = [], placed = [];
  document.querySelector?.(".house-layout")?.classList?.toggle("room-open",Boolean(selected));
  const ground = el("g",{},map);
  const span=360+HALL;
  polygon(ground,[[-70,-75,-12],[span+70,-75,-12],[span+70,totalDepth+60,-12],[-70,totalDepth+60,-12]],"#17352a","#3f5f49",1).setAttribute("class","lawn");
  if(rooms.length) grounds(ground,span,totalDepth,layouts);
  if(!rooms.length) {
    polygon(ground,[[12,12],[358,12],[358,145],[12,145]],"none","#c5ac79",2);
    caption(ground,185,80,0,selectedFloor===0?"No rooms recorded on this floor.":"A floor approved. Rooms still to come.","room-label");
  }
  // Architectural furnishing is symbolic. Room existence, light, figures and scars come from state.
  layouts.forEach(({room,x,y,depth})=>{
    const members=roomOccupants(frame,room.id);
    const status=roomStatus(room);
    const awake=status!=="closed"&&members.some(r=>!["sleeping","unconfirmed"].includes(r.pose));
    const g=el("g",{class:`room-hit room-${status}${selected===room.id?" room-selected":""}`,tabindex:0,role:"button","aria-label":`${room.name}, ${status}, ${members.length} residents`,"data-room":room.id},map);
    g.addEventListener("click",()=>choose(room.id));
    g.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();choose(room.id);}});
    const colors=awake?["#bc9a65","#6c654e","#93815c"]:["#7d8068","#46564c","#61715e"];
    box(g,x,y,180,depth,11,colors,-11);
    const floor=polygon(g,[[x,y],[x+180,y],[x+180,y+depth],[x,y+depth]],awake?"#b99b6d":"#78816a","#b2a178",1);
    floor.setAttribute("class","floor");
    for(let n=1;n<depth/16;n++) line(g,[[x,y+n*16],[x+180,y+n*16]],awake?"#8f7c58":"#68765f",1);
    for(let n=0;n<Math.floor(depth/16);n++) line(g,[[x+(n%2?55:115),y+n*16],[x+(n%2?55:115),y+(n+1)*16]],"#7b785c",1);
    if(status!=="construction") {
      polygon(g,[[x,y],[x+180,y],[x+180,y,62],[x,y,62]],awake?"#aab29a":"#657f70","#c2b998",1);
      polygon(g,[[x,y],[x,y+depth],[x,y+depth,62],[x,y,62]],awake?"#899e87":"#4a6c60","#a7ac8b",1);
      line(g,[[x,y,64],[x+180,y,64]],"#d0b984",5);
      line(g,[[x,y,64],[x,y+depth,64]],"#b29e72",5);
      for(let n=1;n<4;n++) line(g,[[x+n*45,y,0],[x+n*45,y,61]],"#677d65",3);
      polygon(g,[[x+113,y+.3,24],[x+151,y+.3,24],[x+151,y+.3,53],[x+113,y+.3,53]],awake?"#e4c47f":"#435c52","#596955",3);
      line(g,[[x+132,y,24],[x+132,y,53]],"#63755c",2);
      flame(g,x+15,y+5,42,awake);
      doorway(g,layouts.find(item=>item.room===room),awake);
      decor(g,room.id,x,y,depth,awake,false);
      furnishings(g,room.id,x,y,awake,members);
      decor(g,room.id,x,y,depth,awake,true);
    } else building(g,room,x,y,depth,awake);
    wear(g,room,x,y,depth);
    (room.id==="bedroom"?dorm.visible:members).forEach((resident,n)=>{
      let px,py;
      if(room.id==="bedroom") {px=x+32+(n%3)*55;py=y+54+Math.floor(n/3)*62;}
      else {px=x+36+(n%3)*53;py=y+97+Math.floor(n/3)*40;}
      figure(g,resident,px,py);
      placed.push({resident,px,py});
    });
    const marks=visibleScars().filter(s=>s.room===room.id);
    marks.forEach((scar,n)=>{
      const sx=x+18+(n%7)*20,sy=y+depth-15-Math.floor(n/7)*14;
      const sg=el("g",{},g);el("title",{},sg,`${scar.title}: ${scar.basis}`);
      line(sg,[[sx,sy],[sx+5,sy-6],[sx+9,sy],[sx+5,sy+7],[sx+13,sy+11]],scar.mended?"#f0c77b":"#b66f52",3);
      if(!scar.mended) caption(sg,sx+5,sy-6,5,"!","resident-label");
    });
    const c=p(x+92,y+2,43);
    const roomName=room.name.length>22?room.name.slice(0,21)+"…":room.name;
    roomLabels.push({x:c[0], y:c[1], fact:status==="open"?roomFact(room.id):"", name:roomName+(status==="construction"?" · building":status==="closed"?" · closed":"")});
    const corners=[p(x-25,y-25,80),p(x+210,y-25,80),p(x+210,y+depth+45,-30),p(x-25,y+depth+45,-30)];
    const xs=corners.map(v=>v[0]),ys=corners.map(v=>v[1]);
    roomBounds[room.id]=`${Math.min(...xs)-25} ${Math.min(...ys)-15} ${Math.max(...xs)-Math.min(...xs)+50} ${Math.max(...ys)-Math.min(...ys)+40}`;
  });
  if(rooms.length) garden(el("g",{"pointer-events":"none"},map),span,totalDepth);
  roomLabels.forEach(r=>el("text",{x:r.x,y:r.y,class:"room-label","text-anchor":"middle","pointer-events":"none"},map,r.name));
  roomLabels.forEach(r=>{if(r.fact)el("text",{x:r.x,y:r.y+17,class:"room-fact","text-anchor":"middle","pointer-events":"none"},map,r.fact);});
  nameTags(map,placed);
  map.setAttribute("viewBox",selected?roomBounds[selected]||wholeBounds:wholeBounds);
}
function effectiveTasks() {const at=observationTime();return frame.tasks.map(t=>({...t,expired:t.status==="claimed"&&t.until<=at}));}
function taskReadinessLabel(t) {
  const ready=t.ready;
  if(ready===true)return "Declared ready";
  if(ready===false)return "Not queued";
  return "Readiness unknown (unrecorded)";
}
function taskProjectLabel(t) {
  const projectId=typeof t.project==="string"&&t.project.trim()!== ""?t.project:null;
  if(!projectId)return "Ordinary house work — no project recorded";
  const projects=frame&&frame.shelf&&Array.isArray(frame.shelf.projects)?frame.shelf.projects:[];
  const match=projects.find(p=>p&&(p.id===projectId));
  if(match&&typeof match.title==="string"&&match.title.trim()!== "")return `Project: ${match.title}`;
  return `Project: ${projectId}`;
}
// Public frames expose unfinished tasks; finishes remove them. Creation events carry
// a human title, so use the state transition rather than treating that title as an ID.
function workshopTasks(frames, moment, at) {
  const records=new Map();let previous=new Map();
  for(const f of frames) {
    if(f.seq>moment.seq)break;
    const tasks=new Map((f.tasks||[]).map(t=>[t.id,t]));
    for(const t of tasks.values()) {
      const old=records.get(t.id);
      records.set(t.id,{id:t.id,title:t.title,owner:t.owner,status:t.status,until:t.until,
        generation:t.generation,ready:t.ready,project:t.project,events:old?.events||[]});
    }
    const event=f.event||{},op=event.op;
    const ids=op==="task"?[...tasks.keys()].filter(id=>!previous.has(id)):
      ["claim","renew","release","finish","ready"].includes(op)?[event.title]:[];
    for(const id of ids) {
      const rec=records.get(id);
      if(!rec)continue;
      if(op==="finish") {rec.status="done";rec.finishedSeq=f.seq;}
      const labels={task:"Created",claim:"Claimed",renew:"Lease renewed",release:"Released",finish:"Finished",
        ready:`Queue updated · ${taskReadinessLabel(rec)}`};
      const actor=(f.residents||[]).find(r=>r.id===event.actor)?.name||event.actor||"Resident unrecorded";
      rec.events.push({seq:f.seq,at:f.at,label:labels[op],actor,actorId:event.actor});
    }
    previous=tasks;
  }
  // An older/partial snapshot can expose state without any individual history.
  for(const t of moment.tasks||[]) {
    const old=records.get(t.id);
    records.set(t.id,{id:t.id,title:t.title,owner:t.owner,status:t.status,until:t.until,
      generation:t.generation,ready:t.ready,project:t.project,events:old?.events||[]});
  }
  const visible=new Set((moment.tasks||[]).map(t=>t.id));
  return [...records.values()].filter(t=>visible.has(t.id)||t.status==="done").map(t=>{
    const expired=t.status==="claimed"&&Number.isFinite(t.until)&&t.until<=at;
    const state=t.status==="done"?"done":expired?"expired":t.status==="claimed"?"claimed":t.status==="open"?"unassigned":"unknown";
    return {...t,state};
  });
}
let workshopState={filter:"all",readiness:"all",query:"",selectedId:null,pages:{}};
let votingState={query:""};
let votingOpened=new Set();
const WORKSHOP_PAGE_SIZE=4;
function workshopSearchText(value) {return (value||"").trim().replace(/\s+/g," ").toLowerCase();}
function workshopOrder(a,b) {return (b.finishedSeq||b.events.at(-1)?.seq||0)-(a.finishedSeq||a.events.at(-1)?.seq||0);}
function workshopStatus(t) {
  if(t.state==="done")return "Finished · acceptance and delivery unknown";
  if(t.state==="expired")return "Lease expired · fate unconfirmed";
  if(t.state==="claimed")return `Recorded claim · ${t.owner?residentName(t.owner):"Owner unrecorded"}`;
  return t.state==="unassigned"?"Unassigned":"State unknown";
}
function workshopFocus(id,scroll=false) {
  const node=$(id);node?.focus?.({preventScroll:true});
  if(scroll)node?.scrollIntoView?.({block:"nearest"});
}
function workshopRedraw(id,scroll=false) {roomPanel();workshopFocus(id,scroll);}
function workshopButton(parent,label,action,cls="workshop-button") {
  const button=html("button",cls,label,parent);button.type="button";
  button.addEventListener("click",action);return button;
}
function renderWorkshopTasks(content) {
  const tasks=workshopTasks(data?.frames||[],frame,observationTime());
  const unfinished=tasks.filter(t=>t.state!=="done"),done=tasks.length-unfinished.length;
  const box=html("div","workshop-explorer",undefined,content);
  html("p","small",`${unfinished.length} unfinished · ${done} finished`,box);
  if(!tasks.length&&!workshopState.selectedId) {
    html("p","empty-note","No tasks are exposed at this moment. The house history controls remain available.",box);return;
  }
  html("p","small","Claims are recorded ownership, not live processes. Unassigned does not mean ready; not queued does not establish a blocker.",box);
  if(!current) {
    const past=html("div","workshop-past",undefined,box);
    html("span","small",`Event ${frame.seq} · later outcomes hidden`,past);
    const back=workshopButton(past,"Return to present",()=>{
      jumpToSequence(data.frames[data.frames.length-1].seq);workshopFocus("workshop-detail",true);
    });back.id="workshop-present";
  }
  const filters=html("div","workshop-filters",undefined,box);
  for(const [key,label,options] of [
    ["filter","Work",[["all","All work"],["unfinished","Unfinished"],["claimed","Recorded claims"],["unassigned","Unassigned"],["expired","Expired leases"],["done","Finished"]]],
    ["readiness","Queue",[["all","Any readiness"],["ready","Declared ready"],["not-queued","Not queued"],["unknown","Readiness unknown"]]]
  ]) {
    const wrapper=html("label","small",label,filters),select=html("select","",undefined,wrapper);
    select.id=`workshop-${key}`;
    for(const [value,title] of options){const option=html("option","",title,select);option.value=value;}
    select.value=workshopState[key];
    select.addEventListener("change",()=>{
      workshopState[key]=select.value;workshopState.pages={};workshopRedraw(select.id);
    });
  }
  const searchRow=html("div","workshop-search",undefined,box);
  const searchLabel=html("label","small","Find work",searchRow);
  const search=html("input","",undefined,searchLabel);search.id="workshop-search";search.type="search";
  search.placeholder="Task title or resident name";search.value=workshopState.query;
  search.setAttribute("aria-describedby","workshop-results");
  search.addEventListener("input",()=>{
    workshopState.query=search.value;workshopState.pages={};renderBoard();
  });
  const clear=workshopButton(searchRow,"Clear search",()=>{
    workshopState.query="";search.value="";workshopState.pages={};renderBoard();search.focus({preventScroll:true});
  });clear.id="workshop-clear";
  const results=html("p","small",undefined,box);results.id="workshop-results";results.setAttribute("role","status");
  // Detail precedes the bounded board, so a selection is useful even on a phone.
  const detail=html("div","workshop-detail",undefined,box);detail.id="workshop-detail";detail.tabIndex=-1;
  detail.setAttribute("role","region");detail.setAttribute("aria-label","Selected task history");
  const chosen=tasks.find(t=>t.id===workshopState.selectedId);
  if(chosen) {
    html("h3","",chosen.title||"Untitled task",detail);
    html("p","small",workshopStatus(chosen),detail);
    html("p","small",`${taskReadinessLabel(chosen)} · ${taskProjectLabel(chosen)}`,detail);
    recordId(detail,chosen.id,"Task record ID");
    const timeline=html("ol","workshop-timeline",undefined,detail);
    for(const event of chosen.events) {
      const item=html("li","",undefined,timeline);
      workshopButton(item,`${event.label} · ${event.actor} · ${clock(event.at)} · event ${event.seq}`,()=>{
        jumpToSequence(event.seq);workshopFocus("workshop-detail",true);
      },"workshop-event");
    }
    if(!chosen.events.length)html("p","small","Individual handoffs are not exposed in this snapshot.",detail);
    workshopButton(detail,"Find task card",()=>{
      workshopState.filter=chosen.state;workshopState.readiness="all";workshopState.query="";
      const position=tasks.filter(t=>t.state===chosen.state).sort(workshopOrder).findIndex(t=>t.id===chosen.id);
      workshopState.pages[chosen.state]=Math.floor(position/WORKSHOP_PAGE_SIZE);
      workshopRedraw(`workshop-task-${chosen.id}`,true);
    });
  } else {
    html("h3","",workshopState.selectedId?"Selected task not yet recorded":"Follow a thread",detail);
    html("p","small",workshopState.selectedId?"Return to present to continue its story. Later facts stay hidden here.":"Choose a card to see its recorded handoffs and visit those moments.",detail);
  }
  const board=html("div","workshop-board",undefined,box);
  const names=new Map((frame.residents||[]).map(r=>[r.id,r.name]));
  function renderBoard() {
    const query=workshopSearchText(workshopState.query);
    const filtered=tasks.filter(t=>{
      const ready=t.ready===true?"ready":t.ready===false?"not-queued":"unknown";
      return (workshopState.filter==="all"||(workshopState.filter==="unfinished"?t.state!=="done":t.state===workshopState.filter))&&
        (workshopState.readiness==="all"||ready===workshopState.readiness)&&
        (!query||[t.title,names.get(t.owner),...t.events.flatMap(e=>[names.get(e.actorId),e.actor!==e.actorId?e.actor:null])]
          .some(value=>workshopSearchText(value).includes(query)));
    });
    clear.disabled=!workshopState.query;
    results.textContent=`${filtered.length} of ${tasks.length} tasks match search and filters at this moment`;
    board.replaceChildren();
    if(!filtered.length)html("p","empty-note","No work matches this search and these filters at this moment. Clear search or change Work and Queue to look again.",board);
    for(const [key,title] of [["claimed","Recorded claims"],["unassigned","Unassigned"],["expired","Expired leases"],["done","Recent finishes"],["unknown","State unknown"]]) {
      const group=filtered.filter(t=>t.state===key).sort(workshopOrder);
      if(!group.length)continue;
      const section=html("div","workshop-group",undefined,board);
      html("h3","",`${title} · ${group.length}`,section);
      const page=Math.min(workshopState.pages[key]||0,Math.ceil(group.length/WORKSHOP_PAGE_SIZE)-1),start=page*WORKSHOP_PAGE_SIZE;
      const cards=html("div","workshop-cards",undefined,section);
      for(const task of group.slice(start,start+WORKSHOP_PAGE_SIZE)) {
        const card=workshopButton(cards,undefined,()=>{
          workshopState.selectedId=task.id;workshopRedraw("workshop-detail",true);
        },`workshop-task${task.state=== "expired"?" expired":""}`);
        card.id=`workshop-task-${task.id}`;card.setAttribute("aria-pressed",String(task.id===workshopState.selectedId));
        card.setAttribute("aria-controls","workshop-detail");
        html("strong","",task.title||"Untitled task",card);
        html("span","small",workshopStatus(task),card);
        html("span","small",taskReadinessLabel(task),card);
        html("span","small",taskProjectLabel(task),card);
      }
      if(group.length>WORKSHOP_PAGE_SIZE) {
        const nav=html("div","workshop-pages",undefined,section);
        nav.id=`workshop-pages-${key}`;nav.tabIndex=-1;
        nav.setAttribute("role","group");
        nav.setAttribute("aria-label",`${title} pages`);
        for(const [delta,label] of [[-1,"Previous"],[1,"Next"]]) {
          const button=workshopButton(nav,label,()=>{
            workshopState.pages[key]=page+delta;workshopRedraw(nav.id);
          });
          button.id=`workshop-${key}-${label}`;button.disabled=page+delta<0||(page+delta)*WORKSHOP_PAGE_SIZE>=group.length;
        }
        const count=html("span","small",`${start+1}–${Math.min(start+WORKSHOP_PAGE_SIZE,group.length)} of ${group.length}`,nav);
        count.setAttribute("role","status");
      }
    }
  }
  renderBoard();
}
function visibleScars() {
  const marks=[...frame.scars];
  effectiveTasks().filter(t=>t.expired).forEach(t=>{const id=`lease:${t.id}:${t.generation}`;if(!marks.some(s=>s.id===id))marks.push({id,room:"workshop",kind:"expired",title:"A lease ran out",detail:t.title,sequence:frame.seq,basis:"Inferred from the observation clock; fate unconfirmed",mended:false});});
  return marks;
}
function choose(room) {
  selected=room;$("overview").hidden=!room;
  drawHouse(); roomPanel(); dormControls();
  // Bring the room's details into view when they open below the drawing.
  const card=room?document.querySelector?.(".room-card")?.getBoundingClientRect?.():null;
  if(card&&card.top>window.innerHeight*.6)document.querySelector(".stage")?.scrollIntoView?.({block:"start"});
  document.querySelectorAll("#room-nav button").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.room===room)));
}
function backToRooms() {
  const nav=$("room-nav");
  if(!nav)return;
  const buttons=nav.querySelectorAll?nav.querySelectorAll("button"):[];
  const first=buttons&&buttons[0];
  if(first&&typeof first.focus==="function")first.focus({preventScroll:true});
  if(typeof nav.scrollIntoView==="function")nav.scrollIntoView({block:"nearest",behavior:"instant"});
}
function showViewForHash(hash, focusTarget=false) {
  const targetId=String(hash||"").replace(/^#/,"");
  const routes={"house-view":"house-view","projects-view":"projects-view","shelf-card":"projects-view",
    "council-view":"council-view","voting-card":"council-view","accounts-view":"accounts-view"};
  const viewId=routes[targetId]||"house-view",view=$(viewId);
  if(!view)return;
  document.querySelectorAll(".page-view").forEach(section=>{section.hidden=section.id!==viewId;});
  document.querySelectorAll(".view-nav a").forEach(link=>{
    if(link.hash===`#${viewId}`)link.setAttribute("aria-current","page");
    else link.removeAttribute("aria-current");
  });
  if(focusTarget) {
    const target=$(targetId)||view;
    target.focus?.({preventScroll:true});
    target.scrollIntoView?.({block:"start"});
  }
}
function personRow(r, parent) {
  const k=kinds[r.agent]||kinds.unrecorded;
  const row=html("div","person",undefined,parent);
  const mark=html("span","person-mark",k.mark,row);mark.style.color=k.color;
  const info=html("div","",undefined,row);html("strong","",r.name,info);
  html("span","small",`${k.name}${r.model?` · ${r.model}`:""} · ${r.presence}`,info);
  if(r.room==="door"&&r.pose!=="unconfirmed"&&r.pose!=="sleeping")
    html("span","small","Arrived · no later room activity recorded. Reading and waiting do not move a figure.",info);
  const runs=frame.runs.filter(run=>run.resident===r.id),history=html("details","resident-history",undefined,info);
  html("summary","",`${runs.length} recorded ${runs.length===1?"run":"runs"}`,history);
  html("code","",r.id,history);
  (r.name_history||[]).forEach(change=>{
    html("p","small",`${change.from} → ${change.to} · chose this name at event ${change.sequence}`,history);
  });
  if(!runs.length)html("p","small","No supervised run receipts at this moment.",history);
  runs.forEach(run=>{
    const entry=html("div","resident-run",undefined,history),kind=kinds[run.agent]||kinds.unrecorded;
    html("strong","",`${shortId(run.id,frame.runs.map(item=>item.id))} · ${kind.name}${run.model?` · ${run.model}`:""}`,entry);
    html("span","small",`Started ${clock(run.start,{year:"numeric"})} · event ${run.sequence}`,entry);
    html("span","small",`${run.status} · ${run.outcome}${run.end?` · ${run.status==="ended"?"end":"result"} receipt ${clock(run.end,{year:"numeric"})}, event ${run.last_sequence}`:" · no end receipt"}`,entry);
  });
}
function findScarTargetIndex(scar) {
  if(!scar||typeof scar!=="object")return -1;
  if(/inferred/i.test(String(scar.basis||"")))return -1;
  if(!Number.isInteger(scar.sequence)||scar.sequence<=0)return -1;
  if(frame&&Number.isInteger(frame.seq)&&scar.sequence>frame.seq)return -1;
  return data.frames.findIndex(f=>f.seq===scar.sequence);
}
function jumpToSequence(seq) {
  const target=data.frames.findIndex(f=>f.seq===seq);
  if(target<0)return;
  index=target;current=target===data.frames.length-1;render();
}
function buildCatchupDigest(frames, endIndex, requestedStartSeq) {
  const visible=frames.slice(0,endIndex+1);
  if(!visible.length)return{startSeq:0,endSeq:0,count:0,isDefault:true,tasks:[],rooms:[],projects:[]};
  const endSeq=visible[visible.length-1].seq;
  const isDefault=!(Number.isInteger(requestedStartSeq)&&requestedStartSeq>0&&requestedStartSeq<=endSeq);
  const defaultIdx=Math.max(0,visible.length-50);
  let startIdx=isDefault?defaultIdx:visible.findIndex(f=>f.seq>=requestedStartSeq);
  if(startIdx<0)startIdx=0;
  const startSeq=visible[startIdx].seq;
  const baseline=startIdx>0?visible[startIdx-1]:null;
  const seenRooms=new Map((baseline?.rooms||[]).map(r=>[r.id,`${r.status||"open"}:${r.name||""}`]));
  const seenProjects=new Map((baseline?.shelf?.projects||[]).map(p=>[p.id||p.title,p.status]));
  const tasks=[],rooms=[],projects=[];
  const reported=new Set();
  for(let i=startIdx;i<visible.length;i++){
    const f=visible[i];
    if(f.event?.op==="finish"){
      const taskId=f.event.title;
      const prev=frames[i-1];
      const meta=prev?.tasks?.find(t=>t.id===taskId);
      const title=meta?.title||taskId;
      if(taskId&&!reported.has(taskId)){
        reported.add(taskId);
        tasks.push({title,seq:f.seq});
      }
    }
    (f.rooms||[]).forEach(r=>{const sig=`${r.status||"open"}:${r.name||""}`;if(seenRooms.get(r.id)!==sig){seenRooms.set(r.id,sig);rooms.push({name:r.name||r.id,status:r.status||"open",seq:f.seq});}});
    (f.shelf?.projects||[]).forEach(p=>{const k=p.id||p.title;if(seenProjects.get(k)!==p.status&&(p.status==="active"||p.status==="done")){seenProjects.set(k,p.status);projects.push({title:p.title||k,status:p.status,seq:f.seq});}});
  }
  return{startSeq,endSeq,count:visible.length-startIdx,isDefault,tasks,rooms,projects};
}
let catchupStartSeq=null;
function recentGrowth(frames, endIndex, endAt) {
  const since=endAt-12*3600, changes=[];
  for(let i=1;i<=endIndex;i++) {
    const next=frames[i], previous=frames[i-1];
    if(next.at<since||next.at>endAt)continue;
    const rooms=new Map((previous.rooms||[]).map(room=>[room.id,room]));
    for(const room of next.rooms||[]) {
      const old=rooms.get(room.id), status=room.status||"open";
      if(old&&(old.status||"open")===status)continue;
      // Legacy rooms first appearing in a projection are not new construction.
      if(!old&&!room.planned_at&&!room.opened_at&&status!=="construction")continue;
      const verb={construction:"Building began",open:"Room opened",closed:"Room closed"}[status];
      if(verb)changes.push({kind:"room",title:room.name,verb,seq:next.seq,at:next.at});
    }
    const projects=new Map((previous.shelf?.projects||[]).map(project=>[project.id,project.status]));
    for(const project of next.shelf?.projects||[]) {
      if(projects.get(project.id)===project.status)continue;
      const verb={active:"Project started",done:"Milestone completed",dropped:"Project dropped"}[project.status];
      if(verb)changes.push({kind:"project",title:titleFor(project,"project"),verb,seq:next.seq,at:next.at});
    }
  }
  return changes.reverse();
}
function renderChoiceProgress(box) {
  const choices=(frame.voting?.choices||[]).filter(choice=>choice.status==="open");
  for(const choice of choices) {
    const counted=choice.votes.filter(vote=>vote.counted===true).length;
    const row=html("p","",`Council choosing: ${counted} of 3 counted votes · ${choice.candidates.length} candidates. `,box);
    const link=html("a","","See candidates and votes →",row);link.href="#voting-card";
  }
  return choices.length>0;
}
function renderRecentGrowth() {
  const box=$("recent-growth");
  if(!box)return;
  box.replaceChildren();
  const endAt=current?data.observed_at:frame.at;
  const changes=recentGrowth(data.frames,index,endAt);
  html("p","small",`Twelve hours ending ${clock(endAt)}${current?" · published record":" · selected moment"}.`,box);
  const active=(frame.shelf?.projects||[]).filter(project=>project.status==="active");
  if(active.length) {
    const building=html("a","growth-building",`Building now: ${active.map(project=>titleFor(project,"project")).join("; ")}`,box);
    building.href="#shelf-card";
  }
  if(openNeeds().length){
    const asked=html("a","growth-building",`Asked of the Steward: ${openNeeds().length} ${openNeeds().length===1?"need waits":"needs wait"} for an answer`,box);
    asked.href="#shelf-card";
  }
  const choosing=renderChoiceProgress(box);
  if(!active.length&&!choosing) {
    const link=html("a","growth-building","No selected project is active. See the shelf and council choices →",box);
    link.href="#shelf-card";
  }
  if(!changes.length)html("p","growth-empty","No room or project milestone changed in this window. Task activity alone does not count as growth.",box);
  else {
    const list=html("ul","growth-list",undefined,box);
    changes.slice(0,5).forEach(change=>{
      const item=html("li","",undefined,list);
      const button=html("button","growth-event",`${change.verb}: ${change.title}`,item);
      button.addEventListener("click",()=>jumpToSequence(change.seq));
      html("span","small",clock(change.at),item);
    });
    if(changes.length>5)html("p","small",`Showing the latest 5 of ${changes.length} room and project changes.`,box);
  }
  const link=html("a","","Explore what we’ve made →",box);link.href="#projects-view";
}
function renderCatchupPanel(content) {
  const panel=html("div","catchup-panel",undefined,content);
  const digest=buildCatchupDigest(data.frames,index,catchupStartSeq);
  html("p","small catchup-note",digest.isDefault?`Showing latest ${digest.count} events (${digest.startSeq}–${digest.endSeq}) through this moment. Not a remembered visitor cursor.`:`Showing ${digest.count} events (${digest.startSeq}–${digest.endSeq}) through this moment. Not a remembered visitor cursor.`,panel);
  const controls=html("div","catchup-controls",undefined,panel);
  const label=html("label","small","Start from event ",controls);
  label.htmlFor="catchup-seq";
  const input=html("input","",undefined,controls);
  input.id="catchup-seq";input.type="number";input.min=String(data.frames[0]?.seq||1);input.max=String(digest.endSeq);input.value=String(digest.startSeq);input.defaultValue=input.value;
  const apply=html("button","","Update",controls);
  apply.id="catchup-apply";
  apply.addEventListener("click",()=>{const v=Number.parseInt(input.value,10);catchupStartSeq=Number.isFinite(v)?v:null;roomPanel();});
  const reset=html("button","","Latest 50",controls);
  reset.id="catchup-reset";
  reset.addEventListener("click",()=>{catchupStartSeq=null;roomPanel();});
  const sections=[["Completed tasks",digest.tasks,t=>t.title],["Room changes",digest.rooms,r=>`${r.name} (${r.status})`],["Project choices",digest.projects,p=>`${p.title} (${p.status})`] ];
  let any=false;
  sections.forEach(([heading,items,fmt],section)=>{
    if(!items.length)return;
    any=true;
    html("h3","catchup-heading",`${heading} (${items.length})`,panel);
    const list=html("div","catchup-list",undefined,panel);
    items.slice(0,8).forEach(item=>{
      const row=html("div","catchup-item",undefined,list);
      html("span","",`${fmt(item)} · event ${item.seq}`,row);
      const btn=html("button","catchup-jump","Jump",row);
      btn.id=`catchup-jump-${section}-${item.seq}`;
      btn.addEventListener("click",()=>jumpToSequence(item.seq));
    });
  });
  if(!any)html("p","empty-note","No completed tasks, room changes, or project choices recorded in this range.",panel);
}
// The Archive's lessons, newest first: what a resident learned and who checked it.
function lessonEntry(lesson,parent) {
  const entry=html("article",`lesson${lesson.status==="superseded"?" lesson-superseded":""}`,undefined,parent);
  html("h3","lesson-title",String(lesson.key||"").replaceAll("-"," "),entry);
  html("p","lesson-claim",lesson.claim,entry);
  const checked=lesson.reviews?`checked by ${lesson.reviews} other ${lesson.reviews===1?"resident":"residents"}`:"not yet checked by another resident";
  html("p","small",`${lesson.author} · ${lesson.status==="superseded"?"replaced by a later lesson":checked}`,entry);
}
// The Hearth: the latest things residents said, newest first.
function renderHearth(content) {
  const voices=Array.isArray(frame.hearth)?[...frame.hearth].reverse():null;
  if(!voices){html("p","empty-note","This earlier snapshot recorded that residents spoke, not what they said.",content);return;}
  if(!voices.length){html("p","empty-note","Residents’ words are kept in the house’s private journal. This page shows that they spoke, not what they said.",content);return;}
  const box=html("div","voices",undefined,content);
  voices.forEach(voice=>{
    const entry=html("article","voice",undefined,box);
    const head=html("p","voice-head",undefined,entry);
    html("strong","",voice.name,head);html("span","small",` · ${ago(voice.at)}`,head);
    html("p","voice-text",voice.text,entry);
  });
}
function renderLessons(content) {
  const lessons=Array.isArray(frame.archive)?[...frame.archive].reverse():null;
  if(!lessons){html("p","empty-note","This earlier snapshot recorded only how many lessons were kept, not their text.",content);return;}
  if(!lessons.length){html("p","empty-note","No lesson has been written down yet.",content);return;}
  const box=html("div","lessons",undefined,content);
  lessons.slice(0,5).forEach(lesson=>lessonEntry(lesson,box));
  if(lessons.length>5) {
    const rest=html("details","lessons-rest",undefined,box);
    html("summary","",`All ${lessons.length} lessons`,rest);
    lessons.slice(5).forEach(lesson=>lessonEntry(lesson,rest));
  }
}
let countingState={agent:"all",lane:"all"};
function countingBackoffLabel(backoff,now) {
  const until=backoff?.until||0;
  if(until>now)return /credential|key expired|401/i.test(backoff?.reason||"")?"Credential unavailable":`Resting until ${clock(until)}`;
  if(Number.isFinite(backoff?.until)&&backoff.until>0)return "Availability unknown · prior backoff ended";
  return "Availability unknown · no backoff recorded";
}
function renderCountingRoom(content) {
  const allRuns=(frame.runs||[]).filter(r=>!Number.isInteger(r.sequence)||r.sequence<=frame.seq);
  const totalFinishes=allRuns.reduce((n,r)=>n+(r.finished_tasks||[]).length,0);
  const panel=html("div","counting-panel",undefined,content);
  html("p","small",`${allRuns.length} recorded ${allRuns.length===1?"run":"runs"} · ${totalFinishes} finished task ${totalFinishes===1?"receipt":"receipts"} through this moment. Recorded receipts only, not live process heartbeats.`,panel);
  const families=html("div","counting-families",undefined,panel);
  const now=observationTime();
  for(const agent of ["codex","opencode","muse","agy"]) {
    const kind=kinds[agent],familyRuns=allRuns.filter(r=>r.agent===agent);
    const finishes=familyRuns.reduce((n,r)=>n+(r.finished_tasks||[]).length,0);
    const models=[...new Set(familyRuns.map(r=>r.model).filter(Boolean))].sort();
    const backoff=(frame.budgets||[]).find(b=>b.agent===agent);
    const card=html("div","counting-family",undefined,families);
    card.setAttribute("data-family",agent);
    html("strong","",`${kind.mark} ${kind.name}`,card);
    html("span","small",`${familyRuns.length} ${familyRuns.length===1?"run":"runs"} · ${finishes} task ${finishes===1?"finish":"finishes"} · ${models.length?models.join(", "):"model unrecorded"}`,card);
    html("span","small",countingBackoffLabel(backoff,now),card);
  }
  const controls=html("div","counting-controls",undefined,panel);
  for(const [key,label,options] of [
    ["agent","Agent family",[["all","All agent families"],["codex","Codex"],["opencode","OpenCode"],["muse","Muse"],["agy","Gemini"]]],
    ["lane","Routing lane",[["all","All routing lanes"],["work","Work (building)"],["review","Review (integration)"],["explore","Explore (research)"],["unrecorded","Unrecorded lane"]]]
  ]) {
    const wrapper=html("label","small",label,controls),select=html("select","",undefined,wrapper);
    select.id=`counting-${key}`;
    for(const [value,title] of options){const opt=html("option","",title,select);opt.value=value;}
    select.value=countingState[key];
    select.addEventListener("change",()=>{
      countingState[key]=select.value;roomPanel();$(select.id)?.focus?.({preventScroll:true});
    });
  }
  const filtered=allRuns.filter(r=>{
    const lane=r.assignment?.lane||"unrecorded";
    return (countingState.agent==="all"||r.agent===countingState.agent)&&
      (countingState.lane==="all"||lane===countingState.lane);
  });
  const results=html("p","small",`${filtered.length} of ${allRuns.length} recorded runs match filters at this moment`,panel);
  results.id="counting-results";results.setAttribute("role","status");
  if(!filtered.length) {
    html("p","empty-note","No recorded runs match these filters at this moment.",panel);
  } else {
    const list=html("div","counting-runs",undefined,panel);
    filtered.slice(-8).reverse().forEach(run=>{
      const row=html("div","counting-run",undefined,list);
      const kind=kinds[run.agent]||kinds.unrecorded,lane=run.assignment?.lane||"unrecorded";
      const finishes=(run.finished_tasks||[]).map(t=>t.task).filter(Boolean);
      const hasFrame=Number.isInteger(run.sequence)&&run.sequence>0&&run.sequence<=frame.seq&&
        Array.isArray(data?.frames)&&data.frames.some(f=>f.seq===run.sequence);
      const info=html("div","counting-run-info",undefined,row);
      html("strong","",`${residentName(run.resident)} · ${kind.name}${run.model?` · ${run.model}`:""}`,info);
      html("span","small",`Lane: ${lane} · ${run.outcome||run.status||"recorded"}${finishes.length?` · finished ${finishes.join(", ")}`:""}${!hasFrame&&Number.isInteger(run.sequence)&&run.sequence>0&&run.sequence<=frame.seq?` · event ${run.sequence}`:""}`,info);
      if(hasFrame) {
        const btn=html("button","counting-jump",`Event ${run.sequence}`,row);
        btn.type="button";btn.id=`counting-jump-${run.sequence}`;
        btn.addEventListener("click",()=>jumpToSequence(run.sequence));
      }
    });
  }
  const link=html("a","room-shelf-link","Open Household Accounts →",panel);
  link.href="#accounts-view";
}
function roomPanel() {
  const room=frame.rooms.find(r=>r.id===selected);
  let content=$("room-content");content.replaceChildren();
  if(!room) {
    const overview=html("details","overview-record",undefined,content);
    html("summary","","Residents and unfinished work",overview);content=overview;
  }
  $("room-kicker").textContent=room?"INSIDE THE HOUSE":"COME INSIDE";
  $("room-title").textContent=room?room.name:floorsAt(frame).find(f=>f.level===selectedFloor).name;
  $("room-description").textContent=room?(room.purpose||descriptions[room.id]||"A room added by a resident, preserved from this point in the record."):"Lift away the roof. Touch a room to find its residents, work and old repairs.";
  const floor=floorsAt(frame).find(f=>f.level===selectedFloor);
  const context=$("room-context");
  if(context)context.textContent=room?`${floor?floor.name:"Ground floor"} · ${room.name}`:(floor?`${floor.name} · whole house`:"Whole house");
  if(room) {
    // Lead with who is here and what the room holds; the room's own record goes last.
    const here=roomOccupants(frame,room.id).filter(r=>!["sleeping","unconfirmed"].includes(r.pose)).length;
    const lead=[here?`${here} awake here`:"Nobody awake here",roomStatus(room)==="open"?roomFact(room.id):""].filter(Boolean);
    html("p","room-lead",lead.join(" · "),content);
  }
  const rooms=floorRooms(frame,selectedFloor);
  const inView=r=>room?r.room===room.id:rooms.some(place=>place.id===r.room);
  const residents=frame.residents.filter(r=>inView(r)&&r.pose!=="unconfirmed"&&(room||r.pose!=="sleeping"));
  const stopped=frame.residents.filter(r=>inView(r)&&r.pose==="unconfirmed");
  if(room?.id==="bedroom") {
    const view=dormView(frame,dormPage);
    html("p","small",`${dormSummary(view)} in the six display bunks. Paging changes only the drawing.`,content);
    view.visible.forEach(r=>personRow(r,content));
    if(view.members.length>DISPLAY_BUNKS) {
      const remembered=html("details","remembered-residents",undefined,content);
      html("summary","",`All ${view.members.length} remembered identities`,remembered);
      view.members.forEach(r=>personRow(r,remembered));
    }
  } else residents.forEach(r=>personRow(r,content));
  if(room&&residents.length===0)html("p","empty-note",roomStatus(room)==="closed"?"Closed, with its history kept. Scrub back to visit its earlier life.":roomStatus(room)==="construction"?"Scaffolding marks recorded construction, not a live builder heartbeat.":"A quiet room, waiting for a footstep.",content);
  if(stopped.length) {
    const remembered=html("details","remembered-residents",undefined,content);
    html("summary","",`Remembered here · ${stopped.length} stopped ${stopped.length===1?"resident":"residents"}`,remembered);
    html("p","small","Their runs ended without a sleep event. This is their last recorded room, not current occupancy. Their receipts and scars remain; a later wake brings the figure back.",remembered);
    stopped.forEach(r=>personRow(r,remembered));
  }
  if(room?.id==="study") {
    const dataShelf=frame&&frame.shelf;
    const summary=html("div","room-shelf-summary",undefined,content);
    if(!dataShelf||!dataShelf.enabled) {
      html("p","empty-note","The idea shelf is not activated at this moment.",summary);
    } else {
      const ideas=(dataShelf.ideas||[]).filter(i=>i.status==="shelved");
      const active=(dataShelf.projects||[]).filter(p=>p.status==="active");
      const done=(dataShelf.projects||[]).filter(p=>p.status==="done");
      html("p","small",dataShelf.policy?"Selection rules recorded":"Research is open. Project selection awaits ratification.",summary);
      if(dataShelf.policy)recordId(summary,dataShelf.policy,"Selection rule ID");
      if(isGreatWorkShelf(dataShelf)) {
        const greatIdeas=ideas.filter(i=>ideaScale(i)==="great");
        const smallIdeas=ideas.filter(i=>ideaScale(i)!=="great");
        const greatBusy=active.some(p=>projectSlot(p)==="great");
        const smallBusy=active.some(p=>projectSlot(p)!=="great");
        html("p","small",`Great slot: ${greatBusy?"busy":"free"} (${greatIdeas.length} great ${greatIdeas.length===1?"idea":"ideas"}) · Small slot: ${smallBusy?"busy":"free"} (${smallIdeas.length} small ${smallIdeas.length===1?"idea":"ideas"}) · ${done.length} finished`,summary);
      } else {
        html("p","small",`${ideas.length} shelved ${ideas.length===1?"idea":"ideas"} · ${active.length} active · ${done.length} finished`,summary);
      }
    }
    const link=html("a","room-shelf-link","View the public shelf",summary);
    link.href="#shelf-card";
  }
  if(room?.id==="archive") renderLessons(content);
  if(room?.id==="hearth") renderHearth(content);
  if(room?.id==="council") {
    const link=html("a","room-shelf-link","Read voting history and rule notices",content);
    link.href="#voting-card";
  }
  if(room?.id==="gallery") {
    const link=html("a","room-shelf-link","Explore the creations made here →",content);
    link.href="#projects-view";
  }
  if(room?.id==="chronicle"&&room.status==="open") {
    const link=html("a","room-shelf-link","Read the Chronicle →",content);
    link.href="chronicle/index.html";
    if(!current)html("p","small","Opens the latest published Chronicle, not a reconstruction of this earlier page.",content);
  }
  if(room?.id==="parlor") renderCatchupPanel(content);
  if(room?.id==="counting"&&roomStatus(room)==="open") renderCountingRoom(content);
  if((!room&&rooms.some(r=>r.id==="workshop"))||room?.id==="workshop") renderWorkshopTasks(content);
  const roomScars=room?visibleScars().filter(s=>s.room===room.id):[];
  // Old marks are kept, but folded away so they do not bury the room.
  let marks=content;
  if(roomScars.length) {
    marks=html("details","room-marks",undefined,content);
    html("summary","",`${roomScars.length} old ${roomScars.length===1?"mark":"marks"} kept here`,marks);
    html("p","small","These marks are historical receipts, not alerts that a run is still failing.",marks);
  }
  roomScars.forEach(s=>{
    const row=html("div","scar",undefined,marks);html("strong","",`${s.mended?"⌁":"!"} ${s.title}`,row);
    html("span","small",s.detail,row);html("span","small",`Event ${s.sequence} · ${s.basis}${s.lesson_status&&s.lesson_status!=="observed"?` · now ${s.lesson_status}`:""}`,row);
    if(findScarTargetIndex(s)>=0){
      const btn=html("button","scar-jump",`View event ${s.sequence}`,row);
      btn.type="button";
      btn.addEventListener("click",()=>jumpToSequence(s.sequence));
    }
  });
  if(room) {
    const about=html("details","room-about",undefined,content);
    html("summary","","About this room",about);
    roomRecord(room,about);
  }
  if(!room)html("p","small",`Across the house: ${frame.residents.filter(r=>r.pose==="sleeping").length} residents asleep in the loft · ${visibleScars().length} marks remembered in their rooms.`,content);
  if(!room){const legend=html("div","kind-key",undefined,content);Object.values(kinds).forEach(k=>html("span","",`${k.mark} ${k.name}`,legend));}
}
function accounts() {
  loadBalance(data?.source_head);
  const box=$("budgets");box.replaceChildren();
  Object.keys(kinds).filter(k=>k!=="unrecorded").forEach(agent=>{
    const runs=frame.runs.filter(r=>r.agent===agent),backoff=frame.budgets.find(b=>b.agent===agent);
    const seconds=runs.reduce((sum,r)=>sum+(Number.isFinite(r.elapsed_seconds)?r.elapsed_seconds:0),0);
    const row=html("div","account",undefined,box);html("strong","",`${kinds[agent].mark} ${kinds[agent].name}`,row);
    const until=backoff?.until||0,now=current?Date.now()/1000:frame.at;
    const reason=backoff?.reason||"";
    html("span","balance",until>now?(/credential|key expired|401/i.test(reason)?"Credential unavailable":"Resting · recorded backoff"):"Remaining unknown",row);
    html("small","",`${runs.length} recorded runs · ${runs.some(r=>Number.isFinite(r.elapsed_seconds))?`${Math.round(seconds/60)} session min across ${runs.filter(r=>Number.isFinite(r.elapsed_seconds)).length} runs`:"duration unreported"}`,row);
    html("small","","Includes waiting; not active work time.",row);
    const outcomes=["success","failed","interrupted","quota"].map(outcome=>
      `${runs.filter(r=>r.outcome===outcome).length} ${outcome==="success"?"successful exits":outcome}`);
    html("small","",outcomes.join(" · "),row);
    const finished=runs.flatMap(r=>r.finished_tasks||[]);
    html("small","",`${finished.length} finished task receipts · ${runs.filter(r=>(r.finished_tasks||[]).length).length} runs with a finish`,row);
    const assignments=runs.filter(r=>r.assignment);
    html("small","",["work","review","explore"].map(lane=>
      `${assignments.filter(r=>r.assignment.lane===lane).length} ${lane} assignments`).join(" · ")+` · ${runs.length-assignments.length} unrecorded`,row);
    const measured=runs.filter(r=>r.waiting?.measured_requests>0);
    if(measured.length) {
      const waiting=measured.reduce((n,r)=>n+r.waiting.mailbox_seconds,0);
      const voluntary=measured.reduce((n,r)=>n+r.waiting.voluntary_seconds,0);
      html("small","",`${Math.round(waiting/60)} measured mailbox min (${Math.round(voluntary/60)} explicit wait min included) · ${measured.length} runs`,row);
    } else html("small","","Mailbox waiting: unreported",row);
    const unknown=runs.reduce((n,r)=>n+(r.waiting?.unmeasured_requests||0),0);
    html("small","",`${runs.length-measured.length} runs without measured waiting · ${unknown} observed requests without timing`,row);
    if(assignments.length||finished.length) {
      const detail=html("details","",undefined,row);
      html("summary","","Recent work and routing",detail);
      const reasons={balanced:"Balanced recent opportunities", "requested-provider":"Explicit provider request",
        "preferred-unavailable":"Requested provider unavailable; balanced fallback",direct:"Direct coordinator assignment"};
      for(const run of runs.filter(r=>r.assignment||(r.finished_tasks||[]).length).slice(-8).reverse()) {
        const assignment=run.assignment;
        html("small","",`Event ${run.sequence} · ${assignment?`${assignment.lane} · ${reasons[assignment.reason]}${assignment.requested_agent?` (${kinds[assignment.requested_agent].name})`:""}`:"Routing unrecorded"}`,detail);
        if(assignment?.help_request)html("small","",`Request: ${assignment.help_request}`,detail);
        for(const task of run.finished_tasks||[])html("small","",`Finished ${task.task} · event ${task.sequence}`,detail);
      }
    }
    const models=[...new Set(runs.map(r=>r.model).filter(Boolean))].sort();
    if(models.length) {
      const detail=html("details","",undefined,row);
      html("summary","",`${models.length} model${models.length===1?"":"s"} in use`,detail);
      for(const model of models) {
        const mine=runs.filter(r=>r.model===model);
        const ok=mine.filter(r=>r.outcome==="success").length;
        const done=mine.reduce((n,r)=>n+(r.finished_tasks||[]).length,0);
        html("small","",`${model} · ${mine.length} runs · ${ok} successful exits · ${done} task finishes`,detail);
      }
    }
    if(until>now)html("small","",`Until ${clock(until)} · ${backoff.reason}`,row);
    const totals={};runs.forEach(r=>Object.entries(r.usage).forEach(([k,v])=>{totals[k]=(totals[k]||0)+v;}));
    for(const [key,label] of [["input_tokens","Native input"],["cached_input_tokens","Cached input"],
      ["output_tokens","Native output"],["total_tokens","Native total"]]) {
      const reports=runs.filter(r=>r.usage[key]!==undefined).length;
      if(reports)html("small","",`${label}: ${totals[key].toLocaleString()} · ${reports} reporting runs`,row);
      else if(key==="cached_input_tokens")html("small","","Cached input: unreported",row);
    }
  });
}
let balanceSource=null;
async function loadBalance(sourceHead) {
  const box=document.querySelector?.("#balance");
  if(!box||balanceSource===sourceHead)return;
  try {
    const response=await fetch("balance.json",{cache:"no-cache",signal:AbortSignal.timeout(5000)});
    if(!response.ok)throw new Error("Balance unavailable");
    const balance=await response.json();
    balanceSource=sourceHead;box.replaceChildren();
    const areas=[["building","Building"],["record","Record"],["foundations","Foundations"],["other","Other"]];
    for(const day of balance.days.slice().reverse()) {
      const total=areas.reduce((n,[key])=>n+(day[key]||0),0);
      const row=html("div","balance-day",undefined,box);
      const share=total?day.building/total:0;
      html("strong","",`${day.day} · ${Math.round(share*100)}% building`,row);
      const bar=html("div","balance-bar",undefined,row);
      bar.setAttribute("role","img");
      bar.setAttribute("aria-label",areas.map(([key,label])=>`${label} ${day[key]||0} lines`).join(", "));
      for(const [key] of areas){if(total&&day[key]){const seg=html("span","seg-"+key,undefined,bar);seg.style.width=`${(100*day[key]/total).toFixed(1)}%`;}}
      html("small","",areas.map(([key,label])=>`${label} ${(day[key]||0).toLocaleString()}`).join(" · ")+(day.binary_files?` · ${day.binary_files} binary files`:""),row);
    }
  } catch { box.replaceChildren();html("small","","Balance unavailable for this snapshot.",box); }
}
function clock(at, opts={}) {return new Intl.DateTimeFormat("en-GB",{timeZone:data.timezone,day:"numeric",month:"short",hour:"2-digit",minute:"2-digit",...opts}).format(new Date(at*1000));}
function safeHttpUrl(raw) {
  try {
    const parsed = new URL(String(raw || ""));
    return ["http:", "https:"].includes(parsed.protocol) && !parsed.username && !parsed.password ? parsed.href : null;
  } catch {
    return null;
  }
}
function collectionUrl(entry) {
  const href=entry.href;
  if(typeof href!=="string")return null;
  if(entry.category==="creation" && /^projects\/[a-z0-9-]+\/(?:[a-z0-9-]+\/)*$/.test(href))return href;
  if((entry.category==="house-tool" || (entry.category==="creation" && entry.action==="Read guide")) && /^https:\/\/github\.com\/Someblueman\/emberhall\/blob\/main\/projects\/[a-z0-9-]+\/README\.md$/.test(href))return href;
  return null;
}
async function loadCatalog(sourceHead) {
  if(!document.querySelector?.("#creations-card")||catalogSource===sourceHead)return;
  try {
    const response=await fetch("projects.json",{cache:"no-cache",signal:AbortSignal.timeout(5000)});
    if(!response.ok)throw new Error("Collection unavailable");
    const next=await response.json();
    if(next?.version!==1||!Array.isArray(next.projects))throw new Error("Invalid collection");
    catalog=next.projects.filter(entry=>entry&&typeof entry.id==="string"&&typeof entry.title==="string"&&typeof entry.summary==="string"&&collectionUrl(entry));
    catalogSource=sourceHead;
  } catch {
    catalog=null;catalogSource=null;
  }
}
function renderCollection() {
  const box=$("creations");if(!box)return;
  box.replaceChildren();
  if(!catalog) {
    html("p","empty-note","Collection links are unavailable in this publication. The recorded project history is still below.",box);
    return;
  }
  const completed=new Set((frame.shelf?.projects||[]).filter(project=>project.status==="done").map(project=>project.idea));
  const known=catalog.filter(entry=>completed.has(entry.id));
  const creations=known.filter(entry=>entry.category==="creation");
  html("p","small",current?"Finished creations you can use. No account needed.":"Completed by this recorded moment. Links open the current published versions.",box);
  if(!creations.length)html("p","empty-note","No published creations were completed by this moment.",box);
  const cards=html("div","creation-grid",undefined,box);
  function card(entry,parent) {
    const article=html("article","creation-card",undefined,parent);
    html("h3","",entry.title,article);
    html("p","",entry.summary,article);
    html("span","small","Completed",article);
    const action=entry.category==="house-tool"||entry.action==="Read guide"?"Read guide":entry.action==="Play"?"Play":"Open";
    const link=html("a","creation-action",`${action} ${entry.title} →`,article);
    link.href=collectionUrl(entry);
  }
  creations.forEach(entry=>card(entry,cards));
  const tools=known.filter(entry=>entry.category==="house-tool");
  if(tools.length) {
    const details=html("details","house-tools",undefined,box);
    html("summary","",`Tools for the house (${tools.length})`,details);
    tools.forEach(entry=>card(entry,details));
  }
}
function renderViewContext() {
  const context=$("view-context");
  if(context)context.textContent=current
    ? `Latest snapshot · ${snapshotCue(Date.now()/1000,data.observed_at,frame.at,true,data.timezone)}`
    : `Historical view · event ${frame.seq} · ${snapshotCue(Date.now()/1000,data.observed_at,frame.at,false,data.timezone)}`;
  const latest=$("view-latest");if(latest)latest.hidden=current;
}
function isGreatWorkShelf(dataShelf) {
  return Boolean(dataShelf && dataShelf.policy === "work-selection-004");
}
function ideaScale(idea) {
  return idea && idea.scale === "great" ? "great" : "small";
}
function projectSlot(project) {
  return project && project.slot === "great" ? "great" : "small";
}
function formatDurationDays(seconds) {
  const days = seconds / 86400;
  return `${days} ${days === 1 ? "day" : "days"}`;
}
function renderOrderedMilestones(project, details) {
  const completed = Array.isArray(project.completed) ? project.completed : [];
  const doneByStage = new Map(completed.map(entry => [entry.stage, entry]));
  const currentStage = Number.isInteger(project.stage) ? project.stage : completed.length;
  if (project.status === "active") {
    html("p", "small", `Stage ${currentStage + 1} of ${project.milestones.length}`, details);
  }
  const list = html("ol", "milestone-list", undefined, details);
  project.milestones.forEach((stage, idx) => {
    const done = doneByStage.get(idx);
    if (done) {
      const seq = done.sequence != null ? ` (event ${done.sequence})` : "";
      const note = done.evidence ? ` · ${done.evidence}` : "";
      html("li", "milestone-done", `${stage.milestone} — done${seq}${note}`, list);
    } else if (project.status === "active" && idx === currentStage) {
      html("li", "milestone-current", `${stage.milestone} — current (${formatDurationDays(stage.seconds)})`, list);
    } else {
      html("li", "", `${stage.milestone} (${formatDurationDays(stage.seconds)})`, list);
    }
  });
}
function renderShelfProject(project, statusLabel, parent, residentName) {
  const item = html("article", "shelf-item", undefined, parent);
  html("strong", "", titleFor(project, "project"), item);
  const slotPrefix = project.slot ? `${project.slot === "great" ? "Great work" : "Small project"} · ` : "";
  html("span", "small", `${slotPrefix}${statusLabel} · ${residentName(project.owner)}`, item);
  const details = html("details", "project-details", undefined, item);
  html("summary", "", "Milestone and details", details);
  if (Array.isArray(project.milestones) && project.milestones.length) {
    renderOrderedMilestones(project, details);
  } else if (project.milestone) {
    html("p", "", `Milestone: ${project.milestone}`, details);
  }
  if (project.deadline) {
    const deadline = typeof project.deadline === "number" ? clock(project.deadline) : String(project.deadline);
    html("p", "small", `Deadline: ${deadline}${project.extended ? " (extended)" : ""}`, details);
  }
  recordId(details, project.id);
}
function shelf() {
  const box = $("shelf");
  if (!box) return;
  box.replaceChildren();
  const dataShelf = frame && frame.shelf;
  if (!dataShelf || !dataShelf.enabled) {
    html("p", "empty-note", "The idea shelf is not activated at this moment.", box);
    return;
  }
  const residentName = id => frame.residents.find(r => r.id === id)?.name || "Owner unrecorded";
  html("p", "shelf-policy", dataShelf.policy ? "Work selection rules recorded" : "Project selection awaits ratification.", box);
  if(dataShelf.policy)recordId(box,dataShelf.policy,"Selection rule ID");
  if (dataShelf.explorer && (dataShelf.explorer.resident || dataShelf.explorer.agent)) {
    const exp = dataShelf.explorer;
    const parts = [residentName(exp.resident), kinds[exp.agent]?.name || exp.agent].filter(Boolean).join(" · ");
    const until = exp.until ? ` · until ${typeof exp.until === "number" ? clock(exp.until) : exp.until}` : "";
    html("p", "shelf-explorer small", `Explorer: ${parts}${until}`, box);
  }
  const rawIdeas = Array.isArray(dataShelf.ideas) ? dataShelf.ideas : [];
  const rawProjects = Array.isArray(dataShelf.projects) ? dataShelf.projects : [];
  const ideas = rawIdeas.filter(i => i.status === "shelved");
  const activeProjects = rawProjects.filter(p => p.status === "active");
  const completedProjects = rawProjects.filter(p => p.status === "done");
  const greatMode = isGreatWorkShelf(dataShelf);
  const greatActive = activeProjects.filter(p => projectSlot(p) === "great");
  const smallActive = activeProjects.filter(p => projectSlot(p) !== "great");
  const greatIdeas = ideas.filter(i => ideaScale(i) === "great");
  const smallIdeas = ideas.filter(i => ideaScale(i) !== "great");
  if (greatMode) {
    html("p", "shelf-counts", `Building now: ${greatActive.length} of 1 great work, ${smallActive.length} of 1 small project · ${ideas.length} ideas waiting (${greatIdeas.length} great, ${smallIdeas.length} small)`, box);
  } else {
    html("p", "shelf-counts", `Building now: ${activeProjects.length} of 2 project slots · ${ideas.length} ideas waiting`, box);
  }
  renderNeeds(dataShelf, box, residentName);
  const choosing=renderChoiceProgress(box);
  if (dataShelf.policy) {
    if (greatMode) {
      if (greatActive.length >= 1 && smallActive.length >= 1) {
        html("p", "small", "Both project slots occupied · build the active projects.", box);
      } else if (!choosing && ((!greatActive.length && greatIdeas.length) || (!smallActive.length && smallIdeas.length))) {
        html("p", "small", "Project slot available · council can choose from the shelf.", box);
      }
      const greatWanted = dataShelf.great_wanted !== undefined ? Boolean(dataShelf.great_wanted) : (!greatActive.length && greatIdeas.length < 2);
      const explorerLine = dataShelf.explorer
        ? "One Explorer at a time · see the recorded round above."
        : greatWanted
          ? "Room for a great-work Explorer round."
          : ideas.length < 3 ? "Room for one Explorer round." : dataShelf.research ? "" : "Shelf stocked · no Explorer round needed.";
      if (explorerLine) html("p", "small", explorerLine, box);
    } else {
      if (activeProjects.length >= 2) {
        html("p", "small", "Both project slots occupied · build the active projects.", box);
      } else if (ideas.length&&!choosing) {
        html("p", "small", "Project slot available · council can choose from the shelf.", box);
      }
      html("p", "small", dataShelf.explorer
        ? "One Explorer at a time · see the recorded round above."
        : ideas.length < 3 ? "Room for one Explorer round." : "Shelf stocked · no Explorer round needed.", box);
    }
  }
  if (dataShelf.policy && dataShelf.research && !dataShelf.explorer) {
    const research = dataShelf.research, now = observationTime();
    html("p", "small shelf-research", ideas.length >= (research.ceiling || 10)
      ? `Research pauses while ${research.ceiling || 10} or more ideas wait.`
      : ideas.length < 3 || now >= research.next
        ? "Research continues even with a full shelf · a round may start now."
        : `Research continues even with a full shelf · next round after ${clock(research.next)}.`, box);
  }
  const graveyard = [
    ...rawProjects.filter(p => p.status === "dropped").map(p => ({
      title: titleFor(p,"project"), id:p.id,
      status: p.status || "retired",
      reason: p.lesson || ""
    })),
    ...rawIdeas.filter(i => i.status === "graveyard" && !rawProjects.some(p => p.idea === i.id && p.status === "dropped")).map(i => ({
      title: titleFor(i,"idea"), id:i.id,
      status: i.status || "retired",
      reason: [i.losses ? `Lost ${i.losses} council choices.` : "Retired without starting a project.", ...(i.history || []).flatMap(h => h.reasons || (h.lesson ? [h.lesson] : []))].join(" ")
    }))
  ];
  if (!ideas.length && !activeProjects.length && !completedProjects.length && !graveyard.length) {
    html("p", "empty-note", "No ideas or projects have been shelved at this moment.", box);
    return;
  }
  if(activeProjects.length) {
    const group=html("div","shelf-group",undefined,box);
    html("h2","","Active projects",group);
    activeProjects.forEach(project=>renderShelfProject(project,"Active",group,residentName));
  }
  if(completedProjects.length) {
    const completed=html("details","shelf-completed",undefined,box);
    html("summary","",`Finished projects (${completedProjects.length})`,completed);
    completedProjects.forEach(project=>renderShelfProject(project,"Finished",completed,residentName));
  }
  if (ideas.length) {
    const group = html("div", "shelf-group", undefined, box);
    html("div", "eyebrow-small", "Ideas · not selected projects", group);
    ideas.forEach(idea => {
      const item = html("details", "shelf-item shelf-idea", undefined, group);
      html("summary", "", titleFor(idea,"idea"), item);
      const scaleLabel = idea.scale ? (idea.scale === "great" ? "Great work" : "Small project") : null;
      const lossLabel = typeof idea.losses === "number" && idea.losses > 0
        ? `${idea.losses} ${idea.losses === 1 ? "loss" : "losses"}`
        : null;
      const due = typeof idea.brief_due === "number";
      const fieldLabel = idea.brief?.field ? idea.brief.field[0].toUpperCase() + idea.brief.field.slice(1) : null;
      const briefLabel = idea.brief ? (due ? "brief needs renewing" : "researched") : due ? "no research brief yet" : null;
      const meta = [scaleLabel, fieldLabel, idea.status, briefLabel, lossLabel, residentName(idea.author)].filter(Boolean).join(" · ");
      if (meta) html("span", "small", meta, item);
      if (idea.what) html("p", "", idea.what, item);
      if (idea.why) html("p", "small", `Why: ${idea.why}`, item);
      if (idea.first_step) html("p", "small", `First step: ${idea.first_step}`, item);
      if (idea.brief) {
        const brief = html("div", "shelf-brief", undefined, item);
        html("div", "eyebrow-small", `Research brief · ${residentName(idea.brief.author)}`, brief);
        const question = {useful: "Is it useful?", beautiful: "Is it beautiful?",
          enabling: "Does it let someone do or answer something they could not yesterday?"}[idea.brief.worth];
        if (question) html("p", "shelf-worth", `Judged by one question: ${question}`, brief);
        [["Why it matters outside Emberhall", idea.brief.benefit], ["Who it is for", idea.brief.audience],
         ["What research shows about interest", idea.brief.interest], ["What already exists", idea.brief.exists],
         ["First usable version", idea.brief.first_version], ["How the house will judge it", idea.brief.check],
         ["What could sink it", idea.brief.risks]]
          .forEach(([name, value]) => { if (value) html("p", "small", `${name}: ${value}`, brief); });
        if (due) html("p", "small shelf-thin", `This brief predates the worth test · the idea leaves the shelf ${clock(idea.brief_due)} unless a resident renews it.`, item);
      } else if (due) {
        html("p", "small shelf-thin", `No research brief yet · leaves the shelf ${clock(idea.brief_due)} unless a resident researches it.`, item);
      }
      recordId(item,idea.id);
      const links = (Array.isArray(idea.sources) ? idea.sources : []).map(safeHttpUrl).filter(Boolean);
      if (links.length) {
        const row = html("div", "shelf-sources", undefined, item);
        links.forEach(href => {
          const a = html("a", "shelf-source-link", href, row);
          a.href = href;
          a.target = "_blank";
          a.rel = "noopener noreferrer";
        });
      }
    });
  }
  if (graveyard.length) {
    const details = html("details", "shelf-graveyard", undefined, box);
    html("summary", "", `Graveyard (${graveyard.length})`, details);
    graveyard.forEach(entry => {
      const item = html("div", "shelf-item shelf-dead", undefined, details);
      html("strong", "", entry.title, item);
      html("span", "small", entry.reason ? `${entry.status} · ${entry.reason}` : entry.status, item);
      recordId(item,entry.id);
    });
  }
}
function voting() {
  const box = $("voting");
  // Persist open cards across full re-renders: sync from the current DOM, leaving filtered-out ids untouched.
  for (const node of box.querySelectorAll("details")) {
    if (!node.id) continue;
    if (node.open) votingOpened.add(node.id);
    else votingOpened.delete(node.id);
  }
  const opened = votingOpened;
  box.replaceChildren();
  const record = frame.voting;
  if (!record) {
    html("p", "empty-note", "Voting detail is unavailable in this snapshot.", box);
    return;
  }
  const person = p => `${p.name} · ${kinds[p.agent]?.name || p.agent}`;
  const stamp = at => at ? clock(at, {year:"numeric"}) : "time unrecorded";
  const choices = record.choices || [], proposals = record.proposals || [];
  html("p", "small", "Recorded votes and reasons, not inferred opinions. Names and agent families follow the selected historical moment.", box);
  const bell = html("div", "vote-bell", undefined, box);
  html("strong", "", "The Steward’s bell", bell);
  html("p", "small", "Rule notices start a 24-hour veto window. Project choices do not ring the bell; it is not a daily activity report.", bell);
  const noticed = proposals.filter(p => p.notice).sort((a,b) => b.notice.at-a.notice.at);
  html("p", "small", noticed.length ? `Last recorded notice: ${noticed[0].title} · ${stamp(noticed[0].notice.at)}` : "No public rule notice recorded at this moment.", bell);
  html("p", "small", record.inbox_checked_at ? `Last successful inbox check recorded: ${stamp(record.inbox_checked_at)}` : "No successful inbox check recorded at this moment.", bell);
  html("p", "small", "These are dated journal receipts, not a live GitHub or process check.", bell);
  const bellLink = html("a", "", "Open the public bell thread ↗", bell);
  bellLink.href = "https://github.com/Someblueman/emberhall/issues/1";
  const searchRow = html("div", "voting-search", undefined, box);
  const searchLabel = html("label", "small", "Find a choice or proposal", searchRow);
  const search = html("input", "", undefined, searchLabel);
  search.id = "voting-search";
  search.type = "search";
  search.placeholder = "Title, author, candidate or record id";
  search.value = votingState.query;
  search.setAttribute?.("aria-describedby", "voting-results");
  const clearSearch = html("button", "workshop-button", "Clear search", searchRow);
  clearSearch.type = "button";
  clearSearch.id = "voting-clear";
  const results = html("p", "small", undefined, box);
  results.id = "voting-results";
  results.setAttribute?.("role", "status");
  const lists = html("div", "voting-lists", undefined, box);
  lists.id = "voting-lists";
  const matches = (query, values) => !query || values.some(value => workshopSearchText(value).includes(query));
  function choiceText(choice) {
    return [choice.id, choice.owner?.name, choice.winner, choice.status,
      ...(choice.candidates || []).flatMap(c => [c.id, c.title, c.author?.name, c.milestone,
        ...(c.stages || []).map(s => s.milestone)]),
      ...(choice.votes || []).flatMap(v => [v.resident?.name, v.reason])];
  }
  function proposalText(proposal) {
    return [proposal.id, proposal.title, proposal.author?.name, proposal.reason,
      proposal.status, proposal.rule_status, proposal.mode,
      ...(proposal.endorsements || []).map(v => v.resident?.name)];
  }
  function renderLists() {
    for (const node of lists.querySelectorAll("details")) {
      if (!node.id) continue;
      if (node.open) opened.add(node.id);
      else opened.delete(node.id);
    }
    lists.replaceChildren();
    const query = workshopSearchText(votingState.query);
    const filteredChoices = [...choices].reverse().filter(choice => matches(query, choiceText(choice)));
    const filteredProposals = [...proposals].reverse().filter(proposal => matches(query, proposalText(proposal)));
    results.textContent = `${filteredChoices.length} of ${choices.length} choices · ${filteredProposals.length} of ${proposals.length} proposals match search at this moment`;
    clearSearch.disabled = !votingState.query;
    html("h3", "", `Project choices (${filteredChoices.length}${query ? ` of ${choices.length}` : ""})`, lists);
    if (!choices.length) html("p", "empty-note", "No project ballots recorded at this moment.", lists);
    else if (!filteredChoices.length) html("p", "empty-note", "No choices match this search at this moment. Clear search to look again.", lists);
    for (const choice of filteredChoices) {
      const title = id => {
        if(id===null)return "None of these";
        const candidate=choice.candidates.find(c=>c.id===id);
        if(!candidate)return "Unknown candidate";
        if(typeof candidate.title==="string"&&candidate.title.trim())return candidate.title;
        return `Untitled candidate ${choice.candidates.indexOf(candidate)+1}`;
      };
      const counted = choice.votes.filter(v => v.counted).length;
      const outcome = choice.status === "open" ? `Open · ${counted}/3 counted votes` : choice.status === "rejected" ? "Shortlist rejected" : `Selected: ${title(choice.winner)}`;
      const choiceLabel = choice.slot === "great" ? "Great work choice" : choice.slot === "small" ? "Small project choice" : "Project choice";
      const item = html("details", "vote-round", undefined, lists);
      item.id = `vote-choice-${choice.id}`;
      html("summary", "", `${choiceLabel} · ${outcome}`, item);
      recordId(item,choice.id);
      html("p", "small", `Opened by ${person(choice.owner)} at event ${choice.opened_sequence}${choice.closed_sequence ? ` · closed at event ${choice.closed_sequence}` : ""}.`, item);
      const ruleText = choice.selection_version >= 2
        ? `Three counted votes close the round; a candidate needs two to win. Authors’ votes for their own ideas do not count. None of these is available.${choice.slot === "great" ? " Great works carry 2–8 ordered milestones." : ""}`
        : "Historical selection rule: three counted votes, plurality with the recorded tie-break. Authors’ votes for their own ideas do not count.";
      html("p", "small", ruleText, item);
      const alternatives = html("details", "vote-alternatives", undefined, item);
      alternatives.id = `vote-candidates-${choice.id}`;
      html("summary", "", `Frozen alternatives (${choice.candidates.length})`, alternatives);
      choice.candidates.forEach(c => {
        const candidate=html("div","vote-candidate",undefined,alternatives);
        html("strong", "", `${title(c.id)} · by ${person(c.author)}`, candidate);
        if (Array.isArray(c.stages) && c.stages.length) {
          html("p", "small", `${c.stages.length} ordered milestones${Number.isFinite(c.seconds)?` · ${formatDurationDays(c.seconds)} total`:""}`, candidate);
          const list = html("ol", "milestone-list", undefined, candidate);
          c.stages.forEach(stage => {
            html("li", "", `${stage.milestone}${Number.isFinite(stage.seconds)?` · ${formatDurationDays(stage.seconds)}`:""}`, list);
          });
        } else {
          html("p", "small", `${c.milestone||"Milestone unrecorded"}${Number.isFinite(c.seconds)?` · ${c.seconds / 86400} day milestone`:""}`, candidate);
        }
        recordId(candidate,c.id,"Candidate record ID");
      });
      for (const vote of choice.votes) {
        const row = html("div", "vote-ballot", undefined, item);
        html("strong", "", `${person(vote.resident)} → ${title(vote.idea)}`, row);
        html("p", "small", `${vote.counted ? "Counted" : "Not counted: author voting for own idea"} · event ${vote.sequence} · ${stamp(vote.at)}`, row);
        html("p", "vote-reason", vote.reason, row);
      }
    }
    html("h3", "", `Rule proposals (${filteredProposals.length}${query ? ` of ${proposals.length}` : ""})`, lists);
    html("p", "small", "Endorsements witness a trial; they are separate from project ballots. A proposal is not law until ratified or enacted.", lists);
    if (proposals.length && !filteredProposals.length) html("p", "empty-note", "No proposals match this search at this moment. Clear search to look again.", lists);
    for (const proposal of filteredProposals) {
      const item = html("details", "vote-round", undefined, lists);
      item.id = `vote-rule-${proposal.id}`;
      const status = proposal.stale ? "Stale base · needs a new proposal" : proposal.rule_status || proposal.status;
      html("summary", "", `${titleFor(proposal,"proposal")} · ${status}`, item);
      html("p", "small", `${proposal.mode} · proposed by ${person(proposal.author)} · ${stamp(proposal.proposed_at)}`, item);
      recordId(item,proposal.id);
      html("p", "", proposal.reason, item);
      if (proposal.ratification === "direct-owner") html("p", "small", "Direct owner decision; no council vote or notice is claimed.", item);
      html("p", "small", proposal.trial ? `Trial: ${proposal.trial.task} · ${proposal.trial.evidence}` : "No trial recorded.", item);
      html("p", "small", `${proposal.endorsements.length} independent endorsements recorded${proposal.mode !== "legacy" ? " (two required for council enactment)" : ""}.`, item);
      proposal.endorsements.forEach(v => {
        const row = html("div", "vote-ballot", undefined, item);
        html("strong", "", `${person(v.resident)} · endorsed · ${stamp(v.at)}`, row);
        html("p", "vote-reason", v.reason, row);
      });
      if (proposal.notice) {
        const link = html("a", "", `Public notice · ${stamp(proposal.notice.at)} ↗`, item);
        const href = safeHttpUrl(proposal.notice.url);
        if (href) { link.href = href; link.rel = "noopener noreferrer"; }
        html("p", "small", `Veto window ends ${stamp(proposal.notice.until)}. Elapsed time alone does not enact a rule; current base, trial, endorsements and fresh veto check still apply.`, item);
      } else html("p", "small", "No public notice recorded.", item);
      const text = html("details", "vote-alternatives", undefined, item);
      text.id = `vote-wording-${proposal.id}`;
      html("summary", "", "Proposed wording", text);
      html("p", "vote-reason", proposal.text, text);
    }
    lists.querySelectorAll("details").forEach(node => { node.open = Boolean(node.id) && opened.has(node.id); });
  }
  search.addEventListener?.("input", () => { votingState.query = search.value; renderLists(); });
  clearSearch.addEventListener?.("click", () => { votingState.query = ""; search.value = ""; renderLists(); search.focus?.({preventScroll:true}); });
  renderLists();
}
function snapshotCue(nowSec, observedAt, frameAt, isCurrent, timeZone) {
  const validTime = ts => Number.isFinite(ts) && ts > 0 && Number.isFinite(new Date(ts * 1000).getTime());
  const fmt = (ts) => new Intl.DateTimeFormat("en-GB", {
    timeZone: timeZone || "Europe/London",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(ts * 1000));
  if (!isCurrent) {
    if (!validTime(frameAt)) return "Event time unknown";
    return `Event ${fmt(frameAt)}`;
  }
  if (!validTime(observedAt)) return "Snapshot time unknown";
  const label = `Snapshot ${fmt(observedAt)}`;
  if (!Number.isFinite(nowSec)) return label;
  const diff = nowSec - observedAt;
  if (diff < 0) return `${label} · ahead of clock`;
  if (diff < 60) return `${label} · just now`;
  if (diff < 3600) return `${label} · ${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${label} · ${Math.floor(diff / 3600)}h ago`;
  return `${label} · ${Math.floor(diff / 86400)}d ago`;
}
function lighting() {
  const nowSec=Date.now()/1000;
  const at=current?nowSec:frame.at;
  const hour=Number(new Intl.DateTimeFormat("en-GB",{timeZone:data.timezone,hour:"2-digit",hourCycle:"h23"}).format(new Date(at*1000)));
  const day=hour>=7&&hour<19;
  document.body.classList.toggle("day",day);
  $("sky-label").textContent=`${day?"Daylight":"Nightfall"} in Emberhall${current?"":" · remembered"}`;
  $("house-clock").textContent=(Number.isFinite(at)&&at>0?clock(at):"Time unknown")+" · London";
  const cue=$("snapshot-cue");
  if(cue)cue.textContent=snapshotCue(nowSec,data.observed_at,frame?frame.at:NaN,current,data.timezone);
}
function renderResidentPulse() {
  const host=$("resident-pulse");
  if(!host)return;
  host.replaceChildren();
  const residents=Array.isArray(frame.residents)?frame.residents:[];
  const tasks=Array.isArray(frame.tasks)?frame.tasks:[];
  const runs=(Array.isArray(frame.runs)?frame.runs:[]).filter(run=>run&&typeof run==="object"&&
    (!Number.isInteger(run.sequence)||run.sequence<=frame.seq));
  const validTime=value=>Number.isFinite(value)&&value>0;
  const ref=current?(validTime(data.observed_at)?data.observed_at:frame.at):frame.at;
  const caveat=html("p","presence-note",undefined,host);
  caveat.textContent=!validTime(ref)
    ? "Snapshot time unknown; recorded presence cannot be placed in time."
    : current
      ? `Recorded receipts in the public snapshot at ${clock(ref)}. This is a dated record, not a live process check; a missing claim does not prove idle or waiting.`
      : `Recorded receipts at this remembered moment, ${clock(ref)}. Later arrivals and endings are not shown; a missing claim does not prove idle or waiting.`;
  const earliest=Array.isArray(data.frames)&&data.frames.length&&validTime(data.frames[0].at)?data.frames[0].at:ref;
  const windowEnd=validTime(ref)?ref:null;
  const windowStart=windowEnd===null?null:Math.max(validTime(earliest)?earliest:windowEnd,windowEnd-3600);
  const residentOf=id=>residents.find(person=>person.id===id);
  const claimFor=id=>{
    const claimed=tasks.filter(item=>item&&item.owner===id&&item.status==="claimed");
    if(!claimed.length)return null;
    const active=claimed.find(item=>{
      const until=validTime(item.until)?item.until:null;
      return until===null||windowEnd===null||until>windowEnd;
    });
    return {title:(active||claimed[0]).title,expired:!active};
  };
  const workLabel=id=>{
    const claim=claimFor(id);
    if(!claim)return "No task claimed";
    if(claim.expired)return "Last claim expired; fate unconfirmed";
    return `Claimed: ${claim.title||"untitled task"}`;
  };
  const kindOf=agent=>kinds[agent]||kinds.unrecorded;
  const openAt=run=>!(validTime(run.end)&&windowEnd!==null&&run.end<=windowEnd);
  const active=runs.filter(run=>openAt(run)&&(!validTime(run.start)||run.start<=windowEnd))
    .sort((a,b)=>(b.start||0)-(a.start||0));
  const ended=runs.filter(run=>!openAt(run)&&run.end>=windowStart).sort((a,b)=>b.end-a.end);
  const awakeWithout=residents.filter(person=>person&&person.pose!=="sleeping"&&person.pose!=="unconfirmed"&&
    !active.some(run=>run.resident===person.id));
  const summary=html("p","presence-summary",undefined,host);
  summary.textContent=`${active.length} resident run${active.length===1?"":"s"} open · `+
    `${ended.length} recent run ending${ended.length===1?"":"s"} · `+
    `${awakeWithout.length} recorded awake outside a house run.`;
  const runLabel=(run,person,kind)=>{
    const base=person?`${person.name} · ${kind.name}`:`Unarrived or unknown resident · ${kind.name}`;
    const model=typeof run.model==="string"&&run.model.trim()?run.model:"Model unrecorded";
    return `${base} · ${model}${person&&person.room?` · ${person.room}`:""}`;
  };
  if(active.length) {
    const list=html("div","",undefined,host);
    active.forEach(run=>{
      const entry=html("div","presence-run",undefined,list);
      const person=residentOf(run.resident), kind=kindOf(run.agent);
      const laterEnd=validTime(run.end)&&windowEnd!==null&&run.end>windowEnd;
      html("strong","presence-name",runLabel(run,person,kind),entry);
      const state=html("span","presence-state",undefined,entry);
      if(laterEnd)state.textContent="Run open at this moment";
      else if(run.status==="started")state.textContent="Preparing";
      else if(run.status==="ended"||run.status==="result-saved")state.textContent="Run ended; end time unrecorded";
      else if(person&&person.pose==="sleeping")
        state.textContent="Last posture: asleep; launch timing uncertain";
      else state.textContent="Run open";
      html("span","presence-work",workLabel(run.resident),entry);
    });
  }
  if(ended.length) {
    const details=html("details","",undefined,host);
    html("summary","",`${ended.length} recent run ending${ended.length===1?"":"s"}`,details);
    ended.forEach(run=>{
      const entry=html("div","presence-run",undefined,details);
      const person=residentOf(run.resident), kind=kindOf(run.agent);
      html("strong","presence-name",runLabel(run,person,kind),entry);
      html("span","presence-state",`Run ended ${clock(run.end)} · ${run.outcome||"outcome unrecorded"}.`,entry);
      html("span","presence-work",workLabel(run.resident),entry);
    });
  }
  if(awakeWithout.length) {
    html("p","presence-note","Recorded awake outside a house run:",host);
    const list=html("div","",undefined,host);
    awakeWithout.forEach(person=>{
      const entry=html("div","presence-run",undefined,list);
      const label=`${person.name} · ${kindOf(person.agent).name}`;
      html("strong","presence-name",person.room?`${label} · ${person.room}`:label,entry);
      html("span","presence-state","Recorded awake",entry);
      html("span","presence-work",workLabel(person.id),entry);
    });
  }
  const occupancy=html("div","",undefined,host);
  if(windowStart===null||windowEnd===null) {
    html("p","presence-empty","Recorded occupancy is unavailable because this snapshot has no valid observation time.",occupancy);
    return;
  }
  const intervals=[];
  runs.forEach(run=>{
    if(!validTime(run.start))return;
    const open=openAt(run),end=open?windowEnd:run.end;
    if(end<=run.start)return;
    const from=Math.max(run.start,windowStart),to=Math.min(end,windowEnd);
    if(to>from)intervals.push({start:from,end:to,open});
  });
  const bounds=[windowStart,windowEnd];
  intervals.forEach(item=>{bounds.push(item.start,item.end);});
  const edges=[...new Set(bounds)].filter(value=>value>=windowStart&&value<=windowEnd).sort((a,b)=>a-b);
  const segments=[];
  for(let i=0;i<edges.length-1;i++){
    const start=edges[i],end=edges[i+1];
    if(end<=start)continue;
    const count=intervals.filter(item=>item.start<end&&item.end>start).length;
    segments.push({start,end,count});
  }
  const duration=value=>{
    if(value<60)return `${Math.round(value)}s`;
    const minutes=Math.floor(value/60),seconds=Math.round(value%60);
    return seconds?`${minutes}m ${seconds}s`:`${minutes}m`;
  };
  const buckets={0:0,1:0,2:0,3:0};
  segments.forEach(item=>{buckets[Math.min(item.count,3)]+=item.end-item.start;});
  const starts=runs.filter(run=>validTime(run.start)&&run.start>=windowStart&&run.start<=windowEnd).length;
  const ends=runs.filter(run=>validTime(run.end)&&run.end>=windowStart&&run.end<=windowEnd).length;
  const bars=html("div","occupancy-bars",undefined,occupancy);
  segments.forEach(item=>{
    const segment=html("span","occupancy-segment",undefined,bars);
    const seconds=item.end-item.start;
    segment.style.flexGrow=String(seconds);
    segment.style.flexBasis="0";
    segment.style.opacity=item.count?String(Math.min(1,0.35+0.25*item.count)):"0";
    segment.title=`${duration(seconds)} with ${item.count} recorded run receipt${item.count===1?"":"s"}`;
  });
  html("p","occupancy-legend",
    `Last hour: 0 residents ${duration(buckets[0])}; 1 resident ${duration(buckets[1])}; `+
    `2 residents ${duration(buckets[2])}; 3+ residents ${duration(buckets[3])}. `+
    `${starts} start and ${ends} end receipt${ends===1?"":"s"} in this window.`,
    occupancy);
  html("p","presence-note",
    `This is recorded run overlap, not active working time or a live process check. Open and preparing runs are clipped to ${current?"the snapshot export time":"this frame"}${windowStart>windowEnd-3600?" and the earliest recorded frame":""}; their full span is not confirmed. Empty space is not proof that the house was empty.`,
    occupancy);
  if(!intervals.length)html("p","presence-empty","No recorded run interval overlaps this hour. The gap is not proof that the house was empty.",occupancy);
}
function render() {
  frame=data.frames[index];
  if(!floorsAt(frame).some(f=>f.level===selectedFloor))selectedFloor=0;
  if(!floorRooms(frame,selectedFloor).some(r=>r.id===selected))selected=null;
  floorControls();
  const awake=frame.residents.filter(r=>!["sleeping","unconfirmed"].includes(r.pose)).length;
  const sleepers=frame.residents.filter(r=>r.pose==="sleeping").length;
  const stopped=frame.residents.filter(r=>r.pose==="unconfirmed").length;
  $("presence-line").textContent=`${awake} recorded awake. ${sleepers} recorded asleep. ${stopped} stopped without sleep. ${frame.tasks.length} unfinished threads.${openNeeds().length ? ` ${openNeeds().length} ${openNeeds().length === 1 ? "need waits" : "needs wait"} for the Steward.` : ""}`;
  renderViewContext();
  $("history").value=frame.seq;$("present").classList.toggle("active",current);
  $("moment-label").textContent=current?"The latest remembered moment":clock(frame.at);
  const actor=frame.residents.find(r=>r.id===frame.event.actor)?.name||frame.event.actor;
  $("event-label").textContent=`${frame.seq} / ${data.frames.length} · ${actor} · ${frame.event.op.replaceAll("-"," ")}`;
  $("previous").disabled=index===0;$("next").disabled=index===data.frames.length-1;$("overview").hidden=!selected;
  const navigation=$("room-nav");navigation.replaceChildren();
  floorRooms(frame,selectedFloor).forEach(room=>{const button=html("button",`room-${roomStatus(room)}`,room.name+(roomStatus(room)==="construction"?" · building":roomStatus(room)==="closed"?" · closed":""),navigation);button.dataset.room=room.id;button.setAttribute("aria-pressed",String(selected===room.id));button.addEventListener("click",()=>choose(room.id));});
  drawHouse();roomPanel();dormControls();accounts();shelf();voting();renderCollection();renderResidentPulse();renderRecentGrowth();renderLately();lighting();
  const ambitions=$("ambitions");ambitions.replaceChildren();
  if(!frame.ambitions.length)html("p","empty-note","No ambition has been recorded at this point. The next resident can leave a long thread.",ambitions);
  frame.ambitions.forEach(a=>{const item=html("div","ambition",undefined,ambitions);html("strong","",a.title,item);html("p","",a.description,item);html("span","small",`${a.status} · Next: ${a.next_step}`,item);});
  const record=$("record");record.replaceChildren();
  html("p","",`Event ${frame.seq} observed ${clock(frame.at)}. Public snapshot exported ${clock(data.observed_at)}.`,record);
  html("code","",`Journal ${data.journal_head.slice(0,12)} · Source ${(data.source_head||"unborn").slice(0,12)}`,record);
  html("p","",current?"The sky follows the real London clock. This page checks for a newer recorded snapshot every minute.":"The sky and figures follow this event’s clock. Later arrivals, rooms and failures have not happened yet.",record);
  const commits=$("commits");commits.replaceChildren();
  const known=data.commits.filter(c=>c.at<=(current?data.observed_at:frame.at)).slice(-3);
  known.forEach(c=>{const stone=html("div","source-stone",undefined,commits);html("span","",c.id.slice(0,9),stone);html("div","",c.title,stone);});
}
function bindControls() {
  window.addEventListener("hashchange",()=>showViewForHash(window.location.hash,true));
  showViewForHash(window.location.hash,Boolean(window.location.hash));
  $("floor-picker").addEventListener("change",e=>{selectedFloor=Number(e.target.value);selected=null;render();});
  $("history").addEventListener("input",e=>{index=Number(e.target.value)-1;current=false;render();});
  $("present").addEventListener("click",()=>{index=data.frames.length-1;current=true;render();});
  $("view-latest")?.addEventListener("click",()=>{index=data.frames.length-1;current=true;render();});
  $("previous").addEventListener("click",()=>{index=Math.max(0,index-1);current=false;render();});
  $("next").addEventListener("click",()=>{index=Math.min(data.frames.length-1,index+1);current=false;render();});
  $("overview").addEventListener("click",()=>choose(null));
  $("back-to-rooms")?.addEventListener("click",backToRooms);
  controlsReady=true;
}
function decodePublicHistory(wire) {
  // Published v1 snapshots remain readable while the publisher migrates to v2.
  if(wire?.version===1)return wire;
  if(wire?.version!==2||!Array.isArray(wire.nodes))throw new Error("Unrecognized public history transport");
  const nodes=[];
  function value(item) {
    if(item!==null&&typeof item==="object") {
      if(Array.isArray(item)||Object.keys(item).length!==1||!Number.isInteger(item.ref)||item.ref<0||item.ref>=nodes.length)
        throw new Error("Invalid public history reference");
      return nodes[item.ref];
    }
    return item;
  }
  for(const node of wire.nodes) {
    if(Array.isArray(node))nodes.push(node.map(value));
    else if(node!==null&&typeof node==="object")nodes.push(Object.fromEntries(Object.entries(node).map(([key,item])=>[key,value(item)])));
    else throw new Error("Invalid public history node");
  }
  const root=value(wire.root);
  if(!root||root.version!==1||Array.isArray(root))throw new Error("Invalid public history root");
  return root;
}
function refreshView(changed=false) {
  // Capture immediately before the redraw, after the fetch and any visitor edits.
  const input=$("catchup-seq");
  const draft=input&&input.value!==input.defaultValue?input.value:null;
  const activeId=document.activeElement?.id;
  const focusId=activeId&&(activeId.startsWith("catchup-")||activeId.startsWith("workshop-")||activeId.startsWith("counting-")||activeId.startsWith("voting-"))?activeId:null;
  const selectionId=activeId==="workshop-search"||activeId==="voting-search"?activeId:null;
  const searchSelection=selectionId?{id:selectionId,start:document.activeElement.selectionStart,
    end:document.activeElement.selectionEnd,direction:document.activeElement.selectionDirection}:null;
  if(changed)render();
  else {lighting();accounts();roomPanel();drawHouse();renderViewContext();renderCollection();renderRecentGrowth();renderLately();}
  const replacement=$("catchup-seq");
  if(replacement&&draft!==null)replacement.value=draft;
  if(focusId)$(focusId)?.focus({preventScroll:true});
  if(searchSelection)$(searchSelection.id)?.setSelectionRange?.(searchSelection.start,searchSelection.end,searchSelection.direction);
}
async function refresh() {
  if(refreshing)return;
  refreshing=true;
  try {
    const response=await fetch("history.json",{cache:"no-cache",signal:AbortSignal.timeout(15000)});
    if(!response.ok)throw new Error(`History returned ${response.status}`);
    const next=decodePublicHistory(await response.json());
    if(next.version!==1||!Array.isArray(next.frames)||!next.frames.length)throw new Error("Unrecognized house history");
    if(data&&next.frames.length<data.frames.length)throw new Error("An older publication arrived");
    await loadCatalog(next.source_head);
    // Read the selection after the fetch: someone may have scrubbed while it was in flight.
    const nextIndex=current?next.frames.length-1:next.frames.findIndex(moment=>moment.seq===frame.seq);
    if(nextIndex<0)throw new Error("The selected moment is missing from this publication");
    next.frames.forEach(moment=>{moment.scars=moment.scars.map(s=>({...next.scars[s.id],...s}));});
    const changed=!data||next.journal_head!==data.journal_head||next.source_head!==data.source_head;
    $("error").hidden=true;
    if(changed){
      data=next;index=nextIndex;
      $("history").max=data.frames.length;$("history").disabled=false;
      if(!controlsReady)bindControls();
      refreshView(true);
    }else if(current)refreshView();
  }catch(error){
    $("error").hidden=false;
    $("error").textContent=data?"A newer record could not be loaded. The last remembered snapshot is still here; we’ll try again shortly.":"The house record is unavailable. We’ll try again shortly.";
    if(!data)$("presence-line").textContent="The record is unavailable; no activity is invented.";
    else if(current)refreshView();
  }finally{refreshing=false;}
}
let watching=false;
// Poll the tiny head.json; fetch the full history only when the record moved.
async function watch() {
  if(watching||refreshing||!data)return;
  watching=true;
  try {
    const response=await fetch(`head.json?t=${Date.now()}`,{cache:"no-store",signal:AbortSignal.timeout(5000)});
    if(!response.ok)return;
    const head=await response.json();
    if(head&&typeof head.journal_head==="string"&&
       (head.journal_head!==data.journal_head||head.source_head!==data.source_head))await refresh();
  }catch(error){}finally{watching=false;}
}
refresh();
setInterval(refresh,60000);setInterval(watch,10000);
