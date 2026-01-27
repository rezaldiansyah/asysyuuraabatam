"use client"

import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import { TeacherFormDialog } from "@/components/dashboard/guru/TeacherFormDialog"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Loader2 } from "lucide-react"

interface Teacher {
    id: number
    full_name: string
    nik: string | null
    email: string
    is_active: boolean
}

export default function GuruPage() {
    const [teachers, setTeachers] = useState<Teacher[]>([])
    const [loading, setLoading] = useState(true)

    const fetchTeachers = async () => {
        setLoading(true)
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/academic/teachers`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            })
            if (response.ok) {
                const data = await response.json()
                setTeachers(data)
            } else {
                console.error("Failed to fetch teachers")
            }
        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchTeachers()
    }, [])

    return (
        <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Data Guru</h2>
                    <p className="text-muted-foreground">Manajemen data guru dan staf pengajar.</p>
                </div>
                <TeacherFormDialog onSuccess={fetchTeachers} />
            </div>
            <Separator />

            <div className="rounded-md border bg-white">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Nama Lengkap</TableHead>
                            <TableHead>NIK</TableHead>
                            <TableHead>Email</TableHead>
                            <TableHead>Status</TableHead>
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
                        ) : teachers.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} className="h-24 text-center">
                                    Belum ada data guru.
                                </TableCell>
                            </TableRow>
                        ) : (
                            teachers.map((teacher) => (
                                <TableRow key={teacher.id}>
                                    <TableCell className="font-medium">{teacher.full_name}</TableCell>
                                    <TableCell>{teacher.nik || "-"}</TableCell>
                                    <TableCell>{teacher.email}</TableCell>
                                    <TableCell>
                                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${teacher.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                                            }`}>
                                            {teacher.is_active ? "Aktif" : "Nonaktif"}
                                        </span>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}
