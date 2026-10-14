import { computed } from 'vue'
import { useAuthStore } from '~/stores/auth'

export type CrudAction = 'create' | 'read' | 'update' | 'delete' | 'c' | 'r' | 'u' | 'd'

export function usePermission() {
  const authStore = useAuthStore()

  const isSuperadmin = computed(() => {
    const role = authStore.user?.role
    const code = (role && typeof role === 'object' ? role.code : role) || ''
    return code === 'superadmin'
  })

  const userRole = computed(() => {
    const role = authStore.user?.role
    return (role && typeof role === 'object' ? role.code : role) || 'guest'
  })

  const permissions = computed<string[]>(() => {
    const role = authStore.user?.role
    if (!role || typeof role !== 'object') return []
    return (role as any).permissions || []
  })

  /**
   * Check if current user has permission to perform action on featureKey.
   * e.g. can('internal.dokumen', 'delete')
   * e.g. can('akademik.kalender', 'create')
   */
  function can(featureKey: string, action: CrudAction): boolean {
    if (isSuperadmin.value) return true

    const actMap: Record<string, string> = {
      'c': 'create', 'create': 'create',
      'r': 'read', 'read': 'read',
      'u': 'update', 'update': 'update',
      'd': 'delete', 'delete': 'delete'
    }
    const act = actMap[action] || action
    const perms = permissions.value

    // 1. Wildcard access
    if (perms.includes('*') || perms.includes(`${featureKey}:*`)) {
      return true
    }

    // 2. Exact action token
    if (perms.includes(`${featureKey}:${act}`)) {
      return true
    }

    // 3. Exact feature token without action (legacy format)
    if (perms.includes(featureKey)) {
      return true
    }

    // 4. If checking read access, and parent module is allowed without explicit child restrictions
    const parentKey = featureKey.split('.')[0]
    if (act === 'read' && perms.includes(parentKey)) {
      const hasChildExplicit = perms.some(p => p.startsWith(`${featureKey}:`))
      if (!hasChildExplicit) {
        return true
      }
    }

    return false
  }

  function canAny(featureKey: string, actions: CrudAction[]): boolean {
    if (isSuperadmin.value) return true
    return actions.some(a => can(featureKey, a))
  }

  function hasMenuAccess(menuKey: string): boolean {
    if (isSuperadmin.value) return true
    const perms = permissions.value
    if (perms.includes(menuKey)) return true
    if (perms.includes(`${menuKey}:read`) || perms.includes(`${menuKey}:create`)) return true
    return perms.some(p => p.startsWith(`${menuKey}.`))
  }

  return {
    can,
    canAny,
    hasMenuAccess,
    isSuperadmin,
    userRole,
    permissions
  }
}
