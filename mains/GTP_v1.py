#%%

from misc_funcs import *
from GTP_functions_v1_1 import * 
import json


f = open('gtp_test2_1_nodes_dict.txt', 'r')
nodes_dict = json.loads(f.read())
f = open('gtp_test2_1_ien_dict.txt', 'r')
ien_dict = json.loads(f.read())
f = open('gtp_test2_1_iden_dict.txt', 'r')
iden_dict = json.loads(f.read())
xyz,ien,iden_dict2=DictToArray(nodes_dict,ien_dict,iden_dict)

# plotmap(xyz,ien,False,False,False)

#%%

dt=1 # s
tf=160 # s
tlist=np.arange(0, tf, step=1)
cant_steps=int(tf/dt+1) # se considera que comienza de t=0 hasta t=tf, entonces son tf/dt+1 steps


sim_params={
'xyz': xyz,
'ien' : ien,
'dt' : dt,
'cant_steps' : cant_steps,
't_picking_per_unit' : 1,
'nodo_pllt_vacios' : 9,
'nodos_almacenamiento' : iden_dict2['nodos_almacenamiento'],
'max_orders_per_pps' : 2,
'print_log' : True,
'tiempo_carga_pllt' : 5
}


bot_common_params={
'bot_vel' : 0.6, # m/s
'tbateria_inicial' : 1200, # s
'tbateria_lim' : 30, # s
'tgiro' : 5, # s
'staging_nodes':[0], # s
'giro_tol' : 0.5, # m
'lim_dist_congestion' : 2, # m
'nodos_bateria' : [3], 
} 

sim1=cSimulation(sim_params,bot_common_params)

# crear bots
cant_bots=2
sim1.create_bots_gtp(cant_bots,0)
# crear pps
cant_pps=1
sim1.create_pps(cant_pps,[10])
# crear pallets
pllt_params={
'tin' : 3,
'sku' : '0',
'qty' : 10,
'id_pos' : 11,       
'state' : 2,
'id_almacenamiento' : False
}
sim1.create_pllt(pllt_params)
# crear ordenes
lista1={
'0' : 5
}
sim1.create_order(lista1)
lista2={
'0' : 2
}
sim1.create_order(lista2)
lista3={
'0' : 6
}
sim1.create_order(lista3)
# correr simulacion
sim1.psim_gtp()
bot_list=sim1.bot_list
bot1=bot_list[0]



#%%

matplotlib.use('TkAgg')
plot_anim_gtp(sim1.xyz,sim1.bot_list,sim1.cant_steps,64.3,38.9,'gtp1.png',False,20)





