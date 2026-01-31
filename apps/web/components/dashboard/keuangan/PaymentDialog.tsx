"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Loader2, DollarSign } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { toast } from "sonner"

const formSchema = z.object({
    amount_paid: z.coerce.number().min(1, { message: "Nominal bayar wajib diisi." }),
    method: z.enum(["CASH", "TRANSFER"]),
    notes: z.string().optional(),
})

interface PaymentDialogProps {
    bill: { id: number, title: string, amount: number, status: string }
    onSuccess?: () => void
}

export function PaymentDialog({ bill, onSuccess }: PaymentDialogProps) {
    const [open, setOpen] = useState(false)
    const [isLoading, setIsLoading] = useState(false)

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            amount_paid: bill.amount, // Default full amount
            method: "CASH",
            notes: "",
        },
    })

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)
        try {
            const payload = {
                ...values,
                bill_id: bill.id
            }

            const API_URL = "http://localhost:8000"
            const response = await fetch(`${API_URL}/finance/payments`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(payload),
            })

            if (!response.ok) {
                throw new Error("Gagal menyimpan pembayaran")
            }

            toast.success("Pembayaran berhasil dicatat")
            setOpen(false)
            form.reset()
            onSuccess?.()
        } catch (error) {
            toast.error("Gagal mencatat pembayaran")
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button size="sm" className="bg-[var(--syuura-green)] hover:bg-[var(--syuura-green)]/90">
                    <DollarSign className="mr-2 h-4 w-4" /> Bayar
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Catat Pembayaran</DialogTitle>
                    <DialogDescription>
                        Pembayaran untuk: <b>{bill.title}</b><br />
                        Total Tagihan: Rp {bill.amount.toLocaleString('id-ID')}
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="amount_paid"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Nominal Diterima (Rp)</FormLabel>
                                    <FormControl>
                                        <Input type="number" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="method"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Metode Pembayaran</FormLabel>
                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Pilih metode" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="CASH">Tunai (Cash)</SelectItem>
                                            <SelectItem value="TRANSFER">Transfer Bank</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="notes"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Catatan (Opsional)</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Contoh: Diterima oleh Pak Budi" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <DialogFooter>
                            <Button type="submit" disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Simpan Pembayaran
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
