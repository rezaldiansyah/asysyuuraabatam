import { useAuthStore } from '~/stores/auth'

interface FetchOptions {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
    body?: any
    headers?: Record<string, string>
}

export function useApi() {
    const config = useRuntimeConfig()
    const authStore = useAuthStore()

    const baseUrl = (config.public.apiBase || '').replace(/\/$/, '')

    function resolveToken(): string | null {
        if (authStore.token) return authStore.token
        if (import.meta.client) {
            const lsToken = localStorage.getItem('token')
            if (lsToken) {
                authStore.initAuth()
                return lsToken
            }
            const match = document.cookie.match(/(?:^|; )auth_token=([^;]*)/)
            if (match && match[1]) {
                const cookieToken = decodeURIComponent(match[1])
                authStore.initAuth()
                return cookieToken
            }
        }
        return null
    }

    async function fetch<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...options.headers,
        }

        // Add auth token if available
        const token = resolveToken()
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
        }

        const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`

        const response = await $fetch<T>(url, {
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
        const token = resolveToken()
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
        }

        const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`

        const response = await $fetch<{ url: string }>(url, {
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
