// 클라우드플레어 워커: 네이버 시세를 CORS 허용으로 넘겨준다 (선택 사항, 약 8초 간격 갱신용)
const SRC = {
  NDX: 'https://polling.finance.naver.com/api/realtime/worldstock/index/.NDX',
  SNDK: 'https://polling.finance.naver.com/api/realtime/worldstock/stock/SNDK.O',
  KOSPI: 'https://polling.finance.naver.com/api/realtime/domestic/index/KOSPI',
  SEC: 'https://polling.finance.naver.com/api/realtime/domestic/stock/005930',
  SKH: 'https://polling.finance.naver.com/api/realtime/domestic/stock/000660',
};
const n = x => { const v = parseFloat(String(x ?? '').replace(/,/g, '')); return isFinite(v) ? v : null };
export default {
  async fetch() {
    const bars = {};
    await Promise.all(Object.entries(SRC).map(async ([k, u]) => {
      try {
        const r = await fetch(u, { headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://m.stock.naver.com/' }, cf: { cacheTtl: 5 } });
        const d = (await r.json()).datas[0], day = (d.localTradedAt || '').slice(0, 10);
        const o = n(d.openPriceRaw ?? d.openPrice), h = n(d.highPriceRaw ?? d.highPrice), l = n(d.lowPriceRaw ?? d.lowPrice), c = n(d.closePriceRaw ?? d.closePrice);
        if (day && o && c) bars[k] = [[day, o, h ?? c, l ?? c, c, (n(d.accumulatedTradingVolumeRaw) ?? 0) / (k === 'KOSPI' ? 1000 : 1)]];
      } catch (e) {}
    }));
    const updated = new Date(Date.now() + 9 * 3600e3).toISOString().slice(11, 19) + ' KST';
    return new Response(JSON.stringify({ updated, bars }), { headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*', 'cache-control': 'no-store' } });
  },
};
