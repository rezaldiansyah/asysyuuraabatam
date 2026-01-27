"use client"

import { useEffect, useState } from "react"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Search, Filter, CircleDollarSign, History, Banknote, BookOpen, CreditCard } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"

import { PaymentCategoryDialog } from "@/components/dashboard/keuangan/PaymentCategoryDialog"
import { GenerateBillDialog } from "@/components/dashboard/keuangan/GenerateBillDialog"
import { PaymentDialog } from "@/components/dashboard/keuangan/PaymentDialog"
import { AccountFormDialog } from "@/components/dashboard/keuangan/AccountFormDialog"

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"

export default function KeuanganPage() {
    const [loading, setLoading] = useState(false)
    const [bills, setBills] = useState<any[]>([])
    const [categories, setCategories] = useState<any[]>([])
    const [accounts, setAccounts] = useState<any[]>([])
    const [journals, setJournals] = useState<any[]>([])

    const fetchBills = async () => {
        setLoading(true)
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/finance/bills`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setBills(data)
            }
        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    const fetchCategories = async () => {
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/finance/categories`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setCategories(data)
            }
        } catch (error) {
            console.error(error)
        }
    }

    const fetchAccounts = async () => {
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/finance/accounts`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setAccounts(data)
            }
        } catch (error) {
            console.error(error)
        }
    }

    const fetchJournals = async () => {
        try {
            const API_URL = "http://localhost:8000"
            const token = localStorage.getItem("token")
            const response = await fetch(`${API_URL}/finance/journals`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setJournals(data)
            }
        } catch (error) {
            console.error(error)
        }
    }


    useEffect(() => {
        fetchBills()
        fetchCategories()
        fetchAccounts()
        fetchJournals()
    }, [])

    const totalUnpaid = bills.filter(b => b.status === "UNPAID").reduce((acc, curr) => acc + curr.amount, 0)

    return (
        <div className="flex flex-col gap-4">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Keuangan & Akuntansi</h2>
                <p className="text-muted-foreground">Kelola tagihan, pembayaran, dan pembukuan sederhana.</p>
            </div>
            <Separator />

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Tagihan Aktif</CardTitle>
                        <CircleDollarSign className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">Rp {totalUnpaid.toLocaleString('id-ID')}</div>
                        <p className="text-xs text-muted-foreground">Potensi pendapatan tagihan unpaid</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Jurnal Transaksi</CardTitle>
                        <BookOpen className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{journals.length}</div>
                        <p className="text-xs text-muted-foreground">Entri jurnal tercatat</p>
                    </CardContent>
                </Card>
            </div>

            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="overview">Daftar Tagihan</TabsTrigger>
                    <TabsTrigger value="accounts">Daftar Akun (CoA)</TabsTrigger>
                    <TabsTrigger value="journals">Jurnal Umum</TabsTrigger>
                    <TabsTrigger value="categories">Master Kategori</TabsTrigger>
                </TabsList>

                {/* --- BILLS TAB --- */}
                <TabsContent value="overview" className="space-y-4">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                            <Input
                                placeholder="Cari siswa..."
                                className="w-[150px] lg:w-[250px]"
                            />
                        </div>
                        <div className="flex items-center space-x-2">
                            <GenerateBillDialog onSuccess={fetchBills} />
                        </div>
                    </div>

                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>ID</TableHead>
                                    <TableHead>Siswa ID</TableHead>
                                    <TableHead>Keterangan</TableHead>
                                    <TableHead>Nominal</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Tanggal</TableHead>
                                    <TableHead className="text-right">Aksi</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {bills.length === 0 ? (
                                    <TableRow><TableCell colSpan={7} className="h-24 text-center">Belum ada tagihan.</TableCell></TableRow>
                                ) : (
                                    bills.map((bill) => (
                                        <TableRow key={bill.id}>
                                            <TableCell className="font-mono text-xs">{bill.id}</TableCell>
                                            <TableCell><span className="font-medium">Siswa #{bill.student_id}</span></TableCell>
                                            <TableCell>{bill.title}</TableCell>
                                            <TableCell>Rp {bill.amount.toLocaleString('id-ID')}</TableCell>
                                            <TableCell>
                                                <Badge variant={bill.status === "PAID" ? "default" : bill.status === "PARTIAL" ? "secondary" : "destructive"}>
                                                    {bill.status}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>{new Date(bill.created_at).toLocaleDateString('id-ID')}</TableCell>
                                            <TableCell className="text-right">
                                                {bill.status !== "PAID" && (
                                                    <PaymentDialog bill={bill} onSuccess={() => { fetchBills(); fetchJournals(); }} />
                                                )}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </TabsContent>

                {/* --- ACCOUNTS TAB (CoA) --- */}
                <TabsContent value="accounts" className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium">Chart of Accounts (CoA)</h3>
                        <AccountFormDialog onSuccess={fetchAccounts} />
                    </div>
                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Kode Akun</TableHead>
                                    <TableHead>Nama Akun</TableHead>
                                    <TableHead>Tipe</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {accounts.length === 0 ? (
                                    <TableRow><TableCell colSpan={3} className="h-24 text-center">Belum ada akun.</TableCell></TableRow>
                                ) : (
                                    accounts.map((acc) => (
                                        <TableRow key={acc.id}>
                                            <TableCell className="font-medium">{acc.code}</TableCell>
                                            <TableCell>{acc.name}</TableCell>
                                            <TableCell><Badge variant="outline">{acc.type}</Badge></TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </TabsContent>

                {/* --- JOURNALS TAB --- */}
                <TabsContent value="journals" className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium">Jurnal Umum</h3>
                        {/* Filter date maybe */}
                    </div>
                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Tanggal</TableHead>
                                    <TableHead>No. Ref</TableHead>
                                    <TableHead>Keterangan</TableHead>
                                    <TableHead>Akun</TableHead>
                                    <TableHead className="text-right">Debit</TableHead>
                                    <TableHead className="text-right">Kredit</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {journals.length === 0 ? (
                                    <TableRow><TableCell colSpan={6} className="h-24 text-center">Belum ada jurnal.</TableCell></TableRow>
                                ) : (
                                    journals.map((journal) => (
                                        <>
                                            {/* Header Row for Journal Entry */}
                                            <TableRow key={`h-${journal.id}`} className="bg-muted/50">
                                                <TableCell className="font-medium">{new Date(journal.date).toLocaleDateString('id-ID')}</TableCell>
                                                <TableCell>{journal.reference_id}</TableCell>
                                                <TableCell colSpan={4} className="italic">{journal.description}</TableCell>
                                            </TableRow>
                                            {/* Item Rows */}
                                            {journal.items.map((item: any) => (
                                                <TableRow key={`i-${item.id}`} className="hover:bg-transparent">
                                                    <TableCell colSpan={3}></TableCell>
                                                    <TableCell className="pl-8">{item.account?.code} - {item.account?.name}</TableCell>
                                                    <TableCell className="text-right">{item.debit > 0 ? `Rp ${item.debit.toLocaleString('id-ID')}` : '-'}</TableCell>
                                                    <TableCell className="text-right">{item.credit > 0 ? `Rp ${item.credit.toLocaleString('id-ID')}` : '-'}</TableCell>
                                                </TableRow>
                                            ))}
                                        </>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </TabsContent>

                {/* --- CATEGORIES TAB --- */}
                <TabsContent value="categories" className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium">Jenis Pembayaran</h3>
                        <PaymentCategoryDialog onSuccess={fetchCategories} />
                    </div>
                    <div className="rounded-md border bg-white">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Nama Kategori</TableHead>
                                    <TableHead>Tipe</TableHead>
                                    <TableHead>Nominal Default</TableHead>
                                    <TableHead>Akun Pendapatan</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {categories.length === 0 ? (
                                    <TableRow><TableCell colSpan={4} className="h-24 text-center">Belum ada kategori.</TableCell></TableRow>
                                ) : (
                                    categories.map((cat) => (
                                        <TableRow key={cat.id}>
                                            <TableCell className="font-medium">{cat.name}</TableCell>
                                            <TableCell>{cat.type}</TableCell>
                                            <TableCell>Rp {cat.amount.toLocaleString('id-ID')}</TableCell>
                                            <TableCell className="text-muted-foreground text-sm">
                                                {cat.income_account_id ? `Akun #${cat.income_account_id}` : '-'}
                                            </TableCell>
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
