"use client"

import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import { PostFormDialog } from "@/components/dashboard/cms/PostFormDialog"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Trash2 } from "lucide-react"
import { toast } from "sonner"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export default function BeritaCMSPage() {
    const [posts, setPosts] = useState<any[]>([])
    const [isLoading, setIsLoading] = useState(true)

    const fetchPosts = async () => {
        setIsLoading(true)
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/cms/posts`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setPosts(data)
            }
        } catch (error) {
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    const handleDelete = async (id: number) => {
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/cms/posts/${id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (response.ok) {
                toast.success("Berita dihapus")
                fetchPosts()
            } else {
                toast.error("Gagal menghapus berita")
            }
        } catch (error) {
            console.error(error)
        }
    }

    useEffect(() => {
        fetchPosts()
    }, [])

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h3 className="text-lg font-medium">Berita & Artikel</h3>
                    <p className="text-sm text-muted-foreground">
                        Kelola berita sekolah, artikel, dan pengumuman.
                    </p>
                </div>
                <PostFormDialog onSuccess={fetchPosts} />
            </div>
            <Separator />

            <div className="rounded-md border bg-white">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Judul</TableHead>
                            <TableHead>Penulis</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Tanggal</TableHead>
                            <TableHead className="text-right">Aksi</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {posts.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="h-24 text-center">
                                    Belum ada berita.
                                </TableCell>
                            </TableRow>
                        ) : (
                            posts.map((post) => (
                                <TableRow key={post.id}>
                                    <TableCell className="font-medium">
                                        {post.title}
                                        <div className="text-xs text-muted-foreground">/{post.slug}</div>
                                    </TableCell>
                                    <TableCell>Admin</TableCell>
                                    <TableCell>
                                        <Badge variant={post.is_published ? "default" : "secondary"}>
                                            {post.is_published ? "Published" : "Draft"}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>{new Date(post.created_at).toLocaleDateString("id-ID")}</TableCell>
                                    <TableCell className="text-right flex justify-end gap-2">
                                        <PostFormDialog post={post} onSuccess={fetchPosts} />

                                        <AlertDialog>
                                            <AlertDialogTrigger asChild>
                                                <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive hover:bg-destructive/10">
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </AlertDialogTrigger>
                                            <AlertDialogContent>
                                                <AlertDialogHeader>
                                                    <AlertDialogTitle>Hapus Berita?</AlertDialogTitle>
                                                    <AlertDialogDescription>
                                                        Tindakan ini tidak dapat dibatalkan. Berita akan dihapus permanen.
                                                    </AlertDialogDescription>
                                                </AlertDialogHeader>
                                                <AlertDialogFooter>
                                                    <AlertDialogCancel>Batal</AlertDialogCancel>
                                                    <AlertDialogAction className="bg-destructive hover:bg-destructive/90" onClick={() => handleDelete(post.id)}>
                                                        Hapus
                                                    </AlertDialogAction>
                                                </AlertDialogFooter>
                                            </AlertDialogContent>
                                        </AlertDialog>
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
