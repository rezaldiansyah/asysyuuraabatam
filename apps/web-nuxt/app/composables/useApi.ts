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

        // Build candidate URLs with same-origin prioritized on client
        // This completely eliminates CORS preflight failures and browser adblocker interference
        const isClient = typeof window !== 'undefined'
        const candidateUrls: string[] = []

        if (endpoint === '/cms/upload' || endpoint === 'cms/upload') {
            if (isClient) {
                candidateUrls.push('/api/upload')
                candidateUrls.push('/api-proxy/cms/upload')
            }
            const directUrl = `${baseUrl}/cms/upload`
            if (!candidateUrls.includes(directUrl)) {
                candidateUrls.push(directUrl)
            }
        } else if (endpoint === '/cms/upload/batch' || endpoint === 'cms/upload/batch') {
            if (isClient) {
                candidateUrls.push('/api/upload-batch')
                candidateUrls.push('/api-proxy/cms/upload/batch')
            }
            const directUrl = `${baseUrl}/cms/upload/batch`
            if (!candidateUrls.includes(directUrl)) {
                candidateUrls.push(directUrl)
            }
        } else {
            const resolvedUrl = endpoint.startsWith('http')
                ? endpoint
                : `${baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`
            candidateUrls.push(resolvedUrl)
        }

        let lastError: any = null
        for (const url of candidateUrls) {
            try {
                const response = await $fetch<{ url: string }>(url, {
                    method: 'POST',
                    headers,
                    body: formData,
                })
                return response
            } catch (err: any) {
                lastError = err
                const status = err?.statusCode || err?.status || err?.response?.status
                // If it's a 4xx validation or auth error (not network error/404), throw immediately
                if (status && status >= 400 && status < 500 && status !== 404) {
                    throw err
                }
                console.warn(`[useApi.upload] Failed on ${url}:`, err?.message || err)
            }
        }

        throw lastError
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
