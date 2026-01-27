"use client"

import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import { StudentFormDialog } from "@/components/dashboard/siswa/StudentFormDialog"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Loader2 } from "lucide-react"

// Define interface matching API response
interface Student {
    id: number
    nis: string | null
    nisn: string | null
    full_name: string
    gender: "L" | "P"
    status: string
    unit_id: number
}

export default function SiswaPage() {
    const [students, setStudents] = useState<Student[]>([])
    const [loading, setLoading] = useState(true)

    const fetchStudents = async () => {
        setLoading(true)
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/academic/students`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            })
            if (response.ok) {
                const data = await response.json()
                setStudents(data)
            } else {
                console.error("Failed to fetch students")
            }
        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchStudents()
    }, [])

    return (
        <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Data Siswa</h2>
                    <p className="text-muted-foreground">Manajemen data siswa aktif.</p>
                </div>
                {/* Pass refresh callback to form */}
                <StudentFormDialog onSuccess={fetchStudents} />
            </div>
            <Separator />

            <div className="rounded-md border bg-white">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Nama Lengkap</TableHead>
                            <TableHead>NIS / NISN</TableHead>
                            <TableHead>L/P</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Unit ID</TableHead>
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
                        ) : students.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="h-24 text-center">
                                    Belum ada data siswa.
                                </TableCell>
                            </TableRow>
                        ) : (
                            students.map((student) => (
                                <TableRow key={student.id}>
                                    <TableCell className="font-medium">{student.full_name}</TableCell>
                                    <TableCell>
                                        <div className="flex flex-col">
                                            <span className="text-xs text-muted-foreground">NIS: {student.nis || "-"}</span>
                                            <span className="text-xs">NISN: {student.nisn || "-"}</span>
                                        </div>
                                    </TableCell>
                                    <TableCell>{student.gender}</TableCell>
                                    <TableCell>
                                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${student.status === "ACTIVE" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                                            }`}>
                                            {student.status}
                                        </span>
                                    </TableCell>
                                    <TableCell>{student.unit_id}</TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}
