
import numpy as np
import matplotlib.pyplot as plt

from misc_funcs import *
from calcular_ruta_2_v2 import *
from GTP_classes_v1_1 import *

# estudiar si es conveniente que la clase cMover pertenezca a su vez a una clase "simulacion"
# para que herede los parametros de la simulacion que son comunes a todos los bots por ejemplo
# de forma que los bots tambien hereden de simulacion y puedan sacar de ahi los parametros
# comunes a todos los bots. quizas asi el codigo corre mas rapido porque cada bot no tendria que
# "cargar" con tantos parametros


class cSimulation():

    def __init__(self,sim_params,bot_common_params,guardar_registro):

        self.guardar_registro=guardar_registro

        # sim params
        self.xyz = sim_params['xyz']
        self.ien = sim_params['ien']
        self.iden_dict2 = sim_params['iden_dict2']
        self.dt = sim_params['dt']
        self.cant_steps = sim_params['cant_steps']
        self.t_picking_per_unit = sim_params['t_picking_per_unit']
        self.nodos_pllt_vacios = sim_params['nodos_pllt_vacios']
        self.nodos_almacenamiento = sim_params['nodos_almacenamiento']
        self.nodos_recepcion = sim_params['nodos_recepcion']
        self.max_orders_per_pps = sim_params['max_orders_per_pps']

        # sim params prints
        self.print_abrir_ordenes = sim_params['print_abrir_ordenes']
        self.print_generar_skus_a_llamar = sim_params['print_generar_skus_a_llamar']
        self.print_generar_skus_a_llamar2 = sim_params['print_generar_skus_a_llamar2']
        self.print_generar_ot = sim_params['print_generar_ot']
        self.print_calcular_picking = sim_params['print_calcular_picking']
        self.print_calcular_picking2 = sim_params['print_calcular_picking2']
        self.print_check_tiempo_picking = sim_params['print_check_tiempo_picking']
        self.print_bot_states = sim_params['print_bot_states']
        self.order_print_list = sim_params['order_print_list']

        # bot_common_params
        self.bot_vel=bot_common_params['bot_vel']
        self.tbateria_inicial=bot_common_params['tbateria_inicial']
        self.tbateria_lim=bot_common_params['tbateria_lim']
        self.tgiro=bot_common_params['tgiro']
        self.tiempo_carga_pllt = bot_common_params['tiempo_carga_pllt']
        self.staging_nodes=bot_common_params['staging_nodes']
        self.giro_tol=bot_common_params['giro_tol']
        self.lim_dist_congestion=bot_common_params['lim_dist_congestion']
        self.nodos_bateria = bot_common_params['nodos_bateria']

        # stock tiene estructura {  'id sku': [pllt1,pllt2,etc.]  }
        self.stock={}
        self.waiting_pllts=[]
        self.waiting_orders=[]
        self.t=0
        self.bot_list=[]
        self.pllt_list=[]
        self.pps_list=[]
        self.order_list=[]
        self.nodos_ocupados=[]
        self.skus_llamados=[]
        self.seguir=True
        # como al comienzo de la simulacion no hay skus a llamar, comienza con los skus a llamar terminados
        self.skus_a_llamar_terminados=True

        self.ad,self.con=build_ad_con(self.xyz,self.ien)


    def create_bots_gtp(self,cant_bots,lista_nodos):
        for i in range(0,cant_bots):
            if len(lista_nodos)==cant_bots:
                nodo=lista_nodos[i]
            else:
                nodo=0
            bot=cBot(nodo,self)
            bot.id=len(self.bot_list)
            self.bot_list.append(bot)            

    def create_pllt(self,pllt_params):
        pllt=cPllt(pllt_params,self)
        pllt.id=len(self.pllt_list)
        self.pllt_list.append(pllt)
        if pllt.state==2:
            # podria incluir funcion para que los pllts se agreguen a waiting pllts cuando 
            # en un determinado tiempo de ingreso (pllt.tin)
            self.waiting_pllts.append(pllt)
            pllt.id_pos=np.random.choice(self.nodos_recepcion)
            # print(f"se agrega {pllt} waiting pllts: {self.waiting_pllts}")
        elif pllt.state==0:

            # se le asigna un nodo en almacenamiento
            hay_espacio=False
            for nodo in self.nodos_almacenamiento:
                if nodo not in self.nodos_ocupados:
                    pllt.id_almacenamiento=nodo
                    pllt.id_pos=nodo
                    self.nodos_ocupados.append(nodo)
                    hay_espacio=True
                    # print("NODOS OCUPADOS",self.nodos_ocupados)
                    break
            if hay_espacio==False: 
                print(f"NO HAY ESPACIO DE ALMACENAMIENTO PARA {pllt}")

            # se actualiza el stock
            sku_existente=False
            for key,value in self.stock.items():
                if key==pllt.sku: 
                    self.stock[pllt.sku].append(pllt)
                    sku_existente=True
                    break
            if sku_existente==False: 
                self.stock[pllt.sku] = [pllt]

    def create_pps(self,cant_pps,lista_id_nodos):
        for i in range(0,cant_pps):
            pps=cPps(lista_id_nodos[i])
            pps.id=len(self.pps_list)
            self.pps_list.append(pps)
            cant_nodos_fila_cola=4     
            cant_nodos_cola_pps=9
            nodo_actual=pps.id_nodo
            cant_nodos_fila_actual=0
            cant_nodos_agregados=0

            hacia_la_der=True
            for k in range(0,100):
                if cant_nodos_agregados<cant_nodos_cola_pps:
                    if cant_nodos_fila_actual<cant_nodos_fila_cola:
                        # añadir nodo en direccion horizontal
                        for nodo in self.con[nodo_actual]:
                            if hacia_la_der==True:
                                # criterio para armar la cola hacia la derecha de la pps
                                if self.xyz[nodo,0]>self.xyz[nodo_actual,0] and round(self.xyz[nodo,1],1)==round(self.xyz[nodo_actual,1],1):
                                    pps.nodos_cola.append(nodo)
                                    nodo_actual=nodo
                                    cant_nodos_agregados+=1
                                    cant_nodos_fila_actual+=1
                                    break
                            else:
                                # criterio para armar la cola hacia la izquierda de la pps
                                if self.xyz[nodo,0]<self.xyz[nodo_actual,0] and round(self.xyz[nodo,1],1)==round(self.xyz[nodo_actual,1],1):
                                    pps.nodos_cola.append(nodo)
                                    nodo_actual=nodo
                                    cant_nodos_agregados+=1
                                    cant_nodos_fila_actual+=1
                                    break
                            
                    if cant_nodos_fila_actual==cant_nodos_fila_cola:
                        # añadir nodo hacia abajo
                        for nodo in self.con[nodo_actual]:
                            # criterio para armar la cola hacia abajo
                            if round(self.xyz[nodo,0],1)==round(self.xyz[nodo_actual,0],1) and self.xyz[nodo,1]<self.xyz[nodo_actual,1]:
                                pps.nodos_cola.append(nodo)
                                nodo_actual=nodo
                                cant_nodos_agregados+=1
                                hacia_la_der= not hacia_la_der
                                cant_nodos_fila_actual=1
                                break
                    
                else: break

            pps.state_nodos_cola=[0]*len(pps.nodos_cola)


    def create_order(self,id,lista):
        order1=cOrder_gtp(id,lista,self)
        self.order_list.append(order1)
        self.waiting_orders.append(order1)


    # tienda -> orden (es mas general)
    # se llama a esta funcion cuando hay al menos 1 pps sin orden (tienda)
    # (cuando una orden termina de pickear sus skus, la orden se cierra y la pps queda sin esa orden)
    # funcion que ve las tiendas abiertas actualmente y de alguna forma
    # elige cual conviene abrir en cada pps
    # una pps puede tener mas de una tienda
    def abrir_ordenes(self):
        # if self.print_abrir_ordenes == True : print(f"------------ abrir_ordenes ---------------------")
        se_abre_order=False
        for pps in self.pps_list:
            # se abren ordenes en la pps hasta que no se cumpla este if
            if len(pps.orders) < self.max_orders_per_pps:
                for order in self.order_list:
                    if order.state==0: 
                        if len(pps.orders) < self.max_orders_per_pps:
                            pps.orders.append(order)
                            order.pps=pps
                            # la pps puede estar en picking, finalizar una orden y llamar a abrir_ordenes,
                            # en ese caso, no se cambia el state de la pps a 1 pq ya esta en picking
                            if pps.state!=3:
                                pps.state=1
                            order.state=1
                            self.waiting_orders.remove(order)
                            se_abre_order=True    
                            # if self.print_abrir_ordenes == True : print(f"t={self.t}| se abre la {order} en la {pps}")                    
                        else:
                            break

        # if self.print_abrir_ordenes == True : print(f"--------------------------------------------------")
        # basta que se abra una tienda para que se actualice la lista de skus a llamar
        return se_abre_order

    # MUY IMPORTANTE: tener en cuenta cuando se llama esta funcion, ya que permite entender
    # como funciona el "sistema". La funcion es llamada en los siguientes casos:
    # -luego de abrir_ordenes solamente si efectivamente se abre una orden
    # un sku entra a la lista de skus a llamar solamente si el sku esta en stock
    # puede ser que las ordenes pidan una qty de sku mayor a la disponible en stock
    def generar_skus_a_llamar(self):
        # if self.print_generar_skus_a_llamar == True or self.print_generar_skus_a_llamar2 == True: print(f"------------ skus_a_llamar ---------------------")
        # skus a llamar tiene key=sku value=lista con ordenes que piden dicho sku
        # skus a llamar = {'sku1' : [orden1, orden3, orden6], 'sku2' : [orden5, orden1, orden9]}
        self.skus_a_llamar={}
        
        for pps in self.pps_list:
            for order in pps.orders:
                for key in order.lista:
                    # requisitos para que sku entre a lista de skus a llamar:
                    # que el sku este en el stock de almacenaje
                    # que el sku no haya sido llamado antes (skus_llamados)
                    # que la qty que se pide del sku sea >0
                    
                    order_qty=order.lista[key]-order.lista_picked[key]

                    if key in self.stock and key not in self.skus_llamados and order_qty>0:
                        if key not in self.skus_a_llamar:
                            self.skus_a_llamar[key] = [order]
                            # if self.print_generar_skus_a_llamar == True: print(f"t={self.t}| se agrega el sku {key}, skus_a_llamar: {self.skus_a_llamar}")
                        else:
                            self.skus_a_llamar[key].append(order)
                            # if self.print_generar_skus_a_llamar == True: print(f"t={self.t}| se agrega la {order} al sku {key}, skus_a_llamar: {self.skus_a_llamar}")


        if len(self.skus_a_llamar)>0:
            self.skus_a_llamar=sorted(self.skus_a_llamar.items(), key=lambda item: len(item[1]), reverse=True)
            self.skus_a_llamar=dict(self.skus_a_llamar)
            self.index_skus_a_llamar=0
            self.skus_a_llamar_terminados=False
            # if self.print_generar_skus_a_llamar2 == True: print(f"t={self.t}| se genera nueva lista de skus a llamar {self.skus_a_llamar}")

        # if self.print_generar_skus_a_llamar == True: print(f"--------------------------------------------------")




    def elegir_pps(self,bot):
        # print('aaa',bot.recorrido_pps)
        # inicio de reordenar recorrido segun distancia PPS
        # es un algoritmo simple para evaluar el orden en que se visitan las pps, la idea es comenzar por la mas cercana
        # a la posicion actual del bot e ir recorriendo las pps hasta la mas lejana 

        # primero calculo la pps mas lejana a la posicion actual del bot
        # nuevo_recorrido_pps=[]
        # dist_pps_mas_lejana=0
        # pps_mas_lejana=0
        # for pps in bot.recorrido_pps:
        #     dist=np.linalg.norm( self.xyz[pps.id_nodo]-self.xyz[bot.nodo_actual] )
        #     if dist > dist_pps_mas_lejana:
        #         dist_pps_mas_lejana = dist
        #         pps_mas_lejana=pps

        # # print(f"pps mas lejana {pps_mas_lejana}")
        # # ahora calculo la pps mas lejana a la pps calculada antes, de forma que sera donde comienza el recorrido de pps
        # dist_pps_mas_lejana2=0
        # pps_comenzar=None
        # for pps in bot.recorrido_pps:
        #     dist=np.linalg.norm( self.xyz[pps_mas_lejana.id_nodo]-self.xyz[pps.id_nodo] )
        #     if dist >= dist_pps_mas_lejana2:
        #         dist_pps_mas_lejana2 = dist
        #         pps_comenzar=pps
        # # print(f"pps comenzar {pps_comenzar}")
        # # ahora calculo la pps mas cercana a la pps donde comienzo y asi sucesivamente hasta llegar a la mas lejana
        # nuevo_recorrido_pps.append(pps_comenzar)
        # cant_pps_visitar=len(bot.recorrido_pps)-1
        # for i in range(0,cant_pps_visitar):
        #     pps_siguiente=None
        #     dist_pps_mas_cercana=999999
        #     for pps in bot.recorrido_pps:
        #         if pps not in nuevo_recorrido_pps:
        #             dist=np.linalg.norm( self.xyz[nuevo_recorrido_pps[-1].id_nodo]-self.xyz[pps.id_nodo] )
        #             if dist<dist_pps_mas_cercana:
        #                 pps_siguiente=pps
        #                 dist_pps_mas_cercana=dist

        #     nuevo_recorrido_pps.append(pps_siguiente)
        # bot.recorrido_pps=nuevo_recorrido_pps
        # fin reordenamiento recorido pps por distancia

        # inicio reordenamiento recorrido pps por ocupacion de la pps
        lista_ocupacion=[]
        for pps in bot.recorrido_pps:
            ocupacion=0
            for state in pps.state_nodos_cola:
                if state!=0 : ocupacion+=1
            lista_ocupacion.append(ocupacion)

        sorted_indices = sorted(range(len(bot.recorrido_pps)), key=lambda i: lista_ocupacion[i])
        nuevo_recorrido_pps = [bot.recorrido_pps[i] for i in sorted_indices]
        # print(lista_ocupacion)
        # print(bot.recorrido_pps)
        # print(nuevo_recorrido_pps)
        # fin reordenamiento recorrido pps por ocupacion de la pps

        # ahora se selecciona la siguiente pps del recorrido de pps del bot, para eso se ve cual 
        # pps esta disponible
        # print('bbbb',nuevo_recorrido_pps)
        bot.pps_elegida=None 
        for i in range(0,len(nuevo_recorrido_pps)):  
            pps=nuevo_recorrido_pps[i] 
            # print(f"{bot}, pps {pps} con state {pps.state}") 
            if pps.state==1: # caso pps libre y SIN NODOS EN LA COLA 
                # print('entraaaaaaa')
                bot.pps_elegida=pps
                bot.nodo_asignado_pps=None
                bot.state=3
                pps.state=2
                # for bot in self.bot_list:
                    # print(bot.nodo_actual,bot.xyz,self.xyz[bot.nodo_actual])
                    # if bot.nodo_actual == pps.id_nodo:
                        # print(self.t,pps,bot,bot.nodo_actual,bot.xyz,'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                        # bot1=self.bot_list[6]
                        # print(bot1.nodo_actual,bot1.xyz)
                # print(f"XXXXXXXXXXXXXXXXXXXXXXXXXX {self.t} {pps} {bot}")
                break
            else: # caso pps ya esta reservada o con bots esperando en su cola
                # print(self.t, pps.state_nodos_cola)
                # print(f"{bot} con state {bot.state} entra, {pps}") 
                # se recorren los nodos de la cola de la pps
                for j in range(0,len(pps.nodos_cola)):
                    if pps.state_nodos_cola[j]==0: # encontramos un nodo libre en la cola
                        # se reserva el nodo de la cola (state=1) para que no sea
                        # ocupado mientras el bot esta en camino a ese nodo
                        pps.state_nodos_cola[j]=1
                        bot.pps_elegida=pps
                        bot.nodo_asignado_pps = pps.nodos_cola[j]   
                        bot.state=3.2
                        # print(f"{bot}, pps {pps} con state {pps.state} nodo asigado {bot.nodo_asignado_pps}")
                        break
                # si al terminar de recorrer los nodos de la cola se eligio algun nodo
                # entonces ya se eligio una pps y se deja de recorrer las pps (break para el primer for)
                if bot.pps_elegida!=None: break    
        
        if bot.pps_elegida==None:
            # si no encuentra pps (pps_elegida=None) y bot estaba con state 3.1, entonces se mantiene con 3.1
            bot.state=3.1
            # # si no encuentra pps y bot estaba en estacion en picking, entonces queda con state 3.6
            # elif bot.state==4:
            #     bot.state=3.6



        # else:
            
        #     cant_queue_list=[]
        #     for pps in recorrido_pps:
        #         cant_queue_list.append(pps.cant_queue)
        #     print(recorrido_pps)
        #     print(cant_queue_list)
        #     sorted_indices = sorted(range(len(recorrido_pps)), key=lambda i: cant_queue_list[i])
        #     nuevo_recorrido_pps = [recorrido_pps[i] for i in sorted_indices]
        #     bot_elegido.recorrido_pps = nuevo_recorrido_pps

        #     recorrido_nodos=[]
        #     for pps in nuevo_recorrido_pps:
        #         recorrido_nodos.append(pps.id_nodo)
        #     bot_elegido.recorrido_nodos = recorrido_nodos

    # se usa esta funcion cuando un bot termina de pickear y no tiene ninguna pps donde ir pq 
    # estan ocupadas (la funcion se llama en check_tiempo_picking)
    # def calcular_nodo_espera(self,bot):
    #     ocupacion_pps=[0]*len(bot.recorrido_pps)
    #     # se recorre cada pps y se calcula la ocupacion que tiene (cantidad de bots 
    #     # esperando en la cola de la pps)
    #     for i in range(0,len(bot.recorrido_pps)):
    #         pps=bot.recorrido_pps[i]
    #         ocupacion=0
    #         for state in pps.state_nodos_cola:
    #             if state !=0: ocupacion+=1
    #         ocupacion_pps[i]=ocupacion
    #     # se busca pps con menor ocupacion
    #     min_index = ocupacion_pps.index(min(ocupacion_pps))
    #     pps_menos_ocupada = bot.recorrido_pps[min_index]
    #     for i in range(0,len(pps_menos_ocupada.nodos_cola)):
    #         nodo_cola=pps_menos_ocupada.nodos_cola[i]  
    #         for nodo in self.con[nodo_cola]:
    #             if self.xyz[nodo,0]==self.xyz[nodo_cola,0] and self.xyz[nodo,1]<self.xyz[nodo_cola,1]:
    #                 nodo_salida1=nodo
    #         for nodo in self.con[nodo_cola]:
    #             if self.xyz[nodo,0]==self.xyz[nodo_cola,0] and self.xyz[nodo,1]<self.xyz[nodo_cola,1]:
    #                 nodo_salida1=nodo



    # En cada time step de la simulacion se evalua si se llama esta funcion (ver codigo mas abajo),
    # para que se llame generar_ot
    # debe cumplirse que 1. la lista de skus a llamar (lista generada previamente por la 
    # funcion generar_skus_a_llamar) no este terminada, es decir, queden skus para llamar
    # 2. haya al menos 1 bot con state 0 3. haya al menos 1 pallet esperando en recepcion  
    # si se llama esta funcion es pq al menos hay 1 bot con state 0
    # Entonces, como es despues de abrir_ordenes(), dada una lista de ordenes abiertas con sus 
    # respectivos skus-qty, debe elegir que pallets traer primero 
    # GenerarOT de alguna forma elige cual sku-pallet debe ser recogido por un bot para
    # ser pickeado en las pps's. 
    # como puede haber mas de un pallet por sku,
    # entonces no elige un sku ni un pallet si no un pallet y sku (pallet-sku)
    # se supone que si hay 2 pallets con un mismo sku, primero deberia elegir el que 
    # tiene menos unidades
    # debe recorrer bots para ver cuales estan en un state idle
    # debe cambiar el state de los bots a un state de orden asignada
    # no solo debe generar una ot desde un nodo de almacenaje a una pps sino que debe calcular
    # por cuantas pps debe pasar el bot con el pallet, entonces es parecido a un order picking
    # por eso uso como base las funciones de order picking. 
    def generar_ot(self): 
        # if self.print_generar_ot == True: print(f"------------ generar_ot ---------------------")  
        # ORDEN PARA BUSCAR PALLET EN ALMACENAMIENTO Y GENERAR RECORRIDO EN PPS
        if self.skus_a_llamar_terminados==False and len(self.waiting_pllts)==0:
            cant_bots_s0=0
            for bot in self.bot_list:
                if bot.state==0 : cant_bots_s0 += 1
            # if self.print_generar_ot == True: print(f"skus a llamar {self.skus_a_llamar}")
            for i in range(0,99):
                if cant_bots_s0>0 and self.skus_a_llamar_terminados==False:
                    
                    sku=list(self.skus_a_llamar)[self.index_skus_a_llamar]
                    # if self.print_generar_ot == True: print(f"index skus a llamar: {self.index_skus_a_llamar}")
                    # if self.print_generar_ot == True: print(f"se busca pallet en stock que tenga SKU {sku}")

                    # se elige pllt con menor qty del sku
                    less_qty=99999999
                    pllt_a_mover=False
                    pllt_a_mover_xyz=0
                    dist_mejor_pllt=999999999
                    for pllt in self.stock[sku]:
                        # es necesario poner la condicion pllt.bot==None porque puede ocurrir que se seleccione un
                        # pllt a mover, luego abajo se le asigne un bot y al llamar nuevamente a generar_ot se le vuelva a 
                        # asignar un bot, entonces pllt.bot==None lo evita
                        if pllt.bot==False:
                            if pllt.qty<less_qty: # este if self.print_generar_ot == True: print siempre debe decir False, ojo con el bot con id=0, quizas es mejor dejar el pllt con None en vez de False
                                less_qty=pllt.qty
                                pllt_a_mover=pllt
                                pllt_a_mover_xyz=self.xyz[pllt_a_mover.id_pos]
                                dist_mejor_pllt=np.linalg.norm(self.avg_pps_xyz-pllt_a_mover_xyz)
                            else:
                                 dist=np.linalg.norm(self.avg_pps_xyz-self.xyz[pllt.id_pos])
                                 if dist<dist_mejor_pllt:pllt_a_mover=pllt

                    if pllt_a_mover==False:
                        # if self.print_generar_ot == True: print(f"XXXXXXXXXXXX No hay pallets en stock con el {sku}, se avanza al siguiente sku XXXXXXXXXXXXXXXX")
                        # como ya le asigne un bot al primer sku de skus_a_llamar
                        # el siguiente bot tendra el siguiente sku
                        if len(self.skus_a_llamar)==self.index_skus_a_llamar+1:
                            # terminan de pickearse las ordenes abiertas
                            self.skus_a_llamar_terminados=True
                            # if self.print_generar_ot == True: print(f"t={self.t}| XXXXXXXXXXX TERMINAN DE LLAMARSE SKUS XXXXXXXXXXXX")
                        else:
                            self.index_skus_a_llamar+=1


                    else:
                        # if self.print_generar_ot == True: print(f"XXXXXXXXXXXX se elige {pllt_a_mover} con SKU {sku} XXXXXXXXXXXXXXXX")
                        # se elige bot mas cercano al pllt
                        menor_dist=9999999
                        bot_elegido=False
                        for bot in self.bot_list:
                            dist=np.linalg.norm(bot.xyz-pllt_a_mover_xyz)
                            if bot.state==0 and dist < menor_dist:
                                menor_dist=dist
                                bot_elegido=bot
                        cant_bots_s0 += -1
                        # se le asigna el bot al pllt para que en la siguiente llamada a generar_ot el pllt elegido no se vuelva a elegir
                        pllt_a_mover.bot=bot_elegido
                        # if self.print_generar_ot == True: print(f"t={self.t}| se elige {bot_elegido} para trasladar {pllt_a_mover} con sku {pllt_a_mover.sku} a las PPS")

                        # importante: se agrega el sku a skus_llamados para que no se vuelva a llamar el sku hasta que el bot termine el recorrido
                        # en las pps. una vez que el bot termina el recorrido, el sku se elimina de skus_llamados para que se pueda volver a llamar
                        # antes usaba un check de si el sku estaba en movimiento, viendo si el pllt con el sku tenia un bot asignado pero
                        # el problema es que a veces ek bot aun no llegaba al pallet, entonces se volvia a llamar el sku. en este caso
                        # a penas se elige un bot para un pallet, el sku asociado ya queda como llamado y no se espera a que el bot llegue al pallet
                        self.skus_llamados.append(sku)

                        ordenes_con_sku=self.skus_a_llamar[sku] 
                        pps_agregadas=[]
                        recorrido_pps=[]
                        for orden in ordenes_con_sku:
                            pps=orden.pps 
                            if pps not in pps_agregadas:
                                # bot_elegido.recorrido_nodos.append(pps.id_nodo)
                                recorrido_pps.append(pps) 
                                pps_agregadas.append(pps)

                        bot_elegido.recorrido_pps = recorrido_pps
                        bot_elegido.en_recorrido_pps=True
                        # print(bot_elegido,recorrido_pps)

                        # if self.print_generar_ot == True: print(f"t={self.t}| {bot_elegido} queda con recorrido pps {bot_elegido.recorrido_pps}")

                        # se manda al bot a buscar el pllt primero
                        id_destino_ruta=pllt_a_mover.id_pos
                        bot_elegido.calcular_ruta(id_destino_ruta)
                        bot_elegido.state=1
                        bot_elegido.pllt=pllt_a_mover
                        # if self.print_generar_ot == True: print(f"t={self.t}| {bot_elegido} se manda a buscar {pllt_a_mover} ubicado en nodo {pllt_a_mover.id_pos}")

                        # como ya le asigne un bot al primer sku de skus_a_llamar
                        # el siguiente bot tendra el siguiente sku
                        if len(self.skus_a_llamar)==self.index_skus_a_llamar+1:
                            # terminan de pickearse las ordenes abiertas
                            self.skus_a_llamar_terminados=True
                            # if self.print_generar_ot == True: print(f"t={self.t}| XXXXXXXXXXX TERMINAN DE LLAMARSE SKUS A LLAMAR XXXXXXXXXXXX")
                        else:
                            self.index_skus_a_llamar+=1


                # cuando se acaben los bots con state 0 ya no se sigue recorriendo
                # la lista de skus a llamar. pero si debe quedar guardado el 
                # index_skus_a_llamar, de forma que cuando vuelvan a haber bots con
                # state0, se siga desde ese indice
                # else:
                #     if cant_bots_s0==0:
                #         # if self.print_generar_ot == True: print(f"t={self.t}| no quedan bots con state 0")
                #         # pass
                #     elif self.skus_a_llamar_terminados==True:
                #         # if self.print_generar_ot == True: print("se termina de llamar los skus")
                #         pass
                #     break
            
        # ORDEN PARA BUSCAR PALLET A RECEPCION Y TRASLADAR A ALMACENAMIENTO
        if len(self.waiting_pllts)>0:
            cant_bots_s0=0
            for bot in self.bot_list:
                if bot.state==0 : cant_bots_s0 += 1

            for i in range(0,99):
                if len(self.waiting_pllts)>0 and cant_bots_s0>0:
                    pllt=self.waiting_pllts[0]
                    pllt_xyz=self.xyz[pllt.id_pos] 
                    bot_elegido=False 
                    less_dist=99999999
                    for bot in self.bot_list: 
                        if bot.state==0:
                            dist=np.linalg.norm(pllt_xyz-bot.xyz)
                            if dist<less_dist:
                                bot_elegido=bot
                                less_dist=dist

                    if bot_elegido!=False:
                        self.waiting_pllts.remove(pllt)
                        # if self.print_generar_ot == True: print(f"t={self.t}| {pllt} en recepcion asignado a {bot_elegido}, waiting_pllts: {self.waiting_pllts}") 
                        cant_bots_s0 += -1
                        bot_elegido.pllt=pllt
                        pllt.bot=bot_elegido
                        bot_elegido.state=9
                        id_destino_ruta=pllt.id_pos
                        bot_elegido.calcular_ruta(id_destino_ruta)

                        for nodo in self.nodos_almacenamiento:
                            if nodo not in self.nodos_ocupados:
                                pllt.id_almacenamiento=nodo
                                self.nodos_ocupados.append(nodo)
                                # if self.print_generar_ot == True: print("NODOS OCUPADOS",self.nodos_ocupados)
                                break
                                
                else:
                    break


        # if self.print_generar_ot == True: print(f"------------------------------------------------")
        




    # debe considerar que si una orden pide
    # mas qty de la que le queda al pallet, entonces no puede sacar mas que esa cantidad
    # entonces las ordenes deben ser una matriz donde las filas son el sku, primera columna es cantidad
    # pickeada actualmente y 2da columna cantidad total requerida, cada vez que llega un pallet se debe
    # actualizar esa matriz de orden de la orden
    # esta funcion genera lo siguiente (cada uno explicado abajo)
    # pps.orders_cant_picking
    # pps.orders_picking_time
    # pps.orders_t_picking
    # pps.index_picking
    def calcular_picking(self,pps):
        # if self.print_calcular_picking == True or self.print_calcular_picking2 == True : print(f"------------ calcular_picking ---------------------")
        # if self.print_calcular_picking == True : print(f"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

        # aca hay una oportunidad de optimizacion, tengo X unidades y busco
        # suplir una lista de ordenes done cada una pide Y,Z,W, etc. unidades
        # busco maximizar la cantidad de ordenes a cerrar
        # creo que la solucion puede ser ordenar las ordenes de forma ascendente
        # desde la que pide menos a la q pide mas unidades e ir pickeando en ese
        # orden hasta que se me acaben las unidades o supla todas las ordenes
        # si una orden tiene prioridad (debe ser finalizada antes de un tiempo)
        # se podria colocar primero

        bot=pps.bot
        pllt=bot.pllt
        sku=pllt.sku
        qty_disp=pllt.qty

        # if self.print_calcular_picking == True : print(f"t={self.t}| Se calcula picking en {pps} de {bot} con {pllt}, SKU {pllt.sku}, qty {pllt.qty}")

        ordenes_a_pickear={}
        for order in pps.orders:
            # solo se revisan las ordenes que tienen el sku que trae el pllt 
            if sku in order.lista:
                order_qty=order.lista[sku]-order.lista_picked[sku]
                if order_qty>0:
                    ordenes_a_pickear[order]=order_qty
                    # if self.print_calcular_picking == True : print('antes',order)
                    # if self.print_calcular_picking == True : print(order.lista_picked)
        
        # if len(ordenes_a_pickear)>0:
        ordenes_a_pickear_sorted=sorted(ordenes_a_pickear.items(), key=lambda item: item[1])
        ordenes_a_pickear_sorted=dict(ordenes_a_pickear_sorted)
        
        # orden:[cant_a_pickear,cant_a_pickear]
        pps.orders_cant_picking={}
        # orden:[cant_a_pickear,cant_segundos_a_pickear]
        pps.orders_picking_time={}
        # orden:segundos pickeados
        pps.orders_t_picking={}
        # indica el indice de la orden que se esta pickeando
        pps.index_picking=0

        for order in ordenes_a_pickear_sorted:
            order_qty=order.lista[sku]-order.lista_picked[sku]
            qty_a_pickear=min(qty_disp,order_qty)
            # importante aca usar += porque la cantidad de picking actual (qty_a_pickear)
            # se debe sumar a la cantidad ya pickeada (order.lista_picked[sku])
            order.lista_picked[sku]+=qty_a_pickear
            order.pick_h[self.t]=[sku,qty_a_pickear,pps]
            qty_disp=qty_disp-qty_a_pickear

            pps.orders_cant_picking[order]=qty_a_pickear
            pps.orders_picking_time[order]=qty_a_pickear*self.t_picking_per_unit
            pps.orders_t_picking[order]=0

            # if self.print_calcular_picking == True : print('despues',order)
            # if self.print_calcular_picking == True : print(order.lista_picked)
            # if self.print_calcular_picking2 == True: print(f"{order}, lista_picked, {order.lista_picked}")

            if qty_disp==0:
                bot.pllt_vacio=True
                # si pllt queda vacio se remueve del stock
                self.stock[sku].remove(pllt)
                if len(self.stock[sku])==0:
                    del self.stock[sku]
                self.nodos_ocupados.remove(pllt.id_almacenamiento)
                break
        # print(pps.orders_picking_time)
            
        pllt.qty=qty_disp
        # if self.print_calcular_picking == True : print(f"{pps} tiene orders_cant_picking de SKU {sku}: {pps.orders_cant_picking}")
        # if self.print_calcular_picking == True : print(f"orders_picking_time: {pps.orders_picking_time}")
        # if qty_disp==0:
            # if self.print_calcular_picking == True : print(f"t={self.t}| el {pllt} queda vacio, bot queda con tarea de pallet vacio")
            # if self.print_calcular_picking == True : print(f"se elimina {pllt} de stock: {self.stock}")
            # if self.print_calcular_picking == True : print(f"se libera el nodo de almacenamiento {pllt.id_almacenamiento} que usaba el {pllt}")
            # pass
        # else:
            # if self.print_calcular_picking == True : print(f"{pllt} queda con qty disp = {pllt.qty}")
            # pass

        # if self.print_calcular_picking == True : print(f"--------------------------------------------")

    # sumar el tiempo t de picking en pps, si termina el picking debe cambiar state del bot para
    # que pase a siguiente pps o se vaya a zona de pllts vacios pq se le acabaron las units
    # funcion que revisa si ya se hizo el picking
    # debe considerar cuantas tiendas tiene abierta la pps y cuantas unidades se estan 
    # pickeando por tienda
    # si el tiempo de picking finaliza la funcion debe cambiar el state del bot y pps
    def check_tiempo_picking(self,pps):
        # if self.print_check_tiempo_picking == True: print(f"        ------------ check_tiempo_picking ---------------------")
        # se obtiene la orden que se esta pickeando actualmente en la pps
        # con list() convierto el diccionario orders_t_picking a una lista, para luego poder usar el index
        # al usar list en un diccionario, quedan los key del diccionario como una lista y los value se pierden
        order=list(pps.orders_t_picking)[pps.index_picking]
        # se aumenta el tiempo de picking de la orden
        pps.orders_t_picking[order]+=self.dt
        # if self.print_check_tiempo_picking == True: print(f"        t={self.t}| {pps} state {pps.state}: la {order} aumenta el picking de {pps.bot} sku {pps.bot.pllt.sku}, queda {pps.orders_t_picking}") 
        # if self.print_check_tiempo_picking == True: print(f"t={self.t}| orders picking times: {pps.orders_picking_time}")

        if pps.orders_t_picking[order] >= pps.orders_picking_time[order]:
            # if self.print_check_tiempo_picking == True: print(f"        t={self.t}| {pps}: la {order} termina de pickear el sku {pps.bot.pllt.sku}, queda {pps.orders_t_picking}")
            # este es el picking de solamente 1 sku de la orden. 
            # cuando una orden termina de pickear TODOS sus skus, la orden se debe cerrar
            # entonces la pps puede admitir una nueva orden
            # entonces hay que llamar la funcion para abrir ordenes 
            orden_finalizada=self.check_order_state(order)
            if orden_finalizada==True:
                # print(f"t={self.t}| {pps}: la {order} esta finalizada")
                if self.cant_ordenes_finalizadas == len(self.order_list):
                    self.seguir = False

                # if self.print_check_tiempo_picking == True: 
                #     print(f"        t={self.t}| {pps}: la {order} esta finalizada")
                #     print(f"        lista       : {order.lista}")
                #     print(f"        lista_picked: {order.lista_picked}")

                
                order.state=2
                pps.orders.remove(order)
                # check si ya se pickearon todas las ordenes de la pps
                if pps.index_picking == len(pps.orders_t_picking)-1:
                    # pps state = 0 para que se ejecute abrir_ordenes en proximo time step
                    pps.state=0
                    # if self.print_check_tiempo_picking == True: print(f"la {order} es la ultima orden por pickear y quedo finalizada, entonces pps state = 0")
            # else:
            #     if self.print_check_tiempo_picking == True: print(f"        t={self.t}| la {order} aun no esta finalizada")
            #     if self.print_check_tiempo_picking == True: print(f"        lista       : {order.lista}")
            #     if self.print_check_tiempo_picking == True: print(f"        lista_picked: {order.lista_picked}")
            
            
            bot_sale_de_la_pps=True # lo mas normal es que el bot salga de la pps, excepto cuando no encuentra a cual pps ir (state 3.6)
            # check si ya se terminaron de pickear las ordenes y el bot debe irse
            if pps.index_picking == len(pps.orders_t_picking)-1:    
                # if self.print_check_tiempo_picking == True: print(f"        t={self.t}| {pps}: todas las ordenes terminan de pickear el sku {pps.bot.pllt.sku}, queda {pps.orders_t_picking}")
                # las variables de picking de la pps como order_t_picking se resetean en la funcion
                # calcular_picking, de igual forma reseteo el indice aca a False por seguridad y para que me salte un error reconocible en caso de bug
                pps.index_picking=False
                bot=pps.bot
                # print(pps)
                # print(bot)
                # print(bot.recorrido_pps)
                # print(bot.nodo_actual)
                bot.recorrido_pps.remove(pps)
                # check si al bot le quedan pps por visitar
                if bot.pllt_vacio==False:

                    # termina recorrido y debe dejar pllt en almacenamiento
                    if len(bot.recorrido_pps)==0: 
                        # if self.print_check_tiempo_picking == True: print(f"        t={self.t}| {bot} se manda al almacenamiento a dejar el {bot.pllt} a su nodo de almacenamiento {bot.pllt.id_almacenamiento}")         
                        bot.state=6
                        bot.calcular_ruta(bot.pllt.id_almacenamiento)
                        # se elimina el sku de skus_llamados para que pueda ser llamado de nuevo por funcion "generar_skus_a_llamar"
                        self.skus_llamados.remove(pps.bot.pllt.sku)
                        # print('se va al alma')
                    # debe ir a la siguiente pps
                    else:
                        # if self.print_check_tiempo_picking == True: print(f"        t={self.t}| {bot} continua a la siguiente pps")

                        self.elegir_pps(bot)
                        if bot.state==3:
                            bot.calcular_ruta(bot.pps_elegida.id_nodo)
                            # print('asa',bot.pps_elegida.id_nodo)
                        elif bot.state==3.2:
                            bot.calcular_ruta(bot.nodo_asignado_pps)
                            # print('ppppp',bot.nodo_asignado_pps)
                        # caso bot sale con state 3.1 de elegir_pps
                        elif bot.state==3.1:
                            # print('entraaaaaaa 3.1')
                            bot_sale_de_la_pps=False



                # tiene pllt vacio y debe dejar el pllt en zona de pllts vacios        
                else:
                    # if self.print_check_tiempo_picking == True: print(f"        t={self.t}| {bot} va a dejar pllt vacio")
                    bot.state=8
                    id_destino_ruta=False
                    menor_dist=999999
                    for nodo in self.nodos_pllt_vacios:
                        dist=np.linalg.norm(self.xyz[nodo]-np.array(bot.xyz))
                        if dist<menor_dist:
                            menor_dist=dist
                            id_destino_ruta=nodo
                    bot.calcular_ruta(id_destino_ruta)
                    self.skus_llamados.remove(pps.bot.pllt.sku)


                if bot_sale_de_la_pps==True:
                    # print('entra 1')
                    # se deja la pps con state 1 o 4 para que pueda llegar otro bot a la pps
                    pps_tiene_cola=False
                    for state_nodo_cola in pps.state_nodos_cola:
                        if state_nodo_cola!=0:
                            pps.state=4
                            pps_tiene_cola=True
                            break
                    if pps_tiene_cola == False: pps.state=1

                else:
                    # print('entra 2')
                    pps.state=5


            else:
                # en el siguiente time step la pps va a pickear la siguiente orden
                pps.index_picking+=1            

        # if self.print_check_tiempo_picking == True: print(f"-------------------------------------------------")


    # funcion que revisa si la orden esta finalizada o no
    def check_order_state(self,order):
        order_finalizada=True
        for key,value in order.lista.items():
            if order.lista_picked[key] < value:
                order_finalizada=False
                break

        return order_finalizada


    def psim_gtp(self):

        for i in range(0,self.cant_steps):
            self.t=i*self.dt
            
            # se hacen calculos iniciales que solo hay q hacer 1 vez y las hago en el t=0
            if self.t==0:
                # calcular posicion promedio de las pps
                xlist=[]
                ylist=[]
                for pps in self.pps_list:
                    xlist.append(self.xyz[pps.id_nodo][0])
                    ylist.append(self.xyz[pps.id_nodo][1])
                self.avg_pps_xyz=np.array([ np.average(xlist) , np.average(ylist) ])


            # if self.print_log == True : print('------------------------------------')
            # if self.print_log == True : print(f"t={t}")
            # print(f"t={self.t}")

            abrir_ordenes=False
            for pps in self.pps_list:

                if pps.state==0 and len(self.waiting_orders)>0:
                    # basta que una pps este sin orden para que se ejecute
                    # la funcion que abre las ordenes en las ppss
                    abrir_ordenes=True

                if pps.state==1:
                    pass   

                elif pps.state==3:
                    # order=pps.order
                    self.check_tiempo_picking(pps)


            if abrir_ordenes==True:
                # NOTAR QUE EN TODO EL CODIGO ACA ES EL UNICO LUGAR DONDE SE LLAMA EL METODO ABRIR ORDENES
                se_abre_order=self.abrir_ordenes() 
                if se_abre_order == True:
                    self.generar_skus_a_llamar()
                
            generar_ot=False
            if self.skus_a_llamar_terminados==False or len(self.waiting_pllts)>0:
                for bot in self.bot_list:
                    if bot.state==0:
                        generar_ot=True
                        break
            if generar_ot==True:
                self.generar_ot()


            # print(self.pps_list[0],self.pps_list[0].state)

            # bot1=self.bot_list[6]
            # print(bot1.nodo_actual,bot1.xyz)

            for bot in self.bot_list:

                if bot.state==1:
                    bot.do()
                    if bot.state==2: 
                        # if self.print_bot_states == True: print(f"t={self.t}| {bot} llega a {bot.pllt} en nodo {bot.nodo_actual} de almacenamiento y lo empieza a cargar para ir a PPS")
                        bot.pllt.state=1
                        bot.pllt.bot=bot
                    

                elif bot.state==2:
                    # print(bot.tiempo_cargando_pllt)
                    bot.tiempo_cargando_pllt+=1
                    if bot.tiempo_cargando_pllt == self.tiempo_carga_pllt:
                        # se resetea el tiempo de carga de pallet para que la proxima vez que cargue un pallet el tiempo comience en 0
                        bot.tiempo_cargando_pllt=0 
                        if bot.en_recorrido_pps == True:
                            # if self.print_bot_states == True: print(f"t={self.t}| {bot} termina de cargar {bot.pllt}, se dirige a recorrido PPS {bot.recorrido_pps}")
                            bot.pllt.state=1
                            self.elegir_pps(bot)
                            # print(f"pps elegida {bot.pps_elegida}")
                            if bot.state==3:
                                bot.calcular_ruta(bot.pps_elegida.id_nodo)
                                # print('asa',bot.pps_elegida.id_nodo)
                            elif bot.state==3.2:
                                bot.calcular_ruta(bot.nodo_asignado_pps)
                                # print('ppppp',bot.nodo_asignado_pps)
                            # pps_destino=bot.recorrido_pps[bot.index_recorrido]
                        else:
                            # print('XXXXXXXXXXXXXXXXXXXXX')
                            # if self.print_bot_states == True: print(f"t={self.t}| {bot} termina de cargar {bot.pllt} en recepcion, se dirige a almacenamiento")
                            bot.calcular_ruta(bot.pllt.id_almacenamiento)

                elif bot.state==3.1:
                    # check si bot esta en almacenamiento o en pps
                    en_pps=False
                    if bot.nodo_actual in self.iden_dict2['nodos_pps']:
                        en_pps=True
                        # print('XXXXXXXXXXXXXXXXXXXXXXX')
                        for pps in self.pps_list:
                            if pps.id_nodo == bot.nodo_actual : pps_bot=pps
                        
                    # se revisa si hay alguna pps donde el bot pueda ir
                    self.elegir_pps(bot)
                    if bot.state==3.2:
                        # si bot estaba en pps, entonces ahora sale y libera a la pps
                        if en_pps == True : pps_bot.state=4
                        # print(bot.state, bot.nodo_asignado_pps)
                        bot.calcular_ruta(bot.nodo_asignado_pps)
                    elif bot.state==3:
                        bot.calcular_ruta(bot.pps_elegida.id_nodo)
                    # else:
                        # print(f"{self.t}| {bot} no encuentra forma de ir a {bot.pps_elegida}")

                elif bot.state==3.2:
                    bot.do()
                
                # 3.3= en cola de nodo PPS
                elif bot.state==3.3:
                    for i in range(0,len(bot.pps_elegida.nodos_cola)):
                        i2=len(bot.pps_elegida.nodos_cola)-1-i
                        # se recorren los nodos desde el ultimo de la cola hasta el primero hasta encontrar
                        # el nodo donde esta el bot
                        if bot.pps_elegida.nodos_cola[i2]==bot.nodo_asignado_pps:
                            if i2 == 0: # si esta en la 1era posicion de la cola
                                if bot.pps_elegida.state==4: 
                                    # print('siiiiiiiii')
                                    bot.calcular_ruta(bot.pps_elegida.id_nodo)
                                    bot.state=3.4
                                    # le quito el nodo que tenia asignado
                                    bot.nodo_asignado_pps=None
                                    # se libera el nodo que el bot estaba ocupando en la cola
                                    bot.pps_elegida.state_nodos_cola[i2]=0
                                    # defino el state de la pps
                                    bot.pps_elegida.state=2
                                    break
                                # else:
                                    # pass
                                    # print('noooooooo',bot.pps_elegida.state)
                            else:
                                # se checkea si el siguiente nodo de la cola se desocupo para avanzar
                                if bot.pps_elegida.state_nodos_cola[i2-1]==0:
                                    bot.calcular_ruta(bot.pps_elegida.nodos_cola[i2-1])
                                    bot.state=3.5
                                    # se le asigna el nodo siguiente al bot
                                    bot.nodo_asignado_pps=bot.pps_elegida.nodos_cola[i2-1]
                                    # se libera el nodo que el bot estaba ocupando y se ocupa el nodo de destino
                                    bot.pps_elegida.state_nodos_cola[i2]=0
                                    bot.pps_elegida.state_nodos_cola[i2-1]=1
                                    break

                # 3.4= bot avanzando a nodo pps desde su cola (esta en 1era posición de cola y avanza a la pps)
                elif bot.state==3.4:
                    bot.do()
                    pps=bot.pps_elegida
                    if bot.state==4:
                        bot.pps_elegida.state=3
                        pps.bot=bot
                        # if self.print_bot_states == True: print(f"XXXXXXXXXXXXXXX t={self.t}| {bot} con {bot.pllt} llega a la {pps} que tiene state {pps.state} en nodo {bot.nodo_actual}, se ejecuta calcular_picking")
                        self.calcular_picking(pps)
                        # se asigna pps state 3 para que haga check del tiempo de picking 
                        pps.state=3

                # 3.5 = bot avanzando a siguiente posición en la cola de la pps
                elif bot.state==3.5:
                    # si el bot llega a la siguiente posicion en la cola, bot.do() le va a cambiar el state a 3.3
                    bot.do() 

                elif bot.state==3 or bot.state==5:
                    bot.do() 
                    pps=bot.pps_elegida
                    if bot.state==4:
                        bot.pps_elegida.state=3
                        pps.bot=bot
                        # if self.print_bot_states == True: print(f"XXXXXXXXXXXXXXX t={self.t}| {bot} con {bot.pllt} llega a la {pps} que tiene state {pps.state} en nodo {bot.nodo_actual}, se ejecuta calcular_picking")
                        self.calcular_picking(pps)
                        # se asigna pps state 3 para que haga check del tiempo de picking 
                        pps.state=3

                elif bot.state==6:
                    bot.do()
                    # if bot.state==7:
                        # if self.print_bot_states == True: print(f"t={self.t}| {bot} llega al nodo {bot.nodo_actual} del almacenamiento para dejar {bot.pllt}")

                # DESCARGA DE PLLT
                elif bot.state==7:
                    bot.tiempo_cargando_pllt+=1
                    if bot.tiempo_cargando_pllt == self.tiempo_carga_pllt:
                        bot.tiempo_cargando_pllt=0
                        bot.state_change()
                        bot.pllt.bot=False
                        bot.pllt.id_pos=bot.nodo_actual

                        ### CASO BOT DESCARGA PALLET QUE VIENE DE RECORRIDO EN PPS
                        if bot.en_recorrido_pps == True:
                            bot.en_recorrido_pps = False
                            bot.recorrido_nodos=[]
                            bot.recorrido_pps=[]
                            bot.index_recorrido=False
                            
                            ### caso bot descarga pallet vacio
                            if bot.pllt_vacio==True:
                                bot.pllt.state=3
                                bot.state=0
                                # if self.print_bot_states == True: print(f"t={self.t}| {bot} termina de descargar {bot.pllt} VACIO, bot queda con state {bot.state}")
                            ### caso bot descarga pallet en almacenamiento
                            else:
                                bot.pllt.state=0
                                bot.state=0
                                # if self.print_bot_states == True: print(f"t={self.t}| {bot} termina de descargar {bot.pllt} en almacenamiento")
                        
                        ### CASO BOT DESCARGA PALLET NUEVO QUE VIENE DE RECEPCION
                        else:
                            bot.pllt.state=0
                            # if self.print_bot_states == True: print(f"t={self.t}| {bot} termina de descargar {bot.pllt} nuevo desde recepcion en almacenamiento")
                            # se actualiza el stock
                            sku_existente=False
                            for key,value in self.stock.items():
                                if key==bot.pllt.sku: 
                                    self.stock[bot.pllt.sku].append(bot.pllt)
                                    sku_existente=True
                                    break
                            if sku_existente==False: 
                                self.stock[bot.pllt.sku] = [bot.pllt]
                            # if self.print_bot_states == True: print(f"t={self.t}| se almacena {bot.pllt}, stock: {self.stock}")
                            # if self.print_bot_states == True: print(f"t={self.t}| por nuevo pllt almacenado, se llama a generar_skus_a_llamar")

                        # # si se termina de descargar un pallet, ya sea un pallet que venia de un recorrido en pps o un pallet nuevo
                        # # se vuelve a generar la lista de skus a llamar porque hay un nuevo pallet disponible
                        # # en almacenamiento que puede ser llamado
                        # hay_bot_state_0=False
                        # for bot1 in self.bot_list:
                        #     if bot1 != bot: # no se considera el bot actual que acaba de tener state 0
                        #         if bot1.state==0: hay_bot_state_0 = True
                        #     if hay_bot_state_0 == True: self.generar_skus_a_llamar()


                elif bot.state==8:
                    bot.do()

                elif bot.state==9:
                    bot.do()
                    # if bot.state==2:
                    #     if self.print_bot_states == True: print(f"t={self.t}| {bot} llega a recepcion y empieza a cargar {bot.pllt}")

                

                # elif bot.state==6:
                #     bot.do(t,sim_params,print_log)
                #     if bot.state==7:
                #         # if self.print_log == True : print(f"t={t}| {bot} llega a cargador")

                # elif bot.state==7:
                #     bot.tbateria+=10
                #     # # if self.print_log == True : print(f"t={t}| {bot} cargandose, bateria: {bot.tbateria}")
                #     if bot.tbateria >= bot.tbateria:
                #         # if self.print_log == True : print(f"t={t}| {bot} termina de cargarse, bateria: {bot.tbateria}, se dirige a staging")
                #         bot.state=8
                #         id_destino_ruta=np.random.choice(bot.staging_nodes)
                #         bot.calcular_ruta(t,sim_params,id_destino_ruta,print_log)


                # comentado por sizing
                if self.guardar_registro==True:
                    bot.xyz_h[self.t] = bot.xyz
                    bot.state_h[self.t] = bot.state
                    for pllt in self.pllt_list:
                        pllt.state_h[self.t]=pllt.state

            if self.seguir == False:
                print(f"t={self.t}| TERMINAN DE PICKEARSE TODAS LAS ORDENES")
                print("fin simulacion")
                break
            # self.t+=self.dt    
        
        ordenes_terminadas=0
        ordenes_terminadas_list=[]
        cajas_pickeadas=0
        for order in self.order_list:
            if order.state==2:
                ordenes_terminadas+=1
                ordenes_terminadas_list.append(order)
            for key,value in order.lista_picked.items():
                cajas_pickeadas+=value

        return ordenes_terminadas,ordenes_terminadas_list, cajas_pickeadas

    def orders_state(self):
        for order in self.order_list:
            print(order)
            for key,value in order.lista.items():
                print(key,':',order.lista_picked[key],'/',value)
            print('--------------')

    def __str__(self):
        return f"simulacion psim"
    def __repr__(self):
        return self.__str__()




























