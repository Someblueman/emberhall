/* Pure, dependency-free SVG reach map and evidence-bridge view model for Night Ferry.
 * Works in Node (CommonJS) and browser (<script defer>) without touching DOM or network.
 * Never reads truth.deduction or truth.facts[].statement so spoilers cannot leak.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  }
  if (root) {
    root.NightFerryReach = api;
    if (root.window && root.window !== root) {
      root.window.NightFerryReach = api;
    }
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function escapeXml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }

  function buildReachViewModel(truth, scenes, activeSceneId, citedKeys) {
    const cited = citedKeys instanceof Set ? citedKeys : new Set(citedKeys || []);
    const sceneEntries = truth && Array.isArray(truth.scenes) ? truth.scenes : [];
    const accounts = sceneEntries.map(function (entry) {
      const scene = scenes && typeof scenes.get === 'function' ? scenes.get(entry.id) : null;
      const statements = scene && Array.isArray(scene.statements) ? scene.statements : [];
      let citedCount = 0;
      statements.forEach(function (_st, idx) {
        if (cited.has(entry.id + '#' + idx)) citedCount += 1;
      });
      return {
        id: entry.id,
        title: (scene && scene.title) || entry.title || entry.id,
        perspective: (scene && scene.perspective) || entry.id,
        statementCount: statements.length,
        citedCount: citedCount,
        factIds: statements.map(function (st) { return st.fact; }),
        active: activeSceneId === entry.id,
      };
    });

    const factIds = (truth && Array.isArray(truth.facts) ? truth.facts : []).map(function (f) {
      return f.id;
    });

    const facts = factIds.map(function (factId) {
      let shoreCited = false;
      let engineCited = false;
      let shoreAvailable = false;
      let engineAvailable = false;
      sceneEntries.forEach(function (entry) {
        const scene = scenes && typeof scenes.get === 'function' ? scenes.get(entry.id) : null;
        const statements = scene && Array.isArray(scene.statements) ? scene.statements : [];
        statements.forEach(function (st, idx) {
          if (st.fact !== factId) return;
          const isShore = entry.id === 'landing-clerk' || (scene && scene.perspective === 'shore');
          if (isShore) {
            shoreAvailable = true;
            if (cited.has(entry.id + '#' + idx)) shoreCited = true;
          } else {
            engineAvailable = true;
            if (cited.has(entry.id + '#' + idx)) engineCited = true;
          }
        });
      });
      return {
        id: factId,
        shoreAvailable: shoreAvailable,
        engineAvailable: engineAvailable,
        shoreCited: shoreCited,
        engineCited: engineCited,
        cited: shoreCited || engineCited,
      };
    });

    const isMothCase = Boolean(truth && truth.case === 'moth-last-crossing');
    const beacons = isMothCase
      ? [
          { id: 'north', name: 'North Landing', pattern: 'steady white', kind: 'white' },
          { id: 'south', name: 'South Pier', pattern: 'steady amber', kind: 'amber' },
          { id: 'orchard', name: 'Orchard Float', pattern: '2 short white flashes', kind: 'flash' },
        ]
      : [];

    return {
      caseId: truth ? truth.case : '',
      caseTitle: truth ? truth.title : '',
      isMothCase: isMothCase,
      accounts: accounts,
      facts: facts,
      citedFactsCount: facts.filter(function (f) { return f.cited; }).length,
      beacons: beacons,
    };
  }

  function renderFactBridge(vmState, yBase) {
    const parts = [];
    const total = vmState.facts.length || 6;
    parts.push(
      '<text x="24" y="' + yBase + '" fill="#b5b9a5" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11" letter-spacing="1.1">EVIDENCE BRIDGE</text>'
    );
    parts.push(
      '<text x="776" y="' + yBase + '" fill="#e1ac64" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11.5" font-weight="600" text-anchor="end">' +
        vmState.citedFactsCount + ' / ' + total + ' facts cited</text>'
    );

    const accounts = vmState.accounts;
    const activeAcct = accounts.find(function (a) { return a.active; });
    const activeLabel = activeAcct ? 'Reading: ' + activeAcct.title : 'Choose an account';
    parts.push(
      '<text x="200" y="' + yBase + '" fill="#eee4cb" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11">' +
        escapeXml(activeLabel) + '</text>'
    );

    const startX = 24;
    const gap = 12;
    const boxW = Math.floor((752 - gap * (total - 1)) / total);
    const boxY = yBase + 12;

    vmState.facts.forEach(function (fact, idx) {
      const x = startX + idx * (boxW + gap);
      const stroke = fact.cited ? '#e1ac64' : '#516259';
      const fill = fact.cited ? '#233a35' : '#132423';
      const textFill = fact.cited ? '#eee4cb' : '#b5b9a5';
      parts.push('<rect x="' + x + '" y="' + boxY + '" width="' + boxW + '" height="48" rx="7" fill="' + fill + '" stroke="' + stroke + '" stroke-width="1.25"/>');
      parts.push(
        '<text x="' + (x + boxW / 2) + '" y="' + (boxY + 20) + '" fill="' + textFill + '" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="13" font-weight="700" text-anchor="middle">' +
          escapeXml(fact.id) + '</text>'
      );
      const shoreDot = fact.shoreCited ? '#e1ac64' : fact.shoreAvailable ? '#5c7066' : '#263834';
      const engineDot = fact.engineCited ? '#a9d8b0' : fact.engineAvailable ? '#5c7066' : '#263834';
      parts.push('<circle cx="' + (x + boxW / 2 - 14) + '" cy="' + (boxY + 35) + '" r="3.5" fill="' + shoreDot + '"/>');
      parts.push('<text x="' + (x + boxW / 2 - 6) + '" y="' + (boxY + 38.5) + '" fill="#93a094" font-family="ui-sans-serif,system-ui,sans-serif" font-size="9">S</text>');
      parts.push('<circle cx="' + (x + boxW / 2 + 8) + '" cy="' + (boxY + 35) + '" r="3.5" fill="' + engineDot + '"/>');
      parts.push('<text x="' + (x + boxW / 2 + 16) + '" y="' + (boxY + 38.5) + '" fill="#93a094" font-family="ui-sans-serif,system-ui,sans-serif" font-size="9">E</text>');
    });
    return parts.join('');
  }

  function renderMothReachChannel(yOffset) {
    const parts = [];
    // Dark river reach band
    parts.push('<rect x="24" y="' + yOffset + '" width="752" height="132" rx="10" fill="#102020" stroke="#364a44" stroke-width="1"/>');
    // Subtle river contour curve around the bend
    parts.push(
      '<path d="M 38 ' + (yOffset + 86) + ' C 210 ' + (yOffset + 92) + ', 320 ' + (yOffset + 42) + ', 440 ' + (yOffset + 58) + ' S 630 ' + (yOffset + 74) + ', 756 ' + (yOffset + 48) + '" fill="none" stroke="#1e3c3c" stroke-width="26" stroke-linecap="round"/>'
    );
    parts.push(
      '<path d="M 118 ' + (yOffset + 82) + ' C 250 ' + (yOffset + 78) + ', 340 ' + (yOffset + 54) + ', 430 ' + (yOffset + 56) + '" fill="none" stroke="#e1ac64" stroke-opacity="0.5" stroke-width="2" stroke-dasharray="5,5"/>'
    );
    // Split dashed tracks after the bend (never reveals which berth Moth visited)
    parts.push(
      '<path d="M 438 ' + (yOffset + 56) + ' Q 530 ' + (yOffset + 34) + ' 610 ' + (yOffset + 36) + '" fill="none" stroke="#87917b" stroke-opacity="0.6" stroke-width="1.6" stroke-dasharray="4,5"/>'
    );
    parts.push(
      '<path d="M 438 ' + (yOffset + 56) + ' Q 530 ' + (yOffset + 86) + ' 610 ' + (yOffset + 96) + '" fill="none" stroke="#87917b" stroke-opacity="0.6" stroke-width="1.6" stroke-dasharray="4,5"/>'
    );

    // Bend / sightline boundary
    parts.push('<line x1="406" y1="' + (yOffset + 16) + '" x2="406" y2="' + (yOffset + 116) + '" stroke="#e1ac64" stroke-opacity="0.35" stroke-width="1.2" stroke-dasharray="3,4"/>');
    parts.push('<text x="406" y="' + (yOffset + 124) + '" fill="#93a094" font-family="ui-sans-serif,system-ui,sans-serif" font-size="9.5" text-anchor="middle">channel bend · unseen from north desk</text>');

    // North Landing beacon (steady white)
    parts.push('<circle cx="96" cy="' + (yOffset + 76) + '" r="16" fill="#f7f4e8" fill-opacity="0.16"/>');
    parts.push('<circle cx="96" cy="' + (yOffset + 76) + '" r="6" fill="#fffdf5" stroke="#b5b9a5" stroke-width="1.5"/>');
    parts.push('<text x="40" y="' + (yOffset + 32) + '" fill="#eee4cb" font-family="Georgia,serif" font-size="14">North Landing</text>');
    parts.push('<text x="40" y="' + (yOffset + 48) + '" fill="#b5b9a5" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11">22:00 departure · steady white</text>');

    // Moth hull silhouette leaving North Landing
    parts.push('<polygon points="214,' + (yOffset + 76) + ' 244,' + (yOffset + 70) + ' 256,' + (yOffset + 75) + ' 244,' + (yOffset + 81) + '" fill="#eee4cb" fill-opacity="0.88"/>');
    parts.push('<text x="235" y="' + (yOffset + 63) + '" fill="#e1ac64" font-family="Georgia,serif" font-style="italic" font-size="11.5" text-anchor="middle">Moth</text>');

    // South Pier beacon (steady amber)
    parts.push('<circle cx="628" cy="' + (yOffset + 36) + '" r="14" fill="#e1ac64" fill-opacity="0.18"/>');
    parts.push('<circle cx="628" cy="' + (yOffset + 36) + '" r="5.5" fill="#e1ac64" stroke="#855a24" stroke-width="1.5"/>');
    parts.push('<text x="648" y="' + (yOffset + 33) + '" fill="#eee4cb" font-family="Georgia,serif" font-size="13">South Pier</text>');
    parts.push('<text x="648" y="' + (yOffset + 47) + '" fill="#e1ac64" font-family="ui-sans-serif,system-ui,sans-serif" font-size="10.5">steady amber</text>');

    // Orchard Float beacon (two short white flashes, long dark interval)
    parts.push('<circle cx="628" cy="' + (yOffset + 96) + '" r="14" fill="#f7f4e8" fill-opacity="0.16"/>');
    parts.push('<circle cx="628" cy="' + (yOffset + 96) + '" r="5.5" fill="#fffdf5" stroke="#b5b9a5" stroke-width="1.5"/>');
    parts.push('<text x="648" y="' + (yOffset + 90) + '" fill="#eee4cb" font-family="Georgia,serif" font-size="13">Orchard Float</text>');
    parts.push('<rect x="648" y="' + (yOffset + 98) + '" width="12" height="4" rx="2" fill="#fffdf5"/>');
    parts.push('<rect x="664" y="' + (yOffset + 98) + '" width="12" height="4" rx="2" fill="#fffdf5"/>');
    parts.push('<rect x="680" y="' + (yOffset + 98) + '" width="28" height="4" rx="2" fill="#2c4440"/>');
    parts.push('<text x="714" y="' + (yOffset + 104) + '" fill="#b5b9a5" font-family="ui-sans-serif,system-ui,sans-serif" font-size="10.5">2 flashes</text>');

    return parts.join('');
  }

  function liveReachSvg(vmState) {
    const height = vmState.isMothCase ? 248 : 112;
    const parts = [];
    parts.push(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 ' + height + '" width="800" height="' + height + '" class="reach-svg" role="img" aria-label="Crossing reach map and evidence bridge">'
    );
    parts.push('<rect width="800" height="' + height + '" rx="12" fill="#172b2b"/>');

    if (vmState.isMothCase) {
      parts.push(
        '<text x="24" y="25" fill="#e1ac64" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11" letter-spacing="1.2">THE REACH AT 22:00 — THREE USABLE LANDINGS</text>'
      );
      parts.push(renderMothReachChannel(36));
      parts.push(renderFactBridge(vmState, 180));
    } else {
      parts.push(renderFactBridge(vmState, 28));
    }

    parts.push('</svg>');
    return parts.join('');
  }

  function galleryPreviewSvg(truth, scenes) {
    const vmState = buildReachViewModel(truth, scenes, null, new Set());
    const parts = [];
    parts.push(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 420" width="800" height="420" role="img" aria-labelledby="nf-preview-title">'
    );
    parts.push(
      '<title id="nf-preview-title">Night Ferry: river reach with three signal beacons and two witness accounts</title>'
    );
    parts.push('<rect width="800" height="420" fill="#102020"/>');
    parts.push('<rect x="14" y="14" width="772" height="392" rx="14" fill="#172b2b" stroke="#364a44" stroke-width="1.5"/>');
    parts.push(
      '<text x="32" y="42" fill="#e1ac64" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12" letter-spacing="1.4">NIGHT FERRY · TWO ACCOUNTS, ONE CROSSING</text>'
    );
    parts.push(
      '<text x="32" y="70" fill="#eee4cb" font-family="Georgia,serif" font-size="24">' +
        escapeXml(vmState.caseTitle || 'Night Ferry') + '</text>'
    );
    parts.push(
      '<text x="768" y="42" fill="#b5b9a5" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12" text-anchor="end">22:00 – 22:18</text>'
    );

    parts.push(renderMothReachChannel(92));

    // Two witness account cards derived from real scenes (spoiler-free)
    vmState.accounts.slice(0, 2).forEach(function (acct, idx) {
      const cardX = idx === 0 ? 24 : 408;
      const cardY = 246;
      const cardW = 368;
      const cardH = 140;
      const accent = idx === 0 ? '#e1ac64' : '#a9d8b0';
      parts.push('<rect x="' + cardX + '" y="' + cardY + '" width="' + cardW + '" height="' + cardH + '" rx="10" fill="#1d2f2d" stroke="#3a4c46" stroke-width="1.2"/>');
      parts.push(
        '<text x="' + (cardX + 18) + '" y="' + (cardY + 26) + '" fill="' + accent + '" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11" letter-spacing="1.2">' +
          escapeXml(acct.perspective.toUpperCase() + ' ACCOUNT') + '</text>'
      );
      parts.push(
        '<text x="' + (cardX + 18) + '" y="' + (cardY + 54) + '" fill="#eee4cb" font-family="Georgia,serif" font-size="20">' +
          escapeXml(acct.title) + '</text>'
      );
      const lines = idx === 0
        ? ['Sees boarding at North Landing and all', '3 beacons; cannot see past the bend.']
        : ['Logs one stop and a double-flash shore', 'signal; knows no place name.'];
      parts.push(
        '<text x="' + (cardX + 18) + '" y="' + (cardY + 74) + '" fill="#b5b9a5" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11.5">' +
          escapeXml(lines[0]) + '</text>'
      );
      parts.push(
        '<text x="' + (cardX + 18) + '" y="' + (cardY + 90) + '" fill="#b5b9a5" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11.5">' +
          escapeXml(lines[1]) + '</text>'
      );
      acct.factIds.slice(0, 4).forEach(function (fid, fIdx) {
        const bx = cardX + 18 + fIdx * 54;
        const by = cardY + 104;
        parts.push('<rect x="' + bx + '" y="' + by + '" width="44" height="24" rx="5" fill="#102020" stroke="' + accent + '" stroke-width="1.1"/>');
        parts.push(
          '<text x="' + (bx + 22) + '" y="' + (by + 16) + '" fill="' + accent + '" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12" font-weight="700" text-anchor="middle">' +
            escapeXml(fid) + '</text>'
        );
      });
    });

    parts.push('</svg>');
    return parts.join('\n') + '\n';
  }

  return {
    escapeXml: escapeXml,
    buildReachViewModel: buildReachViewModel,
    liveReachSvg: liveReachSvg,
    galleryPreviewSvg: galleryPreviewSvg,
  };
});
