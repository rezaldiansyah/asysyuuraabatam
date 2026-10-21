<template>
  <div class="gdocs-workspace">
    <!-- 1. Google Docs Floating Toolbar -->
    <div v-if="editor" class="gdocs-toolbar">
      <!-- Undo / Redo / Print -->
      <div class="flex items-center gap-0.5">
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :disabled="!editor.can().undo()"
          @click="editor.chain().focus().undo().run()" 
          title="Urungkan (Ctrl+Z)"
        >
          <i class="pi pi-undo text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :disabled="!editor.can().redo()"
          @click="editor.chain().focus().redo().run()" 
          title="Ulangi (Ctrl+Y)"
        >
          <i class="pi pi-refresh text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          @click="printDocument" 
          title="Cetak Dokumen"
        >
          <i class="pi pi-print text-xs"></i>
        </button>
      </div>

      <div class="gdocs-tb-divider"></div>

      <!-- Heading / Paragraph Style -->
      <div class="relative">
        <select 
          :value="currentHeadingValue" 
          @change="setHeadingStyle(($event.target as HTMLSelectElement).value)"
          class="gdocs-tb-select"
          title="Gaya Paragraf"
        >
          <option value="p">Teks Normal</option>
          <option value="1">Judul Utama (H1)</option>
          <option value="2">Sub Judul (H2)</option>
          <option value="3">Poin Bahasan (H3)</option>
        </select>
      </div>

      <div class="gdocs-tb-divider"></div>

      <!-- Text Formatting (B, I, U, S, Highlight) -->
      <div class="flex items-center gap-0.5">
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive('bold') }"
          @click="editor.chain().focus().toggleBold().run()" 
          title="Tebal (Ctrl+B)"
        >
          <span class="font-bold text-xs">B</span>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive('italic') }"
          @click="editor.chain().focus().toggleItalic().run()" 
          title="Miring (Ctrl+I)"
        >
          <span class="italic text-xs font-serif">I</span>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive('underline') }"
          @click="editor.chain().focus().toggleUnderline().run()" 
          title="Garis Bawah (Ctrl+U)"
        >
          <span class="underline text-xs">U</span>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive('strike') }"
          @click="editor.chain().focus().toggleStrike().run()" 
          title="Coret"
        >
          <span class="line-through text-xs">S</span>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive('highlight') }"
          @click="editor.chain().focus().toggleHighlight().run()" 
          title="Sorotan / Stabilo Kuning"
        >
          <i class="pi pi-pencil text-xs text-amber-500"></i>
        </button>
      </div>

      <div class="gdocs-tb-divider"></div>

      <!-- Alignment (Left, Center, Right, Justify) -->
      <div class="flex items-center gap-0.5">
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }"
          @click="editor.chain().focus().setTextAlign('left').run()" 
          title="Rata Kiri"
        >
          <i class="pi pi-align-left text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }"
          @click="editor.chain().focus().setTextAlign('center').run()" 
          title="Rata Tengah"
        >
          <i class="pi pi-align-center text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }"
          @click="editor.chain().focus().setTextAlign('right').run()" 
          title="Rata Kanan"
        >
          <i class="pi pi-align-right text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive({ textAlign: 'justify' }) }"
          @click="editor.chain().focus().setTextAlign('justify').run()" 
          title="Rata Kanan-Kiri (Justify)"
        >
          <i class="pi pi-align-justify text-xs"></i>
        </button>
      </div>

      <div class="gdocs-tb-divider"></div>

      <!-- Lists (Bullet, Numbered, Checklist) -->
      <div class="flex items-center gap-0.5">
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive('bulletList') }"
          @click="editor.chain().focus().toggleBulletList().run()" 
          title="Daftar Butir (Bullet •)"
        >
          <i class="pi pi-list text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive('orderedList') }"
          @click="editor.chain().focus().toggleOrderedList().run()" 
          title="Daftar Bernomor (1, 2, 3)"
        >
          <i class="pi pi-sort-numeric-down text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': editor.isActive('taskList') }"
          @click="editor.chain().focus().toggleTaskList().run()" 
          title="Daftar Centang (Checklist)"
        >
          <i class="pi pi-check-square text-xs"></i>
        </button>
      </div>

      <div class="gdocs-tb-divider"></div>

      <!-- Table Menu Dropdown (Clean & Elegant) -->
      <div class="relative">
        <button
          type="button"
          @click="showTableMenu = !showTableMenu"
          :class="{ 'is-active': editor.isActive('table') || showTableMenu }"
          class="gdocs-tb-btn !px-2 flex items-center gap-1 font-semibold text-xs text-slate-700 dark:text-slate-200"
          title="Menu Pengaturan Tabel"
        >
          <i class="pi pi-table text-xs text-primary"></i>
          <span>Tabel</span>
          <i class="pi pi-chevron-down text-[9px] text-slate-400"></i>
        </button>

        <!-- Dropdown Menu -->
        <div 
          v-if="showTableMenu" 
          v-click-outside="() => showTableMenu = false"
          class="absolute left-0 mt-1.5 w-60 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 py-1.5 z-50 text-xs font-sans"
        >
          <div class="px-3 py-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Sisipkan Tabel Baru
          </div>
          <button 
            type="button" 
            @click="insertYayasanTable(); showTableMenu = false" 
            class="w-full text-left px-3 py-1.5 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 flex items-center gap-2 font-medium"
          >
            <i class="pi pi-check-circle text-xs text-emerald-600"></i>
            <span>Tabel 4 Kolom (Resmi Yayasan)</span>
          </button>
          <button 
            type="button" 
            @click="insertCustomTable(3); showTableMenu = false" 
            class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-2"
          >
            <i class="pi pi-table text-xs text-slate-400"></i>
            <span>Tabel 3 Kolom (Masukan & Solusi)</span>
          </button>
          <button 
            type="button" 
            @click="insertCustomTable(2); showTableMenu = false" 
            class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-2"
          >
            <i class="pi pi-table text-xs text-slate-400"></i>
            <span>Tabel 2 Kolom (Sederhana)</span>
          </button>

          <div class="my-1 border-t border-slate-100 dark:border-slate-700"></div>

          <div class="px-3 py-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Aksi Baris & Kolom Aktif
          </div>
          <button 
            type="button" 
            :disabled="!editor.isActive('table')"
            @click="editor.chain().focus().addRowAfter().run(); showTableMenu = false" 
            class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 disabled:opacity-40 disabled:pointer-events-none flex items-center gap-2"
          >
            <i class="pi pi-plus text-xs text-emerald-600"></i>
            <span>Tambah Baris ke Bawah</span>
          </button>
          <button 
            type="button" 
            :disabled="!editor.isActive('table')"
            @click="editor.chain().focus().deleteRow().run(); showTableMenu = false" 
            class="w-full text-left px-3 py-1.5 hover:bg-rose-50 dark:hover:bg-rose-950/40 text-rose-700 dark:text-rose-400 disabled:opacity-40 disabled:pointer-events-none flex items-center gap-2"
          >
            <i class="pi pi-trash text-xs text-rose-500"></i>
            <span>Hapus Baris Ini</span>
          </button>
          <button 
            type="button" 
            :disabled="!editor.isActive('table')"
            @click="editor.chain().focus().addColumnAfter().run(); showTableMenu = false" 
            class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 disabled:opacity-40 disabled:pointer-events-none flex items-center gap-2"
          >
            <i class="pi pi-plus text-xs text-blue-600"></i>
            <span>Tambah Kolom ke Kanan</span>
          </button>
          <button 
            type="button" 
            :disabled="!editor.isActive('table')"
            @click="editor.chain().focus().deleteColumn().run(); showTableMenu = false" 
            class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 disabled:opacity-40 disabled:pointer-events-none flex items-center gap-2"
          >
            <i class="pi pi-minus text-xs text-slate-400"></i>
            <span>Hapus Kolom Ini</span>
          </button>
          <button 
            type="button" 
            :disabled="!editor.isActive('table')"
            @click="editor.chain().focus().mergeCells().run(); showTableMenu = false" 
            class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 disabled:opacity-40 disabled:pointer-events-none flex items-center gap-2"
          >
            <i class="pi pi-link text-xs text-purple-600"></i>
            <span>Gabungkan Sel (Merge)</span>
          </button>

          <div class="my-1 border-t border-slate-100 dark:border-slate-700"></div>

          <button 
            type="button" 
            :disabled="!editor.isActive('table')"
            @click="editor.chain().focus().deleteTable().run(); showTableMenu = false" 
            class="w-full text-left px-3 py-1.5 hover:bg-red-50 dark:hover:bg-red-950/40 text-red-600 disabled:opacity-40 disabled:pointer-events-none flex items-center gap-2 font-semibold"
          >
            <i class="pi pi-times-circle text-xs"></i>
            <span>Hapus Seluruh Tabel</span>
          </button>
        </div>
      </div>

      <div class="gdocs-tb-divider"></div>

      <!-- Quick Template & Clean -->
      <div class="flex items-center gap-1">
        <button 
          type="button" 
          @click="applyFullTemplate" 
          class="gdocs-template-pill"
          title="Sisipkan struktur notulen resmi lengkap"
        >
          <i class="pi pi-file text-xs text-amber-600"></i>
          <span>Template Lengkap</span>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          @click="editor.chain().focus().unsetAllMarks().clearNodes().run()" 
          title="Bersihkan Format"
        >
          <i class="pi pi-filter-slash text-xs"></i>
        </button>
      </div>
    </div>

    <!-- 2. Google Docs Page Ruler Bar -->
    <div class="gdocs-ruler select-none">
      <div class="gdocs-ruler-track">
        <div class="gdocs-ruler-marker-left"></div>
        <div class="flex justify-between w-full px-10 text-[9px] font-mono text-slate-400">
          <span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span>
        </div>
        <div class="gdocs-ruler-marker-right"></div>
      </div>
    </div>

    <!-- 3. The Document Paper Canvas (White A4 Sheet) -->
    <div class="gdocs-paper-container">
      <div class="gdocs-paper">
        <EditorContent :editor="editor" class="tiptap-content" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { Table, TableRow, TableCell, TableHeader } from '@tiptap/extension-table'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import Link from '@tiptap/extension-link'
