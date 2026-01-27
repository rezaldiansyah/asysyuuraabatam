
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "lucide-react";

async function getPosts() {
    const API_URL = "http://localhost:8000";
    try {
        const res = await fetch(`${API_URL}/public/posts`, { next: { revalidate: 60 } });
        if (!res.ok) return [];
        return res.json();
    } catch (error) {
        console.error(error);
        return [];
    }
}

export default async function BeritaPage() {
    const posts = await getPosts();

    return (
        <div className="flex min-h-screen flex-col">
            <Navbar />

            <main className="flex-1 py-12 container mx-auto px-4">
                <div className="text-center mb-12">
                    <h1 className="text-3xl font-bold tracking-tight text-[var(--syuura-green)] mb-4">Berita & Kegiatan Sekolah</h1>
                    <p className="text-muted-foreground max-w-2xl mx-auto">
                        Update terbaru seputar kegiatan belajar mengajar dan prestasi siswa Sekolah Islam Terpadu Asy-Syuuraa Batam.
                    </p>
                </div>

                {posts.length === 0 ? (
                    <div className="text-center py-20 bg-slate-50 rounded-lg border border-dashed text-muted-foreground">
                        <p>Belum ada berita yang dipublikasikan.</p>
                    </div>
                ) : (
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {posts.map((post: any) => (
                            <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                                {post.image_url ? (
                                    <div className="aspect-video w-full overflow-hidden">
                                        <img
                                            src={post.image_url}
                                            alt={post.title}
                                            className="h-full w-full object-cover transition-transform hover:scale-105"
                                        />
                                    </div>
                                ) : (
                                    <div className="aspect-video w-full bg-slate-100 flex items-center justify-center text-slate-300">
                                        No Image
                                    </div>
                                )}
                                <CardHeader>
                                    <div className="flex items-center gap-2 mb-2">
                                        <Badge variant="outline" className="font-normal">Berita</Badge>
                                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                                            <Calendar className="h-3 w-3" />
                                            {new Date(post.created_at).toLocaleDateString("id-ID")}
                                        </span>
                                    </div>
                                    <CardTitle className="line-clamp-2 hover:text-[var(--syuura-green)] transition-colors">
                                        {post.title}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-muted-foreground line-clamp-3">
                                        {post.content}
                                    </p>
                                </CardContent>
                                <CardFooter>
                                    <button className="text-sm font-medium text-[var(--syuura-gold)] hover:underline">
                                        Baca Selengkapnya →
                                    </button>
                                </CardFooter>
                            </Card>
                        ))}
                    </div>
                )}
            </main>

            <Footer />
        </div>
    );
}
