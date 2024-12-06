#%%
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.collections import PathCollection
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import json

def pMap(nodes_dict,ien_dict,iden_dict,img_name,width,height,display_grid_lines):

    create_mode_toggle = True
    delete_mode_toggle = False
    pick_mode_toggle = False
    selected_nodes=[]

    def add_node(event):
        # como es necesario MODIFICAR una variable (count) que no esta definida adentro de la funcion
        # es necesario usar nonlocal. Si solo se UTILIZA count y no se MODIFICA, entonces no es necesario usar nonlocal
        # nonlocal es porque count esta definida en una funcion fuera de esta funcion, si count fuera variable global
        # habria que usar global en vez de nonlocal
        nonlocal count
        # print(fig.canvas.toolbar.mode)
        if fig.canvas.toolbar.mode != "zoom rect" and fig.canvas.toolbar.mode != "pan/zoom":
            if create_mode_toggle == True:
                # check si el click ocurre dentro del espacio del plot
                if event.inaxes is not None:
                    x=np.round(event.xdata,1)
                    y=np.round(event.ydata,1)
                    # count es la key de cada nodo en el diccionario de nodos
                    # se agrega nodo al dicc de coordenada de nodos nodes_dict y al dicc
                    # de label de nodos. notar que se extrae la label del nodo del receptor de texto
                    nodes_dict[str(count)]=[x, y]
                    iden_dict[str(count)]=enter_id.get()
                    print(f"Node added at x={x:.2f}, y={y:.2f}")
                    if enter_id.get()=='':
                        color='b'
                    else:
                        color='r'
                    dot=ax.scatter(x, y,picker=True,c=color)  
                    # scatter_dict.append(dot)
                    scatter_dict[str(count)]=dot
                    canvas.draw()
                    count+=1


    def onpick(event):
        # usar type(event.artist) permite ver el tipo de evento
        # print('Tipo de artista',type(event.artist))
        if pick_mode_toggle == True:

            if isinstance(event.artist,PathCollection):
                nonlocal selected_nodes

                key=-1
                for key1, value in scatter_dict.items():
                    if value==event.artist:
                        key=key1
                        break 
                
                if key==-1 : print("error, index no encontrado por alguna razon")
                selected_nodes.append(str(key))
                
                if len(selected_nodes) == 1:
                    print(f"Nodo {key} seleccionado, seleccionar segundo nodo")

                if len(selected_nodes) == 2: 
                    key_node1=selected_nodes[0]
                    key_node2=selected_nodes[1]
                    xyz_node1=nodes_dict[key_node1] 
                    xyz_node2=nodes_dict[key_node2] 
                    connection=ax.plot( [xyz_node1[0],xyz_node2[0]]  ,
                                        [xyz_node1[1],xyz_node2[1]] ,picker=True,c='yellow')
                    canvas.draw()
                    nonlocal count2
                    ien_dict[str(count2)]=selected_nodes
                    plot_connection_dict[str(count2)]=connection
                    count2+=1
                    selected_nodes=[str(key_node2)]
                    print(f"Nodo {key_node2} seleccionado, seleccionar segundo nodo")

        elif delete_mode_toggle == True:
            if isinstance(event.artist,PathCollection):
                delete_key=-1
                for key1, value in scatter_dict.items():
                    if value==event.artist:
                        delete_key=key1
                        break 
                scatter_dict[delete_key].remove()
                
                del nodes_dict[delete_key]
                del iden_dict[delete_key]

                del_keys=[]
                for key1,value in ien_dict.items():
                    for i in range(0,2):
                        if value[i]==delete_key:
                            # print('aaa',plot_connection_dict[key1])
                            plot_connection_dict[key1][0].remove()
                            del_keys.append(key1)

                canvas.draw()
                for i in range(0,len(del_keys)):
                    del ien_dict[del_keys[i]]

                
    def create_mode():
        nonlocal selected_nodes
        nonlocal create_mode_toggle
        nonlocal pick_mode_toggle
        selected_nodes=[]
        create_mode_toggle=not create_mode_toggle
        pick_mode_toggle = False
        # fig.canvas.toolbar.mode = not fig.canvas.toolbar.mode
        print('create mode',create_mode_toggle)



    def delete_mode():
        nonlocal selected_nodes
        nonlocal delete_mode_toggle
        nonlocal create_mode_toggle
        nonlocal pick_mode_toggle
        selected_nodes=[]
        delete_mode_toggle = not delete_mode_toggle
        create_mode_toggle = False
        pick_mode_toggle = False
        print('delete mode',delete_mode_toggle)

    def pick_mode():
        nonlocal selected_nodes
        nonlocal delete_mode_toggle
        nonlocal create_mode_toggle
        nonlocal pick_mode_toggle
        selected_nodes=[]
        pick_mode_toggle = not pick_mode_toggle
        create_mode_toggle = False
        delete_mode_toggle = False 
        print('pick mode',pick_mode_toggle)

    def clear_selection():
        nonlocal selected_nodes
        selected_nodes=[]
        print(f"Seleccion limpia {selected_nodes}")

    window = tk.Tk()
    window.title("pMap")
    window.geometry("1300x700")


    # En tkinter lo primero que se le hace .pack() va a aparecer primero (desde arriba hacia abajo)
    # frame para los botones de arriba
    frame2=tk.Frame(master=window)
    frame2.pack(side=tk.TOP)

    btn1= tk.Button(master=frame2, text="Create Mode", command=create_mode)
    # como todos los botones estan en el mismo frame, puedo usar grid en vez de pack para hacer un grid de botones 
    btn1.grid(row=0, column=0)

    btn3= tk.Button(master=frame2, text="Delete Mode", command=delete_mode)
    btn3.grid(row=0, column=1)

    btn4= tk.Button(master=frame2, text="Pick Mode", command=pick_mode)
    btn4.grid(row=0, column=2)

    btn2= tk.Button(master=frame2, text="Clear selection", command=clear_selection)
    btn2.grid(row=0, column=3)

    enter_id = tk.Entry(master=frame2, width=30)
    lbl_nod_id = tk.Label(master=frame2, text="Identificador nodos:")
    lbl_nod_id.grid(row=0, column=4, sticky="w",padx=5)
    enter_id.grid(row=0, column=5, sticky="e")

    exit_button = tk.Button(master=frame2, text="Exit", command=window.destroy) 
    exit_button.grid(row=0, column=6, sticky="e",padx=100) 


    # frame para el plot
    frame=tk.Frame(master=window)
    frame.pack(fill=tk.BOTH,expand=True)

    fig = Figure(figsize=(4, 4))
    ax = fig.add_subplot(111)
    
    if img_name!=False:
        img = Image.open(img_name)
        # para convertir imagen en blanco y negro
        # img = img.convert("L")
        # para que al hacer zoom no se pierda la forma del plot
        # ax.set_aspect(aspect='auto')
        ax.imshow(img,cmap='gray',extent=[0, width, 0, height]) 
    else:
        ax.set_xlim([0,width])
        ax.set_ylim([0,height])

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH,expand=True)

    toolbar=NavigationToolbar2Tk(canvas)
    toolbar.update()
    toolbar.pack(anchor="w",fill=tk.X)

    canvas.mpl_connect('button_press_event', add_node)
    canvas.mpl_connect('pick_event', onpick)

    # diccionarios para plot
    scatter_dict={}
    plot_connection_dict={}

    # agregar nodos
    for key,value in nodes_dict.items():
        if iden_dict[key]!='nodos_interiores':
            dot=ax.scatter(value[0], value[1],picker=True,c='b')  
            scatter_dict[key]=dot

    # agregar conexiones
    for key,value in ien_dict.items():
        xyz_node1=nodes_dict[value[0]]
        xyz_node2=nodes_dict[value[1]]

        iden_node1=iden_dict[value[0]]
        iden_node2=iden_dict[value[1]]

        if (iden_node1=='nodos_interiores' or iden_node1=='nodos_exteriores') and (iden_node2=='nodos_interiores' or iden_node2== 'nodos_exteriores'):
            if display_grid_lines==True:
                connection=ax.plot( [xyz_node1[0],xyz_node2[0]]  ,
                                    [xyz_node1[1],xyz_node2[1]] , picker=True,c='yellow')
                plot_connection_dict[key]=connection
        else:
            connection=ax.plot( [xyz_node1[0],xyz_node2[0]]  ,
                                [xyz_node1[1],xyz_node2[1]] , picker=True,c='yellow') 
            plot_connection_dict[key]=connection

        

    # count es la key de cada nodo en el diccionario de nodos
    count=0
    # count2 es la key de cada conexion en el diccionario de conexiones ien_dict
    count2=0

    for key,value in nodes_dict.items():
        if int(key)>count: count = int(key)

    for key,value in ien_dict.items():
        if int(key)>count2: count2 = int(key)

    count=count+1
    count2=count2+1

    window.mainloop()

    return nodes_dict, ien_dict, iden_dict


