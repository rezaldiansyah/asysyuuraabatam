<template>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Manajemen Konten Halaman</h1>
          <p class="text-slate-500 dark:text-slate-400">Kelola konten untuk Halaman Utama dan Unit Pendidikan</p>
        </div>
        <div class="w-full md:w-64">
           <Select 
              v-model="context" 
              :options="contextOptions" 
              optionLabel="label" 
              optionValue="value"
              placeholder="Pilih Halaman"
              class="w-full"
            />
        </div>
      </div>

      <!-- Main Content -->
      <div class="card">
        <TabView>
            <!-- HERO TAB -->
            <TabPanel header="Banner Utama">
                <div class="space-y-4 pt-4">
                    <div class="flex flex-col gap-2">
                        <label class="font-medium">Judul Utama (Headline)</label>
                        <InputText v-model="heroData.title" placeholder="Judul menarik..." />
                    </div>
                    <div class="flex flex-col gap-2">
                        <label class="font-medium">Deskripsi</label>
                        <Textarea v-model="heroData.body" rows="4" placeholder="Deskripsi singkat..." />
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="flex flex-col gap-2">
                            <label class="font-medium">Teks Tombol</label>
                            <InputText v-model="heroData.cta_text" placeholder="Daftar Sekarang" />
                        </div>
                        <div class="flex flex-col gap-2">
                            <label class="font-medium">Link Tombol</label>
                            <InputText v-model="heroData.cta_link" placeholder="/ppdb" />
                        </div>
                    </div>
                     <div class="flex flex-col gap-2">
                        <label class="font-medium">URL Gambar Latar</label>
                        <InputText v-model="heroData.image_url" placeholder="https://..." />
                    </div>
                    <Button label="Simpan Banner" icon="pi pi-save" :loading="loading" @click="saveSection('hero')" />
                </div>
            </TabPanel>

            <!-- VISI MISI TAB (Profil Only) -->
            <TabPanel header="Visi & Misi" v-if="context === 'profil'">
                 <div class="space-y-4 pt-4">
                    <div class="flex flex-col gap-2">
                        <label class="font-medium">Visi</label>
                        <Textarea v-model="visiMisiData.visi" rows="3" placeholder="Visi sekolah..." />
                    </div>
                     <CmsListEditor 
                        v-model="visiMisiData.misi" 
                        titleLabel="Poin Misi" 
                        :withIcon="false"
                        :withDesc="false"
                        :withImage="false"
                    />
                    <Button label="Simpan Visi Misi" icon="pi pi-save" :loading="loading" @click="saveSection('visimisi')" />
                 </div>
            </TabPanel>

            <!-- SEJARAH TAB (Profil Only) -->
            <TabPanel header="Sejarah" v-if="context === 'profil'">
                 <div class="space-y-4 pt-4">
                    <div class="flex flex-col gap-2">
                        <label class="font-medium">Sejarah Singkat</label>
                        <Textarea v-model="historyData.body" rows="12" placeholder="Sejarah berdirinya yayasan..." />
                    </div>
                    <Button label="Simpan Sejarah" icon="pi pi-save" :loading="loading" @click="saveSection('history')" />
                 </div>
            </TabPanel>

            <!-- SAMBUTAN TAB (Hide on Profil) -->
            <TabPanel header="Sambutan" v-if="context !== 'profil'">
                <div class="space-y-4 pt-4">
                     <div class="flex flex-col gap-2">
                        <label class="font-medium">Judul Sambutan</label>
                        <InputText v-model="sambutanData.title" placeholder="Sambutan Ketua Yayasan..." />
                    </div>
                     <div class="flex flex-col gap-2">
                        <label class="font-medium">Sub-judul / Jabatan</label>
                        <InputText v-model="sambutanData.subtitle" placeholder="Ketua Yayasan..." />
                    </div>
                     <div class="flex flex-col gap-2">
                        <label class="font-medium">Isi Sambutan</label>
                        <Textarea v-model="sambutanData.body" rows="8" placeholder="Assalamu'alaikum..." />
                    </div>
                     <div class="flex flex-col gap-2">
                        <label class="font-medium">URL Foto Pimpinan</label>
                        <InputText v-model="sambutanData.image_url" placeholder="https://..." />
                    </div>
                     <Button label="Simpan Sambutan" icon="pi pi-save" :loading="loading" @click="saveSection('sambutan')" />
                </div>
            </TabPanel>

            <!-- KEUNGGULAN TAB (Hide on Profil) -->
            <TabPanel header="Keunggulan" v-if="context !== 'profil'">
                 <div class="space-y-4 pt-4">
                    <CmsListEditor 
                        v-model="featuresData" 
                        titleLabel="Judul Keunggulan" 
                        descLabel="Deskripsi Singkat"
                    />
                    <Button label="Simpan Keunggulan" icon="pi pi-save" :loading="loading" @click="saveSection('features')" />
                 </div>
            </TabPanel>

            <!-- TESTIMONI TAB (Hide on Profil) -->
            <TabPanel header="Testimoni" v-if="context !== 'profil'">
                 <div class="space-y-4 pt-4">
                    <CmsListEditor 
                        v-model="testimonialsData" 
                        titleLabel="Nama Tokoh" 
                        descLabel="Isi Testimoni"
                        imageLabel="Foto Profil URL"
                        :withIcon="false"
                    />
                    <Button label="Simpan Testimoni" icon="pi pi-save" :loading="loading" @click="saveSection('testimonials')" />
                 </div>
            </TabPanel>
        </TabView>
      </div>
    </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({
    layout: 'dashboard'
    // middleware: ['auth'] - Handled by auth.global.ts
})

