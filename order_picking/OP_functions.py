
import numpy as np
import matplotlib.pyplot as plt

# from misc_funcs import *
from calcular_ruta_2_v2 import *


class cMover():
    def __init__(self,mover_params):
        self.id=mover_params['id']
        # en realidad es el id del nodo cuando comienza la ruta y no se actualiza hasta que termina la ruta
        self.id_nodo_actual=mover_params['id_nodo_actual']
        xyz=mover_params['xyz']
        cant_steps=mover_params['cant_steps']
        # notar que no necesito definir este atributo de la clase a partir de un input de
        # __init__ ya que se que siempre que cree un nuevo bot estos atripbutos tendran estos valores
        self.xyz_h=np.zeros([cant_steps,2])
        self.xyz_h[0]=np.array([xyz[self.id_nodo_actual]])
        self.xyz=self.xyz_h[0]
        self.id_destino_ruta=0
        self.order=False
        self.state_h=np.zeros([cant_steps,1])
    def __str__(self):
        return f"Mover {self.id}"
    def __repr__(self):
        return self.__str__()
    
    # este metodo se usa solo cuando el bot ya tiene una ruta calculada
    def do(self,t,sim_params,print_log):

        bot_list=sim_params['bot_list']
        picker_list=sim_params['picker_list']

        llega=False
        # if print_log == True : print(f"t={t}| accion {self}")
        # caso en que ya se encuentra en el punto de destino de la ruta
        if self.ruta.shape[0]==1:
            llega=True
            if print_log == True : print(f"t={t}| {self} ya esta en el punto de destino de la ruta, nodo {self.id_nodo_actual}")
        else:
            congestion=False
            if isinstance(self,cBot): congestion,prioridad=self.CheckCongestion(t,bot_list,picker_list) 

            if congestion==False:
                self.ruta_id_actual+=1
                # la accion de avanzar consiste en actualizar el xyz del bot
                self.xyz=self.ruta[self.ruta_id_actual] 
                if print_log == True : print(f"t={t}| {self} avanza {self.xyz}")
                if self.ruta_id_actual==self.ruta.shape[0]-1:
                    llega=True
            else:
                if print_log == True : print(f"{self} espera para que pase {prioridad}")

        if llega==True:
            self.id_nodo_actual=self.id_destino_ruta
            self.StateChange(t,sim_params,print_log) 


    def calcular_ruta(self,t,sim_params,id_destino_ruta,print_log):

        self.id_destino_ruta=id_destino_ruta

        xyz=sim_params['xyz']
        ad=sim_params['ad']
        con=sim_params['con']
        dt=sim_params['dt']

        if print_log == True : print(f"t={t}| se calcula ruta del {self}, id inicio: {self.id_nodo_actual}, id destino: {self.id_destino_ruta}")
        best_path,cost_best_path=btsolve1(ad,con,int(self.id_nodo_actual),int(self.id_destino_ruta),xyz,False,False,False,False)
        self.ruta=nodpath_to_ruta(xyz,best_path,dt,self.vel,self.tgiro,print_log,self.giro_tol)
        # se resetea el id del nodo actual en la ruta
        self.ruta_id_actual=0
        
        if print_log == True : print(f"t={t}| RUTA CALCULADA {best_path}")

        

class cPicker(cMover):
    # 0=esperando en algun nodo
    # 1=en camino a bot
    # 2=pickeando

  # def __init__(self,id,id_nodo_actual,cant_steps,xyz):
    def __init__(self,mover_params,picker_params):
        super().__init__(mover_params)

        self.vel=picker_params['picker_vel']
        self.tgiro=picker_params['tgiro']
        self.giro_tol=picker_params['giro_tol']
        self.staging_nodes=picker_params['staging_nodes']
        
        self.state=0
        self.bot=False
        self.time_picking=False
        
    def StateChange(self,t,sim_params,print_log): 
        if self.state==0:
            self.state==1
        elif self.state==1:
            self.state=2 


    def __str__(self):
        return f"picker {self.id}"
    def __repr__(self):
        return self.__str__()


