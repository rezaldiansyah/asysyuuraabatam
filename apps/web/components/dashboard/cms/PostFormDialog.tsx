"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Plus, Loader2, Edit, FileText, Upload, ImageIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
    FormDescription,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { toast } from "sonner"
import { RichTextEditor } from "./RichTextEditor"

const formSchema = z.object({
    title: z.string().min(5, { message: "Judul minimal 5 karakter." }),
    slug: z.string().min(3),
    content: z.string().min(20, { message: "Konten terlalu pendek." }),
    image_url: z.string().optional(),
    is_published: z.boolean(),
})

type FormValues = z.infer<typeof formSchema>

export function PostFormDialog({ post, onSuccess }: { post?: any, onSuccess?: () => void }) {
    const [open, setOpen] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [isUploading, setIsUploading] = useState(false)

    const form = useForm<FormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            title: "",
            slug: "",
            content: "",
            image_url: "",
            is_published: true,
        },
    })

    // Load data if editing
    useEffect(() => {
        if (post && open) {
            form.reset({
                title: post.title,
                slug: post.slug,
                content: post.content,
                image_url: post.image_url || "",
                is_published: post.is_published,
            })
        } else if (!post && open) {
            form.reset({
                title: "",
                slug: "",
                content: "",
                image_url: "",
                is_published: true,
            })
        }
    }, [post, open, form])

    // Auto-slug generator (if not manually edited)
    const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const title = e.target.value
        form.setValue("title", title)
        if (!post) { // Only auto-gen for new posts
            const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "")
            form.setValue("slug", slug)
        }
    }

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

    const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        setIsUploading(true)
        try {
            const formData = new FormData()
            formData.append('file', file)

            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/cms/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            })

            if (!response.ok) throw new Error('Upload failed')

            const data = await response.json()
            form.setValue("image_url", data.url)
            toast.success("Gambar berhasil diunggah")
        } catch (error) {
            console.error(error)
            toast.error("Gagal mengupload gambar")
        } finally {
            setIsUploading(false)
            e.target.value = ""
        }
    }

    async function onSubmit(values: FormValues) {
        setIsLoading(true)
        try {
            const token = localStorage.getItem("token")
            const url = post
                ? `${API_URL}/cms/posts/${post.id}`
                : `${API_URL}/cms/posts`

            const method = post ? "PUT" : "POST"

            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(values),
            })

            if (!response.ok) {
                throw new Error("Gagal menyimpan berita")
            }

            toast.success(post ? "Berita berhasil diperbarui" : "Berita berhasil dibuat")
            setOpen(false)
            form.reset()
            onSuccess?.()
        } catch (error) {
            toast.error("Gagal menyimpan berita")
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                {post ? (
                    <Button variant="ghost" size="icon"><Edit className="h-4 w-4" /></Button>
                ) : (
                    <Button>
                        <Plus className="mr-2 h-4 w-4" /> Berita Baru
                    </Button>
                )}
            </DialogTrigger>
            <DialogContent className="sm:max-w-[800px]">
                <DialogHeader>
                    <DialogTitle>{post ? "Edit Berita" : "Buat Berita Baru"}</DialogTitle>
                    <DialogDescription>
                        Bagikan informasi terbaru seputar sekolah.
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="title"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Judul Berita</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Contoh: Pendaftaran Siswa Baru Dibuka" {...field} onChange={(e) => { field.onChange(e); handleTitleChange(e); }} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="slug"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>URL Slug (Unik)</FormLabel>
                                    <FormControl>
                                        <Input placeholder="pendaftaran-siswa-baru" {...field} />
                                    </FormControl>
                                    <FormDescription>Link: /berita/{field.value}</FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="image_url"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Featured Image (Opsional)</FormLabel>
                                    <div className="space-y-3">
                                        <div className="flex gap-2">
                                            <FormControl>
                                                <Input placeholder="https://... atau upload gambar" {...field} />
                                            </FormControl>
                                            <div className="relative">
                                                <input
                                                    type="file"
                                                    className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                                                    accept="image/*"
                                                    onChange={handleImageUpload}
                                                    disabled={isUploading}
                                                />
                                                <Button type="button" variant="outline" size="icon" disabled={isUploading}>
                                                    {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                                                </Button>
                                            </div>
                                        </div>
                                        {field.value && (
                                            <div className="relative rounded-md overflow-hidden border bg-muted/30">
                                                <img
                                                    src={field.value}
                                                    alt="Preview"
                                                    className="w-full h-40 object-cover"
                                                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                                                />
                                            </div>
                                        )}
                                    </div>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="content"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Isi Berita (Konten Lengkap)</FormLabel>
                                    <FormControl>
                                        <RichTextEditor
                                            content={field.value}
                                            onChange={field.onChange}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="is_published"
                            render={({ field }) => (
                                <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                                    <FormControl>
                                        <Checkbox
                                            checked={field.value}
                                            onCheckedChange={field.onChange}
                                        />
                                    </FormControl>
                                    <div className="space-y-1 leading-none">
                                        <FormLabel>
                                            Publikasikan Langsung
                                        </FormLabel>
                                        <FormDescription>
                                            Jika tidak dicentang, berita akan disimpan sebagai draft.
                                        </FormDescription>
                                    </div>
                                </FormItem>
                            )}
                        />
                        <DialogFooter>
                            <Button type="submit" disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Simpan
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
