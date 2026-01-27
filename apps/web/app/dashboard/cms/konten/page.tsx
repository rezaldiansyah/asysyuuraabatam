"use client"

import { useEffect, useState } from "react"
import { Save, Loader2 } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { ListEditor } from "@/components/dashboard/cms/ListEditor"

const DEFAULT_FEATURES = [
    { id: "1", icon: "BookOpen", title: "Kurikulum Terpadu", description: "Memadukan Kurikulum Nasional (Merdeka) dengan Kurikulum Khas Sekolah Islam Terpadu." },
    { id: "2", icon: "Heart", title: "Bina Pribadi Islami", description: "Pembentukan karakter (adab & akhlaq) yang intensif melalui mentoring dan keteladanan." },
    { id: "3", icon: "Sun", title: "Program Tahfidz", description: "Target hafalan yang terukur dengan metode yang menyenangkan sesuai jenjang usia." },
    { id: "4", icon: "Users", title: "Pengajar Berkualitas", description: "Didukung oleh asatidz/asatidzah yang kompeten, berdedikasi, dan menyayangi anak didik." },
    { id: "5", icon: "Trophy", title: "Ekstrakurikuler", description: "Beragam kegiatan penyaluran bakat dan minat siswa (Pramuka, Panahan, Futsal, dll)." },
    { id: "6", icon: "ShieldCheck", title: "Lingkungan Aman", description: "Lingkungan sekolah yang kondusif, aman, dan nyaman untuk tumbuh kembang anak." },
];

const CONTEXT_OPTIONS = [
    { value: "home", label: "Halaman Utama (Yayasan)" },
    { value: "unit_ra", label: "Unit RA" },
    { value: "unit_sdit", label: "Unit SDIT" },
    { value: "unit_smpit", label: "Unit SMPIT" },
]

