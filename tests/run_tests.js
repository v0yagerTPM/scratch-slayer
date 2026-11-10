// Builds the game, then plays every test plan in tests/plans headlessly and reports PASS/FAIL.
//   npm test                  -> all plans
//   npm test -- full-game     -> just the plans whose file name contains "full-game"
const {spawnSync} = require('child_process');
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const build = spawnSync(process.execPath, [path.join(__dirname, 'build.js')], {stdio: 'inherit'});
if (build.status !== 0) process.exit(build.status || 1);
// Runs a Python script with its arguments. Tries "python3", then "python" (Windows), like build.js.
function runPython(...scriptAndArguments) {
    for (const python of ['python3', 'python']) {
        const result = spawnSync(python, scriptAndArguments, {stdio: 'inherit'});
        if (result.error) continue;
        if (result.status !== 0) process.exit(result.status || 1);
        return;
    }
    console.error('Could not find Python. Install Python 3 from python.org.');
    process.exit(1);
}
// The map checker's own tests.
runPython(path.join(__dirname, 'test_levels.py'));
// The projects a plan can be played on: the real game, or a test copy named by the plan's "project".
const PROJECTS = {
    'game': path.join(root, 'dist', 'scratch-slayer.sb3'),
    'map variant copy': path.join(__dirname, 'out', 'map-variant-copy.sb3'),   // levels 1-2 with maps A, B, C
};
const filter = process.argv[2] || '';
const plans = fs.readdirSync(path.join(__dirname, 'plans')).filter(f => f.endsWith('.json') && f.includes(filter));
const projectOf = plan => {
    const planFile = JSON.parse(fs.readFileSync(path.join(__dirname, 'plans', plan), 'utf8'));
    return Array.isArray(planFile) ? 'game' : planFile.project;
};
if (plans.some(plan => projectOf(plan) === 'map variant copy')) {
    runPython(path.join(__dirname, 'build_map_variant_copy.py'), PROJECTS['map variant copy']);
}
let failed = 0;
for (const plan of plans) {
    const name = plan.replace('.json', '');
    const r = spawnSync(process.execPath, [path.join(__dirname, 'harness.js'), PROJECTS[projectOf(plan)],
        path.join(__dirname, 'plans', plan), path.join(__dirname, 'out', name)], {encoding: 'utf8', maxBuffer: 64 * 1024 * 1024});
    const lines = (r.stdout || '').split('\n');
    const fails = lines.filter(l => l.startsWith('FAIL') || l.startsWith('VM error'));
    const passed = r.status === 0;
    if (!passed) failed++;
    console.log(`${passed ? 'PASS' : 'FAIL'}  ${name}`);
    for (const f of fails) console.log('      ' + f);
    if (!passed && !fails.length) console.log((r.stderr || '').split('\n').slice(-8).join('\n'));
}
console.log(`\n${plans.length - failed} of ${plans.length} test plans passed.`);
process.exit(failed ? 1 : 0);
