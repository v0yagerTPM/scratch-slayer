let fakeNow = 1e6; const _realNow = Date.now; Date.now = () => (fakeNow += 0.01);
if (globalThis.performance) globalThis.performance.now = () => (fakeNow += 0.01);
// Headless Scratch VM harness: loads the .sb3, drives keys, records pen + sprite state per frame.
const fs = require('fs');
const VM = require('scratch-vm');
const ScratchStorage = require('scratch-storage').ScratchStorage || require('scratch-storage');

const [,, sb3, script, outdir] = process.argv;
fs.mkdirSync(outdir, {recursive: true});
const failures = [];
const plan = JSON.parse(fs.readFileSync(script, 'utf8')); // [{frames, keys:[...], snap:bool}]

// ---- fake renderer ----
let nextId = 1;
const skins = {};      // id -> {svg,w,h,cx,cy}
const drawables = {};  // id -> {skin, x, y, scale, visible, effects, layer}
let order = [];
let penOps = [];
const R = {
    createDrawable(group) { const id = nextId++; drawables[id] = {group, visible: true, x: 0, y: 0, scale: [100, 100], effects: {}}; order.push(id); return id; },
    destroyDrawable(id) { delete drawables[id]; order = order.filter(o => o !== id); },
    createSVGSkin(svg, rc) { const id = nextId++; const m = /width="([\d.]+)" height="([\d.]+)"/.exec(svg); skins[id] = {svg, w: +m[1], h: +m[2], cx: rc ? rc[0] : 0, cy: rc ? rc[1] : 0}; return id; },
    updateSVGSkin(id, svg, rc) { const m = /width="([\d.]+)" height="([\d.]+)"/.exec(svg); skins[id] = {svg, w: +m[1], h: +m[2], cx: rc[0], cy: rc[1]}; },
    createBitmapSkin() { return nextId++; },
    createPenSkin() { return 9999; },
    createTextSkin() { return nextId++; },
    getSkinSize(id) { const s = skins[id]; return s ? [s.w, s.h] : [0, 0]; },
    getSkinRotationCenter(id) { const s = skins[id]; return s ? [s.cx, s.cy] : [0, 0]; },
    getCurrentSkinSize(did) { const d = drawables[did]; const s = d && skins[d.skin]; return s ? [s.w, s.h] : [0, 0]; },
    updateDrawableSkinId(did, sid) { if (drawables[did]) drawables[did].skin = sid; },
    updateDrawablePosition(did, p) { if (drawables[did]) { drawables[did].x = p[0]; drawables[did].y = p[1]; } },
    updateDrawableDirectionScale(did, dir, sc) { if (drawables[did]) drawables[did].scale = sc; },
    updateDrawableVisible(did, v) { if (drawables[did]) drawables[did].visible = v; },
    updateDrawableEffect(did, e, v) { if (drawables[did]) drawables[did].effects[e] = v; },
    updateDrawableProperties(did, p) {
        const d = drawables[did]; if (!d) return;
        if (p.skinId !== undefined) d.skin = p.skinId;
        if (p.position) { d.x = p.position[0]; d.y = p.position[1]; }
        if (p.scale) d.scale = p.scale;
        if (p.visible !== undefined) d.visible = p.visible;
    },
    getFencedPositionOfDrawable(did, pos) { return pos; },
    setDrawableOrder(did, idx, group, isRelative, min) {
        let cur = order.indexOf(did); if (cur < 0) return;
        order.splice(cur, 1);
        let target = isRelative ? cur + idx : idx;
        if (target === Infinity || target > order.length) target = order.length;
        target = Math.max(min || 0, Math.min(order.length, target));
        order.splice(target, 0, did);
        return target;
    },
    getDrawableOrder(did) { return order.indexOf(did); },
    penClear() { penOps = []; },
    penPoint(skin, a, x, y) { penOps.push(['p', a.color4f.slice(), a.diameter, x, y]); },
    penLine(skin, a, x0, y0, x1, y1) { penOps.push(['l', a.color4f.slice(), a.diameter, x0, y0, x1, y1]); },
    penStamp() {},
    setLayerGroupOrdering() {},
    draw() {},
    getBounds() { return null; }, getBoundsForBubble() { return null; },
};
const renderer = new Proxy(R, { get(t, k) { if (k in t) return t[k]; return () => 0; } });

