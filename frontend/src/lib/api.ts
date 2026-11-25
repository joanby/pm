export const authedFetch = (token: string, path: string, init: RequestInit = {}) =>
  fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...init.headers,
    },
  });

export const apiError = async (response: Response, fallback: string): Promise<never> => {
  const body = await response.json().catch(() => null);
  throw new Error(body?.detail ?? fallback);
};
