from flask import Flask, request, jsonify
from threading import Thread
import time

GlobalIntersections = []

app = Flask(__name__)

@app.route("/", methods=['GET'])
@app.route("/index")
def getIntersections():
    html = '<h3>List of {x} Intersections</h3>'
    if len(GlobalIntersections) == 0:
        html += '<p>No Intersections</p>'
    else:
        idx = 0
        for signal in GlobalIntersections:
            html += '<p>id- '
            html += idx.__str__()
            html += '. '
            html += signal.getStatus().__str__()
            html += '</p>'
            idx += 1
  
    return html.format(x=len(GlobalIntersections))

@app.route("/", methods=['POST'])
def createIntersection():
    GlobalIntersections.append(Intersection())
    data = "{ 'id': "+(len(GlobalIntersections)-1).__str__()+"}"
    return jsonify(data)

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
            return "For signal at intersection ",self," Direction is ",self.curActive," Light is ",self.lightSet[self.curActive]['activeLight']
                    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8010)
    # print("starting main\n")
    # s = Intersection()
    
    