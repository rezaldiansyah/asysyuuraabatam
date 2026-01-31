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
import { Loader2, Check, X, Clock } from "lucide-react"
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
    level: number
}

type AttendanceStatus = "PRESENT" | "SICK" | "PERMIT" | "ABSENT"

interface AttendanceItem {
    student_id: number
    status: AttendanceStatus
    notes: string
}

export default function AbsensiPage() {
    const [classrooms, setClassrooms] = useState<Classroom[]>([])
    const [students, setStudents] = useState<Student[]>([])
    const [selectedClassroom, setSelectedClassroom] = useState<string>("")
    const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0])
    const [loading, setLoading] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [attendanceData, setAttendanceData] = useState<Record<number, AttendanceStatus>>({})

    // Fetch classrooms
    useEffect(() => {
        const fetchClassrooms = async () => {
            try {
                const token = localStorage.getItem("token")
                const res = await fetch(`${API_URL}/academic/classrooms`, {
                    headers: { "Authorization": `Bearer ${token}` }
                })
                if (res.ok) {
                    const data = await res.json()
                    setClassrooms(data)
                }
            } catch (error) {
                console.error(error)
            }
        }
        fetchClassrooms()
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
                    // Filter by classroom
                    const filtered = data.filter(s => s.current_classroom_id === parseInt(selectedClassroom))
                    setStudents(filtered)
                    // Initialize all as PRESENT
                    const initial: Record<number, AttendanceStatus> = {}
                    filtered.forEach(s => { initial[s.id] = "PRESENT" })
                    setAttendanceData(initial)
                }
            } catch (error) {
                console.error(error)
            } finally {
                setLoading(false)
            }
        }
        fetchStudents()
    }, [selectedClassroom])

    const handleStatusChange = (studentId: number, status: AttendanceStatus) => {
        setAttendanceData(prev => ({ ...prev, [studentId]: status }))
    }

    const handleSubmit = async () => {
        if (!selectedClassroom || students.length === 0) return
        setSubmitting(true)
        try {
            const token = localStorage.getItem("token")
            const items: AttendanceItem[] = students.map(s => ({
                student_id: s.id,
                status: attendanceData[s.id] || "PRESENT",
                notes: ""
            }))

            const res = await fetch(`${API_URL}/attendance/students/bulk`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    date: selectedDate,
                    classroom_id: parseInt(selectedClassroom),
                    items
                })
            })

            if (res.ok) {
                const result = await res.json()
                alert(result.message)
            } else {
                alert("Gagal menyimpan absensi")
            }
        } catch (error) {
            console.error(error)
            alert("Terjadi kesalahan")
        } finally {
            setSubmitting(false)
        }
    }

    const getStatusBadge = (status: AttendanceStatus) => {
        const styles = {
            PRESENT: "bg-green-100 text-green-800",
            SICK: "bg-yellow-100 text-yellow-800",
            PERMIT: "bg-blue-100 text-blue-800",
            ABSENT: "bg-red-100 text-red-800"
        }
        const labels = {
            PRESENT: "Hadir",
            SICK: "Sakit",
            PERMIT: "Izin",
            ABSENT: "Alpa"
        }
        return (
            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status]}`}>
                {labels[status]}
            </span>
        )
    }

    return (
        <div className="flex flex-col gap-4">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Absensi Siswa</h2>
                <p className="text-muted-foreground">Input absensi harian per kelas.</p>
            </div>
            <Separator />

            <Tabs defaultValue="input" className="w-full">
                <TabsList>
                    <TabsTrigger value="input">Input Absensi</TabsTrigger>
                    <TabsTrigger value="history">Riwayat</TabsTrigger>
                </TabsList>

                <TabsContent value="input" className="space-y-4">
                    {/* Filters */}
                    <div className="flex gap-4 items-end">
                        <div className="w-[200px]">
                            <label className="text-sm font-medium mb-2 block">Pilih Kelas</label>
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
                        <div className="w-[200px]">
                            <label className="text-sm font-medium mb-2 block">Tanggal</label>
                            <input
                                type="date"
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.target.value)}
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                            />
                        </div>
                    </div>

                    {/* Table */}
                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>No</TableHead>
                                    <TableHead>Nama Siswa</TableHead>
                                    <TableHead>NIS</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Aksi</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={5} className="h-24 text-center">
                                            <div className="flex justify-center items-center gap-2">
                                                <Loader2 className="h-4 w-4 animate-spin" /> Loading...
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ) : !selectedClassroom ? (
                                    <TableRow>
                                        <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                                            Pilih kelas terlebih dahulu
                                        </TableCell>
                                    </TableRow>
                                ) : students.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={5} className="h-24 text-center">
                                            Tidak ada siswa di kelas ini
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    students.map((student, idx) => (
                                        <TableRow key={student.id}>
                                            <TableCell>{idx + 1}</TableCell>
                                            <TableCell className="font-medium">{student.full_name}</TableCell>
                                            <TableCell>{student.nis || "-"}</TableCell>
                                            <TableCell>{getStatusBadge(attendanceData[student.id] || "PRESENT")}</TableCell>
                                            <TableCell>
                                                <div className="flex gap-1">
                                                    <Button
                                                        size="sm"
                                                        variant={attendanceData[student.id] === "PRESENT" ? "default" : "outline"}
                                                        className="h-8 w-8 p-0"
                                                        onClick={() => handleStatusChange(student.id, "PRESENT")}
                                                    >
                                                        <Check className="h-4 w-4" />
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant={attendanceData[student.id] === "SICK" ? "default" : "outline"}
                                                        className="h-8 w-8 p-0 bg-yellow-500 hover:bg-yellow-600"
                                                        onClick={() => handleStatusChange(student.id, "SICK")}
                                                    >
                                                        S
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant={attendanceData[student.id] === "PERMIT" ? "default" : "outline"}
                                                        className="h-8 w-8 p-0 bg-blue-500 hover:bg-blue-600"
                                                        onClick={() => handleStatusChange(student.id, "PERMIT")}
                                                    >
                                                        I
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant={attendanceData[student.id] === "ABSENT" ? "default" : "outline"}
                                                        className="h-8 w-8 p-0 bg-red-500 hover:bg-red-600"
                                                        onClick={() => handleStatusChange(student.id, "ABSENT")}
                                                    >
                                                        <X className="h-4 w-4" />
                                                    </Button>
                                                </div>
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
                                Simpan Absensi
                            </Button>
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="history">
                    <div className="rounded-md border bg-white p-8 text-center text-muted-foreground">
                        Riwayat absensi akan ditampilkan di sini
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    )
}
