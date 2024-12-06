#%%
import numpy as np
import matplotlib
matplotlib.use('TkAgg')

import sys
sys.path.append('C:/Users/PabloUrzúa/sim1pc/modulos_generales')
sys.path.append('C:/Users/PabloUrzúa/sim1pc/GTP/modulos')
sys.path.append('C:/Users/PabloUrzúa/sim1pc/pMap')
from misc_funcs import *
from GTP_functions_v1_3 import * 
from pMap_functions_v1 import *

x0=0
y0=0
cant1=20
d1=3
d2=1.2
d3=1.4
cant2=20

xyz,ien=generar_grid_2(x0,y0,cant1,d1,d2,d3,cant2)
xyz=np.array(xyz)
iden_dict2={}
iden_dict2['nodos_almacenamiento']=[]
for i in range(0,len(xyz)):
    if xyz[i,0]>5 and xyz[i,0]<80 and xyz[i,1]>1 and xyz[i,1]<20:
        iden_dict2['nodos_almacenamiento'].append(i)

iden_dict2['nodos_pps']=[20,140,260,380,500,620]
# iden_dict2['nodos_pps']=[460]
iden_dict2['nodos_pllt_vacio']=377
iden_dict2['nodos_recepcion']=5
# plotmap(xyz,ien,iden_dict2,'nodos_almacenamiento',False,False,False,True)


#%%

np.random.seed(43)

dt=1 # s 
tf=3600 # s
print_anim=1
tlist=np.arange(0, tf, step=1)
cant_steps=int(tf/dt+1) # se considera que comienza de t=0 hasta t=tf, entonces son tf/dt+1 steps

sim_params={
'xyz': xyz,
'ien' : ien,
'dt' : dt,
'cant_steps' : cant_steps,
't_picking_per_unit' : 9, # s
'nodos_pllt_vacios' : iden_dict2['nodos_pllt_vacio'],
'nodos_almacenamiento' : iden_dict2['nodos_almacenamiento'],
'nodos_recepcion' : iden_dict2['nodos_recepcion'],
'max_orders_per_pps' : 2,
'iden_dict2' : iden_dict2,

'print_abrir_ordenes' : 0,
'print_generar_skus_a_llamar' : 0,
'print_generar_skus_a_llamar2' : 0,
'print_generar_ot' : 0,
'print_calcular_picking' : 0,
'print_calcular_picking2' : 0,
'print_check_tiempo_picking' : 0,
'print_bot_states' : 0,
'order_print_list' : [1],
}


bot_common_params={
'bot_vel' : 1, # m/s
'tbateria_inicial' : 1200, # s
'tbateria_lim' : 30, # s
'tgiro' : 5, # s
'tiempo_carga_pllt' : 20,
'staging_nodes':[0], # s
'giro_tol' : 0.5, # m
'lim_dist_congestion' : 1, # m
'nodos_bateria' : [3], 
} 

guardar_registro=True
sim1=cSimulation(sim_params,bot_common_params,guardar_registro)


# crear pps
cant_pps=len(iden_dict2['nodos_pps'])
sim1.create_pps(cant_pps,iden_dict2['nodos_pps'])


# crear ordenes
orders={}
skus=[]
import csv
with open('C:/Users/PabloUrzúa/sim1pc/GTP/varios/orders.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row_index, row in enumerate(csvreader):
        # saltarse header
        if row_index == 0:
            pass
        else:
            orden=row[0]
            sku=row[1]
            if sku not in skus : skus.append(sku)
            qty=int(np.round(float(row[2])))
            if orden not in orders:
                orders[orden]={sku:qty}
            else:
                orders[orden][sku]=qty

for key,value in orders.items():
    id=key
    lista=value
    sim1.create_order(id,lista)


# crear pallets
pllt_params={
'tin' : 3,
'sku' : '0',
'qty' : 800,
'state' : 0,
'id_pos' : False, 
'id_almacenamiento' : False
} 

c=0
for i in range(0,len(iden_dict2['nodos_almacenamiento'])):
    if c>=len(skus)-1:
        c=0
    else:
        c+=1
    pllt_params['sku']=skus[c]
    sim1.create_pllt(pllt_params)
    

# crear bots
cant_bots=40
sim1.create_bots_gtp(cant_bots,np.random.choice(len(xyz), size=cant_bots))

# correr simulacion
ordenes_terminadas,ordenes_terminadas_list,cajas_pickeadas=sim1.psim_gtp()
# print(ordenes_terminadas,ordenes_terminadas_list)
print(cajas_pickeadas)

bot_list=sim1.bot_list
order_list=sim1.order_list
bot_list=sim1.bot_list
pllt_list=sim1.pllt_list
pps_list=sim1.pps_list

#%%

ti=0
interval=2
width=np.max(xyz[:,0])+2
height=np.max(xyz[:,1])+2
plot_pllt=False
if print_anim==1 or 0==1:
    plot_anim_gtp(
        sim1.xyz,sim1.bot_list,pllt_list,pps_list,order_list,
        sim1.cant_steps,width,height,False,False,interval,ti,plot_pllt)

#%%

best_path,cost_best_path=btsolve1(sim1.ad,
                                    sim1.con,
                                    80,
                                    73,
                                    sim1.xyz,
                                    False, #full_search
                                    False, #plot
                                    True, #plot_best
                                    False) #print_log

#%%

best_path,cost_best_path=gtp_btsolve(iden_dict2,
                                     True, #plot_best total
                                    sim1.ad,
                                    sim1.con,
                                    3, #nodo inicio
                                    47, #nodo_destino
                                    sim1.xyz,
                                    False, #full_search
                                    False, #plot
                                    False, #plot_best por partes
                                    False) #print_log

#%%









































