'''

    Pull data from HTML file and extract PM25 data, returning a Pandas DataFrame

'''
def get_ladeq_pm25_data(f_html, loc="lake charles"):
    from bs4 import BeautifulSoup
    from datetime import datetime
    import re

    soup = BeautifulSoup(open(f_html), 'html.parser')
    
    pat  = r"2024,\W+[0-9]+\:\d\d.*[AP]M"
    i_dt = str(soup.find("", string=re.compile(pat, re.I)).string).strip()
    i_dt_obj = datetime.strptime(i_dt, "%A, %B %d, %Y, %H:%M %p")
    
    d = []

    for tr in soup.find_all("table", "forecast"):
        tv = [td.string for td in tr.find("tr", "forecast_header") if td.string.strip()]
        loc, tv = tv[0], list(tv[1:])

        for v in tr.find_all("td", "forecast_pollutant", string=re.compile(r"PM2.?5", re.I)):
            fcst = [loc]
            for w in v.find_parent().find_all("td", "forecast_value"):
                fcst.append(int(w.string.split()[0]))
            d.append(fcst)
    
    return i_dt_obj, d


'''

    See:
        
'''
def pm25_to_aqi(n):
    if n <= 12:
        return n / 0.24
    elif n >12 and n <= 35.4:
        return 50 + ((n - 12) / 0.4755)
    elif n>35.4 and n <= 55.4:
        return 100 + ((n - 35.4) / 0.4082) + 1
    elif n>55.4 and n <= 150.4:
        return 150 + ((n - 55.4) / 1.9388) + 1
    elif n>150.4 and n <= 250.4:
        return 200 + ((n - 150.4) / 1.009) + 1
    elif n>250.4:
        return 300