import { useAuthStore } from '~/stores/auth'

interface FetchOptions {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
    body?: any
    headers?: Record<string, string>
}

export function useApi() {
    const config = useRuntimeConfig()
    const authStore = useAuthStore()

    const baseUrl = config.public.apiBase

    async function fetch<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...options.headers,
        }

        // Add auth token if available
        if (authStore.token) {
            headers['Authorization'] = `Bearer ${authStore.token}`
        }

        const response = await $fetch<T>(`${baseUrl}${endpoint}`, {
            method: options.method || 'GET',
            headers,
            body: options.body ? JSON.stringify(options.body) : undefined,
        })

        return response
    }

    // Upload file (multipart/form-data)
    async function upload(endpoint: string, file: File): Promise<{ url: string }> {
        const formData = new FormData()
        formData.append('file', file)

        const headers: Record<string, string> = {}
        if (authStore.token) {
            headers['Authorization'] = `Bearer ${authStore.token}`
        }

        const response = await $fetch<{ url: string }>(`${baseUrl}${endpoint}`, {
            method: 'POST',
            headers,
            body: formData,
        })

        return response
    }

    return {
        get: <T>(endpoint: string) => fetch<T>(endpoint),
        post: <T>(endpoint: string, body: any) => fetch<T>(endpoint, { method: 'POST', body }),
        put: <T>(endpoint: string, body: any) => fetch<T>(endpoint, { method: 'PUT', body }),
        patch: <T>(endpoint: string, body: any) => fetch<T>(endpoint, { method: 'PATCH', body }),
        delete: <T>(endpoint: string) => fetch<T>(endpoint, { method: 'DELETE' }),
        upload,
    }
}
