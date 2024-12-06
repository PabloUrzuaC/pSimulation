#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
import json

from P2P_functions import *
from misc_funcs import *


# matplotlib.use('TkAgg')

img = Image.open("cd3.png").convert("L")
width=203.7 # m 
height=118 # m


dt=1 # s
tf=600 # s
tlist=np.arange(0, tf, step=1)
cant_steps=int(tf/dt+1) # se considera que comienza de t=0 hasta t=tf, entonces son tf/dt+1 steps

bot_params={
'bot_vel' : 0.6, # m/s
'tbateria' : 1200, # s
'tbateria_lim' : 30, # s
'tgiro' : 5, # s
'staging_nodes':[0], # s
'tcarga_pllt' : 30, # s
'giro_tol' : 0.5, # m
} 


f = open('nodes_dict.txt', 'r')
nodes_dict = json.loads(f.read())
    
f = open('ien_dict.txt', 'r')
ien_dict = json.loads(f.read())

f = open('iden_dict.txt', 'r')
iden_dict = json.loads(f.read())

xyz,ien,iden_dict2=DictToArray(nodes_dict,ien_dict,iden_dict)


# plotmap(xyz,ien,img,width,height)

#%%
ad,con=build_ad_con(xyz,ien)

# create bots
cant_bots=5
bot_list=CreateBots_P2P(cant_bots,xyz,cant_steps,bot_params)


# create pllts
# id,inid,desid,tin
# pllt_list=[cpllt([],0,12,0,tf)]
pllt_list=[]
# flujo reception to storage 
pllt_list=AddFlujo(pllt_list,iden_dict2,47,tf,'reception','storage')
# flujo storage to dynamic ramps
pllt_list=AddFlujo(pllt_list,iden_dict2,5,tf,'storage','dynamic_ramps')
# flujo storage to shipping 
pllt_list=AddFlujo(pllt_list,iden_dict2,32,tf,'storage','shipping')
# flujo storage to pick to belt
pllt_list=AddFlujo(pllt_list,iden_dict2,11,tf,'storage','pick_to_belt')
# flujo sorter to shipping
pllt_list=AddFlujo(pllt_list,iden_dict2,31,tf,'sorter','shipping')

t_termino_tareas, total_congestion_time, total_idle_time, pllts_terminados=psim(xyz,ad,con,bot_list,pllt_list,False,cant_steps,dt)




#%%


cant_bots_list=np.arange(20, 35, 1)
lista_t_termino=[]
congestion_time_list=[]
idle_time_list=[]
for i in range(0,len(cant_bots_list)):
    bot_list=CreateBots(cant_bots_list[i],xyz,cant_steps,bot_params) 
    t_termino_tareas, total_congestion_time, total_idle_time, pllts_terminados=psim(xyz,ad,con,bot_list,pllt_list,False,cant_steps,dt)
    lista_t_termino.append(t_termino_tareas)
    congestion_time_list.append(total_congestion_time)
    idle_time_list.append(total_idle_time)


#%%

fig0, axis0 = plt.subplots()
axis0.plot(cant_bots_list,lista_t_termino)

fig1, axis1 = plt.subplots()
axis1.plot(cant_bots_list,congestion_time_list,c='r')

fig2, axis2 = plt.subplots()
axis2.plot(cant_bots_list,idle_time_list,c='g')

axis0.grid()
axis1.grid()
axis2.grid()

plt.show()

#%%

matplotlib.use('TkAgg')
PlotAnim_P2P(xyz,pllt_list,bot_list,cant_steps,height,width,img,False)







    
    

