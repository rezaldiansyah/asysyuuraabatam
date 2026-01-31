<template>
  <NuxtLayout name="dashboard">
    <div class="space-y-6">
      <!-- Page Header -->
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Keuangan & Akuntansi</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola tagihan, beasiswa, pembayaran, dan pembukuan.</p>
      </div>

      <!-- Summary Cards -->
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 border shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-500">Tagihan Aktif</span>
            <i class="pi pi-dollar text-slate-400"></i>
          </div>
          <p class="text-2xl font-bold text-slate-800 dark:text-white mt-2">
            Rp {{ totalUnpaid.toLocaleString('id-ID') }}
          </p>
          <p class="text-xs text-slate-500 mt-1">Potensi pendapatan tagihan unpaid</p>
        </div>
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 border shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-500">Jurnal Transaksi</span>
            <i class="pi pi-book text-slate-400"></i>
          </div>
          <p class="text-2xl font-bold text-slate-800 dark:text-white mt-2">{{ journals.length }}</p>
          <p class="text-xs text-slate-500 mt-1">Entri jurnal tercatat</p>
        </div>
      </div>

      <!-- Tabs -->
      <TabView>
        <!-- Tab: Daftar Tagihan -->
        <TabPanel header="Daftar Tagihan">
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-medium">Manajemen Tagihan</h3>
              <div class="flex gap-2">
                <Button severity="success" size="small" @click="showBillDialog = true">
                  <i class="pi pi-plus mr-2"></i>Buat Tagihan
                </Button>
              </div>
            </div>
            <DataTable :value="bills" :loading="loadingBills" stripedRows paginator :rows="10" class="p-datatable-sm">
              <template #empty>
                <div class="text-center py-8 text-slate-500">Belum ada tagihan.</div>
              </template>
              <Column field="id" header="ID" style="width: 70px">
                <template #body="{ data }"><span class="font-mono text-xs">{{ data.id }}</span></template>
              </Column>
              <Column header="Siswa">
                <template #body="{ data }">{{ data.student?.full_name || `Siswa #${data.student_id}` }}</template>
              </Column>
              <Column field="title" header="Keterangan" />
              <Column header="Nominal">
                <template #body="{ data }">Rp {{ data.amount.toLocaleString('id-ID') }}</template>
              </Column>
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column header="Tanggal">
                <template #body="{ data }">{{ new Date(data.created_at).toLocaleDateString('id-ID') }}</template>
              </Column>
              <Column header="Aksi" style="width: 100px">
                <template #body="{ data }">
                  <Button v-if="data.status !== 'PAID'" icon="pi pi-credit-card" severity="success" size="small" text rounded title="Bayar" @click="openPaymentDialog(data)" />
                </template>
              </Column>
            </DataTable>
          </div>
        </TabPanel>

        <!-- Tab: Data Beasiswa -->
        <TabPanel header="Data Beasiswa">
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-medium">Master Data Beasiswa</h3>
              <Button severity="success" size="small" @click="showScholarshipDialog = true">
                <i class="pi pi-plus mr-2"></i>Tambah Beasiswa
              </Button>
            </div>
            <DataTable :value="scholarships" :loading="loadingScholarships" stripedRows class="p-datatable-sm">
              <template #empty>
                <div class="text-center py-8 text-slate-500">Belum ada data beasiswa.</div>
              </template>
              <Column field="name" header="Nama Beasiswa" />
              <Column field="type" header="Tipe Potongan">
                <template #body="{ data }"><Tag :value="data.type" severity="info" /></template>
              </Column>
              <Column header="Nilai">
                <template #body="{ data }">
                  {{ data.type === 'FIXED' ? `Rp ${data.value.toLocaleString('id-ID')}` : `${data.value}%` }}
                </template>
              </Column>
              <Column field="is_active" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.is_active ? 'Aktif' : 'Non-Aktif'" :severity="data.is_active ? 'success' : 'secondary'" />
                </template>
              </Column>
            </DataTable>
          </div>
        </TabPanel>

        <!-- Tab: Daftar Akun (CoA) -->
        <TabPanel header="Daftar Akun (CoA)">
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-medium">Chart of Accounts (CoA)</h3>
              <Button severity="success" size="small" @click="showAccountDialog = true">
                <i class="pi pi-plus mr-2"></i>Tambah Akun
              </Button>
            </div>
            <DataTable :value="accounts" :loading="loadingAccounts" stripedRows class="p-datatable-sm">
              <template #empty>
                <div class="text-center py-8 text-slate-500">Belum ada akun.</div>
              </template>
              <Column field="code" header="Kode Akun" />
              <Column field="name" header="Nama Akun" />
              <Column field="type" header="Tipe">
                <template #body="{ data }"><Tag :value="data.type" severity="secondary" /></template>
              </Column>
            </DataTable>
          </div>
        </TabPanel>

        <!-- Tab: Jurnal Umum -->
        <TabPanel header="Jurnal Umum">
          <div class="space-y-4">
            <h3 class="text-lg font-medium">Jurnal Umum</h3>
            <DataTable :value="journals" :loading="loadingJournals" stripedRows class="p-datatable-sm">
              <template #empty>
                <div class="text-center py-8 text-slate-500">Belum ada jurnal.</div>
              </template>
              <Column header="Tanggal">
                <template #body="{ data }">{{ new Date(data.date).toLocaleDateString('id-ID') }}</template>
              </Column>
              <Column field="reference_id" header="No. Ref" />
              <Column field="description" header="Keterangan" />
            </DataTable>
          </div>
        </TabPanel>

        <!-- Tab: Master Kategori -->
        <TabPanel header="Master Kategori">
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-medium">Jenis Pembayaran</h3>
              <Button severity="success" size="small" @click="showCategoryDialog = true">
                <i class="pi pi-plus mr-2"></i>Tambah Kategori
              </Button>
            </div>
            <DataTable :value="categories" :loading="loadingCategories" stripedRows class="p-datatable-sm">
              <template #empty>
                <div class="text-center py-8 text-slate-500">Belum ada kategori.</div>
              </template>
              <Column field="name" header="Nama Kategori" />
              <Column field="type" header="Tipe" />
              <Column header="Nominal Default">
                <template #body="{ data }">Rp {{ data.amount.toLocaleString('id-ID') }}</template>
              </Column>
              <Column header="Akun Pendapatan">
                <template #body="{ data }">{{ data.income_account_id ? `Akun #${data.income_account_id}` : '-' }}</template>
              </Column>
            </DataTable>
          </div>
        </TabPanel>
      </TabView>

      <!-- Bill Dialog -->
      <Dialog v-model:visible="showBillDialog" header="Buat Tagihan Baru" :style="{ width: '500px' }" modal>
        <form @submit.prevent="submitBill" class="space-y-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Siswa</label>
            <Select v-model="billForm.student_id" :options="students" optionLabel="full_name" optionValue="id" placeholder="Pilih siswa" class="w-full" filter />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Kategori</label>
            <Select v-model="billForm.category_id" :options="categories" optionLabel="name" optionValue="id" placeholder="Pilih kategori" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Keterangan</label>
            <InputText v-model="billForm.title" placeholder="SPP Januari 2026" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nominal</label>
            <InputNumber v-model="billForm.amount" mode="currency" currency="IDR" locale="id-ID" class="w-full" />
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showBillDialog = false" />
            <Button type="submit" label="Simpan" :loading="submitting" />
          </div>
        </form>
      </Dialog>

      <!-- Category Dialog -->
      <Dialog v-model:visible="showCategoryDialog" header="Tambah Kategori" :style="{ width: '450px' }" modal>
        <form @submit.prevent="submitCategory" class="space-y-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nama Kategori</label>
            <InputText v-model="categoryForm.name" placeholder="SPP Bulanan" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Tipe</label>
            <Select v-model="categoryForm.type" :options="['MONTHLY', 'YEARLY', 'ONE_TIME']" placeholder="Pilih tipe" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nominal Default</label>
            <InputNumber v-model="categoryForm.amount" mode="currency" currency="IDR" locale="id-ID" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Akun Pendapatan</label>
            <Select v-model="categoryForm.income_account_id" :options="accounts" optionLabel="name" optionValue="id" placeholder="Pilih akun" class="w-full" />
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showCategoryDialog = false" />
            <Button type="submit" label="Simpan" :loading="submitting" />
          </div>
        </form>
      </Dialog>

      <!-- Account Dialog -->
      <Dialog v-model:visible="showAccountDialog" header="Tambah Akun" :style="{ width: '400px' }" modal>
        <form @submit.prevent="submitAccount" class="space-y-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Kode Akun</label>
            <InputText v-model="accountForm.code" placeholder="1101" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nama Akun</label>
            <InputText v-model="accountForm.name" placeholder="Kas" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Tipe</label>
            <Select v-model="accountForm.type" :options="['ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE']" placeholder="Pilih tipe" class="w-full" />
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showAccountDialog = false" />
            <Button type="submit" label="Simpan" :loading="submitting" />
          </div>
        </form>
      </Dialog>

      <!-- Scholarship Dialog -->
      <Dialog v-model:visible="showScholarshipDialog" header="Tambah Beasiswa" :style="{ width: '400px' }" modal>
        <form @submit.prevent="submitScholarship" class="space-y-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nama Beasiswa</label>
            <InputText v-model="scholarshipForm.name" placeholder="Beasiswa Prestasi" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Tipe Potongan</label>
            <Select v-model="scholarshipForm.type" :options="['FIXED', 'PERCENTAGE']" placeholder="Pilih tipe" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nilai</label>
            <InputNumber v-model="scholarshipForm.value" :mode="scholarshipForm.type === 'PERCENTAGE' ? 'decimal' : 'currency'" :currency="scholarshipForm.type === 'FIXED' ? 'IDR' : undefined" locale="id-ID" class="w-full" />
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showScholarshipDialog = false" />
            <Button type="submit" label="Simpan" :loading="submitting" />
          </div>
        </form>
      </Dialog>

      <!-- Payment Dialog -->
      <Dialog v-model:visible="showPaymentDialog" header="Proses Pembayaran" :style="{ width: '450px' }" modal>
        <div v-if="selectedBill" class="space-y-4">
          <div class="bg-slate-100 dark:bg-slate-700 p-4 rounded-lg">
            <p><strong>Siswa:</strong> {{ selectedBill.student?.full_name || `#${selectedBill.student_id}` }}</p>
            <p><strong>Tagihan:</strong> {{ selectedBill.title }}</p>
            <p><strong>Nominal:</strong> Rp {{ selectedBill.amount.toLocaleString('id-ID') }}</p>
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Jumlah Bayar</label>
            <InputNumber v-model="paymentForm.amount" mode="currency" currency="IDR" locale="id-ID" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Metode Pembayaran</label>
            <Select v-model="paymentForm.method" :options="['CASH', 'TRANSFER', 'QRIS']" placeholder="Pilih metode" class="w-full" />
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showPaymentDialog = false" />
            <Button label="Proses" :loading="submitting" @click="submitPayment" />
          </div>
        </div>
      </Dialog>

      <ConfirmDialog />
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: false })

