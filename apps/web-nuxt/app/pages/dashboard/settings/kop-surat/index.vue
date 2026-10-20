<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2.5">
          <i class="pi pi-file-pdf text-emerald-600 text-2xl"></i>
          Pengaturan Kop Surat & Dokumen
        </h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Konfigurasi terpusat untuk kop surat resmi institusi. Seluruh fitur cetak dan ekspor PDF (Notulen Rapat, Kalender Pendidikan, Rapor, Surat Keputusan) otomatis menggunakan identitas ini.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <Button 
          label="Reset Default" 
          icon="pi pi-refresh" 
          severity="secondary" 
          outlined 
          size="small" 
          @click="resetToDefault" 
        />
        <Button 
          label="Simpan Kop Surat" 
          icon="pi pi-save" 
          severity="primary" 
          size="small" 
          :loading="saving" 
          @click="saveData" 
        />
      </div>
    </div>

    <!-- Alert / Banner Standarisasi -->
    <div class="p-4 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-emerald-50 dark:bg-emerald-950/20 text-xs text-emerald-800 dark:text-emerald-300 flex items-start gap-3">
      <i class="pi pi-shield-check text-emerald-600 text-lg mt-0.5 shrink-0"></i>
      <div>
        <p class="font-bold mb-0.5">Standarisasi Format Dokumen Resmi Yayasan Asy-Syuuraa</p>
        <p class="text-emerald-700 dark:text-emerald-400 leading-relaxed">
          Setiap perubahan logo, ukuran, font, maupun nomor kontak di halaman ini akan langsung disinkronkan ke seluruh file PDF resmi yang di-generate dari sistem tanpa perlu mengubah kode program.
        </p>
      </div>
    </div>

    <!-- Main Grid: Form + Live Preview -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- Left Column: Form Settings (7 Cols) -->
      <div class="lg:col-span-7 space-y-5">
        <!-- 1. Logo Lembaga & Ukuran -->
        <div class="card p-5 space-y-4">
          <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-500 border-b border-slate-100 dark:border-slate-800 pb-2 flex items-center gap-2">
            <i class="pi pi-image text-primary"></i> 1. Logo Resmi & Ukuran Kop Surat
          </h2>
          <div>
            <CmsImageUploader 
              v-model="form.logo_url" 
              folder="branding/logo"
              label="Logo Lembaga / Yayasan" 
              placeholder="https://... atau upload file PNG berlatar transparan"
            />
            <p class="text-[11px] text-slate-400 mt-1.5">
              Disarankan menggunakan gambar PNG berlatar transparan atau persegi (minimal 200x200 px). Jika logo dikosongkan, kop surat otomatis ditampilkan dalam format teks terpusat (*centered*).
            </p>

            <!-- Pengaturan Ukuran Logo -->
            <div class="mt-4 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="flex items-center justify-between">
                <label class="font-semibold text-xs text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                  <i class="pi pi-arrows-alt text-primary text-xs"></i>
                  Besaran / Skala Logo di Kop Surat:
                </label>
                <span class="text-xs font-bold text-primary px-2 py-0.5 rounded bg-primary/10">
                  {{ form.logo_size || 75 }} px
                </span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-[11px] text-slate-400">Kecil (50px)</span>
                <input 
                  type="range" 
                  min="50" 
                  max="130" 
                  step="5" 
                  v-model.number="form.logo_size" 
                  class="flex-1 h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-600"
                />
                <span class="text-[11px] text-slate-400">Besar (130px)</span>
              </div>
              <p class="text-[10.5px] text-slate-400">
                Ukuran standar ideal berkisar <b>75 px – 90 px</b> agar logo terlihat proporsional, tegas, dan tajam saat diekspor ke PDF maupun dicetak.
              </p>
            </div>

            <!-- Status Lokasi Penyimpanan di R2 -->
            <div 
              v-if="form.logo_url && form.logo_url.includes('/uploads/')" 
              class="mt-3 p-3 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 shadow-xs"
            >
              <div class="flex items-center gap-2">
                <i class="pi pi-info-circle text-amber-600 text-base shrink-0"></i>
                <div>
                  <div class="font-bold">File logo saat ini berada di folder umum (<code>uploads/</code>)</div>
                  <div class="text-[11px] text-amber-700 dark:text-amber-300">Pindahkan ke folder khusus <code>branding/logo/</code> secara otomatis.</div>
                </div>
              </div>
              <Button 
                label="Pindahkan ke branding/logo/" 
                icon="pi pi-arrow-right" 
                size="small" 
                severity="warn" 
                class="!text-xs font-semibold shrink-0"
                :loading="migratingLogo"
                @click="migrateLogo"
              />
            </div>
            <div 
              v-else-if="form.logo_url && form.logo_url.includes('branding/logo')" 
              class="mt-3 p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs flex items-center gap-2"
            >
              <i class="pi pi-check-circle text-emerald-600"></i>
              <span>File logo telah tersimpan rapi di folder khusus: <b>branding/logo/</b></span>
            </div>
          </div>
        </div>

        <!-- 2. Tipografi & Desain Garis Pembatas -->
        <div class="card p-5 space-y-4">
          <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-500 border-b border-slate-100 dark:border-slate-800 pb-2 flex items-center gap-2">
            <i class="pi pi-palette text-primary"></i> 2. Tipografi & Gaya Garis Kop Surat
          </h2>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <!-- Pilihan Font -->
            <div class="flex flex-col gap-1.5">
              <label class="font-semibold text-slate-700 dark:text-slate-300">
                Jenis Font Dokumen & Kop Surat:
              </label>
              <Select 
                v-model="form.font_family" 
                :options="fontOptions" 
                optionLabel="label" 
                optionValue="value" 
                fluid 
              />
              <span class="text-[10.5px] text-slate-400">
                Pilih <b>Times New Roman</b> untuk dokumen resmi/kedinasan, atau <b>Arial</b> untuk nuansa modern.
              </span>
            </div>

            <!-- Warna Garis Pembatas -->
            <div class="flex flex-col gap-1.5">
              <label class="font-semibold text-slate-700 dark:text-slate-300">
                Warna Aksen Garis Ganda:
              </label>
              <div class="flex items-center gap-2 pt-1">
                <div class="flex items-center gap-1.5">
                  <button
                    v-for="color in presetColors"
                    :key="color.value"
                    type="button"
                    class="w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 flex items-center justify-center text-white text-[10px]"
                    :style="{ backgroundColor: color.value }"
                    :class="form.line_color === color.value ? 'border-slate-800 dark:border-white ring-2 ring-primary/40' : 'border-transparent'"
                    :title="color.label"
                    @click="form.line_color = color.value"
                  >
                    <i v-if="form.line_color === color.value" class="pi pi-check text-[10px]"></i>
                  </button>
                </div>
                <InputText v-model="form.line_color" class="!w-24 !py-1 text-xs font-mono uppercase ml-auto" placeholder="#059669" />
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Mode Pengaturan: Standar vs Fleksibel / Custom Lines -->
        <div class="card p-5 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
            <div>
              <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <i class="pi pi-sliders-h text-primary"></i> 3. Mode Penataan Teks Kop Surat
              </h2>
              <p class="text-[11px] text-slate-400 mt-0.5">
                Pilih menggunakan formulir standar atau editor baris fleksibel (custom baris & ukuran).
              </p>
            </div>

            <!-- Mode Switcher -->
            <div class="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
              <button 
                type="button" 
                class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
                :class="!form.use_custom_lines ? 'bg-white dark:bg-slate-700 text-primary shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-white'"
                @click="form.use_custom_lines = false"
              >
                Form Standar
              </button>
              <button 
                type="button" 
                class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5"
                :class="form.use_custom_lines ? 'bg-white dark:bg-slate-700 text-primary shadow-xs' : 'text-slate-500 hover:text-slate-800 dark:hover:text-white'"
                @click="enableCustomLinesMode"
              >
                <i class="pi pi-pencil text-[10px]"></i> Editor Fleksibel
              </button>
            </div>
          </div>

          <!-- MODE A: Form Standar -->
          <div v-if="!form.use_custom_lines" class="space-y-4">
            <!-- Nama Instansi & Legalitas -->
            <div class="space-y-3 text-xs">
              <div class="flex flex-col gap-1.5">
                <label class="font-semibold text-slate-700 dark:text-slate-300">
                  Nama Badan Penyelenggara / Yayasan (Baris Utama 1) <span class="text-red-500">*</span>
                </label>
                <InputText v-model="form.nama_yayasan" placeholder="YAYASAN ASY-SYUURAA BATAM" fluid />
              </div>

              <div class="flex flex-col gap-1.5">
                <label class="font-semibold text-slate-700 dark:text-slate-300">
                  Nama Satuan Pendidikan / Sub-Instansi (Baris Utama 2) <span class="text-red-500">*</span>
                </label>
                <InputText v-model="form.nama_unit" placeholder="SEKOLAH ISLAM TERPADU ASY-SYUURAA" fluid />
                <span class="text-[11px] text-slate-400">
                  *Catatan: Pada dokumen khusus unit (misal Rapat Unit SMPIT), sistem dapat menyesuaikan baris ini dengan unit terkait.
                </span>
              </div>

              <div class="flex flex-col gap-1.5">
                <label class="font-semibold text-slate-700 dark:text-slate-300">
                  Legalitas, SK Kemenkumham, atau Akreditasi (Baris 3)
                </label>
                <InputText v-model="form.keterangan_legal" placeholder="SK Men Kum No: AHU-0001606.AH.01.05 Tahun 2023" fluid />
              </div>

              <div class="flex flex-col gap-1.5">
                <label class="font-semibold text-slate-700 dark:text-slate-300">
                  Alamat Lengkap Institusi <span class="text-red-500">*</span>
                </label>
                <Textarea v-model="form.alamat" rows="2" placeholder="Komplek Asy-Syuuraa, Sungai Langkai, Kec. Sagulung, Batam..." fluid />
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <div class="flex flex-col gap-1.5">
                  <label class="font-semibold text-slate-700 dark:text-slate-300">No. Telepon Kantor</label>
                  <InputText v-model="form.telepon" placeholder="(0778) 4091272" fluid />
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="font-semibold text-slate-700 dark:text-slate-300">WhatsApp / Layanan Cepat</label>
                  <InputText v-model="form.whatsapp" placeholder="Kosongkan jika tidak ditampilkan" fluid />
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="font-semibold text-slate-700 dark:text-slate-300">Email Resmi</label>
                  <InputText v-model="form.email" placeholder="kabid.asysyuuraa@gmail.com" fluid />
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="font-semibold text-slate-700 dark:text-slate-300">Website Resmi</label>
                  <InputText v-model="form.website" placeholder="https://asy-syuuraabatam.or.id" fluid />
                </div>
              </div>
            </div>
          </div>

          <!-- MODE B: Editor Baris Fleksibel (Custom Lines) -->
          <div v-else class="space-y-4">
            <div class="flex items-center justify-between flex-wrap gap-2">
              <span class="text-xs font-bold text-slate-700 dark:text-slate-300">
                Daftar Baris Teks Kop Surat ({{ form.custom_lines.length }} Baris)
              </span>
              <div class="flex items-center gap-1.5">
                <Button 
                  label="Generate dari Form Standar" 
                  icon="pi pi-sync" 
                  size="small" 
                  outlined 
                  severity="secondary" 
                  class="!text-xs !py-1"
                  @click="populateCustomLinesFromStandard" 
                  title="Salin data yayasan, unit, legalitas, alamat, dan kontak ke daftar baris kustom"
                />
                <Button 
                  label="Tambah Baris" 
                  icon="pi pi-plus" 
                  size="small" 
                  severity="success" 
                  class="!text-xs !py-1"
                  @click="addCustomLine" 
                />
              </div>
            </div>

            <!-- Dynamic Lines List -->
            <div class="space-y-3">
              <div 
                v-for="(line, idx) in form.custom_lines" 
                :key="idx" 
                class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/50 space-y-2.5 transition-all"
              >
                <!-- Line Header: Order and Controls -->
                <div class="flex items-center justify-between gap-2">
                  <div class="flex items-center gap-2">
                    <span class="w-6 h-6 rounded-full bg-primary/10 text-primary font-bold text-xs flex items-center justify-center">
                      {{ idx + 1 }}
                    </span>
                    <span class="text-xs font-semibold text-slate-600 dark:text-slate-300">
                      Baris {{ idx + 1 }}
                    </span>
                  </div>

                  <div class="flex items-center gap-1">
                    <Button 
                      icon="pi pi-arrow-up" 
                      text 
                      rounded 
                      size="small" 
                      severity="secondary" 
                      :disabled="idx === 0" 
                      @click="moveLineUp(idx)" 
                      title="Geser ke atas" 
                    />
                    <Button 
                      icon="pi pi-arrow-down" 
                      text 
                      rounded 
                      size="small" 
                      severity="secondary" 
                      :disabled="idx === form.custom_lines.length - 1" 
                      @click="moveLineDown(idx)" 
                      title="Geser ke bawah" 
                    />
                    <Button 
                      icon="pi pi-trash" 
                      text 
                      rounded 
                      size="small" 
                      severity="danger" 
                      @click="removeCustomLine(idx)" 
                      title="Hapus baris ini" 
                    />
                  </div>
                </div>

                <!-- Text Input -->
                <div>
                  <InputText 
                    v-model="line.text" 
                    placeholder="Tuliskan teks untuk baris ini..." 
                    class="w-full text-xs font-medium" 
                  />
                </div>

                <!-- Formatting Controls (Font Size, Bold, Italic, Color, Align) -->
                <div class="flex items-center flex-wrap gap-3 pt-1 text-xs">
                  <!-- Font Size -->
                  <div class="flex items-center gap-1.5">
                    <span class="text-slate-400 text-[11px]">Ukuran:</span>
                    <Select 
                      v-model.number="line.font_size" 
                      :options="fontSizeOptions" 
                      optionLabel="label" 
                      optionValue="value" 
                      class="!w-24 !py-0.5 text-xs" 
                    />
                  </div>

                  <!-- Bold & Italic Toggles -->
                  <div class="flex items-center gap-1 border border-slate-200 dark:border-slate-700 rounded-lg p-0.5 bg-white dark:bg-slate-700">
                    <button 
                      type="button" 
                      class="px-2 py-1 rounded text-xs font-bold transition-all"
                      :class="line.bold ? 'bg-primary text-white' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100'"
                      @click="line.bold = !line.bold"
                      title="Tebal (Bold)"
                    >
                      B
                    </button>
                    <button 
                      type="button" 
                      class="px-2.5 py-1 rounded text-xs italic font-serif transition-all"
                      :class="line.italic ? 'bg-primary text-white' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100'"
                      @click="line.italic = !line.italic"
                      title="Miring (Italic)"
                    >
                      I
                    </button>
                  </div>

                  <!-- Text Color Selection -->
                  <div class="flex items-center gap-1.5">
                    <span class="text-slate-400 text-[11px]">Warna:</span>
                    <select 
                      v-model="line.color" 
                      class="px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 text-xs bg-white dark:bg-slate-700 text-slate-800 dark:text-white"
                    >
                      <option value="#0F172A">Hitam Gelap (#0F172A)</option>
                      <option :value="form.line_color || '#059669'">Warna Aksen Kop ({{ form.line_color || '#059669' }})</option>
                      <option value="#475569">Abu-abu (#475569)</option>
                      <option value="#1E3A8A">Navy (#1E3A8A)</option>
                      <option value="#831843">Maroon (#831843)</option>
                    </select>
                  </div>

                  <!-- Text Align -->
                  <div class="flex items-center gap-1 border border-slate-200 dark:border-slate-700 rounded-lg p-0.5 bg-white dark:bg-slate-700 ml-auto">
                    <button 
                      type="button" 
                      class="px-2 py-1 rounded text-xs transition-all"
                      :class="line.align === 'left' ? 'bg-primary text-white' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100'"
                      @click="line.align = 'left'"
                      title="Rata Kiri"
                    >
                      <i class="pi pi-align-left text-xs"></i>
                    </button>
                    <button 
                      type="button" 
                      class="px-2 py-1 rounded text-xs transition-all"
                      :class="line.align === 'center' ? 'bg-primary text-white' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100'"
                      @click="line.align = 'center'"
                      title="Rata Tengah"
                    >
                      <i class="pi pi-align-center text-xs"></i>
                    </button>
                    <button 
                      type="button" 
                      class="px-2 py-1 rounded text-xs transition-all"
                      :class="line.align === 'right' ? 'bg-primary text-white' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100'"
                      @click="line.align = 'right'"
                      title="Rata Kanan"
                    >
                      <i class="pi pi-align-right text-xs"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="form.custom_lines.length === 0" class="p-6 text-center text-slate-400 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-dashed border-slate-200 dark:border-slate-700">
                <i class="pi pi-file-edit text-2xl mb-1.5 text-slate-300"></i>
                <p class="font-medium text-xs">Belum ada baris kustom yang ditambahkan.</p>
                <p class="text-[11px] mt-0.5">Klik tombol <b>"Generate dari Form Standar"</b> di atas untuk menyusun baris secara otomatis.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Live Document Preview (5 Cols Sticky) -->
      <div class="lg:col-span-5 space-y-4 sticky top-20">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <i class="pi pi-eye text-emerald-600"></i> Pratinjau Kop Surat (Live Preview)
          </span>
          <span class="text-[11px] text-slate-400">Ukuran A4 Standar</span>
        </div>

        <!-- Simulation Paper A4 Card -->
        <div 
          class="bg-white rounded-xl shadow-xl border border-slate-200/80 p-6 text-slate-800 relative overflow-hidden transition-all"
          :class="form.font_family === 'times' ? 'font-serif' : 'font-sans'"
        >
          <div class="absolute top-0 right-0 px-2 py-0.5 bg-slate-100 border-b border-l border-slate-200 text-[10px] text-slate-400 font-mono">
            Preview PDF ({{ form.font_family === 'times' ? 'Times New Roman' : 'Arial' }})
          </div>

          <!-- Letterhead Box -->
          <div class="pt-2">
            <div class="flex items-center gap-4">
              <!-- Logo Container with Dynamic Scalable Size -->
              <div 
                v-if="form.logo_url" 
                class="shrink-0 rounded-lg flex items-center justify-center p-1 bg-slate-50 border border-slate-100 overflow-hidden"
                :style="{ width: (form.logo_size || 75) + 'px', height: (form.logo_size || 75) + 'px' }"
              >
                <img :src="form.logo_url" alt="Logo" class="max-w-full max-h-full object-contain" />
              </div>
              <div 
                v-else 
                class="shrink-0 rounded-lg border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-[10px] text-slate-400"
                :style="{ width: (form.logo_size || 75) + 'px', height: (form.logo_size || 75) + 'px' }"
              >
                <i class="pi pi-image mb-0.5"></i>
                <span>No Logo</span>
              </div>

              <!-- Institution Titles -->
              <div class="flex-1" :class="{ 'pl-2': form.logo_url }">
                <!-- If Custom Lines mode active and has lines -->
                <div v-if="form.use_custom_lines && form.custom_lines && form.custom_lines.length > 0" class="space-y-0.5">
                  <div 
                    v-for="(cl, cidx) in form.custom_lines" 
                    :key="cidx"
                    :style="{
                      fontSize: (cl.font_size || 10) + 'px',
                      fontWeight: cl.bold ? '700' : '400',
                      fontStyle: cl.italic ? 'italic' : 'normal',
                      color: cl.color || '#0F172A',
                      textAlign: cl.align || 'center',
                      lineHeight: '1.25'
                    }"
                  >
                    {{ cl.text }}
                  </div>
                </div>

                <!-- Otherwise Standard Layout -->
                <div v-else class="text-center">
                  <h3 class="font-extrabold text-sm sm:text-base leading-tight tracking-wide text-slate-900 uppercase">
                    {{ form.nama_yayasan || 'YAYASAN ASY-SYUURAA BATAM' }}
                  </h3>
                  <h4 class="font-bold text-xs sm:text-sm leading-tight uppercase mt-0.5" :style="{ color: form.line_color || '#059669' }">
                    {{ form.nama_unit || 'SEKOLAH ISLAM TERPADU ASY-SYUURAA' }}
                  </h4>
                  <p v-if="form.keterangan_legal" class="text-[9.5px] italic text-slate-500 leading-snug mt-0.5">
                    {{ form.keterangan_legal }}
                  </p>
                  <p class="text-[9.5px] text-slate-600 leading-snug mt-0.5">
                    {{ form.alamat || 'Komplek Asy-Syuuraa, Batam, Kepulauan Riau' }}
                  </p>
                  <p v-if="previewContacts" class="text-[9px] text-slate-500 leading-snug mt-0.5 font-medium">
                    {{ previewContacts }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Double Line Separator -->
            <div class="mt-3.5 space-y-0.5">
              <div class="w-full h-[2.5px]" :style="{ backgroundColor: form.line_color || '#059669' }"></div>
              <div class="w-full h-[0.8px]" :style="{ backgroundColor: form.line_color || '#059669' }"></div>
            </div>
          </div>

          <!-- Document Mock Body -->
          <div class="mt-6 space-y-3 opacity-60 pointer-events-none select-none text-[10px] text-slate-400">
            <div class="text-center font-bold text-slate-700 text-xs uppercase underline">
              SURAT KEPUTUSAN / NOTULEN RAPAT
            </div>
            <div class="text-center text-[9px] text-slate-500 -mt-2">
              Nomor: 012/YYS-AS/SK/2026
            </div>
            <div class="space-y-1.5 pt-2">
              <div class="h-2 bg-slate-200 rounded w-full"></div>
              <div class="h-2 bg-slate-200 rounded w-11/12"></div>
              <div class="h-2 bg-slate-200 rounded w-4/5"></div>
            </div>
            <div class="grid grid-cols-2 gap-4 pt-4">
              <div class="h-10 border border-dashed border-slate-200 rounded"></div>
              <div class="h-10 border border-dashed border-slate-200 rounded"></div>
            </div>
          </div>
        </div>

        <div class="card p-4 space-y-2 text-xs text-slate-500 dark:text-slate-400 bg-slate-50/50 dark:bg-slate-800/40">
          <p class="font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
            <i class="pi pi-info-circle text-primary"></i> Modul Terintegrasi
          </p>
          <ul class="list-disc list-inside space-y-1 text-[11px]">
            <li><strong>Notulen Rapat:</strong> Header otomatis sinkron dengan logo & nomor izin.</li>
            <li><strong>Kalender Pendidikan:</strong> Cetak browser & PDF memakai kop terpusat.</li>
            <li><strong>Kepegawaian & SK:</strong> Surat resmi & data pegawai memakai kop standar.</li>
            <li><strong>PPDB Online:</strong> Formulir & bukti pendaftaran resmi siswa.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const saving = ref(false)

const DEFAULT_SETTINGS = {
  nama_yayasan: 'YAYASAN ASY-SYUURAA BATAM',
  nama_unit: 'SEKOLAH ISLAM TERPADU ASY-SYUURAA',
  keterangan_legal: 'SK Men Kum No: AHU-0001606.AH.01.05 Tahun 2023',
  alamat: 'Kavling Lama RT 03, RW 10 Kel. Sagulung Kota, Kec. Sagulung, Kota Batam, Kepulauan Riau 29439',
  telepon: '(0778) 4091272',
  whatsapp: '',
  email: 'kabid.asysyuuraa@gmail.com',
  website: 'https://asy-syuuraabatam.or.id',
  logo_url: '',
  logo_size: 75,
  font_family: 'times',
  line_color: '#059669',
  use_custom_lines: false,
  custom_lines: [] as Array<{
    text: string
    font_size: number
    bold: boolean
    italic: boolean
    color: string
    align: string
  }>
}

const form = reactive({ ...DEFAULT_SETTINGS })

const fontOptions = [
  { label: 'Times New Roman (Resmi / Lembaga)', value: 'times' },
  { label: 'Arial / Helvetica (Modern / Bersih)', value: 'arial' },
]

const fontSizeOptions = [
  { label: '7 pt', value: 7 },
  { label: '8 pt', value: 8 },
  { label: '9 pt', value: 9 },
  { label: '10 pt', value: 10 },
  { label: '11 pt', value: 11 },
  { label: '12 pt', value: 12 },
  { label: '13 pt', value: 13 },
  { label: '14 pt', value: 14 },
  { label: '16 pt', value: 16 },
  { label: '18 pt', value: 18 },
]

const presetColors = [
  { label: 'Emerald (Khas Yayasan)', value: '#059669' },
  { label: 'Navy Blue (Formal)', value: '#1E3A8A' },
  { label: 'Teal (Modern)', value: '#0D9488' },
  { label: 'Charcoal Slate', value: '#334155' },
  { label: 'Dark Maroon', value: '#831843' }
]

const previewContacts = computed(() => {
  const parts = []
  if (form.telepon) parts.push(`Telp: ${form.telepon}`)
  if (form.whatsapp) parts.push(`WA: ${form.whatsapp}`)
  if (form.email) parts.push(`Email: ${form.email}`)
  if (form.website) parts.push(`Web: ${form.website.replace('https://', '')}`)
  return parts.join(' • ')
})

function enableCustomLinesMode() {
  form.use_custom_lines = true
  if (!form.custom_lines || form.custom_lines.length === 0) {
    populateCustomLinesFromStandard()
  }
}

function populateCustomLinesFromStandard() {
  const lines = []
  if (form.nama_yayasan) {
    lines.push({
      text: form.nama_yayasan.toUpperCase(),
      font_size: 13,
      bold: true,
      italic: false,
      color: '#0F172A',
      align: 'center'
    })
  }
  if (form.nama_unit) {
    lines.push({
      text: form.nama_unit.toUpperCase(),
      font_size: 11,
      bold: true,
      italic: false,
      color: form.line_color || '#059669',
      align: 'center'
    })
  }
  if (form.keterangan_legal) {
    lines.push({
      text: form.keterangan_legal,
      font_size: 8,
      bold: false,
      italic: true,
      color: '#475569',
      align: 'center'
    })
  }
  if (form.alamat) {
    lines.push({
      text: form.alamat,
      font_size: 8,
      bold: false,
      italic: false,
      color: '#475569',
      align: 'center'
    })
  }
  if (previewContacts.value) {
    lines.push({
      text: previewContacts.value,
      font_size: 8,
      bold: false,
      italic: false,
      color: '#475569',
      align: 'center'
    })
  }
  form.custom_lines = lines
  toast.add({ severity: 'info', summary: 'Sinkronisasi', detail: 'Daftar baris kustom berhasil digenerate dari data formulir standar', life: 2500 })
}

function addCustomLine() {
  if (!Array.isArray(form.custom_lines)) {
    form.custom_lines = []
  }
  form.custom_lines.push({
    text: '',
    font_size: 10,
    bold: false,
    italic: false,
    color: '#0F172A',
    align: 'center'
  })
}

function removeCustomLine(idx: number) {
  form.custom_lines.splice(idx, 1)
}

function moveLineUp(idx: number) {
  if (idx <= 0) return
  const temp = form.custom_lines[idx]
  form.custom_lines[idx] = form.custom_lines[idx - 1]
  form.custom_lines[idx - 1] = temp
}

function moveLineDown(idx: number) {
  if (idx >= form.custom_lines.length - 1) return
  const temp = form.custom_lines[idx]
  form.custom_lines[idx] = form.custom_lines[idx + 1]
  form.custom_lines[idx + 1] = temp
}

async function fetchData() {
  try {
    const res = await api.get<any>('/public/content/settings_letterhead')
    if (res && res.content_json) {
      const data = JSON.parse(res.content_json)
      Object.assign(form, data)
      // Clean dummy default WhatsApp if found from older seed
      if (form.whatsapp === '0812-7000-0000') {
        form.whatsapp = ''
      }
      if (!form.logo_size) {
        form.logo_size = 75
      }
      if (!form.font_family) {
        form.font_family = 'times'
      }
    }
    if (res && res.image_url && !form.logo_url) {
      form.logo_url = res.image_url
    }
  } catch (e: any) {
    if (e?.statusCode !== 404 && e?.status !== 404) {
      console.error('Failed to load letterhead settings:', e)
    }
  }
}

async function saveData() {
  if (!form.nama_yayasan.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nama Yayasan wajib diisi', life: 3000 })
    return
  }

  saving.value = true
  try {
    // If not in custom lines mode, empty the custom_lines so backend uses standard format
    const payloadToSave = { ...form }
    if (!form.use_custom_lines) {
      payloadToSave.custom_lines = []
    }

    const payload = {
      section_key: 'settings_letterhead',
      title: form.nama_yayasan,
      subtitle: form.nama_unit,
      body: form.alamat,
      image_url: form.logo_url,
      content_json: JSON.stringify(payloadToSave)
    }

    await api.put('/cms/content/settings_letterhead', payload)
    toast.add({
      severity: 'success',
      summary: 'Berhasil Disimpan',
      detail: 'Konfigurasi kop surat resmi berhasil diperbarui dan aktif di seluruh dokumen.',
      life: 3500
    })
  } catch (e: any) {
    console.error('Error saving letterhead:', e)
    toast.add({
      severity: 'error',
      summary: 'Gagal Menyimpan',
      detail: e?.data?.detail || 'Terjadi kesalahan saat menyimpan pengaturan kop surat.',
      life: 4000
    })
  } finally {
    saving.value = false
  }
}

function resetToDefault() {
  Object.assign(form, DEFAULT_SETTINGS)
  toast.add({
    severity: 'info',
    summary: 'Form Direset',
    detail: 'Konfigurasi dikembalikan ke default. Klik Simpan untuk mempermanenkan.',
    life: 3000
  })
}

const migratingLogo = ref(false)
async function migrateLogo() {
  migratingLogo.value = true
  try {
    const res = await api.post<any>('/cms/migrate-letterhead-logo')
    if (res?.new_url) {
      form.logo_url = res.new_url
    }
    toast.add({
      severity: 'success',
      summary: 'Migrasi Berhasil',
      detail: res?.message || 'Logo berhasil dipindahkan ke folder branding/logo/!',
      life: 4000
    })
  } catch (e: any) {
    console.error('Migrasi logo gagal:', e)
    toast.add({
      severity: 'error',
      summary: 'Gagal Migrasi',
      detail: e?.data?.detail || e?.message || 'Terjadi kesalahan saat memindahkan logo.',
      life: 5000
    })
  } finally {
    migratingLogo.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
