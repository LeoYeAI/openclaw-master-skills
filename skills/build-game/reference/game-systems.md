# Complex Game Systems Reference

Patterns for RPGs, Pokemon-likes, adventure games, and other complex game types. All implemented in a single HTML file with Three.js.

## Multi-Mode Game Architecture

Complex games have multiple modes (overworld, battle, menu, dialogue). Use a mode manager:

```javascript
const MODES = { TITLE: 'title', OVERWORLD: 'overworld', BATTLE: 'battle', MENU: 'menu', DIALOGUE: 'dialogue', GAMEOVER: 'gameover' };

const gameMode = {
    current: MODES.TITLE,
    previous: null,
    transition: null, // { from, to, progress, duration }

    switch(newMode, transitionDuration = 0.5) {
        this.previous = this.current;
        this.transition = { from: this.current, to: newMode, progress: 0, duration: transitionDuration };
        // Hide old UI, prepare new UI
        document.querySelectorAll('.mode-ui').forEach(el => el.style.display = 'none');
        const newUI = document.getElementById(`ui-${newMode}`);
        if (newUI) newUI.style.display = 'block';
    },

    update(delta) {
        if (this.transition) {
            this.transition.progress += delta / this.transition.duration;
            if (this.transition.progress >= 1) {
                this.current = this.transition.to;
                this.transition = null;
            }
        }
    }
};

// In main loop:
function update(delta) {
    gameMode.update(delta);
    switch (gameMode.current) {
        case MODES.OVERWORLD: updateOverworld(delta); break;
        case MODES.BATTLE: updateBattle(delta); break;
        case MODES.DIALOGUE: updateDialogue(delta); break;
        // ...
    }
}
```

## Turn-Based Battle System (Pokemon-style)

