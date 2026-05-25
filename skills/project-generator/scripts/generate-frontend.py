#!/usr/bin/env python3
"""
Frontend Code Generator for Vue 3 + TypeScript with Tech Stack Selection
Generates Vue components, API client, and stores based on specification and UI library choice
"""

from pathlib import Path

def generate_package_json(project_name, tech_stack):
    """Generate package.json with selected UI library"""
    ui_lib = tech_stack.get('uiLibrary', 'element-plus')
    features = tech_stack.get('features', [])
    
    base_json = {
        "name": f"{project_name}-frontend",
        "version": "1.0.0",
        "private": True,
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vue-tsc \u0026\u0026 vite build",
            "preview": "vite preview",
            "lint": "eslint . --ext .vue,.ts,.tsx --fix",
            "format": "prettier --write src/"
        },
        "dependencies": {
            "vue": "^3.4.0",
            "vue-router": "^4.2.0",
            "pinia": "^2.1.0",
            "axios": "^1.6.0",
            "dayjs": "^1.11.0"
        },
        "devDependencies": {
            "@types/node": "^20.0.0",
            "@vitejs/plugin-vue": "^5.0.0",
            "@vue/eslint-config-prettier": "^9.0.0",
            "@vue/eslint-config-typescript": "^12.0.0",
            "eslint": "^8.56.0",
            "eslint-plugin-vue": "^9.20.0",
            "prettier": "^3.2.0",
            "typescript": "~5.3.0",
            "vite": "^5.0.0",
            "vue-tsc": "^1.8.0"
        }
    }
    
    # Add UI library
    if ui_lib == 'element-plus':
        base_json["dependencies"]["element-plus"] = "^2.5.0"
        base_json["dependencies"]["@element-plus/icons-vue"] = "^2.3.0"
    elif ui_lib == 'antdv':
        base_json["dependencies"]["ant-design-vue"] = "^4.0.0"
        base_json["dependencies"]["@ant-design/icons-vue"] = "^7.0.0"
    elif ui_lib == 'naive':
        base_json["dependencies"]["naive-ui"] = "^2.37.0"
        base_json["devDependencies"]["vfonts"] = "^0.0.3"
    
    # Add i18n if selected
    if 'i18n' in features:
        base_json["dependencies"]["vue-i18n"] = "^9.8.0"
    
    # Add PWA if selected
    if 'pwa' in features:
        base_json["devDependencies"]["vite-plugin-pwa"] = "^0.17.0"
    
    import json
    return json.dumps(base_json, indent=2, ensure_ascii=False)

def generate_vite_config(tech_stack):
    """Generate vite.config.ts with selected features"""
    features = tech_stack.get('features', [])
    ui_lib = tech_stack.get('uiLibrary', 'element-plus')
    
    imports = ["import { defineConfig } from 'vite'", "import vue from '@vitejs/plugin-vue'"]
    plugins = ["vue()"]
    
    if 'pwa' in features:
        imports.append("import { VitePWA } from 'vite-plugin-pwa'")
        plugins.append('''VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'My App',
        theme_color: '#ffffff'
      }
    })''')
    
    imports_str = '\n'.join(imports)
    plugins_str = ',\n    '.join(plugins)
    
    return f'''{imports_str}
import path from 'path'

export default defineConfig({{
  plugins: [
    {plugins_str}
  ],
  resolve: {{
    alias: {{
      '@': path.resolve(__dirname, 'src')
    }}
  }},
  server: {{
    port: 3000,
    proxy: {{
      '/api': {{
        target: 'http://localhost:8080',
        changeOrigin: true
      }}
    }}
  }}
}})
'''

def map_type(java_type):
    """Map Java type to TypeScript type"""
    mapping = {
        'String': 'string',
        'Long': 'number',
        'Integer': 'number',
        'BigDecimal': 'number',
        'LocalDateTime': 'string',
        'Boolean': 'boolean',
        'Text': 'string',
        'Enum': 'string',
    }
    return mapping.get(java_type, 'any')

