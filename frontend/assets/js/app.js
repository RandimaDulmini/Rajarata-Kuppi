
// ── PAGE NAVIGATION ──
const titles = {
  home:'Home',
  'student-material':'Student Material',
  modules:'Modules',
  notes:'Notes',
  profile:'Student Profile',
  pastpapers:'Past Papers',
  notifications:'Notifications',
  gpa:'GPA Calculator',
  forum:'Forum',
  support:'Support Center'
};
function showPage(page, el){
  const map = {
    home: 'index.html',
    'student-material': 'student-material.html',
    modules: 'modules.html',
    notes: 'notes.html',
    profile: 'profile.html',
    pastpapers: 'pastpapers.html',
    notifications: 'notifications.html',
    gpa: 'gpa.html',
    forum: 'forum.html',
    support: 'support.html'
  };
  window.location.href = map[page] || 'index.html';
}

// ── STUDENT MATERIAL TABS ──
function showTab(id, el){
  document.querySelectorAll('.mat-tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.mat-panel').forEach(p=>p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('mat-'+id).classList.add('active');
}

// ── FAQ TOGGLE ──
function toggleFAQ(el){
  const wasOpen = el.classList.contains('open');
  document.querySelectorAll('.faq-item').forEach(f=>f.classList.remove('open'));
  if(!wasOpen) el.classList.add('open');
}

// ── GPA CALCULATOR ──
const gradeMap = {
  'A+':4.0,'A':4.0,'A-':3.7,'B+':3.3,'B':3.0,'B-':2.7,
  'C+':2.3,'C':2.0,'C-':1.7,'D':1.0,'E':0.0
};
const grades = Object.keys(gradeMap);
let rowId = 0;
const tbody = document.getElementById('gpa-tbody');

function addRow(mod='',cr=3,gr='B'){
  const id = rowId++;
  const opts = grades.map(g=>`<option value="${g}"${g===gr?' selected':''}>${g}</option>`).join('');
  const gp = gradeMap[gr]||0;
  const tr = document.createElement('tr');
  tr.id='row-'+id;
  tr.innerHTML=`
    <td><input type="text" value="${mod}" placeholder="Module name" style="width:140px"/></td>
    <td><input type="number" value="${cr}" min="1" max="6" style="width:60px" onchange="updateGP(${id})"/></td>
    <td><select onchange="updateGP(${id})">${opts}</select></td>
    <td id="gp-${id}" style="font-weight:700;color:var(--navy)">${gp.toFixed(1)}</td>
    <td><button class="del-btn" onclick="delRow(${id})">✕</button></td>`;
  tbody.appendChild(tr);
}

function updateGP(id){
  const row = document.getElementById('row-'+id);
  const sel = row.querySelector('select');
  document.getElementById('gp-'+id).textContent = (gradeMap[sel.value]||0).toFixed(1);
}

function delRow(id){
  const r = document.getElementById('row-'+id);
  if(r) r.remove();
}

function calcGPA(){
  const rows = tbody.querySelectorAll('tr');
  if(!rows.length){alert('Please add at least one module.');return;}
  let totalGP=0, totalCR=0;
  rows.forEach(r=>{
    const cr = parseFloat(r.querySelector('input[type=number]').value)||0;
    const gr = r.querySelector('select').value;
    const gp = gradeMap[gr]||0;
    totalGP += cr*gp;
    totalCR += cr;
  });
  const gpa = totalCR?totalGP/totalCR:0;
  document.getElementById('gpa-val').textContent = gpa.toFixed(2);
  let cls='', bg='';
  if(gpa>=3.70){cls=' First Class Honours';}
  else if(gpa>=3.30){cls=' Second Class (Upper Division)';}
  else if(gpa>=2.70){cls='Second Class (Lower Division)';}
  else if(gpa>=2.00){cls=' Pass';}
  else{cls=' Fail — Requires Improvement';}
  document.getElementById('gpa-class').textContent=cls;
  document.getElementById('gpa-meta').textContent=`Total Credits: ${totalCR} | Total Grade Points: ${totalGP.toFixed(2)}`;
  const res = document.getElementById('gpa-result');
  res.classList.add('show');
}

function resetGPA(){
  tbody.innerHTML='';
  rowId=0;
  document.getElementById('gpa-result').classList.remove('show');
  addRow('',3,'B');
}

// ── PAST PAPERS FILTER ──
function filterPapers(dept){
  document.querySelectorAll('#papers-list .note-card').forEach(c=>{
    c.style.display = (dept==='all'||c.dataset.dept===dept)?'flex':'none';
  });
}

// ── NOTIFICATIONS ──
function readNotif(el){
  el.classList.remove('unread');
  el.style.borderLeftColor='#e6eaf2';
  const dot = el.querySelector('span[style*="background:var(--accent)"]');
  if(dot) dot.remove();
  updateNotifBadge();
}
function updateNotifBadge(){
  const count = document.querySelectorAll('.notif-card.unread').length;
  const badge = document.getElementById('notif-dot');
  if(count>0){badge.textContent=count;badge.style.display='inline';}
  else{badge.style.display='none';}
}
function markAllRead(){
  document.querySelectorAll('.notif-card.unread').forEach(c=>readNotif(c));
}
if (document.getElementById('gpa-tbody')) {
  addRow('',3,'B');
}