const api = useApi()
const toast = useToast()

// Data
const bills = ref<any[]>([])
const categories = ref<any[]>([])
const accounts = ref<any[]>([])
const journals = ref<any[]>([])
const scholarships = ref<any[]>([])
const students = ref<any[]>([])

// Loading
const loadingBills = ref(false)
const loadingCategories = ref(false)
const loadingAccounts = ref(false)
const loadingJournals = ref(false)
const loadingScholarships = ref(false)
const submitting = ref(false)

// Dialogs
const showBillDialog = ref(false)
const showCategoryDialog = ref(false)
const showAccountDialog = ref(false)
const showScholarshipDialog = ref(false)
const showPaymentDialog = ref(false)
const selectedBill = ref<any>(null)

// Forms
const billForm = reactive({ student_id: null, category_id: null, title: '', amount: 0 })
const categoryForm = reactive({ name: '', type: 'MONTHLY', amount: 0, income_account_id: null })
const accountForm = reactive({ code: '', name: '', type: 'ASSET' })
const scholarshipForm = reactive({ name: '', type: 'FIXED', value: 0 })
const paymentForm = reactive({ amount: 0, method: 'CASH' })

// Computed
const totalUnpaid = computed(() => {
  return bills.value
    .filter((b) => b.status === 'UNPAID')
    .reduce((acc, curr) => acc + (curr.amount || 0), 0)
})

