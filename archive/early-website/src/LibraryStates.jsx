import {useState} from 'react';
import {ArrowRight,Check,Copy,UploadSimple,X,WarningCircle} from '@phosphor-icons/react';

export function LibraryStates(){
 const [busy,setBusy]=useState(false),[toast,setToast]=useState(''),[file,setFile]=useState(''),[modal,setModal]=useState(false);
 return <>
  <div className="info-panel"><h2>按钮的交互状态</h2><p>实际按钮支持悬停、按下和键盘焦点。以下样张用于对照参数。</p><div className="state-samples">{['默认','悬停','按下','焦点','禁用'].map((t,i)=><div key={t}><small>{t}</small><button className={`button sample-${i}`} disabled={i===4}>{t}<ArrowRight size={17}/></button></div>)}</div><button className="button" aria-busy={busy} disabled={busy} onClick={()=>setBusy(true)}>{busy?<><span className="spinner" aria-hidden="true"/>处理中</>:<>查看加载态<ArrowRight size={17}/></>}</button>{busy&&<button className="inline-button" onClick={()=>setBusy(false)}>恢复可操作状态</button>}</div>
  <div className="info-panel"><h2>提示与反馈</h2><div className="notice"><Check size={18}/><span>操作反馈要说明已经完成的动作。</span></div><div className="notice"><WarningCircle size={18}/><span>信息尚未更新。保留上一次明确的来源时间。</span></div><p className="error" role="alert"><WarningCircle size={18}/>必填内容需要补充，输入内容会保留。</p><div className="actions"><button className="button secondary" onClick={()=>setToast('提示样张已打开。没有提交任何资料。')}><Copy size={18}/>查看 Toast</button><button className="button secondary" onClick={()=>setModal(true)}>查看权限提示</button></div></div>
  <div className="info-panel"><h2>附件与选择</h2><p>附件组件只显示本地所选文件名，不上传文件。</p><label className="file-input"><UploadSimple size={20}/><span>{file||'选择本地需求资料'}</span><input type="file" onChange={e=>setFile(e.target.files?.[0]?.name||'')} aria-label="选择本地需求资料"/></label><div className="choice-row"><label><input type="checkbox"/>按实际服务确认通知方式</label><label><input type="radio" name="delivery" defaultChecked/>模型服务</label><label><input type="radio" name="delivery"/>设备与节点</label></div><div className="pagination" aria-label="分页样张"><button disabled>上一页</button><span>当前目录无需分页</span><button disabled>下一页</button></div></div>
  {toast&&<div className="toast" role="status"><span>{toast}</span><button className="icon-button" aria-label="关闭提示" onClick={()=>setToast('')}><X size={19}/></button></div>}
  {modal&&<div className="inline-notice" role="status"><WarningCircle size={22}/><div><h3>需要相应的访问权限</h3><p>权限提示组件样张。实际权限依据正式账户系统返回结果。</p><button className="inline-button" onClick={()=>setModal(false)}>关闭权限提示</button></div></div>}
 </>
}
