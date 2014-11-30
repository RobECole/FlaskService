from flask import Flask, jsonify
import psycopg2
import riotwatcher
app = Flask(__name__)

conn_string = "host='localhost' dbname='LEAGUE_CIRCUIT' user='postgres' password='testdb'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
key = '1dbf97cc-5028-4196-a05c-6645adc80bef'
w = riotwatcher.RiotWatcher(key)

#comment

@app.route('/api/lastGame/<int:summonerid>')
def lastgame(summonerid):
    cursor.execute("""SELECT P.summoner_name,C.name, S.kills
    FROM "league"."player" AS P
    LEFT JOIN "league"."match" AS M
    ON P.game_id = M.Match_id AND P.summoner_id = M.Summoner_id
    LEFT JOIN "league"."match_stats" AS S
    ON M.participant_id = S.participant_id
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


@app.route('/api/freeChamps')
def freechamps():
    cursor.execute("""SELECT CN.Name
    FROM LEAGUE.CHAMPION AS C
    RIGHT JOIN LEAGUE.CHAMPNAME AS CN ON CN.ID = C.Champ_id
    WHERE Free_to_play = 'true'""")
    data = [{'name': name} for (name,) in cursor.fetchall()]
    print data
    return jsonify({'data': data})





if __name__ == '__main__':
    app.run(port=5001, debug=True)
