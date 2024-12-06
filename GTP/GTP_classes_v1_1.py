
import numpy as np
from calcular_ruta_2_v2 import *


class cMover():
    def __init__(self,nodo_actual,sim):
        # en realidad es el id del nodo cuando comienza la ruta y no se actualiza hasta que termina la ruta
        self.nodo_actual=nodo_actual
        self.sim=sim
        # notar que no necesito definir este atributo de la clase a partir de un input de
        # __init__ ya que se que siempre que cree un nuevo bot estos atripbutos tendran estos valores
        self.state=0
        self.id=False
        self.xyz_h=np.zeros([self.sim.cant_steps,2])
        self.xyz_h[0]=np.array([self.sim.xyz[self.nodo_actual]])
        self.xyz=self.xyz_h[0]
        self.id_destino_ruta=False
        self.state_h=np.zeros([self.sim.cant_steps,1])
    def __str__(self):
        return f"Mover {self.id}"
    def __repr__(self):
        return self.__str__()
    
    # este metodo se usa solo cuando el bot ya tiene una ruta calculada
    def do(self):
        llega=False
        # # if print_log == True : print(f"t={t}| accion {self}")
        # caso en que ya se encuentra en el punto de destino de la ruta
        if self.ruta.shape[0]==1:
            llega=True
            # if print_log == True : print(f"t={t}| {self} ya esta en el punto de destino de la ruta, nodo {self.nodo_actual}")
        else:
            congestion=False
            if self.isbot==True: congestion,prioridad=self.check_congestion() 

            if congestion==False:
                self.ruta_id_actual+=1
                # la accion de avanzar consiste en actualizar el xyz del bot
                self.xyz=self.ruta[self.ruta_id_actual] 
                # if print_log == True : print(f"t={t}| {self} avanza {self.xyz}")
                if self.ruta_id_actual==self.ruta.shape[0]-1:
                    llega=True
            else:
                # if self.sim.print_log == True : print(f"{self} espera para que pase {prioridad}")
                pass 

        if llega==True:
            self.nodo_actual=self.id_destino_ruta
            self.state_change() 


    def calcular_ruta(self,id_destino_ruta):
        self.id_destino_ruta=id_destino_ruta

        # if print_log == True : print(f"t={t}| se calcula ruta del {self}, id inicio: {self.nodo_actual}, id destino: {self.id_destino_ruta}")
        # best_path,cost_best_path=btsolve1(self.sim.ad,
        #                                   self.sim.con,
        #                                   int(self.nodo_actual),
        #                                   int(self.id_destino_ruta),
        #                                   self.sim.xyz,
        #                                   False, #full_search
        #                                   False, #plot
        #                                   False, #plot_best
        #                                   False) #print_log
        
        best_path,cost_best_path=gtp_btsolve(self.sim.iden_dict2,
                                            False, # plot total
                                            self.sim.ad,
                                            self.sim.con,
                                            int(self.nodo_actual), #nodo inicio
                                            int(self.id_destino_ruta), #nodo_destino
                                            self.sim.xyz,
                                            False, #full_search
                                            False, #plot
                                            False, #plot_best
                                            False) #print_log


        self.ruta=nodpath_to_ruta(self.sim.xyz,
                                  best_path,
                                  self.sim.dt,
                                  self.sim.bot_vel,
                                  self.sim.tgiro,
                                  False,
                                  self.sim.giro_tol)
        self.ruta_id_actual=0
        
        # if print_log == True : print(f"t={t}| RUTA CALCULADA {best_path}")


class cBot(cMover):

    def __init__(self,id_actual,sim):
        super().__init__(id_actual,sim)

        self.en_recorrido_pps=False
        self.recorrido_pps=[]

        self.pllt_vacio=False
        self.pllt=False
        self.tiempo_cargando_pllt=False
        self.tbateria=self.sim.tbateria_inicial
        self.isbot=True
        self.pps_elegida=None
        self.nodo_asignado_pps=None

    def state_change(self):
        if self.state==1 or self.state==9:
            self.state=2
        
        elif self.state==3 or self.state==5:
            self.state=4

        elif self.state==3.2:
            self.state=3.3

        elif self.state == 3.4:
            self.state=4
        
        elif self.state==3.5:
            self.state=3.3

        elif self.state==6:
            self.state=7

        elif self.state==7:
            self.state=0

        elif self.state==8:
            self.state=7


    def check_congestion(self):
        congestion=False
        prioridad=False
        for botx in self.sim.bot_list:
            if botx != self:
                dist=np.linalg.norm(self.xyz-botx.xyz)
                # print(f"{self} {botx} state {botx.state} y {dist}")
                if dist < self.sim.lim_dist_congestion:
                    # print('aaaaaaaaaaa')
                    # if self.id_destino_ruta == botx.nodo_actual:
                        # congestion=True
                        # prioridad=botx
                        # break # uso break pq basta que haya 1 congestion para no tener que seguir el for

                    # if botx.state==4:
                    #     # print(f"{botx} tiene state 3")
                    #     if self.en_recorrido_pps == True:
                    #         if self.recorrido_pps[self.index_recorrido] == botx.recorrido_pps[botx.index_recorrido]:
                    #             congestion=True
                    #             prioridad=botx
                    #             break
                    
                    
                    if self.state not in [3.4,3.5]: # si bot tiene state 3.4 o 3.5 entonces no esta sujeto a congestion
                        if botx.id < self.id and botx.state not in [4,0,3.1,3.2,3.3,3.4,3.5]:
                            congestion=True
                            prioridad=botx
                            break
                    

                    
        return congestion, prioridad

    def __str__(self):
        return f"bot {self.id}"
    def __repr__(self):
        return self.__str__()

class cPllt():
    def __init__(self,pllt_params,sim):
        self.tin=pllt_params['tin']
        self.sku=pllt_params['sku']
        self.qty=pllt_params['qty']
        self.id_pos=pllt_params['id_pos']
        self.state=pllt_params['state']
        self.id_almacenamiento=pllt_params['id_almacenamiento']
        self.id=False
        self.bot=False
        self.sim=sim
        self.state_h=np.zeros([self.sim.cant_steps,1])
    def __str__(self):
        return f"pllt {self.id}"
    def __repr__(self):
        return self.__str__()

# la pps debe tener una lista de atributos "orden" que indique las ordenes (tiendas) que estan
# abiertas en la pps
class cPps():
    def __init__(self,id_nodo):    
        self.id_nodo=id_nodo
        self.nodo_salida_pps=False

        self.state=0
        self.orders=[]
        self.bot=False

        self.orders_cant_picking={}
        self.orders_picking_time={}
        self.orders_t_picking={}
        self.index_picking=False
        self.nodos_cola=[]
        # 0 = libre, 1=reservado, 2=ocupado
        # la simulacion edita la variable state_nodos_cola al crear la pps
        self.state_nodos_cola=False
        
    def __str__(self):
        return f"PPS {self.id}"
    def __repr__(self):
        return self.__str__()

# lista es sku - qty_requerida
# lista_picked es sku - qty_pickeada
class cOrder_gtp():
    def __init__(self,id,lista,sim):
        self.lista=lista
        self.lista_picked={}
        for key,value in lista.items():
            if key not in self.lista_picked:
                self.lista_picked[key]=0
        self.sim=sim
        self.pps=False
        self.id=id
        self.state=0
        self.pick_h=[0]*sim.cant_steps
    def __str__(self):
        return f"order {self.id}"
    def __repr__(self):
        return self.__str__()