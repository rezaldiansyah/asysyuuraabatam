"use client"

import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Save, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

const formSchema = z.object({
    section_key: z.string(),
    title: z.string().min(3),
    subtitle: z.string().optional(),
    body: z.string().optional(),
    cta_text: z.string().optional(),
    cta_link: z.string().optional(),
})

export default function ContentPage() {
    const [isLoading, setIsLoading] = useState(false)

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            section_key: "home_hero",
            title: "",
            body: "",
            cta_text: "Daftar Sekarang",
        },
    })

    // Load initial data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const API_URL = "http://localhost:8000"
                const res = await fetch(`${API_URL}/public/content/home_hero`)
                if (res.ok) {
                    const data = await res.json()
                    form.reset(data)
                } else {
                    // Pre-fill default if not exists
                    form.reset({
                        section_key: "home_hero",
                        title: "Mendidik Generasi Qurani",
                        body: "Sekolah Islam Terpadu Asy-Syuuraa Batam berkomitmen mencetak pemimpin masa depan yang cerdas, berwawasan global, dan berakhlak mulia.",
                        cta_text: "Daftar Sekarang"
                    })
                }
            } catch (error) {
                console.error(error)
            }
        }
        fetchData()
    }, [])

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/cms/content/home_hero`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(values),
            })

            if (!response.ok) throw new Error("Gagal menyimpan konten")

            toast.success("Konten halaman berhasil diperbarui")
        } catch (error) {
            toast.error("Gagal menyimpan konten")
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-medium">CMS Landing Page</h3>
                <p className="text-sm text-muted-foreground">
                    Atur konten yang muncul di halaman depan website.
                </p>
            </div>
            <Separator />

            <Card>
                <CardHeader>
                    <CardTitle>Hero Section</CardTitle>
                    <CardDescription>Bagian paling atas (Banner utama)</CardDescription>
                </CardHeader>
                <CardContent>
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                            <FormField
                                control={form.control}
                                name="title"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Judul Utama (Headline)</FormLabel>
                                        <FormControl>
                                            <Input placeholder="Contoh: Mendidik Generasi Qurani" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="body"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Deskripsi</FormLabel>
                                        <FormControl>
                                            <Textarea
                                                placeholder="Deskripsi singkat sekolah..."
                                                className="resize-none"
                                                rows={4}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <div className="grid grid-cols-2 gap-4">
                                <FormField
                                    control={form.control}
                                    name="cta_text"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Teks Tombol</FormLabel>
                                            <FormControl>
                                                <Input placeholder="Daftar Sekarang" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="cta_link"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Link Tombol</FormLabel>
                                            <FormControl>
                                                <Input placeholder="/daftar" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                            </div>

                            <Button type="submit" disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                <Save className="mr-2 h-4 w-4" /> Simpan Perubahan
                            </Button>
                        </form>
                    </Form>
                </CardContent>
            </Card>
        </div>
    )
}
