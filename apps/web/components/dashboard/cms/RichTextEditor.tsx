"use client"

import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import { Separator } from "@/components/ui/separator"
import {
    Bold,
    Italic,
    List,
    ListOrdered,
    Quote,
    Heading2,
    ImageIcon,
    Loader2
} from "lucide-react"
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'

interface RichTextEditorProps {
    content: string
    onChange: (content: string) => void
}

export function RichTextEditor({ content, onChange }: RichTextEditorProps) {
    const [isUploading, setIsUploading] = useState(false)

    const editor = useEditor({
        extensions: [
            StarterKit,
            Image,
            Link.configure({
                openOnClick: false,
            }),
        ],
        content: content,
        editorProps: {
            attributes: {
                class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl m-2 focus:outline-none min-h-[200px] max-w-none',
            },
        },
        onUpdate: ({ editor }) => {
            onChange(editor.getHTML())
        },
    })

    // Update content if changed externally (e.g. from parent/reset)
    useEffect(() => {
        if (editor && content !== editor.getHTML()) {
            // Only update if content is really different to avoid cursor jumps
            // For simplicity in this edit form with reset, we can just check length or allow it
            // Ideally we compare semantic content. But for 'reset' case, it works.
            if (editor.isEmpty && content) {
                editor.commands.setContent(content)
            }
        }
    }, [content, editor])

    const uploadImage = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        setIsUploading(true)
        try {
            const formData = new FormData()
            formData.append('file', file)

            const token = localStorage.getItem("token")
            const API_URL = "http://localhost:8000"

            const response = await fetch(`${API_URL}/cms/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            })

            if (!response.ok) throw new Error('Upload failed')

            const data = await response.json()
            editor?.chain().focus().setImage({ src: data.url }).run()
        } catch (error) {
            console.error(error)
            alert("Gagal mengupload gambar")
        } finally {
            setIsUploading(false)
            // Reset input
            e.target.value = ""
        }
    }

    if (!editor) {
        return null
    }

    return (
        <div className="border rounded-md overflow-hidden bg-background">
            <div className="bg-muted/50 border-b p-2 flex flex-wrap gap-1 items-center">
                <Button
                    variant="ghost"
                    size="icon"
                    className={editor.isActive('bold') ? "bg-accent" : ""}
                    onClick={(e) => { e.preventDefault(); editor.chain().focus().toggleBold().run() }}
                    title="Bold"
                >
                    <Bold className="h-4 w-4" />
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className={editor.isActive('italic') ? "bg-accent" : ""}
                    onClick={(e) => { e.preventDefault(); editor.chain().focus().toggleItalic().run() }}
                    title="Italic"
                >
                    <Italic className="h-4 w-4" />
                </Button>
                <Separator orientation="vertical" className="h-6 mx-1" />
                <Button
                    variant="ghost"
                    size="icon"
                    className={editor.isActive('heading', { level: 2 }) ? "bg-accent" : ""}
                    onClick={(e) => { e.preventDefault(); editor.chain().focus().toggleHeading({ level: 2 }).run() }}
                    title="Heading 2"
                >
                    <Heading2 className="h-4 w-4" />
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className={editor.isActive('bulletList') ? "bg-accent" : ""}
                    onClick={(e) => { e.preventDefault(); editor.chain().focus().toggleBulletList().run() }}
                    title="Bullet List"
                >
                    <List className="h-4 w-4" />
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className={editor.isActive('orderedList') ? "bg-accent" : ""}
                    onClick={(e) => { e.preventDefault(); editor.chain().focus().toggleOrderedList().run() }}
                    title="Ordered List"
                >
                    <ListOrdered className="h-4 w-4" />
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className={editor.isActive('blockquote') ? "bg-accent" : ""}
                    onClick={(e) => { e.preventDefault(); editor.chain().focus().toggleBlockquote().run() }}
                    title="Blockquote"
                >
                    <Quote className="h-4 w-4" />
                </Button>
                <Separator orientation="vertical" className="h-6 mx-1" />
                <div className="relative">
                    <input
                        type="file"
                        className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                        accept="image/*"
                        onChange={uploadImage}
                        disabled={isUploading}
                        title="Upload Image"
                    />
                    <Button variant="ghost" size="icon" type="button" disabled={isUploading}>
                        {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ImageIcon className="h-4 w-4" />}
                    </Button>
                </div>
            </div>
            <div className="p-4 min-h-[300px] max-h-[500px] overflow-y-auto">
                <EditorContent editor={editor} />
            </div>
        </div>
    )
}
