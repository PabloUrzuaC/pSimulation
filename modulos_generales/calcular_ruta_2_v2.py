#%%
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random



def plotred(ad,path,xyz,use_xyz,color):
    G = nx.Graph()

    for i in range(0,ad.shape[0]):
        G.add_node(i,pos=(xyz[i]))

    for i in range(0,ad.shape[0]):
        for j in range(0,ad.shape[0]):
            if ad[i,j]!=0:
                G.add_edge(i,j)

    options = {
        "font_size": 10,
        "node_size": 200,
        "edgecolors": "black",
        "linewidths": 1,
        "width": 1,
    }
    
    color_map = [color if np.isin(node,path) else 'gray' for node in G]   

    # plt.figure(figsize=(2,2))
    plt.figure()

    #posicion especifica
    if use_xyz==True:
        pos=nx.get_node_attributes(G,'pos')
    else:
        pos=nx.spring_layout(G, scale=1, seed=42) # posicion random

    nx.draw_networkx(G,pos,**options, node_color=color_map)

    # Set margins for the axes so that nodes aren't clipped
    
    ax = plt.gca()
    ax.margins(0.1)
    plt.axis("off")
    plt.show()


def crear_ad_simple(c1):
    nodo_max=0
    for lista in c1:
        for nd in lista:
            if nd>nodo_max:
                nodo_max=nd
    cant_nodos=nodo_max+1
    # print(cant_nodos)
    ad=np.zeros([cant_nodos,cant_nodos])
    for i in range(0,cant_nodos):
        # print(c1[i][1:])
        for nd in c1[i][1:]:
            if nd!=i:
                ad[c1[i][0],nd]=1
    ad=ad+np.transpose(ad)

    con=[]
    for i in range(0,cant_nodos):
        con.append(i)
        for j in range(0,cant_nodos):
            if ad[i,j]!=0:
                if type(con[i])==list:
                    con[i].append(j)
                else:
                    con[i]=[con[i],j]

    return ad,con




def build_ad_con(xyz,ien):
    cant_nodos=xyz.shape[0]
    ad=np.zeros([cant_nodos,cant_nodos])
    for i in range(0,len(ien)):
        nod1=ien[i][0]
        nod2=ien[i][1]
        xyz1=xyz[nod1]
        xyz2=xyz[nod2]
        dist=np.linalg.norm(xyz2-xyz1)
        ad[nod1,nod2]=dist
    # IEN da la info de que el nodo 1 se une con el nodo2,
    # con el transpose se hace que el nodo2 tambien este unido con el nodo1
    ad=ad+np.transpose(ad)

    # conectividad a partir de matriz de adyacencia
    # formato [nodo_index nodo_destino1 nodo_destino2, etc]
    con=[]
    for i in range(0,cant_nodos):
        con.append(i)
        for j in range(0,cant_nodos):
            if ad[i,j]!=0:
                if type(con[i])==list:
                    con[i].append(j)
                else:
                    con[i]=[con[i],j]

    return ad,con


# CAMINO 1
# cant_nodos=10
# ad=np.zeros([cant_nodos,cant_nodos])
# ad[0,1],ad[1,2],ad[1,3],ad[3,6],ad[3,4],ad[6,4],ad[6,7],ad[4,5]=1,1,1,1,1,1,1,1
# ad=ad+np.transpose(ad)

# CAMINO 2 (RANDOM)
# ad=np.zeros([cant_nodos,cant_nodos])
# for i in range(0,cant_nodos):
#     for j in range(0,i):
#         ad[i,j]=np.random.choice([0, 1],p=[0.8,0.2])
# ad=ad+np.transpose(ad)

# CAMINO 3
# c1_t1=[[0,1],
#      [1,2],
#      [2,3,4],
#      [3],
#      [4,5],
#      [5,6],
#      [6,7],
#      [7,8,9],
#      [8],
#      [9]]
# c1_t2=[[0,1]	,
# [1,	2	,10],
# [2,	3]	,
# [3,	4]	,
# [4,	5]	,
# [5,	6,	7],
# [6,	]	,
# [7,	8]	,
# [8,	9]	,
# [9,	10],
# [10	,1]	]
# c1_t3=[[0,1],[1,2,3],[2,4],[3,4],[4,5],[5,6],[6,7],[7]]

# c1_t4=[[0,1],[1,2],[2,3],[3,6],[4,6,5],[5,1],[6,4,7],[7]]
# xyz4=np.array([[0,4],[4,4],[4,0],[8,0],[8,8],[4,8],[8,4],[12,4]])

