from flask import Flask, Response, jsonify
from threading import Thread
import time, pickle, json
from redis import Redis, RedisError

DB_NAME = 'Intersection'

GlobalTimerThreads = {}

redis = Redis(host="localhost", db=0)
# print("redis=",redis)
# newID = redis.incr("foo")
# print("redis=",redis, "newID=",newID)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def getAllIntersections():
    try:
        x = redis.hkeys(DB_NAME)
    except RedisError:
        js = { 'error': 'database error retrieving list of intersections'}
        js = json.dumps(js)
        resp = Response(js, status=500, mimetype='application/json')
        return resp
    if len(x) == 0:
        x = { 'note': 'Currently no intersections'}
        return jsonify(x)
    else:
        jsarray = []
        for idx in x:
            res, ints = read_from_redis(idx)  # just assume success
            js = json.dumps(ints.__dict__)
            jsarray.append(js)      
        return jsonify(jsarray)
  
@app.route("/<int:idx>", methods=['GET'])
def getIntersection(idx):
    # retrieve the intersection
    print("cyclLights for ",idx)
    res, ints = read_from_redis(idx)
    if res != 0:
        if res == 2: # db error
            js = { 'error': 'database error retrieving requested record', 'idx': idx}
            js = json.dumps(js)
            resp = Response(js, status=500, mimetype='application/json')
            return resp
        elif res == 1:  # it went away
            js = { 'error': 'intersection not found', 'idx': idx}
            js = json.dumps(js)
            resp = Response(js, status=404, mimetype='application/json')
            return resp
    js = json.dumps(ints.__dict__)
    resp = Response(js, status=200, mimetype='application/json')
    return resp
    
    return jsonify(ints)

@app.route("/", methods=['POST'])
def createIntersection():
    print("in creatIntersection()")
    try:
        # create a new ID
        nextID = redis.incr("intersectionID")
        myID = nextID - 1
        data = "{ 'id': "+myID.__str__()+"}"
    except RedisError:
        data = "{ 'error': <i>connot connect to Redis, counter disabled</i>}"
        return jsonify(data)
    # instantiate a new Intersection object, associate it with the ID
    # then store it in the database
    new_int = Intersection(myID)
    if write_to_redis(new_int) != 0:
        data = "{ 'error': <i>reddis hset error on newIntj</i>}"
    return jsonify(data)

def write_to_redis(intersection):
    res = 0  # assume success
    int_pkld = pickle.dumps(intersection)
    try:
        redis.hset(DB_NAME,intersection.myID,int_pkld)
    except RedisError:
        print("redis error writing intersection object ",intersection.myID," to hash");
        res = 1
    return res

def read_from_redis(idx,):
    return_num = 0 # assume success
    return_obj = "" # essentiall null string
    try:
        int_pkld = redis.hget(DB_NAME,idx)
    except RedisError:
        return 2, "Redis Exception reading idx"
    
    if(int_pkld == "None"): # such a thing does not exist
        return_num = 1
        return_obj = int_pkld
    else:
        intersect = pickle.loads(int_pkld)
        return_obj = intersect
    return return_num, return_obj
        
    
class Intersection:
    GREENTIME = 7  # green runs for 27 seconds
    YELLOWTIME = 3  # yellow runs for 3 seconds
    REDTIME = 0  # essentially red waits forever - until the other directions complete
    LightTimes = { 'Green': GREENTIME, 'Yellow': YELLOWTIME, 'Red': REDTIME}
    DirectionNext = {'North': 'South', 'South': 'East', 'East': 'West', 'West': 'North' }
    

    def __init__(self,idx):
        self.myID = idx
        self.lightSet = {  # initial states for which light-set and which light color is active
            'North': { 'activeLight': 'Green', 'isActive': True},
            'South': { 'activeLight': 'Red', 'isActive': False},
            'East': {'activeLight': 'Red', 'isActive': False},
            'West': {'activeLight': 'Red', 'isActive': False} 
        }
        self.curActiveLightSet = 'North'
        self.curState = 'Running'
        self.curActiveLightTimeLeft = self.GREENTIME
        GlobalTimerThreads[idx] = Thread(target = Intersection.timerFire, args=[idx])
        # self.timer = threading.Timer(Intersection.GREENTIME,Intersection.cycleLights, args=[self])
        # self.timer.start()
        GlobalTimerThreads[idx].start()
    
    @staticmethod
    def timerFire(idx):
        print("timerFire for ",idx)
        while True:
            time.sleep(1)
            if Intersection.cycleLights(idx) == 1:
                return  # we're done
    
    @staticmethod
    def cycleLights(idx):
        # retrieve the intersection
        print("cyclLights for ",idx)
        res, ints = read_from_redis(idx)
        if res != 0:
            if res == 2: # db error
                print("could not retrieve intersection:",idx," or unpickle it")
                # should return 5xx error
                js = { 'error': 'database error retrieving requested record', 'idx': idx}
                js = json.dumps(js)
                resp = Response(js, status=500, mimetype='application/json')
                return resp
            elif res == 1:  # it went away
                print("could not find intersection number ",idx)
                # should return 404
                js = { 'error': 'intersection not found', 'idx': idx}
                js = json.dumps(js)
                resp = Response(js, status=404, mimetype='application/json')
                return resp
        
        print("retrieved values: state, lighttime, dir, color", ints.curState,
               ints.curActiveLightTimeLeft, ints.curActiveLightSet, ints.lightSet[ints.curActiveLightSet]['activeLight'])
        # make sure it is still running
        if (ints.curState != 'Running'):
            del GlobalTimerThreads[idx]
            return 1  # say we're done
        
        # check the current value of the remaining light time
        if (ints.curActiveLightTimeLeft == 1): 
            # time ran out. switch light
            Intersection.switchLight(ints)
        else:
            # decrement and write back
            ints.curActiveLightTimeLeft -= 1
            write_to_redis(ints)
        
    @staticmethod
    def switchLight(ints):
        if ints.lightSet[ints.curActiveLightSet]['activeLight'] == 'Green': # go from green to Yellow
            ints.lightSet[ints.curActiveLightSet]['activeLight'] =  'Yellow'
            ints.curActiveLightTimeLeft = Intersection.YELLOWTIME
        else:  # color must be yellow, because red timers don't run
            # cycle direction to next one, change this direction to red, next to green, reset timer
            ints.lightSet[ints.curActiveLightSet]['activeLight'] = 'Red'
            ints.lightSet[ints.curActiveLightSet]['isActive'] = False
            ints.curActiveLightSet = Intersection.DirectionNext[ints.curActiveLightSet]
            ints.lightSet[ints.curActiveLightSet]['activeLight'] = 'Green'
            ints.lightSet[ints.curActiveLightSet]['isActive'] = True
            ints.curActiveLightTimeLeft = Intersection.GREENTIME
        write_to_redis(ints)  # for now, just assume it works
        return 0
            
        '''
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
        '''
    
    def getStatus(self):
            return "For signal at intersection ",self," Direction is ",self.curActive," Light is ",self.lightSet[self.curActive]['activeLight']
                    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8010)
    # print("starting main\n")
    # s = Intersection()
    
    