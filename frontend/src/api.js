const API_BASE = import.meta.env.VITE_API_BASE || "";

function resolveUrl(pathOrUrl) {
  if (pathOrUrl.startsWith("http")) return pathOrUrl;
  // Use dev proxy: /api gets proxied to backend.
  return `${API_BASE}${pathOrUrl}`;
}

export async function apiPost(path, body) {
  const url = resolveUrl(path);
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) return { ok: false, status: resp.status, error: data.message || data };
  return { ok: true, status: resp.status, data, json: async () => data };
}

export async function apiGet(path, headers = {}) {
  const url = resolveUrl(path);
  const resp = await fetch(url, { method: "GET", headers });
  const data = await resp.json().catch(() => ({}));
  return { ok: resp.ok, status: resp.status, data, json: async () => data };
}

