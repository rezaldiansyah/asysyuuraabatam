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
          :class="{ 'is-active': isAlignActive('left') }"
          @click="editor.chain().focus().setTextAlign('left').run()" 
          title="Rata Kiri"
        >
          <i class="pi pi-align-left text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': isAlignActive('center') }"
          @click="editor.chain().focus().setTextAlign('center').run()" 
          title="Rata Tengah"
        >
          <i class="pi pi-align-center text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': isAlignActive('right') }"
          @click="editor.chain().focus().setTextAlign('right').run()" 
          title="Rata Kanan"
        >
          <i class="pi pi-align-right text-xs"></i>
        </button>
        <button 
          type="button" 
          class="gdocs-tb-btn" 
          :class="{ 'is-active': isAlignActive('justify') }"
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

      <!-- Group 6: Table Menu & 1-Click Quick Table -->
      <div class="relative flex items-center" ref="tableDropdownRef">
        <!-- 1-Click Quick Insert Yayasan Table -->
        <button
          type="button"
          @click="insertYayasanTable"
          class="gdocs-tb-btn !px-2 flex items-center gap-1 font-semibold text-xs text-emerald-700 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/40"
          title="1-Klik: Sisipkan Tabel Resmi Yayasan (4 Kolom)"
        >
          <i class="pi pi-table text-xs text-emerald-600"></i>
          <span>+ Tabel</span>
        </button>

        <!-- Dropdown trigger for more formats -->
        <button
          type="button"
          @click.stop="toggleTableMenu"
          :class="{ 'is-active': showTableMenu }"
          class="gdocs-tb-btn !w-5 !px-0 flex items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
          title="Pilihan Format Tabel Lainnya"
        >
          <i class="pi pi-chevron-down text-[8px]"></i>
        </button>

        <!-- Dropdown Menu -->
        <div 
          v-if="showTableMenu" 
          class="absolute left-0 top-full mt-1.5 w-64 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 py-2 z-50 text-xs font-sans"
        >
          <div class="px-3 py-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Sisipkan Tabel Baru
          </div>
          <button 
            type="button" 
            @click="insertYayasanTable" 
            class="w-full text-left px-3 py-2 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 flex items-center gap-2 font-medium"
          >
            <i class="pi pi-check-circle text-xs text-emerald-600"></i>
            <div>
              <div class="font-semibold">Tabel Format Yayasan (4 Kolom)</div>
              <div class="text-[10px] text-slate-500 font-normal">No, Topik, Arahan Pimpinan, Tindak Lanjut</div>
            </div>
          </button>
          <button 
            type="button" 
            @click="insertCustomTable(3)" 
            class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-2"
          >
            <i class="pi pi-table text-xs text-slate-400"></i>
            <span>Tabel 3 Kolom (Masukan & Solusi)</span>
          </button>
          <button 
            type="button" 
            @click="insertCustomTable(2)" 
            class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-2"
          >
            <i class="pi pi-table text-xs text-slate-400"></i>
            <span>Tabel 2 Kolom (Sederhana)</span>
          </button>
          <button 
            type="button" 
            @click="insertStandardTable(3, 3)" 
            class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-2"
          >
            <i class="pi pi-th-large text-xs text-slate-400"></i>
            <span>Tabel Standar Grid (3 x 3)</span>
          </button>

          <template v-if="editor.isActive('table')">
            <div class="my-1 border-t border-slate-100 dark:border-slate-700"></div>

            <div class="px-3 py-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Aksi Baris & Kolom Aktif
            </div>
            <button 
              type="button" 
              @click="editor.chain().focus().addRowAfter().run(); showTableMenu = false" 
              class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-2"
            >
              <i class="pi pi-plus text-xs text-emerald-600"></i>
              <span>Tambah Baris ke Bawah</span>
            </button>
            <button 
              type="button" 
              @click="editor.chain().focus().deleteRow().run(); showTableMenu = false" 
              class="w-full text-left px-3 py-1.5 hover:bg-rose-50 dark:hover:bg-rose-950/40 text-rose-700 dark:text-rose-400 flex items-center gap-2"
            >
              <i class="pi pi-trash text-xs text-rose-500"></i>
              <span>Hapus Baris Ini</span>
            </button>
            <button 
              type="button" 
              @click="editor.chain().focus().addColumnAfter().run(); showTableMenu = false" 
              class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-2"
            >
              <i class="pi pi-plus text-xs text-blue-600"></i>
              <span>Tambah Kolom ke Kanan</span>
            </button>
            <button 
              type="button" 
              @click="editor.chain().focus().deleteColumn().run(); showTableMenu = false" 
              class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-2"
            >
              <i class="pi pi-minus text-xs text-slate-400"></i>
              <span>Hapus Kolom Ini</span>
            </button>
            <button 
              type="button" 
              @click="editor.chain().focus().mergeOrSplit().run(); showTableMenu = false" 
              class="w-full text-left px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-2"
            >
              <i class="pi pi-link text-xs text-purple-600"></i>
              <span>Gabung / Pisahkan Sel (Merge/Split)</span>
            </button>

            <div class="my-1 border-t border-slate-100 dark:border-slate-700"></div>

            <button 
              type="button" 
              @click="editor.chain().focus().deleteTable().run(); showTableMenu = false" 
              class="w-full text-left px-3 py-1.5 hover:bg-red-50 dark:hover:bg-red-950/40 text-red-600 flex items-center gap-2 font-semibold"
            >
              <i class="pi pi-times-circle text-xs"></i>
              <span>Hapus Seluruh Tabel</span>
            </button>
          </template>
        </div>
      </div>

      <!-- Quick Contextual Action Bar when inside a table -->
      <div v-if="editor.isActive('table')" class="flex items-center gap-0.5 bg-emerald-50 dark:bg-emerald-950/40 px-1.5 py-0.5 rounded-lg border border-emerald-200 dark:border-emerald-800">
        <button 
          type="button" 
          @click="editor.chain().focus().addRowAfter().run()" 
          class="gdocs-tb-btn !w-auto !h-6 !px-1.5 text-[11px] font-medium text-emerald-700 dark:text-emerald-300"
          title="Tambah Baris (+)"
        >
          <i class="pi pi-plus text-[9px] mr-1"></i> Baris
        </button>
        <button 
          type="button" 
          @click="editor.chain().focus().addColumnAfter().run()" 
          class="gdocs-tb-btn !w-auto !h-6 !px-1.5 text-[11px] font-medium text-blue-700 dark:text-blue-300"
          title="Tambah Kolom (+)"
        >
          <i class="pi pi-plus text-[9px] mr-1"></i> Kolom
        </button>
        <button 
          type="button" 
          @click="editor.chain().focus().deleteRow().run()" 
          class="gdocs-tb-btn !w-auto !h-6 !px-1 text-[11px] text-rose-600 dark:text-rose-400"
          title="Hapus Baris"
        >
          <i class="pi pi-trash text-[10px]"></i>
        </button>
        <button 
          type="button" 
          @click="editor.chain().focus().mergeOrSplit().run()" 
          class="gdocs-tb-btn !w-auto !h-6 !px-1 text-[11px] text-purple-600 dark:text-purple-400"
          title="Merge / Split"
        >
          <i class="pi pi-link text-[10px]"></i>
        </button>
        <button 
          type="button" 
          @click="editor.chain().focus().deleteTable().run()" 
          class="gdocs-tb-btn !w-auto !h-6 !px-1 text-[11px] text-red-600"
          title="Hapus Tabel"
        >
          <i class="pi pi-times-circle text-[10px]"></i>
        </button>
      </div>

      <div class="gdocs-tb-divider"></div>

      <!-- Group 7: Template & Clean -->
      <div class="flex items-center gap-1">
        <button 
          type="button" 
          @click="applyFullTemplate" 
          class="gdocs-template-pill"
          title="Sisipkan struktur notulen resmi lengkap yayasan"
        >
          <i class="pi pi-file text-xs text-amber-600"></i>
          <span>Template</span>
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

