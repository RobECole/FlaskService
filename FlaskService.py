from flask import Flask, jsonify
import psycopg2
import riotwatcher
app = Flask(__name__)

conn_string = "host='localhost' dbname='LEAGUE_CIRCUIT' user='postgres' password='testdb'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
key = '1dbf97cc-5028-4196-a05c-6645adc80bef'
w = riotwatcher.RiotWatcher(key)


@app.route('/api/update/<name>', methods=['GET'])
def update(name):

    summonerdata = w.get_summoner(name)
    id = summonerdata['id']
    match_history = w.get_match_history(id)
    if 'matches' in match_history:
        matches = match_history['matches']
        matches.reverse()
        match_id = matches[0]['matchId']


@app.route('/api/lastGame/<int:summonerid>')
def lastgame(summonerid):
    cursor.execute("""SELECT P.summoner_name,C.name, S.kills
    FROM "league"."player" AS P
    LEFT JOIN "league"."match_stats" AS S
    ON P.Recent_games_id=S.Match_id AND P.summoner_id = S.summoner_id
    LEFT JOIN "league"."champname" AS C
    ON S.champion_id = C.id
    WHERE P.summoner_id = {0}
    ;""", summonerid)
    data = [
        {'sumname': summoner_name,
         'championname': name,
         'kills': kills}
        for (summoner_name, name, kills) in cursor.fetchall()]
    print data
    return jsonify({'data': data})


@app.route('/api/usedFree')
def usedfree():
    cursor.execute("""SELECT P.summoner_name
    FROM "league"."player" AS P, "league"."match" AS M, "league"."champname" AS C
    WHERE P.game_id = M.match_id AND M.champion_id = ANY (SELECT champ_id
    FROM "league"."champion"
    WHERE free_to_play='true')
    GROUP BY P.summoner_name
    ;""")
    data = [{'sumname': summoner_name} for (summoner_name,) in cursor.fetchall()]
    print data
    return jsonify({'data': data})


@app.route('/api/charkills')
def charkills():
    cursor.execute("""SELECT P.Summoner_name,C.name, S.kills
    FROM "league"."player" AS P, "league"."match_stats" AS S, "league"."champname" AS C, "league"."match" AS M
    WHERE P.game_id = M.match_id AND P.summoner_id = M.summoner_id AND M.participant_id = S.participant_id AND C.id = S.champion_id AND S.kills > (
     SELECT AVG(kills)
     from "league"."match_stats")
    GROUP BY P.summoner_name,C.name, S.kills ORDER BY P.summoner_name
    ;""")
    data = [{'sumname': summoner_name,
             'champname': name,
             'kills': kills}
            for (summoner_name, name, kills) in cursor.fetchall()]
    print data
    return jsonify({'data': data})


@app.route('/api/champdata')
def champdata():
    cursor.execute("""SELECT name, ranked_play_enabled,bot_enabled,free_to_play
    FROM "league"."champname" AS N
    FULL JOIN "league"."champion" AS C
    ON N.id = C.champ_id
    ;""")
    data = [{'name': name,
            'ranked_paly_enabled': ranked_play_enabled,
            'bot_enabled': bot_enabled,
            'free_to_play': free_to_play}
            for (name, ranked_play_enabled, bot_enabled, free_to_play) in cursor.fetchall()]


@app.route('/api/freeChamps')
def freechamps():
    cursor.execute("""SELECT CN.Name
    FROM LEAGUE2.CHAMPION AS C
    RIGHT JOIN LEAGUE2.CHAMPNAME AS CN ON CN.ID = C.Champ_id
    WHERE Free_to_play = 'true'""")
    data = [{'name': name} for (name,) in cursor.fetchall()]
    print data
    return jsonify({'data': data})





if __name__ == '__main__':
    app.run(port=5001, debug=True)
