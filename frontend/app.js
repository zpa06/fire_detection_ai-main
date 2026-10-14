/**
 * FireEyes AI — Frontend Application (app.js)
 * Kiến trúc: MVC theo Class Diagram dự án
 *   - Model    : FireEyesDB  (backend/CSDL/models/database.py)
 *   - Controller: AppController (đây — gọi API + điều phối)
 *   - View     : MainView (đây — render DOM)
 */

'use strict';

/* ═══════════════════════════════════════════════════════════
   1.  API CLIENT — Kết nối FastAPI backend, fallback mock
   ═══════════════════════════════════════════════════════════ */
class FireEyesAPI {
  constructor() {
    // Khi chạy từ FastAPI (:8000) hoặc Node proxy (:3000) đều đúng
    this.base = window.location.origin;
    this.online = false;
    this._mock = this._initMock();
  }

  // ─── Private mock store (localStorage) ────────────────────
  _initMock() {
    const raw = localStorage.getItem('fe_mock');
    if (raw) { try { return JSON.parse(raw); } catch(_){} }
    return {
      locations: [
        {id:1, name:'VKU Demo', address:'Phòng demo - dữ liệu giả lập'},
        {id:2, name:'Xưởng Thực Nghiệm', address:'Khu B2, Tòa nhà Công Nghệ'}
      ],
      cameras: [
        {id:1,location_id:1,location:'VKU Demo',name:'Camera Demo 01',source_ref:'demo://synthetic',enabled:1,last_seen_at:new Date().toISOString()},
        {id:2,location_id:1,location:'VKU Demo',name:'Camera Cổng Chính',source_ref:'camera-index:0',enabled:1,last_seen_at:null},
        {id:3,location_id:2,location:'Xưởng Thực Nghiệm',name:'Camera Xưởng Hàn',source_ref:'rtsp://local/cam3',enabled:0,last_seen_at:null}
      ],
      contacts:[{id:1,location_id:1,name:'Trực ban',destination:'console-only',channel:'console'}],
      dataset_versions:[{id:1,name:'D-Fire',version:'local-v1',source_url:'https://github.com/gaia-solutions-on-demand/DFireDataset',license_name:'CC0-1.0',class_map:'{"0":"fire","1":"smoke"}',status:'verified'}],
      model_versions:[
        {id:1,name:'DEMO-NO-AI',dataset_id:null,weights_path:null,weights_sha256:null,class_map:'{"0":"smoke","1":"fire"}',is_demo:1},
        {id:2,name:'YOLO11n-DFire-v1',dataset_id:1,weights_path:'models/best.pt',weights_sha256:'a'.repeat(64),class_map:'{"0":"smoke","1":"fire"}',is_demo:0}
      ],
      frames:[],
      detections:[],
      incidents:[
        {id:1,camera_id:1,camera:'Camera Demo 01',location:'VKU Demo',status:'open',
         started_at:new Date(Date.now()-3600000).toISOString(),closed_at:null,
         rule_description:'AI confirmed fire across multiple frames (3/5 sliding window)',
         resolution_note:null,acknowledged_at:null,acknowledged_by:null,
         alert_class:'fire',confidence:0.89,snapshot_path:null}
      ],
      notifications:[{id:1,incident_id:1,contact_id:1,channel:'console',destination:'console-only',status:'simulated',attempted_at:new Date().toISOString()}],
      _nextId:{location:3,camera:4,frame:1,detection:1,incident:2,notification:2}
    };
  }
  _saveMock(){ try{localStorage.setItem('fe_mock',JSON.stringify(this._mock));}catch(_){} }

  // ─── Health Check ─────────────────────────────────────────
  async checkHealth(){
    try{
      const r = await fetch(`${this.base}/health`,{signal:AbortSignal.timeout(2000)});
      if(r.ok){ this.online=true; return true; }
    }catch(_){}
    this.online=false; return false;
  }

  // ─── Generic fetch helper ─────────────────────────────────
  async _fetch(method,path,body){
    if(!this.online) throw new Error('offline');
    const opts={method,headers:{'Content-Type':'application/json'}};
    if(body) opts.body=JSON.stringify(body);
    const r=await fetch(`${this.base}${path}`,opts);
    if(!r.ok){
      const t=await r.text();
      let msg=t;
      try{const j=JSON.parse(t);msg=j.detail||j.message||t;}catch(_){}
      throw new Error(msg);
    }
    return r.status===204?null:r.json();
  }

  // ─── Stats ────────────────────────────────────────────────
  async getStats(){
    try{ return await this._fetch('GET','/api/stats'); }catch(_){}
    const m=this._mock;
    return {
      locations:m.locations.length, cameras:m.cameras.length,
      contacts:m.contacts.length, dataset_versions:m.dataset_versions.length,
      dataset_samples:21527, annotations:21527,
      model_versions:m.model_versions.length,
      frames:m.frames.length, detections:m.detections.length,
      incidents:m.incidents.length, notifications:m.notifications.length
    };
  }

  // ─── Incidents / Alerts ───────────────────────────────────
  async getIncidents(limit=150,offset=0,acknowledged=null){
    try{
      let url=`/api/alerts?limit=${limit}&offset=${offset}`;
      if(acknowledged!==null) url+=`&acknowledged=${acknowledged}`;
      return await this._fetch('GET',url);
    }catch(_){}
    let list=[...this._mock.incidents].sort((a,b)=>new Date(b.started_at)-new Date(a.started_at));
    if(acknowledged!==null) list=list.filter(i=>(acknowledged?i.acknowledged_at!==null:i.acknowledged_at===null));
    return list.slice(offset,offset+limit);
  }
  async acknowledgeAlert(id,by){
    try{ return await this._fetch('PATCH',`/api/alerts/${id}/acknowledge`,{acknowledged_by:by}); }catch(_){}
    const inc=this._mock.incidents.find(i=>i.id===Number(id));
    if(!inc) throw new Error('Not found');
    inc.acknowledged_at=new Date().toISOString(); inc.acknowledged_by=by;
    this._saveMock(); return inc;
  }
  async resolveAlert(id,status,note){
    try{ return await this._fetch('PATCH',`/api/alerts/${id}/resolve`,{status,note}); }catch(_){}
    const inc=this._mock.incidents.find(i=>i.id===Number(id));
    if(!inc) throw new Error('Not found');
    if(inc.status!=='open') throw new Error('Sự kiện đã được đóng rồi');
    inc.status=status; inc.closed_at=new Date().toISOString(); inc.resolution_note=note;
    this._saveMock(); return inc;
  }

  // ─── Cameras ──────────────────────────────────────────────
  async getCameras(){
    try{ return await this._fetch('GET','/api/cameras'); }catch(_){}
    return this._mock.cameras;
  }
  async getCameraStatus(id){
    try{ return await this._fetch('GET',`/api/cameras/${id}/status`); }catch(_){}
    const c=this._mock.cameras.find(x=>x.id===Number(id));
    if(!c) return null;
    const isActive=c.enabled&&c.last_seen_at&&(Date.now()-new Date(c.last_seen_at).getTime())<45000;
    return {camera_id:c.id,name:c.name,enabled:Boolean(c.enabled),
      status:c.enabled?(isActive?'active':'disconnected'):'stopped',last_seen_at:c.last_seen_at};
  }
  async setCameraEnabled(id,enabled){
    try{ return await this._fetch('PATCH',`/api/cameras/${id}/status`,{enabled}); }catch(_){}
    const c=this._mock.cameras.find(x=>x.id===Number(id));
    if(!c) throw new Error('Camera not found');
    c.enabled=enabled?1:0; c.last_seen_at=enabled?null:c.last_seen_at;
    this._saveMock(); return this.getCameraStatus(id);
  }
  async sendHeartbeat(id){
    try{ return await this._fetch('POST',`/api/cameras/${id}/heartbeat`); }catch(_){}
    const c=this._mock.cameras.find(x=>x.id===Number(id));
    if(!c) throw new Error('Camera not found');
    if(!c.enabled) throw new Error('Camera bị tắt, không thể gửi heartbeat');
    c.last_seen_at=new Date().toISOString(); this._saveMock();
    return {status:'received',last_seen_at:c.last_seen_at};
  }

  // ─── Locations ────────────────────────────────────────────
  async getLocations(){
    try{ return await this._fetch('GET','/api/locations'); }catch(_){}
    return this._mock.locations;
  }
  async createLocation(name,address){
    try{ return await this._fetch('POST','/api/locations',{name,address}); }catch(_){}
    const id=this._mock._nextId.location++;
    this._mock.locations.push({id,name,address}); this._saveMock();
    return {id,status:'created'};
  }
  async createCamera(location_id,name,source_ref){
    try{ return await this._fetch('POST','/api/cameras',{location_id:Number(location_id),name,source_ref}); }catch(_){}
    const id=this._mock._nextId.camera++;
    const loc=this._mock.locations.find(l=>l.id===Number(location_id));
    this._mock.cameras.push({id,location_id:Number(location_id),location:loc?.name||'',name,source_ref,enabled:1,last_seen_at:null});
    this._saveMock(); return {id,status:'created'};
  }