const tableDropdownRef = ref<HTMLElement | null>(null)
const showTableMenu = ref(false)

function toggleTableMenu() {
  showTableMenu.value = !showTableMenu.value
}

function handleOutsideClick(event: MouseEvent) {
  if (!showTableMenu.value) return
  if (tableDropdownRef.value && !tableDropdownRef.value.contains(event.target as Node)) {
    showTableMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('pointerdown', handleOutsideClick)
})

const editor = useEditor({
  content: props.modelValue || '',
  editorProps: {
    attributes: {
      class: 'tiptap ProseMirror focus:outline-none min-h-[650px] leading-relaxed',
    },
  },
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
      handleWidth: 6,
      cellMinWidth: 35,
      lastColumnResizable: false,
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
  document.removeEventListener('pointerdown', handleOutsideClick)
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

function isAlignActive(align: string) {
  if (!editor.value) return false
  if (align === 'left') {
    return editor.value.isActive({ textAlign: 'left' }) || 
      (!editor.value.isActive({ textAlign: 'center' }) && 
       !editor.value.isActive({ textAlign: 'right' }) && 
       !editor.value.isActive({ textAlign: 'justify' }))
  }
  return editor.value.isActive({ textAlign: align })
}

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

// Insert Standard Grid Table
function insertStandardTable(rows = 3, cols = 3) {
  if (!editor.value) return
  showTableMenu.value = false
  editor.value.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run()
}

// Insert Yayasan Standard 4-Column Table
function insertYayasanTable() {
  if (!editor.value) return
  showTableMenu.value = false
  const html = `
    <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
      <tr>
        <th style="width: 45px; text-align: center;"><p><strong>No</strong></p></th>
        <th style="width: 25%;"><p><strong>Perihal / Topik</strong></p></th>
        <th style="width: 45%;"><p><strong>Pembahasan / Arahan Pimpinan</strong></p></th>
        <th style="width: 25%;"><p><strong>Tindak Lanjut & PIC</strong></p></th>
      </tr>
      <tr>
        <td style="text-align: center;"><p>1</p></td>
        <td><p>Topik pembahasan pertama...</p></td>
        <td><p>a. Poin arahan pimpinan...<br>b. Solusi yang disepakati...</p></td>
        <td><p>PIC dan batas waktu...</p></td>
      </tr>
    </table>
    <p></p>
  `
  try {
    const res = editor.value.chain().focus().insertContent(html).run()
    if (!res) {
      editor.value.chain().focus().insertTable({ rows: 2, cols: 4, withHeaderRow: true }).run()
    }
  } catch (e) {
    editor.value.chain().focus().insertTable({ rows: 2, cols: 4, withHeaderRow: true }).run()
  }
}

// Insert Custom Column Table
function insertCustomTable(cols: 2 | 3) {
  if (!editor.value) return
  showTableMenu.value = false
  if (cols === 3) {
    const html = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tr>
          <th style="width: 45px; text-align: center;"><p><strong>No</strong></p></th>
          <th style="width: 35%;"><p><strong>Topik / Masukan Peserta</strong></p></th>
          <th style="width: 60%;"><p><strong>Tanggapan & Kesepakatan Bersama</strong></p></th>
        </tr>
        <tr>
          <td style="text-align: center;"><p>1</p></td>
          <td><p></p></td>
          <td><p></p></td>
        </tr>
      </table>
      <p></p>
    `
    try {
      const res = editor.value.chain().focus().insertContent(html).run()
      if (!res) {
        editor.value.chain().focus().insertTable({ rows: 2, cols: 3, withHeaderRow: true }).run()
      }
    } catch (e) {
      editor.value.chain().focus().insertTable({ rows: 2, cols: 3, withHeaderRow: true }).run()
    }
  } else {
    const html = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tr>
          <th style="width: 45px; text-align: center;"><p><strong>No</strong></p></th>
          <th><p><strong>Poin Pembahasan / Catatan Rapat</strong></p></th>
        </tr>
        <tr>
          <td style="text-align: center;"><p>1</p></td>
          <td><p></p></td>
        </tr>
      </table>
      <p></p>
    `
    try {
      const res = editor.value.chain().focus().insertContent(html).run()
      if (!res) {
        editor.value.chain().focus().insertTable({ rows: 2, cols: 2, withHeaderRow: true }).run()
      }
    } catch (e) {
      editor.value.chain().focus().insertTable({ rows: 2, cols: 2, withHeaderRow: true }).run()
    }
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
          <th style="width: 45px; text-align: center; padding: 8px; border: 1px solid #94a3b8;">No</th>
          <th style="width: 25%; padding: 8px; border: 1px solid #94a3b8; text-align: left;">Perihal / Topik</th>
          <th style="width: 45%; padding: 8px; border: 1px solid #94a3b8; text-align: left;">Pembahasan / Arahan Pimpinan</th>
          <th style="width: 24%; padding: 8px; border: 1px solid #94a3b8; text-align: left;">Tindak Lanjut</th>
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
  insertStandardTable,
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
  border-radius: 0.875rem;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.08);
  padding: 0.35rem 0.65rem;
  margin: 0 auto 0.75rem auto;
  max-width: 860px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
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
  background-color: #cbd5e1;
  margin: 0 0.25rem;
  flex-shrink: 0;
}
:deep(.dark) .gdocs-tb-divider {
  background-color: #475569;
}

/* Toolbar Icon Buttons */
.gdocs-tb-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
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
:deep(.tiptap-content .ProseMirror),
:deep(.tiptap-content .tiptap) {
  outline: none !important;
  min-height: 650px;
}

:deep(.tiptap-content .ProseMirror p.is-editor-empty:first-child::before),
:deep(.tiptap-content .tiptap p.is-editor-empty:first-child::before) {
  color: #94a3b8;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

:deep(.tiptap-content .ProseMirror h1),
:deep(.tiptap-content .tiptap h1) {
  font-size: 1.6rem;
  font-weight: 700;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
  color: #0f172a;
}
:deep(.tiptap-content .ProseMirror h2),
:deep(.tiptap-content .tiptap h2) {
  font-size: 1.3rem;
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #0f172a;
}
:deep(.tiptap-content .ProseMirror h3),
:deep(.tiptap-content .tiptap h3) {
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 0.75rem;
  margin-bottom: 0.35rem;
  color: #1e293b;
}
:deep(.dark) .tiptap-content .ProseMirror h1,
:deep(.dark) .tiptap-content .ProseMirror h2,
:deep(.dark) .tiptap-content .ProseMirror h3,
:deep(.dark) .tiptap-content .tiptap h1,
:deep(.dark) .tiptap-content .tiptap h2,
:deep(.dark) .tiptap-content .tiptap h3 {
  color: #f8fafc;
}

:deep(.tiptap-content .ProseMirror p),
:deep(.tiptap-content .tiptap p) {
  margin: 0.4rem 0;
}

/* Bullet & Numbered lists */
:deep(.tiptap-content ul:not([data-type="taskList"])),
:deep(.tiptap-content .ProseMirror ul:not([data-type="taskList"])),
:deep(.tiptap-content .tiptap ul:not([data-type="taskList"])) {
  list-style-type: disc !important;
  list-style-position: outside !important;
  padding-left: 1.5rem !important;
  margin: 0.5rem 0 !important;
}
:deep(.tiptap-content ol),
:deep(.tiptap-content .ProseMirror ol),
:deep(.tiptap-content .tiptap ol) {
  list-style-type: decimal !important;
  list-style-position: outside !important;
  padding-left: 1.5rem !important;
  margin: 0.5rem 0 !important;
}
:deep(.tiptap-content li),
:deep(.tiptap-content .ProseMirror li),
:deep(.tiptap-content .tiptap li) {
  padding-left: 0.25rem !important;
  margin-bottom: 0.25rem !important;
}

/* Task lists (Checklist) */
:deep(.tiptap-content ul[data-type="taskList"]),
:deep(.tiptap-content .ProseMirror ul[data-type="taskList"]) {
  list-style: none !important;
  padding-left: 0.25rem !important;
  margin: 0.5rem 0 !important;
}
:deep(.tiptap-content ul[data-type="taskList"] li) {
  display: flex !important;
  align-items: flex-start !important;
  gap: 0.5rem !important;
  margin-bottom: 0.35rem !important;
}
:deep(.tiptap-content ul[data-type="taskList"] li > label) {
  flex: 0 0 auto !important;
  user-select: none !important;
  margin-top: 0.2rem !important;
  cursor: pointer !important;
}
:deep(.tiptap-content ul[data-type="taskList"] li > label input[type="checkbox"]) {
  cursor: pointer !important;
  width: 15px !important;
  height: 15px !important;
  accent-color: #2563eb !important;
}
:deep(.tiptap-content ul[data-type="taskList"] li > div) {
  flex: 1 1 auto !important;
}

/* =========================================================================
   TABLE STYLING (FLAWLESS NESTED LISTS & BORDERS)
   ========================================================================= */
:deep(.tiptap-content .tiptap table) {
  width: 100% !important;
  border-collapse: collapse !important;
  margin: 1.25rem 0 !important;
  border: 1px solid #94a3b8 !important;
  overflow: hidden;
}

:deep(.tiptap-content .tiptap table th),
:deep(.tiptap-content .tiptap table td) {
  border: 1px solid #94a3b8 !important;
  padding: 8px 12px !important;
  vertical-align: top !important;
  box-sizing: border-box !important;
  line-height: 1.6 !important;
  min-width: 35px;
  position: relative;
  word-break: break-word;
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
  text-align: center;
  font-weight: 600;
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

:deep(.tiptap-content .tiptap.resize-cursor),
:deep(.tiptap-content .tiptap.resize-cursor *) {
  cursor: col-resize !important;
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
