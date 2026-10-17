<template>
  <div class="space-y-6 pb-12">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2.5">
          <span class="w-9 h-9 rounded-xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-lg shadow-sm">
            <i class="pi pi-check-square"></i>
          </span>
          Tugas Saya & Kanban Tim
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-sm mt-1">
          Papan kelola alur kerja delegasi tugas, approval pimpinan bertingkat, dan notifikasi email terintegrasi.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <Button 
          label="Segarkan" 
          icon="pi pi-refresh" 
          severity="secondary" 
          outlined 
          size="small" 
          :loading="loading" 
          @click="fetchTasks" 
        />
        <Button 
          label="Tambah Tugas" 
          icon="pi pi-plus" 
          class="p-button-primary shadow-sm" 
          size="small" 
          @click="openCreateModal" 
        />
      </div>
    </div>

    <!-- Quick Stats Summary Cards -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <div 
        class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm transition hover:shadow cursor-pointer"
        :class="{ 'ring-2 ring-slate-400': activeStatusFilter === '' }"
        @click="filterByStatus('')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-500">Semua Tugas</span>
          <i class="pi pi-inbox text-slate-400 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-slate-800 dark:text-white mt-1">{{ stats.total }}</p>
      </div>

      <div 
        class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm transition hover:shadow cursor-pointer"
        :class="{ 'ring-2 ring-slate-400': activeStatusFilter === 'antrian' }"
        @click="filterByStatus('antrian')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-500">Antrian</span>
          <i class="pi pi-hourglass text-slate-400 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-slate-700 dark:text-slate-200 mt-1">{{ stats.antrian }}</p>
      </div>

      <div 
        class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm transition hover:shadow cursor-pointer"
        :class="{ 'ring-2 ring-blue-500': activeStatusFilter === 'in_progress' }"
        @click="filterByStatus('in_progress')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-blue-600 dark:text-blue-400">Dikerjakan</span>
          <i class="pi pi-cog pi-spin text-blue-500 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ stats.in_progress }}</p>
      </div>

      <div 
        class="p-3.5 rounded-xl border border-indigo-200 dark:border-indigo-900/50 bg-indigo-50/40 dark:bg-indigo-950/20 shadow-sm transition hover:shadow cursor-pointer relative overflow-hidden"
        :class="{ 'ring-2 ring-indigo-500': activeStatusFilter === 'awaiting_approval' }"
        @click="filterByStatus('awaiting_approval')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-indigo-700 dark:text-indigo-300">Approval</span>
          <i class="pi pi-check-circle text-indigo-500 text-sm"></i>
        </div>
        <div class="flex items-baseline justify-between mt-1">
          <p class="text-2xl font-bold text-indigo-700 dark:text-indigo-300">{{ stats.awaiting_approval }}</p>
          <span v-if="stats.awaiting_my_approval > 0" class="text-[10px] font-semibold bg-indigo-600 text-white px-1.5 py-0.5 rounded-full" title="Menunggu approval Anda">
            {{ stats.awaiting_my_approval }} Anda
          </span>
        </div>
      </div>

      <div 
        class="p-3.5 rounded-xl border border-rose-200 dark:border-rose-900/50 bg-rose-50/40 dark:bg-rose-950/20 shadow-sm transition hover:shadow cursor-pointer"
        :class="{ 'ring-2 ring-rose-500': activeStatusFilter === 'need_revision' }"
        @click="filterByStatus('need_revision')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-rose-700 dark:text-rose-300">Butuh Revisi</span>
          <i class="pi pi-exclamation-triangle text-rose-500 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-rose-700 dark:text-rose-300 mt-1">{{ stats.need_revision }}</p>
      </div>

      <div 
        class="p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-900/50 bg-emerald-50/40 dark:bg-emerald-950/20 shadow-sm transition hover:shadow cursor-pointer"
        :class="{ 'ring-2 ring-emerald-500': activeStatusFilter === 'done' }"
        @click="filterByStatus('done')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-emerald-700 dark:text-emerald-300">Selesai</span>
          <i class="pi pi-verified text-emerald-500 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">{{ stats.done }}</p>
      </div>
    </div>

    <!-- Filter Bar & Scope Selector -->
    <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      <!-- Scope Tabs -->
      <div class="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-slate-800/80 rounded-lg text-xs overflow-x-auto">
        <button 
          v-for="tab in scopeTabs" 
          :key="tab.key"
          @click="setScope(tab.key)"
          class="px-3 py-1.5 rounded-md font-medium transition whitespace-nowrap"
          :class="scope === tab.key ? 'bg-white dark:bg-slate-700 text-emerald-700 dark:text-emerald-400 shadow-sm font-semibold' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'"
        >
          <i :class="[tab.icon, 'mr-1.5']"></i>
          {{ tab.label }}
          <span v-if="tab.key === 'my_approval' && stats.awaiting_my_approval > 0" class="ml-1 bg-indigo-500 text-white text-[10px] px-1 rounded-full font-bold">
            {{ stats.awaiting_my_approval }}
          </span>
        </button>
      </div>

      <!-- Search & Priority Filters -->
      <div class="flex items-center gap-2.5">
        <div class="relative w-full md:w-64">
          <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Cari tugas..." 
            class="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            @input="debounceSearch"
          />
        </div>

        <select 
          v-model="priorityFilter" 
          @change="fetchTasks"
          class="py-1.5 px-2.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
        >
          <option :value="null">Semua Prioritas</option>
          <option :value="1">🚨 P1 - Sangat Tinggi</option>
          <option :value="2">⚠️ P2 - Tinggi</option>
          <option :value="3">⚡ P3 - Sedang</option>
          <option :value="4">🌱 P4 - Rendah</option>
          <option :value="5">📋 P5 - Normal</option>
        </select>
      </div>
    </div>

    <!-- Kanban Board Grid (6 Kolom) -->
    <div class="overflow-x-auto pb-4">
      <div class="flex gap-4 min-w-[1380px] items-start">
        <!-- Loop 6 Columns -->
        <div 
          v-for="col in kanbanColumns" 
          :key="col.key"
          class="flex-1 min-w-[220px] rounded-2xl bg-slate-50/80 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 p-3 flex flex-col max-h-[820px]"
        >
          <!-- Column Header -->
          <div class="flex items-center justify-between pb-3 mb-2 border-b border-slate-200 dark:border-slate-800">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full" :class="col.dotClass"></span>
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                {{ col.title }}
              </h3>
            </div>
            <span class="text-[11px] font-bold px-2 py-0.5 rounded-full" :class="col.countBadgeClass">
              {{ getTasksForColumn(col.key).length }}
            </span>
          </div>

          <!-- Cards Scrollable Area -->
          <div class="flex-1 overflow-y-auto space-y-3 pr-1 pt-1 min-h-[200px]">
            <!-- Empty Placeholder -->
            <div 
              v-if="getTasksForColumn(col.key).length === 0" 
              class="h-32 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-xl flex flex-col items-center justify-center text-slate-400 text-xs text-center p-3"
            >
              <i :class="[col.icon, 'text-slate-300 dark:text-slate-700 text-lg mb-1.5']"></i>
              <span>Tidak ada tugas</span>
            </div>

            <!-- Task Card -->
            <div 
              v-for="task in getTasksForColumn(col.key)" 
              :key="task.id"
              class="group bg-white dark:bg-slate-800 rounded-xl p-3.5 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md hover:border-emerald-400 dark:hover:border-emerald-600 transition cursor-pointer relative"
              @click="openDetailModal(task)"
            >
              <!-- Card Top: Priority & Due Date -->
              <div class="flex items-center justify-between gap-2 mb-2">
                <span 
                  class="text-[10px] font-bold px-2 py-0.5 rounded-md flex items-center gap-1"
                  :class="getPriorityBadge(task.priority_level).class"
                >
                  {{ getPriorityBadge(task.priority_level).label }}
                </span>

                <!-- Deadline Badge -->
                <span 
                  v-if="task.deadline"
                  class="text-[10px] font-medium flex items-center gap-1 px-1.5 py-0.5 rounded"
                  :class="getDeadlineAlert(task.deadline, task.status)"
                  :title="formatDateTime(task.deadline)"
                >
                  <i class="pi pi-calendar text-[9px]"></i>
                  {{ formatShortDate(task.deadline) }}
                </span>
              </div>

              <!-- Card Title -->
              <h4 class="text-xs font-semibold text-slate-800 dark:text-slate-100 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition line-clamp-2 leading-snug">
                {{ task.title }}
              </h4>

              <!-- Card Excerpt -->
              <p v-if="task.description" class="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                {{ task.description }}
              </p>

              <!-- Card Footer: PIC & Approvers Status -->
              <div class="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-[11px]">
                <!-- PIC Avatar & Name -->
                <div class="flex items-center gap-1.5" :title="task.assignee ? `PIC: ${task.assignee.full_name}` : 'Belum ada PIC'">
                  <div 
                    class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold"
                    :class="task.assignee ? 'bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300' : 'bg-slate-200 dark:bg-slate-700 text-slate-400'"
                  >
                    {{ task.assignee ? getInitials(task.assignee.full_name) : '?' }}
                  </div>
                  <span class="text-slate-600 dark:text-slate-300 font-medium truncate max-w-[90px]">
                    {{ task.assignee ? task.assignee.full_name.split(' ')[0] : 'Unassigned' }}
                  </span>
                </div>

                <!-- Approvers Badge -->
                <div v-if="task.approvers && task.approvers.length > 0" class="flex items-center gap-1" :title="`${task.approvers.length} Approver`">
                  <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center gap-1">
                    <i class="pi pi-user-check text-[9px]"></i>
                    {{ getApprovedCount(task) }}/{{ task.approvers.length }}
                  </span>
                </div>
              </div>

              <!-- Quick Action Row (Hover or Direct Advance) -->
              <div class="mt-2.5 pt-2 border-t border-dashed border-slate-100 dark:border-slate-700/60 flex items-center justify-between gap-1" @click.stop>
                <span class="text-[10px] text-slate-400">Aksi Cepat:</span>
                <div class="flex items-center gap-1">
                  <!-- Button to move to previous or next stage -->
                  <Button 
                    v-if="col.nextAction"
                    :label="col.nextAction.label" 
                    :icon="col.nextAction.icon" 
                    size="small" 
                    text 
                    severity="secondary" 
                    class="!text-[10px] !py-0.5 !px-1.5 !h-auto text-emerald-600 dark:text-emerald-400 font-semibold"
                    @click="advanceTask(task, col.nextAction.nextStatus)"
                  />
                  <!-- Button to approve directly if awaiting approval -->
                  <Button 
                    v-if="col.key === 'awaiting_approval' && canApprove(task)"
                    label="Review" 
                    icon="pi pi-check" 
                    size="small" 
                    class="!text-[10px] !py-0.5 !px-2 !h-auto p-button-success"
                    @click="openDetailModal(task)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Buat / Edit Tugas -->
    <Dialog 
      v-model:visible="createModalVisible" 
      :header="editingTask ? 'Edit Tugas' : 'Tambah Tugas Baru'" 
      modal 
      class="w-full max-w-xl mx-4"
    >
      <form @submit.prevent="saveTask" class="space-y-4 pt-2">
        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Judul Tugas <span class="text-rose-500">*</span>
          </label>
          <input 
            v-model="form.title" 
            type="text" 
            placeholder="Contoh: Penyusunan Rencana Anggaran RAPBS 2026/2027" 
            required
            class="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Deskripsi & Instruksi Pengerjaan
          </label>
          <textarea 
            v-model="form.description" 
            rows="3" 
            placeholder="Jelaskan detail tugas, ruang lingkup, atau tautan berkas pendukung..."
            class="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          ></textarea>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Priority Level -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Tingkat Prioritas
            </label>
            <select 
              v-model="form.priority_level"
              class="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option :value="1">🚨 P1 - Sangat Tinggi (Urgent)</option>
              <option :value="2">⚠️ P2 - Tinggi</option>
              <option :value="3">⚡ P3 - Sedang</option>
              <option :value="4">🌱 P4 - Rendah</option>
              <option :value="5">📋 P5 - Normal</option>
            </select>
          </div>

          <!-- Deadline -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Tenggat Waktu (Deadline)
            </label>
            <input 
              v-model="form.deadline" 
              type="datetime-local" 
              class="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- PIC / Assignee -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Penanggung Jawab (PIC)
            </label>
            <select 
              v-model="form.assignee_id"
              class="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option :value="null">-- Pilih Penanggung Jawab --</option>
              <option v-for="u in usersList" :key="u.id" :value="u.id">
                {{ u.full_name }} ({{ u.role?.name || 'Staf' }})
              </option>
            </select>
            <p class="text-[11px] text-slate-400 mt-1">PIC akan menerima notifikasi email penugasan.</p>
          </div>

          <!-- Unit Terkait (Optional) -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Unit Terkait
            </label>
            <select 
              v-model="form.unit_id"
              class="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option :value="null">Semua Unit / Yayasan</option>
              <option v-for="u in unitsList" :key="u.id" :value="u.id">{{ u.name }}</option>
            </select>
          </div>
        </div>

        <!-- Approvers Selection -->
        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Pimpinan Approver / Reviewer (Pilihan)
          </label>
          <div class="border border-slate-200 dark:border-slate-700 rounded-lg p-3 max-h-36 overflow-y-auto space-y-1.5 bg-slate-50/50 dark:bg-slate-800/50">
            <label 
              v-for="u in approverCandidates" 
              :key="u.id" 
              class="flex items-center gap-2 text-xs text-slate-700 dark:text-slate-300 hover:text-emerald-600 cursor-pointer"
            >
              <input 
                type="checkbox" 
                :value="u.id" 
                v-model="form.approver_ids" 
                class="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
              />
              <span class="font-medium">{{ u.full_name }}</span>
              <span class="text-[11px] text-slate-400">({{ u.role?.name }})</span>
            </label>
          </div>
          <p class="text-[11px] text-slate-400 mt-1">Tugas akan memerlukan persetujuan dari approver yang dipilih sebelum dinyatakan selesai.</p>
        </div>

        <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-200 dark:border-slate-700">
          <Button label="Batal" severity="secondary" text size="small" @click="createModalVisible = false" />
          <Button :label="editingTask ? 'Simpan Perubahan' : 'Buat Tugas'" icon="pi pi-check" size="small" type="submit" :loading="saving" />
        </div>
      </form>
    </Dialog>

    <!-- Modal Detail Tugas, Approvals & Riwayat -->
    <Dialog 
      v-model:visible="detailModalVisible" 
      header="Detail Tugas" 
      modal 
      class="w-full max-w-2xl mx-4"
    >
      <div v-if="selectedTask" class="space-y-5 pt-1">
        <!-- Top Status & Priority Bar -->
        <div class="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold px-2.5 py-1 rounded-md" :class="getStatusBadge(selectedTask.status).class">
              {{ getStatusBadge(selectedTask.status).label }}
            </span>
            <span class="text-xs font-bold px-2.5 py-1 rounded-md" :class="getPriorityBadge(selectedTask.priority_level).class">
              {{ getPriorityBadge(selectedTask.priority_level).label }}
            </span>
          </div>

          <!-- Deadline -->
          <div v-if="selectedTask.deadline" class="text-xs font-medium text-slate-600 dark:text-slate-300 flex items-center gap-1.5">
            <i class="pi pi-calendar text-slate-400"></i>
            Deadline: <span class="font-bold text-rose-600">{{ formatDateTime(selectedTask.deadline) }}</span>
          </div>
        </div>

        <!-- Title & Description -->
        <div>
          <h2 class="text-lg font-bold text-slate-800 dark:text-white leading-snug">
            {{ selectedTask.title }}
          </h2>
          <p v-if="selectedTask.description" class="text-xs text-slate-600 dark:text-slate-300 mt-2 whitespace-pre-line leading-relaxed bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-100 dark:border-slate-700">
            {{ selectedTask.description }}
          </p>
        </div>

        <!-- Assignee & Creator Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div class="p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/60">
            <span class="text-slate-400 block mb-1">Penanggung Jawab (PIC):</span>
            <div class="flex items-center gap-2 font-semibold text-slate-800 dark:text-slate-200">
              <i class="pi pi-user text-emerald-600"></i>
              <span>{{ selectedTask.assignee?.full_name || 'Belum ditentukan' }}</span>
            </div>
            <span class="text-[11px] text-slate-400 block mt-0.5">{{ selectedTask.assignee?.email || '' }}</span>
          </div>

          <div class="p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/60">
            <span class="text-slate-400 block mb-1">Pembuat Tugas:</span>
            <div class="flex items-center gap-2 font-semibold text-slate-800 dark:text-slate-200">
              <i class="pi pi-user-edit text-blue-600"></i>
              <span>{{ selectedTask.creator?.full_name || 'Sistem' }}</span>
            </div>
            <span class="text-[11px] text-slate-400 block mt-0.5">Dibuat: {{ formatDateTime(selectedTask.created_at) }}</span>
          </div>
        </div>

        <!-- Approvers Status Checklist -->
        <div v-if="selectedTask.approvers && selectedTask.approvers.length > 0" class="border border-slate-200 dark:border-slate-700 rounded-xl p-3.5 bg-slate-50/50 dark:bg-slate-800/40">
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-2.5 flex items-center gap-1.5">
            <i class="pi pi-shield text-indigo-500"></i>
            Persetujuan Pimpinan (Approvers)
          </h4>
          <div class="space-y-2">
            <div 
              v-for="link in selectedTask.approvers" 
              :key="link.id"
              class="flex items-center justify-between p-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs"
            >
              <div class="flex items-center gap-2">
                <i 
                  :class="link.status === 'approved' ? 'pi pi-check-circle text-emerald-600' : (link.status === 'revision_requested' ? 'pi pi-exclamation-circle text-rose-600' : 'pi pi-clock text-amber-500')"
                ></i>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ link.user?.full_name }}</span>
                <span class="text-[10px] text-slate-400">({{ link.user?.role?.name }})</span>
              </div>
              <div class="flex items-center gap-2">
                <span 
                  class="text-[10px] font-semibold px-2 py-0.5 rounded"
                  :class="link.status === 'approved' ? 'bg-emerald-100 text-emerald-700' : (link.status === 'revision_requested' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700')"
                >
                  {{ link.status === 'approved' ? 'Disetujui' : (link.status === 'revision_requested' ? 'Butuh Revisi' : 'Menunggu') }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Approver Review Action Box (Only if awaiting approval and user is approver/leadership) -->
        <div 
          v-if="selectedTask.status === 'awaiting_approval' && canApprove(selectedTask)" 
          class="p-4 rounded-xl border-2 border-indigo-200 dark:border-indigo-900 bg-indigo-50/30 dark:bg-indigo-950/20 space-y-3"
        >
          <div class="flex items-center gap-2 text-indigo-800 dark:text-indigo-300 font-bold text-xs">
            <i class="pi pi-bell text-indigo-600"></i>
            Tugas ini menunggu review & persetujuan Anda:
          </div>
          <textarea 
            v-model="approvalNote" 
            rows="2" 
            placeholder="Tuliskan catatan persetujuan atau catatan revisi..." 
            class="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          ></textarea>
          <div class="flex items-center justify-end gap-2">
            <Button 
              label="Minta Revisi" 
              icon="pi pi-times" 
              severity="danger" 
              outlined 
              size="small" 
              :loading="approving"
              @click="submitApproval(false)" 
            />
            <Button 
              label="Setujui Tugas (Approve)" 
              icon="pi pi-check" 
              severity="success" 
              size="small" 
              :loading="approving"
              @click="submitApproval(true)" 
            />
          </div>
        </div>

        <!-- Manual Move Stage & Edit Actions -->
        <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-200 dark:border-slate-700">
          <div class="flex items-center gap-2 text-xs">
            <span class="text-slate-500 font-medium">Pindah Status:</span>
            <select 
              :value="selectedTask.status"
              @change="onManualStatusChange($event)"
              class="px-2.5 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none"
            >
              <option value="antrian">Antrian Tugas</option>
              <option value="prioritas">Prioritas Tugas</option>
              <option value="in_progress">Sedang Dikerjakan</option>
              <option value="awaiting_approval">Menunggu Approval</option>
              <option value="need_revision">Butuh Revisi</option>
              <option value="done">Selesai</option>
            </select>
          </div>

          <div class="flex items-center gap-2">
            <Button 
              v-if="canEditOrDelete(selectedTask)" 
              label="Hapus" 
              icon="pi pi-trash" 
              severity="danger" 
              text 
              size="small" 
              @click="deleteTask(selectedTask.id)" 
            />
            <Button 
              v-if="canEditOrDelete(selectedTask)" 
              label="Edit" 
              icon="pi pi-pencil" 
              severity="secondary" 
              outlined 
              size="small" 
              @click="editTask(selectedTask)" 
            />
          </div>
        </div>

        <!-- Audit Trail / Riwayat Perubahan -->
        <div class="border-t border-slate-200 dark:border-slate-700 pt-4">
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-3 flex items-center gap-1.5">
            <i class="pi pi-history"></i>
            Riwayat Aktivitas & Perubahan
          </h4>
          <div class="space-y-3 max-h-48 overflow-y-auto pr-1">
            <div 
              v-for="h in selectedTask.histories" 
              :key="h.id"
              class="text-xs flex items-start gap-2.5 border-l-2 border-emerald-400 pl-3 py-1"
            >
              <div class="flex-1">
                <div class="flex items-center justify-between">
                  <span class="font-semibold text-slate-800 dark:text-slate-200">{{ h.changed_by?.full_name || 'Sistem' }}</span>
                  <span class="text-[10px] text-slate-400">{{ formatDateTime(h.created_at) }}</span>
                </div>
                <p class="text-slate-500 dark:text-slate-400 mt-0.5 text-[11px]">{{ h.comment }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'

definePageMeta({
  layout: 'dashboard'
})

const toast = useToast()
const authStore = useAuthStore()
const api = useApi()

// States
const tasks = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const approving = ref(false)
const scope = ref('all')
const activeStatusFilter = ref('')
const priorityFilter = ref<number | null>(null)
const searchQuery = ref('')
const stats = ref({
  total: 0,
  antrian: 0,
  prioritas: 0,
  in_progress: 0,
  awaiting_approval: 0,
  need_revision: 0,
  done: 0,
  overdue: 0,
  my_tasks: 0,
  awaiting_my_approval: 0
})

const usersList = ref<any[]>([])
const unitsList = ref<any[]>([])
const createModalVisible = ref(false)
const detailModalVisible = ref(false)
const editingTask = ref<any | null>(null)
const selectedTask = ref<any | null>(null)
const approvalNote = ref('')

const form = ref({
  title: '',
  description: '',
  priority_level: 5,
  assignee_id: null as number | null,
  unit_id: null as number | null,
  deadline: '',
  approver_ids: [] as number[]
})

// Scope Tabs
const scopeTabs = [
  { key: 'all', label: 'Semua Tugas', icon: 'pi pi-list' },
  { key: 'my_assigned', label: 'Tugas Saya', icon: 'pi pi-user' },
  { key: 'my_created', label: 'Dibuat Saya', icon: 'pi pi-user-edit' },
  { key: 'my_approval', label: 'Menunggu Approval', icon: 'pi pi-check-circle' }
]

// 6 Kanban Columns Configuration
const kanbanColumns = [
  {
    key: 'antrian',
    title: 'Antrian Tugas',
    icon: 'pi pi-hourglass',
    dotClass: 'bg-slate-400',
    countBadgeClass: 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200',
    nextAction: { label: 'Prioritaskan', icon: 'pi pi-arrow-right', nextStatus: 'prioritas' }
  },
  {
    key: 'prioritas',
    title: 'Prioritas Tugas',
    icon: 'pi pi-star',
    dotClass: 'bg-amber-500',
    countBadgeClass: 'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300',
    nextAction: { label: 'Kerjakan', icon: 'pi pi-play', nextStatus: 'in_progress' }
  },
  {
    key: 'in_progress',
    title: 'Sedang Dikerjakan',
    icon: 'pi pi-cog',
    dotClass: 'bg-blue-500',
    countBadgeClass: 'bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300',
    nextAction: { label: 'Minta Approval', icon: 'pi pi-send', nextStatus: 'awaiting_approval' }
  },
  {
    key: 'awaiting_approval',
    title: 'Approval / Feedback',
    icon: 'pi pi-check-circle',
    dotClass: 'bg-indigo-500',
    countBadgeClass: 'bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300',
    nextAction: null
  },
  {
    key: 'need_revision',
    title: 'Butuh Revisi',
    icon: 'pi pi-exclamation-triangle',
    dotClass: 'bg-rose-500',
    countBadgeClass: 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300',
    nextAction: { label: 'Perbaiki', icon: 'pi pi-refresh', nextStatus: 'in_progress' }
  },
  {
    key: 'done',
    title: 'Selesai',
    icon: 'pi pi-verified',
    dotClass: 'bg-emerald-500',
    countBadgeClass: 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300',
    nextAction: null
  }
]

// Fetch Tasks
async function fetchTasks() {
  loading.value = true
  try {
    let url = `/tasks?scope=${scope.value}`
    if (activeStatusFilter.value) {
      url += `&status=${activeStatusFilter.value}`
    }
    if (priorityFilter.value) {
      url += `&priority_level=${priorityFilter.value}`
    }
    if (searchQuery.value.trim()) {
      url += `&search=${encodeURIComponent(searchQuery.value.trim())}`
    }

    const [tasksRes, statsRes] = await Promise.all([
      api.get<any[]>(url),
      api.get<any>('/tasks/stats/summary')
    ])

    tasks.value = tasksRes || []
    if (statsRes) stats.value = statsRes
  } catch (e: any) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Memuat Data',
      detail: e?.message || 'Tidak dapat mengambil daftar tugas',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

// Fetch Auxiliary Users & Units for Modal
async function loadAuxiliaryData() {
  try {
    const [uRes, unitsRes] = await Promise.all([
      api.get<any[]>('/users?limit=200').catch(() => []),
      api.get<any[]>('/public/units').catch(() => [])
    ])
    usersList.value = uRes || []
    unitsList.value = unitsRes || []
  } catch (err) {
    console.error('Error loading aux data:', err)
  }
}

// Approver candidates (filter leadership / kabid / kepsek / superadmin)
const approverCandidates = computed(() => {
  return usersList.value.filter(u => {
    const code = u.role?.code || ''
    return ['superadmin', 'kabid_umum', 'kabid_keuangan', 'kepala_unit', 'wakil_kepala', 'tu_yayasan'].includes(code)
  })
})

function getTasksForColumn(colKey: string) {
  return tasks.value.filter(t => t.status === colKey)
}

function setScope(newScope: string) {
  scope.value = newScope
  fetchTasks()
}

function filterByStatus(status: string) {
  if (activeStatusFilter.value === status) {
    activeStatusFilter.value = ''
  } else {
    activeStatusFilter.value = status
  }
  fetchTasks()
}

let searchTimer: any = null
function debounceSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchTasks()
  }, 350)
}

