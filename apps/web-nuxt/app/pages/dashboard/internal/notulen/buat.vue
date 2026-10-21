<template>
  <div class="space-y-6 max-w-5xl mx-auto pb-12">
    <!-- Top Bar -->
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <NuxtLink to="/dashboard/internal/notulen">
          <Button icon="pi pi-arrow-left" severity="secondary" rounded text />
        </NuxtLink>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-bold text-slate-800 dark:text-white">
              {{ isEditing ? 'Edit Notulen Rapat' : 'Tulis Notulen Rapat Baru' }}
            </h1>
            <Tag v-if="isEditing" value="Mode Edit" severity="warn" class="text-xs" />
          </div>
          <p class="text-xs text-slate-500">
            {{ isEditing ? 'Perbarui isi notulensi, agenda pembahasan, dan tindak lanjut tugas.' : 'Catat jalannya rapat resmi, tetapkan kehadiran, dan buat tindak lanjut tugas.' }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button label="Batal" severity="secondary" @click="router.back()" />
        <Button 
          :label="isEditing ? 'Simpan Perubahan' : 'Simpan Draf'" 
          icon="pi pi-save" 
          severity="secondary" 
          :loading="saving" 
          @click="saveMinute(false)" 
        />
        <Button 
          label="Simpan & Ajukan" 
          icon="pi pi-send" 
          severity="primary" 
          :loading="saving" 
          @click="saveMinute(true)" 
        />
      </div>
    </div>

    <!-- Form Body -->
    <div class="space-y-6">
      <!-- 1. Identitas & Cakupan Rapat -->
      <div class="card p-5 space-y-4">
        <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
          <i class="pi pi-info-circle text-primary"></i> 1. Identitas & Cakupan Rapat
        </h2>

        <!-- Cakupan Rapat (Scope) -->
        <div>
          <label class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 block">Tingkat / Cakupan Rapat *</label>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div 
              @click="form.scope = 'unit'"
              class="p-3.5 rounded-xl border cursor-pointer transition-all flex items-start gap-3"
              :class="form.scope === 'unit' ? 'border-primary bg-primary/5 ring-1 ring-primary text-primary' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 text-slate-700 dark:text-slate-300'"
            >
              <i class="pi pi-building text-xl mt-0.5"></i>
              <div>
                <p class="font-bold text-sm">Rapat Tingkat Unit</p>
                <p class="text-xs opacity-75 mt-0.5">Rapat intern RA, SDIT, atau SMPIT (Disahkan oleh Kepala Unit)</p>
              </div>
            </div>

            <div 
              @click="form.scope = 'yayasan_global'"
              class="p-3.5 rounded-xl border cursor-pointer transition-all flex items-start gap-3"
              :class="form.scope === 'yayasan_global' ? 'border-primary bg-primary/5 ring-1 ring-primary text-primary' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 text-slate-700 dark:text-slate-300'"
            >
              <i class="pi pi-globe text-xl mt-0.5"></i>
              <div>
                <p class="font-bold text-sm">Rapat Yayasan / Seluruh Unit</p>
                <p class="text-xs opacity-75 mt-0.5">Rapat Pleno Yayasan / Gabungan Unit (Disahkan oleh Ketua Yayasan)</p>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Pilih Unit jika Scope Unit -->
          <div v-if="form.scope === 'unit'" class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Pilih Unit *</label>
            <Select v-model="form.unit_id" :options="unitOptions" optionLabel="name" optionValue="id" placeholder="Pilih Unit Terkait" class="w-full" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Jenis Pertemuan *</label>
            <Select v-model="form.meeting_type" :options="meetingTypeOptions" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2 flex flex-col gap-1.5">
            <label class="font-medium text-xs">Topik / Judul Rapat *</label>
            <InputText v-model="form.title" placeholder="Contoh: Rapat Koordinasi Kurikulum & Evaluasi KBM Semester Ganjil" class="w-full" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Nomor Notulen (opsional - otomatis jika kosong)</label>
            <InputText v-model="form.nomor_notulen" placeholder="Contoh: NOT/YYS/2026/09/001" class="w-full" />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Tanggal Pelaksanaan *</label>
            <InputText v-model="form.meeting_date" type="date" class="w-full" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Waktu Mulai & Selesai</label>
            <div class="flex items-center gap-2">
              <InputText v-model="form.start_time" placeholder="08:30" class="w-full" />
              <span class="text-slate-400 text-xs">s/d</span>
              <InputText v-model="form.end_time" placeholder="11:30" class="w-full" />
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Lokasi / Tempat</label>
            <InputText v-model="form.location" placeholder="Ruang Rapat Utama / Zoom" class="w-full" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs flex items-center justify-between">
              <span>Notulis Rapat *</span>
              <span class="text-[10px] text-slate-400 font-normal">Default: Akun Login</span>
            </label>
            <Select 
              v-model="form.notulis_id" 
              :options="userOptions" 
              optionLabel="label" 
              optionValue="id" 
              placeholder="Pilih notulis rapat..." 
              filter 
              class="w-full"
            />
          </div>
        </div>
      </div>

      <!-- 2. Kehadiran & Peserta Rapat -->
      <div class="card p-5 space-y-4">
        <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
          <i class="pi pi-users text-primary"></i> 2. Kehadiran & Peserta Rapat
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs text-emerald-700 dark:text-emerald-400">
              <i class="pi pi-check text-[10px]"></i> Peserta Hadir ({{ form.attendees.length }})
            </label>
            <MultiSelect 
              v-model="form.attendees" 
              :options="userOptions" 
              optionLabel="label" 
              optionValue="id" 
              placeholder="Pilih peserta yang hadir..." 
              filter 
              display="chip"
              class="w-full"
            />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs text-rose-700 dark:text-rose-400">
              <i class="pi pi-times text-[10px]"></i> Peserta Berhalangan / Izin ({{ form.absent_members.length }})
            </label>
            <MultiSelect 
              v-model="form.absent_members" 
              :options="userOptions" 
              optionLabel="label" 
              optionValue="id" 
              placeholder="Pilih yang berhalangan..." 
              filter 
              display="chip"
              class="w-full"
            />
          </div>
        </div>
      </div>

      <!-- 3. Agenda Pembahasan -->
      <div class="card p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
            <i class="pi pi-list text-primary"></i> 3. Agenda Pembahasan
          </h2>
          <Button label="Tambah Poin Agenda" icon="pi pi-plus" size="small" severity="secondary" @click="addAgendaItem" />
        </div>

        <div class="space-y-2">
          <div v-for="(ag, idx) in form.agenda" :key="idx" class="flex items-center gap-2">
            <span class="w-6 text-xs text-slate-400 font-bold text-right">{{ idx + 1 }}.</span>
            <InputText v-model="form.agenda[idx]" placeholder="Ketik poin agenda pembahasan..." class="flex-1" />
            <button v-if="form.agenda.length > 1" @click="removeAgendaItem(idx)" class="p-2 text-slate-400 hover:text-red-500">
              <i class="pi pi-times"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 4. Jalannya Rapat & Notulensi -->
      <div class="card p-5 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
              <i class="pi pi-file-edit text-primary"></i> 4. Catatan Pembahasan / Isi Notulensi *
            </h2>
            <p class="text-xs text-slate-500 mt-0.5">
              Catat jalannya rapat secara terstruktur. Gunakan <b>Mode Spreadsheet</b> agar nyaman seperti Excel/Google Sheets, atau <b>Mode Bebas</b> layaknya Word/Docs.
            </p>
          </div>

          <!-- Mode Switcher (Spreadsheet vs Word/Docs) -->
          <div class="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 text-xs font-semibold">
            <button 
              type="button"
              @click="switchEditorMode('table')"
              :class="editorMode === 'table' ? 'bg-white dark:bg-slate-700 shadow text-primary font-bold' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'"
              class="px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all"
            >
              <i class="pi pi-table"></i>
              <span>Mode Tabel Spreadsheet</span>
              <span class="text-[10px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-bold">Rekomendasi</span>
            </button>
            <button 
              type="button"
              @click="switchEditorMode('doc')"
              :class="editorMode === 'doc' ? 'bg-white dark:bg-slate-700 shadow text-primary font-bold' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'"
              class="px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all"
            >
              <i class="pi pi-file-word"></i>
              <span>Mode Dokumen Bebas (Word)</span>
            </button>
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- MODE 1: SPREADSHEET / TABLE GRID (EXCEL / SHEETS STYLE)  -->
        <!-- ======================================================== -->
        <div v-show="editorMode === 'table'" class="space-y-4">
          <!-- Top Controls: Format Selector & Quick Actions -->
          <div class="flex flex-wrap items-center justify-between gap-2.5 bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-200 dark:border-slate-700">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-xs font-bold text-slate-700 dark:text-slate-300">Format Kolom Tabel:</span>
              <div class="inline-flex rounded-lg border border-slate-300 dark:border-slate-600 p-0.5 bg-white dark:bg-slate-800 text-xs shadow-sm">
                <button
                  type="button"
                  @click="changeTableColumnsMode('4_col')"
                  :class="tableColumnsMode === '4_col' ? 'bg-primary text-white font-bold shadow-sm' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'"
                  class="px-3 py-1 rounded-md transition-colors"
                >
                  4 Kolom (Resmi Yayasan: No, Perihal, Pembahasan/Arahan, Tindak Lanjut)
                </button>
                <button
                  type="button"
                  @click="changeTableColumnsMode('3_col')"
                  :class="tableColumnsMode === '3_col' ? 'bg-primary text-white font-bold shadow-sm' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'"
                  class="px-3 py-1 rounded-md transition-colors"
                >
                  3 Kolom (No, Topik/Masukan, Tanggapan & Kesepakatan)
                </button>
                <button
                  type="button"
                  @click="changeTableColumnsMode('2_col')"
                  :class="tableColumnsMode === '2_col' ? 'bg-primary text-white font-bold shadow-sm' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'"
                  class="px-3 py-1 rounded-md transition-colors"
                >
                  2 Kolom (Sederhana)
                </button>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <Button
                type="button"
                label="+ Tambah Baris"
                icon="pi pi-plus"
                size="small"
                severity="success"
                class="!text-xs font-bold !py-1.5"
                @click="addStructuredRow"
              />
            </div>
          </div>

          <!-- Opening Remarks (Optional) -->
          <div class="space-y-1">
            <div class="flex items-center justify-between">
              <label class="text-xs font-semibold text-slate-600 dark:text-slate-300 flex items-center gap-1.5">
                <i class="pi pi-align-left text-primary text-xs"></i> Paragraf Pengantar / Pembukaan Rapat (Opsional)
              </label>
              <button 
                type="button"
                @click="showOpeningText = !showOpeningText" 
                class="text-[11px] text-primary hover:underline font-semibold"
              >
                {{ showOpeningText ? 'Sembunyikan' : '+ Tulis Pengantar Rapat' }}
              </button>
            </div>
            <Textarea
              v-if="showOpeningText"
              v-model="tableOpeningText"
              rows="2"
              placeholder="Contoh: Rapat dibuka secara resmi pada pukul 08:30 WIB dengan membaca Basmalah dan arahan singkat pimpinan terkait fokus pertemuan hari ini..."
              class="w-full text-xs font-sans rounded-lg"
              @input="syncStructuredTableToHtml"
            />
          </div>

          <!-- Spreadsheet Table Grid -->
          <div class="border border-slate-300 dark:border-slate-700 rounded-xl overflow-hidden shadow-sm bg-white dark:bg-slate-900">
            <div class="overflow-x-auto">
              <table class="w-full border-collapse text-xs table-fixed">
                <thead>
                  <tr class="bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border-b-2 border-slate-300 dark:border-slate-700 font-bold">
                    <th class="w-12 py-3 px-2 text-center border-r border-slate-300 dark:border-slate-700">No.</th>
                    
                    <!-- 4 Kolom Headers -->
                    <th v-if="tableColumnsMode === '4_col'" class="w-[22%] py-3 px-3 text-left border-r border-slate-300 dark:border-slate-700">
                      Perihal / Topik
                    </th>
                    <th v-if="tableColumnsMode === '4_col'" class="w-[45%] py-3 px-3 text-left border-r border-slate-300 dark:border-slate-700">
                      Pembahasan / Arahan Pimpinan
                    </th>
                    <th v-if="tableColumnsMode === '4_col'" class="w-[28%] py-3 px-3 text-left border-r border-slate-300 dark:border-slate-700">
                      Tindak Lanjut / Kesepakatan
                    </th>

                    <!-- 3 Kolom Headers -->
                    <th v-if="tableColumnsMode === '3_col'" class="w-[28%] py-3 px-3 text-left border-r border-slate-300 dark:border-slate-700">
                      Topik / Masukan Peserta
                    </th>
                    <th v-if="tableColumnsMode === '3_col'" class="py-3 px-3 text-left border-r border-slate-300 dark:border-slate-700">
                      Tanggapan & Kesepakatan Bersama
                    </th>

                    <!-- 2 Kolom Headers -->
                    <th v-if="tableColumnsMode === '2_col'" class="py-3 px-3 text-left border-r border-slate-300 dark:border-slate-700">
                      Poin Pembahasan / Catatan Rapat
                    </th>
                    <th class="w-12 py-3 px-2 text-center">Aksi</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 dark:divide-slate-800">
                  <tr 
                    v-for="(row, idx) in tableRows" 
                    :key="row.id" 
                    class="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    <!-- Col 0: Number -->
                    <td class="text-center font-bold text-slate-600 dark:text-slate-400 py-3 px-2 border-r border-slate-200 dark:border-slate-800 align-top">
                      <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 font-bold text-xs text-slate-700 dark:text-slate-300">
                        {{ idx + 1 }}
                      </span>
                    </td>

                    <!-- Col 1: Perihal / Topik -->
                    <td class="p-2 border-r border-slate-200 dark:border-slate-800 align-top">
                      <Textarea
                        v-model="row.col1"
                        :autoResize="true"
                        rows="3"
                        placeholder="Contoh: SPMB T.A 2027/2028..."
                        class="w-full text-xs !border-slate-200 dark:!border-slate-700 focus:!border-primary rounded-lg font-sans leading-relaxed"
                        @keydown="handleTextareaKeyDown($event, row, 'col1', idx)"
                        @input="syncStructuredTableToHtml"
                      />
                    </td>

                    <!-- Col 2: Pembahasan / Tanggapan (Mendukung a, b, c, Enter) -->
                    <td v-if="['4_col', '3_col'].includes(tableColumnsMode)" class="p-2 border-r border-slate-200 dark:border-slate-800 align-top">
                      <div class="space-y-1.5">
                        <div class="flex items-center justify-between text-[11px] text-slate-400 bg-slate-50 dark:bg-slate-800/80 px-2 py-1 rounded border border-slate-200/60 dark:border-slate-700/60">
                          <span class="font-semibold text-slate-500 dark:text-slate-400">Sisipkan Poin:</span>
                          <div class="flex items-center gap-1">
                            <button 
                              type="button" 
                              @click="insertListMarker(row, 'col2', 'alpha')"
                              class="px-1.5 py-0.5 font-bold bg-white dark:bg-slate-700 hover:bg-primary hover:text-white dark:hover:bg-primary rounded text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 transition-colors shadow-2xs"
                              title="Sisipkan poin huruf (a., b., c.)"
                            >
                              + a, b, c
                            </button>
                            <button 
                              type="button" 
                              @click="insertListMarker(row, 'col2', 'num')"
                              class="px-1.5 py-0.5 font-bold bg-white dark:bg-slate-700 hover:bg-primary hover:text-white dark:hover:bg-primary rounded text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 transition-colors shadow-2xs"
                              title="Sisipkan nomor (1., 2., 3.)"
                            >
                              + 1, 2, 3
                            </button>
                            <button 
                              type="button" 
                              @click="insertListMarker(row, 'col2', 'bullet')"
                              class="px-1.5 py-0.5 font-bold bg-white dark:bg-slate-700 hover:bg-primary hover:text-white dark:hover:bg-primary rounded text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 transition-colors shadow-2xs"
                              title="Sisipkan poin bullet (•)"
                            >
                              + Bullet (•)
                            </button>
                          </div>
                        </div>
                        <Textarea
                          v-model="row.col2"
                          :autoResize="true"
                          rows="4"
                          :placeholder="tableColumnsMode === '4_col' ? 'a. Jadwal pelaksanaan...\nb. Pembentukan Panitia...\n(Tekan Enter untuk baris baru otomatis poin huruf)' : 'a. Aspirasi yang disampaikan...\nb. Tanggapan yang disepakati...'"
                          class="w-full text-xs !border-slate-200 dark:!border-slate-700 focus:!border-primary rounded-lg font-sans leading-relaxed"
                          @keydown="handleTextareaKeyDown($event, row, 'col2', idx)"
                          @input="syncStructuredTableToHtml"
                        />
                      </div>
                    </td>

                    <!-- Col 3: Tindak Lanjut (Khusus 4 Kolom) -->
                    <td v-if="tableColumnsMode === '4_col'" class="p-2 border-r border-slate-200 dark:border-slate-800 align-top">
                      <div class="space-y-1.5">
                        <div class="flex items-center justify-between text-[11px] text-slate-400 bg-slate-50 dark:bg-slate-800/80 px-2 py-1 rounded border border-slate-200/60 dark:border-slate-700/60">
                          <span class="font-semibold text-slate-500 dark:text-slate-400">Sisipkan Poin:</span>
                          <div class="flex items-center gap-1">
                            <button 
                              type="button" 
                              @click="insertListMarker(row, 'col3', 'alpha')"
                              class="px-1.5 py-0.5 font-bold bg-white dark:bg-slate-700 hover:bg-primary hover:text-white dark:hover:bg-primary rounded text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 transition-colors shadow-2xs"
                              title="Sisipkan poin huruf (a., b., c.)"
                            >
                              + a, b, c
                            </button>
                            <button 
                              type="button" 
                              @click="insertListMarker(row, 'col3', 'num')"
                              class="px-1.5 py-0.5 font-bold bg-white dark:bg-slate-700 hover:bg-primary hover:text-white dark:hover:bg-primary rounded text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 transition-colors shadow-2xs"
                              title="Sisipkan nomor (1., 2., 3.)"
                            >
                              + 1, 2, 3
                            </button>
                            <button 
                              type="button" 
                              @click="insertListMarker(row, 'col3', 'bullet')"
                              class="px-1.5 py-0.5 font-bold bg-white dark:bg-slate-700 hover:bg-primary hover:text-white dark:hover:bg-primary rounded text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 transition-colors shadow-2xs"
                              title="Sisipkan poin bullet (•)"
                            >
                              + Bullet (•)
                            </button>
                          </div>
                        </div>
                        <Textarea
                          v-model="row.col3"
                          :autoResize="true"
                          rows="4"
                          placeholder="a. Melakukan evaluasi teknis...\nb. Jadwal pelaksanaan...\n(Tekan Tab di ujung untuk tambah baris)"
                          class="w-full text-xs !border-slate-200 dark:!border-slate-700 focus:!border-primary rounded-lg font-sans leading-relaxed"
                          @keydown="handleTextareaKeyDown($event, row, 'col3', idx)"
                          @input="syncStructuredTableToHtml"
                        />
                      </div>
                    </td>

                    <!-- Col Action: Delete -->
                    <td class="text-center py-3 px-1 align-top">
                      <Button
                        icon="pi pi-trash"
                        text
                        rounded
                        severity="danger"
                        size="small"
                        :disabled="tableRows.length <= 1"
                        @click="removeStructuredRow(idx)"
                        title="Hapus baris ini"
                      />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Table Footer: Add Row button & tips -->
            <div class="p-3 bg-slate-50 dark:bg-slate-800/60 border-t border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <Button
                type="button"
                label="Tambah Baris Baru (+ Row)"
                icon="pi pi-plus"
                size="small"
                outlined
                severity="success"
                class="!text-xs font-bold"
                @click="addStructuredRow"
              />
              <span class="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <i class="pi pi-info-circle text-primary text-xs"></i>
                <span>Tekan <b>Enter</b> di dalam kolom untuk baris baru (otomatis lanjut a, b, c). Tekan <b>Tab</b> di kolom terakhir untuk menambah baris otomatis.</span>
              </span>
            </div>
          </div>

          <!-- Closing Remarks (Optional) -->
          <div class="space-y-1">
            <div class="flex items-center justify-between">
              <label class="text-xs font-semibold text-slate-600 dark:text-slate-300 flex items-center gap-1.5">
                <i class="pi pi-align-left text-primary text-xs"></i> Catatan Penutup / Rekomendasi Khusus (Opsional)
              </label>
              <button 
                type="button" 
                @click="showClosingText = !showClosingText" 
                class="text-[11px] text-primary hover:underline font-semibold"
              >
                {{ showClosingText ? 'Sembunyikan' : '+ Tulis Catatan Penutup' }}
              </button>
            </div>
            <Textarea
              v-if="showClosingText"
              v-model="tableClosingText"
              rows="2"
              placeholder="Contoh: Rapat ditutup pada pukul 11:00 WIB dengan membaca Hamdalah dan doa bersama. Seluruh pihak terkait diharapkan menyelesaikan tindak lanjut sebelum batas waktu..."
              class="w-full text-xs font-sans rounded-lg"
              @input="syncStructuredTableToHtml"
            />
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- MODE 2: FREE-FORM RICH TEXT (WORD / GOOGLE DOCS STYLE)   -->
        <!-- ======================================================== -->
        <div v-show="editorMode === 'doc'" class="space-y-3">
          <!-- Quick Template & Table Action Buttons for Word Mode -->
          <div class="flex items-center gap-1.5 flex-wrap">
            <div class="flex items-center bg-slate-100 dark:bg-slate-800 rounded-lg p-0.5 border border-slate-200 dark:border-slate-700">
              <Button 
                type="button" 
                label="+ Tabel 4 Kolom" 
                icon="pi pi-table" 
                size="small" 
                text 
                class="!text-xs !py-1 !px-2.5 font-semibold text-slate-700 dark:text-slate-200 hover:!bg-white dark:hover:!bg-slate-700"
                @click="insertTable(4)" 
                title="Sisipkan tabel 4 kolom (No, Perihal, Pembahasan, Tindak Lanjut)"
              />
              <Button 
                type="button" 
                label="+ Tabel 3 Kolom" 
                icon="pi pi-table" 
                size="small" 
                text 
                class="!text-xs !py-1 !px-2.5 font-semibold text-slate-700 dark:text-slate-200 hover:!bg-white dark:hover:!bg-slate-700"
                @click="insertTable(3)" 
                title="Sisipkan tabel 3 kolom (No, Masukan, Kesepakatan)"
              />
              <Button 
                type="button" 
                label="+ Tabel 2 Kolom" 
                icon="pi pi-table" 
                size="small" 
                text 
                class="!text-xs !py-1 !px-2.5 font-semibold text-slate-700 dark:text-slate-200 hover:!bg-white dark:hover:!bg-slate-700"
                @click="insertTable(2)" 
                title="Sisipkan tabel 2 kolom (No, Pembahasan)"
              />
            </div>

            <div class="flex items-center bg-emerald-50 dark:bg-emerald-950/40 rounded-lg p-0.5 border border-emerald-200 dark:border-emerald-800">
              <Button 
                type="button" 
                label="+ Tambah Baris" 
                icon="pi pi-plus" 
                size="small" 
                severity="success" 
                text 
                class="!text-xs !py-1 !px-2.5 font-bold"
                @click="addTableRow" 
                title="Tambahkan baris baru ke tabel (atau tekan tombol Tab pada kolom terakhir)"
              />
              <Button 
                type="button" 
                label="- Hapus Baris" 
                icon="pi pi-minus" 
                size="small" 
                severity="danger" 
                text 
                class="!text-xs !py-1 !px-2.5"
                @click="deleteTableRow" 
                title="Hapus baris terakhir tabel"
              />
              <Button 
                type="button" 
                label="Gabung Tabel" 
                icon="pi pi-link" 
                size="small" 
                severity="help" 
                text 
                class="!text-xs !py-1 !px-2.5 font-medium"
                @click="mergeTables" 
                title="Gabungkan 2 tabel terpisah menjadi 1 tabel bersambung"
              />
            </div>

            <Button 
              type="button" 
              label="Template Notulen" 
              icon="pi pi-file" 
              size="small" 
              outlined 
              severity="info" 
              class="!text-xs !py-1 font-semibold"
              @click="insertNotulenTemplate" 
              title="Gunakan template format notulensi terstruktur"
            />
          </div>

          <p class="text-[11px] text-slate-500 flex items-center gap-1.5 px-0.5">
            <i class="pi pi-info-circle text-primary text-xs"></i>
            <span>Tekan <b>Enter</b> di dalam sel untuk membuat baris baru. Tekan <b>Tab</b> di keyboard untuk berpindah ke kolom sebelah atau otomatis menambah baris di ujung tabel.</span>
          </p>

          <!-- PrimeVue Rich Text Editor with Custom Toolbar -->
          <div class="rich-editor-wrapper">
            <Editor 
              ref="editorRef"
              v-model="form.content" 
              :modules="editorModules"
              @load="onEditorLoad"
              editorStyle="min-height: 280px" 
              placeholder="Tuliskan catatan pembahasan rapat, aspirasi, dan tanggapan peserta di sini...">
              <template #toolbar>
                <span class="ql-formats">
                  <select class="ql-header" title="Format Judul / Paragraf">
                    <option value="1">Judul Utama (H1)</option>
                    <option value="2">Sub Judul (H2)</option>
                    <option value="3">Poin Bahasan (H3)</option>
                    <option selected>Teks Normal</option>
                  </select>
                </span>
                <span class="ql-formats">
                  <button class="ql-bold" type="button" title="Tebal (Bold)"></button>
                  <button class="ql-italic" type="button" title="Miring (Italic)"></button>
                  <button class="ql-underline" type="button" title="Garis Bawah (Underline)"></button>
                  <button class="ql-strike" type="button" title="Coret (Strikethrough)"></button>
                </span>
                <span class="ql-formats">
                  <select class="ql-color" title="Warna Teks"></select>
                  <select class="ql-background" title="Warna Latar / Sorotan"></select>
                </span>
                <span class="ql-formats">
                  <button class="ql-list" value="ordered" type="button" title="Penomoran (1, 2, 3)"></button>
                  <button class="ql-list" value="bullet" type="button" title="Daftar Poin (Bullets)"></button>
                  <button class="ql-list" value="check" type="button" title="Daftar Centang (Checklist)"></button>
                  <button class="ql-indent" value="-1" type="button" title="Geser Kiri (Outdent)"></button>
                  <button class="ql-indent" value="+1" type="button" title="Geser Kanan (Indent)"></button>
                </span>
                <span class="ql-formats">
                  <select class="ql-align" title="Perataan Paragraf"></select>
                </span>
                <span class="ql-formats">
                  <button class="ql-blockquote" type="button" title="Kutipan"></button>
                  <button class="ql-code-block" type="button" title="Blok Kode / Format Rapat"></button>
                  <button class="ql-link" type="button" title="Sisipkan Link"></button>
                </span>
                <span class="ql-formats">
                  <button class="ql-clean" type="button" title="Bersihkan Format"></button>
                </span>
              </template>
            </Editor>
          </div>
        </div>
      </div>

      <!-- 5. Keputusan & Kesimpulan -->
      <div class="card p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
            <i class="pi pi-check-circle text-primary"></i> 5. Keputusan & Kesimpulan Rapat
          </h2>
          <Button label="Tambah Keputusan" icon="pi pi-plus" size="small" severity="secondary" @click="addDecisionItem" />
        </div>

        <div class="space-y-2">
          <div v-for="(dec, idx) in form.decisions" :key="idx" class="flex items-center gap-2">
            <span class="w-6 text-xs text-slate-400 font-bold text-right">{{ idx + 1 }}.</span>
            <InputText v-model="form.decisions[idx]" placeholder="Ketik butir keputusan yang disepakati..." class="flex-1" />
            <button v-if="form.decisions.length > 1" @click="removeDecisionItem(idx)" class="p-2 text-slate-400 hover:text-red-500">
              <i class="pi pi-times"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 6. Tindak Lanjut (Action Items) -->
      <div class="card p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
              <i class="pi pi-th-large text-primary"></i> 6. Tindak Lanjut / Action Items (Tugas)
            </h2>
            <p class="text-xs text-slate-500">Tugaskan PIC dan tenggat waktu agar hasil rapat langsung tereksekusi.</p>
          </div>
          <Button label="Tambah Tugas" icon="pi pi-plus" size="small" severity="secondary" @click="addActionItem" />
        </div>

        <div v-if="form.action_items.length === 0" class="text-center py-4 text-xs text-slate-400">
          Belum ada tugas tindak lanjut. Klik "Tambah Tugas" untuk menugaskan PIC.
        </div>

        <div v-else class="space-y-3">
          <div v-for="(item, idx) in form.action_items" :key="idx" class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-primary">Tugas #{{ idx + 1 }}</span>
              <button @click="removeActionItem(idx)" class="text-xs text-red-500 hover:text-red-700">
                <i class="pi pi-trash mr-1"></i> Hapus
              </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div class="md:col-span-2">
                <InputText v-model="item.task_description" placeholder="Deskripsi tugas yang harus dikerjakan..." class="w-full text-xs" />
              </div>
              <div>
                <Select v-model="item.pic_user_id" :options="userOptions" optionLabel="label" optionValue="id" placeholder="Pilih PIC Pegawai" class="w-full text-xs" filter />
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="flex items-center gap-2">
                <span class="text-xs text-slate-500 shrink-0">Batas Waktu:</span>
                <InputText v-model="item.deadline" type="date" class="w-full text-xs" />
              </div>
              <div>
                <InputText v-model="item.notes" placeholder="Catatan tambahan (opsional)..." class="w-full text-xs" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 7. Berkas / Lampiran -->
      <div class="card p-5 space-y-3">
        <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
          <i class="pi pi-paperclip text-primary"></i> 7. Berkas Lampiran & Link Drive (opsional)
        </h2>
        
        <div class="space-y-2">
          <label class="text-xs font-medium">Link Google Drive Dokumentasi / Materi Rapat</label>
          <div class="relative">
            <i class="pi pi-link absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"></i>
            <InputText v-model="gdriveUrl" placeholder="https://drive.google.com/..." class="w-full !pl-9 text-xs" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'dashboard' })

