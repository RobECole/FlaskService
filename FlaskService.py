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


@app.route('/api/pleb/<matchid>')
def pleb(matchid):
    cursor.execute("""SELECT M.Summoner_id, C.name
    FROM "league"."player" AS P, "league"."match" AS M, "league"."champname" AS C
    WHERE M.match_id = '{0}' AND M.champion_id = C.id AND  M.champion_id = ANY (SELECT champ_id
    FROM "league"."champion"
    WHERE free_to_play='true')
    GROUP BY M.Summoner_id, C.name
    ;""".format(matchid))
    pleb = [{'sumname': summoner_name, 'champname': champion_id} for (summoner_name, champion_id) in cursor.fetchall()]
    print pleb
    return jsonify({'pleb': pleb})


@app.route('/api/topkills/<matchid>')
def topkills(matchid):
    cursor.execute("""SELECT M.summoner_id,C.name, S.kills
    FROM "league"."player" AS P, "league"."match_stats" AS S, "league"."champname" AS C, "league"."match" AS M
    WHERE '{0}' = M.match_id AND M.match_id = S.match_id AND M.participant_id = S.participant_id AND C.id = S.champion_id AND S.kills > (
     SELECT AVG(kills)
     from "league"."match_stats" AS MS,"league"."match" AS LM
     WHERE LM.match_id = '{0}' AND LM.match_id = MS.match_id AND LM.participant_id = MS.participant_id)
    GROUP BY M.summoner_id,C.name, S.kills ORDER BY M.summoner_id
    ;""".format(matchid))
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


@app.route('/api/fastmatch/<int:sumid>')
def fastmatch(sumid):
    cursor.execute("""SELECT M.match_id, M.Duration
    FROM "league"."player" AS P, "league"."match" as M
    WHERE P.Summoner_id = M.Summoner_id AND P.summoner_id = '{0}'
    EXCEPT
    SELECT LM.Summoner_id, LM.Duration
    FROM "league"."match" as LM
    WHERE LM.duration<1200
    ;""".format(sumid))
    fast = [{'name': summoner_id, 'duration': Duration} for (summoner_id, Duration) in cursor.fetchall()]
    print fast
    return jsonify({'fast': fast})


@app.route('/api/wins/<int:id>')
def wins(id):
    cursor.execute(""" SELECT unranked_win, ranked_win3v3, ranked_win5v5
    FROM "league"."player"
    WHERE summoner_id = '{0}';""".format(id))
    wins = [{'unranked': unranked_win,
             'ranked3': ranked_win3v3,
             'ranked5': ranked_win5v5} for (unranked_win, ranked_win3v3, ranked_win5v5) in cursor.fetchall()]
    print wins
    return jsonify({'wins': wins})


@app.route('/api/count/<int:id>')
def teamcount(id):
    cursor.execute("""SELECT T.team_name, T.wins3v3, T.losses3v3, T.wins5v5, T.losses5v5
FROM "league"."team" AS T, "league"."teamlist" as L
WHERE T.team_id = L.id AND L.sumid = '{0}';""".format(id))
    count = [{'name': team_name,
              'w3v3': wins3v3,
              'l3v3': losses3v3,
              'w5v5': wins5v5,
              'l5v5': losses5v5} for (team_name, wins3v3, losses3v3, wins5v5, losses5v5) in cursor.fetchall()]
    print count
    return jsonify({'count': count})


@app.route('/api/secondarystats/<int:matchid>')
def secondarystats(matchid):
    cursor.execute("""SELECT C.name, M.creep_kills, M.gold_earned, M.damage_dealt_to_champs
    FROM "league"."match_stats" AS M, "league"."champname" AS C
    WHERE M.match_id = '{0}' AND C.id = M.champion_id;""".format(matchid))
    secondary = [{'name': name,
                  'creep': creep_kills,
                  'gold': gold_earned,
                  'damage': damage_dealt_to_champs} for (name, creep_kills, gold_earned, damage_dealt_to_champs,) in cursor.fetchall()]
    print secondary
    return jsonify({'secondary': secondary})


@app.route('/api/kdr/<int:matchid>')
def kdr(matchid):
    cursor.execute("""SELECT M.summoner_id, C.name, S.kills, s.deaths
FROM "league"."match" AS M, "league"."match_stats" AS S, "league"."champname" AS C
WHERE S.match_id = '{0}' AND S.match_id = M.match_id AND s.participant_id = M.participant_id AND S.champion_id = C.id
""".format(matchid))
    kdr = [{'sumid': summoner_id, 'cid': champion_id, 'kills': kills, 'deaths': deaths} for (summoner_id, champion_id, kills, deaths) in cursor.fetchall()]
    for x in xrange(len(kdr)):
        if kdr[x].get('deaths') == 0:
            kdr[x]['deaths'] = 1
        print kdr[x].get('deaths')
        kdr[x]['kills'] = kdr[x].get('kills')/float(kdr[x].get('deaths'))
        kdr[x]['kills'] = float("{0:.2}".format(kdr[x].get('kills')))
    return jsonify({'kdr': kdr})


if __name__ == '__main__':
    app.run(port=5001, debug=True)