const api = useApi()
const toast = useToast()
const route = useRoute()
const loading = ref(false)

const context = ref('home')
const contextOptions = [
    { value: 'home', label: 'Halaman Utama (Yayasan)' },
    { value: 'profil', label: 'Profil Yayasan' },
    { value: 'unit_ra', label: 'Unit RA' },
    { value: 'unit_sdit', label: 'Unit SDIT' },
    { value: 'unit_smpit', label: 'Unit SMPIT' },
]

// Data States
const heroData = reactive({ title: '', body: '', cta_text: '', cta_link: '', image_url: '' })
const sambutanData = reactive({ title: '', subtitle: '', body: '', image_url: '' })
const featuresData = ref('[]')
const testimonialsData = ref('[]')
const visiMisiData = reactive({ visi: '', misi: '[]' })
const historyData = reactive({ body: '' })

const defaultFeatures = [
    { icon: "BookOpen", title: "Kurikulum Terpadu", description: "Memadukan Kurikulum Nasional (Merdeka) dengan Kurikulum Khas Sekolah Islam Terpadu." },
    { icon: "Heart", title: "Bina Pribadi Islami", description: "Pembentukan karakter (adab & akhlaq) yang intensif melalui mentoring dan keteladanan." },
]

// Fetch Data
async function fetchData() {
    loading.value = true
    try {
        const prefix = context.value === 'home' ? 'home' : context.value.replace('unit_', '')
        
        // Parallel requests based on context
        const promises = [
            api.get<any>(`/public/content/${prefix}_hero`).catch(() => ({})),
        ]

        if (context.value === 'profil') {
             promises.push(
                api.get<any>(`/public/content/profil_visimisi`).catch(() => ({})),
                api.get<any>(`/public/content/profil_history`).catch(() => ({})),
                Promise.resolve({}), // Dummy for features
                Promise.resolve({})  // Dummy for testimonials
             )
        } else {
             promises.push(
                api.get<any>(`/public/content/${prefix}_sambutan`).catch(() => ({})),
                api.get<any>(`/public/content/${prefix}_features`).catch(() => ({})),
                api.get<any>(`/public/content/${prefix}_testimonials`).catch(() => ({})),
             )
        }
        
        const [hero, second, third, fourth] = await Promise.all(promises)

        // Hero (Common)
        Object.assign(heroData, { 
            title: hero.title || '', 
            body: hero.body || '', 
            cta_text: hero.cta_text || '', 
            cta_link: hero.cta_link || '', 
            image_url: hero.image_url || '' 
        })

        if (context.value === 'profil') {
            // Second = Visi Misi
            if (second.body) {
                visiMisiData.visi = second.body
            } else {
                 visiMisiData.visi = "Mewujudkan generasi Qur'ani yang berakhlak mulia, cerdas, mandiri, dan berwawasan global melalui pendidikan Islam terpadu."
            }

            if (second.content_json && second.content_json !== 'null' && second.content_json !== '[]') {
                visiMisiData.misi = second.content_json
            } else {
                const defaultMisi = [
                    "Menyelenggarakan pendidikan Islam yang berkualitas dan terpadu",
                    "Membina akhlak dan karakter Islami siswa",
                    "Mengembangkan potensi akademik dan non-akademik",
                    "Menanamkan kecintaan terhadap Al-Qur'an"
                ]
                visiMisiData.misi = JSON.stringify(defaultMisi.map(m => ({ title: m, description: '' })))
            }

            // Third = History
            if (third.body) {
                historyData.body = third.body
            } else {
                historyData.body = `Yayasan Asy-Syuuraa didirikan dengan semangat untuk memberikan pendidikan Islam berkualitas bagi masyarakat Batam. Berawal dari sebuah TK Islam kecil, kini telah berkembang menjadi yayasan pendidikan yang menaungi tiga unit pendidikan: RA (Raudhatul Athfal), SDIT (Sekolah Dasar Islam Terpadu), dan SMPIT (Sekolah Menengah Pertama Islam Terpadu).\n\nDengan motto "Mewujudkan Generasi Qur'ani", Yayasan Asy-Syuuraa berkomitmen untuk mencetak lulusan yang tidak hanya unggul dalam akademik, tetapi juga memiliki pemahaman agama yang kuat dan akhlak yang mulia.`
            }

        } else {
            // Normal Flow
            const sambutan = second
            const features = third
            const testimonials = fourth

            Object.assign(sambutanData, {
                title: sambutan.title || '',
                subtitle: sambutan.subtitle || '',
                body: sambutan.body || '',
                image_url: sambutan.image_url || ''
            })

            if (features.content_json && features.content_json !== 'null') {
                featuresData.value = features.content_json
            } else {
                 featuresData.value = context.value === 'home' ? JSON.stringify(defaultFeatures) : '[]'
            }

            if (testimonials.content_json && testimonials.content_json !== 'null') {
                testimonialsData.value = testimonials.content_json
            } else {
                testimonialsData.value = '[]'
            }
        }

    } catch (e) {
        console.error('Failed to fetch content', e)
        toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data konten', life: 3000 })
    } finally {
        loading.value = false
    }
}