def generate_api_client(entity_spec):
    """Generate TypeScript API client"""
    class_name = entity_spec['name']
    class_lower = class_name.lower()
    base_path = class_lower + 's'
    
    fields = entity_spec.get('fields', [])
    field_interfaces = '\n'.join([f"  {f['name']}: {map_type(f['type'])}" for f in fields])
    query_fields = '\n'.join([f"  {f['name']}?: {map_type(f['type'])}" for f in fields[:3]])
    
    return f'''import request from '@/utils/request'
import type {{ PageQuery, PageResult }} from '@/types/common'

export interface {class_name} {{
  id: number
{field_interfaces}
  createdAt: string
  updatedAt: string
}}

export interface {class_name}Query extends PageQuery {{
{query_fields}
}}

export function get{class_name}List(params: {class_name}Query) {{
  return request.get<PageResult<{class_name}>>('/api/{base_path}', {{ params }})
}}

export function get{class_name}ById(id: number) {{
  return request.get<{class_name}>(`/api/{base_path}/${{id}}`)
}}

export function create{class_name}(data: Omit<{class_name}, 'id' | 'createdAt' | 'updatedAt'>) {{
  return request.post<{class_name}>('/api/{base_path}', data)
}}

export function update{class_name}(id: number, data: Partial<{class_name}>) {{
  return request.put<{class_name}>(`/api/{base_path}/${{id}}`, data)
}}

export function delete{class_name}(id: number) {{
  return request.delete(`/api/{base_path}/${{id}}`)
}}
'''

def generate_store(entity_spec, tech_stack):
    """Generate Pinia store"""
    class_name = entity_spec['name']
    class_lower = class_name.lower()
    
    return f'''import {{ defineStore }} from 'pinia'
import {{ ref, computed }} from 'vue'
import type {{ {class_name}, {class_name}Query }} from '@/api/{class_lower}'
import * as api from '@/api/{class_lower}'

export const use{class_name}Store = defineStore('{class_lower}', () => {{
  // State
  const list = ref<{class_name}[]>([])
  const loading = ref(false)
  const current = ref<{class_name} | null>(null)
  const total = ref(0)
  
  // Getters
  const getById = computed(() => (id: number) => {{
    return list.value.find(item => item.id === id)
  }})
  
  // Actions
  async function fetchList(query: {class_name}Query) {{
    loading.value = true
    try {{
      const res = await api.get{class_name}List(query)
      list.value = res.data.list
      total.value = res.data.total
      return res.data
    }} finally {{
      loading.value = false
    }}
  }}
  
  async function fetchById(id: number) {{
    const res = await api.get{class_name}ById(id)
    current.value = res.data
    return res.data
  }}
  
  async function create(data: any) {{
    const res = await api.create{class_name}(data)
    list.value.unshift(res.data)
    return res.data
  }}
  
  async function update(id: number, data: any) {{
    const res = await api.update{class_name}(id, data)
    const index = list.value.findIndex(item => item.id === id)
    if (index > -1) {{
      list.value[index] = res.data
    }}
    return res.data
  }}
  
  async function remove(id: number) {{
    await api.delete{class_name}(id)
    list.value = list.value.filter(item => item.id !== id)
  }}
  
  return {{
    list,
    loading,
    current,
    total,
    getById,
    fetchList,
    fetchById,
    create,
    update,
    remove
  }}
}})
'''

def generate_list_view(entity_spec, tech_stack):
    """Generate list view component with selected UI library"""
    class_name = entity_spec['name']
    class_lower = class_name.lower()
    fields = entity_spec.get('fields', [])
    ui_lib = tech_stack.get('uiLibrary', 'element-plus')
    
    if ui_lib == 'element-plus':
        return _generate_element_plus_list(class_name, class_lower, fields)
    elif ui_lib == 'antdv':
        return _generate_antdv_list(class_name, class_lower, fields)
    else:  # naive
        return _generate_naive_list(class_name, class_lower, fields)