```javascript
// ---- Creature / Move Definitions ----
const TYPES = { FIRE: 'fire', WATER: 'water', EARTH: 'earth', AIR: 'air', ELECTRIC: 'electric', ICE: 'ice', DARK: 'dark', LIGHT: 'light' };

// Type effectiveness chart: attacker type → defender type → multiplier
const TYPE_CHART = {
    fire:     { fire: 0.5, water: 0.5, earth: 2,   air: 1,   ice: 2,   electric: 1, dark: 1, light: 1 },
    water:    { fire: 2,   water: 0.5, earth: 1,   air: 1,   ice: 0.5, electric: 0.5, dark: 1, light: 1 },
    earth:    { fire: 1,   water: 2,   earth: 0.5, air: 0.5, ice: 1,   electric: 2, dark: 1, light: 1 },
    air:      { fire: 1,   water: 1,   earth: 2,   air: 0.5, ice: 1,   electric: 0.5, dark: 1, light: 1 },
    ice:      { fire: 0.5, water: 1,   earth: 1,   air: 2,   ice: 0.5, electric: 1, dark: 1, light: 2 },
    electric: { fire: 1,   water: 2,   earth: 0.5, air: 2,   ice: 1,   electric: 0.5, dark: 1, light: 1 },
    dark:     { fire: 1,   water: 1,   earth: 1,   air: 1,   ice: 1,   electric: 1, dark: 0.5, light: 2 },
    light:    { fire: 1,   water: 1,   earth: 1,   air: 1,   ice: 1,   electric: 1, dark: 2, light: 0.5 },
};

// Creature species database
const SPECIES = {
    flamefox: {
        name: 'Flamefox', type: TYPES.FIRE,
        baseStats: { hp: 45, atk: 60, def: 40, spd: 70 },
        moves: ['ember', 'tackle', 'fireball', 'flame_dash'],
        evolvesTo: 'infernowolf', evolveLevel: 16,
        createModel: () => { /* procedural Three.js model */ },
        color: 0xff6b35,
    },
    // ... more species
};

// Move database
const MOVES = {
    tackle:     { name: 'Tackle', type: 'normal', power: 40, accuracy: 100, category: 'physical', effect: null },
    ember:      { name: 'Ember', type: TYPES.FIRE, power: 40, accuracy: 100, category: 'special', effect: { type: 'burn', chance: 10 } },
    fireball:   { name: 'Fireball', type: TYPES.FIRE, power: 70, accuracy: 90, category: 'special', effect: null },
    flame_dash: { name: 'Flame Dash', type: TYPES.FIRE, power: 55, accuracy: 95, category: 'physical', effect: { type: 'priority', value: 1 } },
    // ... more moves
};

// ---- Creature Instance ----
class Creature {
    constructor(speciesId, level = 5, nickname = null) {
        this.species = SPECIES[speciesId];
        this.speciesId = speciesId;
        this.nickname = nickname || this.species.name;
        this.level = level;
        this.xp = 0;
        this.xpToNext = Math.floor(level * level * 1.5 + 10);

        // Calculate stats from base + level
        const s = this.species.baseStats;
        this.maxHp = Math.floor(s.hp + level * 2.5);
        this.hp = this.maxHp;
        this.atk = Math.floor(s.atk + level * 1.5);
        this.def = Math.floor(s.def + level * 1.5);
        this.spd = Math.floor(s.spd + level * 1.5);

        this.moves = this.species.moves.slice(0, Math.min(4, 1 + Math.floor(level / 5)));
        this.statusEffects = []; // { type, turnsLeft }
        this.mesh = null; // created when entering battle
    }

    gainXP(amount) {
        this.xp += amount;
        while (this.xp >= this.xpToNext) {
            this.xp -= this.xpToNext;
            this.levelUp();
        }
    }

    levelUp() {
        this.level++;
        const s = this.species.baseStats;
        this.maxHp = Math.floor(s.hp + this.level * 2.5);
        this.hp = Math.min(this.hp + 5, this.maxHp);
        this.atk = Math.floor(s.atk + this.level * 1.5);
        this.def = Math.floor(s.def + this.level * 1.5);
        this.spd = Math.floor(s.spd + this.level * 1.5);
        this.xpToNext = Math.floor(this.level * this.level * 1.5 + 10);
        // Learn new moves
        const available = this.species.moves;
        const learnIdx = 1 + Math.floor(this.level / 5);
        if (learnIdx <= available.length && this.moves.length < 4) {
            this.moves.push(available[learnIdx - 1]);
        }
        // Evolution check
        if (this.species.evolvesTo && this.level >= this.species.evolveLevel) {
            this.evolve();
        }
    }

    evolve() {
        const newSpecies = SPECIES[this.species.evolvesTo];
        if (!newSpecies) return;
        this.speciesId = this.species.evolvesTo;
        this.species = newSpecies;
        // Recalculate stats with new base
        const s = this.species.baseStats;
        const hpRatio = this.hp / this.maxHp;
        this.maxHp = Math.floor(s.hp + this.level * 2.5);
        this.hp = Math.floor(this.maxHp * hpRatio);
        this.atk = Math.floor(s.atk + this.level * 1.5);
        this.def = Math.floor(s.def + this.level * 1.5);
        this.spd = Math.floor(s.spd + this.level * 1.5);
        // Trigger evolution animation in battle
        return true; // signal to show evolution
    }
}

// ---- Battle Engine ----
class BattleSystem {
    constructor() {
        this.playerCreature = null;
        this.enemyCreature = null;
        this.phase = 'select'; // 'select' | 'animate' | 'result' | 'capture' | 'end'
        this.turnQueue = [];
        this.animationTimer = 0;
        this.battleLog = [];
        this.isWild = true;
        this.escaped = false;
    }

    start(playerCreature, enemyCreature, isWild = true) {
        this.playerCreature = playerCreature;
        this.enemyCreature = enemyCreature;
        this.isWild = isWild;
        this.phase = 'select';
        this.battleLog = [`A wild ${enemyCreature.nickname} appeared!`];
        this.escaped = false;
        gameMode.switch(MODES.BATTLE);
        // Create 3D battle scene (opponent creatures facing each other)
    }

    selectMove(moveId) {
        const playerMove = MOVES[moveId];
        const enemyMove = MOVES[this.enemyCreature.moves[Math.floor(Math.random() * this.enemyCreature.moves.length)]];

        // Speed determines turn order
        this.turnQueue = [];
        const playerPriority = playerMove.effect?.type === 'priority' ? playerMove.effect.value : 0;
        const enemyPriority = enemyMove.effect?.type === 'priority' ? enemyMove.effect.value : 0;

        if (playerPriority > enemyPriority || (playerPriority === enemyPriority && this.playerCreature.spd >= this.enemyCreature.spd)) {
            this.turnQueue.push({ attacker: 'player', move: playerMove });
            this.turnQueue.push({ attacker: 'enemy', move: enemyMove });
        } else {
            this.turnQueue.push({ attacker: 'enemy', move: enemyMove });
            this.turnQueue.push({ attacker: 'player', move: playerMove });
        }
        this.phase = 'animate';
        this.processNextTurn();
    }

    processNextTurn() {
        if (this.turnQueue.length === 0) {
            this.phase = this.playerCreature.hp <= 0 || this.enemyCreature.hp <= 0 ? 'end' : 'select';
            return;
        }
        const turn = this.turnQueue.shift();
        const attacker = turn.attacker === 'player' ? this.playerCreature : this.enemyCreature;
        const defender = turn.attacker === 'player' ? this.enemyCreature : this.playerCreature;

        if (attacker.hp <= 0) { this.processNextTurn(); return; }

        // Damage calculation
        const move = turn.move;
        const effectiveness = (move.type !== 'normal' && TYPE_CHART[move.type])
            ? (TYPE_CHART[move.type][defender.species.type] || 1) : 1;
        const atkStat = move.category === 'physical' ? attacker.atk : attacker.atk * 1.1;
        const defStat = move.category === 'physical' ? defender.def : defender.def * 0.9;
        const baseDmg = ((2 * attacker.level / 5 + 2) * move.power * atkStat / defStat / 50 + 2);
        const variance = 0.85 + Math.random() * 0.15;
        const accuracyCheck = Math.random() * 100 < move.accuracy;
        const damage = accuracyCheck ? Math.floor(baseDmg * effectiveness * variance) : 0;

        defender.hp = Math.max(0, defender.hp - damage);

        // Battle log
        if (!accuracyCheck) {
            this.battleLog.push(`${attacker.nickname} used ${move.name} but missed!`);
        } else {
            this.battleLog.push(`${attacker.nickname} used ${move.name}!`);
            if (effectiveness > 1) this.battleLog.push("It's super effective!");
            if (effectiveness < 1) this.battleLog.push("It's not very effective...");
        }

        // Apply status effects
        if (accuracyCheck && move.effect && move.effect.type !== 'priority') {
            if (Math.random() * 100 < move.effect.chance) {
                defender.statusEffects.push({ type: move.effect.type, turnsLeft: 3 });
                this.battleLog.push(`${defender.nickname} was ${move.effect.type}ed!`);
            }
        }

        // Animate, then process next turn after delay
        this.animationTimer = 1.2;
    }

    attemptCapture(captureStrength = 1.0) {
        if (!this.isWild) { this.battleLog.push("Can't capture a trainer's creature!"); return false; }
        const hpRatio = this.enemyCreature.hp / this.enemyCreature.maxHp;
        const catchRate = (1 - hpRatio * 0.6) * captureStrength * (0.3 + Math.random() * 0.7);
        this.battleLog.push(`Threw a capture orb...`);
        if (catchRate > 0.5) {
            this.battleLog.push(`Caught ${this.enemyCreature.nickname}!`);
            // Add to player's collection
            return true;
        } else {
            this.battleLog.push(`It broke free!`);
            // Enemy gets a free turn
            return false;
        }
    }

    attemptRun() {
        const chance = this.playerCreature.spd / (this.playerCreature.spd + this.enemyCreature.spd) + 0.3;
        if (Math.random() < chance) {
            this.escaped = true;
            this.battleLog.push('Got away safely!');
            this.phase = 'end';
            return true;
        }
        this.battleLog.push("Can't escape!");
        return false;
    }

    update(delta) {
        if (this.animationTimer > 0) {
            this.animationTimer -= delta;
            if (this.animationTimer <= 0) this.processNextTurn();
        }
    }
}
```

