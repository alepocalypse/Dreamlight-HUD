# Glossary

**Villager**:
Any befriendable character in the game, such as Rapunzel or Moana, whether or not the player has unlocked them yet. A Villager can have a Profession.

**Companion**:
A collectible animal or creature that follows the player and gathers bonus resources, as the game itself calls it. Unlocked mainly by feeding Critters. Not a Villager.
_Avoid_: pet, friend

**Job**:
The kind of bonus resource a Companion gathers (Digging, Fishing, Foraging, Gardening, Mining, Time-bending, Flower pick-up, Wood pick-up, Snippet catching), set by its species.
_Avoid_: profession, role

**Critter**:
A small wild animal in the valley that the player feeds, with several daily feedings, to unlock it as a Companion.

**Companion level**:
A Companion's own friendship level, 1 to 5, earned while it is equipped. Separate from a Villager's Friendship level.

**Friendship level**:
How far a Villager's friendship with the player has progressed, from 0 up to a maximum. This is the "level" the HUD tracks.

**Max level**:
The highest Friendship level a Villager can reach. A Villager at Max level needs no further leveling.

**Profession**:
The gathering role a Villager is assigned (digging, fishing, foraging, gardening, mining, time-bending). Companions have a Job instead.
_Avoid_: role

**Bonus chance**:
The chance of a bonus resource when hanging out with a Villager whose Profession matches the activity: a base (20% Gardening, 25% others) plus 3.5% per Friendship level of the Villager hung out with plus 1% per level of each other Villager with that Profession. Not capped at 100%. The HUD assumes the highest-level Villager is the one hung out with. Not a Companion's Job.

**Daily talk**:
The once-per-day conversation with a Villager that earns friendship.

**Favorite gifts**:
The three items a Villager currently prefers; giving each earns friendship.

**Available**:
A Villager the player has unlocked, whether already living in the valley or still in a realm.
_Avoid_: unlocked

**Unavailable**:
A Villager the player has not yet unlocked through progression.
_Avoid_: locked, secret

**To-do**:
An Available Villager below Max level with today's Daily talk or any Favorite gift still outstanding. A Villager with both done is not shown.

**Chest**:
A storage chest the player has placed in the valley. The backpack and the separate 48-slot storage are not Chests, nor is other furniture that holds items (displays, pet beds, kitchen stations).

**Backpack**:
The player's carried inventory (`ContainerInventories` container ID 0). Not a Chest, and not the separate 48-slot storage (container ID 1).

**Gather For Chests**:
The card listing the raw materials still short for crafting 5 Large Chests (25 Dark Wood and 5 Gold Ingot each). Absent once 5 can be crafted from everything the player holds.

**Moana's Boat**:
The stall at Dazzle Beach (and one per other Village once placed) that fills with free Fish over time, one fish per regen interval up to its Fish spaces, both set by its upgrade level. The save keeps when the player last emptied it, not the fish on board.
_Avoid_: fishing boat, fish stall

**Pick Fruit**:
The card listing each fruit the player holds fewer than 25 of that is on a tree right now, with the zones the trees stand in and how many trees. A fruit tree is wherever the player placed it, so the zones come from the save, not the wiki.

**Pick Up Fish**:
The card listing each zone (Valley, Eternity Isle) whose Moana's Boat is full, with the fish waiting there. Absent while no boat is full.

**Duty**:
One task from a Duty list, with a progress count toward a target ("Catch 5 Fish", 2/5). Open until the count reaches the target; it then pays its Reward.
_Avoid_: task, quest

**Duty list**:
Where a Duty comes from: a Star Path, the Dreamlight Duties, the Mist Duties or a seasonal Event. The player chooses which Duty lists the HUD follows.
_Avoid_: path, duty tree

**Star Path**:
A time-limited event with its own token currency and its own Duties, some fixed for the whole event and some Routine duties.

**Routine duty**:
A Star Path Duty that belongs to one week of the Star Path; three new ones arrive each week, as the game names them.
_Avoid_: weekly duty

**Event**:
A seasonal, time-limited Duty list the game runs beside the Star Paths, such as the Trick-or-Treat Event. Its Duties count toward milestones that each pay an item; the save keeps them as achievements, and the game learns the Event's dates from its servers, so the HUD keeps each Event's window by hand (ADR-0002).
_Avoid_: seasonal event, Tle, live event

**Dreamlight Duties**:
The rotating Duty list of the Valley, paying Dreamlight.

**Mist Duties**:
The rotating Duty list of Eternity Isle, paying Mist.

**Reward**:
What a Duty pays once complete, in its Duty list's currency (Star Path tokens, Dreamlight or Mist), or the item an Event milestone pays.

**Action**:
One thing to do in the game that advances one or more open Duties at once, such as catching a fish at Dazzle Beach when both "Catch any fish" and "Catch fish at Dazzle Beach" are open. The unit the task list and Duty mode show. An Action lasts only while every Duty it advances is open: once one finishes, the rest stand on their own again.
_Avoid_: group, combo

**Size**:
How many open Duties one Action advances: Single (1), Double (2), Triple (3) or Quad (4 or more).

**Duty mode**:
A narrow view of the HUD that shows only the Actions for the Duty lists the player follows, ranked by Reward.
