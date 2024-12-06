import numpy as np
import matplotlib.pyplot as plt

def DictToArray(nodes_dict,ien_dict,iden_dict):
    cant_nodos=len(nodes_dict)
    xyz=np.zeros([cant_nodos,2],dtype=float)
    ien=[]

    c=0
    for key,value in nodes_dict.items():
        xyz[c]=np.array(  nodes_dict[key]  ).reshape(1, 2)  
        c+=1

    for key,value in ien_dict.items():
        nod1=value[0]
        nod2=value[1]
        c=0
        for key1,value1 in nodes_dict.items():
            if key1==nod1:
                nod1_index=c
            if key1==nod2:
                nod2_index=c
            c+=1
        ien.append([  int(nod1_index)  ,  int(nod2_index) ])
    
    iden_dict2={}
    values=[]
    for key,value in iden_dict.items():
        if value not in values: 
            values.append(value)
            iden_dict2[value] = []
        
        c=0
        for key1,value1 in iden_dict.items():
            if key==key1:
                iden_dict2[value].append(c)
            c+=1

    iden_dict2['nodos_almacenamiento']=iden_dict2['nodos_interiores']+iden_dict2['nodos_exteriores']

    return xyz,ien,iden_dict2






def plotmap(xyz,ien,iden_dict2,tipo_nodo,img,width,height,label):
    
    fig, ax = plt.subplots()  
    
    if img!=False:
        ax.imshow(img, cmap='gray' ,extent=[0, width, 0, height]) 
        ax.set_aspect(aspect='auto')

    # for i in range(0,len(ien)):
    #     value=ien[i]
    #     ax.plot(
    #         [   xyz[value[0]][0],xyz[value[1]][0]   ],
    #         [  xyz[value[0]][1],xyz[value[1]][1]  ]
    #             ,c='yellow')

    for i in range(0,xyz.shape[0]):
        value=xyz[i]
        if i in iden_dict2[tipo_nodo]:
            ax.scatter(value[0],value[1],c='b',s=20) 
        else:
            ax.scatter(value[0],value[1],c='gray',s=10) 
            
        if label==True : ax.text(value[0]-0.5,value[1]+0.5,str(i),c='r', fontsize=6)

    plt.show()   


def CalcularInfoPallet(pllt_list,cant_steps):
    lista_nodos_con_pllt = []
    for pllt in pllt_list:
        if pllt.inid not in lista_nodos_con_pllt:
            lista_nodos_con_pllt.append(pllt.inid)

    lista_nodos_con_pllt=np.unique(lista_nodos_con_pllt)

    cant1=len(lista_nodos_con_pllt)
    info_pllt=np.zeros([cant_steps,cant1+1])
    for t in range(0,cant_steps):
        info_pllt[t,0]=t
        for pllt in pllt_list:
            if t >= pllt.tin and t<pllt.pllt_t_picked:
                # [0] pq where retorna tupla y +1 porque la primera columna tiene los tiempos t
                index=np.where(lista_nodos_con_pllt == pllt.inid)[0]+1 
                info_pllt[t,index]+=1
    return info_pllt,lista_nodos_con_pllt


import matplotlib
# from matplotlib import animation
from matplotlib.animation import FuncAnimation

