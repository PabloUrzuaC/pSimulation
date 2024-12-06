#%%
from pMap_functions_v1 import *
import matplotlib
matplotlib.use('Agg')

# USAR UN MAPA YA HECHO PARA EDITARLO
# f = open('gtp_test2_2_nodes_dict.txt', 'r')
# nodes_dict = json.loads(f.read())
# f = open('gtp_test2_2_ien_dict.txt', 'r')
# ien_dict = json.loads(f.read())
# f = open('gtp_test2_2_iden_dict.txt', 'r')
# iden_dict = json.loads(f.read())

# nodes_dict={}
# ien_dict={}
# iden_dict={}

img_name="gtp1.png"
width=64
height=38
nodes_dict, ien_dict, iden_dict=pMap(nodes_dict,ien_dict,iden_dict,img_name,width,height,False)

# iden_dict debe tener:
# 'nodos_pllt_vacio'
# 'nodos_recepcion'
# 'nodos_pps'
# estos 3 se hacen automaticamente al hacer la grilla
# 'nodos_almacenamiento'
# 'nodos_interiores'
# 'nodos_exteriores'

#%%

matplotlib.use('TkAgg')
plotmap_dict(nodes_dict,ien_dict,"gtp1.png",width,height)

#%%

node1='9'
node2='10'
cant_add=4
nodes_iden="nodos_recepcion"
nodes_dict,ien_dict=AddNodes(nodes_dict,ien_dict,iden_dict,node1,node2,cant_add,nodes_iden)

#%%

matplotlib.use('TkAgg')
xyz,ien,nodos_interiores,nodos_exteriores=generar_grid(5.5,4.7)
plot_grid(xyz,ien,False,0,0,nodos_interiores,nodos_exteriores)

#%%

nodes_dict,ien_dict,iden_dict=unir_grid(xyz,ien,nodes_dict,ien_dict,iden_dict,nodos_interiores,nodos_exteriores)
plotmap_dict(nodes_dict,ien_dict,"gtp1.png",width,height)

#%%

f = open('gtp_test2_2_nodes_dict.txt', 'w+')
f.write(json.dumps(nodes_dict))
f.close()

g = open('gtp_test2_2_ien_dict.txt', 'w+')
g.write(json.dumps(ien_dict))
g.close()

h = open('gtp_test2_2_iden_dict.txt', 'w+')
h.write(json.dumps(iden_dict))
h.close()


