import json
import utm
import xml.dom.minidom
import matplotlib.pyplot as plt
import pymysql.cursors
import sys

# 道路数据
max_lat = 34.2803
max_lng = 108.9987
min_lat = 34.2053
min_lng = 108.9111
max_x, max_y, _, __ = utm.from_latlon(max_lat, max_lng)
min_x, min_y, _, __ = utm.from_latlon(min_lat, min_lng)
# selected = ['primary', 'secondary']
selected = ['primary', 'secondary','primary_link', 'secondary_link', 'unclassified','tertiary', 'trunk', 'trunk_link']


dom = xml.dom.minidom.parse('interpreter.osm')
root = dom.documentElement
nodelist = root.getElementsByTagName('node')
waylist = root.getElementsByTagName('way')

node_dic = {}
for node in nodelist:
    node_id = node.getAttribute('id')
    node_lat = float(node.getAttribute('lat'))
    node_lon = float(node.getAttribute('lon'))
    x, y, _, __ = utm.from_latlon(node_lat, node_lon)
    if x > min_x and x < max_x and y > min_y and y < max_y:
        node_dic[node_id] = (x, y)

way_dic = {}
for way in waylist:
    taglist = way.getElementsByTagName('tag')
    way_id = way.getAttribute('id')
    way_name = 'unknown'
    road_flag = False
    for tag in taglist:
        if tag.hasAttribute('name'):
            way_name = tag.getAttribute('name')
        else:
            way_name = tag.getAttribute('name:zh')

        if tag.getAttribute('k') == 'highway' and tag.getAttribute('v') in selected:
            road_flag = True

    if road_flag:
        ndlist = way.getElementsByTagName('nd')
        if len(ndlist) > 0:
            wayndx = []
            wayndy = []
            for nd in ndlist:
                nd_id = nd.getAttribute('ref')
                if nd_id in node_dic:
                    wayndx.append(node_dic[nd_id][0])
                    wayndy.append(node_dic[nd_id][1])
            if len(wayndx) > 0:
                way_dic[way_id] = [[], []]
                way_dic[way_id][0] = wayndx
                way_dic[way_id][1] = wayndy

way_num = len(way_dic)
i = 1

# 画出道路图
for w in way_dic:
    plt.plot(way_dic[w][0], way_dic[w][1], 'b')
    plt.scatter(way_dic[w][0], way_dic[w][1],c='red')
    if i % 100 == 0:
        print((str)(i)+"/"+(str)(way_num)+"\n")
    i += 1
plt.show()