
#%%
import numpy as np
import matplotlib.pyplot as plt



class cPicker():
    def __init__(self,id,xyz,state):
        self.id=id
        self.xyz=xyz
        self.state=state
    def __str__(self):
        return f"picker {self.id}"
    def __repr__(self):
        return self.__str__()


class cBot():
    def __init__(self,id,xyz,state):
        self.id=id
        self.xyz=xyz
        self.state=state
    def __str__(self):
        return f"bot {self.id}"
    
    def __repr__(self):
        return self.__str__()




bot_list=[cBot( 0 , np.array([3,4]) , 2 ) ,
          cBot( 1 , np.array([6,7]) , 2 ) ,
          cBot( 2 , np.array([8,8]) , 2 ) ]

picker_list=[cPicker( 0 , np.array([0,0]) , 0 ) ,
          cPicker( 1 , np.array([2,3]) , 0 ) ,
          cPicker( 2 , np.array([1,8]) , 0 ) ]

fig = plt.figure()            
fig, ax = plt.subplots()  
for bot in bot_list:
    ax.scatter(bot.xyz[0],bot.xyz[1],c='b')
    ax.annotate(str(bot.id),(bot.xyz[0]+0.1,bot.xyz[1]),c='b')

for picker in picker_list:
    ax.scatter(picker.xyz[0],picker.xyz[1],c='r',marker='D')
    ax.annotate(str(picker.id),(picker.xyz[0]+0.1,picker.xyz[1]),c='r')

ax.grid()

#%%


def picker_assign_tasks(t):
    bot_list_s2=[]
    for bot in bot_list:
        if bot.state==2: bot_list_s2.append(bot)
    
    picker_list_s0=[]
    for picker in picker_list:
        if picker.state==0: picker_list_s0.append(picker)

    cant_pickers_s0=len(picker_list_s0)

    dist=np.zeros([len(bot_list_s2),len(picker_list_s0)])        
    for i in range(0,len(bot_list_s2)):
        bot=bot_list_s2[i]
        for j in range(0,len(picker_list_s0)):
            picker=picker_list_s0[j]
            dist[i,j]=np.linalg.norm(picker.xyz-bot.xyz)

    max=np.max(dist)
    pickers_asignados_count=0
    for i in range(0,99):
        bot_index,picker_index=np.unravel_index(dist.argmin(), dist.shape)
        print(f"{bot_list_s2[bot_index]} con {picker_list_s0[picker_index]}")
        # BondPickerBot(t,bot_list_s2[bot_index],picker_list_s0[picker_index])
        dist[bot_index,:]=10*max
        dist[:,picker_index]=10*max
        pickers_asignados_count+=1
        if pickers_asignados_count == cant_pickers_s0:
            break
    
    

dist=picker_assign_tasks(3)