const router = useRouter()
const route = useRoute()
const toast = useToast()
const api = useApi()
const authStore = useAuthStore()

const editId = computed(() => {
  const q = route.query.id
  return q ? Number(q) : null
})
const isEditing = computed(() => !!editId.value)

const saving = ref(false)
const gdriveUrl = ref('')

const form = reactive({
  scope: 'unit',
  unit_id: null as number | null,
  meeting_type: 'rapat_unit',
  title: '',
  nomor_notulen: '',
  meeting_date: new Date().toISOString().substring(0, 10),
  start_time: '08:30',
  end_time: '11:00',
  location: 'Ruang Rapat Utama',
  notulis_id: authStore.user?.id || (null as number | null),
  attendees: [] as number[],
  absent_members: [] as number[],
  agenda: ['Pembahasan Utama'] as string[],
  content: '',
  decisions: ['Disepakati tindak lanjut bersama'] as string[],
  action_items: [] as any[],
})

const unitOptions = [
  { id: 1, name: 'Yayasan Asy-Syuuraa', code: 'YYS' },
  { id: 2, name: 'RA Asy-Syuuraa', code: 'RA' },
  { id: 3, name: 'SDIT Asy-Syuuraa', code: 'SDIT' },
  { id: 4, name: 'SMPIT Asy-Syuuraa', code: 'SMPIT' },
]