### Battle UI (HTML overlay)

```html
<div id="ui-battle" class="mode-ui" style="display:none">
    <!-- Enemy creature info -->
    <div style="position:absolute;top:20px;left:30px;color:#fff;">
        <div id="enemy-name" style="font-size:18px;font-weight:bold;"></div>
        <div id="enemy-level" style="font-size:14px;color:#aaa;"></div>
        <div style="width:200px;height:10px;background:#333;border-radius:5px;margin-top:5px;">
            <div id="enemy-hp-bar" style="height:100%;background:#4ade80;border-radius:5px;transition:width 0.3s;"></div>
        </div>
    </div>
    <!-- Player creature info -->
    <div style="position:absolute;bottom:160px;right:30px;color:#fff;text-align:right;">
        <div id="player-name" style="font-size:18px;font-weight:bold;"></div>
        <div id="player-level" style="font-size:14px;color:#aaa;"></div>
        <div style="width:200px;height:10px;background:#333;border-radius:5px;margin-top:5px;">
            <div id="player-hp-bar" style="height:100%;background:#4ade80;border-radius:5px;transition:width 0.3s;"></div>
        </div>
        <div id="player-hp-text" style="font-size:12px;margin-top:2px;"></div>
    </div>
    <!-- Battle menu -->
    <div id="battle-menu" style="position:absolute;bottom:20px;left:50%;transform:translateX(-50%);display:grid;grid-template-columns:1fr 1fr;gap:10px;pointer-events:auto;">
        <!-- Dynamically populated with move buttons, run, capture, items -->
    </div>
    <!-- Battle log -->
    <div id="battle-log" style="position:absolute;bottom:100px;left:30px;color:#fff;font-size:14px;max-width:400px;"></div>
</div>
```

## Creature Capture & Collection System