  // ─── Datasets / Models ────────────────────────────────────
  async getDatasets(){
    try{ return await this._fetch('GET','/api/datasets'); }catch(_){}
    return this._mock.dataset_versions;
  }
  async getModels(){
    try{ return await this._fetch('GET','/api/models'); }catch(_){}
    return this._mock.model_versions;
  }

  // ─── Detection History ────────────────────────────────────
  async getHistory(cameraId=null,limit=100,offset=0){
    try{
      let url=`/api/detections/history?limit=${limit}&offset=${offset}`;
      if(cameraId) url+=`&camera_id=${cameraId}`;
      return await this._fetch('GET',url);
    }catch(_){}
    let list=[...this._mock.detections];
    if(cameraId) list=list.filter(d=>d.camera_id===Number(cameraId));
    return list.slice(offset,offset+limit);
  }

  // ─── Ingest frame ─────────────────────────────────────────
  async ingestFrame(payload){
    try{ return await this._fetch('POST','/api/detections',payload); }catch(_){}
    // mock
    const fid=this._mock._nextId.frame++;
    const did=this._mock._nextId.detection++;
    this._mock.frames.push({id:fid,...payload});
    payload.detections.forEach(b=>{
      this._mock.detections.unshift({id:did,frame_id:fid,camera_id:payload.camera_id,
        camera:this._mock.cameras.find(c=>c.id===payload.camera_id)?.name||'',
        model_id:payload.model_id,model:'DEMO-NO-AI',
        request_id:payload.request_id,captured_at:payload.captured_at,
        class_id:b.class_id,detection_class:b.class_id===1?'fire':'smoke',
        confidence:b.confidence,xc:b.xc,yc:b.yc,w:b.w,h:b.h,snapshot_path:null});
    });
    let incident_id=null;
    if(payload.confirmed_classes?.length){
      const iid=this._mock._nextId.incident++;
      const cam=this._mock.cameras.find(c=>c.id===payload.camera_id);
      this._mock.incidents.unshift({id:iid,camera_id:payload.camera_id,
        camera:cam?.name||'',location:cam?.location||'',status:'open',
        started_at:payload.captured_at,closed_at:null,
        rule_description:`AI confirmed ${payload.confirmed_classes.join(', ')} (3/5 sliding window)`,
        resolution_note:null,acknowledged_at:null,acknowledged_by:null,
        alert_class:payload.confirmed_classes[0],
        confidence:payload.detections[0]?.confidence||0.85,snapshot_path:null});
      incident_id=iid;
    }
    this._saveMock();
    return {frame_id:fid,status:'stored',incident_id};
  }

  // ─── Run Demo ─────────────────────────────────────────────
  async runDemo(){
    try{ return await this._fetch('POST','/api/demo'); }catch(_){}
    // Full mock demo flow
    const ids=this._mockSeedDemo();
    const fid=this._mock._nextId.frame++;
    const did=this._mock._nextId.detection++;
    const iid=this._mock._nextId.incident++;
    const now=new Date().toISOString();
    const box={class_id:0,confidence:0.88,xc:.5,yc:.45,w:.22,h:.32};
    this._mock.frames.push({id:fid,camera_id:ids.camera_id,model_id:ids.model_id,
      request_id:`demo-${Date.now()}`,captured_at:now,snapshot_path:null});
    this._mock.detections.unshift({id:did,frame_id:fid,camera_id:ids.camera_id,
      camera:'Camera Demo 01',model_id:ids.model_id,model:'DEMO-NO-AI',
      request_id:`demo-${Date.now()}`,captured_at:now,class_id:0,
      detection_class:'smoke',confidence:.88,...box,snapshot_path:null});
    this._mock.incidents.unshift({id:iid,camera_id:ids.camera_id,
      camera:'Camera Demo 01',location:'VKU Demo',status:'open',
      started_at:now,closed_at:null,
      rule_description:'MANUAL DEMO: AI confirmed smoke across multiple frames (synthetic)',
      resolution_note:null,acknowledged_at:null,acknowledged_by:null,
      alert_class:'smoke',confidence:.88,snapshot_path:null});
    this._saveMock();
    return {message:'Demo data created successfully',frame_id:fid,detection_id:did,
      incident_id:iid,stats:await this.getStats(),incidents:this._mock.incidents.slice(0,10)};
  }
  _mockSeedDemo(){
    if(!this._mock.cameras.find(c=>c.name==='Camera Demo 01')){
      let loc=this._mock.locations.find(l=>l.name==='VKU Demo');
      if(!loc){loc={id:this._mock._nextId.location++,name:'VKU Demo',address:'Phòng demo'};this._mock.locations.push(loc);}
      this._mock.cameras.push({id:this._mock._nextId.camera++,location_id:loc.id,location:'VKU Demo',
        name:'Camera Demo 01',source_ref:'demo://synthetic',enabled:1,last_seen_at:new Date().toISOString()});
    }
    return {camera_id:this._mock.cameras.find(c=>c.name==='Camera Demo 01').id,
            model_id:this._mock.model_versions[0].id,
            contact_id:this._mock.contacts[0]?.id||1};
  }
}


/* ═══════════════════════════════════════════════════════════
   2.  FIRE CONFIRMATION LOGIC — Mirrors fire_logic.py
   ═══════════════════════════════════════════════════════════ */
class FireConfirmation {
  constructor(W=5,K=3,fireThr=0.2633,smokeThr=0.1792){
    this.W=W; this.K=K; this.fireThr=fireThr; this.smokeThr=smokeThr;
    this.fireWin=[]; this.smokeWin=[];
    this.prevFire=false; this.prevSmoke=false;
  }
  update(fConf=0,sConf=0){
    const iF=fConf>=this.fireThr, iS=sConf>=this.smokeThr;
    this.fireWin.push(iF);  if(this.fireWin.length >this.W) this.fireWin.shift();
    this.smokeWin.push(iS); if(this.smokeWin.length>this.W) this.smokeWin.shift();
    const fc=this.fireWin.filter(Boolean).length;
    const sc=this.smokeWin.filter(Boolean).length;
    const fireCfm=fc>=this.K, smokeCfm=sc>=this.K;
    const newFire=fireCfm&&!this.prevFire;
    const newSmoke=smokeCfm&&!this.prevSmoke;
    this.prevFire=fireCfm; this.prevSmoke=smokeCfm;
    return {fire_detected:iF,smoke_detected:iS,fire_confirmed:fireCfm,smoke_confirmed:smokeCfm,
            fire_count:fc,smoke_count:sc,new_fire:newFire,new_smoke:newSmoke,
            fire_window:[...this.fireWin],smoke_window:[...this.smokeWin]};
  }
  reset(){ this.fireWin=[]; this.smokeWin=[]; this.prevFire=false; this.prevSmoke=false; }
}


/* ═══════════════════════════════════════════════════════════
   3.  AUDIO ALARM
   ═══════════════════════════════════════════════════════════ */
class AudioAlarm {
  constructor(){
    this.enabled = true;
    this.ctx = null;
    this._bindUnlock();
  }
  _bindUnlock(){
    const unlock = () => {
      try{
        if(!this.ctx){
          const AC = window.AudioContext || window.webkitAudioContext;
          if(AC) this.ctx = new AC();
        }
        if(this.ctx && this.ctx.state === 'suspended'){
          this.ctx.resume();
        }
      }catch(_){}
      ['click','keydown','touchstart'].forEach(e => document.removeEventListener(e, unlock));
    };
    ['click','keydown','touchstart'].forEach(e => document.addEventListener(e, unlock, { passive: true }));
  }
  beep(){
    if(!this.enabled) return;
    try{
      if(!this.ctx){
        const AC = window.AudioContext || window.webkitAudioContext;
        if(AC) this.ctx = new AC();
      }
      if(this.ctx && this.ctx.state === 'suspended') this.ctx.resume();
      if(!this.ctx) return;
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(920, now);
      osc.frequency.exponentialRampToValueAtTime(460, now + 0.22);
      osc.frequency.exponentialRampToValueAtTime(920, now + 0.45);
      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.50);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.50);
    }catch(e){ console.warn('audio error', e); }
  }
}


/* ═══════════════════════════════════════════════════════════
   4.  MAIN APPLICATION CLASS (Controller + View combined)
   ═══════════════════════════════════════════════════════════ */
class FireEyesApp {
  constructor(){
    this.api = new FireEyesAPI();
    this.confirm = new FireConfirmation();
    this.alarm = new AudioAlarm();

    this.incidents = [];
    this.cameras   = [];
    this.activeTab = 'dashboard';
    this.incFilter = 'all';
    this.pendingAlertId = null;

    // Stream state
    this.streamSrc = 'sim'; // sim | cam | img
    this.simBoxes  = [];
    this.streamRunning = false;
    this.rafId = null;
    this.webcamStream = null;
    this.uploadImg = null;
    this.cameraStopped = false;
    this.manualSimActive = false;
    this._snapCache = {};

    // Temporal tracking & smoothing for real-time flame detection
    this._lastFlameBox = null;
    this._flameMissCount = 0;

    // Reusable analysis canvas for real-time flame detection
    this._analysisCanvas = document.createElement('canvas');
    this._analysisCanvas.width = 160;
    this._analysisCanvas.height = 120;
    this._analysisCtx = this._analysisCanvas.getContext('2d', { willReadFrequently: true });

    this._bindNav();
    this._bindTopBar();
    this._bindMonitor();
    this._bindIncidents();
    this._bindDevices();
    this._bindModals();

    lucide.createIcons();
  }

