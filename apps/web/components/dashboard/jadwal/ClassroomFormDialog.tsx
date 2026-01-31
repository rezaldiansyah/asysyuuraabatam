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
    name: z.string().min(2, { message: "Nama kelas minimal 2 karakter." }),
    level: z.coerce.number().min(1, { message: "Level wajib diisi." }),
    unit_id: z.coerce.number().min(1, { message: "Wajib pilih unit." }),
    academic_year_id: z.coerce.number().min(1, { message: "Wajib pilih tahun ajaran." }),
})

export function ClassroomFormDialog({ onSuccess }: { onSuccess?: () => void }) {
    const [open, setOpen] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [units, setUnits] = useState<{ id: number, name: string }[]>([])
    const [academicYears, setAcademicYears] = useState<{ id: number, name: string }[]>([])

    useEffect(() => {
        const fetchData = async () => {
            try {
                const API_URL = "http://localhost:8000"
                const token = localStorage.getItem("token")
                const headers = { "Authorization": `Bearer ${token}` }

                const [unitsRes, yearsRes] = await Promise.all([
                    fetch(`${API_URL}/units`, { headers }),
                    fetch(`${API_URL}/academic/years`, { headers })
                ])

                if (unitsRes.ok) setUnits(await unitsRes.json())
                if (yearsRes.ok) setAcademicYears(await yearsRes.json())

            } catch (error) {
                console.error("Failed to fetch data", error)
            }
        }
        if (open) fetchData()
    }, [open])

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            name: "",
            level: 1,
            unit_id: 0,
            academic_year_id: 0,
        },
    })

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)
        try {
            const API_URL = "http://localhost:8000"
            const response = await fetch(`${API_URL}/academic/classrooms`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(values),
            })

            if (!response.ok) {
                throw new Error("Gagal menyimpan data kelas")
            }

            toast.success("Data kelas berhasil ditambahkan")
            setOpen(false)
            form.reset()
            onSuccess?.()
        } catch (error) {
            toast.error("Gagal menambahkan kelas")
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                    <Plus className="mr-2 h-4 w-4" /> Tambah Kelas
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Tambah Kelas Ajar</DialogTitle>
                    <DialogDescription>
                        Buat kelas baru untuk tahun ajaran aktif.
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Nama Kelas</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Contoh: 1 Abu Bakar" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="level"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Tingkat / Level</FormLabel>
                                    <FormControl>
                                        <Input type="number" placeholder="1" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <div className="grid grid-cols-2 gap-4">
                            <FormField
                                control={form.control}
                                name="unit_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Unit</FormLabel>
                                        <Select
                                            onValueChange={(value) => field.onChange(parseInt(value))}
                                            defaultValue={field.value ? field.value.toString() : undefined}
                                        >
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Pilih unit" />
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
                            <FormField
                                control={form.control}
                                name="academic_year_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Tahun Ajaran</FormLabel>
                                        <Select
                                            onValueChange={(value) => field.onChange(parseInt(value))}
                                            defaultValue={field.value ? field.value.toString() : undefined}
                                        >
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Pilih tahun" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                {academicYears.map((year) => (
                                                    <SelectItem key={year.id} value={year.id.toString()}>
                                                        {year.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
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