// Card details & transitions
function openDetailModal(task: any) {
  selectedTask.value = task
  approvalNote.value = ''
  detailModalVisible.value = true
}

function openCreateModal() {
  editingTask.value = null
  form.value = {
    title: '',
    description: '',
    priority_level: 5,
    assignee_id: null,
    unit_id: null,
    deadline: '',
    approver_ids: []
  }
  createModalVisible.value = true
}

function editTask(task: any) {
  detailModalVisible.value = false
  editingTask.value = task
  form.value = {
    title: task.title,
    description: task.description || '',
    priority_level: task.priority_level,
    assignee_id: task.assignee_id,
    unit_id: task.unit_id,
    deadline: task.deadline ? task.deadline.slice(0, 16) : '',
    approver_ids: task.approvers ? task.approvers.map((a: any) => a.user_id) : []
  }
  createModalVisible.value = true
}

async function saveTask() {
  saving.value = true
  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      priority_level: form.value.priority_level,
      assignee_id: form.value.assignee_id,
      unit_id: form.value.unit_id,
      deadline: form.value.deadline ? new Date(form.value.deadline).toISOString() : null,
      approver_ids: form.value.approver_ids
    }

    if (editingTask.value) {
      await api.patch(`/tasks/${editingTask.value.id}`, payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Tugas berhasil diperbarui', life: 3000 })
    } else {
      await api.post('/tasks', payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Tugas baru berhasil dibuat & email notifikasi dikirimkan', life: 3000 })
    }

    createModalVisible.value = false
    fetchTasks()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal Menyimpan', detail: e?.message || 'Terjadi kesalahan', life: 4000 })
  } finally {
    saving.value = false
  }
}