import Highlight from '@tiptap/extension-highlight'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Placeholder from '@tiptap/extension-placeholder'

const props = defineProps<{
  modelValue?: string
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const showTableMenu = ref(false)

// Custom Click-Outside Directive
const vClickOutside = {
  mounted(el: any, binding: any) {
    el.__clickOutsideHandler__ = (event: Event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el.__clickOutsideHandler__)
  },
  unmounted(el: any) {
    document.removeEventListener('click', el.__clickOutsideHandler__)
  }
}

const editor = useEditor({
  content: props.modelValue || '',
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3] },
      bulletList: { keepMarks: true, keepAttributes: false },
      orderedList: { keepMarks: true, keepAttributes: false },
    }),
    Underline,
    Highlight.configure({ multicolor: false }),
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
    Link.configure({
      openOnClick: false,
      autolink: true,
    }),
    TaskList,
    TaskItem.configure({ nested: true }),
    Table.configure({
      resizable: true,
      HTMLAttributes: {
        class: 'notulen-table',
      },
    }),
    TableRow,
    TableHeader,
    TableCell,
    Placeholder.configure({
      placeholder: props.placeholder || 'Ketik catatan pembahasan rapat di sini layaknya Google Docs...',
    }),
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

// Sync incoming modelValue changes
watch(
  () => props.modelValue,
  (newVal) => {
    if (!editor.value) return
    const isSame = editor.value.getHTML() === newVal
    if (!isSame) {
      editor.value.commands.setContent(newVal || '', false)
    }
  }
)

