// Headless test harness: loads the .sb3 into the real Scratch engine (scratch-vm), with a fake
// renderer and a fake clock, then plays it frame by frame following a test plan.
//
//   node tests/harness.js dist/scratch-slayer.sb3 tests/plans/sprint.json tests/out/sprint
//
// A plan is a JSON list of steps. Each step can set things up, hold keys for some frames (or until
// something happens), then log, snapshot and check what it expects. The step keys are listed in
// CLAUDE.md ("Tests"). The harness exits with code 1 if any check fails or the engine logs an error.

// ---- fake clock: the game reads Scratch's timer, so time must move exactly one frame per frame ----
// (This must happen before scratch-vm is loaded.)
let fakeNow = 1e6;
const realNow = Date.now;
Date.now = () => (fakeNow += 0.01);
if (globalThis.performance) globalThis.performance.now = () => (fakeNow += 0.01);
const FRAME_MS = 1000 / 30;

// ---- seeded random numbers: Scratch's "pick random" uses Math.random. Seeding it makes every run
// of a plan play out exactly the same, so a failure can be repeated step for step.
// Set TEST_SEED=<number> to try a different (but still repeatable) run.
let randomState = Number(process.env.TEST_SEED || 20261109) >>> 0;
Math.random = () => {      // mulberry32: a small, well-known pseudo-random generator
    randomState = (randomState + 0x6D2B79F5) >>> 0;
    let mixed = randomState;
    mixed = Math.imul(mixed ^ (mixed >>> 15), mixed | 1);
    mixed ^= mixed + Math.imul(mixed ^ (mixed >>> 7), mixed | 61);
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 4294967296;
};

const fs = require('fs');
const VM = require('scratch-vm');
const ScratchStorage = require('scratch-storage').ScratchStorage || require('scratch-storage');

const [,, projectPath, planPath, outputFolder] = process.argv;
fs.mkdirSync(outputFolder, {recursive: true});
const failures = [];
const plan = expandNamedSteps(JSON.parse(fs.readFileSync(planPath, 'utf8')));

// ---- named steps: common moves through the game, written once ----
// Each one becomes a few ordinary steps. They wait for the game to get somewhere instead of
// counting frames, so a change in how long a screen lasts doesn't break every plan.
function expandNamedSteps(steps) {
    const expanded = [];
    for (const step of steps) {
        if (step.startGame) {            // from the title screen into level play (the card times out by itself)
            expanded.push({tap: 'space', while: {'game state': 'title'}, note: 'start the game'},
                          {until: {'game state': 'playing'}, note: 'level card + melt'});
        } else if (step.continueToNextLevel) {   // from the exit switch through the tally into the next level
            expanded.push({until: {'screen showing': 'level complete'}, note: 'reach the tally'},
                          {tap: 'space', while: {'screen showing': 'level complete'}, note: 'leave the tally'},
                          {until: {'game state': 'playing'}, note: 'next level card + melt'});
        } else if (step.retryLevel) {    // from dying back into the same level
            expanded.push({until: {'screen showing': 'died'}, note: 'death screen'},
                          {tap: 'space', while: {'screen showing': 'died'}, note: 'retry'},
                          {until: {'game state': 'playing'}, note: 'melt back in'});
        } else {
            expanded.push(step);
            continue;
        }
        const extra = {...step};          // anything else on the named step (log, expect...) runs at the end
        delete extra.startGame; delete extra.continueToNextLevel; delete extra.retryLevel;
        if (Object.keys(extra).length) expanded.push({frames: 0, ...extra});
    }
    return expanded;
}

