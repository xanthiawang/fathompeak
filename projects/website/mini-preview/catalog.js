// Source: ../index.html var M, catalog captured 2026-10-13. Reference data, not live offers.
export const catalog = [
  {
    "id": "deepseek-v4-flash",
    "name": "DeepSeek-V4-Flash",
    "vendor": "DeepSeek",
    "type": [
      "对话"
    ],
    "ctx": "1M",
    "mkt": 4.5,
    "seen": "2026-10-13",
    "desc": "用于对话等推理任务。"
  },
  {
    "id": "deepseek-v4-pro",
    "name": "DeepSeek-V4-Pro",
    "vendor": "DeepSeek",
    "type": [
      "推理"
    ],
    "ctx": "1M",
    "mkt": 13.5,
    "seen": "2026-10-13",
    "desc": "复杂推理与智能体任务的候选模型，建议用实际样例验证质量、时延与工具调用。"
  },
  {
    "id": "qwen3-8-flash",
    "name": "Qwen3.8-Flash",
    "vendor": "Alibaba",
    "type": [
      "对话"
    ],
    "ctx": "1M",
    "mkt": 2.7,
    "seen": "2026-10-13",
    "desc": "通义千问系列模型。"
  },
  {
    "id": "glm-5-3-flash",
    "name": "GLM-5.3-Flash",
    "vendor": "Zhipu",
    "type": [
      "对话"
    ],
    "ctx": "1M",
    "mkt": 2.8,
    "seen": "2026-10-13",
    "desc": "GLM 系列模型，适合对话任务。"
  },
  {
    "id": "glm-5-3",
    "name": "GLM-5.3",
    "vendor": "Zhipu",
    "type": [
      "推理"
    ],
    "ctx": "1M",
    "mkt": 28,
    "seen": "2026-10-13",
    "desc": "GLM 系列推理模型，适合复杂任务。"
  },
  {
    "id": "minimax-m2-7",
    "name": "MiniMax-M2.7",
    "vendor": "MiniMax",
    "type": [
      "对话"
    ],
    "ctx": "1M",
    "mkt": 8.4,
    "seen": "2026-10-13",
    "desc": "MiniMax 系列候选模型，按任务质量、响应时延与总费用评估适配性。"
  },
  {
    "id": "minimax-m3",
    "name": "MiniMax-M3",
    "vendor": "MiniMax",
    "type": [
      "推理"
    ],
    "ctx": "1M",
    "mkt": 8.4,
    "seen": "2026-10-13",
    "desc": "MiniMax 系列推理模型，输出参考价对应 ≤512k 档。"
  }
];
export const endpoint = "https://api.fathompeak.cn/v1";
export const selectedModel = s => catalog.find(m => m.id === s.modelId);
export const priceCondition = m => m.vendor === "DeepSeek" ? "空闲时段参考价" : m.id === "minimax-m3" ? "≤512k 档参考价" : "目录输出参考价";

// Cost estimates use user-entered CNY / million Token rates, never the historical mkt as a discount baseline.
// Lowest advertised tier: "4 折起" (40% of the public price). Real tiers by model and volume are not yet published.
export const discountRate = 0.4;
export const emptyEstimate = () => ({modelId:'',input:'',output:'',inputRate:'',outputRate:''});
export function estimateNumber(value) {
 const text=String(value).trim();
 return /^(?:0|[1-9]\d{0,5})(?:\.\d{1,6})?$/.test(text) ? Number(text) : null;
}
export function estimateCosts(value) {
 const input=estimateNumber(value.input),output=estimateNumber(value.output);
 const inputRate=estimateNumber(value.inputRate),outputRate=estimateNumber(value.outputRate);
 if(input===null||output===null||(inputRate===null&&(input>0||String(value.inputRate).trim()!==''))||(outputRate===null&&(output>0||String(value.outputRate).trim()!=='')))return null;
 const publicCost=input*(inputRate??0)+output*(outputRate??0);
 return {publicCost,discountCost:publicCost*discountRate,saving:publicCost*(1-discountRate)};
}
export function costLabel(value) {
 if(value>0&&value<.000001)return '¥<0.000001';
 return '¥'+value.toLocaleString('zh-CN',{minimumFractionDigits:2,maximumFractionDigits:6});
}
