"""네이버 시세를 받아 quotes.json(종목별 최근 일봉)을 만든다. GitHub Actions에서 5분마다 실행."""
import json, sys, urllib.request, datetime, os

SRC = {
    'NDX':   'https://polling.finance.naver.com/api/realtime/worldstock/index/.NDX',
    'SNDK':  'https://polling.finance.naver.com/api/realtime/worldstock/stock/SNDK.O',
    'KOSPI': 'https://polling.finance.naver.com/api/realtime/domestic/index/KOSPI',
    'SEC':   'https://polling.finance.naver.com/api/realtime/domestic/stock/005930',
    'SKH':   'https://polling.finance.naver.com/api/realtime/domestic/stock/000660',
}
UA = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://m.stock.naver.com/'}

def num(x):
    try: return float(str(x).replace(',', ''))
    except Exception: return None

def bar(code, url):
    req = urllib.request.Request(url, headers=UA)
    d = json.load(urllib.request.urlopen(req, timeout=15))['datas'][0]
    day = (d.get('localTradedAt') or '')[:10]
    o, h, l, c = (num(d.get(k + 'Raw') or d.get(k)) for k in ('openPrice', 'highPrice', 'lowPrice', 'closePrice'))
    v = num(d.get('accumulatedTradingVolumeRaw')) or 0
    if code == 'KOSPI': v = round(v / 1000)
    if not day or not c or not o: return None
    return [day, o, h or c, l or c, c, v]

path = sys.argv[1] if len(sys.argv) > 1 else 'quotes.json'
try: old = json.load(open(path))
except Exception: old = {'bars': {}}
out = {'updated': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%m/%d %H:%M KST'), 'bars': {}}
for k, u in SRC.items():
    rows = {b[0]: b for b in old.get('bars', {}).get(k, [])}
    try:
        b = bar(k, u)
        if b: rows[b[0]] = b
    except Exception as e:
        print(k, 'fail', e)
    out['bars'][k] = [rows[d] for d in sorted(rows)][-40:]
json.dump(out, open(path, 'w'), ensure_ascii=False, separators=(',', ':'))
print(out['updated'], {k: v[-1] if v else None for k, v in out['bars'].items()})
