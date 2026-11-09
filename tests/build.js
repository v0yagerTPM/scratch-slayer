// Builds dist/scratch-slayer.sb3 from the Python source. Tries "python3", then "python" (Windows).
const {spawnSync} = require('child_process');
const path = require('path');
const root = path.join(__dirname, '..');
const out = path.join(root, 'dist', 'scratch-slayer.sb3');
for (const python of ['python3', 'python']) {
    const r = spawnSync(python, [path.join(root, 'src', 'build.py'), out], {stdio: 'inherit'});
    if (!r.error) process.exit(r.status);
}
console.error('Could not find Python. Install Python 3 from python.org.');
process.exit(1);
