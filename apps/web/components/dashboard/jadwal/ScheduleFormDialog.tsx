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
    academic_year_id: z.coerce.number().min(1, { message: "Wajib pilih tahun ajaran." }),
    classroom_id: z.coerce.number().min(1, { message: "Wajib pilih kelas." }),
    subject_id: z.coerce.number().min(1, { message: "Wajib pilih mapel." }),
    teacher_id: z.coerce.number().min(1, { message: "Wajib pilih guru." }),
    day: z.enum(["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    start_time: z.string().min(1, "Jam mulai wajib diisi"),
    end_time: z.string().min(1, "Jam selesai wajib diisi"),
})

export function ScheduleFormDialog({ onSuccess }: { onSuccess?: () => void }) {
    const [open, setOpen] = useState(false)
    const [isLoading, setIsLoading] = useState(false)

    // Data Sources
    const [academicYears, setAcademicYears] = useState<{ id: number, name: string }[]>([])
    const [classrooms, setClassrooms] = useState<{ id: number, name: string }[]>([])
    const [subjects, setSubjects] = useState<{ id: number, name: string }[]>([])
    const [teachers, setTeachers] = useState<{ id: number, full_name: string }[]>([])

    useEffect(() => {
        const fetchData = async () => {
            try {
                const API_URL = "http://localhost:8000"
                const token = localStorage.getItem("token")
                const headers = { "Authorization": `Bearer ${token}` }

                const [years, classes, subs, teac] = await Promise.all([
                    fetch(`${API_URL}/academic/years`, { headers }).then(res => res.json()),
                    fetch(`${API_URL}/academic/classrooms`, { headers }).then(res => res.json()),
                    fetch(`${API_URL}/academic/subjects`, { headers }).then(res => res.json()),
                    fetch(`${API_URL}/academic/teachers`, { headers }).then(res => res.json()),
                ])

                setAcademicYears(years)
                setClassrooms(classes)
                setSubjects(subs)
                setTeachers(teac)

            } catch (error) {
                console.error("Failed to fetch form data", error)
            }
        }
        if (open) fetchData()
    }, [open])

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            academic_year_id: 0,
            classroom_id: 0,
            subject_id: 0,
            teacher_id: 0,
            day: "SENIN",
            start_time: "07:30",
            end_time: "09:00",
        },
    })

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)
        try {
            const API_URL = "http://localhost:8000"
            const response = await fetch(`${API_URL}/academic/schedules`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(values),
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || "Gagal menyimpan jadwal")
            }

            toast.success("Jadwal berhasil ditambahkan")
            setOpen(false)
            form.reset()
            onSuccess?.()
        } catch (error: any) {
            toast.error(error.message || "Gagal menyimpan jadwal")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="bg-[var(--syuura-green)] hover:bg-[var(--syuura-green)]/90">
                    <Plus className="mr-2 h-4 w-4" /> Buat Jadwal
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>Buat Jadwal Pelajaran</DialogTitle>
                    <DialogDescription>
                        Atur jadwal pelajaran untuk kelas tertentu.
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <FormField
                                control={form.control}
                                name="academic_year_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Tahun Ajaran</FormLabel>
                                        <Select onValueChange={(v) => field.onChange(parseInt(v))} defaultValue={field.value ? field.value.toString() : undefined}>
                                            <FormControl><SelectTrigger><SelectValue placeholder="Pilih Tahun" /></SelectTrigger></FormControl>
                                            <SelectContent>{academicYears.map(y => <SelectItem key={y.id} value={y.id.toString()}>{y.name}</SelectItem>)}</SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="classroom_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Kelas</FormLabel>
                                        <Select onValueChange={(v) => field.onChange(parseInt(v))} defaultValue={field.value ? field.value.toString() : undefined}>
                                            <FormControl><SelectTrigger><SelectValue placeholder="Pilih Kelas" /></SelectTrigger></FormControl>
                                            <SelectContent>{classrooms.map(c => <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>)}</SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <FormField
                                control={form.control}
                                name="subject_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Mata Pelajaran</FormLabel>
                                        <Select onValueChange={(v) => field.onChange(parseInt(v))} defaultValue={field.value ? field.value.toString() : undefined}>
                                            <FormControl><SelectTrigger><SelectValue placeholder="Pilih Mapel" /></SelectTrigger></FormControl>
                                            <SelectContent>{subjects.map(s => <SelectItem key={s.id} value={s.id.toString()}>{s.name}</SelectItem>)}</SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="teacher_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Guru Pengampu</FormLabel>
                                        <Select onValueChange={(v) => field.onChange(parseInt(v))} defaultValue={field.value ? field.value.toString() : undefined}>
                                            <FormControl><SelectTrigger><SelectValue placeholder="Pilih Guru" /></SelectTrigger></FormControl>
                                            <SelectContent>{teachers.map(t => <SelectItem key={t.id} value={t.id.toString()}>{t.full_name}</SelectItem>)}</SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            <FormField
                                control={form.control}
                                name="day"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Hari</FormLabel>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <FormControl><SelectTrigger><SelectValue placeholder="Pilih Hari" /></SelectTrigger></FormControl>
                                            <SelectContent>
                                                {["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"].map(d => (
                                                    <SelectItem key={d} value={d}>{d}</SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="start_time"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Jam Mulai</FormLabel>
                                        <FormControl><Input type="time" {...field} /></FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="end_time"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Jam Selesai</FormLabel>
                                        <FormControl><Input type="time" {...field} /></FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <DialogFooter>
                            <Button type="submit" disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Simpan Jadwal
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
