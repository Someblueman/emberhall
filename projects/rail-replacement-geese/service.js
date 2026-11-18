/* The slider is the only clock. A fold always has the same drawing in either direction. */
(() => {
  "use strict";
  const ns = "http://www.w3.org/2000/svg";
  const stock = document.querySelector("#rolling-stock");
  const slider = document.querySelector("#tab");
  const ink = "#243e38", green = "#386359", ivory = "#f6e9c9", brass = "#dbac60";

  function element(parent, tag, attributes = {}) {
    const node = document.createElementNS(ns, tag);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    parent.appendChild(node);
    return node;
  }
  const lift = (a, b, t) => a + (b - a) * t;
  function fold(t, from, to) {
    const u = Math.max(0, Math.min(1, (t - from) / (to - from)));
    return u * u * (3 - 2 * u);
  }

  // Each point has a place on a carriage and a place on the bird. The command
  // letters and their order stay fixed as the creases open.
  function paper(parent, commands, rail, air, fill, stroke = ink, width = 1.8) {
    const node = element(parent, "path", {fill, stroke, "stroke-width":width,
      "stroke-linejoin":"round", "stroke-linecap":"round"});
    return progress => {
      let i = 0;
      node.setAttribute("d", commands.replace(/@/g, () => {
        const value = lift(rail[i], air[i], progress);
        i++;
        return value.toFixed(2);
      }));
    };
  }

  const treeLine = document.querySelector("#trees");
  for (const [x,y,s] of [[14,166,.76],[34,181,.46],[65,177,.53],[102,186,.42],
      [281,178,.55],[294,169,.65],[314,184,.43],[512,172,.52],[526,161,.74],
      [547,179,.44],[692,164,.72],[713,154,.88],[737,173,.62]]) {
    element(treeLine, "use", {href:"#pine", transform:`translate(${x} ${y}) scale(${s})`});
  }

  function coach(dining, livery) {
    const frame = element(stock, "g");
    const drawings = [];
    const piece = (...args) => drawings.push(paper(frame, ...args));

    // Far wing folds out first behind the roof.
    piece("M@ @ Q@ @ @ @ L@ @ Q@ @ @ @ Z",
      [-64,-28,-14,-36,56,-31,69,-24,6,-18,-64,-28],
      [-24,-6,8,-45,30,-83,38,-69,31,-29,5,-7], "#9aa594");
    // Underframe. In flight its tapered ends form the breast and tail.
    piece("M@ @ Q@ @ @ @ L@ @ Q@ @ @ @ L@ @ Q@ @ @ @ L@ @ Q@ @ @ @ Z",
      [-75,-27,-78,-28,-78,-17,-78,6,-76,12,-65,12,70,12,78,12,78,4,78,-21,78,-28,69,-27],
      [-48,-13,-58,-10,-51,0,-34,11,-16,23,11,17,70,-4,61,-13,44,-12,29,-14,-1,-17,-22,-12], livery);
    piece("M@ @ Q@ @ @ @ Q@ @ @ @ L@ @ Q@ @ @ @ Z",
      [-74,2,-1,2,73,2,75,5,72,8,-70,8,-75,8,-74,2],
      [-49,0,-32,16,-8,17,7,17,20,13,43,1,0,8,-49,0], ivory, "none");

    // The buffer and its mounting plate unfold into the neck, cheek and bill.
    piece("M@ @ Q@ @ @ @ Q@ @ @ @ Q@ @ @ @ Q@ @ @ @ L@ @ Q@ @ @ @ Z",
      [-58,-20,-73,-18,-78,-8,-80,-5,-84,-5,-88,-5,-87,1,-86,5,-78,5,-69,5,-57,5,-54,-2],
      [-22,-8,-45,-5,-62,-20,-77,-32,-95,-28,-112,-24,-111,-14,-109,-7,-95,-10,-82,-16,-55,17,-33,9], green);
    piece("M@ @ Q@ @ @ @ Q@ @ @ @ Z",
      [-84,-2,-81,-3,-76,-3,-77,2,-84,2],
      [-106,-13,-100,-18,-87,-17,-91,-9,-106,-13], ivory, "none");
    piece("M@ @ Q@ @ @ @ L@ @ Z",
      [-86,-3,-92,-3,-95,0,-86,2],
      [-109,-19,-119,-19,-124,-14,-109,-13], brass);
    const eye = element(frame, "circle", {r:2, fill:ink});
    const brow = element(frame, "path", {stroke:ink,"stroke-width":1.5,fill:"none","stroke-linecap":"round"});
    drawings.push(f => {
      eye.setAttribute("cx", lift(-83,-104,f)); eye.setAttribute("cy", lift(-1,-20,f));
    });

    // Coach windows travel with the body. A dining saloon keeps its china in
    // the window while the other roofs are already in the sky.
    const glazing = element(frame, "g");
    for (let i = 0; i < 5; i++) {
      const x = -61 + i * 25;
      element(glazing, "rect", {x, y:-24, width:19, height:17, rx:2, fill:i % 2 ? "#edc882" : "#f0dbac", stroke:ink, "stroke-width":1.3});
      element(glazing, "path", {d:`M${x+2} -22h15l-4 4H${x+2}z`, fill:"#b98451"});
      if (dining && i % 2 === 0) {
        element(glazing, "path", {d:`M${x+3} -13h12q-1 5-6 5t-6-5z`, fill:ivory, stroke:ink, "stroke-width":.9});
        element(glazing, "path", {d:`M${x+12} -13l4-5`, stroke:ink, "stroke-width":1.3});
      } else {
        element(glazing, "path", {d:`M${x+4} -9l8-10`, stroke:ivory,"stroke-width":1.8});
      }
    }
    drawings.push(f => glazing.setAttribute("transform", `translate(${f*2} ${f*3}) rotate(${-f*12}) scale(${1-.63*f} ${1-.67*f})`));

    // The wheelsets fold against the belly, into the goose's tucked webbed feet.
    for (const x of [-50,49]) {
      const axle = element(frame, "g");
      element(axle, "circle", {r:9,fill:ink,stroke:"#f0dbac","stroke-width":1.2});
      element(axle, "circle", {r:4,fill:brass});
      element(axle, "path", {d:"M-6 0H6M0-6V6",stroke:ivory,"stroke-width":1.2});
      drawings.push(f => axle.setAttribute("transform",
        `translate(${lift(x,x<0?8:21,f)} ${lift(13,17,f)}) rotate(${-22*f}) scale(${1-.43*f} ${1-.70*f})`));
    }

    // The ribbed green roof is the near wing. Its four roof seams make four
    // individually visible feather tips. It never disappears behind a second image.
    piece("M@ @ Q@ @ @ @ Q@ @ @ @ L@ @ L@ @ L@ @ L@ @ L@ @ L@ @ Q@ @ @ @ Z",
      [-80,-27,-79,-35,-64,-36,0,-39,69,-35,80,-29,64,-29,60,-28,40,-28,34,-27,10,-27,-42,-23,-80,-27],
      [-40,-1,-38,-24,-15,-35,18,-49,50,-96,40,-64,57,-77,43,-51,58,-58,40,-37,48,-39,6,-1,-40,-1], livery);
    piece("M@ @ Q@ @ @ @ Q@ @ @ @",
      [-67,-33,-14,-36,45,-34,59,-34,72,-32],
      [-34,-10,-18,-26,8,-35,26,-48,42,-71], "none", ivory, 2.5);
    for (let i = 0; i < 4; i++) {
      const a = -32 + i * 23;
      piece("M@ @ Q@ @ @ @",
        [a,-34,a+4,-32,a+5,-28],
        [-26+i*8,-7-i*3,-3+i*8,-11-i*6,20+i*7,-35-i*9], "none", "#9bb39a", 1.2);
    }
    const plate = element(frame, "g");
    if (dining) {
      element(plate, "rect", {x:-57,y:-6,width:114,height:17,rx:3,fill:ivory,stroke:ink,"stroke-width":1.4});
      const label = element(plate,"text",{x:0,y:6,"text-anchor":"middle","font-family":"Georgia,serif",
        "font-weight":"bold","font-size":13,"letter-spacing":1,fill:ink});
      label.textContent = "DINING CAR";
      drawings.push(f => plate.setAttribute("transform",
        `translate(${f*8} ${f*1.5}) rotate(${f*-12}) scale(${1-.56*f})`));
    } else {
      element(plate,"path",{d:"M-65-4H65",stroke:brass,"stroke-width":2});
      drawings.push(f => plate.setAttribute("transform",`translate(0 ${8*f}) rotate(${-12*f}) scale(${1-.63*f} 1)`));
    }

    return (x,y,angle,scale,opening,load = 0) => {
      frame.setAttribute("transform",`translate(${x} ${y}) rotate(${angle}) scale(${scale})`);
      drawings.forEach(draw => draw(opening));
      const ex = Number(eye.getAttribute("cx")), ey = Number(eye.getAttribute("cy"));
      brow.setAttribute("d", `M${ex-2.7} ${ey-3.5}q2 ${-1+load*2.7} 6 ${-load*2.8}`);
      // A pin on the near end of the saloon and the tip of the following bill.
      const local = dining ? [76, -1] : [lift(-94,-123,opening), lift(0,-14,opening)];
      const rad = angle * Math.PI / 180;
      return [x+scale*(local[0]*Math.cos(rad)-local[1]*Math.sin(rad)),
              y+scale*(local[0]*Math.sin(rad)+local[1]*Math.cos(rad))];
    };
  }

  const dining = coach(true, "#8f4936");
  const porter = coach(false, "#315e55");
  const guard = coach(false, "#477369");
  const rope = document.querySelector("#rope"), edge = document.querySelector("#rope-edge");
  const bolt = document.querySelector("#bolt"), description = document.querySelector("#scene-description");

  function draw() {
    const t = Number(slider.value)/100;
    const early = fold(t,0,.46), late = fold(t,.56,1);
    const bob = Math.sin(Math.PI*late);
    const saloonPin = dining(181+53*early-40*late,280-60*early-35*late,
      -17*early+13*late,1-.10*early-.08*late,late);
    const bill = porter(367+55*early-5*late,280-129*early-9*late,
      7*early-8*late,1-.10*early,fold(t,.035,.40),early*(1-late));
    guard(553+55*early+12*late,280-105*early-61*late,
      -5*early+7*late,1-.19*early,fold(t,0,.34));

    // While the saloon flies under its own power, the free end of the same
    // coupling swings back towards the porter's cheek like a red pennant.
    const release = fold(t,.59,.89);
    const endX = lift(saloonPin[0],bill[0]+37,release);
    const endY = lift(saloonPin[1],bill[1]+8,release);
    const sag = 3 + 7*early + 7*bob;
    const line = `M${bill[0]} ${bill[1]} Q${(bill[0]+endX)/2-5*early} ${Math.max(bill[1],endY)+sag} ${endX} ${endY}`;
    rope.setAttribute("d",line); edge.setAttribute("d",line);
    bolt.setAttribute("cx",endX); bolt.setAttribute("cy",endY);
    const descriptionText = t===0 ? "Three railway carriages stand on the track above a frozen mere."
      : t===1 ? "Three geese fly over the empty rails. A red coupling trails from the middle bird."
      : t<.36 ? "Two coach roofs are lifting into wings. The red coupling is pulling the last coach off the rails."
      : t<=.57 ? "A goose grips the red coupling in its bill. The tilted dining car dangles from the other end, soup bowls still in the windows."
      : "The dining car unfolds its own wing. The end of the red coupling swings free.";
    description.textContent = descriptionText;
    slider.setAttribute("aria-valuetext",`${slider.value} percent. ${descriptionText}`);
  }
  slider.addEventListener("input",draw);
  draw();
  document.documentElement.classList.add("live");
})();
