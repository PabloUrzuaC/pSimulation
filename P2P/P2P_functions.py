
import numpy as np
import matplotlib.pyplot as plt
from calcular_ruta_2_v2 import *

# hasta ahora creo que no es necesario usar clases
# para los bots ni palets, ya que en vez podria usar 
# arreglos numpy con la info de id, x, y y state
# pero uso clases igual para aprender a usar las clases
# creo que la ventaja de usar clases es usar herencias 
# ademas parece que el codigo seria mas largo si uso arreglos
class cbot():
    def __init__(self,id,id_pos_actual,xyz_h,bot_params):
        self.id=id
        self.id_pos_actual=id_pos_actual # en realidad es el id del nodo cuando comienza la ruta y no se actualiza hasta que termina la ruta
        self.vel=bot_params['bot_vel']
        self.bateria=bot_params['tbateria']
        self.tbateria_lim=bot_params['tbateria_lim']
        self.tgiro=bot_params['tgiro']
        self.staging_nodes=bot_params['staging_nodes']
        self.tcarga_pllt=bot_params['tcarga_pllt']
        self.giro_tol=bot_params['giro_tol']
        # self.x=x
        # self.y=y 
        # 0=waiting in staging area (without task asigned)
        # 1=moving wo pallet to staging 
        # 2=moving wo pallet to plt zone (task of moving plt already assigned)
        # 3=moving w pallet
        # 4=carga de pllt
        # 5=descarga de pllt
        # 6=camino al cargador
        # 7=cargando bateria
        # 8=asking for pallet
        self.xyz_h=xyz_h
        # notar que no necesito definir este atributo de la clase a partir de un input de
        # __init__ ya que se que siempre que cree un nuevo bot estos atripbutos tendran estos valores
        self.xyz=self.xyz_h[0]
        self.id_destino_ruta=0 
        self.pllt=False
        self.state=0
        cant_steps=xyz_h.shape[0]
        self.state_h=np.zeros([cant_steps,1])
        self.tiempo_carga=False
        self.tiempo_desc=False
        self.idle_time=0
        self.bot_pllts_terminados=0
        self.congestion_time=0
    def __str__(self):
        return f"bot {self.id}"
    def __repr__(self):
        return self.__str__()
    
    # este metodo se usa solo cuando el bot ya tiene una ruta calculada
    def do(self,t,bot_list,log):
        llega=False
        # if log==True : print(f"accion bot {self.id}")
        if self.ruta.shape[0]==1:
            llega=True
            if log==True : print(f"t={t}| bot {self.id} ya esta en el punto de destino de la ruta")
        else:
            congestion=False
            for botx in bot_list:
                if botx.id < self.id and botx.state != 7 and botx.state != 0:
                    if np.linalg.norm(self.xyz-botx.xyz) < 2:
                        congestion=True
                        self.congestion_time+=1
                        # importante el break, si ya se congestiona por 1 bot, no se siguen
                        # revisando los otros bots. si no se coloca el break se va a sumar 1 sg al congestion_time
                        # por cada bot que provoca congestion para un mismo t
                        break 
                        # if log==True : print(f"t={t}| bot {self.id} espera para que pase bot {botx.id}")

            if congestion==False:
                self.ruta_id_actual+=1
                # la accion de avanzar consiste en actualizar el xyz del bot
                self.xyz=self.ruta[self.ruta_id_actual] 
                if log==True : print(f"t={t}| bot {self.id} avanza {self.xyz}")
                if self.ruta_id_actual==self.ruta.shape[0]-1:
                    llega=True
        return llega


    def calcular_ruta(self,t,dt,xyz,ad,con,log):
        if log==True : print(f"t={t}| se calcula ruta del bot {self.id}, id inicio: {self.id_pos_actual}, id destino: {self.id_destino_ruta}")
        best_path,cost_best_path=btsolve1(ad,con,int(self.id_pos_actual),int(self.id_destino_ruta),xyz,False,False,False,False)
        if log==True : print(f"t={t}| RUTA DE NODOS CALCULADA {best_path}")
        self.ruta=nodpath_to_ruta(xyz,best_path,dt,self.vel,self.tgiro,False,self.giro_tol)
        self.ruta_id_actual=0
        self.t_inicio_ruta=t
        
        # if log==True : print(f"t={t}| RUTA XYZ CALCULADA {best_path}")

            
    def check_carga(self,t,log):
        self.tiempo_carga+=-1
        if self.tiempo_carga==0:
            if log==True : print(f"bot {self.id} termina de cargar {self.pllt}")
            self.state=3
            self.pllt.pllt_t_picked=t

    def check_desc(self,t,log):
        desc=False
        self.tiempo_desc+=-1
        if self.tiempo_desc==0:
            # queda pendiente el cambio de state, porque depende de si hay pllts 
            # en espera que se le pueda asignar al bot, retorna llega=True para que el 
            # sistema lo mande a do0 (para ver si hay pallets pendientes)
            if log==True : print(f"t={t}| bot {self.id} termina de descargar pllt {self.pllt.id}")
            self.pllt=False
            desc=True
        return desc
    
    def cargar(self,t):
        cargado=False
        self.bateria+=1
        if self.bateria >= self.tbateria:
            cargado=True
        return cargado