async function advanceTask(task: any, nextStatus: string) {
  try {
    await api.patch(`/tasks/${task.id}`, { status: nextStatus })
    toast.add({ severity: 'success', summary: 'Status Diperbarui', detail: `Tugas dipindahkan`, life: 2500 })
    fetchTasks()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e?.message || 'Gagal mengubah status', life: 3000 })
  }
}

async function onManualStatusChange(event: any) {
  if (!selectedTask.value) return
  const newStatus = event.target.value
  try {
    await api.patch(`/tasks/${selectedTask.value.id}`, { status: newStatus })
    selectedTask.value.status = newStatus
    toast.add({ severity: 'success', summary: 'Status Diperbarui', detail: 'Status tugas berhasil diubah', life: 2500 })
    fetchTasks()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e?.message || 'Gagal mengubah status', life: 3000 })
  }
}

async function submitApproval(approved: boolean) {
  if (!selectedTask.value) return
  approving.value = true
  try {
    const res = await api.post(`/tasks/${selectedTask.value.id}/approve`, {
      approved,
      note: approvalNote.value.trim() || undefined
    })
    selectedTask.value = res
    toast.add({
      severity: approved ? 'success' : 'warn',
      summary: approved ? 'Tugas Disetujui' : 'Revisi Diminta',
      detail: approved ? 'Tugas berhasil disetujui' : 'Catatan revisi dikirimkan ke PIC',
      life: 3000
    })
    fetchTasks()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e?.message || 'Gagal memproses approval', life: 3000 })
  } finally {
    approving.value = false
  }
}

