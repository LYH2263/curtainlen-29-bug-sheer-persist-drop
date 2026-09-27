<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import PanelCut from '../components/PanelCut.vue'
const windows = ref([]); const fabrics = ref([]); const wid = ref(1); const fid = ref(1); const out = ref(null)
const sheerOn = ref(false); const sfid = ref(null); const sfull = ref(2.0); const err = ref('')
onMounted(async () => {
  windows.value = (await getJSON('/api/windows')).items.filter(x=>x.data_quality==='clean')
  fabrics.value = (await getJSON('/api/fabrics')).items.filter(x=>x.data_quality==='clean')
  if (windows.value.length) wid.value = windows.value[0].id
  if (fabrics.value.length) fid.value = fabrics.value[0].id
  sfid.value = fabrics.value.find(x=>x.name.includes('纱'))?.id ?? null
})
function qs(){
  const p = new URLSearchParams({window_id:wid.value, fabric_id:fid.value})
  if (sheerOn.value) { p.set('sheer','true'); p.set('sheer_fabric_id',sfid.value); p.set('sheer_fullness',sfull.value) }
  return p
}
async function go(save){
  err.value=''; out.value=null
  try {
    out.value = save
      ? await postJSON('/api/estimate',{window_id:wid.value,fabric_id:fid.value,save:true,
        sheer_enabled:sheerOn.value, sheer_fabric_id:sheerOn.value?sfid.value:null,
        sheer_fullness:sheerOn.value?Number(sfull.value):null})
      : await getJSON('/api/estimate?'+qs())
  } catch(e){ err.value = String(e.message||e) }
}
</script>
<template><div class="page"><h1>算料</h1>
<select v-model.number="wid"><option v-for="x in windows" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<select v-model.number="fid"><option v-for="x in fabrics" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<label><input type="checkbox" v-model="sheerOn"> 纱帘</label>
<template v-if="sheerOn">
<select v-model.number="sfid"><option v-for="x in fabrics" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<input type="number" step="0.1" v-model.number="sfull"> 纱帘褶量
</template>
<button @click="go(false)">试算</button><button @click="go(true)">保存</button>
<p v-if="err" class="bad">{{ err }}</p>
<table v-if="out">
<tr><th></th><th>褶量</th><th>门幅</th><th>幅数</th><th>下料高</th><th>米数</th></tr>
<tr><td>主帘</td><td>{{ out.fullness }}</td><td>{{ out.fabric_width }}</td><td>{{ out.panels }}</td><td>{{ out.cut_height }}</td><td>{{ out.meters }}</td></tr>
<tr v-if="out.sheer && out.sheer.enabled"><td>纱帘</td><td>{{ out.sheer.fullness }}</td><td>{{ out.sheer.fabric_width }}</td><td>{{ out.sheer.panels }}</td><td>{{ out.sheer.cut_height }}</td><td>{{ out.sheer.meters }}</td></tr>
</table>
<div v-if="out">
<div>主帘<PanelCut :panels="out.panels" :cut-height="out.cut_height" :meters="out.meters" /></div>
<div v-if="out.sheer && out.sheer.enabled">纱帘<PanelCut :panels="out.sheer.panels" :cut-height="out.sheer.cut_height" :meters="out.sheer.meters" /></div>
</div>
</div></template>