def _generate_element_plus_list(class_name, class_lower, fields):
    columns = '\n'.join([f'      <el-table-column prop="{f["name"]}" label="{f["name"].capitalize()}" />' for f in fields[:4]])
    search_fields = '\n'.join([f"      <el-form-item label='{f['name'].capitalize()}'><el-input v-model=\"query.{f['name']}\" placeholder=\"请输入\" /></el-form-item>" for f in fields[:2]])
    
    return f'''<template>
  <div class="{class_lower}-list">
    <!-- Search Form -->
    <el-form :model="query" inline>
{search_fields}
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="success" @click="handleCreate">新增</el-button>
      </el-form-item>
    </el-form>
    
    <!-- Data Table -->
    <el-table :data="store.list" v-loading="store.loading">
      <el-table-column type="index" width="50" />
{columns}
      <el-table-column label="操作" width="180">
        <template #default="{{ row }}">
          <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- Pagination -->
    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.size"
      :total="store.total"
      layout="total, sizes, prev, pager, next"
      @change="handleSearch"
    />
    
    <!-- Form Dialog -->
    <{class_lower}-form-dialog
      v-model:visible="dialogVisible"
      :data="editData"
      @success="handleSearch"
    />
  </div>
</template>

<script setup lang="ts">
import {{ ref, reactive, onMounted }} from 'vue'
import {{ use{class_name}Store }} from '@/stores/{class_lower}'
import {{ ElMessage, ElMessageBox }} from 'element-plus'
import {class_name}FormDialog from './components/{class_name}FormDialog.vue'

const store = use{class_name}Store()
const dialogVisible = ref(false)
const editData = ref(null)

const query = reactive({{
  page: 1,
  size: 10,
{chr(10).join([f"  {f['name']}: undefined," for f in fields[:2]])}
}})

onMounted(() => {{
  handleSearch()
}})

function handleSearch() {{
  store.fetchList(query)
}}

function handleReset() {{
  query.page = 1
{chr(10).join([f"  query.{f['name']} = undefined" for f in fields[:2]])}
  handleSearch()
}}

function handleCreate() {{
  editData.value = null
  dialogVisible.value = true
}}

function handleEdit(row: any) {{
  editData.value = {{ ...row }}
  dialogVisible.value = true
}}

async function handleDelete(row: any) {{
  try {{
    await ElMessageBox.confirm('确认删除该记录？', '提示', {{ type: 'warning' }})
    await store.remove(row.id)
    ElMessage.success('删除成功')
    handleSearch()
  }} catch {{ }}
}}
</script>
'''

def _generate_antdv_list(class_name, class_lower, fields):
    columns = '\n'.join([f'      <a-table-column key="{f["name"]}" dataIndex="{f["name"]}" title="{f["name"].capitalize()}" />' for f in fields[:3]])
    
    return f'''<template>
  <div class="{class_lower}-list">
    <a-form :model="query" layout="inline">
{chr(10).join([f"      <a-form-item label='{f['name'].capitalize()}'><a-input v-model:value=\"query.{f['name']}\" /></a-form-item>" for f in fields[:2]])}
      <a-form-item>
        <a-button type="primary" @click="handleSearch">搜索</a-button>
        <a-button @click="handleReset">重置</a-button>
        <a-button type="primary" @click="handleCreate">新增</a-button>
      </a-form-item>
    </a-form>
    
    <a-table :dataSource="store.list" :loading="store.loading" :pagination="pagination">
      <a-table-column key="id" dataIndex="id" title="ID" />
{columns}
      <a-table-column key="action" title="操作">
        <template #default="{{ {{ record }} }}">
          <a-button type="link" @click="handleEdit(record)">编辑</a-button>
          <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
        </template>
      </a-table-column>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import {{ ref, reactive, computed, onMounted }} from 'vue'
import {{ use{class_name}Store }} from '@/stores/{class_lower}'
import {{ message, Modal }} from 'ant-design-vue'

const store = use{class_name}Store()
const dialogVisible = ref(false)
const editData = ref(null)

const query = reactive({{
  page: 1,
  size: 10,
{chr(10).join([f"  {f['name']}: undefined," for f in fields[:2]])}
}})

const pagination = computed(() => ({{
  current: query.page,
  pageSize: query.size,
  total: store.total,
  showSizeChanger: true
}}))

onMounted(handleSearch)

function handleSearch() {{
  store.fetchList(query)
}}

function handleReset() {{
  query.page = 1
{chr(10).join([f"  query.{f['name']} = undefined" for f in fields[:2]])}
  handleSearch()
}}

function handleCreate() {{
  editData.value = null
  dialogVisible.value = true
}}

function handleEdit(row: any) {{
  editData.value = {{ ...row }}
  dialogVisible.value = true
}}

function handleDelete(row: any) {{
  Modal.confirm({{
    title: '确认删除',
    content: '删除后无法恢复，是否继续？',
    onOk: async () => {{
      await store.remove(row.id)
      message.success('删除成功')
      handleSearch()
    }}
  }})
}}
</script>
'''

