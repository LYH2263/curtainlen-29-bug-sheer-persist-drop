<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const props = defineProps({ id: String })
const w = ref(null); const runs = ref([])
onMounted(async () => {
  w.value = await getJSON(`/api/windows/${props.id}`)
  runs.value = (await getJSON(`/api/runs?window_id=${props.id}`)).items
})
</script>
<template><div class="page" v-if="w"><h1>{{ w.name }}</h1><p v-if="w.data_quality==='dirty'" class="bad">{{ w.note }}</p><p>宽 {{ w.width }} 高 {{ w.height }} 褶倍 {{ w.fullness }}</p>
<ul><li v-for="r in runs" :key="r.id">#{{ r.id }} 主帘 {{ r.result?.panels }}幅 ×{{ r.result?.cut_height }}m = {{ r.result?.meters }}m<template v-if="r.result?.sheer?.enabled">｜纱帘 {{ r.result.sheer.panels }}幅 ×{{ r.result.sheer.cut_height }}m = {{ r.result.sheer.meters }}m（褶量{{ r.result.sheer.fullness }} 门幅{{ r.result.sheer.fabric_width }}）</template></li></ul>
</div></template>
