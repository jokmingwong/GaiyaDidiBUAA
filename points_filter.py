import utm
import matplotlib.pyplot as plt
import pymysql.cursors
import sys
import logging

connection = pymysql.connect(host='10.251.254.54',user='didi',password='123456@BigData',db='data',charset='utf8mb4',cursorclass=pymysql.cursors.SSDictCursor)
buffer = {}
blacklist = {}
max_interval = 3
max_velocity = 100
cnt = 0

try:
    with connection.cursor() as cursor:
        sql = "SELECT id, driver_id, order_id, cur_time, lat, lng FROM gps_1001 order by cur_time asc"
        cursor.execute(sql)
        while True:
            result = cursor.fetchone()
            if cnt % 10000 == 0:
                print(cnt)
            cnt = cnt + 1
            if result is None:
                break
            pid = result['id']
            order_id = result['order_id']
            if order_id in buffer and buffer[order_id] is None:
                continue
            driver_id = result['driver_id']
            cur_time = int(result['cur_time'])
            lat = float(result['lat'])
            lng = float(result['lng'])
            if order_id not in buffer:
                buffer[order_id] = [(cur_time, lat, lng, pid, driver_id)]
            else:
                last = buffer[order_id][-1]
                if cur_time - last[0] > max_interval:
                    buffer[order_id] = None
                    continue
                x1, y1, _, __ = utm.from_latlon(last[1], last[2])
                x2, y2, _, __ = utm.from_latlon(lat, lng)
                if (x1-x2)**2 + (y1-y2)**2 > ((cur_time - last[0])*max_velocity)**2:
                    buffer[order_id] = None
                    continue
                buffer[order_id].append((cur_time, lat, lng, pid, driver_id))
    connection.commit()
    cnt = 0
    print(f"All {len(buffer)}")
    with connection.cursor() as cursor:
        for order_id, plist in buffer.items():
            if cnt % 1000 == 0:
                print(cnt)
            cnt = cnt + 1
            if plist is None:
                continue
            points = cursor.executemany("insert into gps_1001_useful values (null, %s, %s, %s, %s, %s, %s)", [(tp[3],tp[4], order_id, tp[1], tp[2], tp[0]) for tp in plist])
    connection.commit()
except Exception as e:
    logging.exception("")
finally:
    connection.close()