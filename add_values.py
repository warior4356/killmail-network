import database
import cfg
import requests
import json
import datetime

def insert_prices(item_type):
    url = "https://zkillboard.com/api/prices/" + str(item_type) + "/"
    print("Downloaded item price list for type: " + str(item_type))
    response = requests.get(url, headers=headers)
    # print(url)
    # print(response)
    # print(response.content)
    item_dict = json.loads(response.content)

    insert_query = (
        "INSERT INTO items_default (item_id, value, updated) VALUES (%s, %s, %s) ON CONFLICT (item_id) DO UPDATE "
        "SET value = %s, updated = %s;"
    )

    cursor.execute(insert_query, [item_type, item_dict['currentPrice'], datetime.datetime.utcnow().date(),
                                  item_dict['currentPrice'], datetime.datetime.utcnow().date()])

    for key in item_dict:
        if len(key) == 10:
            insert_query = (
                "INSERT INTO items (item_id, date, value) VALUES (%s, %s, %s) ON CONFLICT (item_id, date) DO UPDATE "
                "SET value = %s;"
            )
            cursor.execute(insert_query, [item_type, key, item_dict[key], item_dict[key]])


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}

connection = database.create_connection(
    "killmails", "postgres", cfg.db_password, "127.0.0.1", "5432"
)
connection.autocommit = True
cursor = connection.cursor()

def main():
    fetch_query = (
        "SELECT * FROM killmails where killmails.value IS NULL"
    )

    # fetch_query = (
    #     "SELECT * FROM killmails where killmails.killmail_id = '91860861'"
    # )

    # fetch_query = (
    #     "SELECT * FROM killmails where killmails.killmail_id = '91860631'"
    # )

    cursor.execute(fetch_query)
    rows = cursor.fetchall()

    print("Row count: " + str(len(rows)))
    for row in rows:
        count = 0
        count = count + 1
        if count % 100 == 0:
            print("Current KM count: " + str(count))

        value = 0
        prices = dict()
        types = list()
        types_number = list()
        missing_types = list()
        types.append(row[3]['victim']['ship_type_id'])
        missing_types.append(row[3]['victim']['ship_type_id'])
        types_number.append((row[3]['victim']['ship_type_id'], 1))
        for item in row[3]['victim']['items']:
            if item['item_type_id'] in types:
                continue

            quantity = 0
            if 'quantity_destroyed' in item.keys():
                quantity += item['quantity_destroyed']
            if 'quantity_dropped' in item.keys():
                quantity += item['quantity_dropped']

            types.append(item['item_type_id'])
            missing_types.append(item['item_type_id'])
            types_number.append((item['item_type_id'], quantity))

        fetch_query = (
            "SELECT item_id, value FROM items where item_id IN %s AND date = %s"
        )
        cursor.execute(fetch_query, [tuple(types), row[2].date()])
        items = cursor.fetchall()

        fetch_query = (
            "SELECT item_id, value, updated FROM items_default where item_id IN %s"
        )
        cursor.execute(fetch_query, [tuple(types)])
        items_default = cursor.fetchall()

        if not len(items) == len(missing_types):
            # print(missing_types)

            items_update_dates = dict()
            for item in items_default:
                # print(item[2].date())
                items_update_dates[item[0]] = item[2].date()
            # print(items_update_dates)

            for item in items:
                # print(item[0])
                missing_types.remove(item[0])

            # print(missing_types)

            for item in missing_types:
                # print(item)
                # print("stored")
                # print(items_update_dates[item])
                # print("now")
                # print(datetime.datetime.utcnow().date())
                if item in items_update_dates.keys() and items_update_dates[item] >= datetime.datetime.now().date():
                    # print("removing type:" + str(item))
                    missing_types.remove(item)

            if len(missing_types) > 0:
                print(str(row[0]) + ": " + str(missing_types))

            for item_type in missing_types:
                insert_prices(item_type)

            fetch_query = (
                "SELECT item_id, value FROM items where item_id IN %s AND date = %s"
            )
            cursor.execute(fetch_query, [tuple(types), row[2].date()])
            items = cursor.fetchall()

            fetch_query = (
                "SELECT item_id, value, updated FROM items_default where item_id IN %s"
            )
            cursor.execute(fetch_query, [tuple(types)])
            items_default = cursor.fetchall()

        for item in items:
            prices[item[0]] = item[1]

        for item in items_default:
            if item[0] not in prices.keys():
                prices[item[0]] = item[1]

        # print(prices)

        for type in types_number:
            # print(type[0])
            # print(type[1])
            # print(prices[type[0]])
            value += (prices[type[0]] * type[1])
            # print(value)

        update_query = (
            "UPDATE killmails SET value = %s WHERE killmail_id = %s"
        )
        cursor.execute(update_query, [value, row[0]])

if __name__ == "__main__":
    main()