# c1=c1_t4
# xyz=xyz4


# TEST
# ad=crear_ad_simple(c1)
# path=np.array([])
# plotred(ad,path,xyz,True,'green')


#%%

# podria hacer una clase "path_solve" que tenga como metodos gtp_btsolve, btsolve1, etc. asi evito tener que poner los mismos parametros
# de input para ambas funciones ya que serian parte del objeto y accederia mediante self.ad, self.con, self.nodo_inicio, etc. no se si vale la pena 

# funcion que evalua si el nodo_inicio y nodo_destino está en zona de almacenamiento. 
# si ambos están, entonces usa un algoritmo simple para resolver la ruta.
# si el nodo_inicio está pero el nodo destino no, usa 

def calcular_nodo_intermedio(nodo_1,nodo_2,con,xyz):
    # print('nodo_1',nodo_1)
    # print('nodo_2',nodo_2)
    # se debe encontrar el nodo intermedio con mismo X que nodo inicio 
    x_in=xyz[nodo_1][0]
    x_des=xyz[nodo_2][0]
    dist_horz_actual=abs(x_des-x_in)
    nodo_actual=nodo_1
    if round(dist_horz_actual,0)==0:
        nodo_intermedio=nodo_1
    else:
        fin=False
        for i in range(0,400):
            opciones=con[nodo_actual][1:]
            # print(f"nodo_actual:{nodo_actual}  opciones:{opciones} dist_horz_actual: {dist_horz_actual}")
            for opcion in opciones: 
                x_opcion=xyz[opcion][0]
                if abs(x_opcion-x_des)<=dist_horz_actual:
                    nodo_actual=opcion
                    dist_horz_actual=abs(x_opcion-x_des)
                    if np.round(abs(x_opcion-x_des),0)==0:
                        nodo_intermedio=opcion
                        fin=True
                        break
            if fin==True: break
    # print('nodo_intermedio',nodo_intermedio)
    return nodo_intermedio