onBeforeUnmount(() => {
  editor.value?.destroy()
})

// Current Heading selector value
const currentHeadingValue = computed(() => {
  if (!editor.value) return 'p'
  if (editor.value.isActive('heading', { level: 1 })) return '1'
  if (editor.value.isActive('heading', { level: 2 })) return '2'
  if (editor.value.isActive('heading', { level: 3 })) return '3'
  return 'p'
})

function setHeadingStyle(val: string) {
  if (!editor.value) return
  if (val === 'p') {
    editor.value.chain().focus().setParagraph().run()
  } else {
    const level = parseInt(val, 10) as 1 | 2 | 3
    editor.value.chain().focus().toggleHeading({ level }).run()
  }
}

function printDocument() {
  window.print()
}

// Insert Yayasan Standard 4-Column Table
function insertYayasanTable() {
  if (!editor.value) return
  const html = `
    <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
      <thead>
        <tr style="background-color: #f1f5f9; font-weight: bold;">
          <th style="width: 40px; text-align: center; padding: 8px; border: 1px solid #94a3b8;">No</th>
          <th style="width: 22%; padding: 8px; border: 1px solid #94a3b8; text-align: left;">Perihal / Topik</th>
          <th style="width: 48%; padding: 8px; border: 1px solid #94a3b8; text-align: left;">Pembahasan / Arahan Pimpinan</th>
          <th style="padding: 8px; border: 1px solid #94a3b8; text-align: left;">Tindak Lanjut</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;"><p>1</p></td>
          <td style="padding: 8px; border: 1px solid #94a3b8;"><p>Topik pembahasan pertama...</p></td>
          <td style="padding: 8px; border: 1px solid #94a3b8;"><p>a. Poin arahan pimpinan...<br>b. Solusi yang disepakati...</p></td>
          <td style="padding: 8px; border: 1px solid #94a3b8;"><p>PIC dan batas waktu...</p></td>
        </tr>
      </tbody>
    </table>
    <p></p>
  `
  editor.value.chain().focus().insertContent(html).run()
}

