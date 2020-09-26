import json
import utm
import xml.dom.minidom
import matplotlib.pyplot as plt
import pymysql.cursors
import sys
import math
import numpy as np
from scipy.ndimage import gaussian_filter1d
import time as TIME
# 滴滴GPS数据

x_axis_offset = 309741 - 310162 - 8
y_axis_offset = 3788970 - 3788780 - 5

def compare_by_time(x):
    return x[0]


# Connect to the database
connection = pymysql.connect(host='10.251.254.54',
                             user='didi',
                             password='123456@BigData',
                             db='data',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

orders = {}
nodes = {}

try:
    with connection.cursor() as cursor:
        # Create a new record
        # sql = f"SELECT * FROM gps_1001 order by cur_time"
        print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 建立连接")
        sql = f"SELECT * FROM gps_1001 order by cur_time limit 10000"
        cursor.execute(sql)
        result = cursor.fetchall()
    connection.commit()
    print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 拉取数据完成")
    print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 开始格式化order")
    for line in result:
        driver_id = line['driver_id']
        order_id = line['order_id']
        cur_time = int(line['cur_time'])
        lng = float(line['lng'])
        lat = float(line['lat'])
        if order_id not in orders:
            orders[order_id] = []
        x, y, _, __ = utm.from_latlon(lat, lng)
        orders[order_id].append((cur_time,x + x_axis_offset,y + y_axis_offset))
        # orders[order_id][0][cur_time] = x + x_axis_offset
        # orders[order_id][1][cur_time] = y + y_axis_offset
        # orders[order_id][2].append(cur_time)

finally:
    connection.close()      

print("数据格式化成功，结束连接")


NODE_MAX_DIS2=10000
MAX_DIS = 999999999
ROAD_WIDTH = 200

def distance2(node1,node2):
    return (node1[0]-node2[0])*(node1[0]-node2[0])+(node1[1]-node2[1])*(node1[1]-node2[1])


order_cnt = 0
order_total = len(orders)
flag = True


accs = []

for order in orders:
    print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 处理订单：", order)
    orders[order] = sorted(orders[order],key=compare_by_time)
    order_list = orders[order]

    time = [t[0] for t in orders[order]]
    xs = [t[1] for t in orders[order]]
    ys = [t[2] for t in orders[order]]
    ids = [t[0] for t in orders[order]]

    if order_cnt%100 ==0:
        print("时间：", TIME.asctime(TIME.localtime(TIME.time())), " 进度：", str(order_cnt)+'/'+str(order_total))
    order_cnt+=1

    illegal = False
    gaus_xs=[]
    gaus_ys=[]
    if len(xs) < 5 :
        continue
    else:
        gaus_xs.append(xs[0])
        gaus_ys.append(ys[0])
    
    i = 1
    while i< len(xs):
        pre_point=(xs[i-1],ys[i-1])
        point=(xs[i],ys[i])
        if distance2 (pre_point,point) > NODE_MAX_DIS2:
            illegal = True
            break
        gaus_xs.append(point[0])
        gaus_ys.append(point[1])
        i+=1
    if not illegal:
        gaus_xs = gaussian_filter1d(gaus_xs, 0.5)
        gaus_ys = gaussian_filter1d(gaus_ys, 0.5)

        # plt.plot(gaus_xs, gaus_ys)
        # plt.scatter(gaus_xs, gaus_ys)

        # j = 0
        # while j < len(gaus_xs):
        #     gaus_xs[j],gaus_ys[j] = node_mapping(gaus_xs[j],gaus_ys[j],order)
        #     j+=1

        # modified_orders[order] = [[],[]]
        # modified_orders[order][0] = gaus_xs
        # modified_orders[order][1] = gaus_ys
        
        # orders[order][2].sort()
        # time = orders[order][2]

        velocity = []
        velocity.append(0)
        i = 1
        while i < len(gaus_xs) - 1:
            delta_t1 = time[i+1] - time[i-1]
            # delta_t2 = time[i+1] - time[i]
            delta_x1 = math.sqrt(distance2((gaus_xs[i-1],gaus_ys[i-1]),(gaus_xs[i+1],gaus_ys[i+1])))
            # delta_x2 = math.sqrt(distance2((gaus_xs[i],gaus_ys[i]),(gaus_xs[i+1],gaus_ys[i+1])))
            velo = (delta_x1/delta_t1)
            velocity.append(velo)
            i+=1
        i = len(gaus_xs) - 1
        velocity.append(math.sqrt(distance2((gaus_xs[i-1],gaus_ys[i-1]),(gaus_xs[i],gaus_ys[i])))/(time[i] - time[i-1]))

        speeds = {}
        speeds[ids[0]]=(0,0,0)
        tmp_speed = []
        tmp_speed.append((0,0,0))
        i = 1
        while i<len(velocity):
            v = velocity[i]
            a = velocity[i] - velocity[i-1]
            avg_v = math.sqrt(distance2((gaus_xs[i-1],gaus_ys[i-1]),(gaus_xs[i],gaus_ys[i])))/(time[i] - time[i-1])
            speeds[ids[i]] = (v,avg_v,a)
            tmp_speed.append((v,avg_v,a))
            i+=1
        a = [t[2] for t in tmp_speed]
        accs.append(np.var(a))
#         if flag:
#             v = [t[0] for t in tmp_speed]
#             avg_v = [t[1] for t in tmp_speed]
#             a = [t[2] for t in tmp_speed]
#             plt.plot(v,'r')
#             plt.plot(avg_v,'b')
#             plt.show()
#             plt.plot(a)
#             plt.show()
#             print('速度:\n均值:%f\t方差:%f\t标准差:%f\t最大/最小值:%f/%f\n\n'%(np.mean(v),np.var(v),np.std(v),np.max(v),np.min(v)))
#             print('平均速度:\n均值:%f\t方差:%f\t标准差:%f\t最大/最小值:%f/%f\n\n'%(np.mean(avg_v),np.var(avg_v),np.std(avg_v),np.max(avg_v),np.min(avg_v)))
#             print('加速度:\n均值:%f\t方差:%f\t标准差:%f\t最大/最小值:%f/%f\n\n'%(np.mean(a),np.var(a),np.std(a),np.max(a),np.min(a)))
#             accs.append(np.var(a))
# #             flag= False

# accs.sort()
# plt.plot(accs)
# plt.plot(np.sqrt(accs))

# plt.show()

from numpy import array
from scipy.cluster.vq import vq, kmeans2, whiten
features  = array(accs)
codes = 3
arr1,arr2 = kmeans2(features,codes)


points ={}
for i in range(0,codes):
    points[i] = []
    
i = 0
while i<len(arr2):
    points[arr2[i]].append(accs[i])
    i+=1

print(arr1)

for i in range(0,codes):
    plt.plot(points[i],np.zeros_like(points[i]),'.')
plt.plot(arr1,np.zeros_like(arr1),'yx',markersize=20)
plt.show()