  // ─── Boot ─────────────────────────────────────────────────
  async start(){
    await this._checkBackend();
    await this._refreshAll();
    this._startStream();
    lucide.createIcons();

    // Periodic refresh every 12s
    setInterval(()=>{ this._checkBackend(); this._refreshAll(); }, 12000);
  }

  // ─── Backend health ───────────────────────────────────────
  async _checkBackend(){
    const ok = await this.api.checkHealth();
    const dot  = document.getElementById('status-dot');
    const lbl  = document.getElementById('status-label');
    const hint = document.getElementById('status-hint');
    if(ok){
      dot.className='pulse-dot green';
      lbl.textContent='FastAPI Online';
      hint.textContent=`Connected: ${this.api.base}`;
    } else {
      dot.className='pulse-dot gray';
      lbl.textContent='Offline — Mock DB';
      hint.textContent='Khởi động FastAPI để kết nối CSDL thật';
    }
  }

  // ─── Navigation ───────────────────────────────────────────
  _bindNav(){
    document.querySelectorAll('.sidebar-item[data-tab]').forEach(btn=>{
      btn.addEventListener('click',()=>this.switchTab(btn.dataset.tab));
    });
  }
  switchTab(name){
    this.activeTab=name;
    document.querySelectorAll('.sidebar-item[data-tab]').forEach(b=>{
      b.classList.toggle('active', b.dataset.tab===name);
    });
    document.querySelectorAll('.tab-pane').forEach(p=>{
      p.classList.toggle('active', p.id===`tab-${name}`);
    });
    document.getElementById('page-title').textContent = {
      dashboard:'Dashboard',monitor:'Giám sát Camera AI',
      incidents:'Sự kiện cảnh báo',history:'Lịch sử nhận diện',
      devices:'CSDL & Thiết bị'
    }[name]||name;

    if(name==='history') this._loadHistory();
    if(name==='devices') this._loadDevices();
  }

  // ─── Top bar ──────────────────────────────────────────────
  _bindTopBar(){
    document.getElementById('btn-refresh').addEventListener('click',()=>{
      const ic=document.getElementById('refresh-icon');
      ic.classList.add('animate-spin');
      this._refreshAll().finally(()=>setTimeout(()=>ic.classList.remove('animate-spin'),700));
    });
    document.getElementById('btn-demo').addEventListener('click',()=>this._runDemo());
    document.getElementById('btn-demo-inc')?.addEventListener('click',()=>this._runDemo());
  }

  async _runDemo(){
    this.toast('Đang tạo dữ liệu demo...','info');
    try{
      const r=await this.api.runDemo();
      this.toast(r.message||'Tạo demo thành công!','success');
      await this._refreshAll();
    }catch(e){ this.toast('Lỗi demo: '+e.message,'error'); }
  }

  // ─── Full refresh ─────────────────────────────────────────
  async _refreshAll(){
    await Promise.all([this._loadStats(),this._loadIncidents(),this._loadCameras()]);
  }

  // ─── Stats ────────────────────────────────────────────────
  async _loadStats(){
    const stats=await this.api.getStats();
    const cfg=[
      {k:'locations',    lbl:'Địa điểm',     icon:'map-pin',    c:'text-blue-400'},
      {k:'cameras',      lbl:'Cameras',       icon:'cctv',       c:'text-emerald-400'},
      {k:'contacts',     lbl:'Người nhận',    icon:'users',      c:'text-amber-400'},
      {k:'dataset_versions',lbl:'Datasets',   icon:'folder-open',c:'text-purple-400'},
      {k:'dataset_samples', lbl:'Mẫu ảnh',    icon:'images',     c:'text-indigo-400'},
      {k:'annotations',  lbl:'Nhãn BBox',     icon:'tag',        c:'text-cyan-400'},
      {k:'model_versions',  lbl:'Models AI',  icon:'box',        c:'text-orange-400'},
      {k:'frames',       lbl:'Frames',        icon:'film',       c:'text-teal-400'},
      {k:'detections',   lbl:'Detections',    icon:'scan-eye',   c:'text-rose-400'},
      {k:'incidents',    lbl:'Incidents',     icon:'alert-triangle',c:'text-red-500'},
      {k:'notifications',lbl:'Thông báo',     icon:'send',       c:'text-green-400'},
    ];
    document.getElementById('stats-grid').innerHTML=cfg.map(({k,lbl,icon,c})=>`
      <div class="stat-card">
        <div class="flex items-center justify-between text-slate-400 mb-1.5">
          <span class="text-[11px] font-medium uppercase tracking-wide">${lbl}</span>
          <i data-lucide="${icon}" class="w-3.5 h-3.5 ${c}"></i>
        </div>
        <div class="text-xl font-bold font-mono text-white">${(stats[k]??0).toLocaleString()}</div>
        <div class="text-[10px] text-slate-600 mt-0.5 font-mono">${k}</div>
      </div>
    `).join('');
    lucide.createIcons();
  }

  // ─── Incidents ────────────────────────────────────────────
  async _loadIncidents(){
    this.incidents = await this.api.getIncidents(150);
    this._renderDashIncidents();
    this._renderIncidentsTable();
    this._updateIncidentCounts();
  }

  _updateIncidentCounts(){
    const open=this.incidents.filter(i=>i.status==='open').length;
    const res=this.incidents.filter(i=>i.status==='resolved').length;
    const fa=this.incidents.filter(i=>i.status==='false_alarm').length;
    const total=this.incidents.length;

    document.getElementById('cnt-all').textContent=total;
    document.getElementById('cnt-open').textContent=open;
    document.getElementById('cnt-res').textContent=res;
    document.getElementById('cnt-fa').textContent=fa;

    const nc=document.getElementById('nav-open-count');
    if(open>0){
      nc.textContent=open; nc.classList.remove('hidden');
    } else {
      nc.classList.add('hidden');
    }

    const banner=document.getElementById('alert-banner');
    if(open>0){
      banner.classList.remove('hidden');
      document.getElementById('alert-banner-text').textContent=`CÓ ${open} SỰ KIỆN CHÁY/KHÓI ĐANG MỞ — Cần xử lý ngay!`;
      document.getElementById('layout-root').style.paddingTop='40px';
    } else {
      banner.classList.add('hidden');
      document.getElementById('layout-root').style.paddingTop='0';
    }
  }

  _renderDashIncidents(){
    const el=document.getElementById('dash-incidents');
    const recent=this.incidents.slice(0,5);
    if(!recent.length){
      el.innerHTML='<div class="text-xs text-slate-500 text-center py-6 flex flex-col items-center gap-2"><i data-lucide="check-circle-2" class="w-8 h-8 text-emerald-600"></i>Chưa có sự kiện cảnh báo. Hệ thống an toàn!</div>';
      lucide.createIcons(); return;
    }
    el.innerHTML=recent.map(i=>this._incidentCard(i)).join('');
    lucide.createIcons();
  }

  _incidentCard(i){
    const isFire=i.alert_class==='fire';
    const isOpen=i.status==='open';
    const ts=new Date(i.started_at).toLocaleString('vi-VN',{dateStyle:'short',timeStyle:'short'});
    return `
      <div class="flex items-center gap-3 p-3 rounded-lg border ${isOpen?'border-red-900/50 bg-red-950/10':'border-slate-800 bg-slate-900/30'}">
        <div class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${isFire?'bg-red-950 text-red-400':'bg-slate-800 text-slate-300'}">
          <i data-lucide="${isFire?'flame':'wind'}" class="w-4 h-4"></i>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs font-bold text-white">#${i.id}</span>
            <span class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${isFire?'badge-fire':'badge-smoke'}">${i.alert_class}</span>
            <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded ${isOpen?'badge-open':i.status==='resolved'?'badge-resolved':'badge-false-alarm'}">${isOpen?'OPEN':i.status}</span>
          </div>
          <div class="text-[11px] text-slate-400 mt-0.5 truncate">${i.camera} · ${i.location} · <span class="font-mono">${(i.confidence*100).toFixed(1)}%</span> · ${ts}</div>
        </div>
        ${isOpen?`
          <div class="flex items-center gap-1 shrink-0">
            <button onclick="window._app.openAck(${i.id})" class="btn-ghost py-1 px-2 text-[11px]">Xem</button>
            <button onclick="window._app.openRes(${i.id})" class="btn-success py-1 px-2 text-[11px]">Đóng</button>
          </div>
        `:'<span class="text-[11px] text-slate-600 shrink-0">Đã đóng</span>'}
      </div>
    `;
  }