const vm = new VM();
vm.attachStorage(new ScratchStorage());
vm.attachRenderer(renderer);
vm.runtime.addListener('PROJECT_RUN_STOP', () => {});
const errors = [];
const origWarn = console.warn; console.warn = (...a) => { errors.push(a.join(' ')); };
const origErr = console.error; console.error = (...a) => { errors.push(a.join(' ')); };

function setKeys(keys) {
    const all = ['space', 'up arrow', 'down arrow', 'left arrow', 'right arrow', 'w', 'a', 's', 'd', 'm', 'e', 'z', 'q', '1', '2', '3', '4', '5', 'o', 'p', 'n'];
    for (const k of all) {
        const down = keys.includes(k);
        vm.runtime.ioDevices.keyboard.postData({key: k === 'space' ? ' ' : k.includes('arrow') ? 'Arrow' + k.split(' ')[0][0].toUpperCase() + k.split(' ')[0].slice(1) : k, isDown: down});
    }
}
const ALIAS = {"px": "player x", "py": "player y", "ang": "player angle", "HEALTH": "health", "KILLS": "total kills", "level": "current level", "state": "game state", "overlay": "screen showing", "hasRed": "has red key", "hasBlue": "has blue key", "levelKills": "level kills", "levelMonsters": "level monster count", "levelGot": "level items collected", "levelItems": "level item count", "toast": "message name", "toastT": "message timer"};
const MON = {"ex": "monster x", "ey": "monster y", "alive": "is alive", "myId": "monster id", "hp": "monster health"};
function globals() {
    const st = vm.runtime.getTargetForStage();
    const o = {}; for (const v of Object.values(st.variables)) if (!Array.isArray(v.value)) o[v.name] = v.value;
    for (const [a, n] of Object.entries(ALIAS)) if (n in o) o[a] = o[n];
    return o;
}
function snapshot(name) {
    const sprites = [];
    order.forEach((id, i) => {
        const d = drawables[id]; if (!d || !d.visible || !skins[d.skin]) return;
        sprites.push({layer: i, x: d.x, y: d.y, scale: d.scale[0], skin: d.skin, effects: d.effects, bg: d.group === 'background'});
    });
    fs.writeFileSync(`${outdir}/${name}.json`, JSON.stringify({pen: penOps, sprites, vars: globals()}));
}