const meetingTypeOptions = [
  { label: 'Rapat Unit', value: 'rapat_unit' },
  { label: 'Rapat Pleno Yayasan', value: 'rapat_yayasan' },
  { label: 'Rapat Dewan Guru', value: 'rapat_guru' },
  { label: 'Rapat Koordinasi', value: 'rapat_koordinasi' },
  { label: 'Lainnya', value: 'lainnya' },
]

const users = ref<any[]>([])
const userOptions = computed(() => {
  return users.value.map(u => {
    const roleName = u.role?.name || u.role_name || (u.is_teacher ? 'Guru' : 'Pegawai / Staff')
    return {
      id: u.id,
      label: `${u.full_name} (${roleName}${u.nik ? ' • ' + u.nik : ''})`,
      full_name: u.full_name,
      role_name: roleName,
      nik: u.nik
    }
  })
})

function addAgendaItem() {
  form.agenda.push('')
}
function removeAgendaItem(idx: number) {
  form.agenda.splice(idx, 1)
}

function addDecisionItem() {
  form.decisions.push('')
}
function removeDecisionItem(idx: number) {
  form.decisions.splice(idx, 1)
}

function addActionItem() {
  form.action_items.push({
    task_description: '',
    pic_user_id: null,
    deadline: '',
    notes: '',
  })
}
function removeActionItem(idx: number) {
  form.action_items.splice(idx, 1)
}

