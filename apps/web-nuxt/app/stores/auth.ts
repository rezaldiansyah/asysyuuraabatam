import { defineStore } from 'pinia'

interface User {
    id: number
    nik: string
    name: string
    full_name?: string
    email: string | null
    role: { code: string; name: string; permissions?: string[] } | null
    units: string[]
    must_change_password?: boolean
}

interface AuthState {
    token: string | null
    user: User | null
    isAuthenticated: boolean
}

export const useAuthStore = defineStore('auth', {
    state: (): AuthState => ({
        token: null,
        user: null,
        isAuthenticated: false,
    }),

    getters: {
        getUser: (state) => state.user,
        getToken: (state) => {
            if (state.token) return state.token
            if (import.meta.client) {
                return localStorage.getItem('token')
            }
            return null
        },
        isLoggedIn: (state) => state.isAuthenticated || (import.meta.client && !!localStorage.getItem('token')),
        userRole: (state) => state.user?.role || null,
    },

    actions: {
        setAuth(token: string, user: User) {
            this.token = token
            this.user = user
            this.isAuthenticated = true

            // Persist to localStorage and cookie
            if (import.meta.client) {
                localStorage.setItem('token', token)
                localStorage.setItem('user', JSON.stringify(user))
                document.cookie = `auth_token=${encodeURIComponent(token)}; path=/; max-age=${7 * 24 * 3600}; SameSite=Lax`
            }
        },

        logout() {
            this.token = null
            this.user = null
            this.isAuthenticated = false

            if (import.meta.client) {
                localStorage.removeItem('token')
                localStorage.removeItem('user')
                document.cookie = 'auth_token=; path=/; max-age=0'
            }
        },

        initAuth() {
            if (import.meta.client) {
                let token = localStorage.getItem('token')
                const userStr = localStorage.getItem('user')

                if (!token) {
                    const match = document.cookie.match(/(?:^|; )auth_token=([^;]*)/)
                    if (match && match[1]) {
                        token = decodeURIComponent(match[1])
                    }
                }

                if (token && userStr) {
                    try {
                        const user = JSON.parse(userStr)
                        this.token = token
                        this.user = user
                        this.isAuthenticated = true
                    } catch {
                        this.logout()
                    }
                } else if (token) {
                    this.token = token
                    this.isAuthenticated = true
                }
            }
        },
    },
})
