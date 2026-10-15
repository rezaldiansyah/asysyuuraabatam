import { defineEventHandler, proxyRequest } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = (
    process.env.INTERNAL_API_URL ||
    process.env.NUXT_PUBLIC_API_BASE ||
    config.public.apiBase ||
    'https://api.asy-syuuraabatam.or.id'
  ).replace(/\/$/, '')

  const target = `${apiBase}/cms/upload/batch`
  return proxyRequest(event, target)
})