class cBot(cMover):

    # 0=en stagging inicio sin task
    # 1=en camino hacia nodo picking 
    # 2=en nodo picking, sin picker
    # 3=en camino hacia nodo despacho (recorrido terminado de la orden)
    # 4=en nodo picking con picker asignado que aun no llega
    # 5=en nodo picking con picker pickeando
    # 6=camino al cargador
    # 7=cargando
    # 8=en camino a stagging
    # 9=bot en nodo despacho

    def __init__(self,mover_params,bot_params):
        super().__init__(mover_params)

        self.vel=bot_params['bot_vel']
        self.tbateria=bot_params['tbateria']
        self.tbateria_lim=bot_params['tbateria_lim']
        self.tgiro=bot_params['tgiro']
        self.staging_nodes=bot_params['staging_nodes']
        self.giro_tol=bot_params['giro_tol']
        self.lim_dist_congestion=bot_params['lim_dist_congestion']
        self.nodos_bateria = bot_params['nodos_bateria']

        self.state=0
        self.picker=False
        self.index_ruta_picking=False
        self.order=False

    def StateChange(self,t,sim_params,print_log):
        if self.state==1:
            self.state=2
        elif self.state==3:
            self.state=9
        elif self.state==5:
            if self.index_ruta_picking == len(self.order.order_path):
                self.state=3
                id_destino_ruta=self.staging_nodes
                self.calcular_ruta(t,sim_params,id_destino_ruta,print_log)
        elif self.state==6:
            self.state=7
        elif self.state==8:
            self.state=0

    def CheckCongestion(self,t,bot_list,picker_list):
        congestion=False
        prioridad=False
        for botx in bot_list:
            if np.linalg.norm(self.xyz-botx.xyz) < self.lim_dist_congestion:
                if botx.state in [2,4,5,7] and self.id_destino_ruta == botx.id_nodo_actual:
                    congestion=True
                    prioridad=botx
                    break # uso break pq basta que haya 1 congestion para no tener que seguir el for
                elif botx.state in [1,3,6,8] and botx.id < self.id:
                    congestion=True
                    break
                elif botx.state in [0]:
                    # no hay congestion
                    pass

        for picker in picker_list:
            if np.linalg.norm(self.xyz-picker.xyz) < self.lim_dist_congestion:
                if picker.state in [0,2]:
                    # no hay congestion
                    pass
                elif picker.state in [1]:
                    congestion=True
                    prioridad=picker
                    break
                    
        return congestion, prioridad

    def __str__(self):
        return f"bot {self.id}"
    
    def __repr__(self):
        return self.__str__()


class cOrder():
    def __init__(self,id,t_ingreso,order_path,picking_times):
        self.id=id
        self.t_ingreso=t_ingreso
        # order path es una lista con id's de nodos, el primer id es la primera 
        # ubicacion del picking, el penultimo 
        # id es la ultima ubicacion de picking y el ultimo id es el nodo de despacho
        # aca se podria pasar el order_path por una funcion que reordene los nodos del picking
        # de forma que el camino del picking sea eficiente
        self.order_path=order_path
        self.picking_times=picking_times
    def __str__(self):
        return f"order {self.id}"
    def __repr__(self):
        return self.__str__()
    
def CreateBots_OP(cant_bots,xyz,cant_steps,bot_params):
    bot_list=[]  
    staging_nodes=bot_params['staging_nodes']
    id_nodo_actual=np.random.choice(staging_nodes)
    for i in range(0,cant_bots):
        mover_params={'id' : i,
                      'id_nodo_actual' : id_nodo_actual,
                      'xyz' : xyz,
                      'cant_steps' : cant_steps
                      }
        bot=cBot(mover_params,bot_params)
        bot_list.append(bot)
    return bot_list





# bot entra a system_assign_task() cuando tiene state 0
def bot_assign_task(t,bot,waiting_orders,sim_params,print_log):
    if len(waiting_orders) > 0:
        bot.order=waiting_orders[0]
        waiting_orders=waiting_orders[1:]
        bot.state=1
        if print_log == True : print(f"t={t}| Se asigna {bot.order} a {bot}, waiting_orders={waiting_orders}")
        bot.index_ruta_picking=0
        id_destino_ruta=bot.order.order_path[bot.index_ruta_picking]
        bot.calcular_ruta(t,sim_params,id_destino_ruta,print_log)
    return waiting_orders

