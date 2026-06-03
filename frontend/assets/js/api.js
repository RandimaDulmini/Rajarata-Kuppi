const API_BASE = localStorage.getItem('rk_api_base') || 'http://127.0.0.1:8000/api';

function token(){ return localStorage.getItem('rk_token'); }
function authHeaders(){ return token() ? { Authorization: `Bearer ${token()}` } : {}; }
async function api(path, options = {}){
  const headers = { ...(options.headers || {}), ...authHeaders() };
  if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if(!res.ok){
    let msg = 'API request failed';
    try { msg = (await res.json()).detail || msg; } catch(e) {}
    throw new Error(msg);
  }
  return res.json();
}

function moneyText(n){ return Number(n || 0).toLocaleString(); }
function deptColor(code){ return String(code || '').toLowerCase(); }

const DEPARTMENT_OPTIONS = [
  { label: 'Accountancy and Finance', code: 'ACF' },
  { label: 'Business Management', code: 'MGT' },
  { label: 'Human Resource Management', code: 'HRM' },
  { label: 'Information Systems', code: 'ITM' },
  { label: 'Marketing Management', code: 'MKT' },
  { label: 'Tourism and Hospitality Management', code: 'THM' },
];

function departmentLabel(value){
  const text = String(value || '').trim();
  if(!text) return '';
  const found = DEPARTMENT_OPTIONS.find(option => option.code === text.toUpperCase() || option.label.toLowerCase() === text.toLowerCase());
  return found ? found.label : text;
}

function departmentCodeFromLabel(label){
  const found = DEPARTMENT_OPTIONS.find(option => option.label.toLowerCase() === String(label || '').trim().toLowerCase());
  return found ? found.code : '';
}

function departmentSelectHtml(selected=''){
  const selectedLabel = departmentLabel(selected);
  return `<option value="">Select your department</option>${DEPARTMENT_OPTIONS.map(option => `<option value="${option.label}"${option.label === selectedLabel ? ' selected' : ''}>${option.label}</option>`).join('')}`;
}