(async () => {
    await vm.loadProject(fs.readFileSync(sb3));
    fs.writeFileSync(`${outdir}/skins.json`, JSON.stringify(skins));
    vm.setTurboMode(false); vm.runtime.currentStepTime = 1000 / 30;
    vm.greenFlag();
    let frame = 0, t0 = Date.now(), stepTimes = [];
    for (const step of plan) {
        setKeys(step.keys || []);
        if (step.setList) { const st = vm.runtime.getTargetForStage(); for (const [k, val] of Object.entries(step.setList)) { const l = Object.values(st.variables).find(v => v.name === k); l.value = val.slice(); l._monitorUpToDate = false; } }
        const monsterClones = () => vm.runtime.targets.filter(t => t.sprite.name === 'Monster' && !t.isOriginal);
        const mvar = (t, n) => Object.values(t.variables).find(v => v.name === n);
        if (step.setMonsterType) { for (const t of monsterClones()) if (+mvar(t, 'monster type').value === step.setMonsterType.type) for (const [k, val] of Object.entries(step.setMonsterType.vars)) mvar(t, k).value = val; }
        if (step.hit) { const t = monsterClones().find(t => +mvar(t, 'monster type').value === step.hit.type && +mvar(t, 'is alive').value === 1);
            const st = vm.runtime.getTargetForStage(); const sv = n => Object.values(st.variables).find(v => v.name === n);
            if (t) { sv('shot fired this frame').value = 1; sv('shot target id').value = +mvar(t, 'monster id').value; sv('hit damage').value = step.hit.damage; } else console.log('  no monster of type', step.hit.type); }
        if (step.mouse) { vm.runtime.ioDevices.mouse.postData({x: step.mouse.x + 240, y: 180 - step.mouse.y, canvasWidth: 480, canvasHeight: 360, isDown: !!step.mouse.down}); }
        if (step.toBossKey) { const st = vm.runtime.getTargetForStage(); const sv = n => Object.values(st.variables).find(v => v.name === n); sv('player x').value = +sv('boss death x').value; sv('player y').value = +sv('boss death y').value; }
        if (step.set) { const st = vm.runtime.getTargetForStage(); for (const v of Object.values(st.variables)) { for (const [k, val] of Object.entries(step.set)) if (v.name === k || v.name === ALIAS[k]) v.value = val; } }
        for (let i = 0; i < step.frames; i++) {
            if (step.auto) {   // bot: face nearest live monster, shoot when lined up
                const g = globals();
                let best = null, bd = 1e9;
                for (const m of vm.runtime.targets.filter(t => t.sprite.name === 'Monster' && !t.isOriginal)) {
                    const v = {}; for (const x of Object.values(m.variables)) v[x.name] = +x.value; for (const [a, n] of Object.entries(MON)) v[a] = v[n];
                    if (!v.alive) continue;
                    const d = Math.hypot(v.ex - g.px, v.ey - g.py); if (d < bd) { bd = d; best = v; }
                }
                const keys = [...(step.keys || [])];
                if (best) {
                    let want = Math.atan2(best.ey - g.py, best.ex - g.px) * 180 / Math.PI;
                    let diff = ((want - g.ang) % 360 + 540) % 360 - 180;
                    if (diff > 4) keys.push('right arrow'); else if (diff < -4) keys.push('left arrow');
                    else if (i % 4 < 2) keys.push('space');
                    if (Math.abs(diff) < 12 && bd > 2.5) keys.push('up arrow');
                }
                setKeys(keys);
            }
            const s = _realNow(); vm.runtime._step(); stepTimes.push(_realNow() - s); frame++; fakeNow += 1000 / 30; await new Promise(r => setImmediate(r));
            if (step.snapEvery && frame % step.snapEvery === 0) snapshot(`${step.prefix}${frame}`);
        }
        if (step.snap) snapshot(step.snap);
        if (step.log) { const g = globals(); const keep = ['px','py','ang','HEALTH','KILLS','level','state','overlay','hasRed','hasBlue','levelKills','levelMonsters','levelGot','levelItems','toast','toastT','stamina','is exhausted','speed boost','stamina rest timer'];
            const o = {}; for (const k of keep) o[k] = typeof g[k] === 'number' ? Math.round(g[k]*100)/100 : g[k]; const cc = {}; for (const t of vm.runtime.targets) if (!t.isOriginal) cc[t.sprite.name] = (cc[t.sprite.name]||0)+1; /*CLONECOUNT*/ if (step.dumpMonsters) { for (const t of vm.runtime.targets.filter(t => t.sprite.name === 'Monster' && !t.isOriginal)) { const v = {}; for (const x of Object.values(t.variables)) v[x.name] = typeof x.value === 'number' ? Math.round(x.value*100)/100 : x.value; if (step.dumpMonsters === true || +v['monster type'] === step.dumpMonsters) console.log('   M', v['monster id'], v['monster name'], 'hp', v['monster health'], 'alive', v['is alive'], 'pos', v['monster x'], v['monster y'], 'charge', v['charge state'], 'chase', v['is chasing'], 'vis', t.visible, 'ghost', t.effects.ghost, 'bright', Math.round(t.effects.brightness)); } }
            if (step.dumpSprite) { for (const t of vm.runtime.targets.filter(t => t.sprite.name === step.dumpSprite)) { const v = {}; for (const x of Object.values(t.variables)) v[x.name] = typeof x.value === 'number' ? Math.round(x.value*100)/100 : x.value; console.log('  ', t.isOriginal ? 'ORIG' : 'clone', JSON.stringify(v)); } } /*PROJDUMP*/ { const st = vm.runtime.getTargetForStage();  } { const st = vm.runtime.getTargetForStage(); const L = n => (Object.values(st.variables).find(v => v.name === n) || {}).value; o.ammo = L('ammo counts'); o.owned = L('weapons owned'); o.weapon = g['current weapon']; o.skull = g['has skull key']; o.bossDead = g['boss is dead']; o.boss = g['boss health']; } console.log(step.log, JSON.stringify(o), JSON.stringify(cc)); }
        if (step.expect) {   // assertions: {"var name": value, "list:name": [..], "var": {"gt": n} / {"lt": n}}
            const st = vm.runtime.getTargetForStage(); const g = globals();
            for (const [k, want] of Object.entries(step.expect)) {
                const got = k.startsWith('list:') ? (Object.values(st.variables).find(v => v.name === k.slice(5)) || {}).value : g[k];
                let ok;
                if (want && typeof want === 'object' && !Array.isArray(want)) ok = ('gt' in want ? +got > want.gt : true) && ('lt' in want ? +got < want.lt : true);
                else if (Array.isArray(want)) ok = Array.isArray(got) && JSON.stringify(got.map(String)) === JSON.stringify(want.map(String));
                else ok = String(got) === String(want);
                if (!ok) { failures.push(`${step.log || 'frame ' + frame}: ${k} = ${JSON.stringify(got)}, expected ${JSON.stringify(want)}`); console.log('FAIL', failures[failures.length - 1]); }
            }
        }
        if (step.expectMonsters) {   // {"type": 1, "monster health": 2}: every clone of that type must match
            const {type, ...want} = step.expectMonsters;
            const clones = vm.runtime.targets.filter(t => t.sprite.name === 'Monster' && !t.isOriginal &&
                +Object.values(t.variables).find(v => v.name === 'monster type').value === type);
            if (!clones.length) failures.push(`${step.log || 'frame ' + frame}: no monsters of type ${type}`);
            for (const t of clones) for (const [k, val] of Object.entries(want)) {
                const got = (Object.values(t.variables).find(v => v.name === k) || {}).value;
                if (String(got) !== String(val)) { failures.push(`${step.log || 'frame ' + frame}: monster type ${type} ${k} = ${JSON.stringify(got)}, expected ${JSON.stringify(val)}`); console.log('FAIL', failures[failures.length - 1]); break; }
            }
        }
        if (step.dumpList) { const st = vm.runtime.getTargetForStage(); const l = Object.values(st.variables).find(v => v.name === step.dumpList); console.log('LIST', step.dumpList, JSON.stringify(l.value, null, 1)); const mon = vm.runtime._monitorState.find((m, id) => id === l.id); console.log('monitor visible:', mon ? mon.get('visible') : 'none'); }
        if (step.row !== undefined) { const st = vm.runtime.getTargetForStage(); const m = Object.values(st.variables).find(v => v.name === 'current map'); console.log('  map row', step.row, m.value[step.row]); }
    }
    stepTimes.sort((a, b) => a - b);
    console.log('frames', frame, 'median step ms', stepTimes[stepTimes.length >> 1], 'p90', stepTimes[Math.floor(stepTimes.length * 0.9)]);
    const mons = vm.runtime.targets.filter(t => t.sprite.name === 'Monster' && !t.isOriginal);
    console.log('monster clones', mons.length, mons.map(m => {
        const v = {}; for (const x of Object.values(m.variables)) v[x.name] = x.value; for (const [a, n] of Object.entries(MON)) v[a] = v[n];
        return `#${v.myId} alive=${v.alive} hp=${v.hp} pos=${(+v.ex).toFixed(2)},${(+v.ey).toFixed(2)} vis=${m.visible}`;
    }).join('\n'));
    const realErrors = errors.filter(e => !/audio|Audio|Translation/.test(e));
    console.log('threads', vm.runtime.threads.length, 'errors', realErrors.slice(0, 10));
    for (const e of realErrors) failures.push('VM error: ' + e);
    console.log(failures.length ? `RESULT FAIL (${failures.length})` : 'RESULT PASS');
    process.exit(failures.length ? 1 : 0);
})();