def BondPickerBot(t,bot,picker,sim_params,print_log):
    bot.picker=picker
    picker.bot=bot
    id_destino_ruta=bot.id_nodo_actual
    picker.calcular_ruta(t,sim_params,id_destino_ruta,print_log)
    if picker.id_nodo_actual != bot.id_nodo_actual:
        bot.state=4
        picker.state=1
        id_destino_ruta=bot.order.order_path[bot.index_ruta_picking]
        picker.calcular_ruta(t,sim_params,id_destino_ruta,print_log)
    else:
        picker.state=2
        bot.state=5



def picker_assign_tasks(t,sim_params,print_log):
    
    bot_list=sim_params['bot_list']
    picker_list=sim_params['picker_list']

    bot_list_s2=[]
    for bot in bot_list:
        if bot.state==2: bot_list_s2.append(bot)
    
    picker_list_s0=[]
    for picker in picker_list:
        if picker.state==0: picker_list_s0.append(picker)

    if len(picker_list_s0)>0 and len(bot_list_s2)>0:
        cant_pickers_s0=len(picker_list_s0)
        dist=np.zeros([len(bot_list_s2),len(picker_list_s0)])        
        for i in range(0,len(bot_list_s2)):
            bot=bot_list_s2[i]
            for j in range(0,len(picker_list_s0)):
                picker=picker_list_s0[j]
                dist[i,j]=np.linalg.norm(picker.xyz-bot.xyz)

        max=np.max(dist)
        lista_pickers_asignados=[]
        lista_bots_asignados=[]
        for i in range(0,99):
            bot_index,picker_index=np.unravel_index(dist.argmin(), dist.shape)
            picker=picker_list_s0[picker_index]
            bot=bot_list_s2[bot_index]
            if picker not in lista_pickers_asignados and bot not in lista_bots_asignados:
                BondPickerBot(t,bot,picker,sim_params,print_log)
                dist[bot_index,:]=10*max
                dist[:,picker_index]=10*max
                lista_pickers_asignados.append(picker)
                lista_bots_asignados.append(bot)
                if len(lista_pickers_asignados) == cant_pickers_s0:
                    break
        



def check_picking(t,bot,picker,order,sim_params,print_log):
    t_total_picking=order.picking_times[bot.index_ruta_picking]
    if picker.time_picking == t_total_picking:
        picker.state=0
        picker.bot=False
        # IMPORTANTE: reiniciar tiempo picking del picker para que en su proximo picking empiece con tiempo picking = 0
        picker.time_picking=0 
        # check si bot le quedan ubicaciones para hacer picking o si ya termino y debe ir a despacho
        if bot.index_ruta_picking+1 == len(order.order_path):
            bot.state=3 
            id_destino_ruta=order.order_path[-1]
            bot.calcular_ruta(t,sim_params,id_destino_ruta,print_log)
        else:
            bot.index_ruta_picking+=1
            bot.state=1
            id_destino_ruta=order.order_path[bot.index_ruta_picking]
            bot.calcular_ruta(t,sim_params,id_destino_ruta,print_log)
    else:
        picker.time_picking+=sim_params['dt']
        # if print_log == True : print(f"t={t}| {picker} pickeando en {bot} con tiempo {picker.time_picking} de {t_total_picking}")
        