def plotmap_dict(nodes_dict,ien_dict,img_file,width,height):
    
    fig, ax = plt.subplots()  
    
    img = Image.open(img_file)
    ax.imshow(img,cmap='gray',extent=[0, width, 0, height]) 

    for key,value in nodes_dict.items():
        ax.scatter(value[0],value[1],c='b') 
        ax.text(value[0],value[1],str(key),c='r', fontsize=12)

    for key,value in ien_dict.items():
        ax.plot(
            [   nodes_dict[value[0]][0],nodes_dict[value[1]][0]   ],
            [  nodes_dict[value[0]][1],nodes_dict[value[1]][1]  ]
                ,c='yellow')
        
    plt.show()    




# funcion para agregar nodos entre 2 nodos segun espaciamiento, para eso tiene que ir 
# ploteando con sus ids 
def AddNodes(nodes_dict,ien_dict,iden_dict,node1,node2,cant_add,nodes_iden):
    count = 0
    count2 = 0
    for key,value in nodes_dict.items():
        if int(key)>count: count = int(key)

    for key,value in ien_dict.items():
        if int(key)>count2: count2 = int(key)

    count=count+1
    count2=count2+1
    xyz_node1=np.array(nodes_dict[node1]).reshape(1, 2)  
    xyz_node2=np.array(nodes_dict[node2]).reshape(1, 2)
    avance=np.linalg.norm(xyz_node2-xyz_node1)/(cant_add+1)
    # print(count)
    # print(nodes_dict)
    # print(ien_dict)
    for i in range(0,cant_add):
        magnitud=avance*(i+1)
        vector=xyz_node1+(xyz_node2-xyz_node1)/np.linalg.norm(xyz_node2-xyz_node1)*magnitud
        nodes_dict[str(count)]=vector[0].tolist()
        iden_dict[str(count)]=str(nodes_iden)
        # print('nnn',nodes_dict)
        if i==0:
            ien_dict[str(count2)]=[str(node1),str(count)]
            count2+=1
            # print('aaa',ien_dict)
        elif i==cant_add-1:
            ien_dict[str(count2)]=[str(last),str(count)]
            ien_dict[str(count2+1)]=[str(count),str(node2)]
            # print('bbb',ien_dict)
        else:
            ien_dict[str(count2)]=[str(last),str(count)]
            count2+=1
            # print('ccc',ien_dict)
        last=count
        count+=1
        
    # print(nodes_dict)
    # print('ddd',ien_dict)
    del_keys=[]
    for key,value in ien_dict.items():
        if (value[0]==node1 and value[1]==node2) or (value[0]==node2 and value[1]==node1):
            del_keys.append(key)

    for i in range(0,len(del_keys)):
        del ien_dict[del_keys[i]]

    # plotmap_dict(nodes_dict,ien_dict)
    print("NODOS INCLUIDOS")

    return nodes_dict,ien_dict