def gtp_btsolve(iden_dict2,plot_best_total,ad,con,nodo_inicio,nodo_destino,xyz,full_search,plot,plot_best,print_log):
    if nodo_inicio in iden_dict2['nodos_pps']:
        for nodo in con[nodo_inicio]:
            if xyz[nodo,0]==xyz[nodo_inicio,0] and xyz[nodo,1]<xyz[nodo_inicio,1]:
                nodo_salida=nodo

        path_parte1,cost_path_parte1=btsolve1(ad,con,nodo_inicio,nodo_salida,xyz,full_search,plot,plot_best,print_log)
        nodo_intermedio=calcular_nodo_intermedio(nodo_salida,nodo_destino,con,xyz)
        path_parte2,cost_path_parte2=btsolve1(ad,con,nodo_salida,nodo_intermedio,xyz,full_search,plot,plot_best,print_log)
        path_parte3,cost_path_parte3=btsolve1(ad,con,nodo_intermedio,nodo_destino,xyz,full_search,plot,plot_best,print_log)
        best_path=path_parte1+path_parte2[1::]+path_parte3[1::]
        cost_best_path=cost_path_parte1+cost_path_parte2+cost_path_parte3

    else:
    # if nodo_inicio in iden_dict2['nodos_almacenamiento'] and nodo_destino in iden_dict2['nodos_almacenamiento']:
        # print(f"caso 1")
        # print('nodo_inicio',nodo_inicio)
        # print('nodo_destino',nodo_destino)
        nodo_intermedio=calcular_nodo_intermedio(nodo_inicio,nodo_destino,con,xyz)
        path_parte1,cost_path_parte1=btsolve1(ad,con,nodo_inicio,nodo_intermedio,xyz,full_search,plot,plot_best,print_log)
        path_parte2,cost_path_parte2=btsolve1(ad,con,nodo_intermedio,nodo_destino,xyz,full_search,plot,plot_best,print_log)
        # se usa [1::] en path parte2 para no incluir nuevamente el nodo intermedio en el path, ya que bt1solve entrega el path incluyendo el nodo de inicio
        best_path=path_parte1+path_parte2[1::] 
        cost_best_path=cost_path_parte1+cost_path_parte2

    # elif nodo_inicio in iden_dict2['nodos_almacenamiento'] and nodo_destino not in iden_dict2['nodos_almacenamiento']:
    #     dist=999999
    #     nodo_mas_cercano=0
    #     for nodo in iden_dict2['nodos_exteriores']:
    #         dist2=np.linalg.norm(xyz[nodo]-xyz[nodo_destino])
    #         if dist2<dist: 
    #             dist=dist2
    #             nodo_mas_cercano=nodo
    #     nodo_intermedio=calcular_nodo_intermedio(nodo_inicio,nodo_mas_cercano,con,xyz)
    #     path_parte1,cost_path_parte1=btsolve1(ad,con,nodo_inicio,nodo_intermedio,xyz,full_search,plot,plot_best,print_log)
    #     path_parte2,cost_path_parte2=btsolve1(ad,con,nodo_intermedio,nodo_mas_cercano,xyz,full_search,plot,plot_best,print_log)
    #     path_parte3,cost_path_parte3=btsolve1(ad,con,nodo_mas_cercano,nodo_destino,xyz,full_search,plot,plot_best,print_log)
    #     best_path=path_parte1+path_parte2[1::]+path_parte3[1::]
    #     cost_best_path=cost_path_parte1+cost_path_parte2+cost_path_parte3

    # elif nodo_inicio not in iden_dict2['nodos_almacenamiento'] and nodo_destino in iden_dict2['nodos_almacenamiento']:
    #     dist=999999
    #     nodo_mas_cercano=0
    #     for nodo in iden_dict2['nodos_exteriores']:
    #         dist2=np.linalg.norm(xyz[nodo]-xyz[nodo_inicio])
    #         if dist2<dist: 
    #             dist=dist2
    #             nodo_mas_cercano=nodo
        
    #     path_parte1,cost_path_parte1=btsolve1(ad,con,nodo_inicio,nodo_mas_cercano,xyz,full_search,plot,plot_best,print_log)
    #     nodo_intermedio=calcular_nodo_intermedio(nodo_mas_cercano,nodo_destino,con,xyz)
    #     path_parte2,cost_path_parte2=btsolve1(ad,con,nodo_mas_cercano,nodo_intermedio,xyz,full_search,plot,plot_best,print_log)
    #     path_parte3,cost_path_parte3=btsolve1(ad,con,nodo_intermedio,nodo_destino,xyz,full_search,plot,plot_best,print_log)
    #     best_path=path_parte1+path_parte2[1::]+path_parte3[1::]
    #     cost_best_path=cost_path_parte1+cost_path_parte2+cost_path_parte3

    # elif nodo_inicio not in iden_dict2['nodos_almacenamiento'] and nodo_destino not in iden_dict2['nodos_almacenamiento']:
    #     best_path,cost_best_path=btsolve1(ad,con,nodo_inicio,nodo_destino,xyz,full_search,plot,plot_best,print_log)

    if plot_best_total==True : plotred(ad,best_path,xyz,True,'blue')
    # print(best_path)
    return best_path,cost_best_path