```javascript
class CreatureCollection {
    constructor(maxParty = 6, maxStorage = 30) {
        this.party = []; // Active creatures (up to maxParty)
        this.storage = []; // PC storage
        this.maxParty = maxParty;
        this.maxStorage = maxStorage;
        this.pokedex = new Set(); // Seen/caught species
    }

    addCreature(creature) {
        this.pokedex.add(creature.speciesId);
        if (this.party.length < this.maxParty) {
            this.party.push(creature);
            return 'party';
        } else if (this.storage.length < this.maxStorage) {
            this.storage.push(creature);
            return 'storage';
        }
        return 'full';
    }

    swapPartyMember(partyIdx, storageIdx) {
        const temp = this.party[partyIdx];
        this.party[partyIdx] = this.storage[storageIdx];
        this.storage[storageIdx] = temp;
    }

    healAll() {
        for (const c of this.party) {
            c.hp = c.maxHp;
            c.statusEffects = [];
        }
    }

    getFirstAlive() {
        return this.party.find(c => c.hp > 0);
    }
}

// Wild encounter system
function checkWildEncounter(playerPos, biome) {
    const encounterRate = { forest: 0.03, grass: 0.05, cave: 0.08, water: 0.04, snow: 0.03 };
    if (Math.random() < (encounterRate[biome] || 0.03)) {
        const possibleSpecies = Object.keys(SPECIES).filter(s => SPECIES[s].biomes?.includes(biome));
        if (possibleSpecies.length === 0) return null;
        const speciesId = possibleSpecies[Math.floor(Math.random() * possibleSpecies.length)];
        const level = Math.max(1, Math.floor(state.highestLevel * (0.7 + Math.random() * 0.6)));
        return new Creature(speciesId, level);
    }
    return null;
}
```

## Inventory & Item System

```javascript
const ITEMS = {
    potion:       { name: 'Potion', type: 'consumable', effect: { heal: 30 }, description: 'Restores 30 HP', stackable: true, maxStack: 20 },
    capture_orb:  { name: 'Capture Orb', type: 'capture', effect: { captureBonus: 1.0 }, description: 'Catches wild creatures', stackable: true, maxStack: 30 },
    super_orb:    { name: 'Super Orb', type: 'capture', effect: { captureBonus: 1.5 }, description: 'Better catch rate', stackable: true, maxStack: 15 },
    iron_sword:   { name: 'Iron Sword', type: 'equipment', slot: 'weapon', stats: { atk: 10 }, description: '+10 Attack' },
    leather_armor:{ name: 'Leather Armor', type: 'equipment', slot: 'armor', stats: { def: 8 }, description: '+8 Defense' },
    speed_berry:  { name: 'Speed Berry', type: 'consumable', effect: { buff: 'spd', amount: 5, turns: 3 }, description: '+5 Speed for 3 turns', stackable: true },
    // Key items
    old_key:      { name: 'Old Key', type: 'key', description: 'Opens the ancient gate', unique: true },
};

class Inventory {
    constructor(maxSlots = 20) {
        this.slots = []; // { itemId, quantity }
        this.maxSlots = maxSlots;
        this.equipment = { weapon: null, armor: null, accessory: null };
        this.gold = 0;
    }

    add(itemId, quantity = 1) {
        const itemDef = ITEMS[itemId];
        if (itemDef.stackable) {
            const existing = this.slots.find(s => s.itemId === itemId);
            if (existing) {
                existing.quantity = Math.min(existing.quantity + quantity, itemDef.maxStack || 99);
                return true;
            }
        }
        if (this.slots.length >= this.maxSlots) return false;
        this.slots.push({ itemId, quantity });
        return true;
    }

    remove(itemId, quantity = 1) {
        const idx = this.slots.findIndex(s => s.itemId === itemId);
        if (idx < 0) return false;
        this.slots[idx].quantity -= quantity;
        if (this.slots[idx].quantity <= 0) this.slots.splice(idx, 1);
        return true;
    }

    has(itemId, quantity = 1) {
        const slot = this.slots.find(s => s.itemId === itemId);
        return slot && slot.quantity >= quantity;
    }

    equip(itemId) {
        const itemDef = ITEMS[itemId];
        if (itemDef.type !== 'equipment') return false;
        const prev = this.equipment[itemDef.slot];
        if (prev) this.add(prev);
        this.equipment[itemDef.slot] = itemId;
        this.remove(itemId);
        return true;
    }

    useItem(itemId, target) {
        const itemDef = ITEMS[itemId];
        if (!itemDef || !this.has(itemId)) return false;
        if (itemDef.effect?.heal && target.hp !== undefined) {
            target.hp = Math.min(target.maxHp, target.hp + itemDef.effect.heal);
        }
        if (itemDef.type === 'consumable') this.remove(itemId);
        return true;
    }
}
```

### Inventory UI

```html
<div id="ui-inventory" style="display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
    width:500px;background:rgba(0,0,0,0.9);border:2px solid #555;border-radius:12px;padding:20px;z-index:30;pointer-events:auto;">
    <h2 style="color:#fff;margin-bottom:15px;">Inventory</h2>
    <div id="inv-grid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;"></div>
    <div id="inv-detail" style="color:#aaa;margin-top:15px;min-height:40px;"></div>
    <div style="color:#ffd700;margin-top:10px;" id="inv-gold"></div>
</div>
```

## Dialogue & NPC Interaction System

