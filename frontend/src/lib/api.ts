const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost/api';

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

export async function fetchAPI(endpoint: string, options: RequestInit = {}): Promise<any> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((options.headers as any) || {}),
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && endpoint !== '/auth/refresh' && endpoint !== '/auth/login') {
    if (isRefreshing) {
      return new Promise(function(resolve, reject) {
        failedQueue.push({ resolve, reject });
      }).then(token => {
        return fetchAPI(endpoint, options);
      }).catch(err => {
        throw err;
      });
    }

    isRefreshing = true;
    const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;

    if (refreshToken) {
      try {
        const refreshResponse = await fetch(`${API_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken })
        });
        
        if (refreshResponse.ok) {
           const data = await refreshResponse.json();
           localStorage.setItem('token', data.access_token);
           localStorage.setItem('refresh_token', data.refresh_token);
           document.cookie = `token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`;
           
           processQueue(null, data.access_token);
           isRefreshing = false;
           
           // Retry original request
           return fetchAPI(endpoint, options);
        } else {
           throw new Error('Refresh failed');
        }
      } catch (err) {
        processQueue(err as Error, null);
        isRefreshing = false;
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        if (typeof window !== 'undefined') window.location.href = '/login';
        throw new APIError(401, 'Session expired');
      }
    } else {
       isRefreshing = false;
       localStorage.removeItem('token');
       document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
       if (typeof window !== 'undefined') window.location.href = '/login';
       throw new APIError(401, 'Unauthorized');
    }
  }

  if (!response.ok) {
    let errorMessage = 'API request failed';
    try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
    } catch(e) {}
    throw new APIError(response.status, errorMessage);
  }

  if (response.status === 204) {
    return null;
  }
  
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.indexOf("application/json") !== -1) {
    return response.json();
  }
  return response.text();
}
