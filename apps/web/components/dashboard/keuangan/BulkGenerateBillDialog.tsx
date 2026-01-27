"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { FileText, Loader2, Calculator, Check, ArrowRight } from "lucide-react"

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
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { toast } from "sonner"
import { Badge } from "@/components/ui/badge"

const step1Schema = z.object({
    classroom_id: z.coerce.number().min(1, { message: "Pilih kelas." }),
    category_id: z.coerce.number().min(1, { message: "Pilih kategori." }),
    title: z.string().min(5, { message: "Judul tagihan minimal 5 karakter." }),
    due_date: z.string().optional(),
})

export function BulkGenerateBillDialog({ onSuccess }: { onSuccess?: () => void }) {
    const [open, setOpen] = useState(false)
    const [step, setStep] = useState(1) // 1: Select, 2: Preview
    const [isLoading, setIsLoading] = useState(false)
    const [classrooms, setClassrooms] = useState<any[]>([])
    const [categories, setCategories] = useState<any[]>([])
    const [previewData, setPreviewData] = useState<any[]>([])
    const [step1Values, setStep1Values] = useState<any>(null)

    // Load data
    useEffect(() => {
        if (open) {
            setStep(1)
            setPreviewData([])
            const fetchData = async () => {
                const API_URL = "http://localhost:8000"
                const token = localStorage.getItem("token")
                const headers = { "Authorization": `Bearer ${token}` }

                try {
                    const [clsRes, catRes] = await Promise.all([
                        fetch(`${API_URL}/academic/classrooms`, { headers }),
                        fetch(`${API_URL}/finance/categories`, { headers })
                    ])
                    if (clsRes.ok) setClassrooms(await clsRes.json())
                    if (catRes.ok) setCategories(await catRes.json())
                } catch (e) {
                    toast.error("Gagal memuat data")
                }
            }
            fetchData()
        }
    }, [open])

    const form = useForm<z.infer<typeof step1Schema>>({
        resolver: zodResolver(step1Schema) as any,
        defaultValues: {
            classroom_id: 0,
            category_id: 0,
            title: "",
        },
    })

    // Auto-fill title
    const watchCategory = form.watch("category_id")
    useEffect(() => {
        if (watchCategory && step === 1) {
            const cat = categories.find(c => c.id === watchCategory)
            if (cat) {
                form.setValue("title", `${cat.name} - ${new Date().toLocaleString('id-ID', { month: 'long', year: 'numeric' })}`)
            }
        }
    }, [watchCategory, categories, form, step])

    async function onPreview(values: z.infer<typeof step1Schema>) {
        setIsLoading(true)
        setStep1Values(values)
        try {
            const API_URL = "http://localhost:8000"
            const response = await fetch(`${API_URL}/finance/bills/bulk-preview`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(values),
            })

            if (!response.ok) throw new Error("Gagal load preview")

            const data = await response.json()
            if (data.length === 0) {
                toast.warning("Tidak ada siswa aktif di kelas ini.")
                setIsLoading(false)
                return
            }

            setPreviewData(data)
            setStep(2)
        } catch (error) {
            toast.error("Gagal memuat preview tagihan")
        } finally {
            setIsLoading(false)
        }
    }

    async function onSubmit() {
        setIsLoading(true)
        try {
            // Prepare items from previewData
            // Note: We could add functionality to edit amounts in previewData here
            const items = previewData.map(item => ({
                student_id: item.student_id,
                amount: item.final_amount,
                title: step1Values.title
            }))

            const payload = {
                category_id: step1Values.category_id,
                items: items,
                due_date: step1Values.due_date
            }

            const API_URL = "http://localhost:8000"
            const response = await fetch(`${API_URL}/finance/bills/bulk`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(payload),
            })

            if (!response.ok) throw new Error("Gagal generate tagihan")

            toast.success(`Berhasil membuat tagihan untuk ${items.length} siswa`)
            setOpen(false)
            setStep(1)
            form.reset()
            onSuccess?.()
        } catch (error) {
            toast.error("Gagal generate tagihan")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="bg-[var(--syuura-gold)] text-black hover:bg-[var(--syuura-gold)]/90">
                    <FileText className="mr-2 h-4 w-4" /> Generate Massal
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[700px]">
                <DialogHeader>
                    <DialogTitle>{step === 1 ? "Generate Tagihan Massal" : "Preview Tagihan"}</DialogTitle>
                    <DialogDescription>
                        {step === 1 ? "Pilih kelas dan kategori tagihan untuk diproses." : "Review daftar tagihan sebelum disimpan. Diskon beasiswa dihitung otomatis."}
                    </DialogDescription>
                </DialogHeader>

                {step === 1 && (
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onPreview)} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <FormField
                                    control={form.control}
                                    name="classroom_id"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Pilih Kelas</FormLabel>
                                            <Select onValueChange={(v) => field.onChange(parseInt(v))} defaultValue={field.value ? field.value.toString() : undefined}>
                                                <FormControl><SelectTrigger><SelectValue placeholder="Kelas..." /></SelectTrigger></FormControl>
                                                <SelectContent>
                                                    {classrooms.map(c => (
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
                                    name="category_id"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Kategori Tagihan</FormLabel>
                                            <Select onValueChange={(v) => field.onChange(parseInt(v))} defaultValue={field.value ? field.value.toString() : undefined}>
                                                <FormControl><SelectTrigger><SelectValue placeholder="Kategori..." /></SelectTrigger></FormControl>
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
                            </div>
                            <FormField
                                control={form.control}
                                name="title"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Judul Tagihan</FormLabel>
                                        <FormControl><Input placeholder="Contoh: SPP Februari" {...field} /></FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <DialogFooter>
                                <Button type="submit" disabled={isLoading}>
                                    {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                    Lanjut Preview <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </DialogFooter>
                        </form>
                    </Form>
                )}

                {step === 2 && (
                    <div className="space-y-4">
                        <div className="rounded-md border max-h-[300px] overflow-y-auto">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Nama Siswa</TableHead>
                                        <TableHead>Tagihan Awal</TableHead>
                                        <TableHead>Beasiswa/Diskon</TableHead>
                                        <TableHead className="text-right">Total Tagihan</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {previewData.map(item => (
                                        <TableRow key={item.student_id}>
                                            <TableCell className="font-medium">{item.student_name}</TableCell>
                                            <TableCell>Rp {item.original_amount.toLocaleString('id-ID')}</TableCell>
                                            <TableCell>
                                                {item.scholarship_name ? (
                                                    <div className="flex flex-col">
                                                        <Badge variant="secondary" className="w-fit text-xs">{item.scholarship_name}</Badge>
                                                        <span className="text-xs text-green-600">- Rp {item.discount_amount.toLocaleString('id-ID')}</span>
                                                    </div>
                                                ) : "-"}
                                            </TableCell>
                                            <TableCell className="text-right font-bold">Rp {item.final_amount.toLocaleString('id-ID')}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                        <div className="flex justify-between items-center text-sm text-muted-foreground p-2 border rounded bg-muted/20">
                            <span>Total Tagihan: <b>{previewData.length}</b> Siswa</span>
                            <span>Total Estimasi: <b>Rp {previewData.reduce((acc, curr) => acc + curr.final_amount, 0).toLocaleString('id-ID')}</b></span>
                        </div>
                        <DialogFooter className="gap-2 sm:gap-0">
                            <Button variant="outline" onClick={() => setStep(1)} disabled={isLoading}>Kembali</Button>
                            <Button onClick={onSubmit} disabled={isLoading} className="bg-[var(--syuura-green)] hover:bg-[var(--syuura-green)]/90">
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Proses Generate
                            </Button>
                        </DialogFooter>
                    </div>
                )}
            </DialogContent>
        </Dialog>
    )
}