export default function ContentPage() {
    const [context, setContext] = useState("home")
    const [isLoading, setIsLoading] = useState(false)

    // State for separate sections
    const [heroData, setHeroData] = useState({ title: "", body: "", cta_text: "", cta_link: "", image_url: "" })
    const [sambutanData, setSambutanData] = useState({ title: "", subtitle: "", body: "", image_url: "" })
    const [featuresData, setFeaturesData] = useState("") // JSON String
    const [testimonialsData, setTestimonialsData] = useState("") // JSON String

    // Helper to generate keys based on context
    const getKeys = (ctx: string) => {
        const prefix = ctx === 'home' ? 'home' : ctx.replace('unit_', '')
        return {
            hero: `${prefix}_hero`,
            sambutan: `${prefix}_sambutan`,
            features: `${prefix}_features`,
            testimonials: `${prefix}_testimonials`
        }
    }

    const fetchData = async () => {
        setIsLoading(true)
        const keys = getKeys(context)
        const API_URL = "http://localhost:8000"

        try {
            // Fetch All Sections in Parallel
            const [heroRes, sambutanRes, featuresRes, testimoRes] = await Promise.all([
                fetch(`${API_URL}/public/content/${keys.hero}`),
                fetch(`${API_URL}/public/content/${keys.sambutan}`),
                fetch(`${API_URL}/public/content/${keys.features}`),
                fetch(`${API_URL}/public/content/${keys.testimonials}`)
            ])

            if (heroRes.ok) setHeroData(await heroRes.json())
            else setHeroData({ title: "", body: "", cta_text: "", cta_link: "", image_url: "" })

            if (sambutanRes.ok) setSambutanData(await sambutanRes.json())
            else setSambutanData({ title: "", subtitle: "", body: "", image_url: "" })

            if (featuresRes.ok) {
                const data = await featuresRes.json()
                const jsonContent = data.content_json
                if (jsonContent && jsonContent !== "[]" && jsonContent !== "null") {
                    setFeaturesData(jsonContent)
                } else {
                    // Fallback to default if Home and empty
                    setFeaturesData(context === 'home' ? JSON.stringify(DEFAULT_FEATURES) : "[]")
                }
            } else {
                setFeaturesData(context === 'home' ? JSON.stringify(DEFAULT_FEATURES) : "[]")
            }

            if (testimoRes.ok) {
                const data = await testimoRes.json()
                setTestimonialsData(data.content_json || "[]")
            } else setTestimonialsData("[]")

        } catch (e) {
            console.error(e)
            toast.error("Gagal memuat data konten")
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [context])

    const saveSection = async (section: 'hero' | 'sambutan' | 'features' | 'testimonials') => {
        setIsLoading(true)
        const keys = getKeys(context)
        const API_URL = "http://localhost:8000"
        const token = localStorage.getItem("token")

        let payload = {}
        let key = ""

        if (section === 'hero') {
            key = keys.hero
            payload = { section_key: key, ...heroData }
        } else if (section === 'sambutan') {
            key = keys.sambutan
            payload = { section_key: key, ...sambutanData }
        } else if (section === 'features') {
            key = keys.features
            payload = { section_key: key, content_json: featuresData }
        } else if (section === 'testimonials') {
            key = keys.testimonials
            payload = { section_key: key, content_json: testimonialsData }
        }

        if (!token) {
            toast.error("Anda belum login", { description: "Silakan login kembali." })
            window.location.href = "/login"
            setIsLoading(false)
            return
        }

        try {
            const res = await fetch(`${API_URL}/cms/content/${key}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            })

            if (res.status === 401) {
                localStorage.removeItem("token")
                throw new Error("SESSION_EXPIRED")
            }

            if (!res.ok) throw new Error("Failed to save")
            toast.success(`Bagian ${section} berhasil disimpan!`)
        } catch (e: any) {
            if (e.message === "SESSION_EXPIRED") {
                toast.error("Sesi Anda telah berakhir", { description: "Silakan login kembali untuk menyimpan perubahan." })
                setTimeout(() => window.location.href = "/login", 1500)
            } else {
                console.error(e)
                toast.error("Gagal menyimpan perubahan")
            }
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h3 className="text-lg font-medium">Manajemen Konten Halaman</h3>
                    <p className="text-sm text-muted-foreground">
                        Kelola konten untuk Halaman Utama dan Unit Pendidikan.
                    </p>
                </div>
                <div className="w-full md:w-64">
                    <Select value={context} onValueChange={setContext}>
                        <SelectTrigger>
                            <SelectValue placeholder="Pilih Halaman" />
                        </SelectTrigger>
                        <SelectContent>
                            {CONTEXT_OPTIONS.map(opt => (
                                <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>
            <Separator />

            <Tabs defaultValue="hero" className="w-full">
                <TabsList className="grid w-full grid-cols-4 md:w-auto md:inline-flex">
                    <TabsTrigger value="hero">Banner Utama</TabsTrigger>
                    <TabsTrigger value="sambutan">Sambutan</TabsTrigger>
                    <TabsTrigger value="features">Keunggulan</TabsTrigger>
                    <TabsTrigger value="testimonials">Testimoni</TabsTrigger>
                </TabsList>

                {/* HERO SECTION */}
                <TabsContent value="hero" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Hero Section ({CONTEXT_OPTIONS.find(c => c.value === context)?.label})</CardTitle>
                            <CardDescription>Bagian paling atas halaman yang pertama kali dilihat pengunjung.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid gap-2">
                                <Label>Judul Utama (Headline)</Label>
                                <Input value={heroData.title || ""} onChange={e => setHeroData({ ...heroData, title: e.target.value })} placeholder="Judul menarik..." />
                            </div>
                            <div className="grid gap-2">
                                <Label>Deskripsi</Label>
                                <Textarea value={heroData.body || ""} onChange={e => setHeroData({ ...heroData, body: e.target.value })} placeholder="Deskripsi singkat..." rows={4} />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <Label>Teks Tombol</Label>
                                    <Input value={heroData.cta_text || ""} onChange={e => setHeroData({ ...heroData, cta_text: e.target.value })} placeholder="Daftar Sekarang" />
                                </div>
                                <div className="grid gap-2">
                                    <Label>Link Tombol</Label>
                                    <Input value={heroData.cta_link || ""} onChange={e => setHeroData({ ...heroData, cta_link: e.target.value })} placeholder="/daftar" />
                                </div>
                            </div>
                            <div className="grid gap-2">
                                <Label>URL Gambar Latar (Opsional)</Label>
                                <Input value={heroData.image_url || ""} onChange={e => setHeroData({ ...heroData, image_url: e.target.value })} placeholder="http://..." />
                            </div>
                            <Button onClick={() => saveSection('hero')} disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                <Save className="mr-2 h-4 w-4" /> Simpan Hero
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* SAMBUTAN */}
                <TabsContent value="sambutan" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Sambutan Pimpinan</CardTitle>
                            <CardDescription>
                                {context === 'home' ? 'Sambutan Ketua Yayasan' : 'Sambutan Kepala Sekolah Unit'}
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid gap-2">
                                <Label>Judul Sambutan</Label>
                                <Input value={sambutanData.title || ""} onChange={e => setSambutanData({ ...sambutanData, title: e.target.value })} placeholder="Sambutan Ketua Yayasan..." />
                            </div>
                            <div className="grid gap-2">
                                <Label>Sub-judul / Jabatan</Label>
                                <Input value={sambutanData.subtitle || ""} onChange={e => setSambutanData({ ...sambutanData, subtitle: e.target.value })} placeholder="Ketua Yayasan Asy-Syuuraa Batam" />
                            </div>
                            <div className="grid gap-2">
                                <Label>Isi Sambutan</Label>
                                <Textarea value={sambutanData.body || ""} onChange={e => setSambutanData({ ...sambutanData, body: e.target.value })} placeholder="Assalamu'alaikum..." rows={8} />
                            </div>
                            <div className="grid gap-2">
                                <Label>URL Foto Pimpinan</Label>
                                <Input value={sambutanData.image_url || ""} onChange={e => setSambutanData({ ...sambutanData, image_url: e.target.value })} placeholder="http://..." />
                            </div>
                            <Button onClick={() => saveSection('sambutan')} disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                <Save className="mr-2 h-4 w-4" /> Simpan Sambutan
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* FEATURES (KEUNGGULAN) */}
                <TabsContent value="features" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Keunggulan & Fasilitas</CardTitle>
                            <CardDescription>Daftar poin-poin keunggulan atau fasilitas utama.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <ListEditor
                                value={featuresData}
                                onChange={setFeaturesData}
                                titleLabel="Judul Keunggulan"
                                descLabel="Deskripsi Singkat"
                                imageLabel="Icon/Gambar URL"
                            />
                            <Button onClick={() => saveSection('features')} disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                <Save className="mr-2 h-4 w-4" /> Simpan Keunggulan
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* TESTIMONIALS */}
                <TabsContent value="testimonials" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Testimoni & Kata Mereka</CardTitle>
                            <CardDescription>Apa kata orang tua, alumni, atau tokoh.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <ListEditor
                                value={testimonialsData}
                                onChange={setTestimonialsData}
                                titleLabel="Nama Tokoh"
                                descLabel="Isi Testimoni"
                                imageLabel="Foto Profil URL"
                            />
                            <Button onClick={() => saveSection('testimonials')} disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                <Save className="mr-2 h-4 w-4" /> Simpan Testimoni
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

            </Tabs>
        </div>
    )
}
