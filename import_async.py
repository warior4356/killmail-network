import requests
import json
import cfg
from esipy import EsiApp
from esipy import EsiClient
import database
import datetime
import pytz
import asyncio
from aiohttp import ClientSession
import time

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
# for date in cfg.dates:
#     url = "https://zkillboard.com/api/history/" + date + ".json"
#     print("Downloaded killmail list on " + date)
#     response = requests.get(url, headers=headers)
#     kill_dict = json.loads(response.content)
#     print("Parsing kills on " + date)
#     count = 0
#     for key in kill_dict:
#         count = count + 1
#         if count % 100 == 0:
#             print(count)
#
#         killmail_fetch_operation = app.op['get_killmails_killmail_id_killmail_hash'](
#             killmail_id=key,
#             killmail_hash=kill_dict[key]
#         )
#
#         response = client.request(killmail_fetch_operation)
#         kill_as_dict = json.loads(response.raw)
#         timestamp = kill_as_dict["killmail_time"]
#         timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
#         timestamp = timestamp.replace(tzinfo=utc)
#
#         insert_query = (
#             "INSERT INTO killmails (killmail_id, killmail_hash, date, data) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;"
#         )
#         cursor.execute(insert_query, (key, kill_dict[key], timestamp, json.dumps(kill_as_dict)))

async def fetch_killmail(session, killmail_id, killmail_hash):
    url = "https://esi.evetech.net/latest/killmails/" \
          + killmail_id + \
          "/" \
          + killmail_hash + \
          "/?datasource=tranquility"
    while True:
        async with session.get(url, headers={"User-Agent": cfg.agent}) as response:
            if response.status == 200:
                data = await response.json()
                timestamp = data["killmail_time"]
                timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
                timestamp = timestamp.replace(tzinfo=utc)

                insert_query = (
                    "INSERT INTO killmails (killmail_id, killmail_hash, date, data) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;"
                )
                cursor.execute(insert_query, (killmail_id, killmail_hash, timestamp, json.dumps(data)))
                return await response.json()
            elif response.status >= 400 and response.status <= 499:
                return []
            else:
                print(response.url)
                print(response.status)


async def bound_fetch_killmail(sem, session, killmail_id, killmail_hash):
    # Getter function with semaphore.
    async with sem:
        return await fetch_killmail(session, killmail_id, killmail_hash)

async def collect_killmails(killmail_dict):
    print("Starting Killmail Scrape")
    start_time = time.time()
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(100)

    # Create client session that will ensure we dont open new connection
    # per each request.
    i = 0
    async with ClientSession() as session:
        for killmail_id in killmail_dict:
                # pass Semaphore and session to every GET request
                task = asyncio.ensure_future(bound_fetch_killmail(sem, session, killmail_id, killmail_dict[killmail_id]))
                tasks.append(task)
                i += 1

        responses = asyncio.gather(*tasks)
        await responses
    histories = list()
    count = 0
    for response in responses.result():
        for history in response:
            # histories.append(history["volume"])
            count += 1
    end_time = time.time()
    elapsed = end_time - start_time
    print('Elapsed time for {} killmail requests was: {}'.format(i, elapsed))
    return count


def main():
    loop = asyncio.get_event_loop()

    for date in cfg.dates:
        url = "https://zkillboard.com/api/history/" + date + ".json"
        print("Downloaded killmail list on " + date)
        response = requests.get(url, headers=headers)
        kill_dict = json.loads(response.content)
        print("Parsing " + str(len(kill_dict.keys())) + " kills on " + date)

        killmails = loop.run_until_complete(collect_killmails(kill_dict))
        print("The size of the killmails is " + str(killmails))


if __name__ == "__main__":
    main()