// ---- fake renderer: records what would be drawn, so snapshots can be turned into PNGs ----
let nextId = 1;
const skins = {};       // id -> {svg, w, h, cx, cy}   (a costume's picture, size and center)
const drawables = {};   // id -> {group, skin, x, y, scale, visible, effects}   (a sprite on the stage)
let layerOrder = [];    // drawable ids, back to front
let penOperations = []; // ['l', color, size, x0, y0, x1, y1] lines and ['p', color, size, x, y] dots
function svgSize(svg) { const match = /width="([\d.]+)" height="([\d.]+)"/.exec(svg); return [+match[1], +match[2]]; }
const fakeRenderer = {
    createDrawable(group) {
        const id = nextId++;
        drawables[id] = {group, visible: true, x: 0, y: 0, scale: [100, 100], effects: {}};
        layerOrder.push(id); return id;
    },
    destroyDrawable(id) { delete drawables[id]; layerOrder = layerOrder.filter(other => other !== id); },
    createSVGSkin(svg, center) {
        const id = nextId++; const [w, h] = svgSize(svg);
        skins[id] = {svg, w, h, cx: center ? center[0] : 0, cy: center ? center[1] : 0}; return id;
    },
    updateSVGSkin(id, svg, center) { const [w, h] = svgSize(svg); skins[id] = {svg, w, h, cx: center[0], cy: center[1]}; },
    createBitmapSkin() { return nextId++; },
    createPenSkin() { return 9999; },
    createTextSkin() { return nextId++; },
    getSkinSize(id) { const skin = skins[id]; return skin ? [skin.w, skin.h] : [0, 0]; },
    getSkinRotationCenter(id) { const skin = skins[id]; return skin ? [skin.cx, skin.cy] : [0, 0]; },
    getCurrentSkinSize(drawableId) {
        const drawable = drawables[drawableId]; const skin = drawable && skins[drawable.skin];
        return skin ? [skin.w, skin.h] : [0, 0];
    },
    updateDrawableSkinId(drawableId, skinId) { if (drawables[drawableId]) drawables[drawableId].skin = skinId; },
    updateDrawablePosition(drawableId, position) {
        if (drawables[drawableId]) { drawables[drawableId].x = position[0]; drawables[drawableId].y = position[1]; }
    },
    updateDrawableDirectionScale(drawableId, direction, scale) { if (drawables[drawableId]) drawables[drawableId].scale = scale; },
    updateDrawableVisible(drawableId, visible) { if (drawables[drawableId]) drawables[drawableId].visible = visible; },
    updateDrawableEffect(drawableId, effect, value) { if (drawables[drawableId]) drawables[drawableId].effects[effect] = value; },
    updateDrawableProperties(drawableId, properties) {
        const drawable = drawables[drawableId]; if (!drawable) return;
        if (properties.skinId !== undefined) drawable.skin = properties.skinId;
        if (properties.position) { drawable.x = properties.position[0]; drawable.y = properties.position[1]; }
        if (properties.scale) drawable.scale = properties.scale;
        if (properties.visible !== undefined) drawable.visible = properties.visible;
    },
    getFencedPositionOfDrawable(drawableId, position) { return position; },
    setDrawableOrder(drawableId, index, group, isRelative, minimum) {
        const current = layerOrder.indexOf(drawableId); if (current < 0) return;
        layerOrder.splice(current, 1);
        let target = isRelative ? current + index : index;
        if (target === Infinity || target > layerOrder.length) target = layerOrder.length;
        target = Math.max(minimum || 0, Math.min(layerOrder.length, target));
        layerOrder.splice(target, 0, drawableId);
        return target;
    },
    getDrawableOrder(drawableId) { return layerOrder.indexOf(drawableId); },
    penClear() { penOperations = []; },
    penPoint(skin, pen, x, y) { penOperations.push(['p', pen.color4f.slice(), pen.diameter, x, y]); },
    penLine(skin, pen, x0, y0, x1, y1) { penOperations.push(['l', pen.color4f.slice(), pen.diameter, x0, y0, x1, y1]); },
    penStamp() {},
    setLayerGroupOrdering() {},
    draw() {},
    getBounds() { return null; },
    getBoundsForBubble() { return null; },
};
// Anything the engine asks for that isn't listed above just returns 0.
const renderer = new Proxy(fakeRenderer, {get(target, key) { return key in target ? target[key] : () => 0; }});

// ---- the engine ----
const vm = new VM();
vm.attachStorage(new ScratchStorage());
vm.attachRenderer(renderer);
vm.runtime.addListener('PROJECT_RUN_STOP', () => {});
const engineErrors = [];
console.warn = (...parts) => { engineErrors.push(parts.join(' ')); };
console.error = (...parts) => { engineErrors.push(parts.join(' ')); };

// ---- reading and changing the game ----
const ALL_KEYS = ['space', 'up arrow', 'down arrow', 'left arrow', 'right arrow', 'w', 'a', 's', 'd', 'm', 'e', 'z', 'q',
                  '1', '2', '3', '4', '5', 'o', 'p', 'n'];