def btsolve1(ad,con,nodo_inicio,nodo_destino,xyz,full_search,plot,plot_best,print_log):
    cant_nodos=ad.shape[0]
    path=[nodo_inicio]
    path_cost=[]
    best_path=[]
    cost_best_path=0

    # hago una lista suficientemente grande para no tener problemas de falta de indices
    # (un path no deberia tener mas de cant_nodos nodos)

    # pathlist es una LISTA en que la fila i es una LISTA con LISTAS, cada lista tiene un camino que el algoritmo ha hecho hasta el nodo i
    # por ejemplo, la fila 2 (nodo2) de pathlist es una lista que contiene 3 listas, porque se ha llegado al nodo2 en 3 ocasiones por caminos distintos
    # pathlist = [listas_nodo1, listas_nodo2, listas_nodo3, listas_nodo4]
    # listas_nodo2 = [[camino1_hasta_el_nodo2],[camino2_hasta_el_nodo3],[camino2_hasta_el_nodo3]] 

    # chosen es una LISTA en que la fila i es una LISTA con LISTAS. Va de la mano con pathlist, ya que, para cada uno de los paths de pathlist, entrega las opciones que se han elejido
    # las veces que se ha estado en ese path. Continuando con el ejemplo anterior, la fila 2 (nodo2) de chosen es una lista que contiene 3 listas
    # chosen = [chosen_nodo1, chosen_nodo2, chosen_nodo3, chosen_nodo4]
    # chosen_nodo2 = [[nodos_elegidos_cuando_se_ha_estado_en_camino1], [nodos_elegidos_cuando_se_ha_estado_en_camino2], [nodos_elegidos_cuando_se_ha_estado_en_camino3], [[nodos_elegidos_cuando_se_ha_estado_en_camino4]]]
    
    pathlist=[]
    chosen=[]
    ava=[]
    for i in range(0,cant_nodos):
        ava.append([])
        pathlist.append([])
        chosen.append([])

    cant_steps=1000
    for i in range(0,cant_steps):
        # print('BBBBBBBBBBBBBBBBB',best_path)
        # el algoritmo termina cuando se empieza a devolver porque todas
        # las opciones de camino ya fueron evaluadas, entonces len(path)=0
        if len(path)>0: 
            nodo_actual=path[-1]

            opciones=con[nodo_actual][1:]
            # if print_log == True : print('----------------------')
            # if print_log == True : print('STEP',i,'NODO',nodo_actual,'PATH',path,'OPCIONES',opciones)

            # check para ver si ya se llego al nodo de destino
            if nodo_actual==nodo_destino:
                # if print_log == True : print(f"XXXXXXXXXXXXXXXXXXX llegue al nodo_destino")
                if len(best_path)==0:
                    best_path=tuple(path)
                    cost_best_path=sum(path_cost)
                    # if print_log == True : print(f"XXXXXXXXXXXXXXXXXXX es el primer path encontrado, best: {best_path} costo {cost_best_path}")
                    if full_search==False:
                        break
                else:
                    if sum(path_cost) < cost_best_path:
                        best_path=tuple(path)
                        cost_best_path=sum(path_cost)
                        # if print_log == True : print('XXXXXXXXXXXXXXXXXXX este path es mejor, best',best_path)
                    else:
                        pass
            
            # se genera la lista visited2
            if len(pathlist[nodo_actual])==0: 
                visited2=[]
                # if print_log == True : print('sin visitados:',visited2)
            else:
                for i in range(0,len(pathlist[nodo_actual])):
                    pathh=pathlist[nodo_actual][i]
                    if pathh==tuple(path):
                        visited2=chosen[nodo_actual][i]
                        # if print_log == True : print('path nodo',nodo_actual,'es',pathh,'visitados',visited2)


            ############################ 
            # rutina para ordenar las opciones segun la que tiene direccion mas cercana al nodo_destino
            # se calculan vectores DESDE el nodo actual (ese "desde" se traduce en que el vector que define la distancia 
            # entre el nodo actual y el nodo_destino se calcula
            # como xyz[nodo_destino]-xyz[path[-1]] donde xyz[path[-1]] es la posicion actual) a cada opcion y se compara con el vector DESDE el nodo
            # actual al nodo nodo_destino, la opcion que tenga una mayor proyeccion (np.dot(a,b)/np.linalg.norm(a)) es la que apunta mas cerca 
            a=xyz[nodo_destino]-xyz[path[-1]]
            proyecciones=[]
            for opcion in opciones:
                b=xyz[opcion]-xyz[path[-1]]
                proyecciones.append(np.dot(a,b)/np.linalg.norm(a))

            key=np.argsort(proyecciones)
            aux=np.zeros([1,len(opciones)],dtype=int)
            for i in range(0,len(opciones)): 
                aux[0,i] = opciones[key[i]]  

            # el [0] es para que quede de dimension n en vez de 1xn, el [::-1] es para que el arreglo se ordene de mayor a menor
            opciones=aux[0][::-1]
            ##############################

            move=False
            for opcion in opciones: 
                # el opcion not in visited2 evita que se elija un nodo que ya se ha visitado 
                # el opcion not in path evita que se elija un nodo del path (para que no se devuelva)
                if opcion not in visited2 and opcion not in path:

                    existe1=False
                    for i in range(0,len(pathlist[nodo_actual])):
                        pathh=pathlist[nodo_actual][i] 
                        # se detecta si ya se ha estado en el nodo_actual con exactamente el mismo camino actual (path)
                        if pathh==tuple(path):
                            existe1=True
                            chosen[nodo_actual][i].append(opcion)
                            # if print_log == True : print('habia estado en nodo',nodo_actual,'con path:',path)
                            # if print_log == True : print('pathlist:',pathlist)
                            # if print_log == True : print('chosen:',chosen)
                    if existe1==False:
                        pathlist[nodo_actual].append(tuple(path))
                        chosen[nodo_actual].append([opcion])
                        # if print_log == True : print('no habia estado en nodo',nodo_actual,'con path:',path)
                        # if print_log == True : print('se agrega a pathlist:',pathlist)
                        # if print_log == True : print('chosen:',chosen)

                    path_cost.append(int(ad[path[-1],opcion]))
                    # if print_log == True : print('COSTO',path_cost)
                    
                    path.append(opcion)
                    # if print_log == True : print('opcion nod',opcion,'no visit, no path, path:',path)
                    
                    # if plot==True: plotred(ad,path,xyz,True,'red')
                    move=True
                    # si ya se encontro un nodo para avanzar, no es necesario seguir recorriendo las opciones, entonces se hace break al for opcion in opciones
                    break
            
            # si termina el ciclo for opcion in opciones y no se logra avanzar (move=False) entonces se vuelve al nodo anterior, para eso se elimina
            # el ultimo nodo del path. La idea es que con este nuevo path el algoritmo vuelve a evaluar las opciones del nuevo ultimo nodo pero sin
            # avanzar a las opciones que ya ha elegido
            if move==False:
                # se vuelve al nodo anterior
                path=path[:-1]
                # if print_log == True : print('no hay opciones sin visitar, vuelvo a nodo anterior, path:',path)
                path_cost=path_cost[:-1]
                if plot==True: plotred(ad,path,xyz,True,'red')
        else:
            # if print_log == True : print('no quedan nodos por visitar, fin algoritmo')
            break

        
    # print('BBBBBBBBBBBBBBBBB',best_path)
    # print('COSTO',cost_best_path)
    # print('PPPPPPPPPPPPPP',path)
    if plot_best==True : plotred(ad,best_path,xyz,True,'blue')
    # print(cost_best_path)

    return best_path,cost_best_path



