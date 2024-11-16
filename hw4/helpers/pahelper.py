import pandas as pd
import time
from datetime import datetime, timedelta
import requests
from io import StringIO

def get_pd_dataframe(start, end, stn_id=175671, w_max = 26):
    df = pd.DataFrame()

    # you must have a file called pa_key.txt with YOUR key in it
    key = open("pa_key.txt").read()
    
    headers = {
        "X-API-Key": f"{key}"
    }

    for w in range(0, w_max):

        if start == end:
            break
        elif start + timedelta(days=7) <= end:
            _end = start + timedelta(days=7)
        else:
            _end = end

        dt_start = datetime.strftime(start, "%Y-%m-%dT%M:%H:%SZ")
        dt_end   = datetime.strftime(_end , "%Y-%m-%dT%M:%H:%SZ")

        	
        url = f"https://api.purpleair.com/v1/sensors/{stn_id}/history/csv?fields=2.5_um_count%2C%202.5_um_count_a%2C%202.5_um_count_b%2C%20pm2.5_atm%2C%20pm2.5_atm_a%2C%20pm2.5_atm_b%2C%20pm2.5_cf_1%2C%20pm2.5_cf_1_a%2C%20pm2.5_cf_1_b&end_timestamp={dt_end}&start_timestamp={dt_start}"
        
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            d = r.content
            df = pd.concat([df, pd.read_csv(StringIO(bytes.decode(d)), index_col='time_stamp')])
        else:
            print(r.status_code, r.content)
        
        start = _end
        print(url) 
        time.sleep(5)

    return df
    