def CreateBots_P2P(cant_bots,xyz,cant_steps,bot_params):
    bot_list=[]  
    staging_nodes=bot_params['staging_nodes']
    id_pos_actual=np.random.choice(staging_nodes)
    for i in range(0,cant_bots):
        xyz_h=np.zeros([cant_steps,2])
        xyz_h[0]=np.array([xyz[id_pos_actual]])
        bot=cbot(i,id_pos_actual,xyz_h,bot_params)
        bot_list.append(bot)
    return bot_list

class cpllt():
    def __init__(self,pllt_list,inid,desid,tin,tf):
        self.inid=inid
        self.desid=desid
        self.tin=tin
        # False=no ingresado
        # 0=wait wo bot assigned 
        # 1=wait w bot assigned
        # 2=in movement
        self.bot=False
        self.pllt_t_picked=tf
        self.id=len(pllt_list)+1
    def __str__(self):
        return f"pllt {self.id}"
    def __repr__(self):
        return self.__str__()

# bot entra a system_assign_tasks() cuando tiene state 0,8 y lo que puede pasar es que si no se le asigna ningun pllt quede con state 0 u 8, si se le asigna
# pllt queda con state 2
def system_assign_tasks(t,dt,xyz,ad,con,bot_list,waiting_pllts,log):
    # pllts_asignados=[]

    # # se recorren los pllts en espera
    # for i in range(0,len(waiting_pllts)):
    #     pllt=waiting_pllts[i]
    #     xyz_pallet=xyz[pllt.inid]
    #     # se recorren los bots disponibles para ver cual es el mas indicado
    #     dist=99999999999
    #     hay_bot=False
    #     for bot1 in bot_list:
    #         if bot1.state==0 or bot1.state==8:
    #             dist1=np.linalg.norm(xyz_pallet-bot1.xyz)
    #             if dist1<dist:
    #                 dist=dist1
    #                 hay_bot=True
    #                 best_bot=bot1
    #                 print(f"TTTTTTTTT t={t}| pllt {pllt.id} MEJOR asignado a bot {best_bot.id}")
                    
    #     if hay_bot==True:
    #         print(f"t={t}| pllt {pllt.id} asignado a bot {best_bot.id}")
    #         best_bot.pllt=pllt
    #         best_bot.state=2
    #         best_bot.id_destino_ruta=pllt.inid
    #         best_bot.calcular_ruta(t)
    #         pllts_asignados.append(pllt)
            
    for bot1 in bot_list:
        hay_pllt=False
        if bot1.state==0 or bot1.state==8:
            dist=99999999999
            for i in range(0,len(waiting_pllts)):
                pllt=waiting_pllts[i]
                xyz_pallet=xyz[pllt.inid]
                dist1=np.linalg.norm(xyz_pallet-bot1.xyz)
                if dist1<dist:
                    dist=dist1
                    hay_pllt=True
                    best_pllt=pllt
                    # if log==True : print(f"t={t}| pllt {best_pllt.id} MEJOR asignado a bot {bot1.id}")                
        
        # check si al bot se le asigno un pllt
        if hay_pllt==True:
            waiting_pllts.remove(best_pllt)
            if log==True : print(f"t={t}| pllt {best_pllt.id} asignado a bot {bot1.id} waiting_pllts: {waiting_pllts}")            
            bot1.pllt=best_pllt
            bot1.state=2
            bot1.id_destino_ruta=best_pllt.inid
            bot1.calcular_ruta(t,dt,xyz,ad,con,False)

    return waiting_pllts


