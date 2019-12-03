# fantasy-fencing
like fantasy football but different

## Running/building

Modules to install: `pydantic`, `selenium`, `uvicorn`, `fastapi`, `beautifulsoup4`, `requests`

Run: `uvicorn main:app --reload`

## Ideas for data

Left/right handed

Grip (pistol/french)

## Ideas for UI

- Table list: data on all fencers, broad, sort by weapon, gender, age, ...
- User Profile -> Personal Stats (against specific oponents)
- Coaches view -> data on many fencers (locked unless you buy(?))

## Structure

Each {tournament}.db file has two tables in it: the fencers who fenced in that tournament, and the matches that were played. Each fencer contains the following statistics from their pool:

- `name`: the name of the fencer
- `victories`: the number of victories in the pool
- `victories_over_matches`: victories divided by total matches
- `touches_scored`, `touches_received`, `indicator`: indicator = touches_scored - touches_received
- `match_scores`: the scores of the individual matches, comma-separated (e.g. "D2,V5,D1,D4...")
- `match_against`: the names of the fencers they fenced against, comma-separated

Note that if the tournament contained multiple pools, the statistics for each pool are separated by hyphens. Thus, an indicator value of `+13--11` means that the fencer had an indicator of `+13` day 1, and `-11` day 2.

The matches (`games`) database contains the list of games. Each game contains the players (`p1` and `p2`) *as they were stored in the tableau*, the score `score` with winner first, the round `round` (e.g. 128, 64, 32...), and the winner `winner` of the match. **NOTE: game.p1 is not necessarily the winner.**

The aggregated database will attempt to pull all of the fencers together. This means that the ids in the aggregated database are different than the ids in the individual tournament databases.

The aggregated database will store fencers in the following format: 

- `id`, `name`, `birthdate`, `club`, `country`: the values from the csv database
- `ratings`: comma-joined ratings in saber, epee, and foil (note that for `sqlite3-unpacking` purposes ratings is between club and country)
- `tournaments`, `stats`: `::`-separated list of tournaments and the statistics for those tournaments (stats are `'.'` joined
- `matches`: the matches played at a given tournament. games in a single tournament are separated by `,`, and tournaments are separated by `::`. There is no distinction for day 1 or day 2. The `match` format is: {against}/{score}/{1 if winner else 0}