async function loginUser(email, password){
  const data = await api('/auth/login', { method:'POST', body: JSON.stringify({ email, password }) });
  localStorage.setItem('rk_token', data.access_token);
  return data;
}
async function registerUser(payload){
  return api('/auth/register', { method:'POST', body: JSON.stringify(payload) });
}
async function updateProfile(payload){
  return api('/profile', { method:'PUT', body: JSON.stringify(payload) });
}
function showToast(message, type='success'){
  const container = document.getElementById('toast-container');
  if(!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(()=>{ toast.classList.add('visible'); }, 10);
  setTimeout(()=>{ toast.classList.remove('visible'); setTimeout(()=>toast.remove(),300); }, 3000);
}
function logoutUser(){ localStorage.removeItem('rk_token'); location.href = 'login.html'; }

function updateAuthButtons(){
  const loggedIn = Boolean(token());
  const loginBtn = document.getElementById('topbar-login');
  const signupBtn = document.getElementById('topbar-signup');
  const profileMenu = document.getElementById('topbar-profile');
  if(loginBtn) loginBtn.style.display = loggedIn ? 'none' : 'inline-flex';
  if(signupBtn) signupBtn.style.display = loggedIn ? 'none' : 'inline-flex';
  if(profileMenu) profileMenu.style.display = loggedIn ? 'inline-flex' : 'none';
}

function initTopbarMenu(){
  const profileMenu = document.getElementById('topbar-profile');
  const avatar = document.getElementById('topbar-avatar');
  if(!profileMenu || !avatar) return;
  avatar.addEventListener('click', (event) => {
    event.stopPropagation();
    profileMenu.classList.toggle('open');
  });
  document.addEventListener('click', (event) => {
    if(!profileMenu.contains(event.target)) profileMenu.classList.remove('open');
  });
}

async function initStats(){
  const statsRow = document.querySelector('.stats-row');
  if(!statsRow) return;
  try{
    const s = await api('/stats/home');
    const vals = statsRow.querySelectorAll('.stat-card .val');
    if(vals[0]) vals[0].textContent = `${moneyText(Math.max(s.students, 4600))}+`;
    if(vals[1]) vals[1].textContent = s.departments;
    if(vals[2]) vals[2].textContent = `${Math.max(s.modules, 125)}+`;
    const badge = document.getElementById('notif-dot');
    if(badge){ badge.textContent = s.unread_notifications; badge.style.display = s.unread_notifications ? 'inline' : 'none'; }
  }catch(err){ console.warn(err.message); }
}

function resourceCard(r){
  const cls = deptColor(r.department_code);
  const action = r.resource_type === 'video' ? '▶ Watch' : '⬇ Download';
  return `<div class="note-card" data-dept="${r.department_code}">
    <div class="note-badge ${cls}">${r.department_code}<br><span style="font-size:8px;font-weight:500">${r.file_type}</span></div>
    <div class="note-body">
      <div class="note-title">${r.title}</div>
      <div class="note-desc">${r.description || ''}</div>
      <div class="note-meta"><span class="tag">${r.module_code || r.department_code}</span><span class="tag">${r.downloads} downloads</span>${r.is_new ? '<span class="tag">New</span>' : ''}</div>
    </div>
    <button class="btn-dl" onclick="downloadResource(${r.id}, '${r.file_url || '#'}')">${action}</button>
  </div>`;
}

async function downloadResource(id, url){
  try{ await api(`/resources/${id}/download`, { method:'POST' }); }catch(e){}
  if(url && url !== '#') window.open(url.startsWith('/uploads') ? `http://127.0.0.1:8000${url}` : url, '_blank');
  else alert('This sample resource has no uploaded file yet.');
}

async function initResources(){
  try{
    const page = location.pathname.split('/').pop() || 'index.html';
    if(page === 'notes.html'){
      const list = document.querySelector('.notes-list');
      const data = await api('/resources?resource_type=note&limit=50');
      if(list && data.length) list.innerHTML = data.map(resourceCard).join('');
    }
    if(page === 'pastpapers.html'){
      const list = document.getElementById('papers-list');
      const data = await api('/resources?resource_type=pastpaper&limit=50');
      if(list && data.length) list.innerHTML = data.map(resourceCard).join('');
    }
    if(page === 'index.html'){
      const latest = document.querySelector('.notes-list');
      const data = await api('/resources?limit=3');
      if(latest && data.length) latest.innerHTML = data.map(resourceCard).join('');
    }
    if(page === 'student-material.html'){
      const typeToPanel = { ppt:'mat-ppt', lecture:'mat-lecture', tutorial:'mat-tutorial' };
      for(const [type, panelId] of Object.entries(typeToPanel)){
        const panel = document.getElementById(panelId);
        const grid = panel?.querySelector('.mat-grid');
        if(!grid) continue;
        const data = await api(`/resources?resource_type=${type}&limit=50`);
        if(data.length){
          grid.innerHTML = data.map(r => `<div class="mat-card">
            <div class="mat-card-head"><div class="mat-icon ${type === 'ppt' ? 'ppt' : type === 'lecture' ? 'note' : 'tut'}"></div>
              <div><div class="mat-card-title">${r.title}</div><div class="mat-card-sub">${r.module_code || ''} · ${r.department_code}<br>${r.description || ''}</div></div></div>
            <div class="mat-card-foot"><div class="mat-tags"><span class="mat-tag">${r.file_type}</span><span class="mat-tag">${r.department_code}</span></div><button class="btn-dl" onclick="downloadResource(${r.id}, '${r.file_url || '#'}')">⬇ Download</button></div>
          </div>`).join('');
        }
      }
    }
  }catch(err){ console.warn(err.message); }
}

async function initDepartments(){
  if(!(location.pathname.endsWith('modules.html'))) return;
  const grid = document.querySelector('.dept-grid');
  if(!grid) return;
  try{
    // only show department cards to admins
    const user = await (async ()=>{ try{ return await api('/auth/me'); }catch(e){ return null; } })();
    if(!user || user.role !== 'admin'){
      grid.style.display = 'none';
      return;
    }
    const data = await api('/departments');
    grid.innerHTML = data.map(d => `<div class="dept-card"><div class="dc-icon"></div><div class="dc-name">${d.name}</div><div class="dc-code">${d.code}</div><div class="dc-info">${d.degree} · ${d.credits} Credits · ${d.duration}</div></div>`).join('');
    grid.style.display = '';
  }catch(err){ console.warn(err.message); }
}

async function getModules(params = ''){
  return api(`/modules${params ? ('?' + params) : ''}`);
}

async function getMyEnrollments(){
  return api('/enrollments');
}

async function enrollModule(module_id){
  return api('/enrollments', { method:'POST', body: JSON.stringify({ module_id }) });
}

async function unenrollModule(module_id){
  return api(`/enrollments/${module_id}`, { method:'DELETE' });
}

function moduleCard(m, enrolledIds){
  const deps = (m.departments || []).map(d => d.code).join(', ') || m.department_code || '';
  const isEnrolled = enrolledIds.includes(m.id);
  return `<div class="module-card" data-id="${m.id}">
    <div class="module-head"><div class="module-code">${m.code}</div><div class="module-title">${m.title}</div></div>
    <div class="module-meta">${deps} · ${m.credits} Credits · ${m.year} · ${m.semester}</div>
    <div class="module-actions"><button class="btn-enroll" data-id="${m.id}">${isEnrolled ? 'Unenroll' : 'Enroll'}</button></div>
  </div>`;
}

async function initModules(){
  if(!(location.pathname.endsWith('modules.html'))) return;
  const container = document.getElementById('modules-list');
  if(!container) return;
  try{
    const user = await (async ()=>{ try{ return await api('/auth/me'); }catch(e){ return null; } })();
    const modules = await getModules();
    let enrolled = [];
    try{ enrolled = await getMyEnrollments(); }catch(e){ enrolled = []; }
    const enrolledIds = enrolled.map(e => e.module_id);
    container.innerHTML = modules.map(m => moduleCard(m, enrolledIds)).join('');
    // show admin controls
    const adminControls = document.getElementById('admin-controls');
    if(adminControls) adminControls.style.display = (user && user.role === 'admin') ? 'block' : 'none';
    // adjust header and departments visibility for non-admin users
    const headerH1 = document.querySelector('#page-modules .page-header h1');
    const deptGrid = document.querySelector('.dept-grid');
    if(!user || user.role !== 'admin'){
      if(headerH1) headerH1.textContent = 'Available Modules';
      if(deptGrid) deptGrid.style.display = 'none';
    }else{
      if(headerH1) headerH1.textContent = 'All Modules';
      if(deptGrid) deptGrid.style.display = '';
    }
    if(user && user.role === 'admin'){
        // Manage students
        const manageBtn = document.getElementById('btn-manage-students');
        const manageModal = document.getElementById('manage-students-modal');
        const studentsList = document.getElementById('students-list');
        const closeStudents = document.getElementById('close-students');
        if(manageBtn) manageBtn.addEventListener('click', async ()=>{
          if(manageModal) manageModal.style.display = 'flex';
          try{
            const students = await getStudents();
            if(!studentsList) return;
            studentsList.innerHTML = students.map(s => `<div style="display:flex;align-items:center;justify-content:space-between;padding:8px;border-bottom:1px solid #f2f6fb"><div><div style="font-weight:700">${s.name} <span style="font-size:12px;color:var(--muted)">${s.email}</span></div><div style="font-size:12px;color:var(--muted)">Reg: ${s.reg_no || '-'} · ${s.department_code || '-'}</div></div><div><button data-id="${s.id}" class="btn-promote">Promote</button></div></div>`).join('');
            studentsList.querySelectorAll('.btn-promote').forEach(b=> b.addEventListener('click', async ()=>{
              const id = b.getAttribute('data-id'); b.disabled = true; try{ await promoteUser(id); showToast('User promoted', 'success'); b.remove(); }catch(err){ showToast(err.message || 'Failed', 'error'); } finally{ b.disabled = false }
            }));
          }catch(err){ showToast(err.message || 'Failed to load students', 'error'); }
        });
        if(closeStudents) closeStudents.addEventListener('click', ()=>{ if(manageModal) manageModal.style.display = 'none'; });

      const addBtn = document.getElementById('btn-add-module');
      const modal = document.getElementById('add-module-modal');
      const createBtn = document.getElementById('create-module-btn');
      const cancelBtn = document.getElementById('cancel-create-module');
      if(addBtn) addBtn.addEventListener('click', ()=>{ if(modal) modal.style.display = 'flex'; });
      if(cancelBtn) cancelBtn.addEventListener('click', ()=>{ if(modal) modal.style.display = 'none'; });
      if(createBtn) createBtn.addEventListener('click', async ()=>{
        createBtn.disabled = true;
        try{
          const payload = { code: document.getElementById('new-code').value.trim(), title: document.getElementById('new-title').value.trim(), department_code: document.getElementById('new-department-code').value.trim(), year: document.getElementById('new-year').value.trim(), semester: document.getElementById('new-semester').value.trim(), credits: Number(document.getElementById('new-credits').value) || 0, description: document.getElementById('new-desc').value.trim() };
          await createModule(payload);
          showToast('Module created', 'success');
          if(modal) modal.style.display = 'none';
          initModules();
        }catch(err){ showToast(err.message || 'Create failed', 'error'); }
        createBtn.disabled = false;
      });
    }
    container.querySelectorAll('.btn-enroll').forEach(btn => {
      btn.addEventListener('click', async (ev) => {
        const id = Number(btn.getAttribute('data-id'));
        btn.disabled = true;
        try{
          if(enrolledIds.includes(id)){
            await unenrollModule(id);
            const idx = enrolledIds.indexOf(id); if(idx !== -1) enrolledIds.splice(idx,1);
            btn.textContent = 'Enroll';
            showToast('Unenrolled from module', 'success');
          }else{
            await enrollModule(id);
            enrolledIds.push(id);
            btn.textContent = 'Unenroll';
            showToast('Enrolled in module', 'success');
          }
        }catch(err){ showToast(err.message || 'Action failed', 'error'); }
        btn.disabled = false;
      });
    });
  }catch(err){ console.warn(err.message); container.innerHTML = '<p>No modules available.</p>'; }
}

// init resource upload UI on student-material page
async function initResourceUpload(){
  const allowed = ['student-material.html','pastpapers.html'];
  if(!allowed.some(p => location.pathname.endsWith(p))) return;
  const modal = document.getElementById('upload-resource-modal');
  const uploadBtn = document.getElementById('upload-res-btn');
  const cancelBtn = document.getElementById('cancel-upload-res');
  const moduleSelect = document.getElementById('res-module');
  const deptInput = document.getElementById('res-dept');
  if(cancelBtn) cancelBtn.addEventListener('click', ()=>{ if(modal) modal.style.display = 'none'; });
  // populate module select from enrolled modules
  try{
    const enrolled = await getMyEnrollments();
    for(const e of enrolled){ try{ const m = await api(`/modules/${e.module_id}`); const opt = document.createElement('option'); opt.value = m.code; opt.textContent = `${m.code} — ${m.title}`; moduleSelect.appendChild(opt); }catch(e){} }
    // add open upload button to page header
    const header = document.querySelector('.page-header');
    if(header && token()){
      const openBtn = document.createElement('button'); openBtn.className = 'btn-enroll'; openBtn.style.marginLeft = '12px'; openBtn.textContent = 'Upload Resource';
      openBtn.addEventListener('click', ()=>{ if(modal) modal.style.display = 'flex'; });
      header.appendChild(openBtn);
    }
  }catch(e){ }
  if(uploadBtn){ uploadBtn.addEventListener('click', async ()=>{
    uploadBtn.disabled = true;
    const title = document.getElementById('res-title').value.trim();
    const module_code = document.getElementById('res-module').value;
    const dept = document.getElementById('res-dept').value.trim();
    const type = document.getElementById('res-type').value.trim();
    const desc = document.getElementById('res-desc').value.trim();
    const file = document.getElementById('res-file').files[0];
    if(!title || !dept || !type || !file){ showToast('Title, department, type and file are required', 'error'); uploadBtn.disabled = false; return; }
    const fd = new FormData(); fd.append('title', title); fd.append('department_code', dept); fd.append('resource_type', type); if(module_code) fd.append('module_code', module_code); fd.append('description', desc); fd.append('file', file);
    try{ await uploadResourceForm(fd); showToast('Resource uploaded', 'success'); if(modal) modal.style.display = 'none'; }catch(err){ showToast(err.message || 'Upload failed', 'error'); }
    uploadBtn.disabled = false;
  }); }
}

async function createModule(payload){
  return api('/modules', { method:'POST', body: JSON.stringify(payload) });
}

// Admin: list students and promote
async function getStudents(){
  return api('/admin/students');
}
async function promoteUser(userId){
  return api(`/admin/users/${userId}/promote`, { method:'PATCH' });
}

// Resource upload (uses FormData)
async function uploadResourceForm(formData){
  const headers = { ...(authHeaders()) };
  const res = await fetch(`${API_BASE}/resources/upload`, { method: 'POST', body: formData, headers });
  if(!res.ok){ let msg = 'Upload failed'; try{ msg = (await res.json()).detail || msg }catch(e){} throw new Error(msg); }
  return res.json();
}

function applyProfileToPage(u){
  const nameEl = document.getElementById('profile-name');
  const regEl = document.getElementById('profile-reg');
  const degreeEl = document.getElementById('profile-degree');
  const deptEl = document.getElementById('profile-department');
  const gpaEl = document.getElementById('profile-gpa');
  const metaEl = document.getElementById('profile-meta');
  const avatarEl = document.getElementById('profile-avatar');
  const topbarAvatar = document.getElementById('topbar-avatar');

  if(nameEl) nameEl.textContent = u.name || 'Student';
  if(regEl) regEl.textContent = `REG No: ${u.reg_no || '-'}`;
  if(degreeEl) degreeEl.textContent = departmentLabel(u.department || u.department_code || 'Information Systems') || 'Information Systems';
  if(deptEl) deptEl.textContent = departmentLabel(u.department || u.department_code || 'Information Systems') || 'Information Systems';
  if(gpaEl) gpaEl.textContent = (u.current_gpa ?? '-').toString();
  if(metaEl){
    metaEl.textContent = 'FMS, RUSL';
  }

  const initials = String(u.name || 'Student')
    .split(' ')
    .filter(Boolean)
    .map(part => part[0].toUpperCase())
    .slice(0, 2)
    .join('') || 'ST';
  if(avatarEl) avatarEl.textContent = initials;
  if(topbarAvatar) topbarAvatar.textContent = initials;
}

async function initProfile(){
  if(!location.pathname.endsWith('profile.html')) return;
  if(!token()) return;
  try{
    const u = await api('/profile');
    window.profileData = u;
    applyProfileToPage(u);
    // load enrolled modules into the Enrolled Modules section
    try{
      const enrolled = await getMyEnrollments();
      const container = document.querySelector('#page-profile .notes-list');
      if(container){
        if(!enrolled || enrolled.length === 0){ container.innerHTML = '<div style="color:var(--muted)">No enrolled modules.</div>'; }
        else{
          const cards = [];
          for(const e of enrolled){
            try{
              const m = await api(`/modules/${e.module_id}`);
              const badge = `<div class="note-badge ${m.department_code?.toLowerCase() || ''}" style="width:38px;height:38px;font-size:9px">${m.department_code || ''}</div>`;
              cards.push(`<div class="note-card" style="padding:12px 16px"><div class="note-badge-wrap">${badge}</div><div class="note-body"><div class="note-title" style="font-size:13px">${m.code} — ${m.title}</div><div class="note-meta"><span class="tag">${m.credits} Credits</span><span class="tag">Enrolled</span></div></div></div>`);
            }catch(err){}
          }
          container.innerHTML = cards.join('');
        }
      }
    }catch(err){ console.warn('Enrollments load error', err.message); }
  }catch(err){ console.warn(err.message); }
}

async function initGPAEnrollments(){
  if(!location.pathname.endsWith('gpa.html')) return;
  const tbody = document.getElementById('gpa-tbody');
  if(!tbody) return;
  try{
    const enrolled = await getMyEnrollments();
    const modules = [];
    for(const enrollment of enrolled){
      try{ modules.push(await api(`/modules/${enrollment.module_id}`)); }catch(err){}
    }
    if(modules.length){
      tbody.innerHTML = '';
      rowId = 0;
      modules.forEach(module => addRow(module.code ? `${module.code} — ${module.title}` : module.title, module.credits || 3, 'B'));
      return;
    }
  }catch(err){
    console.warn('Failed to load enrolled modules for GPA', err.message);
  }
  if(!tbody.querySelector('tr')) addRow('', 3, 'B');
}

function initProfileEditor(){
  if(!location.pathname.endsWith('profile.html')) return;
  const editBtn = document.getElementById('edit-profile-btn');
  const editCard = document.getElementById('profile-edit-card');
  const cancelBtn = document.getElementById('profile-cancel-btn');
  const saveBtn = document.getElementById('profile-save-btn');
  const errorBox = document.getElementById('profile-edit-error');
  if(!editBtn || !editCard) return;

  const fields = {
    name: document.getElementById('edit-name'),
    reg_no: document.getElementById('edit-reg-no'),
    department: document.getElementById('edit-department'),
    current_gpa: document.getElementById('edit-gpa')
  };

  const setError = (message) => {
    if(!errorBox) return;
    if(message){
      errorBox.textContent = message;
      errorBox.classList.remove('hidden');
    }else{
      errorBox.textContent = '';
      errorBox.classList.add('hidden');
    }
  };

  const fillForm = (data) => {
    if(fields.name) fields.name.value = data?.name || '';
    if(fields.reg_no) fields.reg_no.value = data?.reg_no || '';
    if(fields.department) fields.department.innerHTML = departmentSelectHtml(data?.department || data?.department_code || '');
    if(fields.current_gpa) fields.current_gpa.value = data?.current_gpa ?? '';
  };

  editBtn.addEventListener('click', () => {
    if(!token()){
      setError('Please log in to edit your profile.');
      return;
    }
    fillForm(window.profileData || {});
    editCard.classList.add('show');
    setError('');
  });

  if(cancelBtn){
    cancelBtn.addEventListener('click', () => {
      editCard.classList.remove('show');
      setError('');
    });
  }

  if(saveBtn){
    saveBtn.addEventListener('click', async () => {
      setError('');
      const payload = {
        name: fields.name?.value.trim() || undefined,
        reg_no: fields.reg_no?.value.trim() || undefined,
        department: fields.department?.value.trim() || undefined,
        department_code: departmentCodeFromLabel(fields.department?.value.trim()) || undefined
      };
      const gpaRaw = fields.current_gpa?.value.trim();
      if(gpaRaw){
        const gpaVal = Number(gpaRaw);
        if(Number.isNaN(gpaVal)){
          setError('Current GPA must be a number.');
          return;
        }
        payload.current_gpa = gpaVal;
      }

      if(saveBtn) saveBtn.disabled = true;
      try{
        // client-side validation: name required
        if(!payload.name || payload.name.trim().length === 0){ setError('Full name is required.'); return; }
        // gpa already parsed above and validated as number; ensure range
        if(payload.current_gpa !== undefined){
          const g = Number(payload.current_gpa);
          if(g < 0 || g > 4){ setError('Current GPA must be between 0.00 and 4.00'); return; }
        }
        const updated = await updateProfile(payload);
        window.profileData = updated;
        applyProfileToPage(updated);
        editCard.classList.remove('show');
        showToast('Profile updated successfully', 'success');
      }catch(err){
        const msg = err?.message || String(err);
        setError(msg);
        showToast(msg, 'error');
      }finally{
        if(saveBtn) saveBtn.disabled = false;
      }
    });
  }
}

async function initNotifications(){
  if(!location.pathname.endsWith('notifications.html')) return;
  const list = document.querySelector('.notif-card')?.parentElement;
  if(!list) return;
  try{
    const data = await api('/notifications');
    list.innerHTML = data.map(n => `<div class="notif-card ${n.is_read ? '' : 'unread'}" onclick="markNotificationRead(${n.id}, this)" style="background:#fff;border-radius:12px;box-shadow:var(--shadow);padding:16px 20px;display:flex;gap:14px;align-items:flex-start;border-left:4px solid ${n.is_read ? '#e6eaf2' : 'var(--accent)'};cursor:pointer;transition:.2s">
      <div style="font-size:22px">${n.is_read ? '✅' : '🔔'}</div><div style="flex:1"><div style="font-size:13.5px;font-weight:700;color:var(--navy);margin-bottom:4px">${n.title}</div><div style="font-size:12px;color:var(--muted);line-height:1.6">${n.message}</div><div class="recent-meta">${new Date(n.created_at).toLocaleString()}</div></div>${n.is_read ? '' : '<span style="background:var(--accent);width:9px;height:9px;border-radius:50%;margin-top:6px"></span>'}
    </div>`).join('');
    updateNotifBadge();
  }catch(err){ console.warn(err.message); }
}
async function markNotificationRead(id, el){
  try{ await api(`/notifications/${id}/read`, { method:'PATCH' }); }catch(e){}
  readNotif(el);
}

async function initForum(){
  if(!location.pathname.endsWith('forum.html')) return;
  const page = document.getElementById('page-forum');
  if(!page) return;
  try{
    const posts = await api('/forum/posts');
    // fetch user's enrolled modules to populate selector
    let enrolled = [];
    try{ enrolled = await getMyEnrollments(); }catch(e){ enrolled = []; }
    const moduleOptions = [];
    for(const e of enrolled){
      try{ const m = await api(`/modules/${e.module_id}`); moduleOptions.push(m); }catch(err){}
    }
    const moduleSelectHtml = moduleOptions.length ? `<select id="post-module"><option value="">Select module</option>${moduleOptions.map(m=>`<option value="${m.code}">${m.code} — ${m.title}</option>`).join('')}</select>` : '<div style="font-size:12px;color:var(--muted)">No enrolled modules — enroll to post questions.</div>';

    page.innerHTML = `<div class="page-header"><h1>Student Forum</h1><p>Collaborate and discuss with fellow FMS students.</p></div>
      <div class="gpa-card" style="margin-bottom:18px"><h2>Create Discussion</h2><div class="form-group"><input id="post-title" placeholder="Question title"></div><div class="form-group">${moduleSelectHtml}</div><div class="form-group"><textarea id="post-body" rows="4" placeholder="Write your question..."></textarea></div><button class="btn-send" onclick="createForumPost()">Post Question</button><p style="font-size:11px;color:var(--muted);margin-top:8px">Login required. Demo student: student@rajaratakuppi.lk / student123</p></div>
      <div class="notes-list">${posts.map(p => `<div class="note-card"><div class="note-badge itm">${p.module_code || 'FMS'}</div><div class="note-body"><div class="note-title">${p.title}</div><div class="note-desc">${p.body}</div><div class="note-meta"><span class="tag">${new Date(p.created_at).toLocaleDateString()}</span></div></div></div>`).join('')}</div>`;
  }catch(err){ console.warn(err.message); }
}
async function createForumPost(){
  const title = (document.getElementById('post-title')?.value || '').trim();
  const body = (document.getElementById('post-body')?.value || '').trim();
  const moduleEl = document.getElementById('post-module');
  const module_code = moduleEl ? moduleEl.value : null;
  if(!token()){ showToast('Please login to post', 'error'); return; }
  if(!module_code){ showToast('Select a module to post', 'error'); return; }
  if(!title || !body){ showToast('Title and body are required', 'error'); return; }
  try{
    await api('/forum/posts', { method:'POST', body: JSON.stringify({ title, module_code, body }) });
    location.reload();
  }catch(err){ showToast(err.message || 'Failed to create post', 'error'); }
}

async function initSupportForm(){
  if(!location.pathname.endsWith('support.html')) return;
  const btn = document.querySelector('.btn-send');
  if(!btn) return;
  btn.onclick = async () => {
    const form = btn.closest('.contact-form');
    const inputs = form.querySelectorAll('input, select, textarea');
    const payload = { name: inputs[0].value, email: inputs[1].value, topic: inputs[2].value, message: inputs[3].value };
    try{ await api('/support/messages', { method:'POST', body: JSON.stringify(payload) }); alert('Message saved in backend.'); }
    catch(err){ alert(err.message); }
  };
}

const oldCalcGPA = window.calcGPA;
window.calcGPA = async function(){
  if(!document.getElementById('gpa-tbody')) return oldCalcGPA?.();
  const rows = [...document.querySelectorAll('#gpa-tbody tr')].map(r => ({
    module: r.querySelector('input[type=text]').value,
    credits: Number(r.querySelector('input[type=number]').value),
    grade: r.querySelector('select').value
  }));
  try{
    const result = await api('/gpa/calculate', { method:'POST', body: JSON.stringify({ rows }) });
    document.getElementById('gpa-val').textContent = result.gpa.toFixed(2);
    document.getElementById('gpa-class').textContent = result.classification;
    document.getElementById('gpa-meta').textContent = `Total Credits: ${result.total_credits} | Total Grade Points: ${result.total_grade_points}`;
    document.getElementById('gpa-result').classList.add('show');
  }catch(err){
    console.warn(err.message);
    oldCalcGPA?.();
  }
}

window.addEventListener('DOMContentLoaded', () => {
  initStats(); initResources(); initDepartments(); initProfile(); initNotifications(); initForum(); initSupportForm();
  initModules();
  initResourceUpload();
  initGPAEnrollments();
  updateAuthButtons();
  initTopbarMenu();
  initProfileEditor();
});
