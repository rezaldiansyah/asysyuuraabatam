"use client"

import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, BookOpen, GraduationCap, CalendarDays } from "lucide-react"

import { ScheduleFormDialog } from "@/components/dashboard/jadwal/ScheduleFormDialog"
import { SubjectFormDialog } from "@/components/dashboard/jadwal/SubjectFormDialog"
import { ClassroomFormDialog } from "@/components/dashboard/jadwal/ClassroomFormDialog"

// We can reuse a simple Table component or create inline tables for simplicity
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"

export default function JadwalPage() {
    const [loading, setLoading] = useState(false)

    // State lists
    const [schedules, setSchedules] = useState<any[]>([])
    const [subjects, setSubjects] = useState<any[]>([])
    const [classrooms, setClassrooms] = useState<any[]>([])

    // Fetch Functions
    const fetchData = async (type: 'schedules' | 'subjects' | 'classrooms') => {
        setLoading(true)
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const endpoint = type === 'classrooms' ? 'classrooms' : type // consistency tweak

            const response = await fetch(`${API_URL}/academic/${endpoint}`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                if (type === 'schedules') setSchedules(data)
                if (type === 'subjects') setSubjects(data)
                if (type === 'classrooms') setClassrooms(data)
            }
        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        // Initial load - fetch all relevant data
        fetchData('schedules')
        fetchData('subjects')
        fetchData('classrooms')
    }, [])

    return (
        <div className="flex flex-col gap-4">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Manajemen Akademik</h2>
                <p className="text-muted-foreground">Kelola jadwal pelajaran, mata pelajaran, dan kelas.</p>
            </div>
            <Separator />

            <Tabs defaultValue="schedules" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="schedules" className="flex items-center gap-2">
                        <CalendarDays className="h-4 w-4" /> Jadwal Pelajaran
                    </TabsTrigger>
                    <TabsTrigger value="classrooms" className="flex items-center gap-2">
                        <GraduationCap className="h-4 w-4" /> Data Kelas
                    </TabsTrigger>
                    <TabsTrigger value="subjects" className="flex items-center gap-2">
                        <BookOpen className="h-4 w-4" /> Mata Pelajaran
                    </TabsTrigger>
                </TabsList>

                {/* --- SCHEDULES TAB --- */}
                <TabsContent value="schedules" className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium">Jadwal Aktif</h3>
                        <ScheduleFormDialog onSuccess={() => fetchData('schedules')} />
                    </div>

                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Hari</TableHead>
                                    <TableHead>Jam</TableHead>
                                    <TableHead>Kelas</TableHead>
                                    <TableHead>Mapel</TableHead>
                                    <TableHead>Guru</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {schedules.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={5} className="h-24 text-center">Belum ada jadwal.</TableCell>
                                    </TableRow>
                                ) : (
                                    schedules.map((item: any) => (
                                        <TableRow key={item.id}>
                                            <TableCell className="font-medium">{item.day}</TableCell>
                                            <TableCell>{item.start_time} - {item.end_time}</TableCell>
                                            <TableCell>{item.classroom?.name || item.classroom_id}</TableCell>
                                            <TableCell>{item.subject?.name || item.subject_id}</TableCell>
                                            <TableCell>{item.teacher?.full_name || item.teacher_id}</TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </TabsContent>

                {/* --- CLASSROOMS TAB --- */}
                <TabsContent value="classrooms" className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium">Daftar Kelas</h3>
                        <ClassroomFormDialog onSuccess={() => fetchData('classrooms')} />
                    </div>
                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Nama Kelas</TableHead>
                                    <TableHead>Level</TableHead>
                                    <TableHead>Unit</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {classrooms.length === 0 ? (
                                    <TableRow><TableCell colSpan={3} className="h-24 text-center">Belum ada data kelas.</TableCell></TableRow>
                                ) : (
                                    classrooms.map((c: any) => (
                                        <TableRow key={c.id}>
                                            <TableCell className="font-medium">{c.name}</TableCell>
                                            <TableCell>{c.level}</TableCell>
                                            <TableCell>Unit ID: {c.unit_id}</TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </TabsContent>

                {/* --- SUBJECTS TAB --- */}
                <TabsContent value="subjects" className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium">Daftar Mata Pelajaran</h3>
                        <SubjectFormDialog onSuccess={() => fetchData('subjects')} />
                    </div>
                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Kode</TableHead>
                                    <TableHead>Mata Pelajaran</TableHead>
                                    <TableHead>Unit</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {subjects.length === 0 ? (
                                    <TableRow><TableCell colSpan={3} className="h-24 text-center">Belum ada mapel.</TableCell></TableRow>
                                ) : (
                                    subjects.map((s: any) => (
                                        <TableRow key={s.id}>
                                            <TableCell>{s.code || "-"}</TableCell>
                                            <TableCell className="font-medium">{s.name}</TableCell>
                                            <TableCell>Unit ID: {s.unit_id}</TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    )
}
