import utm
import matplotlib.pyplot as plt
import pymysql.cursors
import sys

def sort_by_time(path: dict):
    keys = list(path.keys())
    keys.sort()
    return [path[t] for t in keys]


# Connect to the database
connection = pymysql.connect(host='10.251.254.54',
                             user='didi',
                             password='123456@BigData',
                             db='data',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

orders = {}

try:
    with connection.cursor() as cursor:
        # Create a new record
        # sql = f"SELECT * FROM gps_{sys.argv[1]} limit 500000"
        sql = f"SELECT * FROM gps_{sys.argv[1]} limit 500000"
        cursor.execute(sql)
        result = cursor.fetchall()
    connection.commit()
    for line in result:
        driver_id = line['driver_id']
        order_id = line['order_id']
        cur_time = int(line['cur_time'])
        lng = float(line['lng'])
        lat = float(line['lat'])
        if order_id not in orders:
            orders[order_id] = ({},{})
        x, y, _, __ = utm.from_latlon(lat, lng)
        orders[order_id][0][cur_time] = x
        orders[order_id][1][cur_time] = y
    for v in orders.values():
        xs = sort_by_time(v[0])
        ys = sort_by_time(v[1])
        plt.plot(xs, ys)
        n=50
        plt.scatter(xs[::n],ys[::n])
    plt.show()

finally:
    connection.close()