def psim(xyz,ad,con,bot_list,pllt_list,log,cant_steps,dt):
    cant_pllts=len(pllt_list)
    cant_bots=len(bot_list)
    waiting_pllts=[]
    pllts_ingresados=[]
    pllts_terminados=0
    t_termino_tareas=False
    t=0
    # se recorren los cant_steps setps de tiempo dt 
    # Importante: se va aumentando el tiempo de dt en dt porque al
    # final del for se hace t+=dt. En cada step del for se resuelve qué acción hacen 
    # los bots en el t actual (t=t0). Dicha acción dura dt segundos, ya que en la proxima
    # iteracion for, el step de tiempo t=t0+dt, se vuelve a calcular la acción de los bots con 
    # duración dt. La función nodpath_to_ruta() es importante ya que determina cuanto avanza el bot dada su 
    # velocidad y la duración dt de la acción, entonces el avance en cada step de tiempo es avance=dt*velocidad
    for t in range(0,cant_steps):
        # if log==True : print('--------------------')
        # if log==True : print(f"t={t}")

        # print('--------------------')
        # print(f"t={t}")

        # check pllts que ingresan
        for p in range(0,cant_pllts):
            pllt=pllt_list[p]
            if pllt.tin==t:
                waiting_pllts.append(pllt)
                if log==True : print(f"t={t}| pllt {pllt.id} ingresa, waiting_pllts: {waiting_pllts}")
                pllts_ingresados.append(pllt)
                # if pllts_ingresados == cant_pllts:
                    # if log==True : print(f"t={t}| ingresa el ultimo pllt")
        # if log==True : print(f"t={t}| {pllts_ingresados}")
        
        # perform bot actions
        for i in range(0,cant_bots):
            bot=bot_list[i]
            # if log==True : print(f"t={t}| Veo bot {bot.id}, state: {bot.state}")

            if bot.state==0:
                if bot.bateria>bot.tbateria_lim:
                    waiting_pllts = system_assign_tasks(t,dt,xyz,ad,con,bot_list,waiting_pllts,False)
                    if bot.state == 2: 
                        # orden para que el bot haga su accion de tiempo=t
                        bot.do(t,bot_list,log)
                    elif bot.state==0:
                        bot.idle_time+=dt
                        # if log==True : print(f"t={t}| waiting_pllts vacia: {waiting_pllts}, bot {bot.id} SIGUE en espera")

                else:
                    if log==True : print(f"t={t}| bot {bot.id} descargado, bateria: {bot.bateria}")
                    bot.state=6
                    bot.id_destino_ruta=5
                    bot.calcular_ruta(t,dt,xyz,ad,con,False)
                    bot.do(t,bot_list,log)

            elif bot.state==1:
                llega=bot.do(t,bot_list,log)
                # si bot llega a stagging, entonces se revisa si hay pllt para asignar
                # notar que mas eficiente seria que durante el camino del bot hacia el stagging
                # este consultando si hay pllts disponibles para asignarle.
                # para asignarle una tarea al bot cuando va 
                # camino a stagging tendria que incluir un nodo en el grafo para que pueda
                # calcular la ruta desde donde sea que se encuentre
                if llega == True:
                    # ojo solo se actualiza id_pos_actual cuando el bot llega al nodo de destino de la ruta
                    # entonces el nombre de la variable es confuso pq no es tan actual 
                    bot.id_pos_actual=bot.id_destino_ruta
                    bot.state=0
            # `       if log==True : print(f"t={t}| bot {bot.id} llega a staging")
                    waiting_pllts = system_assign_tasks(t,dt,xyz,ad,con,bot_list,waiting_pllts,False)
                    if bot.state == 2: 
                        # orden para que el bot haga su accion de tiempo=t
                        bot.do(t,bot_list,log)
                    elif bot.state==0:
                        # if log==True : print(f"t={t}| waiting_pllts vacia: {waiting_pllts}, bot {bot.id} SIGUE en espera")
                        pass
            
            elif bot.state==2:
                llega=bot.do(t,bot_list,log)
                if llega==True:
                    bot.id_pos_actual=bot.id_destino_ruta
                    bot.state=4
                    bot.tiempo_carga=bot.tcarga_pllt
                    bot.id_destino_ruta=bot.pllt.desid
                    if log==True : print(f"t={t}| bot {bot.id} llega al pllt asignado, ahora bot tiene state: {bot.state}")
                    bot.calcular_ruta(t,dt,xyz,ad,con,False)

            elif bot.state==3:
                llega=bot.do(t,bot_list,log)
                if llega==True:
                    bot.id_pos_actual=bot.id_destino_ruta
                    bot.state=5
                    bot.tiempo_desc=bot.tcarga_pllt  

            elif bot.state==4:
                bot.check_carga(t,False)

            elif bot.state==5:
                desc=bot.check_desc(t,False)
                if desc == True:
                    pllts_terminados+=1
                    bot.bot_pllts_terminados+=1
                    if pllts_terminados == cant_pllts:
                        # print(f"XXXXXXXXXX t={t}| ULTIMO PALLET TERMINADO XXXXXXXXXXX")
                        t_termino_tareas=t
                    if bot.bateria>bot.tbateria_lim:
                        bot.state=8
                        waiting_pllts = system_assign_tasks(t,dt,xyz,ad,con,bot_list,waiting_pllts,False)
                        if bot.state == 2: 
                            # orden para que el bot haga su accion de tiempo=t
                            bot.do(t,bot_list,log)
                        elif bot.state==0:
                            if log==True : print(f"t={t}| waiting_pllts vacia: {waiting_pllts}, bot {bot.id} SIGUE en espera")
                        elif bot.state==8:
                            if log==True : print(f"t={t}| no hay pllts en espera, bot: {bot.id} a stagging")
                            bot.state=1
                            bot.id_destino_ruta=np.random.choice(bot.staging_nodes)
                            bot.calcular_ruta(t,dt,xyz,ad,con,False)
                    else:
                        if log==True : print(f"t={t}| bot {bot.id} descargado, bateria: {bot.bateria}")
                        bot.state=6
                        bot.id_destino_ruta=5 
                        bot.calcular_ruta(t,dt,xyz,ad,con,False)

            elif bot.state==6:
                llega=bot.do(t,bot_list,log)
                if llega==True:
                    bot.id_pos_actual=bot.id_destino_ruta
                    bot.state=7
                    if log==True : print(f"t={t}| bot {bot.id} llega a cargador")

            elif bot.state==7:
                cargado=bot.cargar(t)
                if cargado == True:
                    if log==True : print(f"bot {bot.id} termina de cargarse, bateria: {bot.bateria}")
                    bot.state=8
                    waiting_pllts = system_assign_tasks(t,dt,xyz,ad,con,bot_list,waiting_pllts,False)
                    if bot.state == 2: 
                        # orden para que el bot haga su accion de tiempo=t
                        bot.do(t,bot_list,log)
                    elif bot.state==0:
                        if log==True : print(f"t={t}| waiting_pllts vacia: {waiting_pllts}, bot {bot.id} SIGUE en espera")
                    elif bot.state==8:
                        if log==True : print(f"t={t}| no hay pllts en espera, bot: {bot.id} a stagging")
                        bot.state=1
                        bot.id_destino_ruta=np.random.choice(bot.staging_nodes) 
                        bot.calcular_ruta(t,dt,xyz,ad,con,False)

            else:
                if log==True : print("bot unknown state")
        
            bot.xyz_h[t] = bot.xyz
            bot.state_h[t] = bot.state
            if bot.state != 7 and bot.state != 0:
                bot.bateria+=-1/4
            # if bot.id == 0:    
                # if log==True : print(f"AAAAAAAAA bot {bot.id} state {bot.state} bateria {bot.bateria}")
            

        t+=dt

    total_congestion_time=0
    for j in range(0,cant_bots):
        total_congestion_time+=bot_list[j].congestion_time

    total_idle_time=0
    for j in range(0,cant_bots):
        total_idle_time+=bot_list[j].idle_time

    if t_termino_tareas != False:
        print(f"En tiempo {t_termino_tareas} se terminan las tareas, pallets_terminados:{pllts_terminados}/{cant_pllts}")
    else:
        print(f"No se terminan las tareas, pallets_terminados:{pllts_terminados}/{cant_pllts}")

    # print('TERMINADO')
    return t_termino_tareas, total_congestion_time, total_idle_time, pllts_terminados




def AddFlujo(pllt_list,iden_dict2,cant,tf,inicio,destino):
    for p in range(0,cant):
        inid=np.random.choice(iden_dict2[inicio])
        desid=np.random.choice(iden_dict2[destino])
        pllt_list.append(  cpllt(pllt_list,inid,desid,0,tf)  )

    return pllt_list















