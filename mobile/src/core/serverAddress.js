// Turn whatever the user typed or scanned into the server's WebSocket URL.
//
// Accepted:
//   192.168.0.247                      -> ws://192.168.0.247:8080/ws/edge
//   192.168.0.247:9000                 -> ws://192.168.0.247:9000/ws/edge
//   https://192.168.0.247:8443/phone   (the dashboard's phone QR) -> ws://192.168.0.247:8080/ws/edge
//   http://mac.local:8080/dashboard    -> ws://mac.local:8080/ws/edge
//   ws://host:port/ws/edge             -> unchanged
//   balltracker://connect?ws=<url>     (the dashboard's app QR) -> <url>

export const DEFAULT_HTTP_PORT = 8080;
const BROWSER_HTTPS_PORT = 8443;

/**
 * @param {string} input
 * @returns {string | null} ws:// or wss:// URL, or null if it can't be understood
 */
export function toEdgeUrl(input) {
  let s = (input || '').trim();
  if (!s) return null;
  const app = /^balltracker:\/\/connect\?(.*)$/i.exec(s);
  if (app) {
    const params = new Map(app[1].split('&').map((kv) => {
      const i = kv.indexOf('=');
      return i < 0 ? [kv, ''] : [kv.slice(0, i), decodeURIComponent(kv.slice(i + 1))];
    }));
    const ws = params.get('ws');
    return ws && /^wss?:\/\//i.test(ws) ? ws : null;
  }
  if (/^wss?:\/\//i.test(s)) {
    const m = /^(wss?):\/\/([^/?#]+)(\/[^?#]*)?/i.exec(s);
    if (!m) return null;
    const path = m[3] && m[3] !== '/' ? m[3] : '/ws/edge';
    return `${m[1].toLowerCase()}://${m[2]}${path}`;
  }
  let scheme = '';
  const sm = /^(https?):\/\//i.exec(s);
  if (sm) {
    scheme = sm[1].toLowerCase();
    s = s.slice(sm[0].length);
  }
  const hostPort = s.split(/[/?#]/)[0];
  const hp = /^(\[[0-9a-f:]+\]|[a-z0-9.-]+)(?::(\d{1,5}))?$/i.exec(hostPort);
  if (!hp) return null;
  const host = hp[1];
  let port = hp[2] ? Number(hp[2]) : DEFAULT_HTTP_PORT;
  // The phone page runs on the HTTPS port; the app talks plain ws:// on the HTTP port.
  if (scheme === 'https' && (port === BROWSER_HTTPS_PORT || !hp[2])) port = DEFAULT_HTTP_PORT;
  if (port < 1 || port > 65535) return null;
  return `ws://${host}:${port}/ws/edge`;
}

/**
 * Short form for display: "192.168.0.247:8080".
 * @param {string} url
 */
export function displayHost(url) {
  const m = /^wss?:\/\/([^/]+)/i.exec(url || '');
  return m ? m[1] : url;
}
