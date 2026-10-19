export default defineNuxtRouteMiddleware((to) => {
    const authStore = useAuthStore()

    // Public password reset & recovery pages (always accessible without restriction)
    if (to.path === '/reset-password' || to.path === '/forgot-password') {
        return
    }

    // Initialize auth from localStorage on client
    if (import.meta.client && !authStore.isAuthenticated) {
        authStore.initAuth()
    }

    // Protect dashboard routes
    if (to.path.startsWith('/dashboard')) {
        if (!authStore.isAuthenticated) {
            return navigateTo('/login')
        }
        
        // Force change password check
        if (authStore.user?.must_change_password && to.path !== '/dashboard/force-change-password') {
            return navigateTo('/dashboard/force-change-password')
        }
    }

    // Redirect logged in users away from login page
    if (to.path === '/login' && authStore.isAuthenticated) {
        if (authStore.user?.must_change_password) {
            return navigateTo('/dashboard/force-change-password')
        }
        return navigateTo('/dashboard')
    }
})
