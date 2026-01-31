"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { FileText, Loader2 } from "lucide-react"

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
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { toast } from "sonner"

const formSchema = z.object({
    student_id: z.coerce.number().min(1, { message: "Pilih siswa." }),
    category_id: z.coerce.number().min(1, { message: "Pilih kategori." }),
    title: z.string().min(5, { message: "Judul tagihan minimal 5 karakter." }),
    amount: z.coerce.number().min(1, { message: "Nominal wajib diisi." }),
    due_date: z.string().optional(),
})

export function GenerateBillDialog({ onSuccess }: { onSuccess?: () => void }) {
    const [open, setOpen] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [students, setStudents] = useState<any[]>([])
    const [categories, setCategories] = useState<any[]>([])

    // Load data on open
    useEffect(() => {
        if (open) {
            const fetchData = async () => {
                const API_URL = "http://localhost:8000"
                const token = localStorage.getItem("token")
                const headers = { "Authorization": `Bearer ${token}` }

                try {
                    const [studRes, catRes] = await Promise.all([
                        fetch(`${API_URL}/academic/students`, { headers }),
                        fetch(`${API_URL}/finance/categories`, { headers })
                    ])
                    if (studRes.ok) setStudents(await studRes.json())
                    if (catRes.ok) setCategories(await catRes.json())
                } catch (e) {
                    console.error("Failed to load form data", e)
                }
            }
            fetchData()
        }
    }, [open])

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            student_id: 0,
            category_id: 0,
            title: "",
            amount: 0,
        },
    })

    // Auto-fill amount when category changes
    const watchCategory = form.watch("category_id")
    useEffect(() => {
        if (watchCategory) {
            const cat = categories.find(c => c.id === watchCategory)
            if (cat) {
                form.setValue("amount", cat.amount)
                form.setValue("title", `${cat.name} - ${new Date().toLocaleString('id-ID', { month: 'long', year: 'numeric' })}`)
            }
        }
    }, [watchCategory, categories, form])

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)
        try {
            const API_URL = "http://localhost:8000"
            const response = await fetch(`${API_URL}/finance/bills/generate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(values),
            })

            if (!response.ok) throw new Error("Gagal membuat tagihan")

            toast.success("Tagihan berhasil dibuat")
            setOpen(false)
            form.reset()
            onSuccess?.()
        } catch (error) {
            toast.error("Gagal membuat tagihan")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="bg-[var(--syuura-green)] hover:bg-[var(--syuura-green)]/90">
                    <FileText className="mr-2 h-4 w-4" /> Buat Tagihan
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Buat Tagihan Siswa</DialogTitle>
                    <DialogDescription>
                        Generate tagihan baru untuk siswa.
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="student_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Siswa</FormLabel>
                                    <Select onValueChange={(v) => field.onChange(parseInt(v))} defaultValue={field.value ? field.value.toString() : undefined}>
                                        <FormControl><SelectTrigger><SelectValue placeholder="Pilih Siswa" /></SelectTrigger></FormControl>
                                        <SelectContent>
                                            {students.map(s => (
                                                <SelectItem key={s.id} value={s.id.toString()}>{s.full_name} ({s.nis})</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="category_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Kategori Tagihan</FormLabel>
                                    <Select onValueChange={(v) => field.onChange(parseInt(v))} defaultValue={field.value ? field.value.toString() : undefined}>
                                        <FormControl><SelectTrigger><SelectValue placeholder="Pilih Kategori" /></SelectTrigger></FormControl>
                                        <SelectContent>
                                            {categories.map(c => (
                                                <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="title"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Judul Tagihan</FormLabel>
                                    <FormControl><Input placeholder="Contoh: SPP Januari" {...field} /></FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="amount"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Nominal (Rp)</FormLabel>
                                    <FormControl><Input type="number" {...field} /></FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <DialogFooter>
                            <Button type="submit" disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Generate Tagihan
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