def PlotAnim_P2P(xyz,pllt_list,bot_list,cant_steps,height,width,img,save):
    
    info_pllt,lista_nodos_con_pllt=CalcularInfoPallet(pllt_list,cant_steps)

    fig, axis = plt.subplots()

    axis.scatter(xyz[:,0],xyz[:,1], c ="black", s=0.1)

    xmax=xyz[:,0].max()
    ymax=xyz[:,1].max()
    anim_text = axis.text(width,height,'', fontsize=12, color='red')

    if img != False:
        axis.imshow(img,cmap='gray',extent=[0, width, 0, height]) 

    axis.set_aspect(aspect='auto')

    ax1_list=[] # lista para plotear contador de pallets
    for i in range(0,len(lista_nodos_con_pllt)):
        nod_id=int(lista_nodos_con_pllt[i])
        ax1_list.append(axis.text(xyz[nod_id,0],xyz[nod_id,1],'', fontsize=12, color='blue'))

    ax2_list=[] # lista para plotear bots
    for i in range(0,len(bot_list)):
        ax2_list.append(axis.plot([],[],'o',markersize=5,color='red'))


    marker_colors = {
        0: 'b',  
        1: 'b',
        2: 'b',
        3: 'r',
        4: 'orange',
        5: 'orange',
        6: 'b',
        7: 'green'
    }


    def update(frame):
        anim_text.set_text(str(frame))

        # plot bots
        for i in range(0,len(bot_list)):
            ax2=ax2_list[i][0]
            bot=bot_list[i]

            color=marker_colors[bot.state_h[frame][0]]
            ax2.set_mfc(color)
            ax2.set_mec(color)

            ax2.set_data([bot.xyz_h[frame,0]],[bot.xyz_h[frame,1]])

        # plot contador de pallets, el for i es para recorrer los nodos
        # que en algun momento tienen pllt
        for i in range(0,len(lista_nodos_con_pllt)):
            ax1=ax1_list[i]
            # i+1 pq la primera columna de info_pllt tiene el tiempo t
            cant_pllts=int(info_pllt[frame,i+1]) 
            if cant_pllts>0:
                ax1.set_text(str(cant_pllts))  
            else:
                ax1.set_text('')  
        return 

    # axis.set_xlim([0,width])
    # axis.set_ylim([0,height])
    # axis.grid()


    animation = FuncAnimation(
                        fig=fig,
                        func=update,
                        frames=cant_steps,
                        interval=50,
                    ) 
    
    if save==True:
        matplotlib.rcParams['animation.ffmpeg_path'] =  "C:\\Users\\PabloUrzúa\\Downloads\\ffmpeg-7.1-essentials_build\\ffmpeg-7.1-essentials_build\\bin\\ffmpeg.exe"
        writer = matplotlib.animation.FFMpegWriter()
        animation.save("animation2.mp4")
    else:
        plt.show() 




def PlotAnim_OP(xyz,bot_list,picker_list,cant_steps,interval1):

    fig, axis = plt.subplots()

    axis.scatter(xyz[:,0],xyz[:,1], c ="black")
    anim_text = axis.text(10,10,'', fontsize=12, color='red')


    ax2_list=[] # lista para plotear bots
    for i in range(0,len(bot_list)):
        ax2_list.append(axis.plot([],[],'o',markersize=10,color='red'))

    ax3_list=[] # lista para plotear pickers
    for i in range(0,len(picker_list)):
        ax3_list.append(axis.plot([],[],'D',markersize=10,color='blue'))


    picker_marker_colors = {
        0: 'gray',  
        1: 'pink',
        2: 'cyan'
    }

    bot_marker_colors = {
        0: 'gray',  
        1: 'b',
        2: 'orange',
        3: 'b',
        4: 'orange',
        5: 'r',
        6: 'b',
        7: 'green',
        8: 'b'
    }

    t_inicio=0

    def update(frame):
        frame=frame+t_inicio
        anim_text.set_text(str(frame))
        
        # bots
        for i in range(0,len(bot_list)):
            ax2=ax2_list[i][0]
            bot=bot_list[i]

            color=bot_marker_colors[bot.state_h[frame][0]]
            # color='b'
            ax2.set_mfc(color)
            ax2.set_mec(color)

            ax2.set_data([bot.xyz_h[frame,0]],[bot.xyz_h[frame,1]])
        
        # pickers
        for i in range(0,len(picker_list)):
            ax3=ax3_list[i][0]
            picker=picker_list[i]

            color=picker_marker_colors[picker.state_h[frame][0]]
            # color='r'
            ax3.set_mfc(color)
            ax3.set_mec(color)

            if picker.state_h[frame][0] == 2:
                ax3.set_data([picker.xyz_h[frame,0]+1],[picker.xyz_h[frame,1]])
            else:
                ax3.set_data([picker.xyz_h[frame,0]],[picker.xyz_h[frame,1]])

        return 

    axis.set_xlim([0, 13])
    axis.set_ylim([0, 9])
    # axis.grid()


    animation = FuncAnimation(
                        fig=fig,
                        func=update,
                        frames=cant_steps-t_inicio,
                        interval=interval1,
                    ) 

    plt.show()




