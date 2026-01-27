"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            // Prepare form data for OAuth2 format
            const formData = new URLSearchParams();
            formData.append("username", username);
            formData.append("password", password);

            const res = await fetch("http://localhost:8000/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: formData,
            });

            if (!res.ok) {
                throw new Error("Login failed");
            }

            const data = await res.json();

            // Store Token
            localStorage.setItem("token", data.access_token);

            toast.success("Login Berhasil!", { description: "Selamat datang kembali." });

            // Redirect
            router.push("/dashboard");

        } catch (error) {
            toast.error("Gagal Masuk", { description: "Periksa kembali NIK/Email dan Password Anda." });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[var(--syuura-green-surface)] p-4">

            {/* Back to Home Link */}
            <div className="absolute top-8 left-8">
                <Button asChild variant="ghost" className="text-[var(--syuura-green)] hover:bg-green-100">
                    <Link href="/">&larr; Kembali ke Beranda</Link>
                </Button>
            </div>

            <Card className="w-full max-w-md shadow-xl border-t-8 border-t-[var(--syuura-gold)]">
                <CardHeader className="space-y-1 text-center">
                    <div className="flex justify-center mb-4">
                        <div className="h-16 w-16 bg-[var(--syuura-green)] rounded-full flex items-center justify-center text-white text-2xl font-bold">
                            AS
                        </div>
                    </div>
                    <CardTitle className="text-2xl font-bold text-[var(--syuura-green)]">Login Sistem</CardTitle>
                    <CardDescription>
                        Masukkan NIK atau Email untuk masuk ke portal Asy-Syuuraa Batam
                    </CardDescription>
                </CardHeader>
                <form onSubmit={handleLogin}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">NIK / Email</Label>
                            <Input
                                id="username"
                                placeholder="Contoh: 1234567890"
                                required
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="pr-10"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700"
                                >
                                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                </button>
                            </div>
                        </div>
                    </CardContent>
                    <CardFooter className="flex flex-col gap-6 pt-4">
                        <Button
                            type="submit"
                            className="w-full bg-[var(--syuura-green)] hover:bg-[#14532D] text-white h-11 text-base"
                            disabled={isLoading}
                        >
                            {isLoading ? "Memproses..." : "Masuk Sekarang"}
                        </Button>
                        <p className="text-center text-sm text-slate-500">
                            Lupa password? <Link href="/forgot-password" className="font-semibold text-[var(--syuura-green)] hover:underline">Reset disini</Link>
                        </p>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
