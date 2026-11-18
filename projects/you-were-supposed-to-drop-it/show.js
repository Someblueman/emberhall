(function () {
  'use strict';

  const rig = window.DropItRig;
  const SVG_NS = 'http://www.w3.org/2000/svg';

  const state = rig.createShowState({
    leadRig: 'rook',
    initialCast: { A: 0, B: 1, C: 2 },
  });

  let selectedPuppet = 'D';
  let replayTimer = null;

  const el = {
    leadRook: document.getElementById('lead-rook'),
    leadShrikhande: document.getElementById('lead-shrikhande'),
    btnStartPlay: document.getElementById('btn-start-play'),
    btnNewTake: document.getElementById('btn-new-take'),
    btnReblock: document.getElementById('btn-reblock'),
    blockingPanel: document.getElementById('blocking-panel'),
    playPanel: document.getElementById('play-panel'),
    castTray: document.getElementById('cast-tray'),
    fitReport: document.getElementById('fit-report'),
    btnBenchDot: document.getElementById('btn-bench-dot'),
    btnResetThree: document.getElementById('btn-reset-three'),
    receiverRow: document.getElementById('receiver-row'),
    btnHoldBeat: document.getElementById('btn-hold-beat'),
    btnPrevStill: document.getElementById('btn-prev-still'),
    btnReplayTake: document.getElementById('btn-replay-take'),
    btnNextStill: document.getElementById('btn-next-still'),
    beatStrip: document.getElementById('beat-strip'),
    beatReadout: document.getElementById('beat-readout'),
    curtainAudit: document.getElementById('curtain-live-audit'),
  };

  function markCoord(index) {
    const row = Math.floor(index / 4);
    const col = index % 4;
    const y = 165 + row * 22;
    const halfSpan = 96 + row * 12;
    const x = 180 + ((col - 1.5) / 1.5) * halfSpan;
    return { x, y, row, col };
  }

  function svgEl(tag, attrs = {}) {
    const node = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) {
      node.setAttribute(k, String(v));
    }
    return node;
  }

  function stopReplay() {
    if (replayTimer !== null) {
      clearInterval(replayTimer);
      replayTimer = null;
      el.btnReplayTake.textContent = 'Replay actual take';
    }
  }

  function currentSnapshot() {
    if (!state.inPlay || state.beats.length === 0) return null;
    return rig.stepTake(state, state.cursor);
  }

  function rigTitle(rigName) {
    return rigName === 'rook' ? 'Stage I' : 'Stage II';
  }

  function describeFitReport() {
    const r = state.lastFitReport;
    if (!r) {
      return 'Pip (A), Bess (B), and Gus (C) stand on matched marks. Dot (D) waits in the wings.';
    }
    const pName = `${rig.PUPPET_META[r.puppet].name} (${r.puppet})`;
    const rivalName = rigTitle(r.rivalRig);
    const markNum = state.marks[state.leadRig][r.puppet] + 1;
    if (r.exact) {
      return `${pName} moved to mark ${markNum}. ${rivalName} matched every wire and gap while keeping the others planted.`;
    }
    const keptNames = r.settled
      .filter((p) => !r.missedAgainst.includes(p))
      .map((p) => rig.PUPPET_META[p].name);
    const missedNames = r.missedAgainst.map((p) => rig.PUPPET_META[p].name);
    return `${pName} took mark ${markNum}. ${rivalName} kept ${keptNames.join(' & ')}'s ties, and could not match ${missedNames.join(' & ')}.`;
  }

  function drawBowler(g, x, y, scale = 1, tilt = 0) {
    const wrap = svgEl('g', {
      transform: `translate(${x.toFixed(1)}, ${y.toFixed(1)}) rotate(${tilt}) scale(${scale})`,
    });
    wrap.appendChild(svgEl('path', {
      d: 'M-12 2 Q0 5 12 2 L13 4 Q0 8 -13 4 Z',
      fill: '#1b1614',
      stroke: '#f4ebd7',
      'stroke-width': '0.9',
    }));
    wrap.appendChild(svgEl('path', {
      d: 'M-8 2 C-8 -9 8 -9 8 2 Z',
      fill: '#231d1a',
      stroke: '#f4ebd7',
      'stroke-width': '0.8',
    }));
    wrap.appendChild(svgEl('path', {
      d: 'M-7.8 0.2 H7.8',
      stroke: '#b7832e',
      'stroke-width': '1.6',
    }));
    g.appendChild(wrap);
  }

  function drawPuppet(g, puppetId, x, y, opts) {
    const meta = rig.PUPPET_META[puppetId];
    const isHolding = opts.holder === puppetId;
    const isSelected = opts.selected === puppetId && !state.inPlay;
    const isWings = opts.inWings;

    const grp = svgEl('g', {
      transform: `translate(${x.toFixed(1)}, ${y.toFixed(1)})`,
      opacity: isWings ? '0.86' : '1',
    });

    // Cut-paper floor shadow
    grp.appendChild(svgEl('ellipse', {
      cx: 0, cy: 1, rx: 11, ry: 3.5,
      fill: 'rgba(34, 25, 20, 0.25)',
    }));

    if (isSelected) {
      grp.appendChild(svgEl('ellipse', {
        cx: 0, cy: 1, rx: 14, ry: 5,
        fill: 'none', stroke: '#7b1e1b', 'stroke-width': '1.8', 'stroke-dasharray': '3 2',
      }));
    }

    // Articulated cut-paper body silhouette per puppet
    if (puppetId === 'A') {
      grp.appendChild(svgEl('path', {
        d: 'M-8 -4 L-6 -26 L6 -26 L8 -4 L4 -4 L3 -13 L-3 -13 L-4 -4 Z',
        fill: meta.color, stroke: '#f7efd9', 'stroke-width': '1',
      }));
      grp.appendChild(svgEl('path', {
        d: 'M6 -23 L13 -31',
        stroke: '#f7efd9', 'stroke-width': '2.2', 'stroke-linecap': 'round',
      }));
    } else if (puppetId === 'B') {
      grp.appendChild(svgEl('path', {
        d: 'M-10 -6 L-4 -25 L4 -25 L10 -6 Z',
        fill: meta.color, stroke: '#f7efd9', 'stroke-width': '1',
      }));
      grp.appendChild(svgEl('path', {
        d: 'M-3 -6 V-1 M3 -6 V-1',
        stroke: '#2c2019', 'stroke-width': '2',
      }));
    } else if (puppetId === 'C') {
      grp.appendChild(svgEl('path', {
        d: 'M-7 -4 L-7 -25 L7 -25 L7 -4 L2 -4 L0 -12 L-2 -4 Z',
        fill: meta.color, stroke: '#f7efd9', 'stroke-width': '1',
      }));
      grp.appendChild(svgEl('path', {
        d: 'M-7 -18 H7 M-7 -13 H7',
        stroke: '#f7efd9', 'stroke-width': '1', opacity: '0.65',
      }));
    } else {
      grp.appendChild(svgEl('path', {
        d: 'M-6 -4 L-8 -23 L8 -23 L6 -4 Z',
        fill: meta.color, stroke: '#f7efd9', 'stroke-width': '1',
      }));
      grp.appendChild(svgEl('rect', {
        x: -10, y: -15, width: 6, height: 8, rx: 1,
        fill: '#8f5f34', stroke: '#f7efd9', 'stroke-width': '0.8',
      }));
    }

    // Head
    grp.appendChild(svgEl('circle', {
      cx: 0, cy: -31, r: 5.8,
      fill: '#f5dfc0', stroke: '#221914', 'stroke-width': '1.1',
    }));

    // Brass paper fastener pin on chest
    grp.appendChild(svgEl('circle', {
      cx: 0, cy: -21, r: 1.8,
      fill: '#f4c867', stroke: '#4d3310', 'stroke-width': '0.7',
    }));

    // Letter badge below feet
    grp.appendChild(svgEl('rect', {
      x: -7, y: -12, width: 14, height: 10, rx: 2,
      fill: '#221914', stroke: '#f4ebd7', 'stroke-width': '0.8',
    }));
    const lbl = svgEl('text', {
      x: 0, y: -4.5, 'text-anchor': 'middle',
      fill: '#fff6e5', 'font-size': '7.5', 'font-weight': '700',
      'font-family': 'Helvetica Neue, Arial, sans-serif',
    });
    lbl.textContent = puppetId;
    grp.appendChild(lbl);

    if (isHolding) {
      grp.appendChild(svgEl('circle', {
        cx: 0, cy: -31, r: 9.5,
        fill: 'none', stroke: '#f4c867', 'stroke-width': '1.6', opacity: '0.9',
      }));
    }

    g.appendChild(grp);
  }

  function drawDrummer(g, stageSnap) {
    const slipped = stageSnap ? stageSnap.landedOnDrummer : false;
    const isHold = stageSnap && stageSnap.lastAction === 'hold' && !slipped;

    const grp = svgEl('g', { transform: 'translate(180, 294)' });

    // Pit shadow & snare drum
    grp.appendChild(svgEl('ellipse', { cx: 0, cy: 20, rx: 32, ry: 7, fill: '#0e0a08' }));
    grp.appendChild(svgEl('rect', {
      x: -22, y: 2, width: 44, height: 18, rx: 3,
      fill: '#a63429', stroke: '#f4c867', 'stroke-width': '1.5',
    }));
    grp.appendChild(svgEl('ellipse', {
      cx: 0, cy: 2, rx: 22, ry: 5,
      fill: '#efe0be', stroke: '#4c341a', 'stroke-width': '1.2',
    }));

    // Drummer torso
    grp.appendChild(svgEl('path', {
      d: 'M-15 2 L-11 -18 L11 -18 L15 2 Z',
      fill: '#2f3d4c', stroke: '#d8c5a3', 'stroke-width': '1',
    }));

    // Head
    const headY = slipped ? -21 : -24;
    grp.appendChild(svgEl('circle', {
      cx: 0, cy: headY, r: 8.5,
      fill: '#f5dfc0', stroke: '#1b1411', 'stroke-width': '1.2',
    }));

    if (!slipped) {
      // Wide anticipatory eyes
      grp.appendChild(svgEl('circle', { cx: -3, cy: headY - 1, r: 1.3, fill: '#1b1411' }));
      grp.appendChild(svgEl('circle', { cx: 3, cy: headY - 1, r: 1.3, fill: '#1b1411' }));
      // Raised drumsticks
      const lift = isHold ? -39 : -35;
      grp.appendChild(svgEl('line', {
        x1: -11, y1: -10, x2: -20, y2: lift,
        stroke: '#f3d49b', 'stroke-width': '2.2', 'stroke-linecap': 'round',
      }));
      grp.appendChild(svgEl('line', {
        x1: 11, y1: -10, x2: 20, y2: lift,
        stroke: '#f3d49b', 'stroke-width': '2.2', 'stroke-linecap': 'round',
      }));
      grp.appendChild(svgEl('circle', { cx: -20, cy: lift, r: 2.3, fill: '#fff6e5' }));
      grp.appendChild(svgEl('circle', { cx: 20, cy: lift, r: 2.3, fill: '#fff6e5' }));
    } else {
      // Dropped sticks, bowler jammed right over eyes!
      grp.appendChild(svgEl('line', {
        x1: -12, y1: -8, x2: -25, y2: 0,
        stroke: '#d6b681', 'stroke-width': '2', 'stroke-linecap': 'round',
      }));
      grp.appendChild(svgEl('line', {
        x1: 12, y1: -8, x2: 26, y2: -2,
        stroke: '#d6b681', 'stroke-width': '2', 'stroke-linecap': 'round',
      }));
      drawBowler(grp, 0, headY - 3, 1.12, -4);
    }

    g.appendChild(grp);
  }

  function renderStage(rigName, snap) {
    const card = document.getElementById(`card-${rigName}`);
    const roleEl = document.getElementById(`role-${rigName}`);
    const statusEl = document.getElementById(`status-${rigName}`);
    const captionEl = document.getElementById(`caption-${rigName}`);

    const marksLayer = document.getElementById(`marks-layer-${rigName}`);
    const wireLayer = document.getElementById(`wire-layer-${rigName}`);
    const puppetsLayer = document.getElementById(`puppets-layer-${rigName}`);
    const drummerLayer = document.getElementById(`drummer-layer-${rigName}`);
    const hatLayer = document.getElementById(`hat-layer-${rigName}`);
    const buttonsLayer = document.getElementById(`buttons-${rigName}`);

    const isLeading = state.leadRig === rigName;
    const stageSnap = snap ? snap[rigName] : null;
    const slipped = stageSnap ? stageSnap.landedOnDrummer : false;

    card.classList.toggle('is-leading', isLeading);
    card.classList.toggle('has-slipped', slipped);
    roleEl.textContent = isLeading ? 'Leading troupe' : 'Rival troupe';

    if (!state.inPlay) {
      statusEl.textContent = isLeading ? 'Blocking cast' : 'Matching';
      statusEl.className = 'stage-pill';
      if (isLeading) {
        captionEl.textContent = state.castOrder.includes('D')
          ? 'Four on marks. Move anyone or put the hat in play.'
          : 'Three on marks. Bring Dot (D) out or move any puppet.';
      } else {
        captionEl.textContent = state.lastFitReport && !state.lastFitReport.exact && state.lastFitReport.rivalRig === rigName
          ? `Could not match ${state.lastFitReport.missedAgainst.join(' & ')} — kept longest-serving ties.`
          : 'Every seated wire and gap currently matches.';
      }
    } else if (stageSnap) {
      if (slipped) {
        statusEl.textContent = 'Hat slipped!';
        statusEl.className = 'stage-pill slipped';
        captionEl.textContent = 'No wire for that throw — bowler landed on the pit drummer!';
      } else if (stageSnap.lastAction === 'caught') {
        statusEl.textContent = `Caught by ${stageSnap.holder}`;
        statusEl.className = 'stage-pill caught';
        captionEl.textContent = `${rig.PUPPET_META[stageSnap.holder].name} (${stageSnap.holder}) caught the bowler cleanly along the lit wire.`;
      } else if (stageSnap.lastAction === 'hold') {
        statusEl.textContent = 'Holding a beat';
        statusEl.className = 'stage-pill';
        captionEl.textContent = `Drummer waits with sticks raised; ${stageSnap.holder} holds the hat.`;
      } else {
        statusEl.textContent = `With ${stageSnap.holder}`;
        statusEl.className = 'stage-pill';
        captionEl.textContent = `${rig.PUPPET_META[stageSnap.holder].name} (${stageSnap.holder}) stands ready with the bowler.`;
      }
    }

    // Clear SVG layers & mark buttons
    marksLayer.innerHTML = '';
    wireLayer.innerHTML = '';
    puppetsLayer.innerHTML = '';
    drummerLayer.innerHTML = '';
    hatLayer.innerHTML = '';
    buttonsLayer.innerHTML = '';

    // Draw 16 floor marks (and interactive buttons on leading stage during blocking)
    for (let i = 0; i < 16; i += 1) {
      const { x, y } = markCoord(i);
      const occupant = rig.PUPPETS.find((p) => state.marks[rigName][p] === i) || null;

      marksLayer.appendChild(svgEl('ellipse', {
        cx: x, cy: y, rx: 11, ry: 4.5,
        fill: occupant ? 'rgba(34,25,20,0.22)' : 'rgba(255,248,231,0.45)',
        stroke: '#6c4d2d',
        'stroke-width': '1',
      }));

      // Tiny ceiling pin eyelet (unlit rigging socket)
      marksLayer.appendChild(svgEl('circle', {
        cx: x, cy: 38 + Math.floor(i / 4) * 3, r: 1.3,
        fill: '#9c7848', opacity: '0.45',
      }));

      if (isLeading && !state.inPlay) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'mark-btn';
        btn.style.left = `${(x / 360) * 100}%`;
        const topPct = (y / 340) * 100;
        btn.style.top = `${topPct}%`;
        btn.style.setProperty('--mark-top', `${topPct}%`);
        if (occupant) {
          btn.classList.add('is-occupied');
          if (occupant === selectedPuppet) btn.classList.add('is-selected-puppet');
          btn.textContent = occupant;
          btn.setAttribute('aria-label', `${rigTitle(rigName)} mark ${i + 1}, occupied by ${rig.PUPPET_META[occupant].name} (${occupant})`);
          btn.addEventListener('click', () => {
            selectedPuppet = occupant;
            renderAll();
          });
        } else {
          btn.textContent = String(i + 1);
          btn.setAttribute('aria-label', `Move ${rig.PUPPET_META[selectedPuppet].name} (${selectedPuppet}) to ${rigTitle(rigName)} mark ${i + 1}`);
          btn.addEventListener('click', () => {
            rig.placePuppet(state, selectedPuppet, i);
            renderAll();
          });
        }
        buttonsLayer.appendChild(btn);
      }
    }

    // Light ONLY the current wire when a catch happens
    if (stageSnap && stageSnap.litWire) {
      const fromCoord = markCoord(state.marks[rigName][stageSnap.litWire.from]);
      const toCoord = markCoord(state.marks[rigName][stageSnap.litWire.to]);
      const y1 = fromCoord.y - 34;
      const y2 = toCoord.y - 34;
      const midX = (fromCoord.x + toCoord.x) / 2;
      const ctrlY = Math.min(y1, y2) - 34;
      const d = `M${fromCoord.x.toFixed(1)} ${y1.toFixed(1)} Q${midX.toFixed(1)} ${ctrlY.toFixed(1)} ${toCoord.x.toFixed(1)} ${y2.toFixed(1)}`;
      wireLayer.appendChild(svgEl('path', {
        d, fill: 'none', stroke: 'rgba(244, 200, 103, 0.45)', 'stroke-width': '7', 'stroke-linecap': 'round',
      }));
      wireLayer.appendChild(svgEl('path', {
        d, fill: 'none', stroke: '#f4c867', 'stroke-width': '2.6', 'stroke-linecap': 'round',
      }));
    } else if (stageSnap && stageSnap.lastAction === 'slipped' && snap.from) {
      // Dotted fall line into the pit (no lit wire!)
      const fromMark = state.marks[rigName][snap.from];
      if (fromMark !== null) {
        const fc = markCoord(fromMark);
        wireLayer.appendChild(svgEl('path', {
          d: `M${fc.x.toFixed(1)} ${(fc.y - 34).toFixed(1)} Q${((fc.x + 180) / 2).toFixed(1)} 165 180 264`,
          fill: 'none', stroke: '#b5372f', 'stroke-width': '2', 'stroke-dasharray': '4 4',
        }));
      }
    }

    // Draw seated puppets sorted back-to-front by y so foreground overlaps naturally
    const seatedOrdered = state.castOrder
      .filter((p) => state.marks[rigName][p] !== null)
      .sort((a, b) => markCoord(state.marks[rigName][a]).y - markCoord(state.marks[rigName][b]).y);

    for (const p of seatedOrdered) {
      const c = markCoord(state.marks[rigName][p]);
      drawPuppet(puppetsLayer, p, c.x, c.y, {
        holder: stageSnap ? stageSnap.holder : null,
        selected: selectedPuppet,
        inWings: false,
      });
    }

    // Draw Dot waiting in the left wings if not seated
    if (!state.castOrder.includes('D')) {
      drawPuppet(puppetsLayer, 'D', 31, 198, {
        holder: null,
        selected: selectedPuppet,
        inWings: true,
      });
    }

    // Draw bowler on active holder's head
    if (stageSnap && stageSnap.holder && state.marks[rigName][stageSnap.holder] !== null) {
      const hc = markCoord(state.marks[rigName][stageSnap.holder]);
      drawBowler(hatLayer, hc.x, hc.y - 38, 0.9, -6);
    }

    drawDrummer(drummerLayer, stageSnap);
  }

  function renderCastTray() {
    el.castTray.innerHTML = '';
    for (const p of rig.PUPPETS) {
      const meta = rig.PUPPET_META[p];
      const onStage = state.castOrder.includes(p);
      const mark = state.marks[state.leadRig][p];
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'cast-btn' + (selectedPuppet === p ? ' selected' : '');
      btn.setAttribute('aria-pressed', String(selectedPuppet === p));

      const swatch = document.createElement('span');
      swatch.className = 'cast-swatch';
      swatch.style.backgroundColor = meta.color;

      const label = document.createElement('span');
      label.textContent = `${meta.name} (${p})`;

      const pos = document.createElement('span');
      pos.className = 'cast-meta';
      pos.textContent = onStage ? `Mark ${mark + 1}` : 'In wings';

      btn.append(swatch, label, pos);
      btn.addEventListener('click', () => {
        selectedPuppet = p;
        renderAll();
      });
      el.castTray.appendChild(btn);
    }

    el.btnBenchDot.disabled = !state.castOrder.includes('D');
    el.fitReport.textContent = describeFitReport();
  }

  function renderPlayControls(snap) {
    el.receiverRow.innerHTML = '';
    const activeHolders = new Set(
      ['rook', 'shrikhande']
        .filter((r) => !state.stageStatus[r].ended)
        .map((r) => state.stageStatus[r].holder)
    );
    const bothEnded = activeHolders.size === 0;
    const onlyHolder = activeHolders.size === 1 ? activeHolders.values().next().value : null;

    for (const p of state.castOrder) {
      const meta = rig.PUPPET_META[p];
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'pill-btn';
      const isHolder = onlyHolder === p;
      btn.disabled = bothEnded || isHolder;
      btn.textContent = isHolder ? `${meta.name} (${p}) · holds hat` : `Throw to ${meta.name} (${p})`;
      btn.addEventListener('click', () => {
        stopReplay();
        rig.throwHat(state, p);
        renderAll();
      });
      el.receiverRow.appendChild(btn);
    }

    el.btnHoldBeat.disabled = bothEnded;
    el.btnPrevStill.disabled = !snap || snap.index <= 0;
    el.btnNextStill.disabled = !snap || snap.index >= snap.total - 1;
    el.btnReplayTake.disabled = state.beats.length < 2;

    el.beatStrip.innerHTML = '';
    state.beats.forEach((beat, idx) => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'beat-chip';
      if (snap && snap.index === idx) chip.classList.add('active');
      if (beat.outcomes.rook === 'slipped' || beat.outcomes.shrikhande === 'slipped') {
        chip.classList.add('has-slip');
      }
      if (beat.kind === 'curtain-up') chip.textContent = '0 · Curtain';
      else if (beat.kind === 'hold') chip.textContent = `${idx} · Beat`;
      else chip.textContent = `${idx} · ${beat.from}→${beat.to}`;

      chip.setAttribute('aria-label', `Still ${idx + 1} of ${state.beats.length}: ${beat.note}`);
      chip.addEventListener('click', () => {
        stopReplay();
        rig.stepTake(state, idx);
        renderAll();
      });
      el.beatStrip.appendChild(chip);
    });

    if (snap) {
      el.beatReadout.textContent = `Still ${snap.index + 1} of ${snap.total}: ${snap.note}`;
    } else {
      el.beatReadout.textContent = '';
    }
  }

  function renderCurtainAudit() {
    const audit = rig.auditRigs();
    const pairs = rig.pairSummary(state);

    let html = `<p><strong>Verified 4-mark census (all ${audit.rook.totalSubsets.toLocaleString()} subsets per rig):</strong> ` +
      `Stage I (Rook) has <strong>${audit.rook.edgeCounts[6] || 0}</strong> sets with 6 wires and <strong>${audit.rook.edgeCounts[5] || 0}</strong> with 5; ` +
      `Stage II (Shrikhande) has <strong>${audit.shrikhande.edgeCounts[5] || 0}</strong> sets with 5 wires and <strong>${audit.shrikhande.edgeCounts[6] || 0}</strong> with 6.</p>`;

    if (pairs.length > 0) {
      html += '<table class="wire-table"><thead><tr><th>Pair</th><th>Stage I (Rook)</th><th>Stage II (Shrikhande)</th><th>Match</th></tr></thead><tbody>';
      for (const row of pairs) {
        html += `<tr><td>${row.pair}</td><td>${row.rook ? 'Wire' : 'Gap'}</td><td>${row.shrikhande ? 'Wire' : 'Gap'}</td><td>${row.matches ? 'Same' : 'Different'}</td></tr>`;
      }
      html += '</tbody></table>';
    }
    el.curtainAudit.innerHTML = html;
  }

  function renderAll() {
    const snap = currentSnapshot();

    el.leadRook.classList.toggle('active', state.leadRig === 'rook');
    el.leadRook.setAttribute('aria-pressed', String(state.leadRig === 'rook'));
    el.leadRook.disabled = state.inPlay;

    el.leadShrikhande.classList.toggle('active', state.leadRig === 'shrikhande');
    el.leadShrikhande.setAttribute('aria-pressed', String(state.leadRig === 'shrikhande'));
    el.leadShrikhande.disabled = state.inPlay;

    el.btnStartPlay.hidden = state.inPlay;
    el.btnStartPlay.disabled = state.castOrder.length < 2;
    el.btnNewTake.hidden = !state.inPlay;
    el.btnReblock.hidden = !state.inPlay;

    el.blockingPanel.hidden = state.inPlay;
    el.playPanel.hidden = !state.inPlay;

    renderStage('rook', snap);
    renderStage('shrikhande', snap);

    if (!state.inPlay) {
      renderCastTray();
    } else {
      renderPlayControls(snap);
    }
    renderCurtainAudit();
  }

  el.leadRook.addEventListener('click', () => {
    rig.setLeadRig(state, 'rook');
    renderAll();
  });

  el.leadShrikhande.addEventListener('click', () => {
    rig.setLeadRig(state, 'shrikhande');
    renderAll();
  });

  el.btnStartPlay.addEventListener('click', () => {
    stopReplay();
    rig.startHatPlay(state, state.castOrder[0]);
    renderAll();
  });

  el.btnNewTake.addEventListener('click', () => {
    stopReplay();
    rig.reblockCast(state);
    rig.startHatPlay(state, state.castOrder[0]);
    renderAll();
  });

  el.btnReblock.addEventListener('click', () => {
    stopReplay();
    rig.reblockCast(state);
    renderAll();
  });

  el.btnBenchDot.addEventListener('click', () => {
    rig.removePuppet(state, 'D');
    selectedPuppet = 'D';
    renderAll();
  });

  el.btnResetThree.addEventListener('click', () => {
    rig.removePuppet(state, 'A');
    rig.removePuppet(state, 'B');
    rig.removePuppet(state, 'C');
    rig.removePuppet(state, 'D');
    rig.placePuppet(state, 'A', 0);
    rig.placePuppet(state, 'B', 1);
    rig.placePuppet(state, 'C', 2);
    state.lastFitReport = null;
    selectedPuppet = 'D';
    renderAll();
  });

  el.btnHoldBeat.addEventListener('click', () => {
    stopReplay();
    rig.holdBeat(state);
    renderAll();
  });

  el.btnPrevStill.addEventListener('click', () => {
    stopReplay();
    rig.stepTake(state, state.cursor - 1);
    renderAll();
  });

  el.btnNextStill.addEventListener('click', () => {
    stopReplay();
    rig.stepTake(state, state.cursor + 1);
    renderAll();
  });

  el.btnReplayTake.addEventListener('click', () => {
    if (replayTimer !== null) {
      stopReplay();
      return;
    }
    if (state.beats.length < 2) return;
    let idx = 0;
    rig.stepTake(state, 0);
    renderAll();
    el.btnReplayTake.textContent = 'Pause replay';
    replayTimer = setInterval(() => {
      idx += 1;
      if (idx >= state.beats.length) {
        stopReplay();
        return;
      }
      rig.stepTake(state, idx);
      renderAll();
    }, 620);
  });

  renderAll();
})();