// =========================================================================
// DUAL-MODE NOTULEN EDITOR STATE (SPREADSHEET MODE & WORD/DOCS MODE)
// =========================================================================
const editorMode = ref<'table' | 'doc'>('table')
const tableColumnsMode = ref<'4_col' | '3_col' | '2_col'>('4_col')
const showOpeningText = ref(false)
const showClosingText = ref(false)
const tableOpeningText = ref('')
const tableClosingText = ref('')

interface NotulenTableRow {
  id: string
  col1: string
  col2?: string
  col3?: string
}

const tableRows = ref<NotulenTableRow[]>([
  { id: 'row_1', col1: '', col2: '', col3: '' },
  { id: 'row_2', col1: '', col2: '', col3: '' }
])

function changeTableColumnsMode(mode: '4_col' | '3_col' | '2_col') {
  tableColumnsMode.value = mode
  syncStructuredTableToHtml()
}

function addStructuredRow() {
  tableRows.value.push({
    id: 'row_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6),
    col1: '',
    col2: '',
    col3: ''
  })
  syncStructuredTableToHtml()
}

function removeStructuredRow(idx: number) {
  if (tableRows.value.length <= 1) return
  tableRows.value.splice(idx, 1)
  syncStructuredTableToHtml()
}

// Helper: Insert list markers (+ a,b,c | + 1,2,3 | + Bullet)
function insertListMarker(row: NotulenTableRow, colKey: 'col1' | 'col2' | 'col3', type: 'alpha' | 'num' | 'bullet') {
  const current = (row[colKey] || '').trimEnd()
  let marker = ''

  if (type === 'alpha') {
    const matches = Array.from(current.matchAll(/([a-z])\.\s/gi))
    if (matches.length > 0) {
      const lastChar = matches[matches.length - 1][1].toLowerCase()
      const nextChar = String.fromCharCode(lastChar.charCodeAt(0) + 1)
      marker = `${nextChar}. `
    } else {
      marker = 'a. '
    }
  } else if (type === 'num') {
    const matches = Array.from(current.matchAll(/(\d+)\.\s/g))
    if (matches.length > 0) {
      const lastNum = parseInt(matches[matches.length - 1][1], 10)
      marker = `${lastNum + 1}. `
    } else {
      marker = '1. '
    }
  } else if (type === 'bullet') {
    marker = '• '
  }

  if (!current) {
    row[colKey] = marker
  } else {
    row[colKey] = current + '\n' + marker
  }
  syncStructuredTableToHtml()
}

