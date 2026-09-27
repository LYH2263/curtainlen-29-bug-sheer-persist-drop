<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
function sheerHint(r) {
  const side = r.result?.list_sheer_meters
  if (side == null) return ''
  return `（列表侧记纱 ${side}m）`
}
</script>
<template><div class="page"><h1>记录</h1><ul>
<li v-for="r in items" :key="r.id">
  {{ r.window_name }} 主 {{ r.result?.meters }}m
  <template v-if="r.result?.sheer?.enabled">
    / 纱 {{ r.result.sheer.meters }}m（{{ r.result.sheer.fabric_name }}）{{ sheerHint(r) }}
  </template>
</li>
</ul>
<p class="hint">开放视图保留纱帘开关与面料名；纱米可并入主帘或侧记 list_sheer_meters。</p>
</div></template>