```javascript
// Dialogue tree format
const DIALOGUES = {
    elder_intro: {
        speaker: 'Village Elder',
        lines: [
            { text: "Welcome, young one. The mountain spirits are restless.", next: 'elder_choice' },
        ]
    },
    elder_choice: {
        speaker: 'Village Elder',
        lines: [
            {
                text: "Will you help us calm them?",
                choices: [
                    { text: "Of course!", next: 'elder_accept', action: () => { questSystem.start('calm_spirits'); } },
                    { text: "Tell me more first.", next: 'elder_explain' },
                    { text: "Not right now.", next: null }, // null = end dialogue
                ]
            }
        ]
    },
    elder_explain: {
        speaker: 'Village Elder',
        lines: [
            { text: "Long ago, the spirits guarded this mountain...", next: 'elder_explain2' },
            // ...
        ]
    },
};

class DialogueSystem {
    constructor() {
        this.active = false;
        this.currentDialogue = null;
        this.currentLine = 0;
        this.displayedText = '';
        this.textTimer = 0;
        this.textSpeed = 0.03; // seconds per character
        this.fullText = '';
        this.waitingForInput = false;
        this.choices = null;
    }

    start(dialogueId) {
        this.active = true;
        this.currentDialogue = DIALOGUES[dialogueId];
        this.currentLine = 0;
        this.showLine();
        gameMode.switch(MODES.DIALOGUE);
    }

    showLine() {
        if (!this.currentDialogue) { this.end(); return; }
        const line = this.currentDialogue.lines[this.currentLine];
        if (!line) { this.end(); return; }
        this.fullText = line.text;
        this.displayedText = '';
        this.textTimer = 0;
        this.waitingForInput = false;
        this.choices = line.choices || null;
        // Update speaker name in UI
    }

    update(delta) {
        if (!this.active) return;
        if (this.displayedText.length < this.fullText.length) {
            this.textTimer += delta;
            while (this.textTimer >= this.textSpeed && this.displayedText.length < this.fullText.length) {
                this.displayedText += this.fullText[this.displayedText.length];
                this.textTimer -= this.textSpeed;
            }
        } else {
            this.waitingForInput = true;
        }
        // Update dialogue box DOM
    }

    advance(choiceIndex = null) {
        // Skip text animation
        if (this.displayedText.length < this.fullText.length) {
            this.displayedText = this.fullText;
            this.waitingForInput = true;
            return;
        }
        const line = this.currentDialogue.lines[this.currentLine];
        if (this.choices && choiceIndex !== null) {
            const choice = this.choices[choiceIndex];
            if (choice.action) choice.action();
            if (choice.next) {
                this.currentDialogue = DIALOGUES[choice.next];
                this.currentLine = 0;
                this.showLine();
            } else {
                this.end();
            }
        } else if (line.next) {
            this.currentDialogue = DIALOGUES[line.next];
            this.currentLine = 0;
            this.showLine();
        } else {
            this.currentLine++;
            if (this.currentLine < this.currentDialogue.lines.length) {
                this.showLine();
            } else {
                this.end();
            }
        }
    }

    end() {
        this.active = false;
        this.currentDialogue = null;
        gameMode.switch(MODES.OVERWORLD);
    }
}
```

### Dialogue UI

```html
<div id="ui-dialogue" class="mode-ui" style="display:none;position:fixed;bottom:20px;left:50%;transform:translateX(-50%);
    width:700px;background:rgba(0,0,0,0.9);border:2px solid #666;border-radius:12px;padding:20px;z-index:25;pointer-events:auto;">
    <div id="dlg-speaker" style="color:#ffd700;font-weight:bold;font-size:16px;margin-bottom:8px;"></div>
    <div id="dlg-text" style="color:#fff;font-size:15px;line-height:1.6;min-height:50px;"></div>
    <div id="dlg-choices" style="margin-top:12px;display:flex;flex-direction:column;gap:8px;"></div>
    <div id="dlg-continue" style="color:#888;font-size:12px;text-align:right;margin-top:8px;">Press E or Click to continue</div>
</div>
```

## Quest / Mission System

