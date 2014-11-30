from flask import Flask, jsonify
import psycopg2
app = Flask(__name__)

conn_string = "host='localhost' dbname='LEAGUE_CIRCUIT' user='postgres' password='testdb'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()


@app.route('/api/lastGame/<int:summonerid>')
def lastgame(summonerid):
    cursor.execute("""SELECT M.summoner_id,C.name, S.kills
    FROM "league"."player" AS P
    LEFT JOIN "league"."match" AS M
    ON P.game_id = M.Match_id
    LEFT JOIN "league"."match_stats" AS S
    ON M.participant_id = S.participant_id AND M.Match_id = S.Match_id
    LEFT JOIN "league"."champname" AS C
    ON S.champion_id = C.id
    WHERE P.summoner_id = '{0}'
    ;""".format(summonerid))
    last = [
        {'sumname': summoner_name,
         'championname': name,
         'kills': kills}
        for (summoner_name, name, kills) in cursor.fetchall()]
    print last
    return jsonify({'last': last})


@app.route('/api/pleb')
def pleb():
    cursor.execute("""SELECT P.summoner_name
    FROM "league"."player" AS P, "league"."match" AS M, "league"."champname" AS C
    WHERE P.game_id = M.match_id AND M.champion_id = ANY (SELECT champ_id
    FROM "league"."champion"
    WHERE free_to_play='true')
    GROUP BY P.summoner_name
    ;""")
    pleb = [{'sumname': summoner_name} for (summoner_name,) in cursor.fetchall()]
    print pleb
    return jsonify({'pleb': pleb})


@app.route('/api/topkills/<int:matchid')
def topkills(matchid):
    cursor.execute("""SELECT P.Summoner_name,C.name, S.kills
    FROM "league"."player" AS P, "league"."match_stats" AS S, "league"."champname" AS C, "league"."match" AS M
    WHERE P.game_id = M.match_id AND P.summoner_id = M.summoner_id AND M.participant_id = S.participant_id AND C.id = S.champion_id AND S.kills > (
     SELECT AVG(kills)
     from "league"."match_stats"
     WHERE )
    GROUP BY P.summoner_name,C.name, S.kills ORDER BY P.summoner_name
    ;""")
    top = [{'sumname': summoner_name,
             'champname': name,
             'kills': kills}
            for (summoner_name, name, kills) in cursor.fetchall()]
    print top
    return jsonify({'top': top})


@app.route('/api/champdata')
def champdata():
    cursor.execute("""SELECT name, ranked_play_enabled,bot_enabled,free_to_play
    FROM "league"."champname" AS N
    FULL JOIN "league"."champion" AS C
    ON N.id = C.champ_id
    ;""")
    champ = [{'name': name,
            'ranked_paly_enabled': ranked_play_enabled,
            'bot_enabled': bot_enabled,
            'free_to_play': free_to_play}
            for (name, ranked_play_enabled, bot_enabled, free_to_play) in cursor.fetchall()]
    print champ
    return jsonify({'champ': champ})


@app.route('/api/freeChamps')
def freechamps():
    cursor.execute("""SELECT CN.Name
    FROM LEAGUE.CHAMPION AS C
    RIGHT JOIN LEAGUE.CHAMPNAME AS CN ON CN.ID = C.Champ_id
    WHERE Free_to_play = 'true'""")
    data = [{'name': name} for (name,) in cursor.fetchall()]
    print data
    return jsonify({'data': data})


@app.route('/api/fastmatch')
def fastmatch():
    cursor.execute("""SELECT P.Summoner_id
    FROM "league"."player" AS P
    EXCEPT
    SELECT M.Summoner_id
    FROM "league"."match" AS M
    WHERE duration<1200
    ;""")
    fast = [{'name': name} for (name,) in cursor.fetchall()]
    print fast
    return jsonify({'fast': fast})


if __name__ == '__main__':
    app.run(port=5001, debug=True)