// Helpers
function getStatusSeverity(status: string) {
  if (status === 'PAID') return 'success'
  if (status === 'PARTIAL') return 'warn'
  return 'danger'
}

function openPaymentDialog(bill: any) {
  selectedBill.value = bill
  paymentForm.amount = bill.amount
  paymentForm.method = 'CASH'
  showPaymentDialog.value = true
}

// Fetch functions
async function fetchBills() {
  loadingBills.value = true
  try { bills.value = await api.get('/finance/bills') } catch (e) { console.error(e) } finally { loadingBills.value = false }
}
async function fetchCategories() {
  loadingCategories.value = true
  try { categories.value = await api.get('/finance/categories') } catch (e) { console.error(e) } finally { loadingCategories.value = false }
}
async function fetchAccounts() {
  loadingAccounts.value = true
  try { accounts.value = await api.get('/finance/accounts') } catch (e) { console.error(e) } finally { loadingAccounts.value = false }
}
async function fetchJournals() {
  loadingJournals.value = true
  try { journals.value = await api.get('/finance/journals') } catch (e) { console.error(e) } finally { loadingJournals.value = false }
}
async function fetchScholarships() {
  loadingScholarships.value = true
  try { scholarships.value = await api.get('/finance/scholarships') } catch (e) { console.error(e) } finally { loadingScholarships.value = false }
}
async function fetchStudents() {
  try { students.value = await api.get('/academic/students') } catch (e) { console.error(e) }
}