async function deleteTask(taskId: number) {
  if (!confirm('Apakah Anda yakin ingin menghapus tugas ini?')) return
  try {
    await api.delete(`/tasks/${taskId}`)
    toast.add({ severity: 'success', summary: 'Dihapus', detail: 'Tugas berhasil dihapus', life: 2500 })
    detailModalVisible.value = false
    fetchTasks()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e?.message || 'Gagal menghapus tugas', life: 3000 })
  }
}

// Permissions Helper
function canApprove(task: any) {
  const currentUserId = authStore.user?.id
  const roleCode = authStore.user?.role?.code || ''
  const isLeader = ['superadmin', 'kabid_umum', 'kabid_keuangan', 'kepala_unit'].includes(roleCode)
  const isApprover = task.approvers?.some((a: any) => a.user_id === currentUserId)
  return isApprover || isLeader
}

function canEditOrDelete(task: any) {
  const currentUserId = authStore.user?.id
  const roleCode = authStore.user?.role?.code || ''
  const isLeader = ['superadmin', 'kabid_umum', 'kabid_keuangan'].includes(roleCode)
  return isLeader || task.creator_id === currentUserId
}

function getApprovedCount(task: any) {
  if (!task.approvers) return 0
  return task.approvers.filter((a: any) => a.status === 'approved').length
}

