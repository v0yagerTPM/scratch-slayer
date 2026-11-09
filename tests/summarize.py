import sys, json
for l in sys.stdin:
    l = l.rstrip()
    if ' {"px"' in l:
        name, rest = l.split(' {', 1); d = json.loads('{' + rest.split('} {')[0] + '}')
        keep = {k: d.get(k) for k in ['px', 'py', 'HEALTH', 'level', 'state', 'overlay', 'toast', 'ammo', 'owned', 'weapon', 'skull', 'bossDead', 'boss', 'levelKills', 'levelMonsters']}
        print(name.ljust(26), json.dumps(keep))
    elif 'Translation' not in l and 'No audio' not in l:
        print(l[:300])