// Insert Custom Column Table
function insertCustomTable(cols: 2 | 3) {
  if (!editor.value) return
  if (cols === 3) {
    const html = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <thead>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <th style="width: 40px; text-align: center; padding: 8px; border: 1px solid #94a3b8;">No</th>
            <th style="width: 32%; padding: 8px; border: 1px solid #94a3b8; text-align: left;">Topik / Masukan Peserta</th>
            <th style="padding: 8px; border: 1px solid #94a3b8; text-align: left;">Tanggapan & Kesepakatan Bersama</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;"><p>1</p></td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"><p></p></td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"><p></p></td>
          </tr>
        </tbody>
      </table>
      <p></p>
    `
    editor.value.chain().focus().insertContent(html).run()
  } else {
    const html = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <thead>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <th style="width: 40px; text-align: center; padding: 8px; border: 1px solid #94a3b8;">No</th>
            <th style="padding: 8px; border: 1px solid #94a3b8; text-align: left;">Poin Pembahasan / Catatan Rapat</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;"><p>1</p></td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"><p></p></td>
          </tr>
        </tbody>
      </table>
      <p></p>
    `
    editor.value.chain().focus().insertContent(html).run()
  }
}

// Full Official Notulen Template
function applyFullTemplate() {
  if (!editor.value) return
  const currentContent = editor.value.getText().trim()
  if (currentContent.length > 20) {
    if (!confirm('Konten yang ada akan diganti dengan format template resmi yayasan. Lanjutkan?')) {
      return
    }
  }

  const templateHtml = `
    <h2>NOTULENSI RAPAT</h2>
    <p></p>

    <h3>1. Pembukaan & Pengantar Pimpinan</h3>
    <p>Rapat dibuka secara resmi dengan membaca Basmalah dan arahan singkat pimpinan terkait agenda rapat hari ini.</p>
    <p></p>

    <h3>2. Pembahasan Pokok & Jalannya Diskusi</h3>
    <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
      <thead>
        <tr style="background-color: #f1f5f9; font-weight: bold;">
          <th style="width: 40px; text-align: center; padding: 8px; border: 1px solid #94a3b8;">No</th>
          <th style="width: 22%; padding: 8px; border: 1px solid #94a3b8; text-align: left;">Perihal / Topik</th>
          <th style="width: 48%; padding: 8px; border: 1px solid #94a3b8; text-align: left;">Pembahasan / Arahan Pimpinan</th>
          <th style="padding: 8px; border: 1px solid #94a3b8; text-align: left;">Tindak Lanjut</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;"><p>1</p></td>
          <td style="padding: 8px; border: 1px solid #94a3b8;"><p>Evaluasi Kegiatan & Perencanaan Program</p></td>
          <td style="padding: 8px; border: 1px solid #94a3b8;">
            <p>Rangkuman pembahasan dan arahan pimpinan:</p>
            <ul>
              <li>Poin arahan pertama terkait jadwal dan koordinasi lapangan.</li>
              <li>Poin arahan kedua terkait penganggaran serta persiapan teknis.</li>
            </ul>
          </td>
          <td style="padding: 8px; border: 1px solid #94a3b8;">
            <p>Tim terkait menuntaskan persiapan sebelum batas waktu yang disepakati.</p>
          </td>
        </tr>
      </tbody>
    </table>
    <p></p>

    <h3>3. Catatan Khusus & Penutup</h3>
    <p>Rapat ditutup dengan pembacaan Hamdalah dan doa bersama. Seluruh tindak lanjut diharapkan diselesaikan sesuai tenggat waktu yang disepakati.</p>
    <p></p>
  `
  editor.value.commands.setContent(templateHtml, true)
}

// Expose methods for parent if needed
defineExpose({
  editor,
  insertYayasanTable,
  insertCustomTable,
  applyFullTemplate,
})
</script>

