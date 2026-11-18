/* A finite chart for a fictional two-dimensional Klein-bottle town. */
"use strict";
const GloveWorld = (() => {
  const size=5, home=2;
  const start=()=>({x:home,y:home,turned:false,steps:0,delivered:false});
  const atCounter=s=>s.x===home&&s.y===home;
  function move(s,direction) {
    const offsets={east:[1,0],west:[-1,0],north:[0,-1],south:[0,1]};
    if(!Object.hasOwn(offsets,direction))throw new RangeError("Unknown direction");
    if(s.delivered)return s;
    const [dx,dy]=offsets[direction];
    let x=s.x+dx,y=s.y,turned=s.turned;
    if(x<0||x>=size){x=(x+size)%size;y=size-1-y;turned=!turned;}
    y=(y+dy+size)%size;
    return {...s,x,y,turned,steps:s.steps+1};
  }
  const fits=s=>s.turned;
  const deliver=s=>atCounter(s)&&fits(s)?{...s,delivered:true}:s;
  return {size,home,start,move,atCounter,fits,deliver};
})();
if(typeof module!=="undefined")module.exports=GloveWorld;
