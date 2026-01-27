"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("token");

        if (!token) {
            toast.error("Akses Ditolak", { description: "Silakan login terlebih dahulu." });
            router.push("/login");
        } else {
            // TODO: Validate token expiry/validity with API later
            setIsAuthenticated(true);
        }
    }, [router]);

    if (!isAuthenticated) {
        return (
            <div className="flex h-screen w-full items-center justify-center bg-slate-50">
                <div className="flex flex-col items-center gap-4">
                    <div className="h-12 w-12 animate-spin rounded-full border-4 border-[var(--syuura-green)] border-t-transparent"></div>
                    <p className="text-slate-500 font-medium">Memverifikasi akses...</p>
                </div>
            </div>
        );
    }

    return <>{children}</>;
}