<style scoped>
/* =========================================================================
   GOOGLE DOCS STYLE WORKSPACE & CANVAS
   ========================================================================= */
.gdocs-workspace {
  background-color: #f0f4f9;
  border-radius: 1rem;
  border: 1px solid #e2e8f0;
  padding: 1rem 0.5rem 2rem 0.5rem;
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.03);
}
:deep(.dark) .gdocs-workspace {
  background-color: #0b1329;
  border-color: #1e293b;
}

/* Sticky Google Docs Toolbar */
.gdocs-toolbar {
  position: sticky;
  top: 0.5rem;
  z-index: 25;
  background-color: #ffffff;
  border-radius: 9999px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.08);
  padding: 0.35rem 0.85rem;
  margin: 0 auto 0.75rem auto;
  max-width: 860px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem;
}
:deep(.dark) .gdocs-toolbar {
  background-color: #1e293b;
  border-color: #334155;
  box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.35);
}

/* Toolbar Divider */
.gdocs-tb-divider {
  width: 1px;
  height: 1.25rem;
  background-color: #e2e8f0;
  margin: 0 0.25rem;
}
:deep(.dark) .gdocs-tb-divider {
  background-color: #475569;
}

/* Toolbar Icon Buttons */
.gdocs-tb-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 0.375rem;
  color: #475569;
  transition: all 0.15s;
  background: transparent;
  border: none;
  cursor: pointer;
}
.gdocs-tb-btn:hover:not(:disabled) {
  background-color: #f1f5f9;
  color: #0f172a;
}
.gdocs-tb-btn.is-active {
  background-color: #e0e7ff;
  color: #3730a3;
  font-weight: 700;
}
:deep(.dark) .gdocs-tb-btn {
  color: #94a3b8;
}
:deep(.dark) .gdocs-tb-btn:hover:not(:disabled) {
  background-color: #334155;
  color: #f8fafc;
}
:deep(.dark) .gdocs-tb-btn.is-active {
  background-color: #312e81;
  color: #c7d2fe;
}
.gdocs-tb-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

/* Toolbar Select Dropdown */
.gdocs-tb-select {
  font-size: 0.75rem;
  font-weight: 600;
  color: #334155;
  background-color: transparent;
  border: 1px solid transparent;
  border-radius: 0.375rem;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  outline: none;
  transition: all 0.15s;
}
.gdocs-tb-select:hover {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
}
:deep(.dark) .gdocs-tb-select {
  color: #cbd5e1;
}
:deep(.dark) .gdocs-tb-select:hover {
  background-color: #334155;
  border-color: #475569;
}

/* Template Pill */
.gdocs-template-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 0.375rem;
  background-color: #fffbeb;
  color: #92400e;
  border: 1px solid #fde68a;
  cursor: pointer;
  transition: all 0.15s;
}
.gdocs-template-pill:hover {
  background-color: #fef3c7;
}
:deep(.dark) .gdocs-template-pill {
  background-color: rgba(120, 53, 15, 0.2);
  color: #fcd34d;
  border-color: #78350f;
}