def _generate_naive_list(class_name, class_lower, fields):
    columns = '\n'.join([f"      {{ title: '{f['name'].capitalize()}', key: '{f['name']}' }}," for f in fields[:3]])
    
    return f'''<template>
  <div class="{class_lower}-list">
    <n-space vertical>
      <n-form :model="query" inline>
{chr(10).join([f"        <n-form-item label='{f['name'].capitalize()}'><n-input v-model:value=\"query.{f['name']}\" /></n-form-item>" for f in fields[:2]])}
        <n-form-item>
          <n-button type="primary" @click="handleSearch">搜索</n-button>
          <n-button @click="handleReset">重置</n-button>
          <n-button type="primary" @click="handleCreate">新增</n-button>
        </n-form-item>
      </n-form>
      
      <n-data-table
        :columns="columns"
        :data="store.list"
        :loading="store.loading"
        :pagination="pagination"
        @update:page="handlePageChange"
      />
    </n-space>
  </div>
</template>

<script setup lang="ts">
import {{ ref, reactive, onMounted }} from 'vue'
import {{ use{class_name}Store }} from '@/stores/{class_lower}'
import {{ useMessage, useDialog }} from 'naive-ui'

const store = use{class_name}Store()
const message = useMessage()
const dialog = useDialog()

const query = reactive({{
  page: 1,
  size: 10,
{chr(10).join([f"  {f['name']}: undefined," for f in fields[:2]])}
}})

const columns = [
  {{ title: 'ID', key: 'id' }},
{columns}
  {{
    title: '操作',
    key: 'actions',
    render(row: any) {{
      return h(NSpace, null, {{
        default: () => [
          h(NButton, {{ type: 'primary', size: 'small', onClick: () => handleEdit(row) }}, {{ default: () => '编辑' }}),
          h(NButton, {{ type: 'error', size: 'small', onClick: () => handleDelete(row) }}, {{ default: () => '删除' }})
        ]
      }})
    }}
  }}
]

const pagination = reactive({{
  page: 1,
  pageSize: 10,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50]
}})

onMounted(handleSearch)

function handleSearch() {{
  store.fetchList(query).then(data => {{
    pagination.itemCount = data.total
  }})
}}

function handlePageChange(page: number) {{
  query.page = page
  handleSearch()
}}

function handleReset() {{
  query.page = 1
{chr(10).join([f"  query.{f['name']} = undefined" for f in fields[:2]])}
  handleSearch()
}}

function handleCreate() {{
  // Open create dialog
}}

function handleEdit(row: any) {{
  // Open edit dialog
}}

function handleDelete(row: any) {{
  dialog.warning({{
    title: '确认删除',
    content: '删除后无法恢复，是否继续？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {{
      await store.remove(row.id)
      message.success('删除成功')
      handleSearch()
    }}
  }})
}}
</script>
'''

def main():
    """Test with sample data"""
    tech_stack = {
        'uiLibrary': 'element-plus',
        'stateManagement': 'pinia',
        'features': ['darkMode']
    }
    
    entity_spec = {
        'name': 'Product',
        'fields': [
            {'name': 'name', 'type': 'String'},
            {'name': 'price', 'type': 'BigDecimal'},
            {'name': 'stock', 'type': 'Integer'},
        ]
    }
    
    print(generate_package_json('demo', tech_stack))

if __name__ == '__main__':
    main()