function scratchKeyName(key) {
    if (key === 'space') return ' ';
    if (key.includes('arrow')) { const direction = key.split(' ')[0]; return 'Arrow' + direction[0].toUpperCase() + direction.slice(1); }
    return key;
}
function holdKeys(keys) {
    for (const key of ALL_KEYS) vm.runtime.ioDevices.keyboard.postData({key: scratchKeyName(key), isDown: keys.includes(key)});
}

// Short names a plan may use for stage variables.
const ALIAS = {"px": "player x", "py": "player y", "ang": "player angle", "HEALTH": "health", "KILLS": "total kills",
               "level": "current level", "state": "game state", "overlay": "screen showing", "hasRed": "has red key",
               "hasBlue": "has blue key", "levelKills": "level kills", "levelMonsters": "level monster count",
               "levelGot": "level items collected", "levelItems": "level item count", "toast": "message name",
               "toastT": "message timer"};
const stage = () => vm.runtime.getTargetForStage();
const stageVariable = name => Object.values(stage().variables).find(variable => variable.name === name);
function stageValues() {     // every stage variable (not lists) by name, plus the aliases
    const values = {};
    for (const variable of Object.values(stage().variables)) if (!Array.isArray(variable.value)) values[variable.name] = variable.value;
    for (const [alias, name] of Object.entries(ALIAS)) if (name in values) values[alias] = values[name];
    return values;
}
const monsterClones = () => vm.runtime.targets.filter(target => target.sprite.name === 'Monster' && !target.isOriginal);
const localVariable = (target, name) => Object.values(target.variables).find(variable => variable.name === name);
function localValues(target, round) {
    const values = {};
    for (const variable of Object.values(target.variables)) {
        values[variable.name] = round && typeof variable.value === 'number' ? Math.round(variable.value * 100) / 100 : variable.value;
    }
    return values;
}

// Does the game match these conditions? Same rules as "expect":
// {"name": value} must be equal (compared as text), {"name": {"gt": n, "lt": n}} a range,
// "list:name" compares a whole list.
function valueOf(name) { return name.startsWith('list:') ? (stageVariable(name.slice(5)) || {}).value : stageValues()[name]; }
function matches(got, want) {
    if (want && typeof want === 'object' && !Array.isArray(want)) {
        return ('gt' in want ? +got > want.gt : true) && ('lt' in want ? +got < want.lt : true);
    }
    if (Array.isArray(want)) return Array.isArray(got) && JSON.stringify(got.map(String)) === JSON.stringify(want.map(String));
    return String(got) === String(want);
}
const allMatch = conditions => Object.entries(conditions).every(([name, want]) => matches(valueOf(name), want));

function snapshot(name) {
    const sprites = [];
    layerOrder.forEach((id, layer) => {
        const drawable = drawables[id]; if (!drawable || !drawable.visible || !skins[drawable.skin]) return;
        sprites.push({layer, x: drawable.x, y: drawable.y, scale: drawable.scale[0], skin: drawable.skin,
                      effects: drawable.effects, bg: drawable.group === 'background'});
    });
    fs.writeFileSync(`${outputFolder}/${name}.json`, JSON.stringify({pen: penOperations, sprites, vars: stageValues()}));
}

// ---- running frames ----
let frame = 0;
const stepTimes = [];
async function runFrame(step, frameInStep) {
    if (step.auto) autoAim(step, frameInStep);
    const started = realNow();
    vm.runtime._step();
    stepTimes.push(realNow() - started);
    frame++; fakeNow += FRAME_MS;
    await new Promise(resolve => setImmediate(resolve));
    if (step.snapEvery && frame % step.snapEvery === 0) snapshot(`${step.prefix}${frame}`);
}

// "auto": a simple bot. Turn toward the nearest live monster, shoot when lined up, walk closer.
function autoAim(step, frameInStep) {
    const player = stageValues();
    let nearest = null, nearestDistance = 1e9;
    for (const clone of monsterClones()) {
        const monster = localValues(clone);
        if (+monster['is alive'] !== 1) continue;
        const distance = Math.hypot(monster['monster x'] - player.px, monster['monster y'] - player.py);
        if (distance < nearestDistance) { nearestDistance = distance; nearest = monster; }
    }
    const keys = [...(step.keys || [])];
    if (nearest) {
        const wanted = Math.atan2(nearest['monster y'] - player.py, nearest['monster x'] - player.px) * 180 / Math.PI;
        const turn = ((wanted - player.ang) % 360 + 540) % 360 - 180;
        if (turn > 4) keys.push('right arrow');
        else if (turn < -4) keys.push('left arrow');
        else if (frameInStep % 4 < 2) keys.push('space');
        if (Math.abs(turn) < 12 && nearestDistance > 2.5) keys.push('up arrow');
    }
    holdKeys(keys);
}