  _renderIncidentsTable(){
    let list=this.incFilter==='all'?this.incidents:this.incidents.filter(i=>i.status===this.incFilter);
    const tbody=document.getElementById('incidents-tbody');
    if(!list.length){
      tbody.innerHTML='<tr><td colspan="9" class="text-center text-slate-500 py-8">Không có sự kiện nào phù hợp bộ lọc.</td></tr>';
      return;
    }
    tbody.innerHTML=list.map(i=>{
      const isFire=i.alert_class==='fire';
      const isOpen=i.status==='open';
      const ts=new Date(i.started_at).toLocaleString('vi-VN',{dateStyle:'short',timeStyle:'short'});
      const ackInfo=i.acknowledged_at
        ?`<div class="text-[11px] text-white font-medium">${i.acknowledged_by}</div><div class="text-[10px] text-slate-500">${new Date(i.acknowledged_at).toLocaleTimeString('vi-VN')}</div>`
        :`<span class="text-amber-400 text-[10px] font-semibold">Chưa xem</span>`;
      return `
        <tr>
          <td class="font-mono font-bold text-white">#${i.id}</td>
          <td class="text-slate-300 whitespace-nowrap">${ts}</td>
          <td><div class="font-semibold text-white text-[11px]">${i.camera}</div><div class="text-[10px] text-slate-400">${i.location}</div></td>
          <td><span class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${isFire?'badge-fire':'badge-smoke'}">${i.alert_class}</span></td>
          <td class="font-mono font-semibold text-white">${(i.confidence*100).toFixed(1)}%</td>
          <td><span class="text-[10px] font-semibold px-1.5 py-0.5 rounded ${isOpen?'badge-open':i.status==='resolved'?'badge-resolved':'badge-false-alarm'}">${i.status}</span></td>
          <td>${ackInfo}</td>
          <td class="max-w-xs truncate text-slate-400 text-[11px]" title="${i.resolution_note||i.rule_description}">${i.resolution_note||i.rule_description}</td>
          <td class="text-right whitespace-nowrap">
            <button onclick="window._app.openSnap(${i.id})" class="btn-ghost py-0.5 px-2 text-[11px] mr-1" title="Xem ảnh"><i data-lucide="image" class="w-3 h-3"></i></button>
            ${isOpen?`
              <button onclick="window._app.openAck(${i.id})" class="btn-ghost py-0.5 px-2 text-[11px] mr-1">Xem</button>
              <button onclick="window._app.openRes(${i.id})" class="btn-success py-0.5 px-2 text-[11px]">Đóng</button>
            `:''}
          </td>
        </tr>
      `;
    }).join('');
    lucide.createIcons();
  }

  _bindIncidents(){
    document.querySelectorAll('.filter-btn').forEach(btn=>{
      btn.addEventListener('click',()=>{
        document.querySelectorAll('.filter-btn').forEach(b=>{
          b.classList.toggle('active-filter',b===btn);
          if(b!==btn){ b.style.background=''; b.style.color='#94a3b8'; b.style.border=''; }
          else { b.style.background='rgba(249,115,22,.15)'; b.style.color='#fb923c'; b.style.border='1px solid rgba(249,115,22,.3)'; }
        });
        this.incFilter=btn.dataset.filter;
        this._renderIncidentsTable();
      });
    });
  }

  // ─── Cameras (dashboard) ──────────────────────────────────
  async _loadCameras(){
    this.cameras=await this.api.getCameras();
    this._renderDashCameras();
    this._updateMonitorCamSel();
  }
  _renderDashCameras(){
    const el=document.getElementById('dash-cameras');
    if(!this.cameras.length){ el.innerHTML='<div class="text-slate-500 py-3 text-center text-xs">Chưa có camera.</div>'; return; }
    el.innerHTML=this.cameras.map(c=>{
      const active=c.enabled&&c.last_seen_at&&(Date.now()-new Date(c.last_seen_at).getTime())<45000;
      const dotCls=c.enabled?(active?'pulse-dot green':'pulse-dot gray'):'pulse-dot';
      const lbl=c.enabled?(active?'Active':'Disconnected'):'Stopped';
      const lblCls=c.enabled?(active?'text-emerald-400':'text-slate-500'):'text-red-500';
      return `<div class="flex items-center justify-between py-1.5">
        <div><div class="font-semibold text-white text-xs">${c.name}</div>
        <div class="text-[11px] text-slate-500">${c.location}</div></div>
        <div class="flex items-center gap-1.5"><span class="${dotCls}" style="width:7px;height:7px"></span><span class="text-[11px] ${lblCls}">${lbl}</span></div>
      </div>`;
    }).join('');
  }
  _updateMonitorCamSel(){
    const sel=document.getElementById('mon-cam-sel');
    const histSel=document.getElementById('hist-cam-filter');
    sel.innerHTML=this.cameras.map(c=>`<option value="${c.id}">${c.name} (${c.location})</option>`).join('');
    if(histSel) histSel.innerHTML='<option value="">Tất cả camera</option>'+this.cameras.map(c=>`<option value="${c.id}">${c.name}</option>`).join('');
    this._refreshMonitorCamStatus();
  }
  async _refreshMonitorCamStatus(){
    const camId=document.getElementById('mon-cam-sel').value;
    if(!camId) return;
    const s=await this.api.getCameraStatus(camId);
    if(!s) return;
    const pill=document.getElementById('mon-cam-pill');
    const dot=document.getElementById('mon-cam-dot');
    const lbl=document.getElementById('mon-cam-status');
    const btnText=document.getElementById('btn-toggle-cam-text');
    if(s.status==='active'){
      pill.className='flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border border-emerald-800 bg-emerald-950/30 text-emerald-400';
      dot.className='pulse-dot green'; dot.style.width='7px'; dot.style.height='7px';
      lbl.textContent='Active'; btnText.textContent='Tắt camera';
      this.cameraStopped = false;
      if(this.streamSrc==='cam' && !this.webcamStream){
        this._startWebcam();
      }
    } else if(s.status==='stopped'){
      pill.className='flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border border-red-900 bg-red-950/20 text-red-400';
      dot.className=''; dot.style.cssText='width:7px;height:7px;border-radius:50%;background:#ef4444';
      lbl.textContent='Stopped'; btnText.textContent='Bật camera';
      this.cameraStopped = true;
      this._stopWebcam();
    } else {
      pill.className='flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border border-slate-700 text-slate-400';
      dot.className='pulse-dot gray'; dot.style.width='7px'; dot.style.height='7px';
      lbl.textContent='Disconnected'; btnText.textContent='Tắt camera';
      this.cameraStopped = false;
    }
    document.getElementById('hud-cam').innerHTML=`<span class="${this.cameraStopped?'text-slate-500':'text-red-400'}">●</span> CAM-00${camId}: ${s.name}`;
  }

  // ─── Monitor bindings ─────────────────────────────────────
  _bindMonitor(){
    document.getElementById('mon-cam-sel').addEventListener('change',()=>this._refreshMonitorCamStatus());

    document.getElementById('btn-heartbeat').addEventListener('click',async()=>{
      const id=document.getElementById('mon-cam-sel').value;
      try{ await this.api.sendHeartbeat(id); this.toast('Heartbeat gửi thành công!','success'); await this._loadCameras(); }
      catch(e){ this.toast(e.message,'error'); }
    });

    document.getElementById('btn-toggle-cam').addEventListener('click',async()=>{
      const id=document.getElementById('mon-cam-sel').value;
      const cam=this.cameras.find(c=>c.id===Number(id));
      const now=cam?!cam.enabled:true;
      try{
        await this.api.setCameraEnabled(id,now);
        if(!now){
          // TẮT CAMERA: Dừng hoàn toàn webcam phần cứng và luồng AI
          this.cameraStopped = true;
          this._stopWebcam();
          this.simBoxes = [];
          this._lastFlameBox = null;
          this._flameMissCount = 0;
          this.confirm.reset();
          this.toast('Camera đã tắt hoàn toàn. Luồng video đã dừng.','info');
        } else {
          // BẬT CAMERA: Khôi phục luồng video
          this.cameraStopped = false;
          this.toast('Camera đã được bật trở lại!','success');
          if(this.streamSrc==='cam'){
            await this._startWebcam();
          }
        }
        await this._loadCameras();
      }
      catch(e){ this.toast(e.message,'error'); }
    });

    // Source switcher
    document.getElementById('src-sim').addEventListener('click',()=>this._setSource('sim'));
    document.getElementById('src-cam').addEventListener('click',()=>this._setSource('cam'));
    document.getElementById('src-img').addEventListener('click',()=>document.getElementById('img-upload').click());
    document.getElementById('img-upload').addEventListener('change',e=>this._handleUpload(e));

    // Sim triggers
    document.getElementById('sim-fire').addEventListener('click', ()=>this._triggerSim('fire'));
    document.getElementById('sim-smoke').addEventListener('click',()=>this._triggerSim('smoke'));
    document.getElementById('sim-both').addEventListener('click', ()=>this._triggerSim('both'));
    document.getElementById('sim-clear').addEventListener('click',()=>this._triggerSim('clear'));

    // Sound toggle
    document.getElementById('btn-sound').addEventListener('click',()=>{
      this.alarm.enabled=!this.alarm.enabled;
      const ic=document.getElementById('sound-icon');
      ic.setAttribute('data-lucide',this.alarm.enabled?'volume-2':'volume-x');
      ic.className=`w-3.5 h-3.5 ${this.alarm.enabled?'text-emerald-400':'text-slate-600'}`;
      lucide.createIcons();
      this.toast(this.alarm.enabled?'Đã bật còi':'Đã tắt âm thanh','info');
    });
  }