// Helper: Spreadsheet Textarea Keyboard navigation (Enter auto-increments a,b,c or 1,2,3 or •)
function handleTextareaKeyDown(e: KeyboardEvent, row: NotulenTableRow, colKey: 'col1' | 'col2' | 'col3', idx: number) {
  const target = e.target as HTMLTextAreaElement | null
  if (!target) return

  // Handle Tab navigation on last cell of last row -> auto append new row
  if (e.key === 'Tab' && !e.shiftKey) {
    const isLastCol = (tableColumnsMode.value === '4_col' && colKey === 'col3') ||
                      (tableColumnsMode.value === '3_col' && colKey === 'col2') ||
                      (tableColumnsMode.value === '2_col' && colKey === 'col1')
    if (isLastCol && idx === tableRows.value.length - 1) {
      e.preventDefault()
      addStructuredRow()
      return
    }
  }

  // Handle Enter key for auto bullet / numbering continuation
  if (e.key === 'Enter' && !e.shiftKey) {
    const val = target.value
    const start = target.selectionStart
    const beforeCursor = val.substring(0, start)
    const afterCursor = val.substring(target.selectionEnd)

    const lastNewlineIdx = beforeCursor.lastIndexOf('\n')
    const currentLine = lastNewlineIdx === -1 ? beforeCursor : beforeCursor.substring(lastNewlineIdx + 1)

    // 1. Check letter pattern: e.g. "a. ", "b. ", "a) "
    const alphaMatch = currentLine.match(/^([a-z])([.)])\s(.*)$/i)
    if (alphaMatch) {
      e.preventDefault()
      const char = alphaMatch[1]
      const sep = alphaMatch[2]
      const content = alphaMatch[3]

      if (!content.trim()) {
        // Empty bullet line -> clear list marker (exit list mode)
        const newBefore = lastNewlineIdx === -1 ? '' : beforeCursor.substring(0, lastNewlineIdx + 1)
        row[colKey] = newBefore + afterCursor
        syncStructuredTableToHtml()
        nextTick(() => {
          target.selectionStart = target.selectionEnd = newBefore.length
        })
        return
      }

      const nextChar = String.fromCharCode(char.charCodeAt(0) + 1)
      const insertion = `\n${nextChar}${sep} `
      row[colKey] = beforeCursor + insertion + afterCursor
      syncStructuredTableToHtml()
      nextTick(() => {
        target.selectionStart = target.selectionEnd = start + insertion.length
      })
      return
    }

    // 2. Check number pattern: e.g. "1. ", "2. ", "1) "
    const numMatch = currentLine.match(/^(\d+)([.)])\s(.*)$/)
    if (numMatch) {
      e.preventDefault()
      const num = parseInt(numMatch[1], 10)
      const sep = numMatch[2]
      const content = numMatch[3]

      if (!content.trim()) {
        const newBefore = lastNewlineIdx === -1 ? '' : beforeCursor.substring(0, lastNewlineIdx + 1)
        row[colKey] = newBefore + afterCursor
        syncStructuredTableToHtml()
        nextTick(() => {
          target.selectionStart = target.selectionEnd = newBefore.length
        })
        return
      }

      const nextNum = num + 1
      const insertion = `\n${nextNum}${sep} `
      row[colKey] = beforeCursor + insertion + afterCursor
      syncStructuredTableToHtml()
      nextTick(() => {
        target.selectionStart = target.selectionEnd = start + insertion.length
      })
      return
    }

    // 3. Check bullet pattern: e.g. "• ", "- ", "* "
    const bulletMatch = currentLine.match(/^([•\-\*])\s(.*)$/)
    if (bulletMatch) {
      e.preventDefault()
      const bullet = bulletMatch[1]
      const content = bulletMatch[2]

      if (!content.trim()) {
        const newBefore = lastNewlineIdx === -1 ? '' : beforeCursor.substring(0, lastNewlineIdx + 1)
        row[colKey] = newBefore + afterCursor
        syncStructuredTableToHtml()
        nextTick(() => {
          target.selectionStart = target.selectionEnd = newBefore.length
        })
        return
      }

      const insertion = `\n${bullet} `
      row[colKey] = beforeCursor + insertion + afterCursor
      syncStructuredTableToHtml()
      nextTick(() => {
        target.selectionStart = target.selectionEnd = start + insertion.length
      })
      return
    }
  }
}