```javascript
const QUESTS = {
    calm_spirits: {
        name: 'Calm the Mountain Spirits',
        description: 'Defeat 5 enraged spirits on the mountain peak.',
        objectives: [
            { type: 'defeat', target: 'enraged_spirit', count: 5, progress: 0 },
        ],
        rewards: { xp: 200, gold: 100, items: [{ id: 'super_orb', qty: 3 }] },
        followUp: 'elder_thanks',
    },
    collect_herbs: {
        name: 'Gather Healing Herbs',
        description: 'Collect 3 moonflowers from the forest.',
        objectives: [
            { type: 'collect', target: 'moonflower', count: 3, progress: 0 },
        ],
        rewards: { xp: 50, gold: 30, items: [{ id: 'potion', qty: 5 }] },
    },
};

class QuestSystem {
    constructor() {
        this.active = [];   // Quest IDs currently in progress
        this.completed = []; // Quest IDs finished
    }

    start(questId) {
        if (this.active.includes(questId) || this.completed.includes(questId)) return;
        this.active.push(questId);
        // Deep copy objectives for tracking
        const quest = QUESTS[questId];
        quest.objectives.forEach(o => o.progress = 0);
    }

    notify(eventType, targetId) {
        // Call this when player defeats enemies, collects items, etc.
        for (const qid of this.active) {
            const quest = QUESTS[qid];
            for (const obj of quest.objectives) {
                if (obj.type === eventType && obj.target === targetId && obj.progress < obj.count) {
                    obj.progress++;
                }
            }
            // Check completion
            if (quest.objectives.every(o => o.progress >= o.count)) {
                this.complete(qid);
            }
        }
    }

    complete(questId) {
        const idx = this.active.indexOf(questId);
        if (idx < 0) return;
        this.active.splice(idx, 1);
        this.completed.push(questId);
        const quest = QUESTS[questId];
        // Grant rewards
        if (quest.rewards.xp) { /* grant XP to party */ }
        if (quest.rewards.gold) state.inventory.gold += quest.rewards.gold;
        if (quest.rewards.items) quest.rewards.items.forEach(i => state.inventory.add(i.id, i.qty));
        // Show completion notification
    }

    isComplete(questId) { return this.completed.includes(questId); }
    isActive(questId) { return this.active.includes(questId); }
}
```

## Save / Load System (localStorage)

```javascript
const SAVE_KEY = 'game_save_v1';

function saveGame() {
    const data = {
        version: 1,
        timestamp: Date.now(),
        player: {
            x: camera.position.x, y: camera.position.y, z: camera.position.z,
            health: state.health,
        },
        party: state.collection.party.map(c => ({
            speciesId: c.speciesId, level: c.level, xp: c.xp,
            hp: c.hp, nickname: c.nickname, moves: c.moves,
        })),
        storage: state.collection.storage.map(c => ({
            speciesId: c.speciesId, level: c.level, xp: c.xp,
            hp: c.hp, nickname: c.nickname, moves: c.moves,
        })),
        inventory: {
            slots: state.inventory.slots,
            equipment: state.inventory.equipment,
            gold: state.inventory.gold,
        },
        quests: {
            active: state.questSystem.active,
            completed: state.questSystem.completed,
        },
        flags: state.flags, // game progression flags
        score: state.score,
        wave: state.wave,
    };
    localStorage.setItem(SAVE_KEY, JSON.stringify(data));
}

function loadGame() {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return false;
    try {
        const data = JSON.parse(raw);
        // Restore player position
        camera.position.set(data.player.x, data.player.y, data.player.z);
        state.health = data.player.health;
        // Restore creatures
        state.collection.party = data.party.map(c => {
            const creature = new Creature(c.speciesId, c.level, c.nickname);
            creature.xp = c.xp; creature.hp = c.hp; creature.moves = c.moves;
            return creature;
        });
        // ... restore inventory, quests, flags
        return true;
    } catch (e) { return false; }
}

function deleteSave() { localStorage.removeItem(SAVE_KEY); }
```

## NPC / Shop System

```javascript
class NPC {
    constructor({ name, position, dialogueId, type = 'talk', shopItems = null, model }) {
        this.name = name;
        this.mesh = model;
        this.mesh.position.copy(position);
        this.dialogueId = dialogueId;
        this.type = type; // 'talk', 'shop', 'healer', 'quest'
        this.shopItems = shopItems; // [{ itemId, price }]
        this.interactionRadius = 2.5;
        scene.add(this.mesh);

        // Floating name tag
        // (use CSS2DRenderer or DOM overlay projected from 3D)
    }

    canInteract(playerPos) {
        return this.mesh.position.distanceTo(playerPos) < this.interactionRadius;
    }

    interact() {
        switch (this.type) {
            case 'talk': dialogueSystem.start(this.dialogueId); break;
            case 'shop': openShop(this.shopItems); break;
            case 'healer': state.collection.healAll(); showNotification('Your creatures are fully healed!'); break;
            case 'quest': dialogueSystem.start(this.dialogueId); break;
        }
    }
}

function openShop(items) {
    // Show shop UI overlay with buy/sell options
    // Player can buy items with gold
    // Player can sell items for half price
}
```

## Weather System

