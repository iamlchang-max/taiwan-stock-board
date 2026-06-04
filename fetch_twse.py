import urllib.request
import json
from datetime import datetime

def get_twse_limit_up():
    today_str = datetime.now().strftime('%Y%m%d')
    print("Fetching TWSE data for " + today_str + "...")
    
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={today_str}&type=ALLBUT0999"
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = response.read().decode('utf-8')
            data = json.loads(res_data)
    except Exception as e:
        print("Network error: " + str(e))
        return []
    
    if data.get('stat') != 'OK':
        print("No data available for today: " + today_str)
        return []

    raw_data = None
    for table in data.get('tables', []):
        if 'fields' in table and len(table['fields']) == 16:
            raw_data = table['data']
            break
            
    if not raw_data:
        print("Cannot find target table.")
        return []

    limit_up_list = []
    for row in raw_data:
        try:
            close_str = str(row[8]).replace(',', '')
            change_str = str(row[10]).replace(',', '')
            up_down_sign = str(row[9])
            
            if not close_str or close_str == '--':
                continue
                
            close_price = float(close_str)
            
            if '+' in up_down_sign or 'red' in change_str:
                change_price = float(change_str)
                yesterday_price = close_price - change_price
                
                if yesterday_price > 0:
                    percentage = (change_price / yesterday_price) * 100
                    
                    if percentage >= 9.5:
                        vol_shares = int(str(row[2]).replace(',', ''))
                        vol_sheets = int(vol_shares / 1000)
                        
                        limit_up_list.append({
                            "code": row[0],
                            "name": row[1],
                            "close": close_price,
                            "volume": vol_sheets,
                            "percentage": round(percentage, 2)
                        })
        except Exception:
            continue
            
    return limit_up_list

if __name__ == "__main__":
    result = get_twse_limit_up()
    
    # 日期格式改成 YYYY-MM-DD 顯示用
    today_display = datetime.now().strftime('%Y-%m-%d')
    
    output = {
        "date": today_display,
        "stocks": result
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    
    print(f"Successfully saved to data.json ({len(result)} stocks on {today_display})")
