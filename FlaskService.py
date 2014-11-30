from flask import Flask, jsonify
import json
import psycopg2
import requests
#import riotwatcher
app = Flask(__name__)

conn_string = "host='localhost' dbname='LEAGUE_CIRCUIT' user='postgres' password='testdb'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
#key = '1dbf97cc-5028-4196-a05c-6645adc80bef'
#w = riotwatcher.RiotWatcher(key)


#@app.route('/api/update/<name>', methods=['GET'])
#def update(name):

    #summonerdata = w.get_summoner(name)
    #id = summonerdata['id']
    #match_history = w.get_match_history(id)
    #if 'matches' in match_history:
    #    matches = match_history['matches']
    #    matches.reverse()
    #    match_id = matches[0]['matchId']


@app.route('/api/lastGame', methods=['GET', 'POST'])
def lastgame():
    cursor.execute("""SELECT P.summoner_name,C.name, S.kills
    FROM "league"."player" AS P
    LEFT JOIN "league"."match" AS M
    ON P.game_id = M.Match_id AND P.summoner_id = M.Summoner_id
    LEFT JOIN "league"."match_stats" AS S
    ON M.participant_id = S.participant_id
    LEFT JOIN "league"."champname" AS C
    ON S.champion_id = C.id
    WHERE P.summoner_id = 45979934
    ;""")
    name = [{'name': name} for (name,) in cursor.fetchall()]
    cname = [{'cname': cname} for (cname,) in cursor.fetchall()]
    kills = []
    print name
    print cname
    print kills
    return jsonify({'last': name})



@app.route('/api/freeChamps', methods=['GET', 'POST'])
def freechamps():
    cursor.execute("SELECT CN.Name FROM LEAGUE.CHAMPION AS C RIGHT JOIN LEAGUE.CHAMPNAME AS CN ON CN.ID = C.Champ_id WHERE Free_to_play = 'true'")
    data = [{'name': name} for (name,) in cursor.fetchall()]
    print data
    return jsonify({'data': data})





if __name__ == '__main__':
    app.run(port=5001, debug=True)