# inicio=0
# destino=3
# sj=True
# plot=sj
# plot_best=sj
# print_log=sj
# best_path,cost_best_path=btsolve1(ad,inicio,destino,xyz,False,plot,plot_best,print_log)

#%%

def plot1(xyz,xyzr):    
    plt.figure(figsize=(2,2))
    plt.scatter(xyz[:,0],xyz[:,1], c ="black")
    plt.scatter(xyzr[:,0],xyzr[:,1], c ="red",s=5)
    plt.grid()
    plt.show()


def nodpath_to_ruta(xyz,nodpath,dt,vel,tgiro,print_log,giro_tol):
    cant_dt_giro=tgiro/dt
    avance=dt*vel
    # en cada dt el bot puede avanzar a un nuevo elemento de la ruta
    xyz_inicial=xyz[nodpath[0]]
    ruta=np.array([xyz_inicial])

    continuar=False
    for j in range(0,len(nodpath)-1):
        n1=nodpath[j]
        n2=nodpath[j+1]
        # ndest=nact+1
        xyz1=xyz[n1]
        xyz2=xyz[n2]

        # if print_log == True : print('checkpoint',n1,xyz1,xyz2)

        vect_avance=(xyz2-xyz1)/np.linalg.norm(xyz2-xyz1)*avance
        # if print_log == True : print('vect avance',vect_avance)
        pos=xyz1
        continuar=False
        for i in range(0,200):
            if continuar==False:
                
                # if print_log == True : ('dif',xyz2,pos)
                # if print_log == True : ('norm',np.linalg.norm(xyz2-pos))
                if np.linalg.norm(xyz2-pos) <= avance:
                    # if print_log == True : ('entra')
                    pos=xyz2
                    continuar=True
                else:
                    pos=pos+vect_avance
    
                ruta=np.concatenate((ruta,[pos]),axis=0)
                # plot1(xyz,ruta2)
                # if print_log == True : ('ruta:')
                # if print_log == True : (ruta)
            else:
                # cada vez que llega a un nodo, se agrega tiempo de giro
                # excepto cuando llega al ultimo nodo, por eso el if
                if j!=len(nodpath)-2:
                    nod_siguiente=nodpath[j+2]
                    xyz_nod_siguiente=xyz[nod_siguiente]
                    # solamente se agrega tiempo de giro si el siguiente nodo esta en
                    # un X e Y distinos al nodo anterior al que acabo de llegar 
                    if abs(xyz1[0]-xyz_nod_siguiente[0])>giro_tol and abs(xyz1[1]-xyz_nod_siguiente[1])>giro_tol:
                        for i in range(0,int(cant_dt_giro)):
                            ruta=np.concatenate((ruta,[ruta[-1]]),axis=0)
                
                # si continuar=true entonces se usa break para terminar el for 
                break
    return ruta



# dt=1 #s
# vel=0.5 #m/s
# tgiro=5
# nodpath=[5,1,2,3]

# ruta=nodpath_to_ruta(xyz,nodpath,dt,vel,tgiro,print_log)
# print(ruta)
# plot1(xyz,ruta)