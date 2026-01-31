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
import { Loader2 } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const API_URL = "http://localhost:8000"

interface Student {
    id: number
    full_name: string
    nis: string | null
    current_classroom_id: number | null
}

interface Classroom {
    id: number
    name: string
}

interface Subject {
    id: number
    name: string
    code: string
}

interface AcademicYear {
    id: number
    name: string
    is_active: boolean
}

type GradeType = "QUIZ" | "MIDTERM" | "FINAL" | "ASSIGNMENT" | "PRACTICE"

interface GradeItem {
    student_id: number
    score: number
    notes: string
}

export default function NilaiPage() {
    const [classrooms, setClassrooms] = useState<Classroom[]>([])
    const [subjects, setSubjects] = useState<Subject[]>([])
    const [academicYears, setAcademicYears] = useState<AcademicYear[]>([])
    const [students, setStudents] = useState<Student[]>([])

    const [selectedClassroom, setSelectedClassroom] = useState<string>("")
    const [selectedSubject, setSelectedSubject] = useState<string>("")
    const [selectedYear, setSelectedYear] = useState<string>("")
    const [selectedType, setSelectedType] = useState<GradeType>("QUIZ")

    const [loading, setLoading] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [gradeData, setGradeData] = useState<Record<number, number>>({})

    // Fetch initial data
    useEffect(() => {
        const token = localStorage.getItem("token")

        // Fetch classrooms
        fetch(`${API_URL}/academic/classrooms`, {
            headers: { "Authorization": `Bearer ${token}` }
        }).then(res => res.json()).then(setClassrooms).catch(console.error)

        // Fetch subjects
        fetch(`${API_URL}/academic/subjects`, {
            headers: { "Authorization": `Bearer ${token}` }
        }).then(res => res.json()).then(setSubjects).catch(console.error)

        // Fetch academic years
        fetch(`${API_URL}/academic/academic-years`, {
            headers: { "Authorization": `Bearer ${token}` }
        }).then(res => res.json()).then((data: AcademicYear[]) => {
            setAcademicYears(data)
            const active = data.find(y => y.is_active)
            if (active) setSelectedYear(active.id.toString())
        }).catch(console.error)
    }, [])

    // Fetch students when classroom changes
    useEffect(() => {
        if (!selectedClassroom) return
        const fetchStudents = async () => {
            setLoading(true)
            try {
                const token = localStorage.getItem("token")
                const res = await fetch(`${API_URL}/academic/students`, {
                    headers: { "Authorization": `Bearer ${token}` }
                })
                if (res.ok) {
                    const data: Student[] = await res.json()
                    const filtered = data.filter(s => s.current_classroom_id === parseInt(selectedClassroom))
                    setStudents(filtered)
                    // Initialize all with 0
                    const initial: Record<number, number> = {}
                    filtered.forEach(s => { initial[s.id] = 0 })
                    setGradeData(initial)
                }
            } catch (error) {
                console.error(error)
            } finally {
                setLoading(false)
            }
        }
        fetchStudents()
    }, [selectedClassroom])

    const handleScoreChange = (studentId: number, score: string) => {
        const numScore = parseInt(score) || 0
        setGradeData(prev => ({ ...prev, [studentId]: Math.min(100, Math.max(0, numScore)) }))
    }

    const handleSubmit = async () => {
        if (!selectedClassroom || !selectedSubject || !selectedYear || students.length === 0) {
            alert("Lengkapi semua filter terlebih dahulu")
            return
        }
        setSubmitting(true)
        try {
            const token = localStorage.getItem("token")
            const items: GradeItem[] = students.map(s => ({
                student_id: s.id,
                score: gradeData[s.id] || 0,
                notes: ""
            }))

            const res = await fetch(`${API_URL}/academic/grades/bulk`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    subject_id: parseInt(selectedSubject),
                    academic_year_id: parseInt(selectedYear),
                    type: selectedType,
                    classroom_id: parseInt(selectedClassroom),
                    items
                })
            })

            if (res.ok) {
                const result = await res.json()
                alert(result.message)
            } else {
                alert("Gagal menyimpan nilai")
            }
        } catch (error) {
            console.error(error)
            alert("Terjadi kesalahan")
        } finally {
            setSubmitting(false)
        }
    }

    const gradeTypes = [
        { value: "QUIZ", label: "Ulangan Harian" },
        { value: "MIDTERM", label: "UTS" },
        { value: "FINAL", label: "UAS" },
        { value: "ASSIGNMENT", label: "Tugas" },
        { value: "PRACTICE", label: "Praktik" },
    ]

    return (
        <div className="flex flex-col gap-4">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Nilai Siswa</h2>
                <p className="text-muted-foreground">Input nilai akademik per kelas.</p>
            </div>
            <Separator />

            <Tabs defaultValue="input" className="w-full">
                <TabsList>
                    <TabsTrigger value="input">Input Nilai</TabsTrigger>
                    <TabsTrigger value="sikap">Nilai Sikap</TabsTrigger>
                </TabsList>

                <TabsContent value="input" className="space-y-4">
                    {/* Filters */}
                    <div className="flex flex-wrap gap-4 items-end">
                        <div className="w-[180px]">
                            <label className="text-sm font-medium mb-2 block">Tahun Ajaran</label>
                            <Select value={selectedYear} onValueChange={setSelectedYear}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Tahun..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {academicYears.map(y => (
                                        <SelectItem key={y.id} value={y.id.toString()}>
                                            {y.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="w-[180px]">
                            <label className="text-sm font-medium mb-2 block">Kelas</label>
                            <Select value={selectedClassroom} onValueChange={setSelectedClassroom}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Pilih kelas..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {classrooms.map(c => (
                                        <SelectItem key={c.id} value={c.id.toString()}>
                                            {c.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="w-[180px]">
                            <label className="text-sm font-medium mb-2 block">Mata Pelajaran</label>
                            <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Pilih mapel..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {subjects.map(s => (
                                        <SelectItem key={s.id} value={s.id.toString()}>
                                            {s.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="w-[180px]">
                            <label className="text-sm font-medium mb-2 block">Jenis Nilai</label>
                            <Select value={selectedType} onValueChange={(v) => setSelectedType(v as GradeType)}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {gradeTypes.map(t => (
                                        <SelectItem key={t.value} value={t.value}>
                                            {t.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Table */}
                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-[50px]">No</TableHead>
                                    <TableHead>Nama Siswa</TableHead>
                                    <TableHead>NIS</TableHead>
                                    <TableHead className="w-[120px]">Nilai</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={4} className="h-24 text-center">
                                            <div className="flex justify-center items-center gap-2">
                                                <Loader2 className="h-4 w-4 animate-spin" /> Loading...
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ) : !selectedClassroom ? (
                                    <TableRow>
                                        <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                                            Pilih kelas terlebih dahulu
                                        </TableCell>
                                    </TableRow>
                                ) : students.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={4} className="h-24 text-center">
                                            Tidak ada siswa di kelas ini
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    students.map((student, idx) => (
                                        <TableRow key={student.id}>
                                            <TableCell>{idx + 1}</TableCell>
                                            <TableCell className="font-medium">{student.full_name}</TableCell>
                                            <TableCell>{student.nis || "-"}</TableCell>
                                            <TableCell>
                                                <Input
                                                    type="number"
                                                    min={0}
                                                    max={100}
                                                    value={gradeData[student.id] || 0}
                                                    onChange={(e) => handleScoreChange(student.id, e.target.value)}
                                                    className="w-20"
                                                />
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    {/* Submit Button */}
                    {students.length > 0 && (
                        <div className="flex justify-end">
                            <Button onClick={handleSubmit} disabled={submitting}>
                                {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Simpan Nilai
                            </Button>
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="sikap">
                    <div className="rounded-md border bg-white p-8 text-center text-muted-foreground">
                        Input nilai sikap (spiritual & sosial) akan ditampilkan di sini
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    )
}