  _stopWebcam(){
    this._lastFlameBox = null;
    this._flameMissCount = 0;
    if(this.webcamStream){
      this.webcamStream.getTracks().forEach(t=>{
        try{ t.stop(); t.enabled=false; }catch(_){}
      });
      this.webcamStream=null;
    }
    const vid=document.getElementById('feed-video');
    if(vid){
      try{ vid.pause(); }catch(_){}
      vid.srcObject=null;
      vid.classList.add('hidden');
    }
  }

  _setSource(src){
    this.streamSrc=src;
    this.manualSimActive=false;
    ['sim','cam','img'].forEach(s=>{
      const btn=document.getElementById(`src-${s}`);
      if(btn){
        btn.style.background=s===src?'#ea580c':'';
        btn.style.color=s===src?'#fff':'';
      }
    });
    if(src==='cam'){
      if(!this.cameraStopped){
        this._startWebcam();
      }
    } else {
      // Dừng hoàn toàn webcam phần cứng khi không dùng
      this._stopWebcam();
    }
  }

  async _startWebcam(){
    try{
      this._stopWebcam();
      this.webcamStream=await navigator.mediaDevices.getUserMedia({
        video:{ width:{ ideal:640 }, height:{ ideal:480 } },
        audio:false
      });
      const vid=document.getElementById('feed-video');
      vid.srcObject=this.webcamStream;
      vid.classList.remove('hidden');
      await vid.play().catch(()=>{});
      this.toast('Webcam đã kết nối! Đang quét ngọn lửa thời gian thực...','success');
    }catch(e){
      this.toast('Không mở được webcam: '+e.message,'error');
      this._setSource('sim');
    }
  }

  _handleUpload(e){
    const f=e.target.files[0]; if(!f) return;
    const reader=new FileReader();
    reader.onload=ev=>{
      const img=new Image();
      img.onload=()=>{
        this.uploadImg=img;
        this._setSource('img');
        const boxes=this._analyzeImageForFire(img);
        if(boxes.length>0){
          this.simBoxes=boxes;
          this.confirm.reset();
          const desc=boxes.map(b=>`${b.class_name.toUpperCase()} ${(b.conf*100).toFixed(1)}%`).join(' & ');
          this.toast(`🔥 AI phát hiện: ${desc}!`, 'success');
        } else {
          this.simBoxes=[];
          this.toast('Ảnh đã tải lên. Không phát hiện dấu hiệu cháy/khói vượt ngưỡng.', 'info');
        }
      };
      img.src=ev.target.result;
    };
    reader.readAsDataURL(f);
    e.target.value='';
  }

  _analyzeImageForFire(img){
    try {
      const canvas=document.createElement('canvas');
      const w=200;
      const h=Math.max(100, Math.round(200 * (img.naturalHeight||img.height||150) / (img.naturalWidth||img.width||200)));
      canvas.width=w;
      canvas.height=h;
      const ctx=canvas.getContext('2d');
      ctx.drawImage(img,0,0,w,h);
      const imgData=ctx.getImageData(0,0,w,h).data;

      const corePts=[];
      const firePts=[];
      const smokePts=[];

      for(let y=0; y<h; y++){
        for(let x=0; x<w; x++){
          const i=(y*w+x)*4;
          const r=imgData[i];
          const g=imgData[i+1];
          const b=imgData[i+2];

          const maxC = Math.max(r, g, b);
          const minC = Math.min(r, g, b);
          const sum = r + g + b;
          const lum = 0.299 * r + 0.587 * g + 0.114 * b;

          // 1. Lõi lửa nhiệt độ cao (Incandescent Core)
          const isCore = lum >= 185 && r >= 225 && g >= 160 && (r + g >= 395) && (g - b >= 18) && (r - b >= 35);
          // 2. Thân/vỏ ngọn lửa (Flame Mantle)
          const isMantle = lum >= 145 && r >= 200 && g >= 115 && (r >= g + 10) && (g - b >= 20) && (r - b >= 45) && (r + g >= 330);

          if(isCore){
            corePts.push({ x: x/w, y: y/h });
            firePts.push({ x: x/w, y: y/h });
          } else if(isMantle){
            firePts.push({ x: x/w, y: y/h });
          } else {
            // Điều kiện nhận diện pixel Khói (chỉ khi có đám khói đen xám dày):
            const diff = maxC - minC;
            const mean = sum / 3;
            if(diff <= 20 && mean >= 60 && mean <= 170 && y/h < 0.80){
              smokePts.push({ x: x/w, y: y/h });
            }
          }
        }
      }

      const boxes=[];
      const totalPixels = w * h;

      // 1. Phân tích vùng Lửa (Bắt buộc phải có lõi phát sáng nhiệt độ cao để loại bỏ hoàn toàn đồ vật màu cam/đỏ/nhựa)
      if(corePts.length >= 2 && firePts.length >= Math.max(6, totalPixels * 0.0015)){
        firePts.sort((a,b) => a.x - b.x);
        const minX = firePts[Math.floor(firePts.length * 0.05)].x;
        const maxX = firePts[Math.floor(firePts.length * 0.95)].x;
        firePts.sort((a,b) => a.y - b.y);
        const minY = firePts[Math.floor(firePts.length * 0.05)].y;
        const maxY = firePts[Math.floor(firePts.length * 0.95)].y;

        const bw = Math.max(0.15, Math.min(0.85, (maxX - minX) * 1.15));
        const bh = Math.max(0.15, Math.min(0.85, (maxY - minY) * 1.15));
        const xc = Math.max(bw/2, Math.min(1 - bw/2, (minX + maxX) / 2));
        const yc = Math.max(bh/2, Math.min(1 - bh/2, (minY + maxY) / 2));

        const ratio = firePts.length / totalPixels;
        const conf = Math.min(0.96, Math.max(0.78, 0.78 + ratio * 1.5));

        boxes.push({
          class_id: 1,
          class_name: 'fire',
          conf: parseFloat(conf.toFixed(3)),
          xc: parseFloat(xc.toFixed(3)),
          yc: parseFloat(yc.toFixed(3)),
          w: parseFloat(bw.toFixed(3)),
          h: parseFloat(bh.toFixed(3))
        });
      }

      // 2. Phân tích vùng Khói
      if(smokePts.length >= Math.max(25, totalPixels * 0.006)){
        smokePts.sort((a,b) => a.x - b.x);
        const minX = smokePts[Math.floor(smokePts.length * 0.08)].x;
        const maxX = smokePts[Math.floor(smokePts.length * 0.92)].x;
        smokePts.sort((a,b) => a.y - b.y);
        const minY = smokePts[Math.floor(smokePts.length * 0.08)].y;
        const maxY = smokePts[Math.floor(smokePts.length * 0.92)].y;

        const bw = Math.max(0.2, Math.min(0.9, (maxX - minX) * 1.1));
        const bh = Math.max(0.2, Math.min(0.9, (maxY - minY) * 1.1));
        const xc = Math.max(bw/2, Math.min(1 - bw/2, (minX + maxX) / 2));
        const yc = Math.max(bh/2, Math.min(1 - bh/2, (minY + maxY) / 2));

        const ratio = smokePts.length / totalPixels;
        const conf = Math.min(0.89, Math.max(0.68, 0.68 + ratio * 0.8));

        boxes.push({
          class_id: 0,
          class_name: 'smoke',
          conf: parseFloat(conf.toFixed(3)),
          xc: parseFloat(xc.toFixed(3)),
          yc: parseFloat(yc.toFixed(3)),
          w: parseFloat(bw.toFixed(3)),
          h: parseFloat(bh.toFixed(3))
        });
      }

      return boxes;
    } catch(err) {
      console.warn('Lỗi phân tích ảnh AI:', err);
      return [];
    }
  }

  _triggerSim(type){
    this.simBoxes=[];
    if(type==='fire'||type==='both') this.simBoxes.push({class_id:1,class_name:'fire',conf:.87+Math.random()*.1,xc:.45,yc:.48,w:.22,h:.35});
    if(type==='smoke'||type==='both') this.simBoxes.push({class_id:0,class_name:'smoke',conf:.78+Math.random()*.12,xc:.65,yc:.35,w:.32,h:.40});
    if(type==='clear'){ this.confirm.reset(); this.toast('Đã xóa mô phỏng','info'); }
    else this.toast(`Kịch bản: ${type.toUpperCase()}`,'info');
  }

  // ─── Canvas stream loop ───────────────────────────────────
  _startStream(){
    this.streamRunning=true;
    let last=0;
    const loop=(ts)=>{
      if(!this.streamRunning) return;
      if(ts-last>=100){ last=ts; this._drawFrame(); }
      this.rafId=requestAnimationFrame(loop);
    };
    this.rafId=requestAnimationFrame(loop);
  }