def generar_grid(x0,y0):
    xyz=[]
    ien=[]
    nodos_interiores=[]
    # cant plts profundidad
    cant1=16
    # ancho pasillos centro a centro plts
    d1=3
    # ancho plt
    d2=1.2
    # largo plt
    d3=1.4
    # cant racks
    cant2=12
    c=0
    x=0
    for i in range(0,cant2):
        for j in range(0,2):
            for k in range(0,cant1):

                # agregar nodos
                if j==0: #sube
                    xyz.append([   x0+x   ,   y0+d2*k   ])
                elif j==1: #baja
                    xyz.append([   x0+x   ,   y0+d2*(cant1-1)-k*d2   ])

                if k!=0 and k!=cant1-1:
                    if i==0 and j==0:
                        pass
                    elif i==cant2-1 and j==1:
                        pass
                    else:
                        nodos_interiores.append(c)

                # conectividad
                # solo en la primera subida no hay que contar laterlamente sino 
                # solamente vertical
                if i==0 and j==0:
                    if k==0:
                        pass
                    else:
                        ien.append([c,c-1])
                else:
                    ien.append([c,c-1])
                    if k!=0: ien.append([c,c-k*2-1])

                c+=1

            if j==0: x+=d3
        x+=d1
    
    cant_total_nodos=len(xyz)
    total_nodos=list(range(cant_total_nodos))
    nodos_exteriores=total_nodos
    for nodo in nodos_interiores:
        nodos_exteriores.remove(nodo)
    
    return xyz,ien,nodos_interiores,nodos_exteriores