function escapeHtml(text: string): string {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function formatCellTextToHtml(text: string): string {
  if (!text) return ''
  return text
    .split('\n')
    .map(line => escapeHtml(line))
    .join('<br/>')
}

// Generate valid, clean HTML from structured spreadsheet table
function generateHtmlFromTableRows(): string {
  let html = ''

  if (tableOpeningText.value && tableOpeningText.value.trim()) {
    const pLines = tableOpeningText.value.trim().split('\n').map(l => `<p>${escapeHtml(l)}</p>`).join('')
    html += pLines + '<p><br></p>'
  }

  if (tableColumnsMode.value === '4_col') {
    html += `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 35px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="width: 22%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Perihal / Topik</b></td>
            <td style="width: 48%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Pembahasan / Arahan Pimpinan</b></td>
            <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Tindak Lanjut</b></td>
          </tr>
    `
    tableRows.value.forEach((r, idx) => {
      const col1Html = formatCellTextToHtml(r.col1 || '')
      const col2Html = formatCellTextToHtml(r.col2 || '')
      const col3Html = formatCellTextToHtml(r.col3 || '')
      html += `
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">${idx + 1}</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">${col1Html}</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">${col2Html}</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">${col3Html}</td>
          </tr>
      `
    })
    html += `</tbody></table><p><br></p>`
  } else if (tableColumnsMode.value === '3_col') {
    html += `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 35px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="width: 30%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Topik / Masukan Peserta</b></td>
            <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Tanggapan & Kesepakatan Bersama</b></td>
          </tr>
    `
    tableRows.value.forEach((r, idx) => {
      const col1Html = formatCellTextToHtml(r.col1 || '')
      const col2Html = formatCellTextToHtml(r.col2 || '')
      html += `
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">${idx + 1}</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">${col1Html}</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">${col2Html}</td>
          </tr>
      `
    })
    html += `</tbody></table><p><br></p>`
  } else {
    html += `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 40px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Poin Pembahasan / Catatan Rapat</b></td>
          </tr>
    `
    tableRows.value.forEach((r, idx) => {
      const col1Html = formatCellTextToHtml(r.col1 || '')
      html += `
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">${idx + 1}</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">${col1Html}</td>
          </tr>
      `
    })
    html += `</tbody></table><p><br></p>`
  }

  if (tableClosingText.value && tableClosingText.value.trim()) {
    const pLines = tableClosingText.value.trim().split('\n').map(l => `<p>${escapeHtml(l)}</p>`).join('')
    html += pLines + '<p><br></p>'
  }

  return html.trim()
}

function syncStructuredTableToHtml() {
  if (editorMode.value === 'table') {
    form.content = generateHtmlFromTableRows()
  }
}

// Parse existing HTML back into structured table rows
function parseHtmlToTableRows(html: string): boolean {
  if (!html || !html.includes('<table')) return false
  if (typeof window === 'undefined') return false

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const table = doc.querySelector('table')
    if (!table) return false

    // Opening text
    const openingParagraphs: string[] = []
    let prev = table.previousElementSibling
    while (prev) {
      const txt = prev.textContent?.trim() || ''
      if (txt) openingParagraphs.unshift(txt)
      prev = prev.previousElementSibling
    }
    if (openingParagraphs.length > 0) {
      tableOpeningText.value = openingParagraphs.join('\n\n')
      showOpeningText.value = true
    }

    // Closing text
    const closingParagraphs: string[] = []
    let next = table.nextElementSibling
    while (next) {
      const txt = next.textContent?.trim() || ''
      if (txt) closingParagraphs.push(txt)
      next = next.nextElementSibling
    }
    if (closingParagraphs.length > 0) {
      tableClosingText.value = closingParagraphs.join('\n\n')
      showClosingText.value = true
    }

    const trs = Array.from(table.querySelectorAll('tr'))
    if (trs.length === 0) return false

    // Detect column count from header or first row
    const headerCols = Array.from(trs[0].querySelectorAll('th, td'))
    const colCount = headerCols.length

    if (colCount >= 4) {
      tableColumnsMode.value = '4_col'
    } else if (colCount === 3) {
      tableColumnsMode.value = '3_col'
    } else {
      tableColumnsMode.value = '2_col'
    }

    const extractText = (cell: Element | undefined) => {
      if (!cell) return ''
      const clone = cell.cloneNode(true) as HTMLElement
      clone.querySelectorAll('br').forEach(br => br.replaceWith('\n'))
      clone.querySelectorAll('p, li').forEach(p => p.append('\n'))
      return clone.textContent?.trim() || ''
    }

    const parsedRows: NotulenTableRow[] = []
    const startIdx = trs.length > 1 ? 1 : 0

    for (let i = startIdx; i < trs.length; i++) {
      const tr = trs[i]
      const cells = Array.from(tr.querySelectorAll('td, th'))
      if (cells.length < 2) continue

      parsedRows.push({
        id: 'row_' + (i + 1) + '_' + Math.random().toString(36).substring(2, 6),
        col1: extractText(cells[1]),
        col2: extractText(cells[2]),
        col3: extractText(cells[3]),
      })
    }

    if (parsedRows.length > 0) {
      tableRows.value = parsedRows
      return true
    }
  } catch (err) {
    console.warn('Failed to parse html into table rows:', err)
  }
  return false
}

// Mode Switcher between Spreadsheet & Word/Docs
function switchEditorMode(mode: 'table' | 'doc') {
  if (mode === 'doc' && editorMode.value === 'table') {
    form.content = generateHtmlFromTableRows()
    editorMode.value = 'doc'
  } else if (mode === 'table' && editorMode.value === 'doc') {
    if (form.content && form.content.includes('<table')) {
      parseHtmlToTableRows(form.content)
    }
    editorMode.value = 'table'
  }
}

// Editor table management & keyboard navigation for Word/Docs Mode
const editorRef = ref<any>(null)
const quillInstance = ref<any>(null)
const editorModules = {
  table: true
}

function onEditorLoad(event: any) {
  const instance = event?.instance || event
  quillInstance.value = instance

  const editorEl = (instance?.root || document.querySelector('.rich-editor-wrapper .ql-editor')) as HTMLElement | null
  if (editorEl) {
    editorEl.removeEventListener('keydown', handleEditorKeyDown)
    editorEl.addEventListener('keydown', handleEditorKeyDown)
  }
}

function focusCell(cell: HTMLElement) {
  if (!cell) return
  const range = document.createRange()
  const sel = window.getSelection()
  range.selectNodeContents(cell)
  range.collapse(false)
  sel?.removeAllRanges()
  sel?.addRange(range)
}

function handleEditorKeyDown(e: KeyboardEvent) {
  const sel = window.getSelection()
  const node = sel?.anchorNode
  const currentCell = (node instanceof HTMLElement ? node : node?.parentElement)?.closest('td') as HTMLElement | null

  // In Word/Doc mode: Intercept Enter inside <td> so it does NOT jump out of cell
  if (e.key === 'Enter' && !e.shiftKey && currentCell) {
    e.preventDefault()
    e.stopPropagation()
    const range = sel?.getRangeAt(0)
    if (range) {
      range.deleteContents()
      const br = document.createElement('br')
      range.insertNode(br)
      const textNode = document.createTextNode('')
      br.after(textNode)
      range.setStartAfter(br)
      range.setEndAfter(br)
      sel?.removeAllRanges()
      sel?.addRange(range)
    }
    return
  }

  // Handle Tab navigation inside table
  if (e.key === 'Tab') {
    if (currentCell) {
      e.preventDefault()
      const table = currentCell.closest('table')
      if (table) {
        const allCells = Array.from(table.querySelectorAll('td')) as HTMLElement[]
        const currentIndex = allCells.indexOf(currentCell)
        if (currentIndex !== -1) {
          if (!e.shiftKey) {
            if (currentIndex < allCells.length - 1) {
              focusCell(allCells[currentIndex + 1])
            } else {
              addTableRow()
            }
          } else {
            if (currentIndex > 0) {
              focusCell(allCells[currentIndex - 1])
            }
          }
        }
      }
    }
  }
}

// Auto-heal legacy or malformed table HTML
function autoHealNotulenTableHtml(raw: string): string {
  if (!raw) return ''
  let cleaned = raw.replace(/<th\b([^>]*)>(.*?)<\/th>/gis, '<td$1><b>$2</b></td>')
  cleaned = cleaned.replace(/<\/?thead\b[^>]*>/gi, '')
  cleaned = cleaned.replace(/<table\b([^>]*)>/gi, (m, attrs) => {
    if (!attrs.includes('border-collapse')) {
      return `<table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">`
    }
    return m
  })
  return cleaned
}