// Watch context change
watch(context, () => fetchData(), { value: 'home' }) // Immediate handled by watcher if we set initial? No, watch works. But fetch called on mount if immediate true.

// Initial fetch
onMounted(() => {
    fetchData()
})

async function saveSection(section: 'hero' | 'sambutan' | 'features' | 'testimonials' | 'visimisi' | 'history') {
    loading.value = true
    try {
        const prefix = context.value === 'home' ? 'home' : context.value.replace('unit_', '')
        let key = `${prefix}_${section}`
        if (context.value === 'profil') {
             if (section === 'visimisi') key = 'profil_visimisi'
             if (section === 'history') key = 'profil_history'
        }
        
        let payload: any = { section_key: key }

        if (section === 'hero') Object.assign(payload, heroData)
        else if (section === 'sambutan') Object.assign(payload, sambutanData)
        else if (section === 'features') payload.content_json = featuresData.value
        else if (section === 'testimonials') payload.content_json = testimonialsData.value
        else if (section === 'visimisi') {
            payload.body = visiMisiData.visi
            payload.content_json = visiMisiData.misi
        }
        else if (section === 'history') {
            payload.body = historyData.body
        }

        await api.put(`/cms/content/${key}`, payload)
        
        toast.add({ severity: 'success', summary: 'Sukses', detail: `Konten ${section} berhasil disimpan`, life: 3000 })
    } catch (e) {
        console.error('Failed to save', e)
        toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan konten', life: 3000 })
    } finally {
        loading.value = false
    }
}
</script>
