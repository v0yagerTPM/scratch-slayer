// npm run compare -- <git ref>: runs tests/compare_builds.py with "python3", or "python" (Windows).
const {spawnSync} = require('child_process');
const path = require('path');
for (const python of ['python3', 'python']) {
    const result = spawnSync(python, [path.join(__dirname, 'compare_builds.py'), ...process.argv.slice(2)], {stdio: 'inherit'});
    if (!result.error) process.exit(result.status);
}
console.error('Could not find Python. Install Python 3 from python.org.');
process.exit(2);
