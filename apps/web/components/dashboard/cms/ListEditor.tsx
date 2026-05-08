"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Plus, Trash2, ArrowUp, ArrowDown, BookOpen, Heart, Sun, Users, Trophy, ShieldCheck, Star, Sparkles, CheckCircle, Upload, Loader2 } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { toast } from "sonner"

export interface ListItem {
    id: string
    title: string
    description: string
    image_url?: string
    icon?: string
}

interface ListEditorProps {
    value: string // JSON string
    onChange: (json: string) => void
    titleLabel?: string
    descLabel?: string
    imageLabel?: string
    withIcon?: boolean
}

const AVAILABLE_ICONS = [
    { value: "BookOpen", label: "Buku/Pendidikan", icon: BookOpen },
    { value: "Heart", label: "Hati/Karakter", icon: Heart },
    { value: "Sun", label: "Matahari/Tahfidz", icon: Sun },
    { value: "Users", label: "Orang/Pengajar", icon: Users },
    { value: "Trophy", label: "Piala/Prestasi", icon: Trophy },
    { value: "ShieldCheck", label: "Perisai/Aman", icon: ShieldCheck },
    { value: "Star", label: "Bintang", icon: Star },
    { value: "Sparkles", label: "Kilau", icon: Sparkles },
    { value: "CheckCircle", label: "Centang", icon: CheckCircle },
]

export function ListEditor({ value, onChange, titleLabel = "Title", descLabel = "Description", imageLabel = "Image URL", withIcon = true }: ListEditorProps) {
    const [items, setItems] = useState<ListItem[]>([])
    const [uploadingIndex, setUploadingIndex] = useState<number | null>(null)

    useEffect(() => {
        try {
            if (value) {
                const parsed = JSON.parse(value)
                if (Array.isArray(parsed)) {
                    setItems(parsed)
                }
            } else {
                setItems([])
            }
        } catch (e) {
            console.error("Failed to parse list JSON", e)
            setItems([])
        }
    }, [value])

    const updateItems = (newItems: ListItem[]) => {
        setItems(newItems)
        onChange(JSON.stringify(newItems))
    }

    const addItem = () => {
        const newItem: ListItem = {
            id: Date.now().toString(),
            title: "",
            description: "",
            image_url: "",
            icon: "CheckCircle"
        }
        updateItems([...items, newItem])
    }

    const remoteItem = (index: number) => {
        const newItems = [...items]
        newItems.splice(index, 1)
        updateItems(newItems)
    }

    const moveItem = (index: number, direction: 'up' | 'down') => {
        if (direction === 'up' && index === 0) return
        if (direction === 'down' && index === items.length - 1) return

        const newItems = [...items]
        const temp = newItems[index]
        newItems[index] = newItems[index + (direction === 'up' ? -1 : 1)]
        newItems[index + (direction === 'up' ? -1 : 1)] = temp
        updateItems(newItems)
    }

    const updateItemField = (index: number, field: keyof ListItem, val: string) => {
        const newItems = [...items]
        newItems[index] = { ...newItems[index], [field]: val }
        updateItems(newItems)
    }

    const handleItemImageUpload = async (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
        const file = e.target.files?.[0]
        if (!file) return

        setUploadingIndex(index)
        try {
            const formData = new FormData()
            formData.append('file', file)

            const token = localStorage.getItem("token")
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const response = await fetch(`${API_URL}/cms/upload`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            })

            if (!response.ok) throw new Error('Upload failed')

            const data = await response.json()
            updateItemField(index, 'image_url', data.url)
            toast.success("Gambar berhasil diunggah")
        } catch (error) {
            console.error(error)
            toast.error("Gagal mengupload gambar")
        } finally {
            setUploadingIndex(null)
            e.target.value = ""
        }
    }

    return (
        <div className="space-y-4">
            {items.map((item, index) => (
                <Card key={item.id} className="relative">
                    <CardHeader className="py-2 px-4 bg-muted/30 flex flex-row items-center justify-between">
                        <CardTitle className="text-sm font-medium">Item #{index + 1}</CardTitle>
                        <div className="flex gap-1">
                            <Button variant="ghost" size="icon" onClick={() => moveItem(index, 'up')} disabled={index === 0}>
                                <ArrowUp className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => moveItem(index, 'down')} disabled={index === items.length - 1}>
                                <ArrowDown className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => remoteItem(index)} className="text-red-500 hover:text-red-600 hover:bg-red-50">
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="p-4 space-y-3">
                        <div className="grid grid-cols-[1fr_auto] gap-4 items-start">
                            <div className="space-y-3">
                                <div className="grid gap-2">
                                    <Label>{titleLabel}</Label>
                                    <Input
                                        value={item.title}
                                        onChange={(e) => updateItemField(index, 'title', e.target.value)}
                                        placeholder="Enter title..."
                                    />
                                </div>
                                <div className="grid gap-2">
                                    <Label>{descLabel}</Label>
                                    <Textarea
                                        value={item.description}
                                        onChange={(e) => updateItemField(index, 'description', e.target.value)}
                                        placeholder="Enter description..."
                                        className="min-h-[80px]"
                                    />
                                </div>
                            </div>

                            {withIcon && (
                                <div className="w-32 space-y-2">
                                    <Label>Icon</Label>
                                    <Select
                                        value={item.icon || "CheckCircle"}
                                        onValueChange={(val) => updateItemField(index, 'icon', val)}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {AVAILABLE_ICONS.map(icon => (
                                                <SelectItem key={icon.value} value={icon.value}>
                                                    <div className="flex items-center gap-2">
                                                        <icon.icon className="h-4 w-4" />
                                                        <span className="text-xs">{icon.label}</span>
                                                    </div>
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <div className="flex justify-center p-4 border rounded-md bg-slate-50">
                                        {(() => {
                                            const Icon = AVAILABLE_ICONS.find(i => i.value === item.icon)?.icon || CheckCircle
                                            return <Icon className="h-8 w-8 text-[var(--syuura-gold)]" />
                                        })()}
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="grid gap-2">
                            <Label>{imageLabel}</Label>
                            <div className="flex gap-2">
                                <Input
                                    value={item.image_url || ""}
                                    onChange={(e) => updateItemField(index, 'image_url', e.target.value)}
                                    placeholder="https://... atau upload gambar"
                                />
                                <div className="relative">
                                    <input type="file" className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" accept="image/*" onChange={(e) => handleItemImageUpload(e, index)} disabled={uploadingIndex === index} />
                                    <Button type="button" variant="outline" size="icon" disabled={uploadingIndex === index}>
                                        {uploadingIndex === index ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                                    </Button>
                                </div>
                            </div>
                            {item.image_url && (
                                <div className="rounded-md overflow-hidden border bg-muted/30">
                                    <img src={item.image_url} alt="Preview" className="w-full h-24 object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }} />
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            ))}

            <Button type="button" variant="outline" onClick={addItem} className="w-full border-dashed">
                <Plus className="mr-2 h-4 w-4" /> Add Item
            </Button>
        </div>
    )
}