const TAP_DOWN_FRAMES = 2, TAP_UP_FRAMES = 2, DEFAULT_TIMEOUT = 900;   // 900 frames = 30 seconds
const describe = step => step.log || step.note || `frame ${frame}`;
function fail(message) { failures.push(message); console.log('FAIL', message); }

// "until": keep playing frames (holding the step's keys) until the conditions are true.
async function runUntil(step) {
    const timeout = step.timeout || DEFAULT_TIMEOUT;
    for (let waited = 0; !allMatch(step.until); waited++) {
        if (waited >= timeout) { fail(`${describe(step)}: still waiting for ${JSON.stringify(step.until)} after ${timeout} frames`); return; }
        await runFrame(step, waited);
    }
}

// "tap" + "while": press and let go of a key, again and again, while the conditions are true.
async function runTaps(step) {
    const timeout = step.timeout || DEFAULT_TIMEOUT;
    let waited = 0;
    while (allMatch(step.while)) {
        if (waited >= timeout) { fail(`${describe(step)}: still tapping ${step.tap} after ${timeout} frames`); break; }
        holdKeys([...(step.keys || []), step.tap]);
        for (let count = 0; count < TAP_DOWN_FRAMES; count++, waited++) await runFrame(step, waited);
        holdKeys(step.keys || []);
        for (let count = 0; count < TAP_UP_FRAMES; count++, waited++) await runFrame(step, waited);
    }
}

// ---- setting things up before a step's frames ----
function applySetup(step) {
    if (step.setList) {
        for (const [name, items] of Object.entries(step.setList)) {
            const list = stageVariable(name); list.value = items.slice(); list._monitorUpToDate = false;
        }
    }
    if (step.setMonsterType) {
        for (const clone of monsterClones()) {
            if (+localVariable(clone, 'monster type').value !== step.setMonsterType.type) continue;
            for (const [name, value] of Object.entries(step.setMonsterType.vars)) localVariable(clone, name).value = value;
        }
    }
    if (step.hit) {     // pretend the player shot the first live monster of this type
        const target = monsterClones().find(clone => +localVariable(clone, 'monster type').value === step.hit.type &&
                                                     +localVariable(clone, 'is alive').value === 1);
        if (target) {
            stageVariable('shot fired this frame').value = 1;
            stageVariable('shot target id').value = +localVariable(target, 'monster id').value;
            stageVariable('hit damage').value = step.hit.damage;
        } else console.log('  no monster of type', step.hit.type);
    }
    if (step.mouse) {
        vm.runtime.ioDevices.mouse.postData({x: step.mouse.x + 240, y: 180 - step.mouse.y, canvasWidth: 480,
                                             canvasHeight: 360, isDown: !!step.mouse.down});
    }
    if (step.toBossKey) {
        stageVariable('player x').value = +stageVariable('boss death x').value;
        stageVariable('player y').value = +stageVariable('boss death y').value;
    }
    if (step.set) {
        for (const variable of Object.values(stage().variables)) {
            for (const [name, value] of Object.entries(step.set)) if (variable.name === name || variable.name === ALIAS[name]) variable.value = value;
        }
    }
}

// ---- after a step's frames: logs and checks ----
const LOGGED = ['px', 'py', 'ang', 'HEALTH', 'KILLS', 'level', 'state', 'overlay', 'hasRed', 'hasBlue', 'levelKills',
                'levelMonsters', 'levelGot', 'levelItems', 'toast', 'toastT', 'stamina', 'is exhausted', 'speed boost',
                'stamina rest timer'];
