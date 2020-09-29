import utm
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import pymysql.cursors
import sys
import time as TIME
import numpy as np
from scipy.stats import gaussian_kde


def sort_by_time(path: dict):
    keys = list(path.keys())
    keys.sort()
    return [path[t] for t in keys]


def filter(order_id, orders: dict):
    xs = sort_by_time(orders[order_id][0])
    ys = sort_by_time(orders[order_id][1])
    cur_time = [*orders[order_id][0]]
    cur_time.sort()
    for i in range(0, len(cur_time) - 1):
        if cur_time[i+1] - cur_time[i] > max_interval:
            remove_id.append(order_id)
            return
        x1, y1 = xs[i], ys[i]
        x2, y2 = xs[i + 1], ys[i + 1]
        if (x1-x2)**2 + (y1-y2)**2 > ((cur_time[i+1] - cur_time[i])*max_velocity)**2:
            remove_id.append(order_id)
            return



for gps in range (1001, 1032):
    # Connect to the database
    connection = pymysql.connect(host='10.251.254.54',  
                             user='didi',
                             password='123456@BigData',
                             db='data',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    orders = {}
    illegal_order = []
    illegal_driver = {}  # {名字: 违规订单数}
    max_interval = 30   # 数据最多允许30s的间隔
    max_velocity = 120
    remove_id = []

    try:
        with connection.cursor() as cursor:
            # Create a new record
            # sql = f"SELECT * FROM gps_{gps} limit 500000"

            print("时间：", TIME.asctime(TIME.localtime(
                TIME.time())), " 建立连接，拉取：", gps)
            sql = "SELECT * FROM gps_" + str(gps) + " limit 500000"
            cursor.execute(sql)
            result = cursor.fetchall()
        print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 拉取数据完成")
        connection.commit()
        print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 开始格式化order")
        for line in result:
            driver_id = line['driver_id']
            order_id = line['order_id']
            cur_time = int(line['cur_time'])
            lng = float(line['lng'])
            lat = float(line['lat'])
            if order_id not in orders:
                orders[order_id] = ({}, {})
            x, y, _, __ = utm.from_latlon(lat, lng)
            orders[order_id][0][cur_time] = x
            orders[order_id][1][cur_time] = y
        print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 格式化数据完成")
        for order_id in orders.keys():
            filter(order_id, orders)
        print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 判断非法数据完成")
        for order_id in remove_id:
            orders.pop(order_id, None)
        print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 清理非法数据完成")
        x = []
        y = []
        for v in orders.values():
            xs = sort_by_time(v[0])
            ys = sort_by_time(v[1])
            x.extend(xs)
            y.extend(ys)
            # plt.plot(xs, ys)
            n = 1

        print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " show")
        

        
        plt.hist2d(x,y,bins=60,norm=LogNorm())
        plt.colorbar()
        plt.savefig("gps"+str(gps) + "_trace.png")
    finally:
        connection.close()
