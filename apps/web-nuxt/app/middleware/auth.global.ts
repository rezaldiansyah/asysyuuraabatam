export default defineNuxtRouteMiddleware((to) => {
    const authStore = useAuthStore()

    // Initialize auth from localStorage on client
    if (import.meta.client && !authStore.isAuthenticated) {
        authStore.initAuth()
    }

    // Protect dashboard routes
    if (to.path.startsWith('/dashboard')) {
        if (!authStore.isAuthenticated) {
            return navigateTo('/login')
        }
    }

    // Redirect logged in users away from login page
    if (to.path === '/login' && authStore.isAuthenticated) {
        return navigateTo('/dashboard')
    }
})