// Formatting helpers
function getPriorityBadge(lvl: number) {
  switch (lvl) {
    case 1: return { label: '🚨 Urgent', class: 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300' }
    case 2: return { label: '⚠️ Tinggi', class: 'bg-orange-100 text-orange-700 dark:bg-orange-950/60 dark:text-orange-300' }
    case 3: return { label: '⚡ Sedang', class: 'bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300' }
    case 4: return { label: '🌱 Rendah', class: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300' }
    default: return { label: '📋 Normal', class: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300' }
  }
}

function getStatusBadge(st: string) {
  switch (st) {
    case 'antrian': return { label: 'Antrian Tugas', class: 'bg-slate-100 text-slate-700' }
    case 'prioritas': return { label: 'Prioritas Tugas', class: 'bg-amber-100 text-amber-700' }
    case 'in_progress': return { label: 'Sedang Dikerjakan', class: 'bg-blue-100 text-blue-700' }
    case 'awaiting_approval': return { label: 'Menunggu Approval', class: 'bg-indigo-100 text-indigo-700' }
    case 'need_revision': return { label: 'Butuh Revisi', class: 'bg-rose-100 text-rose-700' }
    case 'done': return { label: 'Selesai', class: 'bg-emerald-100 text-emerald-700' }
    default: return { label: st, class: 'bg-slate-100 text-slate-700' }
  }
}

function getDeadlineAlert(deadlineStr: string, status: string) {
  if (status === 'done') return 'bg-slate-100 text-slate-500 dark:bg-slate-800'
  const dl = new Date(deadlineStr).getTime()
  const now = Date.now()
  if (dl < now) {
    return 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 font-bold'
  }
  if (dl - now < 48 * 3600 * 1000) {
    return 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 font-semibold'
  }
  return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
}

function formatShortDate(dtStr: string) {
  if (!dtStr) return ''
  const d = new Date(dtStr)
  return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })
}

function formatDateTime(dtStr: string) {
  if (!dtStr) return '-'
  const d = new Date(dtStr)
  return d.toLocaleString('id-ID', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function getInitials(name: string) {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

onMounted(() => {
  fetchTasks()
  loadAuxiliaryData()
})
</script>

<style scoped>
/* Scrollbar halus */
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
