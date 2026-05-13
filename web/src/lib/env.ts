export const env = {
  apiBaseUrl: (import.meta.env.VITE_API_BASE_URL as string) ?? "http://localhost:8000/api",
  appName: (import.meta.env.VITE_APP_NAME as string) ?? "Conversation Thematic Analysis",
  authMode: (import.meta.env.VITE_AUTH_MODE as string) ?? "disabled",
};
