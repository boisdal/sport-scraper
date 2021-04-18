import json
import urllib.request as req
import sys

url = "https://www.thesportsdb.com/api/v1/json/1/lookup_all_teams.php?id=" + sys.argv[1]

response = req.urlopen(url)
league = json.loads(response.read())

with open("leagues.json", 'r') as f:
    leagues = json.load(f)

leagueName = league['teams'][0]['strLeague']
leagues[leagueName] = {}
for lea in league['teams']:
    leagues[leagueName][lea['strTeam']] = lea['idTeam'] 

with open("leagues.json", 'w', encoding='utf-8') as f:
    json.dump(leagues, f, indent=4, sort_keys=True, ensure_ascii=False)
