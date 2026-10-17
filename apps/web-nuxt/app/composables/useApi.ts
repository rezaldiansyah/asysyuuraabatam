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

        try {
            const response = await $fetch<T>(url, {
                method: options.method || 'GET',
                headers,
                body: options.body ? JSON.stringify(options.body) : undefined,
            })
            return response
        } catch (err: any) {
            const status = err?.statusCode || err?.status || err?.response?.status
            if (status === 401) {
                console.warn('[useApi] Session 401 Unauthorized. Redirecting to login...')
                authStore.logout()
                if (import.meta.client) {
                    navigateTo('/login')
                }
            }
            throw err
        }
    }

    function xhrUpload(url: string, file: File, token: string | null): Promise<{ url: string }> {
        return new Promise((resolve, reject) => {
            if (typeof XMLHttpRequest === 'undefined') {
                return reject(new Error('XMLHttpRequest not available'))
            }
            const xhr = new XMLHttpRequest()
            const formData = new FormData()
            formData.append('file', file)

            xhr.open('POST', url, true)
            if (token) {
                xhr.setRequestHeader('Authorization', `Bearer ${token}`)
            }

            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const json = JSON.parse(xhr.responseText)
                        resolve(json)
                    } catch {
                        reject(new Error('Respon server tidak valid'))
                    }
                } else {
                    let errMsg = `Server error (${xhr.status})`
                    try {
                        const errJson = JSON.parse(xhr.responseText)
                        errMsg = errJson.detail || errMsg
                    } catch {}
                    const err: any = new Error(errMsg)
                    err.statusCode = xhr.status
                    reject(err)
                }
            }

            xhr.onerror = () => {
                reject(new Error('Upload gagal: Terblokir oleh ekstensi browser (AdBlock) atau koneksi terputus.'))
            }

            xhr.send(formData)
        })
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
        // /api/assets/store uses neutral naming to bypass adblocker filter rules (e.g. EasyList /upload filters)
        const isClient = typeof window !== 'undefined'
        const candidateUrls: string[] = []

        if (endpoint === '/cms/upload' || endpoint === 'cms/upload') {
            if (isClient) {
                candidateUrls.push('/api/assets/store')
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
            // Attempt 1: Standard fetch
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
                console.warn(`[useApi.upload:fetch] Failed on ${url}:`, err?.message || err)
            }

            // Attempt 2: XMLHttpRequest fallback (bypasses some browser extension fetch intercepts)
            if (isClient) {
                try {
                    const response = await xhrUpload(url, file, token)
                    return response
                } catch (xhrErr: any) {
                    lastError = xhrErr
                    const status = xhrErr?.statusCode
                    if (status && status >= 400 && status < 500 && status !== 404) {
                        throw xhrErr
                    }
                    console.warn(`[useApi.upload:xhr] Failed on ${url}:`, xhrErr?.message || xhrErr)
                }
            }
        }

        // If error is caused by browser blocking
        if (lastError && (lastError.message?.includes('Failed to fetch') || lastError.message?.includes('ekstensi'))) {
            throw new Error('Upload gagal dikirim. Terdeteksi ekstensi browser (AdBlock/Privacy) memblokir request. Mohon nonaktifkan AdBlock untuk domain ini atau gunakan Tab Incognito.')
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