function logStep(step) {
    const values = stageValues();
    const shown = {};
    for (const name of LOGGED) shown[name] = typeof values[name] === 'number' ? Math.round(values[name] * 100) / 100 : values[name];
    const cloneCounts = {};
    for (const target of vm.runtime.targets) if (!target.isOriginal) cloneCounts[target.sprite.name] = (cloneCounts[target.sprite.name] || 0) + 1;
    if (step.dumpMonsters) {
        for (const clone of monsterClones()) {
            const monster = localValues(clone, true);
            if (step.dumpMonsters !== true && +monster['monster type'] !== step.dumpMonsters) continue;
            console.log('   M', monster['monster id'], monster['monster name'], 'hp', monster['monster health'], 'alive',
                        monster['is alive'], 'pos', monster['monster x'], monster['monster y'], 'charge', monster['charge state'],
                        'chase', monster['is chasing'], 'vis', clone.visible, 'ghost', clone.effects.ghost, 'bright',
                        Math.round(clone.effects.brightness));
        }
    }
    if (step.dumpSprite) {
        for (const target of vm.runtime.targets.filter(target => target.sprite.name === step.dumpSprite)) {
            console.log('  ', target.isOriginal ? 'ORIG' : 'clone', JSON.stringify(localValues(target, true)));
        }
    }
    shown.ammo = valueOf('list:ammo counts'); shown.owned = valueOf('list:weapons owned');
    shown.weapon = values['current weapon']; shown.skull = values['has skull key'];
    shown.bossDead = values['boss is dead']; shown.boss = values['boss health'];
    console.log(step.log, JSON.stringify(shown), JSON.stringify(cloneCounts));
}

function checkExpectations(step) {
    if (step.expect) {
        for (const [name, want] of Object.entries(step.expect)) {
            const got = valueOf(name);
            if (!matches(got, want)) fail(`${describe(step)}: ${name} = ${JSON.stringify(got)}, expected ${JSON.stringify(want)}`);
        }
    }
    if (step.expectMonsters) {      // {"type": 1, "monster health": 2}: every clone of that type must match
        const {type, ...want} = step.expectMonsters;
        const clones = monsterClones().filter(clone => +localVariable(clone, 'monster type').value === type);
        if (!clones.length) failures.push(`${describe(step)}: no monsters of type ${type}`);
        for (const clone of clones) for (const [name, value] of Object.entries(want)) {
            const got = (localVariable(clone, name) || {}).value;
            if (String(got) !== String(value)) { fail(`${describe(step)}: monster type ${type} ${name} = ${JSON.stringify(got)}, expected ${JSON.stringify(value)}`); break; }
        }
    }
}

function printDumps(step) {
    if (step.dumpList) {
        const list = stageVariable(step.dumpList);
        console.log('LIST', step.dumpList, JSON.stringify(list.value, null, 1));
        const monitor = vm.runtime._monitorState.find((state, id) => id === list.id);
        console.log('monitor visible:', monitor ? monitor.get('visible') : 'none');
    }
    if (step.row !== undefined) console.log('  map row', step.row, stageVariable('current map').value[step.row]);
}

// ---- the run ----
(async () => {
    await vm.loadProject(fs.readFileSync(projectPath));
    fs.writeFileSync(`${outputFolder}/skins.json`, JSON.stringify(skins));
    vm.setTurboMode(false);
    vm.runtime.currentStepTime = FRAME_MS;
    vm.greenFlag();
    for (const step of plan) {
        holdKeys(step.keys || []);
        applySetup(step);
        for (let frameInStep = 0; frameInStep < (step.frames || 0); frameInStep++) await runFrame(step, frameInStep);
        if (step.until) await runUntil(step);
        if (step.tap) await runTaps(step);
        if (step.snap) snapshot(step.snap);
        if (step.log) logStep(step);
        checkExpectations(step);
        printDumps(step);
    }
    stepTimes.sort((first, second) => first - second);
    console.log('frames', frame, 'median step ms', stepTimes[stepTimes.length >> 1], 'p90', stepTimes[Math.floor(stepTimes.length * 0.9)]);
    console.log('monster clones', monsterClones().length, monsterClones().map(clone => {
        const monster = localValues(clone);
        return `#${monster['monster id']} alive=${monster['is alive']} hp=${monster['monster health']} ` +
               `pos=${(+monster['monster x']).toFixed(2)},${(+monster['monster y']).toFixed(2)} vis=${clone.visible}`;
    }).join('\n'));
    const realErrors = engineErrors.filter(error => !/audio|Audio|Translation/.test(error));
    console.log('threads', vm.runtime.threads.length, 'errors', realErrors.slice(0, 10));
    for (const error of realErrors) failures.push('VM error: ' + error);
    console.log(failures.length ? `RESULT FAIL (${failures.length})` : 'RESULT PASS');
    process.exit(failures.length ? 1 : 0);
})();
