import requests
import json
import cfg
from esipy import EsiApp
from esipy import EsiClient
import database
import datetime
import pytz


utc = pytz.timezone('UTC')

# Define PostgresSQL client
connection = database.create_connection(
    "killmails", "postgres", cfg.db_password, "127.0.0.1", "5432"
)
connection.autocommit = True
cursor = connection.cursor()

# Define ESI client
esi_app = EsiApp()
app = esi_app.get_latest_swagger

client = EsiClient(
    retry_requests=True,  # set to retry on http 5xx error (default False)
    headers={'User-Agent': cfg.agent},
    raw_body_only=False,  # default False, set to True to never parse response and only return raw JSON string content.
)

# Start by getting the json file for the kills on the given dates
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}
print("Downloading json files of killmails")
for date in cfg.dates:
    url = "https://zkillboard.com/api/history/" + date + ".json"
    print("Downloaded killmail list on " + date)
    response = requests.get(url, headers=headers)
    kill_dict = json.loads(response.content)
    print("Parsing kills on " + date)
    count = 0
    for key in kill_dict:
        count = count + 1
        if count % 100 == 0:
            print(count)

        killmail_fetch_operation = app.op['get_killmails_killmail_id_killmail_hash'](
            killmail_id=key,
            killmail_hash=kill_dict[key]
        )

        response = client.request(killmail_fetch_operation)
        kill_as_dict = json.loads(response.raw)
        timestamp = kill_as_dict["killmail_time"]
        timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        timestamp = timestamp.replace(tzinfo=utc)

        insert_query = (
            "INSERT INTO killmails (killmail_id, killmail_hash, date, data) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;"
        )
        cursor.execute(insert_query, (key, kill_dict[key], timestamp, json.dumps(kill_as_dict)))

