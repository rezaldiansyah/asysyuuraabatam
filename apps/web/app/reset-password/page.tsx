"use client";

import { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { Eye, EyeOff } from "lucide-react";

function ResetPasswordForm() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const token = searchParams.get("token");

    const [isLoading, setIsLoading] = useState(false);
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    if (!token) {
        return (
            <div className="text-center p-6 text-red-500">
                Token tidak valid atau tidak ditemukan.
            </div>
        );
    }

    const handleReset = async (e: React.FormEvent) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            toast.error("Password Tidak Sama", { description: "Pastikan konfirmasi password sesuai." });
            return;
        }

        setIsLoading(true);

        try {
            const res = await fetch("http://localhost:8000/auth/reset-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token, new_password: password }),
            });

            if (!res.ok) throw new Error("Gagal reset");

            toast.success("Password Berhasil Direset", { description: "Silakan login dengan password baru." });
            router.push("/login");

        } catch (error) {
            toast.error("Gagal Reset Password", { description: "Token mungkin sudah kadaluarsa." });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleReset}>
            <CardContent className="space-y-4">
                <div className="space-y-2">
                    <Label htmlFor="password">Password Baru</Label>
                    <div className="relative">
                        <Input
                            id="password"
                            type={showPassword ? "text" : "password"}
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            minLength={8}
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500"
                        >
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                    </div>
                </div>
                <div className="space-y-2">
                    <Label htmlFor="confirm">Konfirmasi Password</Label>
                    <Input
                        id="confirm"
                        type="password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                </div>
            </CardContent>
            <CardFooter className="pt-4">
                <Button type="submit" className="w-full bg-[var(--syuura-green)] hover:bg-[#14532D]" disabled={isLoading}>
                    {isLoading ? "Menyimpan..." : "Simpan Password Baru"}
                </Button>
            </CardFooter>
        </form>
    );
}

export default function ResetPasswordPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-[var(--syuura-green-surface)] p-4">
            <Card className="w-full max-w-md shadow-xl border-t-8 border-t-[var(--syuura-gold)]">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold text-[var(--syuura-green)]">Reset Password</CardTitle>
                    <CardDescription>Masukkan password baru Anda</CardDescription>
                </CardHeader>
                <Suspense fallback={<div className="p-8 text-center">Loading...</div>}>
                    <ResetPasswordForm />
                </Suspense>
            </Card>
        </div>
    );
}
