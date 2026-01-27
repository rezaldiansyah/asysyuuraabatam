"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { ArrowLeft } from "lucide-react";

export default function ForgotPasswordPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [email, setEmail] = useState("");
    const [isSubmitted, setIsSubmitted] = useState(false);

    const handleReset = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const res = await fetch("http://localhost:8000/auth/forgot-password", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email }),
            });

            if (!res.ok) throw new Error("Gagal");

            setIsSubmitted(true);
            toast.success("Permintaan dikirim!", { description: "Cek email Anda untuk link reset password." });

        } catch (error) {
            toast.error("Gagal Mengirim", { description: "Terjadi kesalahan sistem." });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[var(--syuura-green-surface)] p-4">
            <div className="absolute top-8 left-8">
                <Button asChild variant="ghost" className="text-[var(--syuura-green)] hover:bg-green-100">
                    <Link href="/login"><ArrowLeft className="mr-2 h-4 w-4" /> Kembali ke Login</Link>
                </Button>
            </div>

            <Card className="w-full max-w-md shadow-xl border-t-8 border-t-[var(--syuura-gold)]">
                <CardHeader className="space-y-1 text-center">
                    <div className="flex justify-center mb-4">
                        <div className="h-16 w-16 bg-[var(--syuura-green)] rounded-full flex items-center justify-center text-white text-2xl font-bold">
                            AS
                        </div>
                    </div>
                    <CardTitle className="text-2xl font-bold text-[var(--syuura-green)]">Lupa Password</CardTitle>
                    <CardDescription>
                        Masukkan email yang terdaftar untuk reset password
                    </CardDescription>
                </CardHeader>

                {!isSubmitted ? (
                    <form onSubmit={handleReset}>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="nama@email.com"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        </CardContent>
                        <CardFooter className="flex flex-col gap-6 pt-4">
                            <Button
                                type="submit"
                                className="w-full bg-[var(--syuura-green)] hover:bg-[#14532D] text-white h-11 text-base"
                                disabled={isLoading}
                            >
                                {isLoading ? "Memproses..." : "Kirim Link Reset"}
                            </Button>
                        </CardFooter>
                    </form>
                ) : (
                    <CardContent className="space-y-6 pt-4">
                        <div className="bg-green-50 p-4 rounded-lg text-center border border-green-200">
                            <p className="text-green-800 font-medium">Link reset telah dikirim!</p>
                            <p className="text-sm text-green-600 mt-1">Silakan cek inbox email Anda ({email}).</p>
                        </div>
                        <Button asChild className="w-full bg-[var(--syuura-green)] text-white">
                            <Link href="/login">Kembali ke Login</Link>
                        </Button>
                    </CardContent>
                )}
            </Card>
        </div>
    );
}
