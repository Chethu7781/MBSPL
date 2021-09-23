from types import MethodType
from flask import Flask,request
import json, requests
from datetime import datetime
from itertools import groupby
from collections import defaultdict
from operator import itemgetter

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)


app = Flask(__name__)

@app.route("/")

def Hello():
    return "Hello Chethan! Raj .."

@app.route("/shift_data")
def shift_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    req_data = requests.get("https://gitlab.com/-/snippets/2094509/raw/master/sample_json_1.json")
    json_output = req_data.json()
    final_data = {}
    count_a_6_14=0
    count_b_6_14=0
    count_a_14_20=0
    count_b_14_20=0
    count_a_20_06=0
    count_b_20_06=0

    for i in json_output:
        for k,v in i.items():
            if k=="time":
                
                datetime_object = datetime.strptime(v,'%Y-%m-%d %H:%M:%S')
            if (datetime_object > datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')) and (datetime_object < datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S')): 

                if (datetime_object.hour >=6) and (datetime_object.hour <14):
                    if (k=="production_A") and (v==True):
                        count_a_6_14=count_a_6_14+1
                    if (k=="production_B") and (v==True):
                        count_b_6_14=count_b_6_14+1

                elif (datetime_object.hour >=14) and (datetime_object.hour <20):
                    if (k=="production_A") and (v==True):
                            count_a_14_20=count_a_14_20+1
                    if (k=="production_B") and (v==True):
                            count_b_14_20=count_b_14_20+1

                elif (datetime_object.hour >=20) or (datetime_object.hour <6):
                    if (k=="production_A") and (v==True):
                            count_a_20_06=count_a_20_06+1
                    if (k=="production_B") and (v==True):
                            count_b_20_06=count_b_20_06+1

    shift_A={"production_A":count_a_6_14,"production_B":count_b_6_14}
    shift_B={"production_A":count_a_14_20,"production_B":count_b_14_20}
    shift_C={"production_A":count_a_20_06,"production_B":count_b_20_06}
    final_data.update({"shift_A":shift_A})
    final_data.update({"shift_B":shift_B})
    final_data.update({"shift_C":shift_C})

    ##print(final_data)

    return final_data

@app.route("/runtime_utilization")
def runtime_utilization():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    req_data = requests.get("https://gitlab.com/-/snippets/2094509/raw/master/sample_json_2.json")
    json_output = req_data.json()
    res = {}
    total_runtime = 0
    total_downtime = 0
    for i in json_output:
        for k,v in i.items():
            if k=="time":
                datetime_object = datetime.strptime(v,'%Y-%m-%d %H:%M:%S')
            if (datetime_object > datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')) and (datetime_object < datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S')): 
                if (k=="runtime"):
                    print("v...",v)
                    total_runtime= total_runtime+v 
                    print("total_runtime",total_runtime)
                    if v>1021:
                        sub = v-1021
                        print("sub>>",sub)
                        total_downtime = total_downtime+sub
                        print("total_downtime",total_downtime)

    runtime_count = total_runtime-total_downtime
    runtime = convert(runtime_count)
    downtime = convert(total_downtime)
    machine_utilisation = (total_runtime)/(total_runtime + total_downtime) * 100 

    res.update({"runtime":runtime, "downtime":downtime, "utilization":machine_utilisation})
    return res

@app.route("/average_belt")
def average_belt():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    req_data = requests.get("https://gitlab.com/-/snippets/2094509/raw/master/sample_json_3.json")
    json_output = req_data.json()
    primary_result =[]
    result3 = []
    
    
    for i in json_output:
        
        res ={}
        # print("i.....",i)
        for k,v in i.items():
            if k=="time":
                datetime_object = datetime.strptime(v,'%Y-%m-%d %H:%M:%S')
            if (datetime_object > datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')) and (datetime_object < datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S')):
                
                if (k=="id"):
                    res["id"] = int(v.split("0")[-1])
                elif (k=="state") and (v==True):
                    res["belt1"] = 0
                    res["belt2"] = i["belt2"]
                elif (k=="state") and (v==False):
                    res["belt2"] = 0
                    res["belt1"] = i["belt1"]
        if res: 
            result3.append(res)

    INFO = sorted(result3, key=key_func)
    
    all_requ_value=[]
    for key, value in groupby(INFO, key_func):
        all_requ_value.append(list(value))
    
    for d in all_requ_value:
        result = defaultdict(int)
        n=len(d)
        belt1=0
        belt2=0
        belt_1_cnt=0
        for c in d :
            belt1  += int(c['belt1'])
            belt2 += int(c['belt2'])
            result["id"]=c["id"]
            result["avrg_belt1"]=belt1/n
            result["avrg_belt2"]=belt2/n

        final_result=dict(result)
        primary_result.append(final_result)

    return {"data":primary_result}

def key_func(k):
    return k['id']

if __name__=="__main__":
    app.run(debug=True)