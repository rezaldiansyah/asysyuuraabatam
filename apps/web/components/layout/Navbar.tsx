"use client";

import Link from "next/link";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export function Navbar() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <nav className="sticky top-0 z-50 w-full border-b bg-white shadow-sm">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                {/* LOGO */}
                <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-[var(--syuura-green)]" />
                    <Link href="/" className="text-xl font-bold text-[var(--syuura-green)]">
                        Asy-Syuuraa
                    </Link>
                </div>

                {/* DESKTOP MENU */}
                <div className="hidden md:flex gap-6 items-center">
                    <Link href="/profil" className="text-sm font-medium text-slate-600 hover:text-[var(--syuura-green)]">
                        Profil
                    </Link>
                    <Link href="/unit" className="text-sm font-medium text-slate-600 hover:text-[var(--syuura-green)]">
                        Unit Pendidikan
                    </Link>
                    <Link href="/berita" className="text-sm font-medium text-slate-600 hover:text-[var(--syuura-green)]">
                        Berita
                    </Link>
                    <Link href="/ppdb" className="text-sm font-medium text-slate-600 hover:text-[var(--syuura-green)]">
                        PPDB
                    </Link>
                </div>

                {/* ACTION BUTTONS */}
                <div className="hidden md:flex items-center gap-2">
                    <Button asChild variant="outline" className="text-[var(--syuura-green)] border-[var(--syuura-green)] hover:bg-[var(--syuura-green-surface)]">
                        <Link href="/login">Log In</Link>
                    </Button>
                    <Button asChild className="bg-[var(--syuura-green)] hover:bg-[#14532D] text-white">
                        <Link href="/ppdb/daftar">Daftar PPDB</Link>
                    </Button>
                </div>

                {/* MOBILE MENU TOGGLE */}
                <button className="md:hidden" onClick={() => setIsOpen(!isOpen)}>
                    <Menu className="h-6 w-6 text-slate-600" />
                </button>
            </div>

            {/* MOBILE MENU CONTENT */}
            {isOpen && (
                <div className="md:hidden border-t bg-white p-4 flex flex-col gap-4">
                    <Link href="/profil" className="text-sm font-medium text-slate-600" onClick={() => setIsOpen(false)}>
                        Profil
                    </Link>
                    <Link href="/unit" className="text-sm font-medium text-slate-600" onClick={() => setIsOpen(false)}>
                        Unit Pendidikan
                    </Link>
                    <Link href="/berita" className="text-sm font-medium text-slate-600" onClick={() => setIsOpen(false)}>
                        Berita
                    </Link>
                    <Link href="/ppdb" className="text-sm font-medium text-slate-600" onClick={() => setIsOpen(false)}>
                        PPDB
                    </Link>
                    <div className="flex flex-col gap-2 mt-2">
                        <Button asChild variant="outline" className="w-full text-[var(--syuura-green)] border-[var(--syuura-green)]">
                            <Link href="/login">Log In</Link>
                        </Button>
                        <Button asChild className="w-full bg-[var(--syuura-green)] text-white">
                            <Link href="/ppdb/daftar">Daftar PPDB</Link>
                        </Button>
                    </div>
                </div>
            )}
        </nav>
    );
}