from PIL import Image
def plot_anim_gtp(xyz,bot_list,pllt_list,pps_list,order_list,cant_steps,width,height,img_file,save,interval1,t_inicio,plot_pllt):
    
    fig, axis = plt.subplots()

    # plot nodos con scatter
    # axis.scatter(xyz[:,0],xyz[:,1], c ="black", s=0.1)

    # plot nodos pps
    for i in range(0,len(pps_list)):
        axis.scatter(xyz[pps_list[i].id_nodo,0],xyz[pps_list[i].id_nodo,1], facecolors='none', edgecolors='k', marker="s", linewidths=1.5)
        pass

    # plot etiquetas en los nodos
    # for i in range(0,xyz.shape[0]):
    #     value=xyz[i]
    #     axis.text(value[0],value[1],str(i),c='r', fontsize=12)

    for pps in pps_list:
        for nodo_cola in pps.nodos_cola:
            axis.scatter(xyz[nodo_cola,0],xyz[nodo_cola,1], facecolors='none', edgecolors='b', marker="s", linewidths=1.5)

    xmax=xyz[:,0].max()
    ymax=xyz[:,1].max()
    anim_text = axis.text(xmax,ymax,'', fontsize=12, color='red')

    if img_file != False:
        img = Image.open(img_file)
        axis.imshow(img,cmap='gray',extent=[0, width, 0, height]) 
        # axis.imshow(img ,extent=[0, width, 0, height]) 
    else:
        axis.set_xlim([0,width])
        axis.set_ylim([0,height])

    axis.set_aspect(aspect='auto')

    # plotear pllts
    if plot_pllt==True:
        ax3_list=[] 
        for i in range(0,len(pllt_list)):
            ax3_list.append(axis.plot([],[],'s',markersize=4,color='peru'))

    # plotear bots 
    # agrego los bots dps de los plts para que en el grafico los bots se vean sobre los plts
    ax2_list=[]
    for i in range(0,len(bot_list)):
        ax2_list.append(axis.plot([],[],'o',markersize=5))


    bot_marker_colors = {
        0: 'gray',  
        1: 'b',
        2: 'orange',
        3: 'r',
        4: 'm',
        5: 'r',
        6: 'r',
        7: 'orange',
        8: 'green',
        9: 'gray',
        10: 'r'
    }


    def update(frame):
        frame+=t_inicio
        anim_text.set_text(str(frame))


        # plot bots
        for i in range(0,len(bot_list)):
            ax2=ax2_list[i][0]
            bot=bot_list[i]

            bot_state_actual=bot.state_h[frame][0]
            if bot_state_actual not in list(bot_marker_colors):
                color='yellow'
            else:
                color=bot_marker_colors[bot_state_actual]

            ax2.set_mfc(color)
            ax2.set_mec(color)
            ax2.set_data([bot.xyz_h[frame,0]],[bot.xyz_h[frame,1]])


        # plot pllts
        if plot_pllt==True:
            for i in range(0,len(pllt_list)):
                ax3=ax3_list[i][0]
                pllt=pllt_list[i]
                if pllt.state_h[frame][0]==0:
                    ax3.set_data([xyz[pllt.id_almacenamiento][0]],[xyz[pllt.id_almacenamiento][1]])
                else:
                    ax3.set_data([],[])

        for order in order_list:
            if order.pick_h[frame]!=0:
                print(f"t={frame}| picking {order} sku {order.pick_h[frame][0]} qty {order.pick_h[frame][1]} pps {order.pick_h[frame][2]}")



        return 


    # axis.grid()


    animation = FuncAnimation(
                        fig=fig,
                        func=update,
                        frames=cant_steps-t_inicio,
                        interval=interval1,
                    ) 
    
    if save==True:
        matplotlib.rcParams['animation.ffmpeg_path'] =  "C:\\Users\\PabloUrzúa\\Downloads\\ffmpeg-7.1-essentials_build\\ffmpeg-7.1-essentials_build\\bin\\ffmpeg.exe"
        writer = matplotlib.animation.FFMpegWriter()
        animation.save("animation2.mp4")
    else:
        plt.show() 