```javascript
class WeatherSystem {
    constructor(scene) {
        this.scene = scene;
        this.current = 'clear'; // clear, rain, snow, fog, storm
        this.particles = null;
        this.timer = 0;
        this.transitionTimer = 0;
    }

    set(type) {
        if (type === this.current) return;
        this.current = type;
        this.transitionTimer = 2; // seconds to transition

        // Clean up old particles
        if (this.particles) { this.scene.remove(this.particles); this.particles = null; }

        switch (type) {
            case 'rain':
                this.particles = this.createRainSystem(3000);
                this.scene.fog = new THREE.FogExp2(0x667788, 0.015);
                break;
            case 'snow':
                this.particles = this.createSnowSystem(2000);
                this.scene.fog = new THREE.FogExp2(0xccddee, 0.012);
                break;
            case 'storm':
                this.particles = this.createRainSystem(5000);
                this.scene.fog = new THREE.FogExp2(0x445566, 0.02);
                break;
            case 'clear':
                this.scene.fog = new THREE.FogExp2(0x88aacc, 0.008);
                break;
        }
        if (this.particles) this.scene.add(this.particles);
    }

    createRainSystem(count) {
        const geo = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        const velocities = new Float32Array(count);
        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 100;
            positions[i * 3 + 1] = Math.random() * 50;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
            velocities[i] = 15 + Math.random() * 10;
        }
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const mat = new THREE.PointsMaterial({ color: 0xaaaacc, size: 0.1, transparent: true, opacity: 0.6 });
        const points = new THREE.Points(geo, mat);
        points.userData = { velocities };
        return points;
    }

    createSnowSystem(count) {
        const geo = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        const drifts = new Float32Array(count * 2); // drift x, drift z
        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 100;
            positions[i * 3 + 1] = Math.random() * 40;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
            drifts[i * 2] = (Math.random() - 0.5) * 2;
            drifts[i * 2 + 1] = (Math.random() - 0.5) * 2;
        }
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const mat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.2, transparent: true, opacity: 0.8 });
        const points = new THREE.Points(geo, mat);
        points.userData = { drifts, fallSpeed: 2 };
        return points;
    }

    update(delta) {
        if (!this.particles) return;
        const pos = this.particles.geometry.attributes.position.array;
        const count = pos.length / 3;

        if (this.current === 'rain' || this.current === 'storm') {
            const vel = this.particles.userData.velocities;
            for (let i = 0; i < count; i++) {
                pos[i * 3 + 1] -= vel[i] * delta;
                if (this.current === 'storm') pos[i * 3] += Math.sin(performance.now() * 0.001 + i) * delta * 3;
                if (pos[i * 3 + 1] < 0) {
                    pos[i * 3 + 1] = 40 + Math.random() * 10;
                    pos[i * 3] = camera.position.x + (Math.random() - 0.5) * 100;
                    pos[i * 3 + 2] = camera.position.z + (Math.random() - 0.5) * 100;
                }
            }
        }
        if (this.current === 'snow') {
            const { drifts, fallSpeed } = this.particles.userData;
            for (let i = 0; i < count; i++) {
                pos[i * 3] += drifts[i * 2] * delta + Math.sin(performance.now() * 0.001 + i) * delta * 0.5;
                pos[i * 3 + 1] -= fallSpeed * delta * (0.5 + Math.random() * 0.5);
                pos[i * 3 + 2] += drifts[i * 2 + 1] * delta;
                if (pos[i * 3 + 1] < 0) {
                    pos[i * 3 + 1] = 35 + Math.random() * 10;
                    pos[i * 3] = camera.position.x + (Math.random() - 0.5) * 80;
                    pos[i * 3 + 2] = camera.position.z + (Math.random() - 0.5) * 80;
                }
            }
        }
        this.particles.geometry.attributes.position.needsUpdate = true;
    }
}
```

## Day / Night Cycle

```javascript
class DayNightCycle {
    constructor(sunLight, scene) {
        this.sun = sunLight;
        this.scene = scene;
        this.timeOfDay = 0.3; // 0 = midnight, 0.25 = sunrise, 0.5 = noon, 0.75 = sunset
        this.daySpeed = 0.01; // full cycle speed (increase for faster days)
        this.colors = {
            dawn:     { sky: 0xffaa77, ambient: 0x776655, sun: 0xffcc88, intensity: 0.8 },
            day:      { sky: 0x87CEEB, ambient: 0x404060, sun: 0xfff4e6, intensity: 1.5 },
            dusk:     { sky: 0xff7744, ambient: 0x664433, sun: 0xff8855, intensity: 0.6 },
            night:    { sky: 0x0a0a2e, ambient: 0x111133, sun: 0x4444aa, intensity: 0.15 },
        };
    }

    update(delta) {
        this.timeOfDay = (this.timeOfDay + this.daySpeed * delta) % 1;
        const angle = this.timeOfDay * Math.PI * 2;
        this.sun.position.set(Math.cos(angle) * 80, Math.sin(angle) * 80, 30);

        // Interpolate colors based on time
        let phase;
        if (this.timeOfDay < 0.2) phase = this.lerpColors(this.colors.night, this.colors.dawn, this.timeOfDay / 0.2);
        else if (this.timeOfDay < 0.3) phase = this.lerpColors(this.colors.dawn, this.colors.day, (this.timeOfDay - 0.2) / 0.1);
        else if (this.timeOfDay < 0.7) phase = this.colors.day;
        else if (this.timeOfDay < 0.8) phase = this.lerpColors(this.colors.day, this.colors.dusk, (this.timeOfDay - 0.7) / 0.1);
        else if (this.timeOfDay < 0.9) phase = this.lerpColors(this.colors.dusk, this.colors.night, (this.timeOfDay - 0.8) / 0.1);
        else phase = this.colors.night;

        this.scene.background = new THREE.Color(phase.sky);
        this.scene.fog.color = new THREE.Color(phase.sky);
        this.sun.color = new THREE.Color(phase.sun);
        this.sun.intensity = phase.intensity;
    }

    lerpColors(a, b, t) {
        return {
            sky: new THREE.Color(a.sky).lerp(new THREE.Color(b.sky), t).getHex(),
            ambient: new THREE.Color(a.ambient).lerp(new THREE.Color(b.ambient), t).getHex(),
            sun: new THREE.Color(a.sun).lerp(new THREE.Color(b.sun), t).getHex(),
            intensity: a.intensity + (b.intensity - a.intensity) * t,
        };
    }

    getTimeString() {
        const hours = Math.floor(this.timeOfDay * 24);
        const minutes = Math.floor((this.timeOfDay * 24 - hours) * 60);
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
    }
}
```

