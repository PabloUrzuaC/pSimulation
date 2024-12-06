
#%%
import numpy as np
import matplotlib.pyplot as plt

from misc_funcs import *
from OP_functions import *
from calcular_ruta_2_v2 import *

dt=1 # s
tf=3 # s
cant_steps=int(tf/dt+1) # se considera que comienza de t=0 hasta t=tf, entonces son tf/dt+1 steps

xyz=np.array([[0,4],[4,4],[4,0],[8,0],[8,8],[4,8],[8,4],[12,4]])
ien=[[0,1],[1,2],[2,3],[3,6],[6,7],[6,4],[4,5],[5,1]]
ad,con=build_ad_con(xyz,ien)

# create bots
cant_bots=2
bot_params={
'bot_vel' : 0.6, # m/s
'tbateria' : 1200, # s
'tbateria_lim' : 30, # s
'tgiro' : 5, # s
'staging_nodes':[0], # s
'giro_tol' : 0.5, # m
'lim_dist_congestion' : 2, # m
'nodos_bateria' : [3], 
} 
bot_list=CreateBots_OP(cant_bots,xyz,cant_steps,bot_params)


# create pickers
picker_params={
'picker_vel' : 0.6, # m/s
'tgiro' : 0, # s
'staging_nodes':[0], # s
'giro_tol' : 0.5 # m
} 
cant_pickers=1
picker_list=[]
id_nodo_actual=1
for i in range(0,cant_pickers):
    mover_params={'id' : i,
                    'id_nodo_actual' : id_nodo_actual,
                    'xyz' : xyz,
                    'cant_steps' : cant_steps
                    }
    picker_list.append(  cPicker(mover_params,picker_params)  )


# create orders
order_list=[]
tp=6
 
order_list.append(cOrder(0,3,[2,4,5],[tp,tp,tp]))
order_list.append(cOrder(1,10,[3,4,2],[tp,tp,tp]))
# for i in range(0,20):
#     tingreso=np.random.randint(0,500)
#     order_path=np.random.randint(0,cant_nodos,5).tolist()
#     picking_times=np.ones([1,len(order_path)])*tp
#     order_list.append(cOrder(i,tingreso,order_path,picking_times[0]))




print_log=True

sim_params={'xyz': xyz,
            'ad' : ad,
            'con': con,
            'bot_list' : bot_list,
            'picker_list' : picker_list,
            'cant_steps' : cant_steps,
            'order_list' : order_list,
            'dt' : dt,
            'order_list' : order_list}

psim_op(sim_params,print_log)



#%%

# import matplotlib
matplotlib.use('TkAgg')
PlotAnim_OP(xyz,bot_list,picker_list,cant_steps,120)

