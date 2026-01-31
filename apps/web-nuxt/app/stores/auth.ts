import { defineStore } from 'pinia'

interface User {
    id: number
    nik: string
    name: string
    email: string | null
    role: string
    units: string[]
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
        getToken: (state) => state.token,
        isLoggedIn: (state) => state.isAuthenticated,
        userRole: (state) => state.user?.role || null,
    },

    actions: {
        setAuth(token: string, user: User) {
            this.token = token
            this.user = user
            this.isAuthenticated = true

            // Persist to localStorage
            if (import.meta.client) {
                localStorage.setItem('token', token)
                localStorage.setItem('user', JSON.stringify(user))
            }
        },

        logout() {
            this.token = null
            this.user = null
            this.isAuthenticated = false

            if (import.meta.client) {
                localStorage.removeItem('token')
                localStorage.removeItem('user')
            }
        },

        initAuth() {
            if (import.meta.client) {
                const token = localStorage.getItem('token')
                const userStr = localStorage.getItem('user')

                if (token && userStr) {
                    try {
                        const user = JSON.parse(userStr)
                        this.token = token
                        this.user = user
                        this.isAuthenticated = true
                    } catch {
                        this.logout()
                    }
                }
            }
        },
    },
})