## Region / Zone System (for larger worlds)

```javascript
// Define zones with boundaries and properties
const ZONES = {
    village:    { center: [0, 0], radius: 30, biome: 'grass', music: 'peaceful', encounters: false },
    forest:     { center: [50, 0], radius: 40, biome: 'forest', music: 'adventure', encounters: true },
    snow_peak:  { center: [0, 80], radius: 50, biome: 'snow', music: 'epic', encounters: true },
    cave:       { center: [-40, 40], radius: 20, biome: 'cave', music: 'mysterious', encounters: true },
    lake:       { center: [30, -40], radius: 25, biome: 'water', music: 'calm', encounters: true },
};

function getCurrentZone(playerPos) {
    for (const [id, zone] of Object.entries(ZONES)) {
        const dx = playerPos.x - zone.center[0];
        const dz = playerPos.z - zone.center[1];
        if (Math.sqrt(dx * dx + dz * dz) < zone.radius) return { id, ...zone };
    }
    return { id: 'wilderness', biome: 'grass', music: 'ambient', encounters: true };
}
```

## Minimap

```javascript
function createMinimap(containerId, size = 150) {
    const canvas = document.createElement('canvas');
    canvas.width = size; canvas.height = size;
    canvas.style.cssText = `position:absolute;top:20px;right:20px;border:2px solid rgba(255,255,255,0.3);border-radius:50%;`;
    document.getElementById(containerId).appendChild(canvas);
    const ctx = canvas.getContext('2d');

    return {
        update(playerPos, playerAngle, entities = [], mapRadius = 80) {
            ctx.clearRect(0, 0, size, size);
            // Background
            ctx.fillStyle = 'rgba(0,20,0,0.6)';
            ctx.beginPath(); ctx.arc(size/2, size/2, size/2, 0, Math.PI * 2); ctx.fill();
            // Scale factor
            const scale = (size / 2) / mapRadius;
            // Entities (red dots)
            ctx.fillStyle = '#ff4444';
            for (const e of entities) {
                const dx = (e.x - playerPos.x) * scale;
                const dz = (e.z - playerPos.z) * scale;
                const mx = size / 2 + dx;
                const my = size / 2 + dz;
                if (Math.sqrt(dx*dx + dz*dz) < size/2 - 4) {
                    ctx.beginPath(); ctx.arc(mx, my, 3, 0, Math.PI * 2); ctx.fill();
                }
            }
            // Player (center, white triangle pointing forward)
            ctx.fillStyle = '#fff';
            ctx.save();
            ctx.translate(size / 2, size / 2);
            ctx.rotate(-playerAngle);
            ctx.beginPath(); ctx.moveTo(0, -6); ctx.lineTo(-4, 4); ctx.lineTo(4, 4); ctx.closePath(); ctx.fill();
            ctx.restore();
        }
    };
}
```

## Tips for Complex Games

- **Start simple, then layer systems.** Get movement + one core mechanic working first.
- **Keep data definitions separate from logic.** SPECIES, ITEMS, QUESTS, DIALOGUES should all be plain objects at the top.
- **Mode manager is essential.** Every complex game needs clear state separation between overworld/battle/menu/dialogue.
- **localStorage for persistence.** Save on every significant event (battle won, item acquired, zone change).
- **Performance budget.** Complex games need more aggressive optimization: instanced meshes, object pooling, LOD switching, frustum culling.
- **UI layering.** Use z-index to manage overlapping UI modes. Only one mode-ui should be visible at a time.
- **Sound per mode.** Different background music for overworld vs battle vs menus. Crossfade between them.
