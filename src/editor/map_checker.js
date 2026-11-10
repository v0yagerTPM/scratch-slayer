// THE MAP CHECKER, in JavaScript, for the map editor (docs/map-editor.html).
//
// This is the same detective work as validate() and balance() in src/levels.py, written again
// in JavaScript so the editor can check a map while you draw it, in the web browser, without
// Python. It gives exactly the same messages as the build, in the same order: the first problem
// it lists is the one `npm test` would stop on. (tests/test_levels.py checks that the two
// agree, on every real map and on thousands of broken ones.) If you change a check in
// levels.py, change it here too.
//
// It doesn't know any letters or numbers by itself: the 'game' object handed to it holds the
// letter groups from levels.py and the tables from game/config.py (src/map_editor.py writes
// them into the page), so the two can't drift apart.
//
// A map is a list of strings, one per row, top row first: rows[row][column], like levels.py.
// A square is written [column, row].

(function () {
    'use strict';

    // One step right, left, down and up, as [column change, row change].
    const NEIGHBOR_STEPS = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    // A square as one piece of text, "column,row", so squares can go in a Set or a Map.
    function squareKey(column, row) {
        return column + ',' + row;
    }

    // A square's position, in Python numbers and in Scratch list numbers (like where() in levels.py).
    function where(column, row) {
        return `column ${column}, row ${row} (in Scratch: item ${row + 1} of the list, letter ${column + 1})`;
    }

    // FLOOD FILL with step counting: every square you can walk to from 'start', and how many steps
    // away it is. Returns a Map from squareKey to steps. (reachable_squares() and
    // walking_distances() in levels.py, in one: the squares reached are the Map's keys.)
    function walkingDistances(rows, start, walkableLetters) {
        const mapHeight = rows.length, mapWidth = rows[0].length;
        const steps = new Map([[squareKey(start[0], start[1]), 0]]);
        const toDo = [start];
        for (let next = 0; next < toDo.length; next++) {      // toDo[next] is the front of the queue
            const [column, row] = toDo[next];
            const stepsHere = steps.get(squareKey(column, row));
            for (const [columnStep, rowStep] of NEIGHBOR_STEPS) {
                const neighborColumn = column + columnStep, neighborRow = row + rowStep;
                const neighbor = squareKey(neighborColumn, neighborRow);
                if (neighborColumn >= 0 && neighborColumn < mapWidth && neighborRow >= 0 && neighborRow < mapHeight
                        && !steps.has(neighbor) && walkableLetters.has(rows[neighborRow][neighborColumn])) {
                    steps.set(neighbor, stepsHere + 1);
                    toDo.push([neighborColumn, neighborRow]);
                }
            }
        }
        return steps;
    }

    // True if any of the 4 squares beside [column, row] is in 'squares' (a Set or Map of squareKeys).
    function nextTo(column, row, squares) {
        return NEIGHBOR_STEPS.some(([columnStep, rowStep]) => squares.has(squareKey(column + columnStep, row + rowStep)));
    }

    function union(...letterSets) {
        const together = new Set();
        for (const letters of letterSets) for (const letter of letters) together.add(letter);
        return together;
    }

    // PLAY THE LEVEL, ROUGHLY (play_through() in levels.py): plain doors open; finding the red key
    // opens red doors, the blue key blue doors, reaching the boss the skull doors. Repeat until a
    // pass finds nothing new. 'doorThatNeverOpens' stays shut whatever happens (check 9).
    function playThrough(game, rows, start, doorThatNeverOpens) {
        const keysFound = new Set();
        while (true) {
            const walkable = union(game.floorLetters, 'D');
            if (keysFound.has('K')) walkable.add('R');
            if (keysFound.has('J')) walkable.add('B');
            if (keysFound.has('boss')) walkable.add('Z');
            walkable.delete(doorThatNeverOpens);
            const reachable = walkingDistances(rows, start, walkable);
            let foundSomethingNew = false;
            for (const key of reachable.keys()) {
                const [column, row] = key.split(',').map(Number);
                const letter = rows[row][column];
                const found = game.keyLetters.has(letter) ? letter : game.bossLetters.has(letter) ? 'boss' : null;
                if (found && !keysFound.has(found)) {
                    keysFound.add(found);
                    foundSomethingNew = true;
                }
            }
            if (!foundSomethingNew) return {reachable, walkable};
        }
    }

    // CHECK A MAP: validate() in levels.py, but instead of stopping at the first problem it
    // carries on and lists them all (where it can: without a player start, there's nowhere to
    // walk from). Each problem is {message, squares}: the words, and the squares to point at.
    // Also returns what the overlays in the editor draw: the squares a player can reach without
    // secrets ('reachable'), with secrets ('reachableWithSecrets'), and every square's walking
    // distance from the start with all doors open ('stepsFromStart'). Any of them can be null.
    function checkMap(game, rows) {
        const problems = [];
        const problem = (message, squares) => problems.push({message, squares: squares || []});
        const result = {problems, reachable: null, reachableWithSecrets: null, stepsFromStart: null};
        if (!rows.length) {
            problem('the map is empty.');
            return result;
        }
        const mapHeight = rows.length, mapWidth = rows[0].length;

        // CHECK 1: every row is as long as the first one. (Nothing else makes sense until it is.)
        rows.forEach((rowText, row) => {
            if (rowText.length !== mapWidth) {
                problem(`row ${row} has ${rowText.length} letters but row 0 has ${mapWidth}. `
                        + 'Every row must be the same length.', [[Math.min(rowText.length, mapWidth) , row]]);
            }
        });
        if (problems.length) return result;

        const everySquare = [];
        rows.forEach((rowText, row) => {
            for (let column = 0; column < mapWidth; column++) everySquare.push([column, row, rowText[column]]);
        });
        const allowedLetters = union(game.wallLetters, game.floorLetters, 'E');

        // CHECK 2: no unknown letters.
        for (const [column, row, letter] of everySquare) {
            if (!allowedLetters.has(letter)) {
                problem(`unknown letter '${letter}' at ${where(column, row)}. `
                        + 'See the LEGEND at the top of levels.py for the letters you can use.', [[column, row]]);
            }
        }
        // CHECK 3: the outside edge is all wall (or the exit switch).
        for (const [column, row, letter] of everySquare) {
            const onEdge = row === 0 || row === mapHeight - 1 || column === 0 || column === mapWidth - 1;
            if (onEdge && !game.edgeLetters.has(letter)) {
                problem(`the outside edge must be wall, but there is a '${letter}' at ${where(column, row)}.`, [[column, row]]);
            }
        }
        // CHECK 4: exactly one player start.
        const starts = everySquare.filter(([, , letter]) => letter === 'P').map(([column, row]) => [column, row]);
        if (starts.length !== 1) {
            problem(`there must be exactly one player start P, but there are ${starts.length}`
                    + (starts.length ? ': ' + starts.map(([column, row]) => where(column, row)).join('; ') : '.'), starts);
        }
        const start = starts.length === 1 ? starts[0] : null;

        let reachable = null, walkable = null;
        if (start) {
            ({reachable, walkable} = playThrough(game, rows, start));
            const reachableWithSecrets = walkingDistances(rows, start, union(walkable, 'S'));
            result.reachable = reachable;
            result.reachableWithSecrets = reachableWithSecrets;
            // CHECK 5: monsters and keys reachable without secrets, pickups somehow, and something
            // to stand on next to every secret wall and barrel.
            for (const [column, row, letter] of everySquare) {
                const here = squareKey(column, row);
                if ((game.monsterLetters.has(letter) || game.keyLetters.has(letter)) && !reachable.has(here)) {
                    problem(`the '${letter}' at ${where(column, row)} can't be reached. Monsters and `
                            + 'keys must be reachable without secret walls or blowing up barrels.', [[column, row]]);
                }
                if (game.pickupLetters.has(letter) && !reachableWithSecrets.has(here)) {
                    problem(`the '${letter}' at ${where(column, row)} can't be reached, even through secret walls.`, [[column, row]]);
                }
                if (letter === 'S' && !nextTo(column, row, reachable)) {
                    problem(`the secret wall at ${where(column, row)} has no reachable floor next to it.`, [[column, row]]);
                }
                if (letter === 'E' && !nextTo(column, row, reachable)) {
                    problem(`the barrel at ${where(column, row)} has no reachable floor next to it.`, [[column, row]]);
                }
            }
        }

        // CHECK 6: at most one boss.
        const bosses = everySquare.filter(([, , letter]) => game.bossLetters.has(letter)).map(([column, row]) => [column, row]);
        if (bosses.length > 1) {
            problem(`only one boss per level, but there are ${bosses.length}: `
                    + bosses.map(([column, row]) => where(column, row)).join('; '), bosses);
        }
        const wholeMapText = rows.join('');
        const skullDoors = everySquare.filter(([, , letter]) => letter === 'Z').map(([column, row]) => [column, row]);
        if (skullDoors.length && bosses.length !== 1) {
            problem('a skull door (Z) needs a boss (W or T) to drop the skull key.', skullDoors);
        }

        // CHECK 7: exactly one exit switch, with reachable floor next to it.
        const exits = everySquare.filter(([, , letter]) => letter === 'X').map(([column, row]) => [column, row]);
        if (exits.length !== 1) {
            problem(`there must be exactly one exit switch X, but there are ${exits.length}.`, exits);
        } else if (start) {
            const [exitColumn, exitRow] = exits[0];
            if (!nextTo(exitColumn, exitRow, reachable)) {
                problem(`the exit switch at ${where(exitColumn, exitRow)} can't be reached. Check the `
                        + 'keys come before their doors, and that floor touches the switch.', [exits[0]]);
            }
            // CHECK 8: the skull door really guards the exit.
            if (skullDoors.length) {
                const withoutSkullDoor = new Set(walkable);
                withoutSkullDoor.delete('Z');
                if (nextTo(exitColumn, exitRow, walkingDistances(rows, start, withoutSkullDoor))) {
                    problem('the exit can be reached without going through the skull door, so players '
                            + 'could skip the boss. Put the Z in the only way into the exit.', skullDoors);
                }
            }
            // CHECK 9: every key is needed.
            for (const [keyLetter, doorLetter, color] of [['K', 'R', 'red'], ['J', 'B', 'blue']]) {
                if (wholeMapText.includes(keyLetter)
                        && nextTo(exitColumn, exitRow, playThrough(game, rows, start, doorLetter).reachable)) {
                    problem(`the exit can be reached without going through a ${color} door (${doorLetter}), so `
                            + `the ${color} key (${keyLetter}) isn't needed. Close the other way round, or remove the key.`,
                            everySquare.filter(([, , letter]) => letter === doorLetter).map(([column, row]) => [column, row]));
                }
            }
        }

        // CHECK 10: no monster starts closer than game.safeStartDistance squares' walk (doors open).
        if (start) {
            const stepsFromStart = walkingDistances(rows, start, union(game.floorLetters, 'DRBZ'));
            result.stepsFromStart = stepsFromStart;
            for (const [column, row, letter] of everySquare) {
                const steps = stepsFromStart.get(squareKey(column, row));
                if (game.monsterLetters.has(letter) && steps !== undefined && steps < game.safeStartDistance) {
                    problem(`the '${letter}' at ${where(column, row)} is only ${steps} squares' walk `
                            + `from the player start. Monsters must start at least ${game.safeStartDistance} squares away.`,
                            [[column, row]]);
                }
            }
        }
        return result;
    }

    // ROUNDING, three ways, so the numbers match the game and the Python report exactly.
    // Scratch's 'round' block: 2.5 -> 3 (scratch_round() in config.py).
    function scratchRound(number) {
        return number >= 0 ? Math.floor(number + 0.5) : -Math.floor(-number + 0.5);
    }
    // Python's round(): halfway goes to the even number, so 2.5 -> 2 and 3.5 -> 4.
    function pythonRound(number) {
        const whole = Math.floor(number);
        if (number - whole === 0.5) return whole % 2 === 0 ? whole : whole + 1;
        return Math.round(number);
    }
    // Python's round(number, 2). Python looks at the exact number the computer stores: 1.575 is
    // really stored as 1.57499999..., so it rounds to 1.57 (toFixed() does the same). Only a number
    // stored exactly halfway goes to the even last digit, and the only ones are eighths: 1.125, 1.375 ...
    function pythonRound2(number) {
        const eighths = number * 8;
        if (Number.isInteger(eighths) && eighths % 2 !== 0) {
            const hundredths = Math.floor(number * 100);
            return (hundredths % 2 === 0 ? hundredths : hundredths + 1) / 100;
        }
        return Number(number.toFixed(2));
    }

    // Which supplies (H A I U ?) appear at this 'supplies kept' percent, in reading order
    // (supplies_kept() in config.py): a running count goes up by the percent at each supply;
    // reaching 100 keeps one and takes 100 off.
    function suppliesKept(game, rows, percentKept) {
        let share = game.supplyShareStart;
        const kept = [];
        rows.forEach((rowText, row) => {
            [...rowText.toUpperCase()].forEach((letter, column) => {
                if (game.supplyLetters.has(letter)) {
                    share += percentKept;
                    if (share >= 100) {
                        share -= 100;
                        kept.push([column, row, letter]);
                    }
                }
            });
        });
        return kept;
    }

    // Add up a list of numbers carefully, like math.fsum() in balance(): keep track of the tiny
    // bits plain adding loses to rounding (Neumaier's method), so a total like 365.5 is really
    // 365.5 and gets rounded the same way as in the Python balance report.
    function carefulSum(numbers) {
        let total = 0, lostBits = 0;
        for (const number of numbers) {
            const newTotal = total + number;
            lostBits += Math.abs(total) >= Math.abs(number) ? (total - newTotal) + number : (number - newTotal) + total;
            total = newTotal;
        }
        return total + lostBits;
    }

    function countLetter(text, letter) {
        return text.split(letter).length - 1;
    }

    // BALANCE: what a map gives you and what it throws at you, at one difficulty (balance() in
    // levels.py, where every number is explained).
    function balance(game, rows, difficultyName) {
        const difficulty = game.difficulties.find(each => each.name === difficultyName);
        const wholeMapText = rows.join('').toUpperCase();
        const monsterHealth = letter => scratchRound(game.monsters[letter].health * difficulty.monsterHealth / 100);
        const monsterLetters = Object.keys(game.monsters);
        let totalHealth = 0;
        for (const letter of monsterLetters) totalHealth += monsterHealth(letter) * countLetter(wholeMapText, letter);
        if (wholeMapText.includes('T')) totalHealth += 2 * monsterHealth(game.chargerLetter);

        const pickupsOnMap = suppliesKept(game, rows, difficulty.suppliesKept).map(([, , letter]) => letter)
            .concat([...wholeMapText].filter(letter => 'NQL'.includes(letter)));
        const ammoDamageOf = letter => {
            if (letter === '?') {
                return carefulSum(game.mysteryItems.map(ammoDamageOf)) / game.mysteryItems.length;
            }
            if (!(letter in game.ammoPickups)) return 0;
            const [ammoName, amount] = game.ammoPickups[letter];
            return game.damagePerAmmo[ammoName] * scratchRound(amount * difficulty.pickupAmount / 100);
        };
        const healthPack = scratchRound(game.healthPack * difficulty.pickupAmount / 100);
        const ammoDamage = carefulSum(pickupsOnMap.map(ammoDamageOf));
        const mysteryHealthShare = game.mysteryItems.filter(letter => letter === 'H').length / game.mysteryItems.length;
        const health = pythonRound(healthPack * (pickupsOnMap.filter(letter => letter === 'H').length
                                                 + pickupsOnMap.filter(letter => letter === '?').length * mysteryHealthShare));
        return {
            monsters: monsterLetters.reduce((sum, letter) => sum + countLetter(wholeMapText, letter), 0),
            monster_health: totalHealth,
            ammo_damage: pythonRound(ammoDamage),
            ammo_ratio: totalHealth ? pythonRound2(ammoDamage / totalHealth) : null,
            health,
        };
    }

    // The game data arrives as plain lists (JSON); turn the letter groups into Sets once.
    function prepareGame(gameData) {
        const game = Object.assign({}, gameData);
        for (const name of ['wallLetters', 'monsterLetters', 'bossLetters', 'pickupLetters', 'keyLetters',
                            'floorLetters', 'edgeLetters', 'supplyLetters']) {
            game[name] = new Set(gameData[name]);
        }
        return game;
    }

    const mapChecker = {checkMap, balance, prepareGame, squareKey, where, scratchRound};
    if (typeof module !== 'undefined' && module.exports) module.exports = mapChecker;   // Node (the tests)
    else window.mapChecker = mapChecker;                                                 // the web page
})();
