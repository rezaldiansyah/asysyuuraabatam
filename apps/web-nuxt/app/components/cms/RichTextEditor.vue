<template>
  <div class="cms-editor-container border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden bg-white dark:bg-slate-900 focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all">
    <!-- Toolbar -->
    <div v-if="editor" class="flex flex-wrap items-center gap-1 p-2 bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-700 text-xs">
      <!-- Undo / Redo -->
      <div class="flex items-center gap-0.5">
        <button
          type="button"
          :disabled="!editor.can().undo()"
          @click="editor.chain().focus().undo().run()"
          class="tb-btn"
          title="Undo (Ctrl+Z)"
        >
          <i class="pi pi-undo text-xs"></i>
        </button>
        <button
          type="button"
          :disabled="!editor.can().redo()"
          @click="editor.chain().focus().redo().run()"
          class="tb-btn"
          title="Redo (Ctrl+Y)"
        >
          <i class="pi pi-refresh text-xs"></i>
        </button>
      </div>

      <div class="h-4 w-px bg-slate-200 dark:bg-slate-700 mx-1"></div>

      <!-- Heading Selector -->
      <select
        :value="currentHeading"
        @change="setHeading(($event.target as HTMLSelectElement).value)"
        class="text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded px-2 py-1 text-slate-700 dark:text-slate-200 focus:outline-none"
      >
        <option value="p">Teks Normal</option>
        <option value="1">Judul Besar (H1)</option>
        <option value="2">Sub Judul (H2)</option>
        <option value="3">Poin Penting (H3)</option>
      </select>

      <div class="h-4 w-px bg-slate-200 dark:bg-slate-700 mx-1"></div>

      <!-- Basic Formatting -->
      <div class="flex items-center gap-0.5">
        <button
          type="button"
          :class="{ 'is-active': editor.isActive('bold') }"
          @click="editor.chain().focus().toggleBold().run()"
          class="tb-btn font-bold"
          title="Tebal (Ctrl+B)"
        >
          B
        </button>
        <button
          type="button"
          :class="{ 'is-active': editor.isActive('italic') }"
          @click="editor.chain().focus().toggleItalic().run()"
          class="tb-btn italic font-serif"
          title="Miring (Ctrl+I)"
        >
          I
        </button>
        <button
          type="button"
          :class="{ 'is-active': editor.isActive('underline') }"
          @click="editor.chain().focus().toggleUnderline().run()"
          class="tb-btn underline"
          title="Garis Bawah (Ctrl+U)"
        >
          U
        </button>
        <button
          type="button"
          :class="{ 'is-active': editor.isActive('strike') }"
          @click="editor.chain().focus().toggleStrike().run()"
          class="tb-btn line-through"
          title="Coret"
        >
          S
        </button>
      </div>

      <div class="h-4 w-px bg-slate-200 dark:bg-slate-700 mx-1"></div>

      <!-- Alignment -->
      <div class="flex items-center gap-0.5">
        <button
          type="button"
          :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }"
          @click="editor.chain().focus().setTextAlign('left').run()"
          class="tb-btn"
          title="Rata Kiri"
        >
          <i class="pi pi-align-left text-xs"></i>
        </button>
        <button
          type="button"
          :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }"
          @click="editor.chain().focus().setTextAlign('center').run()"
          class="tb-btn"
          title="Rata Tengah"
        >
          <i class="pi pi-align-center text-xs"></i>
        </button>
        <button
          type="button"
          :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }"
          @click="editor.chain().focus().setTextAlign('right').run()"
          class="tb-btn"
          title="Rata Kanan"
        >
          <i class="pi pi-align-right text-xs"></i>
        </button>
      </div>

      <div class="h-4 w-px bg-slate-200 dark:bg-slate-700 mx-1"></div>

      <!-- Lists & Quotes -->
      <div class="flex items-center gap-0.5">
        <button
          type="button"
          :class="{ 'is-active': editor.isActive('bulletList') }"
          @click="editor.chain().focus().toggleBulletList().run()"
          class="tb-btn"
          title="Daftar Butir (Bullet)"
        >
          <i class="pi pi-list text-xs"></i>
        </button>
        <button
          type="button"
          :class="{ 'is-active': editor.isActive('orderedList') }"
          @click="editor.chain().focus().toggleOrderedList().run()"
          class="tb-btn"
          title="Daftar Angka (1, 2, 3)"
        >
          <i class="pi pi-sort-numeric-down text-xs"></i>
        </button>
        <button
          type="button"
          :class="{ 'is-active': editor.isActive('blockquote') }"
          @click="editor.chain().focus().toggleBlockquote().run()"
          class="tb-btn"
          title="Kutipan (Quote)"
        >
          <i class="pi pi-comment text-xs"></i>
        </button>
      </div>
    </div>

    <!-- Content Area -->
    <EditorContent
      :editor="editor"
      class="cms-tiptap-content p-4 text-slate-800 dark:text-slate-100"
      :style="{ minHeight: minHeight || '220px' }"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, watch, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import Placeholder from '@tiptap/extension-placeholder'

