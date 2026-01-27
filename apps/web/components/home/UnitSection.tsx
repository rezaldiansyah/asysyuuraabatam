import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function UnitSection() {
    const units = [
        {
            code: "RA",
            title: "RA Asy-Syuuraa",
            desc: "Pendidikan usia dini yang ceria, kreatif, dan menanamkan nilai-nilai Islam sejak dini.",
            color: "bg-green-100 text-green-800",
        },
        {
            code: "SDIT",
            title: "SDIT Asy-Syuuraa",
            desc: "Sekolah Dasar Islam Terpadu dengan kurikulum nasional dan penguatan Tahfidz Al-Qur'an.",
            color: "bg-yellow-100 text-yellow-800",
        },
        {
            code: "SMPIT",
            title: "SMPIT Asy-Syuuraa",
            desc: "Mencetak remaja muslim yang berkarakter, berprestasi akademik, dan hafal Al-Qur'an.",
            color: "bg-slate-100 text-slate-800",
        },
    ];

    return (
        <section className="py-20 bg-white">
            <div className="container mx-auto px-4">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-[var(--syuura-green)] mb-2">Unit Pendidikan</h2>
                    <p className="text-slate-500">Jenjang pendidikan berkualitas di bawah naungan Yayasan Asy-Syuuraa Batam</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {units.map((unit) => (
                        <Card key={unit.code} className="hover:shadow-lg transition-transform hover:-translate-y-1 border-t-4 border-t-[var(--syuura-green)]">
                            <CardHeader>
                                <div className={`w-12 h-12 rounded-lg ${unit.color} flex items-center justify-center font-bold mb-4`}>
                                    {unit.code}
                                </div>
                                <CardTitle className="text-xl font-bold text-slate-800">{unit.title}</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-slate-600 leading-relaxed">
                                    {unit.desc}
                                </p>
                            </CardContent>
                            <CardFooter>
                                <Button asChild variant="ghost" className="text-[var(--syuura-green)] hover:text-[var(--syuura-gold)] p-0">
                                    <Link href={`/${unit.code.toLowerCase()}`}>Selengkapnya &rarr;</Link>
                                </Button>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            </div>
        </section>
    );
}
