import { env } from "@/lib/env";

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

type Options = Omit<RequestInit, "body"> & {
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null>;
};

function requestInit(opts: Options): RequestInit {
  const { query: _query, body: _body, ...init } = opts;
  return init;
}

function buildUrl(path: string, query?: Options["query"]) {
  const base = env.apiBaseUrl.replace(/\/$/, "");
  const url = new URL(`${base}${path.startsWith("/") ? path : `/${path}`}`);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
    }
  }
  return url.toString();
}

async function handle<T>(res: Response): Promise<T> {
  const ct = res.headers.get("content-type") || "";
  const isJson = ct.includes("application/json");
  const data = isJson ? await res.json().catch(() => null) : await res.text().catch(() => null);
  if (!res.ok) {
    const msg =
      (isJson && data && (data as any).detail) ||
      (isJson && data && (data as any).message) ||
      res.statusText ||
      "Request failed";
    throw new ApiError(String(msg), res.status, data);
  }
  return data as T;
}

export const api = {
  async get<T>(path: string, opts: Options = {}): Promise<T> {
    const res = await fetch(buildUrl(path, opts.query), { ...requestInit(opts), method: "GET" });
    return handle<T>(res);
  },
  async post<T>(path: string, body?: unknown, opts: Options = {}): Promise<T> {
    const res = await fetch(buildUrl(path, opts.query), {
      ...requestInit(opts),
      method: "POST",
      headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handle<T>(res);
  },
  async put<T>(path: string, body?: unknown, opts: Options = {}): Promise<T> {
    const res = await fetch(buildUrl(path, opts.query), {
      ...requestInit(opts),
      method: "PUT",
      headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handle<T>(res);
  },
  async patch<T>(path: string, body?: unknown, opts: Options = {}): Promise<T> {
    const res = await fetch(buildUrl(path, opts.query), {
      ...requestInit(opts),
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handle<T>(res);
  },
  async del<T>(path: string, opts: Options = {}): Promise<T> {
    const res = await fetch(buildUrl(path, opts.query), { ...requestInit(opts), method: "DELETE" });
    return handle<T>(res);
  },
  async upload<T>(path: string, file: File, fields: Record<string, string> = {}): Promise<T> {
    const fd = new FormData();
    fd.append("file", file);
    for (const [k, v] of Object.entries(fields)) fd.append(k, v);
    const res = await fetch(buildUrl(path), { method: "POST", body: fd });
    return handle<T>(res);
  },
  async download(path: string, query?: Options["query"]): Promise<Blob> {
    const res = await fetch(buildUrl(path, query), { method: "GET" });
    if (!res.ok) throw new ApiError(res.statusText, res.status, null);
    return res.blob();
  },
};

export async function ping(): Promise<boolean> {
  try {
    const res = await fetch(buildUrl("/health"), { method: "GET" });
    return res.ok;
  } catch {
    return false;
  }
}