// Helper: Insert formatted table into content (supports 2, 3, or 4 columns)
function insertTable(cols: 2 | 3 | 4) {
  let tableHtml = ''
  if (cols === 4) {
    tableHtml = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 35px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="width: 22%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Perihal / Topik</b></td>
            <td style="width: 48%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Pembahasan / Arahan Pimpinan</b></td>
            <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Tindak Lanjut</b></td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">1</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Topik bahasan pertama...</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">a. Poin arahan pertama...<br/>b. Poin arahan kedua...</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">a. PIC dan batas waktu...</td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">2</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
          </tr>
        </tbody>
      </table>
      <p><br></p>
    `
  } else if (cols === 2) {
    tableHtml = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 40px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Poin Pembahasan / Catatan Rapat</b></td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">1</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Tuliskan poin pembahasan pertama di sini...</td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">2</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Tuliskan poin pembahasan kedua di sini...</td>
          </tr>
        </tbody>
      </table>
      <p><br></p>
    `
  } else {
    tableHtml = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 35px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="width: 30%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Topik / Masukan Peserta</b></td>
            <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Tanggapan & Kesepakatan Bersama</b></td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">1</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Aspirasi / kendala yang disampaikan...</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Tanggapan pimpinan / solusi yang disepakati...</td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">2</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
          </tr>
        </tbody>
      </table>
      <p><br></p>
    `
  }
  form.content = (form.content ? form.content + '<br/>' : '') + tableHtml
  toast.add({ severity: 'info', summary: 'Tabel Disisipkan', detail: `Tabel ${cols} kolom berhasil ditambahkan ke catatan notulensi`, life: 2500 })
}

// Helper: Add a new row to active or last table
function addTableRow() {
  const editorRoot = (quillInstance.value?.root || document.querySelector('.rich-editor-wrapper .ql-editor')) as HTMLElement | null
  if (editorRoot) {
    const tables = editorRoot.querySelectorAll('table')
    if (tables.length > 0) {
      const sel = window.getSelection()
      const currentCell = (sel?.anchorNode instanceof HTMLElement ? sel.anchorNode : sel?.anchorNode?.parentElement)?.closest('td')
      const targetTable = currentCell?.closest('table') || tables[tables.length - 1]
      const rows = Array.from(targetTable.querySelectorAll('tr'))
      const lastRow = rows[rows.length - 1]
      const colCount = lastRow ? lastRow.querySelectorAll('td').length : 2
      const nextNum = rows.length // row 0 is header

      const newTr = document.createElement('tr')
      let cellsHtml = `<td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">${nextNum}</td>`
      for (let c = 1; c < colCount; c++) {
        cellsHtml += `<td style="padding: 8px; border: 1px solid #94a3b8;"></td>`
      }
      newTr.innerHTML = cellsHtml
      const tbody = targetTable.querySelector('tbody') || targetTable
      tbody.appendChild(newTr)

      // Sync form.content
      form.content = editorRoot.innerHTML

      // Focus second cell of the newly added row
      nextTick(() => {
        const targetTd = newTr.querySelectorAll('td')[1] || newTr.querySelector('td')
        if (targetTd) focusCell(targetTd as HTMLElement)
      })

      toast.add({ severity: 'success', summary: 'Baris Ditambahkan', detail: `Baris ke-${nextNum} berhasil ditambahkan`, life: 2000 })
      return
    }
  }

  // Fallback if no table exists yet
  insertTable(2)
}

// Helper: Delete row from active or last table
function deleteTableRow() {
  const editorRoot = (quillInstance.value?.root || document.querySelector('.rich-editor-wrapper .ql-editor')) as HTMLElement | null
  if (editorRoot) {
    const tables = editorRoot.querySelectorAll('table')
    if (tables.length > 0) {
      const sel = window.getSelection()
      const currentCell = (sel?.anchorNode instanceof HTMLElement ? sel.anchorNode : sel?.anchorNode?.parentElement)?.closest('td')
      const targetTable = currentCell?.closest('table') || tables[tables.length - 1]
      const rows = Array.from(targetTable.querySelectorAll('tr'))

      if (rows.length > 2) {
        const currentRow = currentCell?.closest('tr')
        const rowToDelete = (currentRow && rows.indexOf(currentRow) > 0) ? currentRow : rows[rows.length - 1]
        rowToDelete.remove()

        // Re-number rows
        const remainingRows = Array.from(targetTable.querySelectorAll('tr'))
        let counter = 1
        remainingRows.forEach((r, idx) => {
          if (idx === 0) return
          const firstTd = r.querySelector('td')
          if (firstTd) firstTd.textContent = String(counter++)
        })

        form.content = editorRoot.innerHTML
        toast.add({ severity: 'info', summary: 'Baris Dihapus', detail: 'Baris berhasil dihapus', life: 2000 })
      } else {
        toast.add({ severity: 'warn', summary: 'Peringatan', detail: 'Tabel minimal harus memiliki 1 baris data', life: 2500 })
      }
    } else {
      toast.add({ severity: 'warn', summary: 'Tidak Ada Tabel', detail: 'Belum ada tabel yang dibuat', life: 2500 })
    }
  }
}

// Helper: Merge disjointed tables into one unified table
function mergeTables() {
  const editorRoot = (quillInstance.value?.root || document.querySelector('.rich-editor-wrapper .ql-editor')) as HTMLElement | null
  if (editorRoot) {
    const tables = Array.from(editorRoot.querySelectorAll('table'))
    if (tables.length > 1) {
      const firstTable = tables[0]
      const tbody1 = firstTable.querySelector('tbody') || firstTable

      for (let i = 1; i < tables.length; i++) {
        const nextTable = tables[i]
        const rows = Array.from(nextTable.querySelectorAll('tr'))
        rows.forEach((r, idx) => {
          const text = r.textContent?.trim().toLowerCase() || ''
          // If first row is a repeated header, skip it
          if (idx === 0 && (text.includes('poin pembahasan') || text.includes('topik / masukan') || text === 'no' || text.includes('tanggapan'))) {
            return
          }
          tbody1.appendChild(r)
        })

        // Remove whitespace/paragraphs between the two tables
        let prev = nextTable.previousElementSibling
        while (prev && prev !== firstTable && (prev.tagName === 'P' || prev.tagName === 'BR') && !prev.textContent?.trim()) {
          const toRemove = prev
          prev = prev.previousElementSibling
          toRemove.remove()
        }
        nextTable.remove()
      }

      // Re-number sequentially
      const allRows = Array.from(firstTable.querySelectorAll('tr'))
      let counter = 1
      allRows.forEach((r, idx) => {
        if (idx === 0) return // skip header
        const firstTd = r.querySelector('td')
        if (firstTd) firstTd.textContent = String(counter++)
      })

      form.content = editorRoot.innerHTML
      toast.add({ severity: 'success', summary: 'Tabel Digabung', detail: 'Berhasil menggabungkan seluruh tabel menjadi 1 tabel rapi', life: 3000 })
    } else {
      toast.add({ severity: 'info', summary: 'Info', detail: 'Hanya ada 1 tabel di dalam dokumen notulensi', life: 2500 })
    }
  }
}