def psim_op(sim_params,print_log):
    waiting_orders=[]
    ordenes_ingresadas=[]
    ordenes_terminadas=0

    cant_steps=sim_params['cant_steps']
    order_list=sim_params['order_list']
    bot_list=sim_params['bot_list']
    picker_list=sim_params['picker_list']
    dt=sim_params['dt']

    t=0
    for t in range(0,cant_steps):
        if print_log == True : print('--------------------')
        if print_log == True : print(f"t={t}")


        # check orders que ingresan
        cant_orders=len(order_list)
        for o in range(0,cant_orders):
            order=order_list[o]  
            if order.t_ingreso==t:
                waiting_orders.append(order)
                if print_log == True : print(f"t={t}| orden {order.id} ingresa, waiting_orders: {waiting_orders}")
                ordenes_ingresadas.append(order)


        for bot in bot_list:

            if bot.state == 0:
                if bot.tbateria>bot.tbateria_lim:
                    waiting_orders = bot_assign_task(t,bot,waiting_orders,sim_params,print_log)
                    if bot.state==1:
                        bot.do(t,sim_params,print_log)
                    else:
                        if print_log == True : print(f"t={t}| {bot} sigue esperando en stagging")
                else:
                    if print_log == True : print(f"t={t}| {bot} descargado, bateria: {bot.tbateria}")
                    bot.state=6
                    id_destino_ruta=bot.nodos_bateria
                    bot.calcular_ruta(t,sim_params,id_destino_ruta,print_log)
                    bot.do(t,sim_params,print_log)

            elif bot.state==1:
                bot.do(t,sim_params,print_log)
                if bot.state==2:
                    if print_log == True : print(f"t={t}| {bot} llega al nodo {bot.id_nodo_actual}")
                    picker_assign_tasks(t,sim_params,print_log)       

            elif bot.state==2:
                picker_assign_tasks(t,sim_params,print_log)
                if bot.state==4:
                    if print_log == True : print(f"t={t}| Se asigna {bot.picker} a {bot} que esta en nodo {bot.id_nodo_actual}")
                if bot.state==2:
                    if print_log == True : print(f"t={t}| {bot} sigue esperando picker en nodo {bot.id_nodo_actual}")
                
            elif bot.state==3:
                bot.do(t,sim_params,print_log)

            elif bot.state==4:
                if print_log == True : print(f"t={t}| {bot} sigue en el nodo {bot.id_nodo_actual} esperando picker")

            elif bot.state==5:
                picker=bot.picker
                order=bot.order
                check_picking(t,bot,picker,order,sim_params,print_log)

            elif bot.state==6:
                bot.do(t,sim_params,print_log)
                if bot.state==7:
                    if print_log == True : print(f"t={t}| {bot} llega a cargador")

            elif bot.state==7:
                bot.tbateria+=10
                # if print_log == True : print(f"t={t}| {bot} cargandose, bateria: {bot.tbateria}")
                if bot.tbateria >= bot.tbateria:
                    if print_log == True : print(f"t={t}| {bot} termina de cargarse, bateria: {bot.tbateria}, se dirige a staging")
                    bot.state=8
                    id_destino_ruta=np.random.choice(bot.staging_nodes)
                    bot.calcular_ruta(t,sim_params,id_destino_ruta,print_log)

            elif bot.state==8:
                bot.do(t,sim_params,print_log)
                if bot.state==0:
                    if print_log == True : print(f"t={t}| {bot} llega a staging")
            
            elif bot.state==9:
                if print_log == True : print(f"t={t}| {bot} llega al nodo de despacho {bot.id_nodo_actual}")
                if bot.id_nodo_actual == 0:
                    bot.state=0
                else:
                    bot.state=8
                    id_destino_ruta=np.random.choice(bot.staging_nodes)
                    bot.calcular_ruta(t,sim_params,id_destino_ruta,print_log)

            bot.xyz_h[t] = bot.xyz
            bot.state_h[t] = bot.state
            if bot.state not in [0,7,2]:
                bot.tbateria+=-1

        for picker in picker_list:
            if picker.state == 0:
                picker_assign_tasks(t,sim_params,print_log)
                if picker.state==1:
                    picker.do(t,sim_params,print_log)

            elif picker.state==1:
                bot=picker.bot
                picker.do(t,sim_params,print_log)     
                if picker.state==2:
                    bot.state=5
                    if print_log == True : print(f"t={t}| {picker} llega a nodo {picker.id_nodo_actual} para pickear en {picker.bot}")
 
            elif picker.state==2:
                # el check de picking lo hago en el bot.state==5 del for de los bots
                pass
                # bot=picker.bot
                # order=bot.order
                

            picker.xyz_h[t] = picker.xyz
            picker.state_h[t] = picker.state

        # if print_log == True : print('bbb')
        t+=dt