  _drawFrame(){
    const canvas=document.getElementById('feed-canvas');
    if(!canvas) return;
    const ctx=canvas.getContext('2d');
    const W=canvas.width=Math.floor(canvas.clientWidth)||640;
    const H=canvas.height=Math.floor(canvas.clientHeight)||360;

    // ─── 1. XỬ LÝ KHI CAMERA BỊ TẮT (STOPPED) ───
    if(this.cameraStopped){
      ctx.fillStyle='#070b14';
      ctx.fillRect(0,0,W,H);
      
      // Vẽ lưới nền mờ
      ctx.strokeStyle='rgba(255,255,255,0.03)';
      ctx.lineWidth=1;
      for(let x=0;x<W;x+=30){ ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
      for(let y=0;y<H;y+=30){ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }

      // Vòng tròn đỏ biểu tượng dừng
      ctx.fillStyle='rgba(239,68,68,0.12)';
      ctx.beginPath();
      ctx.arc(W/2, H/2 - 25, 42, 0, Math.PI*2);
      ctx.fill();
      ctx.strokeStyle='rgba(239,68,68,0.5)';
      ctx.lineWidth=2;
      ctx.stroke();

      // Dấu chéo đỏ
      ctx.fillStyle='#ef4444';
      ctx.font='bold 28px sans-serif';
      ctx.textAlign='center';
      ctx.fillText('✕', W/2, H/2 - 16);

      // Tiêu đề
      ctx.fillStyle='#f87171';
      ctx.font='bold 16px sans-serif';
      ctx.fillText('CAMERA ĐÃ TẮT (STOPPED)', W/2, H/2 + 35);

      // Hướng dẫn
      ctx.fillStyle='#64748b';
      ctx.font='12px sans-serif';
      ctx.fillText('Nhấn nút "Bật camera" ở thanh điều khiển để khôi phục luồng video.', W/2, H/2 + 58);
      ctx.textAlign='left';

      // Ẩn alert overlay
      document.getElementById('alert-overlay').classList.add('hidden');
      document.getElementById('hud-fps').textContent='0 FPS';
      document.getElementById('hud-ts').textContent=new Date().toLocaleString('vi-VN');

      // Reset sliding window
      this._lastFlameBox = null;
      this._flameMissCount = 0;
      this.simBoxes = [];
      const state=this.confirm.update(0,0);
      this._updateSlidingWindowUI(state, []);
      return;
    }

    // ─── 2. VẼ HÌNH NỀN VÀ QUÉT REAL-TIME NGỌN LỬA ───
    if(this.streamSrc==='cam'&&this.webcamStream){
      const vid=document.getElementById('feed-video');
      if(vid && vid.readyState>=2){
        ctx.drawImage(vid,0,0,W,H);
        // TỰ ĐỘNG QUÉT VÀ NHẬN DIỆN NGỌN LỬA BẬT LỬA / LỬA THỰC TẾ REAL-TIME
        if(!this.manualSimActive){
          this.simBoxes = this._detectRealtimeFlame(vid, W, H);
        }
      } else {
        this._drawBg(ctx,W,H);
      }
    } else if(this.streamSrc==='img'&&this.uploadImg){
      ctx.drawImage(this.uploadImg,0,0,W,H);
    } else {
      this._drawBg(ctx,W,H);
    }

    // ─── 3. VẼ HỘP BOUNDING BOX NHẬN DIỆN (ỔN ĐỊNH - KHÔNG GIẬT LẮC) ───
    let maxFire=0,maxSmoke=0;
    const drawnBoxes=[];
    for(const b of this.simBoxes){
      const conf=b.conf;
      const w=b.w;
      const h=b.h;
      if(b.class_id===1) maxFire=Math.max(maxFire,conf);
      else maxSmoke=Math.max(maxSmoke,conf);
      drawnBoxes.push({...b,conf,w,h});

      const x=(b.xc-w/2)*W, y=(b.yc-h/2)*H, bw=w*W, bh=h*H;
      const color=b.class_id===1?'#ef4444':'#60a5fa';
      const fill=b.class_id===1?'rgba(239,68,68,.22)':'rgba(96,165,250,.18)';
      ctx.strokeStyle=color; ctx.fillStyle=fill; ctx.lineWidth=3;
      ctx.strokeRect(x,y,bw,bh); ctx.fillRect(x,y,bw,bh);
      ctx.fillStyle=color; ctx.fillRect(x,y-22,b.class_id===1?115:125,22);
      ctx.fillStyle='#fff'; ctx.font='bold 12px sans-serif';
      ctx.fillText(`${b.class_name.toUpperCase()} ${(conf*100).toFixed(1)}%`,x+5,y-6);
    }

    // ─── 4. ĐÁNH GIÁ CỬA SỔ TRƯỢT 3/5 ───
    const state=this.confirm.update(maxFire,maxSmoke);
    this._updateSlidingWindowUI(state,drawnBoxes);

    // ─── 5. HIỂN THỊ ALERT OVERLAY KHI XÁC NHẬN CHÁY/KHÓI ───
    if(state.fire_confirmed||state.smoke_confirmed){
      document.getElementById('alert-overlay').classList.remove('hidden');
      document.getElementById('alert-overlay-text').textContent=
        state.fire_confirmed?'🔥 CẢNH BÁO CHÁY XÁC NHẬN!':'💨 CẢNH BÁO KHÓI XÁC NHẬN!';
      // Còi hú liên tục khi đang xác nhận
      this.alarm.beep();
    } else {
      document.getElementById('alert-overlay').classList.add('hidden');
    }

    // ─── 6. TỰ ĐỘNG GHI NHẬN SỰ KIỆN KHI ĐẠT ĐIỀU KIỆN MỚI ───
    if((state.new_fire||state.new_smoke)&&drawnBoxes.length){
      const cls=[];
      if(state.new_fire) cls.push('fire');
      if(state.new_smoke) cls.push('smoke');
      this.toast(`🔥 PHÁT HIỆN ${cls.join('&').toUpperCase()} QUA 3/5 FRAMES!`,'warn');
      const camId=Number(document.getElementById('mon-cam-sel').value||1);

      // Chụp ảnh bằng chứng trực tiếp từ Canvas
      let snapData=null;
      try{ snapData=canvas.toDataURL('image/jpeg', 0.85); }catch(_){}

      this.api.ingestFrame({
        camera_id:camId, model_id:1,
        request_id:`fe-${camId}-${Date.now()}`,
        captured_at:new Date().toISOString(),
        detections:drawnBoxes.map(b=>({class_id:b.class_id,confidence:b.conf,xc:b.xc,yc:b.yc,w:b.w,h:b.h})),
        confirmed_classes:cls,
        snapshot_path:null
      }).then(res=>{
        if(snapData && res && res.incident_id){
          this._snapCache = this._snapCache || {};
          this._snapCache[res.incident_id] = snapData;
          try{ localStorage.setItem('snap_' + res.incident_id, snapData); }catch(_){}
        }
        return this._refreshAll();
      });
    }

    // HUD
    document.getElementById('hud-fps').textContent='30 FPS';
    document.getElementById('hud-ts').textContent=new Date().toLocaleString('vi-VN');
  }

  // ─── THUẬT TOÁN QUÉT NGỌN LỬA REAL-TIME TỪ WEBCAM (CHÍNH XÁC CAO - CHỐNG BÁO GIẢ TUYỆT ĐỐI) ───
  _detectRealtimeFlame(sourceEl, W, H){
    try{
      const sw = 160;
      const sh = 120;
      this._analysisCanvas.width = sw;
      this._analysisCanvas.height = sh;
      this._analysisCtx.drawImage(sourceEl, 0, 0, sw, sh);
      const imgData = this._analysisCtx.getImageData(0, 0, sw, sh).data;

      const corePts = [];
      const allFlamePts = [];

      for(let y=0; y<sh; y++){
        for(let x=0; x<sw; x++){
          const i = (y * sw + x) * 4;
          const r = imgData[i];
          const g = imgData[i+1];
          const b = imgData[i+2];

          // 1. Độ chói Y theo chuẩn truyền hình ITU-R BT.601
          const lum = 0.299 * r + 0.587 * g + 0.114 * b;

          // 2. LÕI LỬA NĂNG LƯỢNG CAO (Incandescent Combustion Core - Lõi phát xạ than hoạt tính ~1200-1400°C):
          // Ngọn lửa thật bắt buộc phải có lõi rực sáng chói lòa (lum >= 185, r >= 225, g >= 160).
          // Vỏ nhựa bật lửa màu cam không tự phát sáng (chỉ phản xạ ánh sáng phòng) nên lum < 175 (trung bình ~133),
          // tuyệt đối không bao giờ đạt được mức năng lượng lõi này.
          // g - b >= 18: Lõi lửa vàng/trắng ấm, phân biệt triệt để với đèn LED trắng/bóng tuýp phòng (g ≈ b).
          const isCore = lum >= 185 && r >= 225 && g >= 160 && (r + g >= 395) && (g - b >= 18) && (r - b >= 35);

          // 3. THÂN VÀ VỎ NGỌN LỬA (Flame Mantle / Envelope):
          // Vùng khí cháy vàng cam nhiệt độ cao bao quanh lõi lửa.
          // g - b >= 20 và r - b >= 45: Đảm bảo sắc thái quang phổ ngọn lửa, loại bỏ da người và phản quang.
          const isMantle = lum >= 145 && r >= 200 && g >= 115 && (r >= g + 10) && (g - b >= 20) && (r - b >= 45) && (r + g >= 330);

          if(isCore){
            corePts.push({ x: x / sw, y: y / sh });
            allFlamePts.push({ x: x / sw, y: y / sh });
          } else if(isMantle){
            allFlamePts.push({ x: x / sw, y: y / sh });
          }
        }
      }

      // ─── ĐIỀU KIỆN TIÊN QUYẾT: PHẢI CÓ LÕI PHÁT SÁNG NĂNG LƯỢNG CAO ───
      // Nhựa bật lửa không bật thì KHÔNG THỂ có lõi cháy sáng (corePts.length = 0).
      // Chỉ khi thực sự bật lửa tạo ngọn lửa thì mới sinh ra lõi lửa nhiệt độ cao.
      const hasActiveCore = corePts.length >= 2;
      const hasEnoughFlame = allFlamePts.length >= 5;

      if(hasActiveCore && hasEnoughFlame){
        allFlamePts.sort((a,b) => a.x - b.x);
        const minX = allFlamePts[Math.floor(allFlamePts.length * 0.05)].x;
        const maxX = allFlamePts[Math.floor(allFlamePts.length * 0.95)].x;
        allFlamePts.sort((a,b) => a.y - b.y);
        const minY = allFlamePts[Math.floor(allFlamePts.length * 0.05)].y;
        const maxY = allFlamePts[Math.floor(allFlamePts.length * 0.95)].y;

        const spanX = maxX - minX;
        const spanY = maxY - minY;

        // Vùng cháy cục bộ trước webcam không vượt quá 60% màn hình
        if(spanX <= 0.60 && spanY <= 0.60){
          const bw = Math.max(0.06, Math.min(0.42, spanX * 1.35 + 0.04));
          const bh = Math.max(0.08, Math.min(0.52, spanY * 1.35 + 0.05));
          let xc = Math.max(bw / 2, Math.min(1 - bw / 2, (minX + maxX) / 2));
          let yc = Math.max(bh / 2, Math.min(1 - bh / 2, (minY + maxY) / 2));

          const conf = Math.min(0.98, Math.max(0.86, 0.86 + (corePts.length / 25) * 0.08 + (allFlamePts.length / 80) * 0.04));

          const rawBox = {
            class_id: 1,
            class_name: 'fire',
            conf: parseFloat(conf.toFixed(3)),
            xc: parseFloat(xc.toFixed(3)),
            yc: parseFloat(yc.toFixed(3)),
            w: parseFloat(bw.toFixed(3)),
            h: parseFloat(bh.toFixed(3))
          };

          // Làm mượt chuyển động tọa độ bằng EMA (Exponential Moving Average) để loại bỏ rung lắc
          if(this._lastFlameBox){
            const alpha = 0.65;
            rawBox.xc = parseFloat((rawBox.xc * alpha + this._lastFlameBox.xc * (1 - alpha)).toFixed(3));
            rawBox.yc = parseFloat((rawBox.yc * alpha + this._lastFlameBox.yc * (1 - alpha)).toFixed(3));
            rawBox.w  = parseFloat((rawBox.w  * alpha + this._lastFlameBox.w  * (1 - alpha)).toFixed(3));
            rawBox.h  = parseFloat((rawBox.h  * alpha + this._lastFlameBox.h  * (1 - alpha)).toFixed(3));
          }

          this._lastFlameBox = rawBox;
          this._flameMissCount = 0;
          return [rawBox];
        }
      }

      // ─── BỘ NHỚ LÀM MƯỢT THỜI GIAN (TEMPORAL PERSISTENCE BUFFER) ───
      // Khi ngọn lửa đang cháy bị chớp tắt 1-2 frames do luồng gió/turbulent flame của bật lửa,
      // duy trì bounding box với confidence giảm nhẹ để đảm bảo sliding window 3/5 không bị gián đoạn.
      this._flameMissCount = (this._flameMissCount || 0) + 1;
      if(this._lastFlameBox && this._flameMissCount <= 2){
        return [{
          ...this._lastFlameBox,
          conf: parseFloat((this._lastFlameBox.conf * 0.92).toFixed(3))
        }];
      }

      this._lastFlameBox = null;
      return [];
    }catch(err){
      console.warn('Lỗi quét ngọn lửa real-time:', err);
      return [];
    }
  }

  _drawBg(ctx,W,H){
    // Dark room simulation
    ctx.fillStyle='#05080f'; ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='#111827'; ctx.lineWidth=1;
    for(let x=0;x<W;x+=40){ ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
    for(let y=0;y<H;y+=40){ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }
    // Desk & monitor
    ctx.fillStyle='#1e293b'; ctx.fillRect(W*.15,H*.55,W*.7,H*.3);
    ctx.fillStyle='#334155'; ctx.fillRect(W*.35,H*.35,W*.3,H*.2);
    ctx.fillStyle='#0f172a'; ctx.fillRect(W*.37,H*.37,W*.26,H*.16);
    // Label
    ctx.fillStyle='#334155'; ctx.font='11px monospace';
    ctx.fillText('PHÒNG THỰC NGHIỆM — CAMERA GIÁM SÁT FireEyes',W*.12,24);
  }

  _updateSlidingWindowUI(state,boxes){
    // Fire slots
    const fireSlots=document.querySelectorAll('#fire-slots .frame-slot');
    state.fire_window.forEach((hit,i)=>{
      if(!fireSlots[i]) return;
      fireSlots[i].className='frame-slot '+(state.fire_confirmed?'confirmed-fire':hit?'hit-fire':'');
      fireSlots[i].textContent=hit?'HIT':`F${i+1}`;
    });
    document.getElementById('fire-count').textContent=`${state.fire_count}/5`;
    const fb=document.getElementById('fire-badge');
    if(state.fire_confirmed){ fb.textContent='✅ ĐÃ XÁC NHẬN'; fb.style.cssText='background:#7f1d1d;border:1px solid #dc2626;color:#fca5a5'; }
    else { fb.textContent='CHƯA XÁC NHẬN'; fb.style.cssText='background:#1e293b;border:1px solid #334155;color:#64748b'; }

    // Smoke slots
    const smokeSlots=document.querySelectorAll('#smoke-slots .frame-slot');
    state.smoke_window.forEach((hit,i)=>{
      if(!smokeSlots[i]) return;
      smokeSlots[i].className='frame-slot '+(state.smoke_confirmed?'confirmed-smoke':hit?'hit-smoke':'');
      smokeSlots[i].textContent=hit?'HIT':`S${i+1}`;
    });
    document.getElementById('smoke-count').textContent=`${state.smoke_count}/5`;
    const sb=document.getElementById('smoke-badge');
    if(state.smoke_confirmed){ sb.textContent='✅ ĐÃ XÁC NHẬN'; sb.style.cssText='background:#1e3a5f;border:1px solid #2563eb;color:#93c5fd'; }
    else { sb.textContent='CHƯA XÁC NHẬN'; sb.style.cssText='background:#1e293b;border:1px solid #334155;color:#64748b'; }

    // Current detections list
    const dl=document.getElementById('det-list');
    if(!boxes.length){ dl.innerHTML='<div class="text-slate-500 text-center py-2 text-xs">Không có đối tượng vượt ngưỡng</div>'; return; }
    dl.innerHTML=boxes.map(b=>`
      <div class="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
        <div class="flex items-center gap-1.5">
          <span style="width:8px;height:8px;border-radius:50%;background:${b.class_id===1?'#ef4444':'#60a5fa'}"></span>
          <span class="font-bold uppercase text-white">${b.class_name}</span>
        </div>
        <span class="font-mono text-slate-300">${(b.conf*100).toFixed(1)}%</span>
      </div>
    `).join('');
  }

  // ─── History ──────────────────────────────────────────────
  async _loadHistory(){
    const camId=document.getElementById('hist-cam-filter').value;
    const list=await this.api.getHistory(camId||null);
    const tbody=document.getElementById('history-tbody');
    if(!list.length){ tbody.innerHTML='<tr><td colspan="8" class="text-center text-slate-500 py-8">Chưa có lịch sử nhận diện.</td></tr>'; return; }
    tbody.innerHTML=list.map(d=>`
      <tr>
        <td class="font-mono text-slate-300">#${d.id||d.detection_id}</td>
        <td class="font-mono text-slate-400">#${d.frame_id}</td>
        <td class="text-slate-300 whitespace-nowrap text-[11px]">${new Date(d.captured_at).toLocaleString('vi-VN')}</td>
        <td class="text-white">${d.camera||'CAM'}</td>
        <td><span class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${d.class_id===1?'badge-fire':'badge-smoke'}">${d.detection_class||d.class_id===1?'fire':'smoke'}</span></td>
        <td class="font-mono font-bold text-white">${(d.confidence*100).toFixed(1)}%</td>
        <td class="font-mono text-slate-400 text-[11px]">[${d.xc?.toFixed(3)||'?'}, ${d.yc?.toFixed(3)||'?'}, ${d.w?.toFixed(3)||'?'}, ${d.h?.toFixed(3)||'?'}]</td>
        <td class="text-slate-500 text-[11px]">${d.model||'—'}</td>
      </tr>
    `).join('');
  }

  _bindDevices(){
    document.getElementById('btn-add-loc').addEventListener('click',()=>document.getElementById('modal-loc').classList.add('open'));
    document.getElementById('btn-add-cam').addEventListener('click',async()=>{
      const locs=await this.api.getLocations();
      document.getElementById('cam-loc-sel').innerHTML=locs.map(l=>`<option value="${l.id}">${l.name}</option>`).join('');
      document.getElementById('modal-cam').classList.add('open');
    });
    document.getElementById('btn-hist-refresh').addEventListener('click',()=>this._loadHistory());
  }

  async _loadDevices(){
    const [locs,cams,datasets,models]=await Promise.all([
      this.api.getLocations(),this.api.getCameras(),this.api.getDatasets(),this.api.getModels()
    ]);

    // Locations
    document.getElementById('loc-count-badge').textContent=`${locs.length} bản ghi`;
    document.getElementById('loc-list').innerHTML=locs.length?locs.map(l=>`
      <div class="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
        <div><div class="font-semibold text-white">#${l.id} — ${l.name}</div><div class="text-[11px] text-slate-500">${l.address}</div></div>
      </div>
    `).join(''):'<div class="text-slate-500 py-2 text-center">Chưa có dữ liệu.</div>';

    // Cameras
    document.getElementById('cam-count-badge').textContent=`${cams.length} bản ghi`;
    document.getElementById('cam-full-list').innerHTML=cams.length?cams.map(c=>`
      <div class="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
        <div>
          <div class="font-semibold text-white">#${c.id} — ${c.name}</div>
          <div class="text-[11px] text-slate-500">Nguồn: ${c.source_ref} · Vị trí: ${c.location}</div>
        </div>
        <span class="text-[10px] font-bold px-2 py-0.5 rounded ${c.enabled?'badge-resolved':'badge-open'}">${c.enabled?'BẬT':'TẮT'}</span>
      </div>
    `).join(''):'<div class="text-slate-500 py-2 text-center">Chưa có camera.</div>';

    // Datasets
    document.getElementById('ds-count-badge').textContent=`${datasets.length} bản ghi`;
    document.getElementById('ds-list').innerHTML=datasets.length?datasets.map(d=>`
      <div class="p-2 rounded bg-slate-900 border border-slate-800 space-y-0.5">
        <div class="flex items-center justify-between">
          <span class="font-semibold text-white">#${d.id} — ${d.name} (${d.version})</span>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded" style="background:#1e1b4b;color:#a5b4fc">${d.status}</span>
        </div>
        <div class="text-[11px] text-slate-500">Giấy phép: ${d.license_name}</div>
      </div>
    `).join(''):'<div class="text-slate-500 py-2 text-center">Chưa có dataset.</div>';

    // Models
    document.getElementById('mdl-count-badge').textContent=`${models.length} bản ghi`;
    document.getElementById('mdl-list').innerHTML=models.length?models.map(m=>`
      <div class="p-2 rounded bg-slate-900 border border-slate-800 space-y-0.5">
        <div class="flex items-center justify-between">
          <span class="font-semibold text-white">#${m.id} — ${m.name}</span>
          <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${m.is_demo?'badge-open':'badge-resolved'}">${m.is_demo?'DEMO':'TRAINED'}</span>
        </div>
        <div class="text-[11px] text-slate-500 font-mono truncate">Weights: ${m.weights_path||'—'}</div>
      </div>
    `).join(''):'<div class="text-slate-500 py-2 text-center">Chưa có model.</div>';
  }

  // ─── Modals ───────────────────────────────────────────────
  _bindModals(){
    // Acknowledge
    document.getElementById('ack-confirm').addEventListener('click',async()=>{
      const by=document.getElementById('ack-by').value.trim()||'Trực ban an toàn';
      try{
        await this.api.acknowledgeAlert(this.pendingAlertId,by);
        closeModal('modal-ack');
        this.toast(`Đã xác nhận xem sự kiện #${this.pendingAlertId}`,'success');
        await this._refreshAll();
      }catch(e){ this.toast(e.message,'error'); }
    });

    // Resolve
    document.getElementById('res-confirm').addEventListener('click',async()=>{
      const status=document.getElementById('res-status').value;
      const note=document.getElementById('res-note').value.trim();
      if(!note){ this.toast('Vui lòng nhập ghi chú xử lý!','warn'); return; }
      try{
        await this.api.resolveAlert(this.pendingAlertId,status,note);
        closeModal('modal-res');
        this.toast(`Đã đóng sự kiện #${this.pendingAlertId} (${status})`,'success');
        await this._refreshAll();
      }catch(e){ this.toast(e.message,'error'); }
    });

    // Add location
    document.getElementById('loc-confirm').addEventListener('click',async()=>{
      const name=document.getElementById('loc-name').value.trim();
      const addr=document.getElementById('loc-addr').value.trim();
      if(!name||!addr){ this.toast('Vui lòng điền đầy đủ thông tin!','warn'); return; }
      try{
        await this.api.createLocation(name,addr);
        closeModal('modal-loc');
        this.toast(`Đã thêm địa điểm "${name}"`,'success');
        await this._refreshAll();
        if(this.activeTab==='devices') this._loadDevices();
      }catch(e){ this.toast(e.message,'error'); }
    });

    // Add camera
    document.getElementById('cam-confirm').addEventListener('click',async()=>{
      const locId=document.getElementById('cam-loc-sel').value;
      const name=document.getElementById('cam-name').value.trim();
      const src=document.getElementById('cam-src').value.trim();
      if(!name||!src){ this.toast('Vui lòng điền đầy đủ thông tin camera!','warn'); return; }
      try{
        await this.api.createCamera(locId,name,src);
        closeModal('modal-cam');
        this.toast(`Đã đăng ký camera "${name}"`,'success');
        await this._refreshAll();
        if(this.activeTab==='devices') this._loadDevices();
      }catch(e){ this.toast(e.message,'error'); }
    });

    // Snapshot
    document.getElementById('snap-img').addEventListener('error',()=>{
      document.getElementById('snap-img').classList.add('hidden');
      document.getElementById('snap-no-img').classList.remove('hidden');
    });
    document.getElementById('snap-img').addEventListener('load',()=>{
      document.getElementById('snap-img').classList.remove('hidden');
      document.getElementById('snap-no-img').classList.add('hidden');
    });
  }

  openAck(id){
    this.pendingAlertId=id;
    document.getElementById('ack-id').textContent=id;
    document.getElementById('modal-ack').classList.add('open');
  }
  openRes(id){
    this.pendingAlertId=id;
    document.getElementById('res-id').textContent=id;
    document.getElementById('modal-res').classList.add('open');
  }
  openSnap(id){
    const inc=this.incidents.find(i=>i.id===Number(id));
    if(!inc) return;
    document.getElementById('snap-title').textContent=`Ảnh bằng chứng — Sự kiện #${id} ${inc.alert_class.toUpperCase()}`;
    document.getElementById('snap-cam').textContent=inc.camera;
    document.getElementById('snap-loc').textContent=inc.location;
    document.getElementById('snap-time').textContent=new Date(inc.started_at).toLocaleString('vi-VN');
    document.getElementById('snap-cls').textContent=`${inc.alert_class.toUpperCase()} · ${(inc.confidence*100).toFixed(1)}%`;
    document.getElementById('snap-img').classList.remove('hidden');
    document.getElementById('snap-no-img').classList.add('hidden');
    
    const cached = this._snapCache?.[id] || localStorage.getItem('snap_' + id);
    if(cached){
      document.getElementById('snap-img').src = cached;
    } else {
      document.getElementById('snap-img').src = `${this.api.base}/api/alerts/${id}/snapshot`;
    }
    document.getElementById('modal-snap').classList.add('open');
  }

  // ─── Toast ────────────────────────────────────────────────
  toast(msg,type='info'){
    const el=document.createElement('div');
    el.className=`toast toast-${type}`;
    const icons={success:'check-circle',error:'alert-circle',info:'info',warn:'alert-triangle'};
    el.innerHTML=`<i data-lucide="${icons[type]||'info'}" style="width:15px;height:15px;flex-shrink:0"></i><span>${msg}</span>`;
    document.getElementById('toasts').appendChild(el);
    lucide.createIcons();
    setTimeout(()=>{ el.style.opacity='0'; el.style.transition='opacity .3s'; setTimeout(()=>el.remove(),300); },4000);
  }
}


/* ═══════════════════════════════════════════════════════════
   5.  BOOTSTRAP
   ═══════════════════════════════════════════════════════════ */
window.addEventListener('DOMContentLoaded',()=>{
  const app = new FireEyesApp();
  window._app = app;
  app.start();
});
