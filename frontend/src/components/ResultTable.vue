<script setup lang="ts">
import { computed } from "vue";
import type { ResultColumn } from "@/types";

/**
 * 查询结果表格组件
 * 展示 SQL 查询返回的数据
 */
const props = defineProps<{
  data: any[];
}>();

/**
 * 获取表格列定义
 * @returns 列定义数组
 */
const columns = computed<ResultColumn[]>(() => {
  if (!props.data || props.data.length === 0) return [];
  const firstRow = props.data[0];
  return Object.keys(firstRow).map((key) => ({
    prop: key,
    label: key,
  }));
});
</script>

<template>
  <div class="result-table-wrapper">
    <div class="section-header">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="15"
        height="15"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path
          d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
        ></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="16" y1="13" x2="8" y2="13"></line>
        <line x1="16" y1="17" x2="8" y2="17"></line>
        <polyline points="10 9 9 9 8 9"></polyline>
      </svg>
      <span class="section-title-text">查询结果</span>
      <span class="progress-count">{{ data.length }} 行</span>
    </div>

    <div class="result-content">
      <el-table
        :data="data"
        border
        stripe
        size="small"
        class="result-table"
        :header-cell-style="{
          background: '#f8fafc',
          color: '#475569',
          fontWeight: 600,
        }"
      >
        <el-table-column type="index" label="#" width="55" />
        <el-table-column
          v-for="col in columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          min-width="130"
        />
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.result-table-wrapper {
  padding-top: 20px;
  border-top: 1px dashed var(--border);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.section-header svg {
  color: var(--success);
}

.section-title-text {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.progress-count {
  margin-left: auto;
  padding: 3px 10px;
  background: var(--border-light);
  color: var(--text-secondary);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.result-content {
  margin-top: 4px;
}

.result-table {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
}
</style>