const props = defineProps<{
  modelValue?: string
  placeholder?: string
  minHeight?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const editor = useEditor({
  content: props.modelValue || '',
  extensions: [
    StarterKit.configure({
      heading: {
        levels: [1, 2, 3],
      },
    }),
    Underline,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
    Placeholder.configure({
      placeholder: props.placeholder || 'Tuliskan konten artikel di sini...',
    }),
  ],
  onUpdate: () => {
    if (!editor.value) return
    const html = editor.value.getHTML()
    emit('update:modelValue', html === '<p></p>' ? '' : html)
  },
})

watch(
  () => props.modelValue,
  (val) => {
    if (!editor.value) return
    const current = editor.value.getHTML()
    if ((val || '') !== current) {
      editor.value.commands.setContent(val || '', false)
    }
  }
)

const currentHeading = computed(() => {
  if (!editor.value) return 'p'
  if (editor.value.isActive('heading', { level: 1 })) return '1'
  if (editor.value.isActive('heading', { level: 2 })) return '2'
  if (editor.value.isActive('heading', { level: 3 })) return '3'
  return 'p'
})

function setHeading(val: string) {
  if (!editor.value) return
  if (val === 'p') {
    editor.value.chain().focus().setParagraph().run()
  } else {
    const level = parseInt(val) as 1 | 2 | 3
    editor.value.chain().focus().toggleHeading({ level }).run()
  }
}

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<style scoped>
.tb-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 0.25rem;
  color: #475569;
  transition: all 0.15s;
}
:deep(.dark) .tb-btn {
  color: #94a3b8;
}
.tb-btn:hover {
  background-color: #e2e8f0;
  color: #0f172a;
}
:deep(.dark) .tb-btn:hover {
  background-color: #334155;
  color: #f8fafc;
}
.tb-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.tb-btn.is-active {
  background-color: #dbeafe;
  color: #1d4ed8;
  font-weight: 700;
}
:deep(.dark) .tb-btn.is-active {
  background-color: #1e3a8a;
  color: #93c5fd;
}

:deep(.cms-tiptap-content .tiptap) {
  outline: none;
  font-size: 0.925rem;
  line-height: 1.65;
}

:deep(.cms-tiptap-content .tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: #94a3b8;
  pointer-events: none;
  height: 0;
}

:deep(.cms-tiptap-content h1) {
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

:deep(.cms-tiptap-content h2) {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 0.85rem;
  margin-bottom: 0.4rem;
}

:deep(.cms-tiptap-content h3) {
  font-size: 1.05rem;
  font-weight: 600;
  margin-top: 0.75rem;
  margin-bottom: 0.3rem;
}

:deep(.cms-tiptap-content ul) {
  list-style-type: disc;
  margin: 0.5rem 0 0.5rem 1.5rem;
}

:deep(.cms-tiptap-content ol) {
  list-style-type: decimal;
  margin: 0.5rem 0 0.5rem 1.5rem;
}

:deep(.cms-tiptap-content li) {
  margin-bottom: 0.25rem;
}

:deep(.cms-tiptap-content blockquote) {
  border-left: 3px solid #3b82f6;
  padding-left: 0.75rem;
  margin: 0.75rem 0;
  color: #64748b;
  font-style: italic;
}
:deep(.dark) .cms-tiptap-content blockquote {
  color: #94a3b8;
}
</style>