/* Google Docs Ruler Bar */
.gdocs-ruler {
  max-width: 820px;
  margin: 0 auto 0.6rem auto;
  height: 16px;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 2px;
  position: relative;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
:deep(.dark) .gdocs-ruler {
  background-color: #1e293b;
  border-color: #334155;
}
.gdocs-ruler-track {
  width: 100%;
  display: flex;
  align-items: center;
  position: relative;
}
.gdocs-ruler-marker-left {
  position: absolute;
  left: 20px;
  top: 1px;
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid #2563eb;
}
.gdocs-ruler-marker-right {
  position: absolute;
  right: 20px;
  top: 1px;
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid #2563eb;
}

/* The Document Paper (A4 White Sheet) */
.gdocs-paper-container {
  display: flex;
  justify-content: center;
}

.gdocs-paper {
  background-color: #ffffff;
  width: 100%;
  max-width: 820px;
  min-height: 750px;
  margin: 0 auto;
  padding: 48px 56px;
  border-radius: 2px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(60,64,67,.15), 0 2px 6px 2px rgba(60,64,67,.1);
  font-family: Arial, 'Plus Jakarta Sans', system-ui, sans-serif;
  font-size: 11pt;
  line-height: 1.65;
  color: #1e293b;
}
:deep(.dark) .gdocs-paper {
  background-color: #0f172a;
  border-color: #1e293b;
  box-shadow: 0 4px 14px rgba(0,0,0,0.4);
  color: #f1f5f9;
}

/* =========================================================================
   TIPTAP CONTENT STYLES INSIDE DOCUMENT
   ========================================================================= */
:deep(.tiptap-content .tiptap) {
  outline: none !important;
  min-height: 650px;
}

:deep(.tiptap-content .tiptap p.is-editor-empty:first-child::before) {
  color: #94a3b8;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

:deep(.tiptap-content .tiptap h1) {
  font-size: 1.6rem;
  font-weight: 700;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
  color: #0f172a;
}
:deep(.tiptap-content .tiptap h2) {
  font-size: 1.3rem;
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #0f172a;
}
:deep(.tiptap-content .tiptap h3) {
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 0.75rem;
  margin-bottom: 0.35rem;
  color: #1e293b;
}
:deep(.dark) .tiptap-content .tiptap h1,
:deep(.dark) .tiptap-content .tiptap h2,
:deep(.dark) .tiptap-content .tiptap h3 {
  color: #f8fafc;
}

:deep(.tiptap-content .tiptap p) {
  margin: 0.4rem 0;
}

/* Bullet & Numbered lists */
:deep(.tiptap-content .tiptap ul) {
  list-style-type: disc !important;
  padding-left: 1.75rem !important;
  margin: 0.5rem 0 !important;
}
:deep(.tiptap-content .tiptap ol) {
  list-style-type: decimal !important;
  padding-left: 1.75rem !important;
  margin: 0.5rem 0 !important;
}
:deep(.tiptap-content .tiptap li) {
  padding-left: 0.25rem !important;
  margin-bottom: 0.25rem;
}

/* Task lists (Checklist) */
:deep(.tiptap-content .tiptap ul[data-type="taskList"]) {
  list-style: none !important;
  padding: 0 !important;
}
:deep(.tiptap-content .tiptap ul[data-type="taskList"] li) {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}
:deep(.tiptap-content .tiptap ul[data-type="taskList"] li > label) {
  flex: 0 0 auto;
  user-select: none;
  margin-top: 0.2rem;
}
:deep(.tiptap-content .tiptap ul[data-type="taskList"] li > div) {
  flex: 1 1 auto;
}

/* =========================================================================
   TABLE STYLING (FLAWLESS NESTED LISTS & BORDERS)
   ========================================================================= */
:deep(.tiptap-content .tiptap table) {
  width: 100% !important;
  border-collapse: collapse !important;
  margin: 1.25rem 0 !important;
  table-layout: auto !important;
  border: 1px solid #94a3b8 !important;
}

:deep(.tiptap-content .tiptap table th),
:deep(.tiptap-content .tiptap table td) {
  border: 1px solid #94a3b8 !important;
  padding: 8px 12px !important;
  vertical-align: top !important;
  box-sizing: border-box !important;
  line-height: 1.6 !important;
  min-width: 45px;
  position: relative;
}

:deep(.tiptap-content .tiptap table th) {
  background-color: #f1f5f9 !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  border-bottom: 2px solid #64748b !important;
  text-align: left;
}

:deep(.tiptap-content .tiptap table th:first-child),
:deep(.tiptap-content .tiptap table td:first-child) {
  width: 45px !important;
  text-align: center !important;
  font-weight: 600 !important;
}

/* Selected cell / active cell */
:deep(.tiptap-content .tiptap table .selectedCell) {
  background-color: rgba(224, 231, 255, 0.4) !important;
}

/* Table resize handle */
:deep(.tiptap-content .tiptap table .column-resize-handle) {
  background-color: #3b82f6;
  bottom: -2px;
  position: absolute;
  right: -2px;
  pointer-events: none;
  top: 0;
  width: 4px;
}

/* Dark mode tables */
:deep(.dark) .tiptap-content .tiptap table {
  border-color: #475569 !important;
}
:deep(.dark) .tiptap-content .tiptap table th,
:deep(.dark) .tiptap-content .tiptap table td {
  border-color: #475569 !important;
}
:deep(.dark) .tiptap-content .tiptap table th {
  background-color: #1e293b !important;
  color: #f8fafc !important;
  border-bottom-color: #94a3b8 !important;
}
:deep(.dark) .tiptap-content .tiptap table .selectedCell {
  background-color: rgba(49, 46, 129, 0.4) !important;
}
</style>