// Submit functions
async function submitBill() {
  submitting.value = true
  try {
    await api.post('/finance/bills', billForm)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Tagihan dibuat', life: 3000 })
    showBillDialog.value = false
    fetchBills()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal membuat tagihan', life: 3000 })
  } finally { submitting.value = false }
}

async function submitCategory() {
  submitting.value = true
  try {
    await api.post('/finance/categories', categoryForm)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Kategori ditambahkan', life: 3000 })
    showCategoryDialog.value = false
    fetchCategories()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menambah kategori', life: 3000 })
  } finally { submitting.value = false }
}

async function submitAccount() {
  submitting.value = true
  try {
    await api.post('/finance/accounts', accountForm)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Akun ditambahkan', life: 3000 })
    showAccountDialog.value = false
    fetchAccounts()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menambah akun', life: 3000 })
  } finally { submitting.value = false }
}

async function submitScholarship() {
  submitting.value = true
  try {
    await api.post('/finance/scholarships', scholarshipForm)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Beasiswa ditambahkan', life: 3000 })
    showScholarshipDialog.value = false
    fetchScholarships()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menambah beasiswa', life: 3000 })
  } finally { submitting.value = false }
}

async function submitPayment() {
  if (!selectedBill.value) return
  submitting.value = true
  try {
    await api.post(`/finance/bills/${selectedBill.value.id}/pay`, paymentForm)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pembayaran berhasil', life: 3000 })
    showPaymentDialog.value = false
    fetchBills()
    fetchJournals()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Pembayaran gagal', life: 3000 })
  } finally { submitting.value = false }
}

onMounted(() => {
  fetchBills()
  fetchCategories()
  fetchAccounts()
  fetchJournals()
  fetchScholarships()
  fetchStudents()
})
</script>