def plot_grid(xyz,ien,img,width,height,nodos_interiores,nodos_exteriores):
    
    fig, ax = plt.subplots()  
    
    if img!=False:
        ax.imshow(img, cmap='gray' ,extent=[0, width, 0, height]) 
        ax.set_aspect(aspect='auto')

    for i in range(0,len(xyz)):
        value=xyz[i]
        if i in nodos_interiores:
            ax.scatter(value[0],value[1],c='b',s=20) 
        elif i in nodos_exteriores:
            ax.scatter(value[0],value[1],c='r',s=20) 
        ax.text(value[0],value[1],str(i),c='k', fontsize=12)

    # for i in range(0,len(ien)):
    #     value=ien[i]
    #     ax.plot(
    #         [   xyz[value[0]][0],xyz[value[1]][0]   ],
    #         [  xyz[value[0]][1],xyz[value[1]][1]  ]
    #             ,c='yellow')

    plt.show()   
    


def unir_grid(xyz,ien,nodes_dict,ien_dict,iden_dict,nodos_interiores,nodos_exteriores):
    # id_desde es el id del nodo desde donde empiezo a numerar los nodos de la grid
    id_desde=0
    for key,value in nodes_dict.items():
        if int(key) > id_desde:
            id_desde=int(key)
    id_desde=id_desde+1

    for i in range(0,len(xyz)):
        nodes_dict[str(id_desde+i)]=xyz[i]
        iden_dict[str(id_desde+i)]='nodos_almacenamiento'
        if i in nodos_interiores:
            iden_dict[str(id_desde+i)]='nodos_interiores'
        elif i in nodos_exteriores:
            iden_dict[str(id_desde+i)]='nodos_exteriores'

    id_desde2=0
    for key,value in ien_dict.items():
        if int(key) > id_desde2:
            id_desde2=int(key)
    id_desde2=id_desde2+1

    for i in range(0,len(ien)):
        ien_dict[str(id_desde2+i)]=[str(ien[i][0]+id_desde) , str(ien[i][1]+id_desde)]



    return nodes_dict,ien_dict,iden_dict




def generar_grid_2(x0,y0,cant1,d1,d2,d3,cant2):
    xyz=[]
    ien=[]
    # cant1 = cant profundidad
    # d1=ancho pasillos centro a centro plts
    # d2= dist centro a centro horizontal nodos  
    # d3= dist centro a centro vertical nodos  
    # cant2=cant racks
    c=0
    x=0
    for i in range(0,cant2):
        for j in range(0,2):
            for k in range(0,cant1):

                # agregar nodos
                if j==0: #sube
                    xyz.append([   x0+x   ,   y0+d2*k   ])
                elif j==1: #baja
                    xyz.append([   x0+x   ,   y0+d2*(cant1-1)-k*d2   ])

                if k!=0 and k!=cant1-1:
                    if i==0 and j==0:
                        pass
                    elif i==cant2-1 and j==1:
                        pass

                # conectividad
                # solo en la primera subida no hay que contar laterlamente sino 
                # solamente vertical
                if i==0 and j==0:
                    if k==0:
                        pass
                    else:
                        ien.append([c,c-1])
                else:
                    ien.append([c,c-1])
                    if k!=0: ien.append([c,c-k*2-1])

                c+=1

            if j==0: x+=d3
        x+=d1
    
    return xyz,ien