// Helper: Insert structured notulen template
function insertNotulenTemplate() {
  const templateHtml = `
    <h3>1. Pembukaan & Pengantar Pimpinan</h3>
    <p>Rapat dibuka secara resmi pada pukul ${form.start_time || '08:30'} WIB dengan membaca Basmalah dan arahan singkat pimpinan terkait fokus pertemuan hari ini.</p>
    
    <h3>2. Pembahasan Pokok & Jalannya Diskusi</h3>
    <p>Berikut rangkuman tanggapan dan aspirasi yang disampaikan oleh seluruh peserta rapat:</p>
    <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
      <tbody>
        <tr style="background-color: #f1f5f9; font-weight: bold;">
          <td style="width: 50px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
          <td style="width: 38%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Topik / Masukan Peserta</b></td>
          <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Tanggapan & Solusi yang Disepakati</b></td>
        </tr>
        <tr>
          <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">1</td>
          <td style="padding: 8px; border: 1px solid #94a3b8;">Evaluasi pelaksanaan kegiatan dan kendala di lapangan...</td>
          <td style="padding: 8px; border: 1px solid #94a3b8;">Disepakati penyesuaian jadwal dan koordinasi tim teknis...</td>
        </tr>
      </tbody>
    </table>

    <h3>3. Catatan Khusus & Rekomendasi</h3>
    <ul>
      <li>Seluruh pihak terkait diharapkan menyelesaikan tindak lanjut sebelum batas waktu yang ditentukan.</li>
      <li>Koordinasi teknis lanjutan akan dilakukan secara bertahap pada masing-masing unit kerja.</li>
    </ul>
    <p></p>
  `
  if (form.content && !confirm('Konten yang ada akan ditambahkan dengan template. Lanjutkan?')) return
  form.content = (form.content ? form.content + '<br/>' : '') + templateHtml
  toast.add({ severity: 'success', summary: 'Template Digunakan', detail: 'Template format notulensi berhasil diterapkan', life: 2500 })
}

async function fetchUsers() {
  try {
    users.value = await api.get<any[]>('/users?limit=200')
  } catch (e) {
    console.error('Failed to fetch users', e)
  }
}

async function loadExistingMinute(id: number) {
  try {
    const data = await api.get<any>(`/meeting/minutes/${id}`)
    if (!data) return

    form.scope = data.scope || 'unit'
    form.unit_id = data.unit_id || null
    form.meeting_type = data.meeting_type || 'rapat_unit'
    form.title = data.title || ''
    form.nomor_notulen = data.nomor_notulen || ''
    form.meeting_date = data.meeting_date ? String(data.meeting_date).substring(0, 10) : new Date().toISOString().substring(0, 10)
    form.start_time = data.start_time || '08:30'
    form.end_time = data.end_time || '11:00'
    form.location = data.location || 'Ruang Rapat Utama'
    form.notulis_id = data.notulis_id || authStore.user?.id || null
    form.content = autoHealNotulenTableHtml(data.content || '')
    if (form.content && form.content.includes('<table')) {
      const parsed = parseHtmlToTableRows(form.content)
      if (parsed) {
        editorMode.value = 'table'
      } else {
        editorMode.value = 'doc'
      }
    } else {
      editorMode.value = 'doc'
    }

    if (Array.isArray(data.attendees)) {
      form.attendees = data.attendees.map((a: any) => typeof a === 'object' ? a.id : a)
    }
    if (Array.isArray(data.absent_members)) {
      form.absent_members = data.absent_members.map((a: any) => typeof a === 'object' ? a.id : a)
    }
    if (Array.isArray(data.agenda) && data.agenda.length > 0) {
      form.agenda = [...data.agenda]
    }
    if (Array.isArray(data.decisions) && data.decisions.length > 0) {
      form.decisions = [...data.decisions]
    }
    if (Array.isArray(data.action_items)) {
      form.action_items = data.action_items.map((ai: any) => ({
        id: ai.id,
        task_description: ai.task_description || '',
        pic_user_id: ai.pic_user_id || ai.pic?.id || null,
        deadline: ai.deadline ? String(ai.deadline).substring(0, 10) : '',
        notes: ai.notes || '',
        status: ai.status || 'pending'
      }))
    }
    if (Array.isArray(data.attachment_urls) && data.attachment_urls.length > 0) {
      gdriveUrl.value = data.attachment_urls[0] || ''
    }
  } catch (e: any) {
    console.error('Failed to load existing minute', e)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data notulen untuk diedit', life: 3000 })
  }
}

async function saveMinute(submitNow: boolean) {
  if (!form.title.trim()) {
    toast.add({ severity: 'error', summary: 'Validasi', detail: 'Judul rapat wajib diisi', life: 3000 })
    return
  }

  // Ensure content is synced from Spreadsheet mode if currently active
  if (editorMode.value === 'table') {
    form.content = generateHtmlFromTableRows()
  }

  saving.value = true
  try {
    const payload = {
      ...form,
      agenda: form.agenda.filter(a => a && a.trim().length > 0),
      decisions: form.decisions.filter(d => d && d.trim().length > 0),
      attachment_urls: gdriveUrl.value.trim() ? [gdriveUrl.value.trim()] : [],
    }

    let targetId = editId.value

    if (isEditing.value && targetId) {
      await api.put(`/meeting/minutes/${targetId}`, payload)
      if (submitNow) {
        await api.post(`/meeting/minutes/${targetId}/submit`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Notulen berhasil diperbarui & diajukan', life: 3000 })
      } else {
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Perubahan notulen berhasil disimpan', life: 3000 })
      }
    } else {
      const res = await api.post<{ id: number; nomor_notulen: string }>('/meeting/minutes', payload)
      targetId = res.id

      if (submitNow) {
        await api.post(`/meeting/minutes/${res.id}/submit`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Notulen berhasil dibuat & diajukan untuk disahkan', life: 3000 })
      } else {
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Draf notulen berhasil disimpan', life: 3000 })
      }
    }

    router.push(`/dashboard/internal/notulen/${targetId}`)
  } catch (e: any) {
    console.error('Save minute failed', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: e.data?.detail || e.message || 'Gagal menyimpan notulen', life: 4000 })
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchUsers()
  if (editId.value) {
    await loadExistingMinute(editId.value)
  }
})
</script>

<style scoped>
.rich-editor-wrapper :deep(.p-editor-content) {
  border-bottom-left-radius: 0.75rem;
  border-bottom-right-radius: 0.75rem;
}
.rich-editor-wrapper :deep(.p-editor-toolbar) {
  border-top-left-radius: 0.75rem;
  border-top-right-radius: 0.75rem;
  background-color: #f8fafc;
}
:deep(.dark) .rich-editor-wrapper :deep(.p-editor-toolbar) {
  background-color: #1e293b;
  border-color: #334155;
}

/* Rich Editor Table Styling - Crisp visible borders and clear column layout */
.rich-editor-wrapper :deep(.ql-editor) {
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.6;
}

.rich-editor-wrapper :deep(.ql-editor table) {
  width: 100% !important;
  border-collapse: collapse !important;
  margin: 1rem 0 !important;
  table-layout: auto !important;
  border: 1px solid #94a3b8 !important;
}

.rich-editor-wrapper :deep(.ql-editor table td),
.rich-editor-wrapper :deep(.ql-editor table th) {
  border: 1px solid #94a3b8 !important; /* Clearly visible, distinct line between cells */
  padding: 8px 12px !important;
  min-height: 40px !important;
  vertical-align: top !important;
  box-sizing: border-box !important;
  color: #1e293b !important;
}

/* Column 1 (No) narrow and centered */
.rich-editor-wrapper :deep(.ql-editor table td:first-child),
.rich-editor-wrapper :deep(.ql-editor table th:first-child) {
  width: 50px !important;
  text-align: center !important;
  font-weight: 600 !important;
}

/* Header row with light slate background & bold text */
.rich-editor-wrapper :deep(.ql-editor table tr:first-child td),
.rich-editor-wrapper :deep(.ql-editor table tr:first-child th) {
  background-color: #f1f5f9 !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  border-bottom: 2px solid #64748b !important;
}

/* Focus and hover cues so users clearly see the active cell and column boundaries */
.rich-editor-wrapper :deep(.ql-editor table td:hover) {
  background-color: #f8fafc !important;
}

.rich-editor-wrapper :deep(.ql-editor table td:focus),
.rich-editor-wrapper :deep(.ql-editor table td:focus-within) {
  outline: 2px solid #3b82f6 !important;
  outline-offset: -2px !important;
}

/* Dark mode styling */
:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table) {
  border-color: #475569 !important;
}

:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table td),
:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table th) {
  border-color: #475569 !important;
  color: #f1f5f9 !important;
}

:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table tr:first-child td),
:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table tr:first-child th) {
  background-color: #1e293b !important;
  color: #f8fafc !important;
  border-bottom-color: #94a3b8 !important;
}

:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table td:hover) {
  background-color: rgba(30, 41, 59, 0.7) !important;
}
</style>
