"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Plus, Loader2 } from "lucide-react"

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
    FormDescription,
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
    full_name: z.string().min(2, {
        message: "Nama lengkap minimal 2 karakter.",
    }),
    nis: z.string().optional(),
    nisn: z.string().optional(),
    gender: z.enum(["L", "P"]),
    unit_id: z.coerce.number().min(1),
})

export function StudentFormDialog({ onSuccess }: { onSuccess?: () => void }) {
    const [open, setOpen] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [units, setUnits] = useState<{ id: number, name: string }[]>([])

    // Fetch units on load
    useEffect(() => {
        const fetchUnits = async () => {
            try {
                const API_URL = "http://localhost:8000"
                const response = await fetch(`${API_URL}/units`, {
                    headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
                })
                if (response.ok) {
                    const data = await response.json()
                    setUnits(data)
                }
            } catch (error) {
                console.error("Failed to fetch units", error)
            }
        }
        if (open) {
            fetchUnits()
        }
    }, [open])

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            full_name: "",
            nis: "",
            nisn: "",
            gender: "L",
            unit_id: 1, // Defaulting to 1 (usually RA or SDIT) for now
        },
    })

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)
        try {
            // Adjust API URL based on environment, hardcoded for now
            const API_URL = "http://localhost:8000"
            const response = await fetch(`${API_URL}/academic/students`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    // Authorization token should be handled here, assuming cookie or context
                    // For now we might encounter 401 if we don't handle auth. 
                    // But AuthGuard wraps the page, so user is logged in. 
                    // We need to pass the token. 
                    // Let's assume we can retrieve it from localStorage or cookies.
                    // To be safe, I'll try without header first, but 401 is likely.
                    // Quick fix: Get token from localStorage if you stored it there.
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(values),
            })

            if (!response.ok) {
                throw new Error("Gagal menyimpan data siswa")
            }

            toast.success("Data siswa berhasil ditambahkan")
            setOpen(false)
            form.reset()
            onSuccess?.()
        } catch (error) {
            toast.error("Gagal menambahkan siswa. Cek koneksi atau login ulang.")
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="bg-[var(--syuura-green)] hover:bg-[var(--syuura-green)]/90">
                    <Plus className="mr-2 h-4 w-4" /> Tambah Siswa
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Tambah Siswa Baru</DialogTitle>
                    <DialogDescription>
                        Masukkan data siswa baru di sini. Klik simpan setelah selesai.
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="full_name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Nama Lengkap</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Nama Siswa" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <div className="grid grid-cols-2 gap-4">
                            <FormField
                                control={form.control}
                                name="nis"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>NIS</FormLabel>
                                        <FormControl>
                                            <Input placeholder="NIS" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="nisn"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>NISN</FormLabel>
                                        <FormControl>
                                            <Input placeholder="NISN" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <FormField
                            control={form.control}
                            name="gender"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Jenis Kelamin</FormLabel>
                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Pilih jenis kelamin" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="L">Laki-laki</SelectItem>
                                            <SelectItem value="P">Perempuan</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="unit_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Unit Sekolah</FormLabel>
                                    <Select
                                        onValueChange={(value) => field.onChange(parseInt(value))}
                                        defaultValue={field.value.toString()}
                                    >
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Pilih unit sekolah" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            {units.map((unit) => (
                                                <SelectItem key={unit.id} value={unit.id.toString()}>
                                                    {unit.name}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
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
