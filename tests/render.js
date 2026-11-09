// Turn a recorded frame (pen ops + sprite placements) into a PNG, Scratch coordinates -> 480x360.
const fs = require('fs'); const sharp = require('sharp');
const [,, dir, ...names] = process.argv;
const skins = JSON.parse(fs.readFileSync(`${dir}/skins.json`));
const rgba = c => `rgba(${Math.round(c[0] * 255)},${Math.round(c[1] * 255)},${Math.round(c[2] * 255)},${c[3].toFixed(3)})`;
(async () => {
  for (const n of names) {
    const f = JSON.parse(fs.readFileSync(`${dir}/${n}.json`));
    let s = `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="#000"/>`;
    const sprite = sp => { const k = skins[sp.skin]; const sc = sp.scale / 100; const op = 1 - Math.min(100, Math.max(0, (sp.effects && sp.effects.ghost) || 0)) / 100;
      const href = 'data:image/svg+xml;base64,' + Buffer.from(k.svg).toString('base64');
      return `<image href="${href}" width="${k.w}" height="${k.h}" opacity="${op}" transform="translate(${sp.x + 240 - k.cx * sc},${180 - sp.y - k.cy * sc}) scale(${sc})"/>`; };
    for (const sp of f.sprites.filter(sp => sp.bg)) s += sprite(sp);
    for (const op of f.pen) {
      if (op[0] === 'l') s += `<line x1="${op[3] + 240}" y1="${180 - op[4]}" x2="${op[5] + 240}" y2="${180 - op[6]}" stroke="${rgba(op[1])}" stroke-width="${op[2]}" stroke-linecap="round"/>`;
      else s += `<circle cx="${op[3] + 240}" cy="${180 - op[4]}" r="${op[2] / 2}" fill="${rgba(op[1])}"/>`;
    }
    for (const sp of f.sprites.filter(sp => !sp.bg)) s += sprite(sp);
    s += '</svg>';
    await sharp(Buffer.from(s)).png().toFile(`${dir}/${n}.png`);
    console.log(n, 'pen ops', f.pen.length, 'sprites', f.sprites.length, JSON.stringify(f.vars));
  }
})();
