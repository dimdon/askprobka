from flask import Flask, session, url_for
from flask_restful import Resource, Api
from flask_restful import reqparse
import werkzeug
from io import StringIO
import pandas as pd
import logging
import datetime
import os
from configparser import SafeConfigParser
from configobj import ConfigObj
import numpy as np

app = Flask(__name__)
api = Api(app)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


_FILE_NAME_ = 'game-cfg.cfg'

def delta2(input_state_new = 0,
           input_state_last = 0,
           data=None,
           cum_many_pos=[0,0,0],
           iter=0):
    list_many = [0,0,0]
    cur_state = {'quats': [0, 0, 0], 'lots': [0, 0, 0], 'dpos': [0, 0, 0]}
    deltas = [0, 0, 0]
    print(input_state_new, end=': ')
    i = iter
    if i == 0:
        cur_state['quats'] = list(data.iloc[0])
        cur_state['lots'] = [0,0,0]
        cur_state['dpos'] = [0,0,0]
        print(cur_state['quats'], "deltas:", deltas, end='')
    else:
        if input_state_new == input_state_last:
            # ставка не изменилась
            td = np.array(np.array(data.iloc[i]-cur_state['quats']))
            cur_state['dpos'] = [0,0,0]
            if input_state_new == 0:
                deltas = td
                print("0 cur_state:", cur_state['quats'], "  data:", np.array(data.iloc[i]), "deltas:", deltas, end='')
            elif input_state_new == 1:
                deltas = [i-td[0] for i in td]
                print("1 cur_state:", cur_state['quats'], "  data:", np.array(data.iloc[i]), "deltas:", deltas, end='')
            elif input_state_new == 2:
                deltas = [i - td[1] for i in td]
                print("2 cur_state:", cur_state['quats'], "  data:", np.array(data.iloc[i]), "deltas:", deltas, end='')
            elif input_state_new == 3:
                deltas = [i - td[2] for i in td]
                print("3 cur_state:", cur_state['quats'], "  data:", np.array(data.iloc[i]), "deltas:", deltas, end='')
        else:
            # мы меняем ставку
            cur_state['quats'] = list(data.iloc[i])
            temp_pose = np.array(cur_state['lots'])
            if input_state_new != 0:
                cur_state['lots'] = [-1,-1,-1]
                cur_state['lots'][input_state_new-1] = 2
            else:
                cur_state['lots'] = [0,0,0]
            cur_state['dpos'] = list(np.array(cur_state['lots']) - temp_pose)
            deltas = [0,0,0]
            print(cur_state['quats'], "deltas:", deltas, end='')

        for j in range(3):
            cum_many_pos[j] = cum_many_pos[j] - cur_state['dpos'][j]*np.array(data.iloc[i])[j]
            list_many[j] = cum_many_pos[j] + cur_state['lots'][j]*np.array(data.iloc[i])[j]

        print("  cur_pos:", cur_state['lots'], "  dpos:", cur_state['dpos'], "  many:", list_many[0]+list_many[1]+list_many[2])

    last_pose = cur_state['lots']
    input_state_last = input_state_new
    #return deltas.tolist(), list_many[0]+list_many[1]+list_many[2]
    try:
        if type(deltas) != list:
            deltas = deltas.tolist()
    except:
        None
    return deltas, list_many[0] + list_many[1] + list_many[2]
    pass

class GetDate4GameEngine(Resource):
    def get(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('curr_road', type=str)
            args = parser.parse_args()
            #print(args)
            _curr_position = args['curr_road']
            data_csv = pd.read_csv('data.csv', parse_dates = ['datetime'], names=['datetime','S','G','L']).drop(['datetime'],axis=1)

            # get game status

            delta = [0.0,0.0,0.0]
            cum_many_pos = [0.0,0.0,0.0]
            last_road = 0
            iter = 0

            #config = SafeConfigParser()
            config = ConfigObj(_FILE_NAME_)

            if not os.path.exists(_FILE_NAME_):
                print ('config does not exists')
                print("0")
                config['delta'] = delta
                config['cum_many_pos'] = cum_many_pos
                config['last_road'] = last_road
                config['iter'] = iter
                print ("1")
                print (config)
                config.write()
                print ("2")
            else:
                print ('config does exists')
                config.reload()
                delta = config['delta']
                #print (delta)
                for rec in range(len(delta)):
                    #print (rec)
                    delta[rec] = float(delta[rec])
                last_road = config['last_road']
                cum_many_pos = config['cum_many_pos']
                for rec in range(len(cum_many_pos)):
                    cum_many_pos[rec] = float(cum_many_pos[rec])
                iter = config['iter']
                print ('3')

            iter = int(iter) + 1
            res = delta2(input_state_new = int(_curr_position),
                         input_state_last = int(last_road),
                         data=data_csv,
                         cum_many_pos=cum_many_pos,
                         iter=iter)
            delta = res[0]
            money = res[1]
            print ("result for web: ",res)

            print (type(delta))
            print (delta)
            for rec in range(len(delta)):
                delta[rec] = delta[rec].__str__()
            config['delta'] = delta
            for rec in range(len(cum_many_pos)):
                cum_many_pos[rec] = cum_many_pos[rec].__str__()
            config['cum_many_pos'] = cum_many_pos
            config['last_road'] = _curr_position
            config['iter'] = iter
            config.write()
            return {'ErrorCode':200, 'error': 'Ok!', 'delta':delta,'money':money,'iter':iter,'curr_road':_curr_position,'last_road':last_road}
        except Exception as e:
            print (str(e))
            return {'error': str(e), 'ErrorCode':20001}

api.add_resource(GetDate4GameEngine, '/api/data')
app.static_url_path = '/PREFIX/static'
app.add_url_rule(app.static_url_path + '/<path:filename>',endpoint='static', view_func=app.send_static_file)

@app.route("/")
def hello():
    return "Welcome to API for ASKProbka!"

app.config['PROFILE'] = True
#app.config['SERVER_NAME'] = '0.0.0.0'
app.config['TRAP_HTTP_EXCEPTIONS'] = True

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5001)
