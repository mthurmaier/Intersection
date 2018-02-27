from threading import Thread
import time

class Intersection:
    GREENTIME = 27  # green runs for 27 seconds
    YELLOWTIME = 3  # yellow runs for 3 seconds
    REDTIME = 0  # essentially red waits forever - until the other directions complete
    LightTimes = { 'Green': GREENTIME, 'Yellow': YELLOWTIME, 'Red': REDTIME}
    LightNext = {'Green:': 'Yellow', 'Yellow': 'Red', 'Red': 'Green' }
    

    def __init__(self):
        self.lightSet = {  # initial states for which light-set and which light color is active
            'North': { 'activeLight': 'Green', 'isActive': True},
            'South': { 'activeLight': 'Red', 'isActive': False},
            'East': {'activeLight': 'Red', 'isActive': False},
            'West': {'activeLight': 'Red', 'isActive': False} 
        }
        self.curActive = 'North'
        self.thread = Thread(target = Intersection.cycleLights, args=[self])
        # self.timer = threading.Timer(Intersection.GREENTIME,Intersection.cycleLights, args=[self])
        # self.timer.start()
        self.thread.start()

    def cycleLights(self):
        while True:  # loop forever - until thread is shut down
            for self.curActive in ['North', 'South', 'East', 'West']:
                print("Changing direction to: ",self.curActive)
                self.lightSet[self.curActive]['isActive'] = True
                for light in [ 'Green', 'Yellow', 'Red' ]:
                    print("changing light to: ",light)
                    self.lightSet[self.curActive]['activeLight'] = light
                    sleepTime = Intersection.LightTimes[light]
                    if light != 'Red':
                        time.sleep(sleepTime)
                    # there is no else. this direction is done.
    
    def getStatus(self):
            print("For signal at intersection: ",self,": Direction is ",self.curActive," Light is ",self.LightSet[self.curActive]['activeLight'])
                    
if __name__ == '__main__':
    print("starting main\n")
    s = Intersection()
    
    