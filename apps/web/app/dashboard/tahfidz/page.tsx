"use client"

import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Loader2, Plus } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"

const API_URL = "http://localhost:8000"

interface Student {
    id: number
    full_name: string
    nis: string | null
}

interface TahfidzProgress {
    id: number
    student_id: number
    date: string
    type: "QURAN" | "MUTUN"
    new_memorization: string
    review: string | null
    kitab_name: string | null
    score: number
    notes: string | null
    student?: { full_name: string }
}

export default function TahfidzPage() {
    const [students, setStudents] = useState<Student[]>([])
    const [progressList, setProgressList] = useState<TahfidzProgress[]>([])
    const [loading, setLoading] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [dialogOpen, setDialogOpen] = useState(false)

    // Form state
    const [formData, setFormData] = useState({
        student_id: "",
        date: new Date().toISOString().split('T')[0],
        type: "QURAN" as "QURAN" | "MUTUN",
        new_memorization: "",
        review: "",
        kitab_name: "",
        score: 0,
        notes: ""
    })

    // Fetch students
    useEffect(() => {
        const fetchStudents = async () => {
            try {
                const token = localStorage.getItem("token")
                const res = await fetch(`${API_URL}/academic/students`, {
                    headers: { "Authorization": `Bearer ${token}` }
                })
                if (res.ok) {
                    const data = await res.json()
                    setStudents(data)
                }
            } catch (error) {
                console.error(error)
            }
        }
        fetchStudents()
    }, [])

    // Fetch progress list
    const fetchProgress = async () => {
        setLoading(true)
        try {
            const token = localStorage.getItem("token")
            const res = await fetch(`${API_URL}/tahfidz/progress`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setProgressList(data)
            }
        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchProgress()
    }, [])

    const handleSubmit = async () => {
        if (!formData.student_id || !formData.new_memorization) {
            alert("Lengkapi data setoran")
            return
        }
        setSubmitting(true)
        try {
            const token = localStorage.getItem("token")
            const payload = {
                student_id: parseInt(formData.student_id),
                date: formData.date,
                type: formData.type,
                new_memorization: formData.new_memorization,
                review: formData.review || null,
                kitab_name: formData.type === "MUTUN" ? formData.kitab_name : null,
                score: formData.score,
                notes: formData.notes || null
            }

            const res = await fetch(`${API_URL}/tahfidz/progress`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            })

            if (res.ok) {
                alert("Setoran berhasil disimpan")
                setDialogOpen(false)
                fetchProgress()
                // Reset form
                setFormData({
                    student_id: "",
                    date: new Date().toISOString().split('T')[0],
                    type: "QURAN",
                    new_memorization: "",
                    review: "",
                    kitab_name: "",
                    score: 0,
                    notes: ""
                })
            } else {
                alert("Gagal menyimpan setoran")
            }
        } catch (error) {
            console.error(error)
            alert("Terjadi kesalahan")
        } finally {
            setSubmitting(false)
        }
    }

    const getTypeBadge = (type: "QURAN" | "MUTUN") => {
        return type === "QURAN"
            ? <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-green-100 text-green-800">Quran</span>
            : <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-purple-100 text-purple-800">Mutun</span>
    }

    return (
        <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Tahfidz</h2>
                    <p className="text-muted-foreground">Setoran hafalan Al-Quran dan Mutun.</p>
                </div>
                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" /> Tambah Setoran
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[500px]">
                        <DialogHeader>
                            <DialogTitle>Input Setoran Harian</DialogTitle>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                            <div className="grid gap-2">
                                <Label>Siswa</Label>
                                <Select
                                    value={formData.student_id}
                                    onValueChange={(v) => setFormData(prev => ({ ...prev, student_id: v }))}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Pilih siswa..." />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {students.map(s => (
                                            <SelectItem key={s.id} value={s.id.toString()}>
                                                {s.full_name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <Label>Tanggal</Label>
                                    <Input
                                        type="date"
                                        value={formData.date}
                                        onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                                    />
                                </div>
                                <div className="grid gap-2">
                                    <Label>Jenis</Label>
                                    <Select
                                        value={formData.type}
                                        onValueChange={(v) => setFormData(prev => ({ ...prev, type: v as "QURAN" | "MUTUN" }))}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="QURAN">Al-Quran</SelectItem>
                                            <SelectItem value="MUTUN">Mutun/Kitab</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>
                            {formData.type === "MUTUN" && (
                                <div className="grid gap-2">
                                    <Label>Nama Kitab</Label>
                                    <Input
                                        placeholder="Urjuzah Mi'iyah, dll"
                                        value={formData.kitab_name}
                                        onChange={(e) => setFormData(prev => ({ ...prev, kitab_name: e.target.value }))}
                                    />
                                </div>
                            )}
                            <div className="grid gap-2">
                                <Label>Hafalan Baru</Label>
                                <Input
                                    placeholder={formData.type === "QURAN" ? "Surah / Ayat" : "Bab / Bait"}
                                    value={formData.new_memorization}
                                    onChange={(e) => setFormData(prev => ({ ...prev, new_memorization: e.target.value }))}
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label>Murojaah</Label>
                                <Input
                                    placeholder="Hafalan yang dimurojaah"
                                    value={formData.review}
                                    onChange={(e) => setFormData(prev => ({ ...prev, review: e.target.value }))}
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <Label>Nilai</Label>
                                    <Input
                                        type="number"
                                        min={0}
                                        max={100}
                                        value={formData.score}
                                        onChange={(e) => setFormData(prev => ({ ...prev, score: parseInt(e.target.value) || 0 }))}
                                    />
                                </div>
                            </div>
                            <div className="grid gap-2">
                                <Label>Catatan</Label>
                                <Textarea
                                    placeholder="Keterangan tambahan..."
                                    value={formData.notes}
                                    onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                                />
                            </div>
                        </div>
                        <div className="flex justify-end">
                            <Button onClick={handleSubmit} disabled={submitting}>
                                {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Simpan
                            </Button>
                        </div>
                    </DialogContent>
                </Dialog>
            </div>
            <Separator />

            <Tabs defaultValue="progress" className="w-full">
                <TabsList>
                    <TabsTrigger value="progress">Setoran Harian</TabsTrigger>
                    <TabsTrigger value="exam">Ujian Tahfidz</TabsTrigger>
                </TabsList>

                <TabsContent value="progress">
                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Tanggal</TableHead>
                                    <TableHead>Nama Siswa</TableHead>
                                    <TableHead>Jenis</TableHead>
                                    <TableHead>Hafalan Baru</TableHead>
                                    <TableHead>Murojaah</TableHead>
                                    <TableHead>Nilai</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={6} className="h-24 text-center">
                                            <div className="flex justify-center items-center gap-2">
                                                <Loader2 className="h-4 w-4 animate-spin" /> Loading...
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ) : progressList.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                                            Belum ada data setoran
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    progressList.map((p) => (
                                        <TableRow key={p.id}>
                                            <TableCell>{new Date(p.date).toLocaleDateString('id-ID')}</TableCell>
                                            <TableCell className="font-medium">{p.student?.full_name || "-"}</TableCell>
                                            <TableCell>
                                                {getTypeBadge(p.type)}
                                                {p.type === "MUTUN" && p.kitab_name && (
                                                    <span className="ml-2 text-xs text-muted-foreground">{p.kitab_name}</span>
                                                )}
                                            </TableCell>
                                            <TableCell>{p.new_memorization}</TableCell>
                                            <TableCell>{p.review || "-"}</TableCell>
                                            <TableCell>{p.score}</TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </TabsContent>

                <TabsContent value="exam">
                    <div className="rounded-md border bg-white p-8 text-center text-muted-foreground">
                        Ujian tahfidz akan ditampilkan di sini
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    )
}
