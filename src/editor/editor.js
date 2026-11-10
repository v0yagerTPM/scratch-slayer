// THE MAP EDITOR: draw a Scratch Slayer map with the mouse, see the build's map checks and the
// balance numbers as you go, and save it as a map file (src/maps/level N map A.txt).
//
// src/map_editor.py puts this file into docs/map-editor.html, together with map_checker.js,
// editor.css, page.html and EDITOR_DATA: the game's own letters, colors, tables and every map.
//
// THE IDEA: the map is a list of strings, one per row ('mapState.rows', rows[row][column]),
// exactly like the text file. Every tool changes that list; then the page redraws the picture,
// re-runs the checks and rewrites the text box. Undo keeps copies of the list from before each change.

(function () {
    'use strict';
    const data = window.EDITOR_DATA;
    const game = mapChecker.prepareGame(data.game);
    const look = data.look;
    const SAFE_DISTANCE = game.safeStartDistance;
    const DRAFT_STORAGE_KEY = 'scratch-slayer-map-editor-draft';
    const RULER_LEFT = 26, RULER_TOP = 18;   // room round the map for the column and row numbers
    const LETTER_FONT = '"IBM Plex Sans", Arial, sans-serif';

    // ---------------------------------------------------------------------------------------------
    // WHAT EACH LETTER IS CALLED, and the groups in the palette on the left
    // ---------------------------------------------------------------------------------------------
    const WALL_DIGITS = '123456789';
    function letterName(letter) {
        if (letter === '0') return 'floor';
        if (WALL_DIGITS.includes(letter)) return `wall ${letter} (${look.wallNames[letter]})`;
        if (letter in look.specialWalls) return look.specialWalls[letter];
        if (letter in look.things) return look.things[letter][1];
        return `unknown letter '${letter}'`;
    }
    const PALETTE_GROUPS = [
        ['Floor and walls', '0' + WALL_DIGITS],
        ['Doors and switches', 'DRBZSX'],
        ['Player start', 'P'],
        ['Monsters', 'MVGCF'],
        ['Bosses (carry the skull key)', 'WT'],
        ['Health and ammo', 'HAIU?'],
        ['Weapons', 'NQL'],
        ['Keys', 'KJ'],
        ['Exploding barrel', 'E'],
    ];
    const PALETTE_LETTERS = PALETTE_GROUPS.map(([, letters]) => letters).join('');
    const TOOLS = [
        ['paint', 'Paint'], ['rectangle', 'Rectangle'], ['box', 'Room walls'],
        ['fill', 'Fill'], ['pick', 'Pick up'],
    ];
    const TOOL_HINTS = {
        paint: 'Click or drag to paint squares.',
        rectangle: 'Drag from corner to corner to fill a rectangle.',
        box: 'Drag from corner to corner to draw a room\'s walls (the inside is left alone).',
        fill: 'Click to repaint a whole patch of the same letter.',
        pick: 'Click a square to use its letter.',
    };

    // ---------------------------------------------------------------------------------------------
    // THE MAP BEING EDITED
    // ---------------------------------------------------------------------------------------------
    const mapState = {
        rows: [],              // the map, one string per row
        originalRows: [],      // as it was when it was opened (for "N squares changed" and Revert)
        fileName: '',          // without .txt
        gameMapNumber: -1,     // which of data.maps it came from, or -1
        secretLook: '9',       // the wall digit secret walls are drawn as
        startAngle: 270,       // the arrow on the player start
    };
    const editor = {
        letter: '1', tool: 'paint', zoom: 18,
        undoList: [], redoList: [],
        hoverSquare: null,           // [column, row] under the mouse
        highlightedSquares: [],      // squares of the problem the mouse is on
        stroke: null,                // the drag in progress: {before, anchor, last, letter}
        lastPainted: null,           // for Shift+click straight lines
        analysis: null,              // what mapChecker.checkMap() found
        typingStartedFrom: null,     // the map before typing in the text box began
    };

    // ---------------------------------------------------------------------------------------------
    // SMALL HELPERS
    // ---------------------------------------------------------------------------------------------
    const page = id => document.getElementById(id);
    const mapWidth = () => Math.max(0, ...mapState.rows.map(row => row.length));
    const mapHeight = () => mapState.rows.length;
    const letterAt = (column, row) => (mapState.rows[row] || '')[column];

    function setLetter(rows, column, row, letter) {
        const rowText = rows[row];
        if (rowText === undefined || column < 0 || column >= rowText.length || rowText[column] === letter) return false;
        rows[row] = rowText.slice(0, column) + letter + rowText.slice(column + 1);
        return true;
    }

    // Read a map file's text the way load_map() in levels.py does: any line endings, an invisible
    // byte-order mark at the start is skipped, blank lines at the end are dropped.
    function rowsFromText(text) {
        const rows = text.replace(/^﻿/, '').split(/\r\n|\r|\n/);
        while (rows.length && rows[rows.length - 1].trim() === '') rows.pop();
        return rows;
    }
    const textFromRows = rows => rows.join('\n') + '\n';

    // Every square on a straight line between two squares (Bresenham's line algorithm, the one
    // drawing programs have used since the 1960s), so a fast drag doesn't leave gaps.
    function squaresOnLine([fromColumn, fromRow], [toColumn, toRow]) {
        const squares = [];
        const columnDistance = Math.abs(toColumn - fromColumn), rowDistance = -Math.abs(toRow - fromRow);
        const columnStep = fromColumn < toColumn ? 1 : -1, rowStep = fromRow < toRow ? 1 : -1;
        let error = columnDistance + rowDistance, column = fromColumn, row = fromRow;
        while (true) {
            squares.push([column, row]);
            if (column === toColumn && row === toRow) return squares;
            const doubled = 2 * error;
            if (doubled >= rowDistance) { error += rowDistance; column += columnStep; }
            if (doubled <= columnDistance) { error += columnDistance; row += rowStep; }
        }
    }

    function showToast(message) {
        const toast = page('toast');
        toast.textContent = message;
        toast.hidden = false;
        clearTimeout(showToast.timer);
        showToast.timer = setTimeout(() => { toast.hidden = true; }, 3200);
    }

    // ---------------------------------------------------------------------------------------------
    // UNDO AND REDO: a copy of everything about the map, from before each change
    // ---------------------------------------------------------------------------------------------
    function snapshot() {
        return JSON.parse(JSON.stringify(mapState));
    }
    function restore(saved) {
        Object.assign(mapState, JSON.parse(JSON.stringify(saved)));
    }
    function remember(before) {
        editor.undoList.push(before);
        if (editor.undoList.length > 300) editor.undoList.shift();
        editor.redoList = [];
    }
    function undo() {
        if (!editor.undoList.length) return;
        editor.redoList.push(snapshot());
        restore(editor.undoList.pop());
        mapChanged({everything: true});
    }
    function redo() {
        if (!editor.redoList.length) return;
        editor.undoList.push(snapshot());
        restore(editor.redoList.pop());
        mapChanged({everything: true});
    }
    // Make a change as one undo step: 'change' edits mapState and returns false if nothing changed.
    function change(makeTheChange) {
        const before = snapshot();
        if (makeTheChange() === false || JSON.stringify(before) === JSON.stringify(mapState)) return;
        remember(before);
        mapChanged({everything: true});
    }

    // ---------------------------------------------------------------------------------------------
    // DRAWING ONE SQUARE: the same colors and tokens as the map pictures (src/map_preview.py)
    // ---------------------------------------------------------------------------------------------
    function drawLetterInSquare(context, letter, left, top, size, color) {
        if (size < 11) return;
        context.fillStyle = color;
        context.font = `700 ${Math.round(size * 0.62)}px ${LETTER_FONT}`;
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(letter, left + size / 2, top + size / 2 + size * 0.04);
    }

    // The square itself: floor, a wall in its color, a door or switch, or a secret wall.
    function drawGround(context, letter, left, top, size, secretLook) {
        if (letter === 'S') {
            context.fillStyle = look.wallColors[secretLook] || look.floorColor;
            context.fillRect(left, top, size, size);
            context.save();
            context.strokeStyle = '#ffd23f';
            context.lineWidth = Math.max(1, size / 10);
            context.setLineDash([size / 6, size / 8]);
            context.strokeRect(left + size * 0.12, top + size * 0.12, size * 0.76, size * 0.76);
            context.restore();
        } else if (letter in look.doorColors) {
            context.fillStyle = look.doorColors[letter];
            context.fillRect(left, top, size, size);
            drawLetterInSquare(context, letter, left, top, size, letter === 'X' ? '#000' : '#fff');
        } else if (WALL_DIGITS.includes(letter)) {
            context.fillStyle = look.wallColors[letter];
            context.fillRect(left, top, size, size);
        } else if (letter === '0' || letter in look.things) {
            context.fillStyle = look.floorColor;
            context.fillRect(left, top, size, size);
        } else {
            // A letter the game doesn't know (or a stray space): bright, so it gets noticed.
            context.fillStyle = '#7a1f5c';
            context.fillRect(left, top, size, size);
            drawLetterInSquare(context, letter === ' ' ? '␣' : letter, left, top, size, '#fff');
        }
    }

    // A thing standing on the floor: a round token with its letter (keys are diamonds, bosses are
    // bigger, the player start has an arrow for the way they face).
    function drawThing(context, letter, left, top, size, startAngle) {
        if (!(letter in look.things)) return;
        const [color] = look.things[letter];
        const middleX = left + size / 2, middleY = top + size / 2;
        context.fillStyle = color;
        context.strokeStyle = '#000';
        context.lineWidth = 1;
        if (letter === 'K' || letter === 'J') {
            const half = size * 0.36;
            context.beginPath();
            context.moveTo(middleX, middleY - half);
            context.lineTo(middleX + half, middleY);
            context.lineTo(middleX, middleY + half);
            context.lineTo(middleX - half, middleY);
            context.closePath();
            context.fill();
            context.stroke();
            return;
        }
        const radius = size * (look.bossLetters.includes(letter) ? 0.62 : 0.42);
        context.beginPath();
        context.arc(middleX, middleY, radius, 0, Math.PI * 2);
        context.fill();
        context.stroke();
        if (letter === 'P') {    // 0 = right, 90 = down, like the game
            context.save();
            context.translate(middleX, middleY);
            context.rotate(startAngle * Math.PI / 180);
            context.scale(size / 16, size / 16);
            context.fillStyle = '#fff';
            context.beginPath();
            context.moveTo(-3, -3.5);
            context.lineTo(4.5, 0);
            context.lineTo(-3, 3.5);
            context.closePath();
            context.fill();
            context.restore();
        } else {
            const darkLetter = color === '#f2c200' || color === '#fd7e14';
            drawLetterInSquare(context, letter, left, top, size * 0.92, darkLetter ? '#000' : '#fff');
        }
    }

    // ---------------------------------------------------------------------------------------------
    // DRAWING THE WHOLE MAP
    // ---------------------------------------------------------------------------------------------
    const canvas = page('map-canvas');
    const context = canvas.getContext('2d');

    function squareLeft(column) { return RULER_LEFT + column * editor.zoom; }
    function squareTop(row) { return RULER_TOP + row * editor.zoom; }

    function drawMap() {
        const size = editor.zoom, width = mapWidth(), height = mapHeight();
        const pixelWidth = RULER_LEFT + width * size + 2, pixelHeight = RULER_TOP + height * size + 2;
        const sharpness = window.devicePixelRatio || 1;
        if (canvas.width !== Math.round(pixelWidth * sharpness) || canvas.height !== Math.round(pixelHeight * sharpness)) {
            canvas.width = Math.round(pixelWidth * sharpness);
            canvas.height = Math.round(pixelHeight * sharpness);
            canvas.style.width = pixelWidth + 'px';
            canvas.style.height = pixelHeight + 'px';
        }
        context.setTransform(sharpness, 0, 0, sharpness, 0, 0);
        context.fillStyle = '#0e0d10';
        context.fillRect(0, 0, pixelWidth, pixelHeight);

        // Column numbers along the top and row numbers down the left, every fifth one.
        context.fillStyle = '#8a8a8a';
        context.font = '10px ' + 'Arial, sans-serif';
        context.textBaseline = 'alphabetic';
        context.textAlign = 'center';
        for (let column = 0; column < width; column += 5) context.fillText(column, squareLeft(column) + size / 2, RULER_TOP - 5);
        context.textAlign = 'right';
        for (let row = 0; row < height; row += 5) context.fillText(row, RULER_LEFT - 5, squareTop(row) + size / 2 + 3.5);

        // The squares first, then the things on them (so a big boss token isn't covered up).
        mapState.rows.forEach((rowText, row) => {
            for (let column = 0; column < width; column++) {
                const left = squareLeft(column), top = squareTop(row);
                if (column >= rowText.length) {      // past the end of a short row: nothing here
                    context.fillStyle = '#2a0d1f';
                    context.fillRect(left, top, size, size);
                    continue;
                }
                drawGround(context, rowText[column], left, top, size, mapState.secretLook);
            }
        });
        drawOverlays(size);
        mapState.rows.forEach((rowText, row) => {
            [...rowText].forEach((letter, column) => drawThing(context, letter, squareLeft(column), squareTop(row), size, mapState.startAngle));
        });

        // Grid lines: faint round every square, brighter every 5 squares to help count.
        context.lineWidth = 1;
        for (let column = 0; column <= width; column++) {
            context.strokeStyle = column % 5 === 0 ? 'rgba(255,255,255,0.16)' : 'rgba(255,255,255,0.045)';
            context.beginPath();
            context.moveTo(squareLeft(column) + 0.5, RULER_TOP);
            context.lineTo(squareLeft(column) + 0.5, squareTop(height));
            context.stroke();
        }
        for (let row = 0; row <= height; row++) {
            context.strokeStyle = row % 5 === 0 ? 'rgba(255,255,255,0.16)' : 'rgba(255,255,255,0.045)';
            context.beginPath();
            context.moveTo(RULER_LEFT, squareTop(row) + 0.5);
            context.lineTo(squareLeft(width), squareTop(row) + 0.5);
            context.stroke();
        }

        // The squares of the problem the mouse is on, and the square under the mouse.
        context.lineWidth = 2.5;
        context.strokeStyle = '#ff6464';
        for (const [column, row] of editor.highlightedSquares) {
            context.strokeRect(squareLeft(column) - 2, squareTop(row) - 2, size + 4, size + 4);
        }
        if (editor.hoverSquare) {
            const [column, row] = editor.hoverSquare;
            context.lineWidth = 1.5;
            context.strokeStyle = '#ffffff';
            context.strokeRect(squareLeft(column) + 0.75, squareTop(row) + 0.75, size - 1.5, size - 1.5);
        }
    }

    // Shading on top of the floor: floor nobody can reach (red), floor only reachable through a
    // secret wall (gold), and the start safety zone where no monster may stand (green).
    function drawOverlays(size) {
        const analysis = editor.analysis;
        if (!analysis || !analysis.reachable) return;
        const showReach = page('show-reach').checked, showSafeZone = page('show-safe-zone').checked;
        mapState.rows.forEach((rowText, row) => {
            [...rowText].forEach((letter, column) => {
                const key = mapChecker.squareKey(column, row);
                const left = squareLeft(column), top = squareTop(row);
                const isFloor = game.floorLetters.has(letter);
                if (showReach && isFloor) {
                    if (!analysis.reachableWithSecrets.has(key)) {
                        context.fillStyle = 'rgba(255, 70, 70, 0.32)';
                        context.fillRect(left, top, size, size);
                    } else if (!analysis.reachable.has(key)) {
                        context.fillStyle = 'rgba(255, 210, 63, 0.16)';
                        context.fillRect(left, top, size, size);
                    }
                }
                if (showSafeZone && analysis.stepsFromStart) {
                    const steps = analysis.stepsFromStart.get(key);
                    if (steps !== undefined && steps < SAFE_DISTANCE && game.floorLetters.has(letter)) {
                        context.fillStyle = 'rgba(79, 209, 107, 0.13)';
                        context.fillRect(left, top, size, size);
                    }
                }
            });
        });
    }

    // ---------------------------------------------------------------------------------------------
    // THE MOUSE ON THE MAP
    // ---------------------------------------------------------------------------------------------
    function squareUnderPointer(event) {
        const box = canvas.getBoundingClientRect();
        const column = Math.floor((event.clientX - box.left - RULER_LEFT) / editor.zoom);
        const row = Math.floor((event.clientY - box.top - RULER_TOP) / editor.zoom);
        if (row < 0 || row >= mapHeight() || column < 0 || column >= mapWidth()) return null;
        return [column, row];
    }

    // Flood fill (like the paint bucket in a drawing program): the patch of squares with the same
    // letter as the one clicked, joined up, side to side.
    function fillPatch(rows, [startColumn, startRow], letter) {
        const oldLetter = rows[startRow][startColumn];
        if (oldLetter === letter) return;
        const toDo = [[startColumn, startRow]];
        while (toDo.length) {
            const [column, row] = toDo.pop();
            if ((rows[row] || '')[column] !== oldLetter) continue;
            setLetter(rows, column, row, letter);
            toDo.push([column + 1, row], [column - 1, row], [column, row + 1], [column, row - 1]);
        }
    }

    function rectangleSquares([firstColumn, firstRow], [secondColumn, secondRow], outlineOnly) {
        const squares = [];
        const left = Math.min(firstColumn, secondColumn), right = Math.max(firstColumn, secondColumn);
        const top = Math.min(firstRow, secondRow), bottom = Math.max(firstRow, secondRow);
        for (let row = top; row <= bottom; row++) {
            for (let column = left; column <= right; column++) {
                const onOutline = row === top || row === bottom || column === left || column === right;
                if (!outlineOnly || onOutline) squares.push([column, row]);
            }
        }
        return squares;
    }

    function pickLetter(square) {
        const letter = letterAt(...square);
        if (letter !== undefined && PALETTE_LETTERS.includes(letter)) chooseLetter(letter);
    }

    canvas.addEventListener('contextmenu', event => event.preventDefault());
    canvas.addEventListener('pointerdown', event => {
        const square = squareUnderPointer(event);
        if (!square || event.button > 2) return;
        event.preventDefault();
        if (editor.tool === 'pick' || event.altKey) {
            pickLetter(square);
            return;
        }
        const letter = event.button === 2 ? '0' : editor.letter;
        const before = snapshot();
        if (editor.tool === 'fill') {
            fillPatch(mapState.rows, square, letter);
            finishStroke(before);
            return;
        }
        canvas.setPointerCapture(event.pointerId);
        editor.stroke = {before, anchor: square, last: square, letter};
        if (editor.tool === 'paint') {
            const from = event.shiftKey && editor.lastPainted ? editor.lastPainted : square;
            for (const [column, row] of squaresOnLine(from, square)) setLetter(mapState.rows, column, row, letter);
            editor.lastPainted = square;
        } else {
            previewRectangle(square);
        }
        mapChanged({quick: true});
    });
    canvas.addEventListener('pointermove', event => {
        const square = squareUnderPointer(event);
        const moved = String(square) !== String(editor.hoverSquare);
        editor.hoverSquare = square;
        if (moved) showSquareInfo();
        const stroke = editor.stroke;
        if (stroke && square && String(square) !== String(stroke.last)) {
            if (editor.tool === 'paint') {
                for (const [column, row] of squaresOnLine(stroke.last, square)) setLetter(mapState.rows, column, row, stroke.letter);
                editor.lastPainted = square;
            } else {
                previewRectangle(square);
            }
            stroke.last = square;
            mapChanged({quick: true});
        } else if (moved) {
            drawMap();
        }
    });
    function endStroke() {
        if (!editor.stroke) return;
        const before = editor.stroke.before;
        editor.stroke = null;
        finishStroke(before);
    }
    canvas.addEventListener('pointerup', endStroke);
    canvas.addEventListener('pointercancel', endStroke);
    canvas.addEventListener('pointerleave', () => {
        if (editor.stroke) return;
        editor.hoverSquare = null;
        showSquareInfo();
        drawMap();
    });

    // Rectangle and room tools: while dragging, draw the rectangle on a fresh copy of the map
    // from before the drag, so moving the mouse back shrinks it again.
    function previewRectangle(square) {
        const stroke = editor.stroke;
        mapState.rows = stroke.before.rows.slice();
        for (const [column, row] of rectangleSquares(stroke.anchor, square, editor.tool === 'box')) {
            setLetter(mapState.rows, column, row, stroke.letter);
        }
    }

    function finishStroke(before) {
        if (JSON.stringify(before.rows) !== JSON.stringify(mapState.rows)) remember(before);
        mapChanged({everything: true});
    }

    // ---------------------------------------------------------------------------------------------
    // AFTER EVERY CHANGE: check, redraw, rewrite the text, save a draft
    // ---------------------------------------------------------------------------------------------
    function mapChanged({quick = false} = {}) {
        // During a drag only the picture is redrawn; the checks wait for the mouse button to go up.
        if (!quick) editor.analysis = mapChecker.checkMap(game, mapState.rows);
        drawMap();
        if (quick) return;
        showProblems();
        showBalance();
        showSquareInfo();
        showMapDetails();
        if (document.activeElement !== page('map-text')) page('map-text').value = textFromRows(mapState.rows);
        page('undo-button').disabled = !editor.undoList.length;
        page('redo-button').disabled = !editor.redoList.length;
        saveDraft();
    }

    function showProblems() {
        const list = page('problem-list'), badge = page('check-badge');
        const problems = editor.analysis.problems;
        list.replaceChildren();
        if (!problems.length) {
            const item = document.createElement('li');
            item.className = 'passes';
            item.textContent = 'This map passes every check. Ready for npm test.';
            list.append(item);
        }
        problems.forEach((problem, number) => {
            const item = document.createElement('li');
            item.textContent = problem.message.charAt(0).toUpperCase() + problem.message.slice(1);
            item.tabIndex = 0;
            if (number === 0) item.classList.add('first-problem');
            const highlight = () => { editor.highlightedSquares = problem.squares; drawMap(); };
            const unhighlight = () => { editor.highlightedSquares = []; drawMap(); };
            item.addEventListener('mouseenter', highlight);
            item.addEventListener('focus', highlight);
            item.addEventListener('mouseleave', unhighlight);
            item.addEventListener('blur', unhighlight);
            item.addEventListener('click', () => { highlight(); scrollToSquare(problem.squares[0]); });
            list.append(item);
        });
        badge.textContent = problems.length ? `${problems.length} problem${problems.length === 1 ? '' : 's'}` : 'passes';
        badge.className = 'check-badge ' + (problems.length ? 'fails' : 'passes');
    }

    function scrollToSquare(square) {
        if (!square) return;
        const scroller = page('canvas-scroller');
        scroller.scrollTo({
            left: squareLeft(square[0]) - scroller.clientWidth / 2,
            top: squareTop(square[1]) - scroller.clientHeight / 2,
            behavior: 'smooth',
        });
    }

    function showBalance() {
        const table = page('balance-table');
        const rectangle = editor.analysis.problems.every(problem => !problem.message.includes('Every row must be the same length'));
        if (!rectangle || !mapState.rows.length) {
            table.innerHTML = '<tbody><tr><td>Make every row the same length first.</td></tr></tbody>';
            page('monster-counts').replaceChildren();
            return;
        }
        const numbers = game.difficulties.map(difficulty => mapChecker.balance(game, mapState.rows, difficulty.name));
        const headings = game.difficulties.map(difficulty => `<th scope="col">${difficulty.name}</th>`).join('');
        const tableRow = (name, key) => `<tr><th scope="row">${name}</th>`
            + numbers.map(each => `<td>${each[key] === null ? '–' : each[key]}</td>`).join('') + '</tr>';
        table.innerHTML = `<thead><tr><th></th>${headings}</tr></thead><tbody>`
            + tableRow('Monster health', 'monster_health') + tableRow('Ammo damage', 'ammo_damage')
            + tableRow('Ammo ratio', 'ammo_ratio') + tableRow('Health', 'health') + '</tbody>';
        const wholeMap = mapState.rows.join('');
        const counts = page('monster-counts');
        counts.replaceChildren();
        for (const [letter, monster] of Object.entries(game.monsters)) {
            const count = wholeMap.split(letter).length - 1;
            if (!count) continue;
            const entry = document.createElement('span');
            entry.innerHTML = `<strong>${count}</strong> ${monster.name}${count === 1 ? '' : 's'}`;
            counts.append(entry);
        }
        if (!counts.children.length) counts.textContent = 'No monsters yet.';
    }

    function showSquareInfo() {
        const info = page('square-info');
        const square = editor.hoverSquare;
        if (!square) {
            info.textContent = TOOL_HINTS[editor.tool] + ' Point at a square to see what it is.';
            return;
        }
        const [column, row] = square;
        const letter = letterAt(column, row);
        const parts = [`<strong>column ${column}, row ${row}</strong>`, `Scratch: item ${row + 1}, letter ${column + 1}`];
        if (letter !== undefined) parts.push(`<strong>${letter === ' ' ? '␣' : escapeHtml(letter)}</strong> ${escapeHtml(letterName(letter))}`);
        const analysis = editor.analysis;
        if (analysis && analysis.stepsFromStart && letter !== undefined) {
            const key = mapChecker.squareKey(column, row);
            const steps = analysis.stepsFromStart.get(key);
            if (steps !== undefined) parts.push(`${steps} squares' walk from the start`);
            if (game.floorLetters.has(letter)) {
                if (!analysis.reachableWithSecrets.has(key)) parts.push('nobody can get here');
                else if (!analysis.reachable.has(key)) parts.push('only through a secret wall');
            }
        }
        info.innerHTML = parts.join(' · ');
    }

    function escapeHtml(text) {
        return text.replace(/[&<>"]/g, character => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[character]);
    }

    function showMapDetails() {
        page('map-size').textContent = `${mapWidth()} × ${mapHeight()} squares`;
        const fileNameInput = page('file-name-input');
        if (document.activeElement !== fileNameInput) fileNameInput.value = mapState.fileName;
        page('secret-look-choice').value = mapState.secretLook;
        page('start-angle-choice').value = String(mapState.startAngle);
        page('game-map-choice').value = String(mapState.gameMapNumber);
        // How many squares differ from the map as it was opened.
        const original = mapState.originalRows, label = page('changes-label');
        let message;
        if (JSON.stringify(original) === JSON.stringify(mapState.rows)) message = 'unchanged';
        else if (original.length !== mapState.rows.length || original.some((rowText, row) => rowText.length !== mapState.rows[row].length)) message = 'size changed';
        else {
            let changed = 0;
            original.forEach((rowText, row) => { for (let column = 0; column < rowText.length; column++) if (rowText[column] !== mapState.rows[row][column]) changed++; });
            message = `${changed} square${changed === 1 ? '' : 's'} changed`;
        }
        label.textContent = message;
        label.classList.toggle('has-changes', message !== 'unchanged');
        page('revert-button').disabled = message === 'unchanged';
        const savePlace = `src/maps/${mapState.fileName}.txt`;
        page('save-hint').innerHTML = data.canDownload
            ? `To put it in the game: save it as <code>${escapeHtml(savePlace)}</code> (Download does), then run <code>npm test</code>. A new map also needs its record in <code>src/levels.py</code>.`
            : `To put it in the game: copy the text into <code>${escapeHtml(savePlace)}</code>, then run <code>npm test</code>. A new map also needs its record in <code>src/levels.py</code>.`;
    }

    // ---------------------------------------------------------------------------------------------
    // OPENING, MAKING AND SAVING MAPS
    // ---------------------------------------------------------------------------------------------
    function openMap({rows, fileName, gameMapNumber = -1, secretLook = mapState.secretLook, startAngle = mapState.startAngle}) {
        change(() => {
            Object.assign(mapState, {rows: rows.slice(), originalRows: rows.slice(), fileName, gameMapNumber,
                                     secretLook: String(secretLook), startAngle: Number(startAngle)});
        });
        editor.lastPainted = null;
        page('canvas-scroller').scrollTo(0, 0);
    }

    function openGameMap(number) {
        const gameMap = data.maps[number];
        openMap({rows: gameMap.rows, fileName: gameMap.fileName, gameMapNumber: number,
                 secretLook: gameMap.secretLook, startAngle: gameMap.angle});
    }

    function newMap(width, height, wallLetter) {
        const rows = [];
        for (let row = 0; row < height; row++) {
            const edgeRow = row === 0 || row === height - 1;
            rows.push(edgeRow ? wallLetter.repeat(width) : wallLetter + '0'.repeat(width - 2) + wallLetter);
        }
        const middle = Math.floor(width / 2);
        setLetter(rows, middle, 0, 'X');
        setLetter(rows, middle, height - 2, 'P');
        openMap({rows, fileName: `level ${data.levelCount + 1} map A`, startAngle: 270});
    }

    function downloadMap() {
        const file = new Blob([textFromRows(mapState.rows)], {type: 'text/plain'});
        const link = document.createElement('a');
        link.href = URL.createObjectURL(file);
        link.download = (mapState.fileName || 'map') + '.txt';
        document.body.append(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(link.href), 1000);
        showToast(`Saved ${link.download} (look in your Downloads folder).`);
    }

    function copyMapText() {
        const text = textFromRows(mapState.rows);
        const selectTheText = () => {
            const box = page('map-text');
            box.focus();
            box.select();
            showToast('The map text is selected: press Ctrl+C (or ⌘C) to copy it.');
        };
        if (!navigator.clipboard) return selectTheText();
        navigator.clipboard.writeText(text).then(() => showToast('Copied the map text.'), selectTheText);
    }

    // Grow or shrink the map by one column or row, just inside the right or bottom wall, so the
    // outside wall stays closed: a new column copies the edge letter at the top and bottom rows
    // and is floor in between.
    function resizeMap(direction, amount) {
        change(() => {
            const rows = mapState.rows, width = mapWidth(), height = mapHeight();
            if (direction === 'columns') {
                if (amount < 0 && width <= 3) return false;
                mapState.rows = rows.map((rowText, row) => {
                    const edgeRow = row === 0 || row === height - 1;
                    const at = rowText.length - 1;
                    if (amount > 0) return rowText.slice(0, at) + (edgeRow ? rowText[at] : '0') + rowText.slice(at);
                    return rowText.slice(0, at - 1) + rowText.slice(at);
                });
            } else {
                if (amount < 0 && height <= 3) return false;
                const at = height - 1;
                if (amount > 0) {
                    const lastRow = rows[at];
                    const newRow = lastRow[0] + '0'.repeat(Math.max(0, lastRow.length - 2)) + lastRow[lastRow.length - 1];
                    mapState.rows = rows.slice(0, at).concat([newRow], rows.slice(at));
                } else {
                    mapState.rows = rows.slice(0, at - 1).concat(rows.slice(at));
                }
            }
        });
    }

    // ---------------------------------------------------------------------------------------------
    // DRAFTS: the map is kept in this browser, so closing the page doesn't lose it
    // ---------------------------------------------------------------------------------------------
    function saveDraft() {
        try {
            localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify({map: mapState, letter: editor.letter, zoom: editor.zoom}));
        } catch (storageRefused) { /* private window or storage switched off: no draft, that's all */ }
    }
    function loadDraft() {
        try {
            const draft = JSON.parse(localStorage.getItem(DRAFT_STORAGE_KEY));
            if (!draft || !Array.isArray(draft.map.rows) || !draft.map.rows.length) return false;
            Object.assign(mapState, draft.map);
            if (PALETTE_LETTERS.includes(draft.letter)) editor.letter = draft.letter;
            if (draft.zoom) editor.zoom = Number(draft.zoom);
            return true;
        } catch (noDraft) {
            return false;
        }
    }

    // ---------------------------------------------------------------------------------------------
    // THE PALETTE AND THE TOOLS
    // ---------------------------------------------------------------------------------------------
    function chooseLetter(letter) {
        editor.letter = letter;
        document.querySelectorAll('.letter-button').forEach(button => {
            button.setAttribute('aria-pressed', String(button.dataset.letter === letter));
        });
        page('current-letter-label').textContent = `${letter} · ${letterName(letter)}`;
        if (editor.tool === 'pick') chooseTool('paint');
        saveDraft();
    }
    function chooseTool(tool) {
        editor.tool = tool;
        document.querySelectorAll('#tool-buttons button').forEach(button => {
            button.setAttribute('aria-checked', String(button.dataset.tool === tool));
        });
        canvas.style.cursor = tool === 'pick' ? 'copy' : 'crosshair';
        showSquareInfo();
    }

    function buildPalette() {
        const palette = page('palette');
        for (const [groupName, letters] of PALETTE_GROUPS) {
            const group = document.createElement('div');
            group.className = 'palette-group';
            group.innerHTML = `<span class="palette-group-name">${groupName}</span><div class="palette-letters"></div>`;
            for (const letter of letters) {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'letter-button';
                button.dataset.letter = letter;
                button.title = `${letter}: ${letterName(letter)}`;
                button.setAttribute('aria-label', `${letter}, ${letterName(letter)}`);
                const swatch = document.createElement('canvas');
                const sharpness = window.devicePixelRatio || 1;
                swatch.width = swatch.height = Math.round(26 * sharpness);
                const swatchContext = swatch.getContext('2d');
                swatchContext.scale(sharpness, sharpness);
                drawGround(swatchContext, letter, 0, 0, 26, '9');
                drawThing(swatchContext, letter, 0, 0, 26, 0);
                if (WALL_DIGITS.includes(letter) || letter === '0') drawLetterInSquare(swatchContext, letter, 0, 0, 26, 'rgba(255,255,255,0.75)');
                button.append(swatch);
                button.addEventListener('click', () => chooseLetter(letter));
                group.querySelector('.palette-letters').append(button);
            }
            palette.append(group);
        }
        const toolButtons = page('tool-buttons');
        for (const [tool, name] of TOOLS) {
            const button = document.createElement('button');
            button.type = 'button';
            button.dataset.tool = tool;
            button.setAttribute('role', 'radio');
            button.textContent = name;
            button.title = TOOL_HINTS[tool];
            button.addEventListener('click', () => chooseTool(tool));
            toolButtons.append(button);
        }
    }

    function buildChoices() {
        const mapChoice = page('game-map-choice');
        const yourMap = document.createElement('option');
        yourMap.value = '-1';
        yourMap.textContent = '(your own map)';
        mapChoice.append(yourMap);
        let group = null;
        data.maps.forEach((gameMap, number) => {
            if (!group || group.dataset.level !== String(gameMap.level)) {
                group = document.createElement('optgroup');
                group.dataset.level = String(gameMap.level);
                group.label = `Level ${gameMap.level}: ${gameMap.levelName}`;
                mapChoice.append(group);
            }
            const option = document.createElement('option');
            option.value = String(number);
            option.textContent = `${gameMap.level}-${gameMap.letter} ${gameMap.mapName}`;
            group.append(option);
        });
        for (const choiceId of ['secret-look-choice', 'new-map-wall']) {
            for (const digit of WALL_DIGITS) {
                const option = document.createElement('option');
                option.value = digit;
                option.textContent = `wall ${digit} (${look.wallNames[digit]})`;
                page(choiceId).append(option);
            }
        }
        page('new-map-wall').value = '1';
    }

    // ---------------------------------------------------------------------------------------------
    // BUTTONS, FIELDS AND KEYS
    // ---------------------------------------------------------------------------------------------
    function connectControls() {
        page('game-map-choice').addEventListener('change', event => {
            const number = Number(event.target.value);
            if (number >= 0) {
                openGameMap(number);
                showToast(`Opened ${data.maps[number].fileName}. Undo brings back the map you had.`);
            }
        });
        page('new-map-button').addEventListener('click', () => {
            page('new-map-form').hidden = !page('new-map-form').hidden;
            if (!page('new-map-form').hidden) page('new-map-width').focus();
        });
        page('new-map-cancel').addEventListener('click', () => { page('new-map-form').hidden = true; });
        page('new-map-form').addEventListener('submit', event => {
            event.preventDefault();
            const clamp = value => Math.max(5, Math.min(64, Math.round(Number(value)) || 20));
            newMap(clamp(page('new-map-width').value), clamp(page('new-map-height').value), page('new-map-wall').value);
            page('new-map-form').hidden = true;
            showToast('Made a new map. Undo brings back the map you had.');
        });
        page('open-file-input').addEventListener('change', event => {
            const file = event.target.files[0];
            if (file) openFile(file);
            event.target.value = '';
        });
        // Drop a .txt file anywhere on the page to open it.
        document.addEventListener('dragover', event => event.preventDefault());
        document.addEventListener('drop', event => {
            event.preventDefault();
            const file = event.dataTransfer.files[0];
            if (file) openFile(file);
        });
        page('undo-button').addEventListener('click', undo);
        page('redo-button').addEventListener('click', redo);
        page('copy-button').addEventListener('click', copyMapText);
        const downloadButton = page('download-button');
        if (data.canDownload) downloadButton.addEventListener('click', downloadMap);
        else downloadButton.hidden = true;
        page('revert-button').addEventListener('click', () => change(() => { mapState.rows = mapState.originalRows.slice(); }));
        document.querySelectorAll('[data-resize]').forEach(button => {
            const [direction, amount] = button.dataset.resize.split(':');
            button.addEventListener('click', () => resizeMap(direction, Number(amount)));
        });
        page('file-name-input').addEventListener('input', event => {
            mapState.fileName = event.target.value.replace(/\.txt$/i, '');
            showMapDetails();
            saveDraft();
        });
        page('secret-look-choice').addEventListener('change', event => change(() => { mapState.secretLook = event.target.value; }));
        page('start-angle-choice').addEventListener('change', event => change(() => { mapState.startAngle = Number(event.target.value); }));
        page('show-reach').addEventListener('change', drawMap);
        page('show-safe-zone').addEventListener('change', drawMap);
        page('zoom-input').addEventListener('input', event => {
            editor.zoom = Number(event.target.value);
            drawMap();
            saveDraft();
        });

        // Typing in the map text: the map follows each key, and the whole bit of typing is one undo step.
        const mapText = page('map-text');
        mapText.addEventListener('focus', () => { editor.typingStartedFrom = snapshot(); });
        mapText.addEventListener('input', () => {
            mapState.rows = rowsFromText(mapText.value);
            mapChanged({everything: true});
        });
        mapText.addEventListener('blur', () => {
            const before = editor.typingStartedFrom;
            editor.typingStartedFrom = null;
            if (before && JSON.stringify(before.rows) !== JSON.stringify(mapState.rows)) remember(before);
            mapChanged({everything: true});
        });

        document.addEventListener('keydown', event => {
            const typingInAField = event.target.closest('input, textarea, select');
            const commandKey = event.ctrlKey || event.metaKey;
            if (commandKey && !typingInAField && event.key.toLowerCase() === 'z') {
                event.preventDefault();
                if (event.shiftKey) redo(); else undo();
            } else if (commandKey && !typingInAField && event.key.toLowerCase() === 'y') {
                event.preventDefault();
                redo();
            } else if (!commandKey && !event.altKey && !typingInAField && event.key.length === 1) {
                const letter = event.key.toUpperCase();
                if (PALETTE_LETTERS.includes(letter)) {
                    event.preventDefault();
                    chooseLetter(letter);
                }
            }
        });
    }

    function openFile(file) {
        const reader = new FileReader();
        reader.onload = () => {
            const rows = rowsFromText(String(reader.result));
            if (!rows.length) return showToast(`${file.name} is empty.`);
            const fileName = file.name.replace(/\.txt$/i, '');
            // A file named like a game map ("level 2 map B") gets that map's picture settings.
            const gameMapNumber = data.maps.findIndex(gameMap => gameMap.fileName === fileName);
            const gameMap = data.maps[gameMapNumber];
            openMap({rows, fileName, gameMapNumber: -1,
                     secretLook: gameMap ? gameMap.secretLook : mapState.secretLook,
                     startAngle: gameMap ? gameMap.angle : mapState.startAngle});
            showToast(`Opened ${file.name}. Undo brings back the map you had.`);
        };
        reader.readAsText(file);
    }

    // ---------------------------------------------------------------------------------------------
    // START: the draft from last time, or the first map of the game
    // ---------------------------------------------------------------------------------------------
    buildPalette();
    buildChoices();
    connectControls();
    if (!loadDraft()) {
        const first = data.maps[0];
        Object.assign(mapState, {rows: first.rows.slice(), originalRows: first.rows.slice(), fileName: first.fileName,
                                 gameMapNumber: 0, secretLook: first.secretLook, startAngle: first.angle});
    }
    page('zoom-input').value = String(editor.zoom);
    chooseLetter(editor.letter);
    chooseTool('paint');
    mapChanged({everything: true});
    // Web fonts can arrive after the first drawing; draw again so the letters use them.
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { drawMap(); });
})();
