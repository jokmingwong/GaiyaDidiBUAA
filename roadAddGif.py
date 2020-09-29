import json
import utm
import xml.dom.minidom
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pymysql.cursors
import sys
import time as TIME

# 道路数据
max_lat = 34.2803
max_lng = 108.9987
min_lat = 34.2053
min_lng = 108.9111
max_x, max_y, _, __ = utm.from_latlon(max_lat, max_lng)
min_x, min_y, _, __ = utm.from_latlon(min_lat, min_lng)
# selected = ['primary', 'secondary']
selected = ['primary', 'secondary','primary_link', 'secondary_link', 'unclassified','tertiary', 'trunk', 'trunk_link']


# 画图初始化
frameNum = 120
numOfPatch = 1
fig, ax = plt.subplots()
xdata,ydata=[],[]
ln, = plt.plot([], [], 'ro',animated=True)

node_id_list=[]
way_dic = {}

def update(frame):
    maxi = (frame + 1) * numOfPatch if (frame + 1) * numOfPatch <= len(way_id_list) else len(way_id_list)
    for i in range(frame * numOfPatch, maxi):
        xdata.extend(way_dic[way_id_list[i]][0])
        ydata.extend(way_dic[way_id_list[i]][1])
    ln.set_data(xdata,ydata)
    print(TIME.asctime(TIME.localtime(TIME.time())),"frame: ", frame)
    return ln,

def init():
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    return ln,

print(TIME.asctime(TIME.localtime(TIME.time())), " 初始化完毕")



# 打开OpenStreetMap文件
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
        node_id_list.append(node_id)

print(TIME.asctime(TIME.localtime(TIME.time())), " 添加node完毕")

way_id_list = []

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
                way_id_list.append(way_id)


print(TIME.asctime(TIME.localtime(TIME.time())), " 道路信息添加完毕")
print(TIME.asctime(TIME.localtime(TIME.time())), " len(way_dic)=", len(way_dic))
print(way_dic[way_id_list[0]])
# 画出道路图
'''
for w in way_dic:
    im=plt.plot(way_dic[w][0], way_dic[w][1], 'r')
    plt.scatter(way_dic[w][0], way_dic[w][1],c='yellow')
'''
numOfPatch = int(len(way_id_list) / frameNum)
anim = animation.FuncAnimation(fig, update, frames=frameNum,interval=20,init_func=init,blit=True)
# plt.show()

animWriter = animation.PillowWriter(fps=20)
print(TIME.asctime(TIME.localtime(TIME.time())), " len(way_id_list)=", len(way_id_list))


anim.save('road_animation.gif',writer=animWriter)