import os

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "index.html")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>My Notes & Reminders</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@400;600;700&family=Inter:wght@300;400;500;600&family=EB+Garamond:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}

/* -- THEME VARIABLES --------------------------------- */
body.theme-cream {
  --bg:       #faf6ef;
  --sidebar:  #e8dcc8;
  --s2:       #d4c4a8;
  --border:   #c8b48a;
  --border2:  #b8a070;
  --text:     #3c2a14;
  --text2:    #6b4c2a;
  --muted:    #9a7a58;
  --accent:   #8b5e2a;
  --accent2:  #a8762e;
  --green:    #2a7a40;
  --red:      #c04040;
  --blue:     #2a5a9a;
  --over-bg:  rgba(40,20,0,.78);
}
body.theme-beige {
  --bg:       #f5f0e8;
  --sidebar:  #ede6d8;
  --s2:       #e0d6c4;
  --border:   #d4c8b0;
  --border2:  #b8a888;
  --text:     #2d2420;
  --text2:    #5a4a38;
  --muted:    #9a8870;
  --accent:   #7c5cbf;
  --accent2:  #9b7de0;
  --green:    #2a8a5c;
  --red:      #c04848;
  --blue:     #3a6abf;
  --over-bg:  rgba(20,10,30,.65);
}
body.theme-neon {
  --bg:       #080c14;
  --sidebar:  #0c1020;
  --s2:       #10162a;
  --border:   #1a2240;
  --border2:  #243060;
  --text:     #e0eeff;
  --text2:    #88aadd;
  --muted:    #3a5080;
  --accent:   #00e5ff;
  --accent2:  #bf00ff;
  --green:    #00ff9d;
  --red:      #ff3366;
  --blue:     #00aaff;
  --over-bg:  rgba(0,0,0,.85);
}

body{
  font-family:'Inter',sans-serif;
  background:var(--bg);color:var(--text);
  min-height:100vh;transition:background .3s,color .3s
}

/* -- LAYOUT ---------------------------------------- */
.layout{display:flex;min-height:100vh}

aside{
  width:232px;flex-shrink:0;background:var(--sidebar);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  position:fixed;top:0;left:0;bottom:0;z-index:50;
  overflow-y:auto;transition:background .3s,border-color .3s
}
.sidebar-logo{
  padding:22px 20px 18px;
  font-family:'Fraunces',serif;font-size:18px;color:var(--accent);
  display:flex;align-items:center;gap:9px;font-weight:700;
  border-bottom:1px solid var(--border);letter-spacing:-.3px
}
.sidebar-section{
  padding:18px 16px 6px;font-size:10px;
  text-transform:uppercase;letter-spacing:2px;color:var(--text2);font-weight:700
}
.nav-item{
  display:flex;align-items:center;gap:9px;
  padding:9px 18px;font-size:13px;color:var(--text2);font-weight:500;
  cursor:pointer;border-radius:8px;margin:1px 8px;
  transition:all .15s;border:none;background:none;
  font-family:'Inter',sans-serif;text-align:left;
  width:calc(100% - 16px)
}
.nav-item:hover{background:var(--s2);color:var(--text)}
.nav-item.active{background:rgba(139,94,42,.15);color:var(--accent)}
body.theme-beige .nav-item.active{background:rgba(124,92,191,.12);color:var(--accent)}
body.theme-neon   .nav-item.active{background:rgba(0,229,255,.1);color:var(--accent)}
.nav-icon{font-size:14px;width:18px;text-align:center}
.nav-count{
  margin-left:auto;background:var(--s2);border-radius:20px;
  padding:1px 8px;font-size:11px;color:var(--text2);font-weight:600
}
.nav-item.active .nav-count{background:rgba(200,160,80,.2);color:var(--accent)}

.sidebar-footer{
  margin-top:auto;padding:14px;
  border-top:1px solid var(--border)
}
.sync-pill{
  display:flex;align-items:center;gap:8px;
  background:var(--s2);border-radius:8px;
  padding:9px 12px;font-size:12px;color:var(--text2)
}
.sdot{width:7px;height:7px;border-radius:50%;background:var(--green);flex-shrink:0}
.sdot.syncing{background:var(--accent);animation:blink 1s infinite}
.sdot.error{background:var(--red)}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
/* 7. Page fade-in */
@keyframes page-fadein{
  from{opacity:0;transform:translateY(6px)}
  to{opacity:1;transform:translateY(0)}
}
.page-entering{animation:page-fadein .18s ease both}

/* -- MAIN ------------------------------------------ */
.main{margin-left:232px;flex:1;display:flex;flex-direction:column;min-width:0}

.topbar{
  background:var(--sidebar);
  border-bottom:1px solid var(--border2);
  padding:0;height:58px;
  display:flex;align-items:stretch;justify-content:space-between;
  position:sticky;top:0;z-index:40;
  transition:background .3s,border-color .3s
}
body.theme-cream .topbar{
  background:#ede3d0;
  border-bottom:1px solid #c8b48a;
  box-shadow:0 1px 8px rgba(139,94,42,.1)
}
body.theme-beige .topbar{
  background:#e8dfc8;
  border-bottom:1px solid #c8b89a;
  box-shadow:0 1px 8px rgba(100,80,50,.1)
}
body.theme-neon .topbar{
  background:rgba(8,12,20,.92);
  border-bottom:1px solid rgba(0,229,255,.18);
  box-shadow:0 1px 20px rgba(0,229,255,.08)
}
.topbar-left{
  display:flex;align-items:center;gap:12px;
  padding:0 20px;flex:1
}
.page-title{
  font-family:'Fraunces',serif;font-size:16px;font-weight:700;
  letter-spacing:-.2px;color:var(--text)
}
body.theme-beige .page-title{color:#2d2420}
body.theme-neon  .page-title{color:#00e5ff}
.topbar-right{display:flex;align-items:center;gap:8px;padding:0 12px}
/* topbar context action area */
.topbar-ctx{display:flex;align-items:center;gap:8px;padding:0 8px}

/* -- CLOCK --------------------------------------- */
.clock-bar{
  display:flex;align-items:stretch;
  border-left:1px solid var(--border);flex-shrink:0
}
.clock-block{
  display:flex;flex-direction:column;justify-content:center;align-items:flex-start;
  padding:0 14px;min-width:102px;border-left:1px solid var(--border);
  background:transparent
}
.clock-block:first-child{border-left:none}
body.theme-cream  .clock-block{background:rgba(255,255,255,.35)}
body.theme-beige  .clock-block{background:rgba(255,255,255,.3)}
body.theme-neon   .clock-block{background:rgba(0,229,255,.04);border-left-color:rgba(0,229,255,.12)}
.clock-zone{
  font-size:9px;font-weight:700;text-transform:uppercase;
  letter-spacing:1.2px;color:var(--muted);
  display:flex;align-items:center;gap:4px;margin-bottom:1px
}
.clock-zone-flag{font-size:11px}
.clock-time{
  font-size:14px;font-weight:600;
  font-family:'Courier New',Courier,monospace;
  font-variant-numeric:tabular-nums;line-height:1.2;
  letter-spacing:.5px;opacity:.92
}
body.theme-cream  .clock-time{color:#2a5a8a}
body.theme-beige  .clock-time{color:#7c5cbf}
body.theme-neon   .clock-time{color:#00e5ff;text-shadow:0 0 8px rgba(0,229,255,.5)}
.clock-date{
  font-size:9px;font-weight:600;margin-top:2px;
  letter-spacing:.3px;opacity:.7;color:var(--muted)
}
.search-wrap{position:relative}
.search-wrap input{
  background:var(--s2);border:1px solid var(--border);border-radius:8px;
  padding:7px 12px 7px 32px;color:var(--text);font-size:13px;
  font-family:'Inter',sans-serif;outline:none;width:220px;transition:all .2s
}
.search-wrap input:focus{border-color:var(--accent);width:260px}
.search-wrap input::placeholder{color:var(--muted)}
.s-icon{position:absolute;left:9px;top:50%;transform:translateY(-50%);font-size:12px;color:var(--muted)}
.btn{
  display:inline-flex;align-items:center;gap:5px;
  background:var(--accent);color:var(--sidebar);border:none;border-radius:8px;
  padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer;
  font-family:'Inter',sans-serif;transition:all .2s;white-space:nowrap
}
body.theme-cream .btn{color:#fff}
body.theme-beige .btn{color:#fff}
body.theme-neon  .btn{color:#080c14;background:var(--accent);box-shadow:0 0 12px rgba(0,229,255,.35)}
.btn:hover{background:var(--accent2)}
.btn-ghost{
  background:transparent;color:var(--muted);border:1px solid var(--border2);
  border-radius:8px;padding:7px 13px;font-size:13px;cursor:pointer;
  font-family:'Inter',sans-serif;transition:all .2s
}
.btn-ghost:hover{border-color:var(--accent);color:var(--accent)}

/* -- STATS ----------------------------------------- */
.stats-row{
  display:grid;grid-template-columns:repeat(4,1fr);
  gap:14px;padding:20px 28px;
  border-bottom:1px solid var(--border)
}
.stat-card{
  background:var(--sidebar);border:1px solid var(--border);
  border-radius:12px;padding:16px 18px;
  display:flex;align-items:center;gap:12px;
  transition:all .2s;cursor:pointer;
}
.stat-card:hover{border-color:var(--border2);background:var(--s2)}
.stat-card.active{
  border-color:var(--accent);
  background:var(--s2);
  box-shadow:0 0 0 2px var(--accent);
}
.stat-icon{
  width:38px;height:38px;border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  font-size:17px;flex-shrink:0
}
.si-notes{background:rgba(90,150,255,.12)}
.si-rem{background:rgba(200,160,80,.12)}
.si-pend{background:rgba(150,100,255,.12)}
.si-files{background:rgba(60,180,120,.12)}
.stat-num{font-family:'Fraunces',serif;font-size:26px;color:var(--text);line-height:1;font-weight:700}
.stat-label{font-size:12px;color:var(--text2);margin-top:3px;font-weight:700;letter-spacing:.3px}

/* -- CONTENT --------------------------------------- */
.content{padding:24px 28px;flex:1}
.sec-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.sec-title{
  font-family:'Fraunces',serif;font-size:16px;color:var(--text);font-weight:700;
  display:flex;align-items:center;gap:8px
}
.pill{
  background:var(--s2);border:1px solid var(--border);
  border-radius:20px;padding:2px 9px;
  font-size:11px;color:var(--text2);font-weight:700;font-family:'Inter',sans-serif
}

/* -- CARDS ----------------------------------------- */
.cards-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
  gap:16px;margin-bottom:32px;width:100%
}
.ncard{
  background:var(--sidebar);
  border:1.5px solid var(--border);
  border-radius:12px;padding:14px 16px;
  display:flex;flex-direction:column;gap:8px;
  transition:border-color .18s,box-shadow .18s;
  position:relative;overflow:hidden;
  cursor:pointer;
}
.ncard:hover{
  border-color:var(--border2);
  box-shadow:0 4px 14px rgba(139,94,42,.1);
}

/* remove old ::after top line */
.ncard::after{ display:none }

/* reminder card default left border = accent */
.ncard[data-type="reminder"]{border-left:4px solid var(--accent)}
.ncard[data-type="reminder"].sent{border-left-color:var(--green)}
.ncard[data-type="reminder"].overdue{border-left-color:var(--red)}
.ncard[data-type="reminder"].pending{border-left-color:var(--accent)}

/* note colour variants */
.ncard.cl-blue{border-left:4px solid var(--blue)!important;}
.ncard.cl-green{border-left:4px solid var(--green)!important;}
.ncard.cl-yellow{border-left:4px solid var(--accent)!important;}
.ncard.cl-red{border-left:4px solid var(--red)!important;}
.ncard.cl-purple{border-left:4px solid #7c3aed!important;}

/* title colours match left border */
.ncard.cl-blue .ctitle{color:var(--blue)}
.ncard.cl-green .ctitle{color:var(--green)}
.ncard.cl-yellow .ctitle{color:var(--accent)}
.ncard.cl-red .ctitle{color:var(--red)}
.ncard.cl-purple .ctitle{color:#7c3aed}

/* overdue card */
.ncard.overdue{border-left:4px solid var(--red)!important;}
.ncard.overdue{border-color:rgba(200,60,60,.3)}
.ncard.overdue::after{background:var(--red)}
.ncard:hover::after{opacity:.8}

.ceyebrow{display:flex;align-items:center;justify-content:space-between}
.ctype{font-size:10px;text-transform:uppercase;letter-spacing:1.4px;color:var(--muted);font-weight:700}
.schip{font-size:10px;padding:2px 9px;border-radius:20px;font-weight:600}
.schip.pending{background:#fdf0d8;color:#8b5e2a}
.schip.sent{background:#e8f4ec;color:#2a7a40}
.schip.overdue{background:#f8eeec;color:#c04040}
.ctitle{
  font-family:'Fraunces',serif;font-size:15px;
  color:var(--text);line-height:1.3;font-weight:700
}
.cbody{font-size:13px;line-height:1.6;color:var(--text2);flex:1;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.due-row{
  display:flex;align-items:center;gap:5px;font-size:11px;
  color:#8b5e2a;background:rgba(139,94,42,.08);
  border-radius:6px;padding:6px 10px;font-weight:600
}
.due-row strong{color:var(--text)}
.tags-row{display:flex;gap:5px;flex-wrap:wrap}
.ctag{
  background:var(--s2);color:var(--text2);
  border-radius:4px;padding:2px 8px;font-size:11px;
  border:1px solid var(--border);font-weight:600
}
.cmeta{
  display:flex;align-items:center;justify-content:space-between;
  padding-top:8px;border-top:1px solid var(--border)
}
.cdate{font-size:10px;color:var(--muted);font-weight:500}
.cbtns{display:flex;gap:5px}
.cbtn{
  background:var(--s2);border:1px solid var(--border);border-radius:6px;
  padding:4px 11px;font-size:11px;color:var(--text2);cursor:pointer;
  font-family:'Inter',sans-serif;transition:all .15s;font-weight:600
}
.cbtn:hover{border-color:var(--accent);color:var(--accent);background:var(--sidebar)}
.cbtn.del:hover{border-color:#c04040;color:#c04040;background:#f8eeec}
.cbtn.done-btn{background:#e8f4ec;border-color:#90c8a0;color:#2a7a40;font-weight:700}
.cbtn.done-btn:hover{background:#d0ecd8;border-color:#2a7a40;color:#1a5a2a}

.empty-state{
  grid-column:1/-1;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  padding:44px;color:var(--muted);gap:8px
}
.empty-state .ei{font-size:32px;opacity:.4}
.empty-state p{font-size:13px}

/* -- VIEW TOGGLE ----------------------------------- */
.view-toggle{
  display:flex;background:var(--s2);border:1px solid var(--border);
  border-radius:8px;padding:3px;gap:2px
}
.vtbtn{
  background:none;border:none;border-radius:6px;
  padding:5px 10px;cursor:pointer;color:var(--muted);
  font-size:14px;line-height:1;transition:all .15s
}
.vtbtn:hover{color:var(--text)}
.vtbtn.active{background:var(--accent);color:var(--sidebar)}
body.theme-cream  .vtbtn.active{color:#fff}
body.theme-beige  .vtbtn.active{color:#fff}
body.theme-neon   .vtbtn.active{color:#080c14}

/* -- LIST VIEW ------------------------------------- */
.list-view{display:flex;flex-direction:column;gap:0;margin-bottom:32px;width:100%}
.list-view .lrow{
  display:flex;align-items:center;gap:12px;
  padding:11px 14px;border-bottom:1px solid var(--border2);
  transition:background .15s;position:relative;
  cursor:pointer;
}
.list-view .lrow:first-child{border-top:1px solid var(--border2);border-radius:10px 10px 0 0}
.list-view .lrow:last-child{border-radius:0 0 10px 10px}
.list-view .lrow:hover{background:var(--s2)}
.lrow-accent{width:3px;height:36px;border-radius:2px;background:var(--border2);flex-shrink:0}
.lrow-accent.cl-blue{background:var(--blue)}
.lrow-accent.cl-green{background:var(--green)}
.lrow-accent.cl-yellow{background:var(--accent)}
.lrow-accent.cl-red{background:var(--red)}
.lrow-accent.cl-purple{background:#7c3aed}
.lrow-icon{font-size:14px;flex-shrink:0;width:20px;text-align:center}
.lrow-main{flex:1;min-width:0}
.lrow-title{
  font-family:'Fraunces',serif;font-size:14px;color:var(--text);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  font-weight:700
}
.lrow-sub{
  font-size:12px;color:var(--text2);margin-top:2px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  font-weight:500
}
.lrow-due{
  font-size:11px;color:var(--text);white-space:nowrap;
  background:var(--s2);border-radius:5px;padding:3px 8px;flex-shrink:0;
  border:1px solid var(--border2);font-weight:600
}
.lrow-tags{display:flex;gap:4px;flex-wrap:nowrap;overflow:hidden;flex-shrink:0;max-width:160px}
.lrow-tags .ctag{
  white-space:nowrap;
  background:rgba(0,0,0,.08);
  color:var(--text2);
  border:1px solid rgba(0,0,0,.1);
  font-weight:500;font-size:11px
}
.lrow-status{flex-shrink:0}
.lrow-date{font-size:11px;color:var(--text2);flex-shrink:0;width:72px;text-align:right;font-weight:600}
.lrow-btns{display:flex;gap:4px;flex-shrink:0}
.list-view .empty-state{border:1px solid var(--border);border-radius:10px}

/* hide grid children in list mode and vice versa */
.cards-grid{display:grid}
.list-view-wrap{display:none}
.is-list .cards-grid{display:none}
.is-list .list-view-wrap{display:block}

/* -- OVERLAY / MODAL ------------------------------- */
.overlay{
  display:none;position:fixed;inset:0;
  background:var(--over-bg);
  z-index:200;align-items:flex-start;justify-content:center;
  padding:40px 20px;overflow-y:auto
}
.overlay.open{display:flex}
.modal{
  background:var(--sidebar);border:1px solid var(--border2);
  border-radius:16px;padding:26px;width:100%;max-width:460px;
  transition:background .3s;margin:auto;
  box-shadow:0 20px 60px rgba(0,0,0,.35),0 0 0 1px rgba(255,255,255,.06)
}
.modal.with-preview{max-width:860px;display:grid;grid-template-columns:1fr 1fr;gap:0}
.mhead{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.mhead h2{font-family:'Fraunces',serif;font-size:19px;color:var(--text)}
.mclose{
  background:var(--s2);border:1px solid var(--border);
  border-radius:6px;color:var(--muted);font-size:13px;
  cursor:pointer;padding:4px 9px
}
/* 2. Visual tab toggle */
.type-tog{
  display:flex;border-bottom:2px solid var(--border);
  margin-bottom:18px;gap:0
}
.tt{
  flex:1;padding:10px 12px;text-align:center;border-radius:0;font-size:13px;
  color:var(--muted);cursor:pointer;transition:all .15s;
  font-family:'Inter',sans-serif;border:none;background:none;
  border-bottom:3px solid transparent;margin-bottom:-2px;font-weight:600
}
.tt:hover{color:var(--text)}
.tt.active{color:var(--accent);border-bottom-color:var(--accent);background:rgba(139,94,42,.05)}
body.theme-beige .tt.active{color:#fff;border-bottom-color:var(--accent)}
body.theme-neon  .tt.active{color:#080c14;border-bottom-color:var(--accent)}
/* Preview panel */
.modal-form-col{padding:26px}
.modal-preview-col{
  padding:26px;background:var(--bg);
  border-left:1px solid var(--border);border-radius:0 16px 16px 0;
  display:flex;flex-direction:column;gap:12px
}
.modal-preview-label{
  font-size:10px;font-weight:700;text-transform:uppercase;
  letter-spacing:1px;color:var(--muted);margin-bottom:6px
}
.preview-card{
  background:var(--sidebar);border:1.5px solid var(--border);
  border-radius:12px;padding:14px 16px;
  display:flex;flex-direction:column;gap:8px;flex:1
}
.preview-card.cl-blue{border-left:4px solid var(--blue)}
.preview-card.cl-green{border-left:4px solid var(--green)}
.preview-card.cl-yellow{border-left:4px solid var(--accent)}
.preview-card.cl-red{border-left:4px solid var(--red)}
.preview-card.cl-purple{border-left:4px solid #7c3aed}
.preview-eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:1.2px;color:var(--muted);font-weight:700}
.preview-title{font-family:'Fraunces',serif;font-size:15px;font-weight:700;color:var(--text);line-height:1.3;min-height:22px}
.preview-body{font-family:'EB Garamond',serif;font-size:13px;color:var(--text2);line-height:1.6;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.preview-tags{display:flex;gap:5px;flex-wrap:wrap}
.preview-meta{display:flex;align-items:center;justify-content:space-between;padding-top:8px;border-top:1px solid var(--border);margin-top:auto}
.preview-date{font-size:10px;color:var(--muted)}
/* Pin */
.pin-btn{
  background:none;border:1px solid var(--border);border-radius:6px;
  padding:4px 10px;font-size:12px;cursor:pointer;color:var(--muted);
  font-family:'Inter',sans-serif;font-weight:600;transition:all .15s
}
.pin-btn.pinned{background:#fef3c7;border-color:#d97706;color:#92400e}
.pin-btn:hover{border-color:var(--accent);color:var(--accent)}
.ncard.pinned-card{border-top:3px solid #d97706}
.pinned-badge{font-size:10px;background:#fef3c7;color:#92400e;border-radius:4px;padding:1px 6px;font-weight:700}
.frow{margin-bottom:13px}
.frow label{display:block;font-size:10px;color:var(--muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:.8px}
.frow input,.frow textarea,.frow select{
  width:100%;background:var(--bg);border:1px solid var(--border2);
  border-radius:8px;padding:9px 12px;color:var(--text);font-size:13px;
  font-family:'EB Garamond',serif;font-size:15px;outline:none;transition:border-color .2s
}
.frow input:focus,.frow textarea:focus,.frow select:focus{border-color:var(--accent)}
.frow textarea{resize:vertical;min-height:120px}
.frow select option{background:var(--sidebar)}
.mfoot{display:flex;gap:8px;justify-content:flex-end;margin-top:18px;padding-top:14px;border-top:1px solid var(--border);align-items:center}
.autosave-lbl{font-size:11px;color:var(--green);margin-right:auto;opacity:0;transition:opacity .4s;font-weight:600}
.autosave-lbl.show{opacity:1}
/* Tag chip input */
.tag-chip-wrap{
  display:flex;flex-wrap:wrap;gap:5px;align-items:center;
  background:var(--bg);border:1px solid var(--border2);border-radius:8px;
  padding:6px 10px;min-height:40px;cursor:text;transition:border-color .2s
}
.tag-chip-wrap:focus-within{border-color:var(--accent)}
.tag-chip{
  display:inline-flex;align-items:center;gap:4px;
  background:var(--s2);border:1px solid var(--border);
  border-radius:20px;padding:2px 8px;font-size:12px;
  color:var(--text2);font-weight:600
}
.tag-chip-x{
  background:none;border:none;cursor:pointer;color:var(--muted);
  font-size:13px;padding:0;line-height:1;transition:color .15s
}
.tag-chip-x:hover{color:var(--red)}
.tag-chip-input{
  border:none;outline:none;background:transparent;
  font-size:13px;color:var(--text);font-family:'Inter',sans-serif;
  min-width:80px;flex:1
}
.tag-chip-input::placeholder{color:var(--muted)}
.tag-suggestions{
  position:absolute;top:100%;left:0;right:0;z-index:10;
  background:var(--sidebar);border:1px solid var(--border2);
  border-radius:8px;margin-top:2px;overflow:hidden;display:none;
  box-shadow:0 4px 16px rgba(0,0,0,.12)
}
.tag-suggestions.open{display:block}
.tag-sug-item{
  padding:8px 12px;font-size:12px;cursor:pointer;color:var(--text2);
  transition:background .1s;display:flex;align-items:center;gap:6px
}
.tag-sug-item:hover{background:var(--s2);color:var(--text)}
/* Color swatches */
.color-swatches{display:flex;gap:8px;flex-wrap:wrap;margin-top:4px}
.cswatch{
  width:28px;height:28px;border-radius:50%;cursor:pointer;
  border:2px solid transparent;transition:all .15s;position:relative
}
.cswatch:hover{transform:scale(1.15)}
.cswatch.selected{border-color:var(--text);box-shadow:0 0 0 2px var(--bg),0 0 0 4px var(--text)}
.cswatch-default{background:var(--s2);border-color:var(--border)}

/* type description banner */
.type-desc{
  display:flex;align-items:flex-start;gap:10px;
  background:var(--s2);border:1px solid var(--border2);
  border-radius:8px;padding:10px 14px;margin-bottom:14px;
  font-size:12px;color:var(--text2);line-height:1.55
}
.type-desc strong{color:var(--text);font-size:13px}
.type-desc span{color:var(--muted)}
.type-desc-icon{font-size:20px;flex-shrink:0;margin-top:1px}

/* -- SETTINGS PANEL -------------------------------- */
#settings-panel{
  display:none;position:fixed;inset:0;
  background:var(--over-bg);
  z-index:300;align-items:flex-start;justify-content:center;
  padding:40px 20px;overflow-y:auto
}
#settings-panel.open{display:flex}
.settings-modal{
  background:var(--sidebar);border:1px solid var(--border2);
  border-radius:16px;padding:28px;width:100%;max-width:520px;
  margin:auto
}
.settings-modal h2{font-family:'Fraunces',serif;font-size:19px;color:var(--text);margin-bottom:22px}
.settings-section-title{
  font-size:11px;text-transform:uppercase;letter-spacing:1.5px;
  color:var(--muted);margin-bottom:10px;margin-top:22px
}
.settings-section-title:first-of-type{margin-top:0}

/* THEME CARDS */
.theme-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:4px}
.theme-card{
  border:2px solid var(--border);border-radius:10px;overflow:hidden;
  cursor:pointer;transition:border-color .2s
}
.theme-card.selected{border-color:var(--accent)}
.theme-preview{height:52px;display:flex;gap:0}
.tp-side{width:30%;flex-shrink:0}
.tp-main{flex:1;padding:7px;display:flex;flex-direction:column;gap:4px}
.tp-line{height:4px;border-radius:2px}
.theme-name{
  font-size:11px;font-weight:500;color:var(--text);
  padding:6px 10px;background:var(--s2);text-align:center
}

/* Neon Glassmorphism overrides */
body.theme-neon .ncard,
body.theme-neon .fin-card,
body.theme-neon .tan-item,
body.theme-neon .fin-sum-card,
body.theme-neon .stat-card{
  background:rgba(12,16,32,.7);
  backdrop-filter:blur(12px);
  border-color:rgba(0,229,255,.15);
}
body.theme-neon .ncard:hover,
body.theme-neon .fin-card:hover,
body.theme-neon .tan-item:hover{
  border-color:rgba(0,229,255,.4);
  box-shadow:0 0 20px rgba(0,229,255,.12)
}
body.theme-neon aside{
  background:rgba(8,10,18,.9);
  border-right:1px solid rgba(0,229,255,.12);
  backdrop-filter:blur(16px)
}
body.theme-neon .ncard.pinned-card{border-top:3px solid #00e5ff}
body.theme-neon .ctitle{color:#00e5ff}
body.theme-neon .stat-num{color:#00e5ff}
/* Beige accent overrides */
body.theme-beige .ctitle{color:#7c5cbf}
body.theme-beige .nav-item.active{color:#7c5cbf}

/* -- STICKY PAGE ----------------------------------- */
.sp-toolbar{
  display:flex;align-items:center;justify-content:space-between;
  padding:12px 28px;border-bottom:1px solid var(--border);
  background:var(--bg);flex-shrink:0;flex-wrap:wrap;gap:10px
}
.sp-toolbar-left{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.sp-toolbar-right{display:flex;align-items:center;gap:10px}
.sp-label{font-size:12px;color:var(--muted);white-space:nowrap;font-weight:600}
.sp-count{font-size:12px;color:var(--muted)}
.sp-colors{display:flex;gap:6px;flex-wrap:wrap}
/* 1. Visual color picker — checkmark on selected */
.sp-dot{
  width:24px;height:24px;border-radius:7px;cursor:pointer;
  border:2px solid transparent;transition:transform .15s,border-color .15s,box-shadow .15s;
  flex-shrink:0;position:relative;display:flex;align-items:center;justify-content:center
}
.sp-dot:hover{transform:scale(1.2);box-shadow:0 2px 8px rgba(0,0,0,.25)}
.sp-dot.active{border-color:rgba(0,0,0,.55);transform:scale(1.1);box-shadow:0 0 0 2px rgba(0,0,0,.15)}
.sp-dot.active::after{
  content:'✓';font-size:11px;font-weight:700;color:rgba(0,0,0,.65);line-height:1
}
/* 2. Filter bar */
.sp-filter-bar{
  display:flex;align-items:center;gap:6px;flex-wrap:wrap;
  padding:8px 28px;border-bottom:1px solid var(--border);
  background:var(--bg);flex-shrink:0
}
.sp-filter-chip{
  display:flex;align-items:center;gap:4px;
  background:var(--sidebar);border:1.5px solid var(--border);
  border-radius:20px;padding:3px 10px;font-size:11px;
  color:var(--text2);cursor:pointer;font-weight:600;
  transition:all .15s
}
.sp-filter-chip:hover{border-color:var(--border2)}
.sp-filter-chip.active{border-color:var(--accent);color:var(--accent);background:rgba(139,94,42,.08)}
.sp-filter-chip .sp-filter-dot{width:10px;height:10px;border-radius:3px;display:inline-block}
.sp-board{
  flex:1;padding:20px 28px;overflow-y:auto;
  display:flex;flex-wrap:wrap;
  gap:16px;align-content:flex-start
}
.sp-empty{
  width:100%;display:flex;flex-direction:column;
  align-items:center;justify-content:center;padding:80px 20px;
  color:var(--muted);gap:10px;text-align:center
}
.sp-empty-icon{font-size:52px;opacity:.3}
.sp-empty p{font-size:13px;line-height:1.6}
/* 7. Animations */
@keyframes sp-fadein{from{opacity:0;transform:scale(.88) translateY(10px)}to{opacity:1;transform:scale(1) translateY(0)}}
@keyframes sp-fadeout{from{opacity:1;transform:scale(1)}to{opacity:0;transform:scale(.85) translateY(8px)}}
.sticky-card{
  border-radius:12px;padding:14px;
  display:flex;flex-direction:column;gap:6px;
  box-shadow:2px 4px 14px rgba(0,0,0,.18);
  transition:box-shadow .15s,transform .15s;
  min-height:140px;min-width:190px;
  position:relative;overflow:hidden;
  box-sizing:border-box;
  animation:sp-fadein .22s ease
}
.sticky-card:hover{box-shadow:4px 8px 22px rgba(0,0,0,.26);transform:translateY(-2px)}
.sticky-card.removing{animation:sp-fadeout .2s ease forwards}
/* 3. Pin badge */
.sticky-pin-btn{
  background:rgba(0,0,0,.12);border:none;border-radius:5px;
  color:rgba(0,0,0,.45);font-size:12px;cursor:pointer;
  padding:2px 6px;line-height:1.4;transition:all .15s
}
.sticky-pin-btn:hover{background:rgba(0,0,0,.2)}
.sticky-pin-btn.pinned{background:rgba(0,0,0,.22);color:rgba(0,0,0,.75)}
.sticky-pinned-badge{
  position:absolute;top:-1px;left:10px;
  font-size:9px;font-weight:700;background:rgba(0,0,0,.18);
  color:rgba(0,0,0,.6);border-radius:0 0 6px 6px;
  padding:1px 7px;letter-spacing:.5px;text-transform:uppercase
}
/* resize handle */
.sticky-resize-handle{
  position:absolute;bottom:0;right:0;
  width:22px;height:22px;cursor:nwse-resize;
  display:flex;align-items:flex-end;justify-content:flex-end;
  padding:4px;opacity:.3;transition:opacity .2s;z-index:5;
  border-radius:0 0 12px 0
}
.sticky-card:hover .sticky-resize-handle{opacity:.7}
.sticky-resize-handle:hover{opacity:1!important}
.sticky-resize-handle svg{width:12px;height:12px;pointer-events:none}
.sticky-card-header{display:flex;align-items:center;justify-content:space-between;gap:4px}
/* 5. timestamps */
.sticky-card-date{font-size:10px;color:rgba(0,0,0,.38);font-weight:500;line-height:1.4}
.sticky-card-del{
  background:rgba(0,0,0,.12);border:none;border-radius:5px;
  color:rgba(0,0,0,.5);font-size:12px;cursor:pointer;
  padding:2px 7px;line-height:1.4;transition:all .15s
}
.sticky-card-del:hover{background:rgba(180,0,0,.25);color:rgba(100,0,0,.8)}
/* 6. archive btn */
.sticky-archive-btn{
  background:rgba(0,0,0,.1);border:none;border-radius:5px;
  color:rgba(0,0,0,.45);font-size:11px;cursor:pointer;
  padding:2px 7px;line-height:1.4;transition:all .15s
}
.sticky-archive-btn:hover{background:rgba(0,0,0,.2)}
.sticky-card-body{
  font-size:13px;color:rgba(0,0,0,.78);line-height:1.6;
  flex:1;outline:none;min-height:60px;
  white-space:pre-wrap;word-break:break-word;cursor:text;
  border-radius:4px;padding:3px 5px
}
.sticky-card-body:focus{background:rgba(0,0,0,.05);outline:1px dashed rgba(0,0,0,.2)}
/* 4. tags row inside sticky */
.sticky-tags{display:flex;gap:4px;flex-wrap:wrap;margin-top:2px}
.sticky-tag{
  font-size:10px;font-weight:600;background:rgba(0,0,0,.12);
  color:rgba(0,0,0,.6);border-radius:10px;padding:1px 7px
}
.sticky-tag-input{
  font-size:11px;background:rgba(0,0,0,.08);border:none;outline:none;
  border-radius:10px;padding:2px 7px;color:rgba(0,0,0,.65);
  font-family:'Inter',sans-serif;min-width:60px;max-width:90px;
  cursor:text
}
.sticky-tag-input::placeholder{color:rgba(0,0,0,.35)}
.sticky-card-footer{
  font-size:10px;color:rgba(0,0,0,.35);
  border-top:1px solid rgba(0,0,0,.1);padding-top:6px;
  display:flex;justify-content:space-between;align-items:center;gap:6px
}
.sticky-save-hint{font-size:10px;color:rgba(0,0,0,.35);font-style:italic}
/* Archive panel */
.sp-archive-panel{
  display:none;flex-direction:column;
  background:var(--bg);border-top:1px solid var(--border);
  padding:16px 28px;flex-shrink:0
}
.sp-archive-panel.open{display:flex}
.sp-archive-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:10px}
.sp-archive-grid{display:flex;flex-wrap:wrap;gap:12px}

/* -- TRADING JOURNAL ------------------------------- */
.tj-toolbar{
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 28px;border-bottom:2px solid var(--border);
  background:#fff;flex-shrink:0;flex-wrap:wrap;gap:10px
}
.tj-toolbar-left{display:flex;gap:10px;flex-wrap:wrap}
.tj-select{
  background:#f0f4ff;border:1px solid #c8d4ee;border-radius:8px;
  padding:8px 14px;color:#1a2040;font-size:13px;font-family:'Inter',sans-serif;
  outline:none;cursor:pointer;font-weight:500
}
.tj-stats{
  display:grid;grid-template-columns:repeat(5,1fr);
  border-bottom:1px solid var(--border);flex-shrink:0;background:#fff
}
.tj-stat{
  padding:16px 22px;border-right:1px solid var(--border);
  display:flex;flex-direction:column;gap:4px;
}
.tj-stat:last-child{border-right:none}
.tj-stat-num{font-family:'Fraunces',serif;font-size:24px;font-weight:700;line-height:1}
.tj-stat-num.g{color:#059669}
.tj-stat-num.r{color:#dc2626}
.tj-stat-num.b{color:#3b5bdb}
.tj-stat-lbl{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#8898c0}
.tj-table-wrap{flex:1;padding:24px 28px;background:var(--bg)}
.tj-table{
  width:100%;border-collapse:collapse;
  background:#fff;border-radius:12px;
  overflow:hidden;border:1px solid #dde4f5;
  box-shadow:0 2px 8px rgba(59,91,219,.06)
}
.tj-table th{
  background:#f0f4ff;color:#3b5bdb;font-weight:700;
  text-transform:uppercase;font-size:10px;letter-spacing:.8px;
  padding:12px 14px;text-align:left;border-bottom:2px solid #dde4f5;
  white-space:nowrap
}
.tj-table td{
  padding:12px 14px;border-bottom:1px solid #f3f4ff;
  color:#374151;font-size:13px;vertical-align:middle
}
.tj-table tr:last-child td{border-bottom:none}
.tj-table tr:hover td{background:#f5f8ff;cursor:pointer}
.tj-symbol{font-weight:700;color:#1a2040;font-family:'Fraunces',serif;font-size:14px}
.tj-type-buy{color:#059669;font-weight:700;font-size:11px;background:#d1fae5;border-radius:4px;padding:3px 9px}
.tj-type-sell{color:#dc2626;font-weight:700;font-size:11px;background:#fee2e2;border-radius:4px;padding:3px 9px}
.tj-pnl-g{color:#059669;font-weight:700}
.tj-pnl-r{color:#dc2626;font-weight:700}
.tj-badge{display:inline-block;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:700}
.tj-badge.win{background:#d1fae5;color:#065f46}
.tj-badge.loss{background:#fee2e2;color:#991b1b}
.tj-badge.open{background:#dbeafe;color:#1e40af}
.tj-notes-cell{font-size:11px;color:#9ca3af;max-width:180px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tj-act-btn{
  background:#f8faff;border:1px solid #dde4f5;border-radius:5px;
  padding:4px 10px;font-size:11px;cursor:pointer;color:#4a5880;
  font-family:'Inter',sans-serif;transition:all .15s;font-weight:600
}
.tj-act-btn:hover{border-color:#3b5bdb;color:#3b5bdb;background:#eef2ff}
.tj-act-btn.del:hover{border-color:#dc2626;color:#dc2626;background:#fff5f5}
.tj-empty{
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;padding:60px 20px;color:var(--muted);
  gap:8px;text-align:center;
  background:#fff;border-radius:12px;border:2px dashed #dde4f5;
  margin-top:0
}
.tj-pnl-preview{
  background:#eef2ff;border:1px solid #c8d4ee;border-radius:8px;
  padding:11px 16px;display:flex;align-items:center;
  justify-content:space-between;font-size:13px;color:#4a5880;
  margin-top:4px;font-weight:500
}
@media(max-width:640px){
  .tj-toolbar{padding:12px 14px}
  .tj-table-wrap{padding:12px 14px}
  .tj-stats{grid-template-columns:repeat(3,1fr)}
  .tj-stat{padding:10px 12px}
}

/* -- ROUTINE PAGE ---------------------------------- */
.rt-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 28px;border-bottom:2px solid var(--accent);
  background:#fff;flex-wrap:wrap;gap:12px;
  box-shadow:0 2px 8px rgba(59,91,219,.06)
}
.rt-header-left{display:flex;flex-direction:column;gap:6px}
.rt-today-label{font-family:'Fraunces',serif;font-size:16px;font-weight:700;color:#1a2040}
.rt-progress-wrap{display:flex;align-items:center;gap:10px}
.rt-progress-bar{
  width:220px;height:8px;background:#e8edf8;border-radius:4px;overflow:hidden
}
.rt-progress-fill{
  height:100%;background:#3b5bdb;border-radius:4px;transition:width .4s ease
}
.rt-progress-pct{font-size:12px;font-weight:700;color:#3b5bdb}
.rt-header-right{display:flex;gap:8px;align-items:center}

/* checklist groups */
.rt-group{
  background:#fff;border:1px solid #dde4f5;border-radius:12px;
  margin-bottom:16px;overflow:hidden;
  box-shadow:0 2px 8px rgba(59,91,219,.05)
}
.rt-group-header{
  display:flex;align-items:center;gap:10px;
  padding:14px 18px;cursor:pointer;
  border-bottom:1px solid #f0f4ff;
  user-select:none
}
.rt-group-icon{font-size:18px}
.rt-group-name{
  font-family:'Fraunces',serif;font-size:15px;font-weight:700;color:#1a2040;flex:1
}
.rt-group-progress{
  font-size:11px;font-weight:700;color:#8898c0;
  background:#f0f4ff;border-radius:20px;padding:3px 10px
}
.rt-group-toggle{font-size:12px;color:#8898c0;margin-left:4px}

/* color accent on group */
.rt-group.c-blue .rt-group-header{border-left:4px solid #3b5bdb}
.rt-group.c-green .rt-group-header{border-left:4px solid #059669}
.rt-group.c-purple .rt-group-header{border-left:4px solid #7c3aed}
.rt-group.c-yellow .rt-group-header{border-left:4px solid #d97706}
.rt-group.c-red .rt-group-header{border-left:4px solid #dc2626}

/* tasks inside group */
.rt-tasks{padding:4px 0}
.rt-task-row{
  display:flex;align-items:center;gap:12px;
  padding:11px 18px;border-bottom:1px solid #f8faff;
  transition:background .15s;cursor:pointer
}
.rt-task-row:last-child{border-bottom:none}
.rt-task-row:hover{background:#f8faff}
.rt-task-row.done{opacity:.55}

/* custom checkbox */
.rt-checkbox{
  width:20px;height:20px;border-radius:50%;border:2px solid #c8d4ee;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;transition:all .2s;background:#fff
}
.rt-task-row.done .rt-checkbox{
  background:#3b5bdb;border-color:#3b5bdb;color:#fff;font-size:11px
}
.rt-task-info{flex:1;min-width:0}
.rt-task-name{
  font-size:13px;font-weight:600;color:#1a2040;
  transition:color .2s
}
.rt-task-row.done .rt-task-name{
  text-decoration:line-through;color:#9ca3af
}
.rt-task-meta{display:flex;align-items:center;gap:8px;margin-top:2px}
.rt-task-time{font-size:11px;color:#8898c0;font-weight:500}
.rt-task-freq{
  font-size:10px;font-weight:700;color:#3b5bdb;
  background:#eef2ff;border-radius:4px;padding:1px 6px
}
.rt-week-count{
  font-size:11px;font-weight:600;color:#6b7280;
  background:#f3f4f6;border-radius:4px;padding:2px 8px;
  margin-left:auto;white-space:nowrap
}

/* manage view */
.rt-manage-toolbar{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:18px
}
.rt-manage-title{
  font-family:'Fraunces',serif;font-size:17px;font-weight:700;color:#1a2040
}
.rt-manage-group{
  background:#fff;border:1px solid #dde4f5;border-radius:12px;
  margin-bottom:14px;overflow:hidden
}
.rt-manage-group-header{
  display:flex;align-items:center;gap:10px;padding:14px 18px;
  background:#f8faff;border-bottom:1px solid #f0f4ff
}
.rt-manage-group-name{font-weight:700;color:#1a2040;font-size:14px;flex:1}
.rt-mg-btn{
  background:#f0f4ff;border:1px solid #dde4f5;border-radius:6px;
  padding:4px 10px;font-size:11px;color:#4a5880;cursor:pointer;
  font-family:'Inter',sans-serif;font-weight:600;transition:all .15s
}
.rt-mg-btn:hover{border-color:#3b5bdb;color:#3b5bdb}
.rt-mg-btn.del:hover{border-color:#dc2626;color:#dc2626}
.rt-manage-tasks{padding:8px 0}
.rt-manage-task-row{
  display:flex;align-items:center;gap:10px;
  padding:9px 18px;border-bottom:1px solid #f8faff;font-size:13px;color:#374151
}
.rt-manage-task-row:last-child{border-bottom:none}
.rt-mtr-info{flex:1}
.rt-mtr-name{font-weight:600;color:#1a2040}
.rt-mtr-meta{font-size:11px;color:#8898c0;margin-top:2px}
.rt-add-task-row{
  padding:10px 18px;display:flex;align-items:center;gap:8px;
  border-top:1px solid #f0f4ff;background:#fafbff
}
.rt-add-task-btn{
  background:none;border:1px dashed #c8d4ee;border-radius:7px;
  padding:6px 14px;font-size:12px;color:#8898c0;cursor:pointer;
  font-family:'Inter',sans-serif;transition:all .15s;width:100%;text-align:left
}
.rt-add-task-btn:hover{border-color:#3b5bdb;color:#3b5bdb}

/* icon picker */
.rt-icon-picker{display:flex;gap:8px;flex-wrap:wrap;margin-top:4px}
.rt-icon-opt{
  font-size:20px;cursor:pointer;padding:5px;border-radius:8px;
  border:2px solid transparent;transition:all .15s
}
.rt-icon-opt:hover{background:#f0f4ff}
.rt-icon-opt.selected{border-color:#3b5bdb;background:#eef2ff}

/* day picker */
.rt-day-picker{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px}
.rt-day-opt{
  padding:5px 10px;border-radius:6px;border:1px solid #dde4f5;
  font-size:12px;font-weight:600;cursor:pointer;color:#6b7280;
  background:#f8faff;transition:all .15s
}
.rt-day-opt.selected{background:#3b5bdb;color:#fff;border-color:#3b5bdb}

@media(max-width:640px){
  .rt-header{padding:12px 14px}
  .rt-progress-bar{width:140px}
  #rt-today-view,#rt-manage-view{padding:12px 14px}
}

/* -- TASK & ACTION NOTES --------------------------- */
.tan-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 28px;border-bottom:2px solid var(--accent);
  background:var(--sidebar);flex-wrap:wrap;gap:12px;flex-shrink:0
}
.tan-title{font-family:'Fraunces',serif;font-size:17px;font-weight:700;color:var(--text)}
.tan-quick-bar{
  display:flex;gap:10px;align-items:flex-start;
  padding:16px 28px;background:var(--bg);
  border-bottom:1px solid var(--border);flex-shrink:0
}
.tan-quick-bar textarea{
  flex:1;resize:none;min-height:48px;max-height:140px;
  background:var(--sidebar);border:1.5px solid var(--border2);
  border-radius:10px;padding:10px 14px;color:var(--text);
  font-family:'EB Garamond',serif;font-size:15px;outline:none;
  transition:border-color .2s;line-height:1.5
}
.tan-quick-bar textarea:focus{border-color:var(--accent)}
.tan-quick-bar textarea::placeholder{color:var(--muted)}
.tan-add-btn{
  display:inline-flex;align-items:center;gap:5px;
  background:var(--accent);color:#fff;border:none;border-radius:10px;
  padding:10px 18px;font-size:13px;font-weight:600;cursor:pointer;
  font-family:'Inter',sans-serif;white-space:nowrap;transition:background .2s;flex-shrink:0
}
.tan-add-btn:hover{background:var(--accent2)}
.tan-filters{
  display:flex;align-items:center;gap:8px;
  padding:12px 28px;background:var(--bg);
  border-bottom:1px solid var(--border);flex-shrink:0;flex-wrap:wrap
}
.tan-filter-btn{
  background:var(--sidebar);border:1px solid var(--border);border-radius:20px;
  padding:5px 14px;font-size:12px;color:var(--text2);cursor:pointer;
  font-family:'Inter',sans-serif;font-weight:600;transition:all .15s
}
.tan-filter-btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.tan-filter-btn:hover:not(.active){border-color:var(--accent2);color:var(--accent)}
.tan-search{
  margin-left:auto;background:var(--sidebar);border:1px solid var(--border);
  border-radius:8px;padding:6px 12px;color:var(--text);font-size:13px;
  font-family:'Inter',sans-serif;outline:none;width:180px;transition:all .2s
}
.tan-search:focus{border-color:var(--accent);width:220px}
.tan-search::placeholder{color:var(--muted)}
.tan-list{flex:1;padding:16px 28px;overflow-y:auto}
.tan-empty{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:60px 20px;color:var(--muted);gap:8px;text-align:center
}
.tan-empty-icon{font-size:40px;opacity:.4}
/* 3. Collapsible section headers */
.tan-section-hdr{
  display:flex;align-items:center;gap:8px;
  padding:8px 4px;cursor:pointer;user-select:none;margin-bottom:6px;margin-top:4px
}
.tan-section-hdr:hover .tan-section-title{color:var(--accent)}
.tan-section-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.9px;color:var(--text2);transition:color .15s}
.tan-section-count{font-size:11px;background:var(--s2);color:var(--muted);border-radius:10px;padding:1px 8px;font-weight:600}
.tan-section-chevron{font-size:10px;color:var(--muted);transition:transform .2s}
.tan-section-chevron.collapsed{transform:rotate(-90deg)}
.tan-section-body{transition:opacity .2s}
.tan-section-body.collapsed{display:none}
/* 4. Card — left priority strip + shadow */
@keyframes tan-fadein{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
@keyframes tan-fadeout{from{opacity:1;max-height:120px;margin-bottom:10px}to{opacity:0;max-height:0;margin-bottom:0;padding:0}}
.tan-item{
  background:var(--sidebar);border:1.5px solid var(--border);
  border-radius:10px;margin-bottom:8px;
  display:flex;flex-direction:column;gap:0;
  transition:border-color .15s,box-shadow .15s;
  box-shadow:0 1px 4px rgba(0,0,0,.06);
  overflow:hidden;
  animation:tan-fadein .2s ease
}
.tan-item:hover{border-color:var(--border2);box-shadow:0 3px 10px rgba(139,94,42,.1)}
.tan-item.editing{border-color:var(--accent);box-shadow:0 0 0 2px rgba(139,94,42,.12)}
.tan-item.fading-out{animation:tan-fadeout .25s ease forwards}
/* 1. Left priority strip */
.tan-item-strip{width:4px;flex-shrink:0;border-radius:0;align-self:stretch;min-height:100%}
.tan-item-strip.high{background:#dc2626}
.tan-item-strip.medium{background:#d97706}
.tan-item-strip.low{background:#059669}
.tan-item-strip.none{background:var(--border)}
.tan-item-inner{padding:12px 14px;display:flex;flex-direction:column;gap:7px;flex:1;min-width:0}
.tan-item-top{display:flex;align-items:flex-start;gap:10px}
.tan-item-priority{
  display:inline-flex;align-items:center;gap:3px;
  font-size:10px;font-weight:700;border-radius:4px;padding:1px 6px;
  flex-shrink:0;margin-top:2px;white-space:nowrap
}
.tan-item-priority.high{background:#fee2e2;color:#991b1b}
.tan-item-priority.medium{background:#fef3c7;color:#92400e}
.tan-item-priority.low{background:#d1fae5;color:#065f46}
.tan-item-text{
  flex:1;font-family:'EB Garamond',serif;font-size:15px;
  color:var(--text);line-height:1.5;word-break:break-word
}
.tan-item-text.done{text-decoration:line-through;color:var(--muted)}
.tan-item-meta{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.tan-date-badge{
  font-size:11px;font-weight:600;color:var(--muted);
  background:var(--s2);border-radius:5px;padding:2px 8px;white-space:nowrap
}
/* 5. Tag chips */
.tan-tag-chip{
  display:inline-flex;align-items:center;gap:3px;
  background:rgba(139,94,42,.1);color:var(--accent);
  border-radius:20px;padding:1px 8px;font-size:11px;font-weight:600
}
.tan-tag-badge{
  font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;
  background:rgba(139,94,42,.12);color:var(--accent);
  border-radius:5px;padding:2px 8px
}
.tan-cat-badge{
  font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;
  border-radius:5px;padding:2px 9px;white-space:nowrap
}
.tan-cat-badge.personal{background:#dbeafe;color:#1e40af}
.tan-cat-badge.official{background:#f3e8ff;color:#6b21a8}
.tan-cat-sel{
  background:var(--sidebar);border:1.5px solid var(--border2);border-radius:10px;
  padding:10px 12px;color:var(--text);font-size:13px;font-family:'Inter',sans-serif;
  outline:none;cursor:pointer;flex-shrink:0;font-weight:600
}
.tan-cat-sel:focus{border-color:var(--accent)}
.tan-filters-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.tan-filters-divider{width:1px;height:20px;background:var(--border);flex-shrink:0;margin:0 4px}
.tan-item-actions{display:flex;gap:5px;align-items:center;margin-left:auto;flex-shrink:0;position:relative}
.tan-act{
  background:none;border:1px solid var(--border);border-radius:6px;
  padding:3px 9px;font-size:11px;cursor:pointer;color:var(--text2);
  font-family:'Inter',sans-serif;font-weight:600;transition:all .15s
}
.tan-act:hover{border-color:var(--accent);color:var(--accent)}
.tan-act.del:hover{border-color:#dc2626;color:#dc2626}
/* 7. 3-dot menu */
.tan-dot-btn{
  background:none;border:1px solid transparent;border-radius:6px;
  padding:3px 7px;font-size:14px;cursor:pointer;color:var(--muted);
  line-height:1;transition:all .15s
}
.tan-dot-btn:hover{border-color:var(--border);color:var(--text)}
.tan-dropdown{
  position:absolute;top:100%;right:0;z-index:50;margin-top:4px;
  background:var(--sidebar);border:1.5px solid var(--border2);
  border-radius:10px;min-width:160px;overflow:hidden;display:none;
  box-shadow:0 4px 16px rgba(0,0,0,.14)
}
.tan-dropdown.open{display:block}
.tan-dd-item{
  display:flex;align-items:center;gap:8px;padding:9px 14px;
  font-size:12px;font-weight:600;color:var(--text2);cursor:pointer;
  transition:background .12s;font-family:'Inter',sans-serif
}
.tan-dd-item:hover{background:var(--s2);color:var(--text)}
.tan-dd-item.danger:hover{background:#fee2e2;color:#dc2626}
.tan-edit-area{display:none;flex-direction:column;gap:8px;padding:0 14px 12px}
.tan-edit-area.open{display:flex}
.tan-edit-textarea{
  width:100%;resize:none;min-height:60px;
  background:var(--bg);border:1.5px solid var(--border2);
  border-radius:8px;padding:9px 12px;color:var(--text);
  font-family:'EB Garamond',serif;font-size:15px;outline:none;
  transition:border-color .2s
}
.tan-edit-textarea:focus{border-color:var(--accent)}
.tan-edit-row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tan-priority-sel{
  background:var(--bg);border:1px solid var(--border2);border-radius:7px;
  padding:5px 10px;color:var(--text);font-size:12px;font-family:'Inter',sans-serif;
  outline:none;cursor:pointer
}
.tan-tag-input{
  flex:1;background:var(--bg);border:1px solid var(--border2);border-radius:7px;
  padding:5px 10px;color:var(--text);font-size:12px;font-family:'Inter',sans-serif;
  outline:none;min-width:100px
}
.tan-tag-input::placeholder{color:var(--muted)}
.tan-save-btn{
  background:var(--accent);color:#fff;border:none;border-radius:7px;
  padding:6px 14px;font-size:12px;font-weight:600;cursor:pointer;
  font-family:'Inter',sans-serif;transition:background .2s
}
.tan-save-btn:hover{background:var(--accent2)}
.tan-done-cb{width:16px;height:16px;accent-color:var(--accent);cursor:pointer;flex-shrink:0;margin-top:3px}
/* 6. Sort select */
.tan-sort-sel{
  background:var(--sidebar);border:1px solid var(--border);border-radius:7px;
  padding:5px 10px;color:var(--text2);font-size:12px;font-family:'Inter',sans-serif;
  outline:none;cursor:pointer;font-weight:600;margin-left:auto
}
@media(max-width:640px){
  .tan-header,.tan-quick-bar,.tan-filters,.tan-list{padding-left:14px;padding-right:14px}
  .tan-filters{gap:6px}
}

/* -- FINANCE TRACKER ------------------------------- */
.fin-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 28px;border-bottom:2px solid var(--accent);
  background:var(--sidebar);flex-wrap:wrap;gap:12px;flex-shrink:0
}
.fin-title{font-family:'Fraunces',serif;font-size:17px;font-weight:700;color:var(--text)}
.fin-summary{
  display:grid;grid-template-columns:repeat(3,1fr);
  gap:10px;padding:12px 20px;border-bottom:1px solid var(--border);
  background:var(--bg);flex-shrink:0
}
.fin-sum-card{
  background:var(--sidebar);border:1.5px solid var(--border);
  border-radius:10px;padding:10px 14px;display:flex;flex-direction:column;gap:3px
}
.fin-sum-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)}
.fin-sum-val{font-family:'Fraunces',serif;font-size:19px;font-weight:700;line-height:1.1}
.fin-sum-val.gave{color:#059669}
.fin-sum-val.borrow{color:#dc2626}
.fin-sum-val.net-pos{color:#059669}
.fin-sum-val.net-neg{color:#dc2626}
.fin-sum-sub{font-size:11px;color:var(--muted);margin-top:2px}
.fin-people{
  padding:10px 20px 0;flex-shrink:0
}
.fin-people-title{
  font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;
  color:var(--muted);margin-bottom:10px
}
.fin-person-chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:4px}
.fin-person-chip{
  display:flex;align-items:center;gap:6px;
  background:var(--sidebar);border:1.5px solid var(--border);
  border-radius:20px;padding:6px 14px;cursor:pointer;transition:all .15s
}
.fin-person-chip:hover{border-color:var(--accent2)}
.fin-person-chip.active{border-color:var(--accent);background:rgba(139,94,42,.1)}
.fin-person-name{font-size:12px;font-weight:700;color:var(--text)}
.fin-person-bal{font-size:11px;font-weight:700}
.fin-person-bal.pos{color:#059669}
.fin-person-bal.neg{color:#dc2626}
.fin-filters{
  display:flex;align-items:center;gap:6px;flex-wrap:wrap;
  padding:8px 20px;border-bottom:1px solid var(--border);
  background:var(--bg);flex-shrink:0
}
.fin-list{flex:1;padding:12px 20px;overflow-y:auto}
.fin-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px}
@media(max-width:1400px){.fin-grid{grid-template-columns:repeat(5,minmax(0,1fr))}}
@media(max-width:1200px){.fin-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media(max-width:900px){.fin-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:600px){.fin-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:400px){.fin-grid{grid-template-columns:1fr}}
/* Finance card — Notes-style */
.fin-card{
  background:var(--sidebar);border:1.5px solid var(--border);
  border-left:4px solid var(--accent);border-radius:12px;
  padding:14px 16px;display:flex;flex-direction:column;gap:8px;
  cursor:pointer;transition:border-color .18s,box-shadow .18s
}
.fin-card:hover{border-color:var(--border2);box-shadow:0 4px 14px rgba(139,94,42,.1)}
.fin-card.gave{border-left-color:#059669}
.fin-card.borrowed{border-left-color:#dc2626}
.fin-card.settled{border-left-color:#9ca3af}
.fin-card.overdue-card{border-left-color:#dc2626;border-color:rgba(220,38,38,.3);animation:fin-shake 3s ease 0.5s}
@keyframes fin-shake{0%,100%{transform:translateX(0)}10%{transform:translateX(-3px)}20%{transform:translateX(3px)}30%{transform:translateX(-2px)}40%{transform:translateX(2px)}50%,90%{transform:translateX(0)}}
/* 3. Floating Add Button */
.fin-fab{
  position:fixed;bottom:28px;right:28px;z-index:100;
  width:52px;height:52px;border-radius:50%;
  background:var(--accent);color:#fff;border:none;
  font-size:24px;cursor:pointer;
  box-shadow:0 4px 16px rgba(139,94,42,.45);
  transition:transform .15s,box-shadow .15s;
  display:none;align-items:center;justify-content:center;font-weight:300
}
.fin-fab:hover{transform:scale(1.1);box-shadow:0 6px 20px rgba(139,94,42,.55)}
.fin-fab.visible{display:flex}
/* 5. Sort select */
.fin-sort-sel{
  background:var(--sidebar);border:1px solid var(--border);border-radius:7px;
  padding:5px 10px;color:var(--text2);font-size:12px;font-family:'Inter',sans-serif;
  outline:none;cursor:pointer;font-weight:600
}
/* 2. Group by person */
.fin-group-hdr{
  display:flex;align-items:center;gap:10px;
  padding:10px 4px 6px;cursor:pointer;user-select:none
}
.fin-group-hdr:hover .fin-group-name{color:var(--accent)}
.fin-group-chevron{font-size:10px;color:var(--muted);transition:transform .2s}
.fin-group-chevron.collapsed{transform:rotate(-90deg)}
.fin-group-name{font-family:'Fraunces',serif;font-size:13px;font-weight:700;color:var(--text);transition:color .15s}
.fin-group-bal{font-size:11px;font-weight:700}
.fin-group-bal.pos{color:#059669}
.fin-group-bal.neg{color:#dc2626}
.fin-group-count{font-size:10px;background:var(--s2);color:var(--muted);border-radius:10px;padding:1px 7px;font-weight:600}
.fin-group-body{transition:opacity .2s}
.fin-group-body.collapsed{display:none}
/* 7. Timeline panel */
.fin-timeline-panel{
  display:none;background:var(--bg);border-top:1px solid var(--border);
  padding:16px 28px;flex-shrink:0;max-height:260px;overflow-y:auto
}
.fin-timeline-panel.open{display:block}
.fin-tl-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:12px}
.fin-tl-row{
  display:flex;align-items:center;gap:10px;
  padding:8px 0;border-bottom:1px solid var(--border);font-size:12px
}
.fin-tl-row:last-child{border-bottom:none}
.fin-tl-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.fin-tl-dot.overdue{background:#dc2626}
.fin-tl-dot.today{background:#d97706}
.fin-tl-dot.soon{background:#d97706}
.fin-tl-dot.ok{background:#059669}
.fin-tl-date{font-weight:700;color:var(--text);min-width:90px}
.fin-tl-person{color:var(--text2);flex:1}
.fin-tl-amt{font-weight:700;font-family:'Fraunces',serif}
.fin-tl-amt.gave{color:#059669}
.fin-tl-amt.borrowed{color:#dc2626}
/* 8. Settled history toggle */
.fin-settled-section{margin-top:8px}
.fin-settled-hdr{
  display:flex;align-items:center;gap:8px;cursor:pointer;
  padding:8px 4px;user-select:none
}
.fin-settled-hdr:hover span{color:var(--accent)}
.fin-settled-body{transition:opacity .2s}
.fin-settled-body.collapsed{display:none}
.fin-card-eyebrow{display:flex;align-items:center;justify-content:space-between}
.fin-card-type{font-size:10px;text-transform:uppercase;letter-spacing:1.2px;color:var(--muted);font-weight:700}
.fin-card-person{font-family:'Fraunces',serif;font-size:15px;font-weight:700;color:var(--text);line-height:1.3}
.fin-card-amount{font-family:'Fraunces',serif;font-size:19px;font-weight:700}
.fin-card-amount.gave{color:#059669}
.fin-card-amount.borrowed{color:#dc2626}
.fin-card-amount.settled{color:var(--muted)}
.fin-card-note{font-family:'EB Garamond',serif;font-size:13px;color:var(--text2);line-height:1.5}
.fin-card-tags{display:flex;gap:5px;flex-wrap:wrap}
.fin-card-meta{
  display:flex;align-items:center;justify-content:space-between;
  padding-top:8px;border-top:1px solid var(--border)
}
.fin-card-date{font-size:10px;color:var(--muted);font-weight:500}
.fin-card-btns{display:flex;gap:5px}
/* Finance list-row */
.fin-lrow{
  display:flex;align-items:center;gap:10px;
  padding:10px 14px;border-bottom:1px solid var(--border);
  background:var(--sidebar);cursor:pointer;transition:background .15s
}
.fin-lrow:first-child{border-top:1px solid var(--border);border-radius:10px 10px 0 0}
.fin-lrow:last-child{border-bottom:none;border-radius:0 0 10px 10px}
.fin-lrow:hover{background:var(--s2)}
.fin-lrow-accent{width:3px;height:32px;border-radius:2px;flex-shrink:0}
.fin-lrow-accent.gave{background:#059669}
.fin-lrow-accent.borrowed{background:#dc2626}
.fin-lrow-accent.settled{background:#9ca3af}
.fin-lrow-main{flex:1;min-width:0}
.fin-lrow-person{font-size:13px;font-weight:700;color:var(--text)}
.fin-lrow-note{font-size:11px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:220px}
.fin-lrow-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
.fin-lrow-amt{font-family:'Fraunces',serif;font-size:14px;font-weight:700}
.fin-lrow-amt.gave{color:#059669}
.fin-lrow-amt.borrowed{color:#dc2626}
.fin-lrow-amt.settled{color:var(--muted)}
.fin-view-list .fin-grid{display:none}
.fin-view-list .fin-listbox{display:block}
.fin-view-card .fin-listbox{display:none}
.fin-listbox{display:none;border-radius:10px;overflow:hidden;border:1px solid var(--border)}
.fin-empty{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:60px 20px;color:var(--muted);gap:8px;text-align:center
}
.fin-item{
  background:var(--sidebar);border:1.5px solid var(--border);
  border-radius:8px;padding:7px 10px;margin-bottom:0;
  cursor:pointer;transition:border-color .15s,background .15s
}
.fin-item:hover{border-color:var(--border2)}
.fin-item.expanded{border-color:var(--accent);background:var(--bg)}
.fin-item-row{display:flex;align-items:center;gap:8px}
.fin-item-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.fin-item-dot.gave{background:#059669}
.fin-item-dot.borrowed{background:#dc2626}
.fin-item-dot.settled{background:#9ca3af}
.fin-item-body{flex:1;min-width:0}
.fin-item-person{font-size:12px;font-weight:700;color:var(--text);line-height:1.2}
.fin-item-meta{display:flex;align-items:center;gap:4px;flex-wrap:wrap;margin-top:2px}
.fin-item-right{display:flex;flex-direction:column;align-items:flex-end;gap:1px;flex-shrink:0}
.fin-item-amount{font-family:'Fraunces',serif;font-size:13px;font-weight:700}
.fin-item-amount.gave{color:#059669}
.fin-item-amount.borrowed{color:#dc2626}
.fin-item-amount.settled{color:var(--muted)}
.fin-item-remaining{font-size:10px;color:var(--muted)}
.fin-item-expand{
  display:none;margin-top:8px;padding-top:8px;
  border-top:1px dashed var(--border)
}
.fin-item.expanded .fin-item-expand{display:block}
.fin-status-badge{
  font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;
  border-radius:5px;padding:2px 8px
}
.fin-status-badge.pending{background:#fef3c7;color:#92400e}
.fin-status-badge.partial{background:#dbeafe;color:#1e40af}
.fin-status-badge.settled{background:#d1fae5;color:#065f46}
.fin-status-badge.overdue{background:#fee2e2;color:#991b1b}
.fin-date-badge{
  font-size:11px;font-weight:600;color:var(--muted);
  background:var(--s2);border-radius:5px;padding:2px 8px
}
.fin-due-badge{font-size:11px;font-weight:600;border-radius:5px;padding:2px 8px}
.fin-due-badge.ok{background:#d1fae5;color:#065f46}
.fin-due-badge.warn{background:#fef3c7;color:#92400e}
.fin-due-badge.over{background:#fee2e2;color:#991b1b}
.fin-item-actions{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap;align-items:center}
.fin-act{
  background:none;border:1px solid var(--border);border-radius:6px;
  padding:4px 10px;font-size:11px;cursor:pointer;color:var(--text2);
  font-family:'Inter',sans-serif;font-weight:600;transition:all .15s
}
.fin-act:hover{border-color:var(--accent);color:var(--accent)}
.fin-act.del:hover{border-color:#dc2626;color:#dc2626}
.fin-act.settle{background:var(--accent);color:#fff;border-color:var(--accent)}
.fin-act.settle:hover{background:var(--accent2)}
.fin-repay-section{
  margin-top:10px;padding-top:10px;border-top:1px dashed var(--border)
}
.fin-repay-title{
  font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;
  color:var(--muted);margin-bottom:8px
}
.fin-repay-row{
  display:flex;align-items:center;gap:8px;
  padding:5px 0;border-bottom:1px solid var(--border);font-size:12px;color:var(--text2)
}
.fin-repay-row:last-child{border-bottom:none}
.fin-repay-amt{font-weight:700;color:#059669;min-width:80px}
.fin-repay-note{flex:1;color:var(--muted)}
.fin-pay-badge{
  font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;
  border-radius:5px;padding:2px 7px;white-space:nowrap
}
.fin-pay-badge.cash{background:#d1fae5;color:#065f46}
.fin-pay-badge.credit_card{background:#dbeafe;color:#1e40af}
.fin-pay-badge.bank{background:#ede9fe;color:#5b21b6}
.fin-pay-badge.upi{background:#fef3c7;color:#92400e}
.fin-rtype-badge{
  font-size:10px;font-weight:700;border-radius:5px;padding:2px 7px;white-space:nowrap
}
.fin-rtype-badge.principal{background:#d1fae5;color:#065f46}
.fin-rtype-badge.interest{background:#fee2e2;color:#991b1b}
.fin-rtype-badge.both{background:#dbeafe;color:#1e40af}
.fin-history-wrap{
  margin-top:10px;padding-top:10px;border-top:1px dashed var(--border)
}
.fin-history-header{
  display:flex;align-items:center;justify-content:space-between;margin-bottom:8px
}
.fin-history-title{
  font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)
}
.fin-history-summary{font-size:11px;color:var(--muted)}
.fin-repay-row{
  display:flex;align-items:center;gap:6px;flex-wrap:wrap;
  padding:7px 0;border-bottom:1px solid var(--border);font-size:12px
}
.fin-repay-row:last-child{border-bottom:none}
  display:flex;gap:8px;align-items:center;margin-top:10px;flex-wrap:wrap
}
.fin-repay-input{
  background:var(--bg);border:1.5px solid var(--border2);border-radius:7px;
  padding:6px 10px;color:var(--text);font-size:13px;font-family:'Inter',sans-serif;
  outline:none;transition:border-color .2s
}
.fin-repay-input:focus{border-color:var(--accent)}
.fin-repay-input::placeholder{color:var(--muted)}
.fin-add-repay-btn{
  background:var(--accent);color:#fff;border:none;border-radius:7px;
  padding:7px 14px;font-size:12px;font-weight:600;cursor:pointer;
  font-family:'Inter',sans-serif;white-space:nowrap;transition:background .2s
}
.fin-add-repay-btn:hover{background:var(--accent2)}
.fin-progress{
  height:5px;background:var(--s2);border-radius:3px;overflow:hidden;margin-top:8px
}
.fin-progress-fill{height:100%;border-radius:3px;background:#059669;transition:width .4s}
@media(max-width:640px){
  .fin-header,.fin-summary,.fin-people,.fin-filters,.fin-list{padding-left:12px;padding-right:12px}
  .fin-summary{grid-template-columns:1fr 1fr}
}

/* -- TOAST ----------------------------------------- */
#toast{
  position:fixed;bottom:20px;right:20px;z-index:999;
  background:var(--sidebar);border:1px solid var(--border2);
  border-radius:10px;padding:10px 16px;font-size:13px;color:var(--text);
  transform:translateY(50px);opacity:0;transition:all .25s;pointer-events:none
}
#toast.show{transform:translateY(0);opacity:1}
#toast.success{border-color:var(--green);color:var(--green)}
#toast.error{border-color:var(--red);color:var(--red)}

/* -- RESPONSIVE ------------------------------------ */
@media(max-width:860px){
  .stats-row{grid-template-columns:repeat(2,1fr)}
  .gh-fields{grid-template-columns:1fr}
  .sp-toolbar{flex-direction:column;align-items:flex-start}
  .sp-toolbar-right{width:100%;justify-content:space-between}
  /* hide CST on tablet, keep IST */
  .clock-block:last-child{display:none}
  .clock-block{min-width:90px;padding:0 12px}
  .clock-time{font-size:13px}
}
@media(max-width:640px){
  aside{
    transform:translateX(-100%);
    transition:transform .25s ease;
    z-index:200;
    width:260px;
    box-shadow:4px 0 24px rgba(0,0,0,.3)
  }
  aside.open{transform:translateX(0)}
  .sidebar-overlay{
    display:none;position:fixed;inset:0;
    background:rgba(0,0,0,.5);z-index:199
  }
  .sidebar-overlay.open{display:block}
  .main{margin-left:0}
  .topbar{padding:0}
  /* hide clocks entirely on mobile */
  .clock-bar{display:none}
  .hamburger{
    display:flex!important;align-items:center;justify-content:center;
    background:var(--s2);border:1px solid var(--border2);
    border-radius:8px;width:36px;height:36px;
    font-size:16px;cursor:pointer;flex-shrink:0
  }
  .stats-row{
    grid-template-columns:repeat(2,1fr);
    padding:12px 14px;gap:10px
  }
  .stat-card{padding:12px}
  .stat-num{font-size:20px!important}
  .content{padding:12px 14px}
  .cards-grid{grid-template-columns:1fr}
  .sec-header{flex-wrap:wrap;gap:8px}
  .search-wrap input{width:140px}
  .search-wrap input:focus{width:160px}
  .theme-grid{grid-template-columns:1fr 1fr}
  .settings-modal{padding:20px}
  .sp-board{padding:14px}
  .sp-toolbar{padding:12px 14px}
  .lrow-date{display:none}
  .lrow-tags{max-width:100px}
  .lrow-due{font-size:10px;padding:2px 6px}
  .modal{padding:20px}
}
@media(max-width:400px){
  .stats-row{grid-template-columns:repeat(2,1fr)}
  .topbar-right .search-wrap{display:none}
  .lrow-tags{display:none}
}
.hamburger{display:none}
</style>
</head>
<body class="theme-cream">
<!-- mobile sidebar overlay -->
<div class="sidebar-overlay" id="sidebar-overlay" onclick="closeSidebar()"></div>
<div class="layout">

<!-- -- SIDEBAR ----------------------------------- -->
<aside>
  <div class="sidebar-logo">📓 MyNotes</div>

  <div class="sidebar-section">Views</div>
  <button class="nav-item active" id="nav-dashboard" onclick="showPage('dashboard',this)" title="Show everything">
    <span class="nav-icon">🏠</span> All Items
    <span class="nav-count" id="nav-all">0</span>
  </button>
  <button class="nav-item" id="nav-notes-btn" onclick="showPage('dashboard',this);filterCards('note',this)">
    <span class="nav-icon">📝</span> Notes
    <span class="nav-count" id="nav-notes">0</span>
  </button>
  <button class="nav-item" id="nav-reminders-btn" onclick="showPage('dashboard',this);filterCards('reminder',this)">
    <span class="nav-icon">⏰</span> Reminders
    <span class="nav-count" id="nav-reminders">0</span>
  </button>
  <button class="nav-item" id="nav-sticky-btn" onclick="showPage('sticky',this)">
    <span class="nav-icon">📌</span> Sticky Notes
    <span class="nav-count" id="nav-sticky-count">0</span>
  </button>
  <button class="nav-item" id="nav-journal-btn" onclick="showPage('journal',this)">
    <span class="nav-icon">📈</span> Trading Journal
    <span class="nav-count" id="nav-journal-count">0</span>
  </button>
  <button class="nav-item" id="nav-routine-btn" onclick="showPage('routine',this)">
    <span class="nav-icon">🔁</span> Routine
    <span class="nav-count" id="nav-routine-count">0</span>
  </button>
  <button class="nav-item" id="nav-tasknotes-btn" onclick="showPage('tasknotes',this)">
    <span class="nav-icon">✍️</span> Task Notes
    <span class="nav-count" id="nav-tasknotes-count">0</span>
  </button>
  <button class="nav-item" id="nav-finance-btn" onclick="showPage('finance',this)">
    <span class="nav-icon">💰</span> Finance Tracker
    <span class="nav-count" id="nav-finance-count">0</span>
  </button>

  <div class="sidebar-section">Status</div>
  <button class="nav-item" onclick="showPage('dashboard',this);filterCards('pending',this)">
    <span class="nav-icon">🔔</span> Pending
    <span class="nav-count" id="nav-pending">0</span>
  </button>
  <button class="nav-item" onclick="showPage('dashboard',this);filterCards('overdue',this)">
    <span class="nav-icon">🔴</span> Overdue
    <span class="nav-count" id="nav-overdue">0</span>
  </button>
  <button class="nav-item" onclick="showPage('dashboard',this);filterCards('sent',this)">
    <span class="nav-icon">✅</span> Completed
    <span class="nav-count" id="nav-sent">0</span>
  </button>

  <div class="sidebar-footer">
    <div class="sync-pill">
      <div class="sdot" id="sdot"></div>
      <span id="stext">Ready</span>
    </div>
    <button class="btn-ghost" onclick="openSettings()" style="width:100%;margin-top:8px;justify-content:center;display:flex">
      ⚙️ Settings
    </button>
  </div>
</aside>

<!-- -- MAIN --------------------------------------- -->
<div class="main">
  <div class="topbar">
    <div class="topbar-left">
      <button class="hamburger" onclick="openSidebar()" title="Menu">☰</button>
      <div class="page-title" id="page-title">📋 Dashboard</div>
    </div>
    <div style="display:flex;align-items:stretch">
      <!-- 5. Context-aware actions -->
      <div class="topbar-ctx" id="topbar-ctx">
        <!-- dashboard: search + add -->
        <div id="ctx-dashboard" style="display:flex;align-items:center;gap:8px">
          <div class="topbar-right" id="topbar-search-wrap">
            <div class="search-wrap" id="topbar-search">
              <span class="s-icon">🔍</span>
              <input type="text" placeholder="Search..." oninput="searchCards(this.value)">
            </div>
            <button class="btn" id="topbar-add-btn" onclick="openModal()">+ Add New</button>
          </div>
        </div>
        <!-- sticky: new + color hint -->
        <div id="ctx-sticky" style="display:none;align-items:center;gap:8px">
          <button class="btn" onclick="addSticky()">+ New Sticky</button>
        </div>
        <!-- journal: new trade -->
        <div id="ctx-journal" style="display:none;align-items:center;gap:8px">
          <button class="btn" onclick="openTradeModal()">+ New Trade</button>
        </div>
        <!-- routine: new routine -->
        <div id="ctx-routine" style="display:none;align-items:center;gap:8px">
          <button class="btn" onclick="openRoutineGroupModal()">+ New Routine</button>
        </div>
        <!-- tasknotes: add note -->
        <div id="ctx-tasknotes" style="display:none;align-items:center;gap:8px">
          <button class="btn" onclick="document.getElementById('tan-quick-input').focus()">+ Quick Note</button>
        </div>
        <!-- finance: new entry -->
        <div id="ctx-finance" style="display:none;align-items:center;gap:8px">
          <button class="btn" onclick="openFinModal()">+ New Entry</button>
        </div>
      </div>
      <!-- Clock -->
      <div class="clock-bar">
        <div class="clock-block">
          <div class="clock-zone"><span class="clock-zone-flag">🇮🇳</span> IST</div>
          <div class="clock-time" id="clk-ist-time">--:--:--</div>
          <div class="clock-date" id="clk-ist-date">--</div>
        </div>
        <div class="clock-block">
          <div class="clock-zone"><span class="clock-zone-flag">🇺🇸</span> CST</div>
          <div class="clock-time" id="clk-cst-time">--:--:--</div>
          <div class="clock-date" id="clk-cst-date">--</div>
        </div>
      </div>
    </div>
  </div>

  <!-- == DASHBOARD PAGE == -->
  <div id="page-dashboard">
    <div class="stats-row">
      <div class="stat-card" id="sc-notes" onclick="statFilter('note',this)">
        <div class="stat-icon si-notes">📝</div>
        <div><div class="stat-num" id="stat-notes">0</div><div class="stat-label">Notes</div></div>
      </div>
      <div class="stat-card" id="sc-reminders" onclick="statFilter('reminder',this)">
        <div class="stat-icon si-rem">⏰</div>
        <div><div class="stat-num" id="stat-reminders">0</div><div class="stat-label">Reminders</div></div>
      </div>
      <div class="stat-card" id="sc-pending" onclick="statFilter('pending',this)">
        <div class="stat-icon si-pend">🔔</div>
        <div><div class="stat-num" id="stat-pending">0</div><div class="stat-label">Pending</div></div>
      </div>
      <div class="stat-card" id="sc-all" onclick="statFilter('sent',this)">
        <div class="stat-icon si-files">✅</div>
        <div><div class="stat-num" id="stat-files">0</div><div class="stat-label">Completed</div></div>
      </div>
    </div>
    <div class="content">
      <div class="sec-header" id="rem-sec-header">
        <div class="sec-title">⏰ Reminders <span class="pill" id="rem-pill">0</span></div>
        <div style="display:flex;align-items:center;gap:8px">
          <div class="view-toggle">
            <button class="vtbtn active" id="rem-vcard" onclick="setView('rem','card')" title="Card view">⊞</button>
            <button class="vtbtn" id="rem-vlist" onclick="setView('rem','list')" title="List view">☰</button>
          </div>
          <button class="btn-ghost" style="font-size:12px" onclick="openModal('reminder')">+ Add Reminder</button>
        </div>
      </div>
      <div id="rem-cat-filter" style="display:flex;align-items:center;gap:8px;margin-bottom:10px;padding:0 2px">
        <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)">Category</span>
        <button class="tan-filter-btn active" id="rem-fc-all"      onclick="setRemCatFilter('all',this)">All</button>
        <button class="tan-filter-btn"        id="rem-fc-personal" onclick="setRemCatFilter('personal',this)">👤 Personal</button>
        <button class="tan-filter-btn"        id="rem-fc-official" onclick="setRemCatFilter('official',this)">💼 Official</button>
      </div>
      <div id="rem-section">
        <div class="cards-grid" id="reminders-grid"></div>
        <div class="list-view-wrap"><div class="list-view" id="reminders-list"></div></div>
      </div>
      <div class="sec-header" id="notes-sec-header" style="margin-top:8px">
        <div class="sec-title">📝 Notes <span class="pill" id="notes-pill">0</span></div>
        <div style="display:flex;align-items:center;gap:8px">
          <div class="view-toggle">
            <button class="vtbtn active" id="notes-vcard" onclick="setView('notes','card')" title="Card view">⊞</button>
            <button class="vtbtn" id="notes-vlist" onclick="setView('notes','list')" title="List view">☰</button>
          </div>
          <button class="btn-ghost" style="font-size:12px" onclick="openModal('note')">+ Add Note</button>
        </div>
      </div>
      <div id="notes-cat-filter" style="display:flex;align-items:center;gap:8px;margin-bottom:10px;padding:0 2px">
        <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)">Category</span>
        <button class="tan-filter-btn active" id="notes-fc-all"      onclick="setNotesCatFilter('all',this)">All</button>
        <button class="tan-filter-btn"        id="notes-fc-personal" onclick="setNotesCatFilter('personal',this)">👤 Personal</button>
        <button class="tan-filter-btn"        id="notes-fc-official" onclick="setNotesCatFilter('official',this)">💼 Official</button>
      </div>
      <div id="notes-section">
        <div class="cards-grid" id="notes-grid"></div>
        <div class="list-view-wrap"><div class="list-view" id="notes-list"></div></div>
      </div>
    </div>
  </div>

  <!-- == STICKY NOTES PAGE == -->
  <div id="page-sticky" style="display:none;flex-direction:column;height:calc(100vh - 56px)">

    <!-- Colour picker toolbar -->
    <div class="sp-toolbar">
      <div class="sp-toolbar-left">
        <span class="sp-label">Colour:</span>
        <div class="sp-colors" id="sp-colors"></div>
      </div>
      <div class="sp-toolbar-right">
        <span class="sp-count" id="sp-count">0 stickies</span>
        <button class="btn-ghost" onclick="toggleArchivePanel()" style="font-size:12px">🗂 Archive</button>
        <button class="btn" onclick="addSticky()">+ New Sticky</button>
      </div>
    </div>

    <!-- 2. Filter bar -->
    <div class="sp-filter-bar" id="sp-filter-bar">
      <span style="font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.8px">Filter:</span>
      <div class="sp-filter-chip active" id="spf-all" onclick="spSetFilter('all',this)">All</div>
      <div class="sp-filter-chip" id="spf-pinned" onclick="spSetFilter('pinned',this)">📌 Pinned</div>
      <div id="sp-color-filters" style="display:flex;flex-wrap:wrap;gap:6px;align-items:center"></div>
    </div>

    <!-- Sticky board -->
    <div class="sp-board" id="sp-board">
      <div class="sp-empty" id="sp-empty">
        <div class="sp-empty-icon">📌</div>
        <p>No sticky notes yet</p>
        <p style="font-size:12px">Pick a colour above and click <strong>+ New Sticky</strong></p>
      </div>
    </div>

    <!-- 6. Archive panel -->
    <div class="sp-archive-panel" id="sp-archive-panel">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
        <span class="sp-archive-title">🗂 Archived Stickies</span>
        <button class="btn-ghost" style="font-size:11px" onclick="toggleArchivePanel()">✕ Close</button>
      </div>
      <div class="sp-archive-grid" id="sp-archive-grid">
        <span style="font-size:12px;color:var(--muted)">No archived stickies</span>
      </div>
    </div>

  </div>

  <!-- -- TRADING JOURNAL PAGE ---------------------- -->
<div id="page-journal" style="display:none;flex-direction:column;width:100%;min-height:calc(100vh - 60px);background:var(--bg)">

  <!-- Toolbar -->
  <div class="tj-toolbar">
    <div class="tj-toolbar-left">
      <select id="tj-filter-month" class="tj-select" onchange="renderJournal()">
        <option value="all">📅 All Time</option>
        <option value="0">January</option><option value="1">February</option>
        <option value="2">March</option><option value="3">April</option>
        <option value="4">May</option><option value="5">June</option>
        <option value="6">July</option><option value="7">August</option>
        <option value="8">September</option><option value="9">October</option>
        <option value="10">November</option><option value="11">December</option>
      </select>
      <select id="tj-filter-status" class="tj-select" onchange="renderJournal()">
        <option value="all">All Trades</option>
        <option value="win">✅ Wins</option>
        <option value="loss">❌ Losses</option>
        <option value="open">⏳ Open</option>
      </select>
    </div>
    <button class="btn" onclick="openTradeModal()">+ New Trade</button>
  </div>

  <!-- Stats bar -->
  <div class="tj-stats" id="tj-stats">
    <div class="tj-stat"><div class="tj-stat-num b">0</div><div class="tj-stat-lbl">Total Trades</div></div>
    <div class="tj-stat"><div class="tj-stat-num b">0%</div><div class="tj-stat-lbl">Win Rate</div></div>
    <div class="tj-stat"><div class="tj-stat-num b">-</div><div class="tj-stat-lbl">Net P&amp;L</div></div>
    <div class="tj-stat"><div class="tj-stat-num g">0</div><div class="tj-stat-lbl">Wins</div></div>
    <div class="tj-stat"><div class="tj-stat-num r">0</div><div class="tj-stat-lbl">Losses</div></div>
  </div>

  <!-- Table -->
  <div class="tj-table-wrap">
    <table class="tj-table">
      <thead>
        <tr>
          <th>Date</th><th>Symbol</th><th>Type</th>
          <th>Entry</th><th>Exit</th><th>Qty</th>
          <th>P&amp;L</th><th>Status</th><th>Notes</th><th></th>
        </tr>
      </thead>
      <tbody id="tj-tbody"></tbody>
    </table>
    <div class="tj-empty" id="tj-empty">
      <div style="font-size:48px;opacity:.25">📈</div>
      <p style="font-size:16px;font-weight:700;color:var(--text)">No trades logged yet</p>
      <p style="font-size:13px;color:var(--muted);margin-top:4px">Click <strong>+ New Trade</strong> above to log your first trade</p>
      <button class="btn" style="margin-top:16px" onclick="openTradeModal()">+ Log First Trade</button>
    </div>
  </div>
</div>




<!-- -- ROUTINE PAGE ------------------------------- -->
<div id="page-routine" style="display:none;flex-direction:column;width:100%;min-height:calc(100vh - 60px);background:var(--bg)">

  <!-- Top progress bar -->
  <div class="rt-header">
    <div class="rt-header-left">
      <div class="rt-today-label" id="rt-today-label">Today · Friday, Mar 20</div>
      <div class="rt-progress-wrap">
        <div class="rt-progress-bar"><div class="rt-progress-fill" id="rt-progress-fill" style="width:0%"></div></div>
        <span class="rt-progress-pct" id="rt-progress-pct">0% done today</span>
      </div>
    </div>
    <div class="rt-header-right">
      <button class="btn-ghost" onclick="showRoutineView('manage')">⚙️ Manage Routines</button>
      <button class="btn" onclick="showRoutineView('today')" id="rt-back-btn" style="display:none">← Today's View</button>
    </div>
  </div>

  <!-- TODAY VIEW -->
  <div id="rt-today-view" style="padding:20px 28px">
    <div id="rt-checklist"></div>
  </div>

  <!-- MANAGE VIEW -->
  <div id="rt-manage-view" style="display:none;padding:20px 28px">
    <div class="rt-manage-toolbar">
      <div class="rt-manage-title">📋 Routine Templates</div>
      <button class="btn" onclick="openRoutineGroupModal()">+ New Routine</button>
    </div>
    <div id="rt-groups-list"></div>
  </div>

</div>

<!-- ── TASK & ACTION NOTES PAGE ───────────────────── -->
<div id="page-tasknotes" style="display:none;flex-direction:column;width:100%;min-height:calc(100vh - 60px);background:var(--bg)">

  <div class="tan-header">
    <span class="tan-title">✍️ Task &amp; Action Notes</span>
    <span style="font-size:12px;color:var(--muted)" id="tan-hdr-count">0 notes</span>
  </div>

  <!-- Quick-add bar -->
  <div class="tan-quick-bar">
    <textarea id="tan-quick-input" placeholder="Quick note… press Ctrl+Enter or click Add" rows="2"
      onkeydown="if((event.ctrlKey||event.metaKey)&&event.key==='Enter'){addTaskNote();event.preventDefault();}"></textarea>
    <select id="tan-quick-cat" class="tan-cat-sel" title="Category">
      <option value="personal">👤 Personal</option>
      <option value="official">💼 Official</option>
    </select>
    <button class="tan-add-btn" onclick="addTaskNote()">+ Add</button>
  </div>

  <!-- Filter / search bar -->
  <div class="tan-filters">
    <div class="tan-filters-row">
      <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)">Category</span>
      <button class="tan-filter-btn active" id="tan-fc-all"      onclick="tanSetCat('all',this)">All</button>
      <button class="tan-filter-btn"        id="tan-fc-personal" onclick="tanSetCat('personal',this)">👤 Personal</button>
      <button class="tan-filter-btn"        id="tan-fc-official" onclick="tanSetCat('official',this)">💼 Official</button>
      <div class="tan-filters-divider"></div>
      <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)">Status</span>
      <button class="tan-filter-btn active" id="tan-f-all"    onclick="tanSetFilter('all',this)">All</button>
      <button class="tan-filter-btn"        id="tan-f-open"   onclick="tanSetFilter('open',this)">Open</button>
      <button class="tan-filter-btn"        id="tan-f-done"   onclick="tanSetFilter('done',this)">Done</button>
      <div class="tan-filters-divider"></div>
      <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)">Priority</span>
      <button class="tan-filter-btn" id="tan-f-high"   onclick="tanSetFilter('high',this)">🔴 High</button>
      <button class="tan-filter-btn" id="tan-f-medium" onclick="tanSetFilter('medium',this)">🟡 Medium</button>
      <button class="tan-filter-btn" id="tan-f-low"    onclick="tanSetFilter('low',this)">🟢 Low</button>
      <input class="tan-search" id="tan-search" placeholder="Search notes…" oninput="renderTaskNotes()">
      <select class="tan-sort-sel" id="tan-sort" onchange="renderTaskNotes()">
        <option value="date-desc">📅 Newest first</option>
        <option value="date-asc">📅 Oldest first</option>
        <option value="priority">🔴 By Priority</option>
        <option value="category">💼 By Category</option>
        <option value="status">✅ By Status</option>
      </select>
    </div>
  </div>

  <!-- Notes list -->
  <div class="tan-list" id="tan-list"></div>

</div>

<!-- ── FINANCE TRACKER PAGE ───────────────────────── -->
<div id="page-finance" style="display:none;flex-direction:column;width:100%;min-height:calc(100vh - 60px);background:var(--bg)">

  <div class="fin-header">
    <span class="fin-title">💰 Finance Tracker</span>
    <div style="display:flex;align-items:center;gap:10px">
      <div class="view-toggle">
        <button class="vtbtn active" id="fin-vcard" onclick="finSetView('card')" title="Card view">⊞</button>
        <button class="vtbtn" id="fin-vlist" onclick="finSetView('list')" title="List view">☰</button>
      </div>
      <button class="btn" onclick="openFinModal()">+ New Entry</button>
    </div>
  </div>

  <!-- Summary cards -->
  <div class="fin-summary">
    <div class="fin-sum-card">
      <div class="fin-sum-label">They Owe Me</div>
      <div class="fin-sum-val gave" id="fin-sum-gave">₹0</div>
      <div class="fin-sum-sub" id="fin-sum-gave-sub">0 entries</div>
    </div>
    <div class="fin-sum-card">
      <div class="fin-sum-label">I Owe Them</div>
      <div class="fin-sum-val borrow" id="fin-sum-borrow">₹0</div>
      <div class="fin-sum-sub" id="fin-sum-borrow-sub">0 entries</div>
    </div>
    <div class="fin-sum-card">
      <div class="fin-sum-label">Net Balance</div>
      <div class="fin-sum-val" id="fin-sum-net">₹0</div>
      <div class="fin-sum-sub" id="fin-sum-net-sub">—</div>
    </div>
  </div>

  <!-- Per-person chips -->
  <div class="fin-people">
    <div class="fin-people-title">Per Person</div>
    <div class="fin-person-chips" id="fin-person-chips"></div>
  </div>

  <!-- Filters -->
  <div class="fin-filters">
    <button class="tan-filter-btn active" id="fin-f-all"      onclick="finSetFilter('all',this)">All</button>
    <button class="tan-filter-btn"        id="fin-f-gave"     onclick="finSetFilter('gave',this)">💚 I Gave</button>
    <button class="tan-filter-btn"        id="fin-f-borrowed" onclick="finSetFilter('borrowed',this)">❤️ I Borrowed</button>
    <div class="tan-filters-divider"></div>
    <button class="tan-filter-btn"        id="fin-f-pending"  onclick="finSetFilter('pending',this)">⏳ Pending</button>
    <button class="tan-filter-btn"        id="fin-f-partial"  onclick="finSetFilter('partial',this)">🔵 Partial</button>
    <button class="tan-filter-btn"        id="fin-f-overdue"  onclick="finSetFilter('overdue',this)">🔴 Overdue</button>
    <button class="tan-filter-btn"        id="fin-f-settled"  onclick="finSetFilter('settled',this)">✅ Settled</button>
    <div class="tan-filters-divider"></div>
    <!-- 5. Sort -->
    <select class="fin-sort-sel" id="fin-sort" onchange="renderFinance()">
      <option value="date-desc">📅 Newest</option>
      <option value="date-asc">📅 Oldest</option>
      <option value="amount-desc">₹ Highest</option>
      <option value="amount-asc">₹ Lowest</option>
      <option value="person">👤 Person</option>
      <option value="duedate">⏰ Due Date</option>
      <option value="status">🔵 Status</option>
    </select>
    <!-- 2. Group toggle -->
    <button class="tan-filter-btn" id="fin-group-toggle" onclick="finToggleGroup(this)">👥 Group by Person</button>
    <!-- 7. Timeline toggle -->
    <button class="tan-filter-btn" id="fin-tl-toggle" onclick="finToggleTimeline(this)">📅 Timeline</button>
    <input class="tan-search" id="fin-search" placeholder="Search person / note…" oninput="renderFinance()" style="margin-left:auto">
  </div>

  <!-- 7. Timeline panel -->
  <div class="fin-timeline-panel" id="fin-timeline-panel">
    <div class="fin-tl-title">Upcoming & Overdue Payments</div>
    <div id="fin-tl-rows"></div>
  </div>

  <!-- Entries -->
  <div class="fin-list fin-view-card" id="fin-list">
    <div class="fin-grid" id="fin-card-grid"></div>
    <div class="fin-listbox" id="fin-listbox"></div>
  </div>

  <!-- 3. Floating Add Button -->
  <button class="fin-fab" id="fin-fab" onclick="openFinModal()" title="New Entry">+</button>

</div>

<!-- ── FINANCE ENTRY MODAL ─────────────────────────── -->
<div class="overlay" id="fin-modal-overlay">
<div class="modal" style="max-width:520px">
  <div class="mhead">
    <h2 id="fin-modal-title">New Entry</h2>
    <button class="mclose" onclick="closeFinModal()">✕</button>
  </div>
  <input type="hidden" id="fin-edit-id">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div class="frow" style="grid-column:1/-1"><label>Type *</label>
      <select id="fin-type">
        <option value="gave">💚 I Gave (they owe me)</option>
        <option value="borrowed">❤️ I Borrowed (I owe them)</option>
      </select>
    </div>
    <div class="frow"><label>Person Name *</label><input id="fin-person" placeholder="e.g. Rahul, Priya"></div>
    <div class="frow"><label>Amount ₹ *</label><input id="fin-amount" type="number" step="0.01" placeholder="0.00"></div>
    <div class="frow"><label>Payment Method *</label>
      <select id="fin-paymethod">
        <option value="cash">💵 Liquid Cash</option>
        <option value="credit_card">💳 Credit Card</option>
        <option value="bank">🏦 Bank Transfer</option>
        <option value="upi">📱 UPI</option>
      </select>
    </div>
    <div class="frow"><label>Interest Rate % / yr</label>
      <input id="fin-interest" type="number" step="0.01" placeholder="0 = no interest">
    </div>
    <div class="frow"><label>Date *</label><input id="fin-date" type="date"></div>
    <div class="frow"><label>Due Date (optional)</label><input id="fin-duedate" type="date"></div>
  </div>
  <div class="frow"><label>Notes / Reason</label>
    <textarea id="fin-notes" placeholder="e.g. For groceries, Wedding gift, Office lunch…" style="min-height:70px"></textarea>
  </div>
  <div class="mfoot">
    <button class="btn-ghost" onclick="closeFinModal()">Cancel</button>
    <button class="btn" onclick="saveFinEntry()">💾 Save Entry</button>
  </div>
</div>
</div>

<div class="overlay" id="rt-group-modal">
<div class="modal" style="max-width:480px">
  <div class="mhead">
    <h2 id="rt-group-modal-title">New Routine</h2>
    <button class="mclose" onclick="closeRoutineGroupModal()">✕</button>
  </div>
  <input type="hidden" id="rt-group-edit-id">
  <div class="frow"><label>Routine Name *</label><input id="rt-group-name" placeholder="e.g. Morning Routine"></div>
  <div class="frow"><label>Icon</label>
    <div class="rt-icon-picker" id="rt-icon-picker">
      <span class="rt-icon-opt selected" onclick="selectIcon(this,'🌅')">🌅</span>
      <span class="rt-icon-opt" onclick="selectIcon(this,'📈')">📈</span>
      <span class="rt-icon-opt" onclick="selectIcon(this,'🌙')">🌙</span>
      <span class="rt-icon-opt" onclick="selectIcon(this,'💪')">💪</span>
      <span class="rt-icon-opt" onclick="selectIcon(this,'📚')">📚</span>
      <span class="rt-icon-opt" onclick="selectIcon(this,'🧘')">🧘</span>
      <span class="rt-icon-opt" onclick="selectIcon(this,'🏃')">🏃</span>
      <span class="rt-icon-opt" onclick="selectIcon(this,'🍎')">🍎</span>
      <span class="rt-icon-opt" onclick="selectIcon(this,'💼')">💼</span>
      <span class="rt-icon-opt" onclick="selectIcon(this,'🎯')">🎯</span>
    </div>
    <input type="hidden" id="rt-group-icon" value="🌅">
  </div>
  <div class="frow"><label>Color</label>
    <select id="rt-group-color">
      <option value="blue">🔵 Blue</option>
      <option value="green">🟢 Green</option>
      <option value="purple">🟣 Purple</option>
      <option value="yellow">🟡 Yellow</option>
      <option value="red">🔴 Red</option>
    </select>
  </div>
  <div class="mfoot">
    <button class="btn-ghost" onclick="closeRoutineGroupModal()">Cancel</button>
    <button class="btn" onclick="saveRoutineGroup()">Save Routine</button>
  </div>
</div>
</div>

<!-- -- ROUTINE TASK MODAL -------------------------- -->
<div class="overlay" id="rt-task-modal">
<div class="modal" style="max-width:460px">
  <div class="mhead">
    <h2 id="rt-task-modal-title">Add Task</h2>
    <button class="mclose" onclick="closeRoutineTaskModal()">✕</button>
  </div>
  <input type="hidden" id="rt-task-edit-id">
  <input type="hidden" id="rt-task-group-id">
  <div class="frow"><label>Task Name *</label><input id="rt-task-name" placeholder="e.g. Workout, Check market"></div>
  <div class="frow"><label>Time (optional)</label><input id="rt-task-time" type="time"></div>
  <div class="frow"><label>Frequency</label>
    <select id="rt-task-freq" onchange="toggleWeekdays()">
      <option value="daily">🔁 Daily</option>
      <option value="weekly">📅 Weekly (select days)</option>
    </select>
  </div>
  <div class="frow" id="rt-weekdays-row" style="display:none">
    <label>Days</label>
    <div class="rt-day-picker">
      <span class="rt-day-opt" data-day="Mon">Mon</span>
      <span class="rt-day-opt" data-day="Tue">Tue</span>
      <span class="rt-day-opt" data-day="Wed">Wed</span>
      <span class="rt-day-opt" data-day="Thu">Thu</span>
      <span class="rt-day-opt" data-day="Fri">Fri</span>
      <span class="rt-day-opt" data-day="Sat">Sat</span>
      <span class="rt-day-opt" data-day="Sun">Sun</span>
    </div>
  </div>
  <div class="mfoot">
    <button class="btn-ghost" onclick="closeRoutineTaskModal()">Cancel</button>
    <button class="btn" onclick="saveRoutineTask()">Save Task</button>
  </div>
</div>
</div>

<!-- -- TRADE MODAL -------------------------------- -->
<div class="overlay" id="trade-modal-overlay">
<div class="modal" style="max-width:580px;max-height:90vh;overflow-y:auto">
  <div class="mhead">
    <h2 id="trade-modal-heading">Log New Trade</h2>
    <button class="mclose" onclick="closeTradeModal()">✕</button>
  </div>
  <input type="hidden" id="trade-edit-id">

  <!-- Row 1: Symbol + Date + Instrument -->
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
    <div class="frow"><label>Symbol *</label><input id="tj-symbol" placeholder="e.g. NIFTY"></div>
    <div class="frow"><label>Date *</label><input id="tj-date" type="date"></div>
    <div class="frow"><label>Instrument *</label>
      <select id="tj-instrument" onchange="onInstrumentChange()">
        <option value="equity">📊 Equity</option>
        <option value="futures">📉 Futures</option>
        <option value="options">🎯 Options</option>
      </select>
    </div>
  </div>

  <!-- ── EQUITY / FUTURES SECTION ── -->
  <div id="tj-eq-section">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="frow"><label>Type *</label>
        <select id="tj-type">
          <option value="BUY">📈 BUY (Long)</option>
          <option value="SELL">📉 SELL (Short)</option>
        </select>
      </div>
      <div class="frow"><label>Quantity</label><input id="tj-qty" type="number" placeholder="e.g. 50"></div>
      <div class="frow"><label>Entry Price *</label><input id="tj-entry" type="number" step="0.01" placeholder="₹0.00"></div>
      <div class="frow"><label>Exit Price</label><input id="tj-exit" type="number" step="0.01" placeholder="₹0.00"></div>
      <div class="frow"><label>Stop Loss</label><input id="tj-sl" type="number" step="0.01" placeholder="₹0.00"></div>
      <div class="frow"><label>Target</label><input id="tj-target" type="number" step="0.01" placeholder="₹0.00"></div>
    </div>
  </div>

  <!-- ── OPTIONS MULTI-LEG SECTION ── -->
  <div id="tj-opt-section" style="display:none">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
      <span style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)">Option Legs</span>
      <button class="btn" style="padding:5px 12px;font-size:12px" onclick="addLeg()">+ Add Leg</button>
    </div>
    <div id="tj-legs-container"></div>
    <!-- Multi-leg P&L breakdown -->
    <div id="tj-legs-pnl" style="display:none;margin-top:8px;background:#f8faff;border:1px solid #dde4f5;border-radius:10px;padding:12px 14px">
      <div id="tj-legs-pnl-rows"></div>
      <div style="border-top:1px solid #dde4f5;margin-top:8px;padding-top:8px;display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:13px;font-weight:700;color:#374151">Combined P&amp;L</span>
        <span id="tj-legs-total" style="font-size:15px;font-weight:700"></span>
      </div>
    </div>
  </div>

  <!-- Status -->
  <div class="frow" style="margin-top:4px"><label>Status</label>
    <select id="tj-status">
      <option value="open">⏳ Open</option>
      <option value="win">✅ Win</option>
      <option value="loss">❌ Loss</option>
    </select>
  </div>

  <div class="frow"><label>Notes / Reasoning</label>
    <textarea id="tj-notes" placeholder="Why did you take this trade? What did you learn?" style="min-height:80px"></textarea>
  </div>

  <!-- Equity/Futures single-leg P&L preview -->
  <div class="tj-pnl-preview" id="tj-pnl-preview" style="display:none">
    <span>Estimated P&amp;L:</span>
    <span id="tj-pnl-val" style="font-weight:700;font-size:15px"></span>
  </div>

  <div class="mfoot">
    <button class="btn-ghost" onclick="closeTradeModal()">Cancel</button>
    <button class="btn" onclick="saveTrade()">💾 Save Trade</button>
  </div>
</div>
</div>

<!-- -- ADD/EDIT MODAL ---------------------------- -->
<div class="overlay" id="modal-overlay">
<div class="modal with-preview" id="main-modal">
  <!-- LEFT: Form column -->
  <div class="modal-form-col">
    <div class="mhead">
      <h2 id="modal-heading">Add New</h2>
      <button class="mclose" onclick="closeModal()">✕</button>
    </div>

    <!-- 2. Visual tab toggle -->
    <div class="type-tog">
      <button class="tt active" id="tt-note" onclick="switchType('note')">📝 Note</button>
      <button class="tt" id="tt-reminder" onclick="switchType('reminder')">⏰ Reminder</button>
    </div>

    <!-- Purpose description -->
    <div id="type-desc-note" class="type-desc">
      <span class="type-desc-icon">📝</span>
      <div>
        <strong>Note</strong> - Write something down to remember later.<br>
        <span>No due date. Just stored and visible on your dashboard.</span>
      </div>
    </div>
    <div id="type-desc-reminder" class="type-desc" style="display:none">
      <span class="type-desc-icon">⏰</span>
      <div>
        <strong>Reminder</strong> - Something you need to act on by a specific time.<br>
        <span>You'll receive an <strong>email alert</strong> when it's due.</span>
      </div>
    </div>

    <input type="hidden" id="edit-id">

    <!-- Shared fields -->
    <div class="frow"><label>Title *</label><input id="f-title" placeholder="Enter a title..." oninput="scheduleAutosave();updatePreview()"></div>
    <!-- 5. Taller description box -->
    <div class="frow"><label>Description</label><textarea id="f-body" placeholder="Add details..." style="min-height:140px" oninput="scheduleAutosave();updatePreview()"></textarea></div>

    <!-- Tag chip input -->
    <div class="frow" style="position:relative">
      <label>Tags</label>
      <input type="hidden" id="f-tags">
      <div class="tag-chip-wrap" id="tag-chip-wrap" onclick="document.getElementById('tag-chip-input').focus()">
        <span id="tag-chips-display"></span>
        <input class="tag-chip-input" id="tag-chip-input" placeholder="Type a tag, press Enter…"
          onkeydown="handleTagKey(event)" oninput="showTagSuggestions(this.value)">
      </div>
      <div class="tag-suggestions" id="tag-suggestions"></div>
    </div>

    <!-- Category (shared for notes & reminders) -->
    <div class="frow"><label>Category</label>
      <select id="f-category">
        <option value="personal">👤 Personal</option>
        <option value="official">💼 Official</option>
      </select>
    </div>

    <!-- Note-only fields -->
    <div id="row-color" class="frow">
      <label>Card Colour</label>
      <input type="hidden" id="f-color" value="default">
      <div class="color-swatches" id="color-swatches">
        <div class="cswatch cswatch-default selected" data-color="default" onclick="selectSwatch(this)" title="Default"></div>
        <div class="cswatch" data-color="blue"   onclick="selectSwatch(this)" style="background:#60a5fa" title="Blue"></div>
        <div class="cswatch" data-color="green"  onclick="selectSwatch(this)" style="background:#4ade80" title="Green"></div>
        <div class="cswatch" data-color="yellow" onclick="selectSwatch(this)" style="background:#fbbf24" title="Yellow"></div>
        <div class="cswatch" data-color="red"    onclick="selectSwatch(this)" style="background:#f87171" title="Red"></div>
        <div class="cswatch" data-color="purple" onclick="selectSwatch(this)" style="background:#c084fc" title="Purple"></div>
      </div>
    </div>

    <!-- 7. Pin toggle (note only) -->
    <div id="row-pin" class="frow" style="display:flex;align-items:center;gap:10px;margin-bottom:13px">
      <label style="margin:0;flex:1">Pin to top of dashboard</label>
      <button type="button" class="pin-btn" id="pin-btn" onclick="togglePin()">📌 Pin</button>
      <input type="hidden" id="f-pinned" value="false">
    </div>

    <!-- Reminder-only fields -->
    <div id="row-due" class="frow" style="display:none">
      <label>📅 Due Date & Time *</label>
      <div style="display:grid;grid-template-columns:1fr auto auto;gap:8px;align-items:center">
        <input id="f-due-date" type="date" style="width:100%">
        <select id="f-due-hour" style="padding:9px 8px;background:var(--bg);border:1px solid var(--border2);border-radius:8px;color:var(--text);font-family:'Inter',sans-serif;font-size:13px;outline:none;cursor:pointer">
          HOUR_OPTIONS_PLACEHOLDER
        </select>
        <select id="f-due-min" style="padding:9px 8px;background:var(--bg);border:1px solid var(--border2);border-radius:8px;color:var(--text);font-family:'Inter',sans-serif;font-size:13px;outline:none;cursor:pointer">
          MIN_OPTIONS_PLACEHOLDER
        </select>
      </div>
      <div style="font-size:11px;color:var(--muted);margin-top:4px">Format: Date · Hour (00-23) · Minute (00-59)</div>
    </div>
    <div id="row-repeat" class="frow" style="display:none">
      <label>🔁 Repeat</label>
      <select id="f-repeat">
        <option value="none">No repeat</option>
        <option value="daily">Daily</option>
        <option value="weekly">Weekly</option>
      </select>
    </div>

    <div class="mfoot">
      <span class="autosave-lbl" id="autosave-lbl">✓ Saved</span>
      <button class="btn-ghost" onclick="closeModal()">Cancel</button>
      <button class="btn" onclick="saveItem()" id="modal-save-btn">💾 Save Note</button>
    </div>
  </div>

  <!-- RIGHT: 6. Live preview panel (note only) -->
  <div class="modal-preview-col" id="modal-preview-col">
    <div class="modal-preview-label">✨ Live Preview</div>
    <div class="preview-card" id="preview-card">
      <div class="preview-eyebrow">📝 Note</div>
      <div class="preview-title" id="preview-title" style="color:var(--muted);font-style:italic;font-weight:400">Your title will appear here…</div>
      <div class="preview-body" id="preview-body" style="color:var(--muted);font-style:italic"></div>
      <div class="preview-tags" id="preview-tags"></div>
      <div class="preview-meta">
        <span class="preview-date" id="preview-date"></span>
        <span id="preview-pin-badge"></span>
      </div>
    </div>
    <!-- 8. timestamps info -->
    <div id="preview-timestamps" style="font-size:11px;color:var(--muted);line-height:1.8;margin-top:4px"></div>
  </div>
</div>
</div>

<!-- -- SETTINGS PANEL ---------------------------- -->
<div id="settings-panel">
<div class="settings-modal">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:22px">
    <h2 style="margin:0">⚙️ Settings</h2>
    <button class="mclose" onclick="closeSettings()">✕</button>
  </div>

  <!-- THEME -->
  <div class="settings-section-title">🎨 Theme</div>
  <div class="theme-grid">

    <!-- Warm Parchment -->
    <div class="theme-card selected" id="theme-btn-cream" onclick="applyTheme('cream')">
      <div class="theme-preview">
        <div class="tp-side" style="background:#e8dcc8;border-right:1px solid #c8b48a"></div>
        <div class="tp-main" style="background:#faf6ef">
          <div class="tp-line" style="background:#8b5e2a;width:60%"></div>
          <div class="tp-line" style="background:#c8b48a;width:90%"></div>
          <div class="tp-line" style="background:#c8b48a;width:70%"></div>
        </div>
      </div>
      <div class="theme-name">🪵 Warm Parchment</div>
    </div>

    <!-- Soft Beige -->
    <div class="theme-card" id="theme-btn-beige" onclick="applyTheme('beige')">
      <div class="theme-preview">
        <div class="tp-side" style="background:#ede6d8;border-right:1px solid #d4c8b0"></div>
        <div class="tp-main" style="background:#f5f0e8">
          <div class="tp-line" style="background:#7c5cbf;width:60%"></div>
          <div class="tp-line" style="background:#d4c8b0;width:90%"></div>
          <div class="tp-line" style="background:#b8a888;width:70%"></div>
        </div>
      </div>
      <div class="theme-name">🌸 Soft Beige</div>
    </div>

    <!-- Neon Edge -->
    <div class="theme-card" id="theme-btn-neon" onclick="applyTheme('neon')">
      <div class="theme-preview" style="background:#080c14">
        <div class="tp-side" style="background:#0c1020;border-right:1px solid rgba(0,229,255,.2)"></div>
        <div class="tp-main" style="background:#080c14">
          <div class="tp-line" style="background:#00e5ff;width:60%;box-shadow:0 0 6px #00e5ff"></div>
          <div class="tp-line" style="background:rgba(0,229,255,.2);width:90%"></div>
          <div class="tp-line" style="background:rgba(191,0,255,.4);width:70%"></div>
        </div>
      </div>
      <div class="theme-name" style="background:#0c1020;color:#00e5ff">⚡ Neon Edge</div>
    </div>

  </div>

  <!-- GITHUB -->
  <div class="settings-section-title" style="margin-top:24px">🔗 GitHub Connection</div>
  <p style="font-size:12px;color:var(--muted);margin-bottom:14px;line-height:1.6">
    Notes are saved to <code style="background:var(--s2);padding:1px 5px;border-radius:4px">notes.json</code> in your repo via the GitHub API.
    Token needs <strong>repo</strong> scope →
    <a href="https://github.com/settings/tokens/new" target="_blank" style="color:var(--accent)">Create one ↗</a>
  </p>
  <div class="gh-fields">
    <div class="frow"><label>GitHub Username</label><input id="cfg-user" placeholder="e.g. krishnateja08"></div>
    <div class="frow"><label>Repository Name</label><input id="cfg-repo" placeholder="e.g. MyNotes"></div>
  </div>
  <div class="frow"><label>Personal Access Token</label><input id="cfg-token" type="password" placeholder="ghp_..."></div>

  <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:18px;padding-top:14px;border-top:1px solid var(--border)">
    <button class="btn-ghost" onclick="closeSettings()">Close</button>
    <button class="btn" onclick="saveConfig()">Save & Connect</button>
  </div>
</div>
</div>

<div id="toast"></div>

<script>
let DATA={notes:[],reminders:[]};
let fileSHA=null;
let currentType='note';

/* -- THEME --------------------------------------- */
const THEMES=['cream','beige','neon'];

function applyTheme(t){
  document.body.className='theme-'+t;
  localStorage.setItem('mynotes_theme',t);
  THEMES.forEach(k=>{
    const el=document.getElementById('theme-btn-'+k);
    if(el) el.classList.toggle('selected',k===t);
  });
}

/* -- CONFIG -------------------------------------- */
const getConfig=()=>({
  user: localStorage.getItem('gh_user')||'',
  repo: localStorage.getItem('gh_repo')||'',
  token:localStorage.getItem('gh_token')||''
});

function openSettings(){
  const c=getConfig();
  document.getElementById('cfg-user').value=c.user;
  document.getElementById('cfg-repo').value=c.repo;
  document.getElementById('cfg-token').value=c.token;
  document.getElementById('settings-panel').classList.add('open');
}
function closeSettings(){document.getElementById('settings-panel').classList.remove('open')}

function saveConfig(){
  const u=document.getElementById('cfg-user').value.trim();
  const r=document.getElementById('cfg-repo').value.trim();
  const t=document.getElementById('cfg-token').value.trim();
  if(!u||!r||!t){toast('Fill all fields','error');return;}
  localStorage.setItem('gh_user',u);
  localStorage.setItem('gh_repo',r);
  localStorage.setItem('gh_token',t);
  closeSettings();
  loadFromGitHub();
}

/* -- GITHUB API ---------------------------------- */
const apiUrl=()=>{const c=getConfig();return`https://api.github.com/repos/${c.user}/${c.repo}/contents/notes.json`};

async function loadFromGitHub(){
  const c=getConfig();
  if(!c.token){openSettings();return;}
  setSyncing(true,'Loading...');
  try{
    const res=await fetch(apiUrl(),{headers:{Authorization:`token ${c.token}`,Accept:'application/vnd.github.v3+json'}});
    if(!res.ok)throw new Error(`${res.status} ${res.statusText}`);
    const j=await res.json();
    fileSHA=j.sha;
    DATA=JSON.parse(atob(j.content.replace(/\n/g,'')));
    if(!DATA.trades)        DATA.trades        = [];
    if(!DATA.routines)      DATA.routines      = [];
    if(!DATA.routine_logs)  DATA.routine_logs  = [];
    if(!DATA.tasknotes)     DATA.tasknotes     = [];
    if(!DATA.finance)       DATA.finance       = [];
    TRADES        = DATA.trades;
    ROUTINES      = DATA.routines;
    ROUTINE_LOGS  = DATA.routine_logs;
    TASKNOTES     = DATA.tasknotes;
    FINANCE       = DATA.finance;
    renderAll();
    updateJournalCount();
    updateRoutineCount();
    renderTaskNotes();
    renderFinance();
    toast('Loaded ✓','success');
  }catch(e){toast('Load failed: '+e.message,'error');}
  setSyncing(false,'Synced');
}

async function saveToGitHub(){
  const c=getConfig();
  if(!c.token){toast('Set up GitHub first','error');openSettings();return false;}
  setSyncing(true,'Saving...');
  try{
    // Always refresh SHA before saving to avoid stale conflicts
    await refreshSHA();
    const res = await fetch(apiUrl(),{
      method:'PUT',
      headers:{Authorization:`token ${c.token}`,Accept:'application/vnd.github.v3+json','Content-Type':'application/json'},
      body:JSON.stringify({
        message:`notes: update ${new Date().toISOString().slice(0,16)}`,
        content: btoa(unescape(encodeURIComponent(JSON.stringify(DATA,null,2)))),
        sha: fileSHA
      })
    });
    if(!res.ok){
      const e=await res.json();
      // SHA mismatch - fetch fresh SHA and retry once more
      if(res.status===409||res.status===422||e.message?.includes('does not match')){
        setSyncing(true,'Resolving conflict...');
        await refreshSHA();
        const res2 = await fetch(apiUrl(),{
          method:'PUT',
          headers:{Authorization:`token ${c.token}`,Accept:'application/vnd.github.v3+json','Content-Type':'application/json'},
          body:JSON.stringify({
            message:`notes: update ${new Date().toISOString().slice(0,16)}`,
            content: btoa(unescape(encodeURIComponent(JSON.stringify(DATA,null,2)))),
            sha: fileSHA
          })
        });
        if(!res2.ok){
          const e2=await res2.json();
          throw new Error(e2.message||'Save failed - please refresh and try again');
        }
        const j2=await res2.json();
        fileSHA=j2.content.sha;
        toast('Saved ✓','success');
        setSyncing(false,'Synced');
        return true;
      }
      throw new Error(e.message||res.statusText);
    }
    const j=await res.json();
    fileSHA=j.content.sha;
    toast('Saved ✓','success');
    setSyncing(false,'Synced');
    return true;
  }catch(e){
    toast('Save failed: '+e.message,'error');
    setSyncing(false,'Error');
    return false;
  }
}

async function refreshSHA(){
  const c=getConfig();
  try{
    const res=await fetch(apiUrl(),{
      headers:{Authorization:`token ${c.token}`,Accept:'application/vnd.github.v3+json'}
    });
    if(res.ok){
      const j=await res.json();
      fileSHA=j.sha;
      // Also merge remote data to avoid stale conflicts
      const remote=JSON.parse(atob(j.content.replace(/\n/g,'')));
      // Keep our current unsaved changes on top of remote base
      DATA.notes        = DATA.notes        || remote.notes        || [];
      DATA.reminders    = DATA.reminders    || remote.reminders    || [];
      DATA.trades       = DATA.trades       || remote.trades       || [];
      DATA.routines     = DATA.routines     || remote.routines     || [];
      DATA.routine_logs = DATA.routine_logs || remote.routine_logs || [];
      DATA.tasknotes    = DATA.tasknotes    || remote.tasknotes    || [];
      DATA.finance      = DATA.finance      || remote.finance      || [];
    }
  }catch(e){ console.warn('refreshSHA failed',e); }
}

function setSyncing(on,label){
  document.getElementById('sdot').className='sdot'+(on?' syncing':'');
  document.getElementById('stext').textContent=label||'Synced';
}

/* -- VIEW TOGGLE --------------------------------- */
const viewState={rem:'card',notes:'card'};

function setView(section, mode){
  viewState[section]=mode;
  localStorage.setItem('view_'+section, mode);
  const sec=document.getElementById(section+'-section');
  sec.classList.toggle('is-list', mode==='list');
  document.getElementById(section+'-vcard').classList.toggle('active', mode==='card');
  document.getElementById(section+'-vlist').classList.toggle('active', mode==='list');
}

/* -- RENDER -------------------------------------- */
function renderAll(){
  const notes=DATA.notes||[];
  const reminders=DATA.reminders||[];
  TRADES       = DATA.trades       || [];
  ROUTINES     = DATA.routines     || [];
  ROUTINE_LOGS = DATA.routine_logs || [];
  TASKNOTES    = DATA.tasknotes    || [];
  FINANCE      = DATA.finance      || [];
  updateJournalCount();
  updateRoutineCount();
  updateTaskNotesCount();
  updateFinanceCount();
  const now=new Date();
  const pending=reminders.filter(r=>!r.sent).length;
  const overdue=reminders.filter(r=>{try{return!r.sent&&new Date(r.due.replace(' ','T'))<now;}catch{return false;}}).length;
  const sent=reminders.filter(r=>r.sent).length;

  document.getElementById('stat-notes').textContent=notes.length;
  document.getElementById('stat-reminders').textContent=reminders.length;
  document.getElementById('stat-pending').textContent=pending;
  document.getElementById('stat-files').textContent=sent;
  document.getElementById('nav-all').textContent=notes.length+reminders.length;
  document.getElementById('nav-notes').textContent=notes.length;
  document.getElementById('nav-reminders').textContent=reminders.length;
  document.getElementById('nav-pending').textContent=pending;
  document.getElementById('nav-overdue').textContent=overdue;
  document.getElementById('nav-sent').textContent=sent;
  document.getElementById('rem-pill').textContent=reminders.length;
  document.getElementById('notes-pill').textContent=notes.length;
  updateJournalCount();

  const ng=document.getElementById('notes-grid');
  const rg=document.getElementById('reminders-grid');
  const nl=document.getElementById('notes-list');
  const rl=document.getElementById('reminders-list');

  const emptyNote=`<div class="empty-state"><div class="ei">📝</div><p>No notes yet</p></div>`;
  const emptyRem=`<div class="empty-state"><div class="ei">⏰</div><p>No reminders yet</p></div>`;

  const sortedNotes=[...notes].reverse().sort((a,b)=>(b.pinned?1:0)-(a.pinned?1:0));
  const sortedRems=[...reminders].reverse();

  // apply category filters
  const filteredNotes = _notesCatFilter==='all' ? sortedNotes
    : sortedNotes.filter(n=>(n.category||'personal')===_notesCatFilter);
  const filteredRems  = _remCatFilter==='all'   ? sortedRems
    : sortedRems.filter(r=>(r.category||'personal')===_remCatFilter);

  ng.innerHTML=filteredNotes.length?filteredNotes.map(renderNoteCard).join(''):emptyNote;
  rg.innerHTML=filteredRems.length ?filteredRems.map(renderReminderCard).join(''):emptyRem;
  nl.innerHTML=filteredNotes.length?filteredNotes.map(renderNoteRow).join(''):emptyNote;
  rl.innerHTML=filteredRems.length ?filteredRems.map(renderReminderRow).join(''):emptyRem;
}

const esc=s=>String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const fd=s=>s?String(s).slice(0,10):'';

/* -- CARD RENDERERS ------------------------------ */
function renderNoteCard(n){
  const tags=(n.tags||[]).map(t=>`<span class="ctag">#${esc(t)}</span>`).join('');
  const cl=n.color&&n.color!=='default'?` cl-${n.color}`:'';
  const pinCls=n.pinned?' pinned-card':'';
  const pinBadge=n.pinned?'<span class="pinned-badge">📌 Pinned</span>':'';
  const updatedLine=n.updated&&n.updated!==n.created
    ?`<span class="cdate" style="margin-left:8px;opacity:.7">✏️ ${fd(n.updated)}</span>`:'';
  return`<div class="ncard${cl}${pinCls}" data-type="note" data-id="${n.id}" onclick="handleCardClick(event,'${n.id}')">
    <div class="ceyebrow"><span class="ctype">📝 Note</span>${pinBadge}</div>
    <div class="ctitle">${esc(n.title)}</div>
    ${n.body?`<div class="cbody" style="font-family:'EB Garamond',serif">${esc(n.body)}</div>`:''}
    ${tags?`<div class="tags-row">${tags}</div>`:''}
    <div class="cmeta">
      <span style="display:flex;align-items:center;gap:4px">
        <span class="cdate">Created ${fd(n.created)}</span>${updatedLine}
      </span>
      <div class="cbtns">
        <button class="cbtn" onclick="event.stopPropagation();editItem('${n.id}')">Edit</button>
        <button class="cbtn del" onclick="event.stopPropagation();deleteItem('${n.id}')">Delete</button>
      </div>
    </div>
  </div>`;
}

function renderReminderCard(r){
  const now=new Date();
  let sc='pending',sl='🔔 Pending';
  try{const d=new Date(r.due.replace(' ','T'));if(r.sent){sc='sent';sl='✅ Done';}else if(d<now){sc='overdue';sl='🔴 Overdue';}}catch{}
  const tags=(r.tags||[]).map(t=>`<span class="ctag">#${esc(t)}</span>`).join('');
  const rep=r.repeat&&r.repeat!=='none'?`<span class="ctag">🔁 ${r.repeat}</span>`:'';
  const doneBtn = !r.sent
    ? `<button class="cbtn done-btn" onclick="event.stopPropagation();markReminderDone('${r.id}')">✅ Done</button>`
    : `<button class="cbtn" onclick="event.stopPropagation();markReminderDone('${r.id}')">↩ Reopen</button>`;
  return`<div class="ncard ${sc}" data-type="reminder" data-id="${r.id}" onclick="handleCardClick(event,'${r.id}')">
    <div class="ceyebrow"><span class="ctype">⏰ Reminder</span><span class="schip ${sc}">${sl}</span></div>
    <div class="ctitle">${esc(r.title)}</div>
    ${r.body?`<div class="cbody">${esc(r.body)}</div>`:''}
    <div class="due-row">📅 Due: <strong>${esc(r.due||'')}</strong></div>
    ${(tags||rep)?`<div class="tags-row">${tags}${rep}</div>`:''}
    <div class="cmeta">
      <span class="cdate">${fd(r.created)}</span>
      <div class="cbtns">
        ${doneBtn}
        <button class="cbtn" onclick="event.stopPropagation();editItem('${r.id}')">Edit</button>
        <button class="cbtn del" onclick="event.stopPropagation();deleteItem('${r.id}')">Delete</button>
      </div>
    </div>
  </div>`;
}

/* -- LIST RENDERERS ------------------------------ */
function renderNoteRow(n){
  const cl=n.color&&n.color!=='default'?` cl-${n.color}`:'';
  const tags=(n.tags||[]).slice(0,3).map(t=>`<span class="ctag">#${esc(t)}</span>`).join('');
  return`<div class="lrow" data-type="note" data-id="${n.id}" onclick="handleCardClick(event,'${n.id}')">
    <div class="lrow-accent${cl}"></div>
    <div class="lrow-icon">📝</div>
    <div class="lrow-main">
      <div class="lrow-title">${esc(n.title)}</div>
      ${n.body?`<div class="lrow-sub">${esc(n.body)}</div>`:''}
    </div>
    ${tags?`<div class="lrow-tags">${tags}</div>`:''}
    <div class="lrow-date">${fd(n.created)}</div>
    <div class="lrow-btns">
      <button class="cbtn" onclick="event.stopPropagation();editItem('${n.id}')">Edit</button>
      <button class="cbtn del" onclick="event.stopPropagation();deleteItem('${n.id}')">Delete</button>
    </div>
  </div>`;
}

function renderReminderRow(r){
  const now=new Date();
  let sc='pending',sl='🔔';
  try{const d=new Date(r.due.replace(' ','T'));if(r.sent){sc='sent';sl='✅';}else if(d<now){sc='overdue';sl='🔴';}}catch{}
  const tags=(r.tags||[]).slice(0,2).map(t=>`<span class="ctag">#${esc(t)}</span>`).join('');
  const rep=r.repeat&&r.repeat!=='none'?`<span class="ctag">🔁 ${r.repeat}</span>`:'';
  const doneBtn = !r.sent
    ? `<button class="cbtn done-btn" onclick="event.stopPropagation();markReminderDone('${r.id}')">✅ Done</button>`
    : `<button class="cbtn" onclick="event.stopPropagation();markReminderDone('${r.id}')">↩ Reopen</button>`;
  return`<div class="lrow ${sc}" data-type="reminder" data-id="${r.id}" onclick="handleCardClick(event,'${r.id}')">
    <div class="lrow-accent${sc==='overdue'?' cl-red':sc==='sent'?' cl-green':''}"></div>
    <div class="lrow-icon">${sl}</div>
    <div class="lrow-main">
      <div class="lrow-title">${esc(r.title)}</div>
      ${r.body?`<div class="lrow-sub">${esc(r.body)}</div>`:''}
    </div>
    ${tags?`<div class="lrow-tags">${tags}${rep}</div>`:''}
    <div class="lrow-due">📅 ${esc(r.due||'')}</div>
    <div class="lrow-date">${fd(r.created)}</div>
    <div class="lrow-btns">
      ${doneBtn}
      <button class="cbtn" onclick="event.stopPropagation();editItem('${r.id}')">Edit</button>
      <button class="cbtn del" onclick="event.stopPropagation();deleteItem('${r.id}')">Delete</button>
    </div>
  </div>`;
}

/* click anywhere on card/row = edit, except delete button */
function handleCardClick(e, id){
  if(e.target.classList.contains('del')) return;
  editItem(id);
}

/* -- MARK REMINDER DONE -------------------------- */
async function markReminderDone(id){
  const rem = (DATA.reminders||[]).find(r=>r.id===id);
  if(!rem) return;
  rem.sent = !rem.sent;
  renderAll();
  await saveToGitHub();
  toast(rem.sent ? '✅ Marked as done!' : '↩ Reopened', 'success');
}

/* -- MODAL --------------------------------------- */
function openModal(type='note'){
  document.getElementById('modal-heading').textContent='Add New';
  document.getElementById('edit-id').value='';
  document.getElementById('f-title').value='';
  document.getElementById('f-body').value='';
  document.getElementById('f-due-date').value='';
  document.getElementById('f-due-hour').value='09';
  document.getElementById('f-due-min').value='00';
  document.getElementById('f-repeat').value='none';
  document.getElementById('f-pinned').value='false';
  document.getElementById('pin-btn').className='pin-btn';
  document.getElementById('pin-btn').textContent='📌 Pin';
  setTagChips([]);
  selectSwatchByValue('default');
  const catEl = document.getElementById('f-category');
  if(catEl) catEl.value = 'personal';
  const pts = document.getElementById('preview-timestamps');
  if(pts) pts.innerHTML='';
  switchType(type);
  document.getElementById('modal-overlay').classList.add('open');
  document.getElementById('autosave-lbl').classList.remove('show');
  updatePreview();
}
function closeModal(){document.getElementById('modal-overlay').classList.remove('open')}

/* ── NOTES / REMINDERS CATEGORY FILTER ── */
let _notesCatFilter = 'all';
let _remCatFilter   = 'all';

function setNotesCatFilter(cat, btn){
  _notesCatFilter = cat;
  document.querySelectorAll('[id^="notes-fc-"]').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  renderAll();
}
function setRemCatFilter(cat, btn){
  _remCatFilter = cat;
  document.querySelectorAll('[id^="rem-fc-"]').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  renderAll();
}

/* ── TAG CHIP SYSTEM ── */
let _tagChips = [];

function setTagChips(arr){
  _tagChips = [...arr];
  renderTagChips();
  document.getElementById('f-tags').value = _tagChips.join(', ');
}

function getTagChips(){ return [..._tagChips]; }

function renderTagChips(){
  const display = document.getElementById('tag-chips-display');
  if(!display) return;
  display.innerHTML = _tagChips.map((t,i)=>
    `<span class="tag-chip">#${esc(t)}<button class="tag-chip-x" onclick="removeTagChip(${i})">×</button></span>`
  ).join('');
}

function removeTagChip(i){
  _tagChips.splice(i,1);
  renderTagChips();
  document.getElementById('f-tags').value = _tagChips.join(', ');
}

function handleTagKey(e){
  const input = e.target;
  const val = input.value.trim().replace(/,/g,'');
  if((e.key==='Enter'||e.key===','||e.key===' ')&&val){
    e.preventDefault();
    if(!_tagChips.includes(val)) _tagChips.push(val);
    renderTagChips();
    document.getElementById('f-tags').value = _tagChips.join(', ');
    input.value='';
    hideTagSuggestions();
  } else if(e.key==='Backspace'&&!input.value&&_tagChips.length){
    _tagChips.pop();
    renderTagChips();
    document.getElementById('f-tags').value = _tagChips.join(', ');
  }
}

function showTagSuggestions(q){
  const box = document.getElementById('tag-suggestions');
  if(!box) return;
  const allTags = [...new Set([
    ...(DATA.notes||[]).flatMap(n=>n.tags||[]),
    ...(DATA.reminders||[]).flatMap(r=>r.tags||[])
  ])].filter(t=>t&&!_tagChips.includes(t)&&t.toLowerCase().includes(q.toLowerCase()));
  if(!q||!allTags.length){ box.classList.remove('open'); return; }
  box.innerHTML = allTags.slice(0,6).map(t=>
    `<div class="tag-sug-item" onclick="pickTagSuggestion('${esc(t)}')">🏷 ${esc(t)}</div>`
  ).join('');
  box.classList.add('open');
}

function hideTagSuggestions(){
  const box=document.getElementById('tag-suggestions');
  if(box) box.classList.remove('open');
}

function pickTagSuggestion(t){
  if(!_tagChips.includes(t)) _tagChips.push(t);
  renderTagChips();
  document.getElementById('f-tags').value = _tagChips.join(', ');
  document.getElementById('tag-chip-input').value='';
  hideTagSuggestions();
  updatePreview();
}

/* ── 6. LIVE PREVIEW ── */
function updatePreview(){
  const title  = document.getElementById('f-title')?.value||'';
  const body   = document.getElementById('f-body')?.value||'';
  const color  = document.getElementById('f-color')?.value||'default';
  const pinned = document.getElementById('f-pinned')?.value==='true';

  const pCard  = document.getElementById('preview-card');
  const pTitle = document.getElementById('preview-title');
  const pBody  = document.getElementById('preview-body');
  const pTags  = document.getElementById('preview-tags');
  const pDate  = document.getElementById('preview-date');
  const pPin   = document.getElementById('preview-pin-badge');

  if(!pCard) return;

  // update card colour class
  pCard.className = 'preview-card'+(color!=='default'?' cl-'+color:'');

  pTitle.textContent = title||'Your title will appear here…';
  pTitle.style.fontStyle = title?'normal':'italic';
  pTitle.style.fontWeight = title?'700':'400';
  pTitle.style.color = title?'':'var(--muted)';

  pBody.textContent = body;
  pBody.style.display = body?'':'none';

  const tagArr = getTagChips();
  pTags.innerHTML = tagArr.map(t=>`<span class="ctag">#${esc(t)}</span>`).join('');
  pTags.style.display = tagArr.length?'':'none';

  const now = new Date().toISOString().slice(0,10);
  pDate.textContent = 'Created '+now;
  pPin.innerHTML = pinned?'<span class="pinned-badge">📌 Pinned</span>':'';
}

/* ── 7. PIN ── */
function togglePin(){
  const hidden = document.getElementById('f-pinned');
  const btn    = document.getElementById('pin-btn');
  if(!hidden) return;
  const isPinned = hidden.value==='true';
  hidden.value = isPinned?'false':'true';
  btn.classList.toggle('pinned', !isPinned);
  btn.textContent = isPinned?'📌 Pin':'📌 Pinned';
  updatePreview();
}

/* ── COLOR SWATCHES ── */
function selectSwatch(el){
  document.querySelectorAll('.cswatch').forEach(s=>s.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById('f-color').value = el.dataset.color;
  updatePreview();
}

function selectSwatchByValue(val){
  document.querySelectorAll('.cswatch').forEach(s=>{
    s.classList.toggle('selected', s.dataset.color===val);
  });
  document.getElementById('f-color').value = val||'default';
  updatePreview();
}

/* ── AUTOSAVE DEBOUNCE ── */
let _autosaveTimer = null;
function scheduleAutosave(){
  clearTimeout(_autosaveTimer);
  _autosaveTimer = setTimeout(()=>{
    const title = document.getElementById('f-title').value.trim();
    if(!title) return;
    // silent background save only if editing existing item
    const id = document.getElementById('edit-id').value;
    if(!id) return;
    saveItem();
  }, 2000);
}

/* close suggestion box on outside click */
document.addEventListener('click', e=>{
  if(!e.target.closest('#tag-chip-wrap')&&!e.target.closest('#tag-suggestions')) hideTagSuggestions();
});

function switchType(t){
  currentType=t;
  document.getElementById('tt-note').classList.toggle('active',t==='note');
  document.getElementById('tt-reminder').classList.toggle('active',t==='reminder');
  document.getElementById('row-color').style.display     = t==='note'     ? '' : 'none';
  document.getElementById('row-pin').style.display       = t==='note'     ? 'flex' : 'none';
  document.getElementById('row-due').style.display       = t==='reminder' ? '' : 'none';
  document.getElementById('row-repeat').style.display    = t==='reminder' ? '' : 'none';
  document.getElementById('type-desc-note').style.display     = t==='note'     ? '' : 'none';
  document.getElementById('type-desc-reminder').style.display = t==='reminder' ? '' : 'none';
  document.getElementById('modal-save-btn').textContent  = t==='note' ? '💾 Save Note' : '⏰ Save Reminder';
  const previewCol = document.getElementById('modal-preview-col');
  const modal      = document.getElementById('main-modal');
  if(previewCol) previewCol.style.display = t==='note' ? '' : 'none';
  if(modal) modal.className = t==='note' ? 'modal with-preview' : 'modal';
}

function editItem(id){
  const item=[...(DATA.notes||[]),...(DATA.reminders||[])].find(i=>i.id===id);
  if(!item)return;
  document.getElementById('modal-heading').textContent='Edit';
  document.getElementById('edit-id').value=id;
  document.getElementById('f-title').value=item.title||'';
  document.getElementById('f-body').value=item.body||'';
  setTagChips(item.tags||[]);
  selectSwatchByValue(item.color||'default');
  // 7. pin
  const isPinned=item.pinned===true;
  document.getElementById('f-pinned').value=String(isPinned);
  const pb=document.getElementById('pin-btn');
  pb.className='pin-btn'+(isPinned?' pinned':'');
  pb.textContent=isPinned?'📌 Pinned':'📌 Pin';
  // 8. timestamps
  const pts=document.getElementById('preview-timestamps');
  if(pts){
    const lines=[];
    if(item.created) lines.push('📅 Created: '+item.created.slice(0,10));
    if(item.updated) lines.push('✏️ Updated: '+item.updated.slice(0,10));
    pts.innerHTML=lines.join('<br>');
  }
  if(item.due){
    const parts=item.due.split(' ');
    document.getElementById('f-due-date').value=parts[0]||'';
    if(parts[1]){
      const tp=parts[1].split(':');
      document.getElementById('f-due-hour').value=(tp[0]||'09').padStart(2,'0');
      document.getElementById('f-due-min').value=(tp[1]||'00').padStart(2,'0');
    }
  }
  document.getElementById('f-repeat').value=item.repeat||'none';
  const catEl2 = document.getElementById('f-category');
  if(catEl2) catEl2.value = item.category||'personal';
  switchType(item.type==='reminder'?'reminder':'note');
  document.getElementById('modal-overlay').classList.add('open');
  document.getElementById('autosave-lbl').classList.remove('show');
  updatePreview();
}

async function saveItem(){
  const title=document.getElementById('f-title').value.trim();
  if(!title){toast('Title is required','error');return;}
  const id=document.getElementById('edit-id').value;
  const tags=getTagChips();
  const color=document.getElementById('f-color').value||'default';
  const pinned=document.getElementById('f-pinned').value==='true';
  const now=new Date().toISOString().slice(0,16).replace('T',' ');
  const ex=id?[...(DATA.notes||[]),...(DATA.reminders||[])].find(i=>i.id===id):null;
  if(currentType==='note'){
    const note={id:id||uid(),type:'note',category:document.getElementById('f-category').value||'personal',title,body:document.getElementById('f-body').value.trim(),tags,color,pinned,created:ex?ex.created:now,updated:now,attachments:ex?ex.attachments||[]:[]};
    if(id)DATA.notes=DATA.notes.map(n=>n.id===id?note:n);else DATA.notes.push(note);
  }else{
    const dueDate=document.getElementById('f-due-date').value;
    const dueHour=document.getElementById('f-due-hour').value||'00';
    const dueMin=document.getElementById('f-due-min').value||'00';
    if(!dueDate){toast('Due date required','error');return;}
    const dueStr=dueDate+' '+dueHour+':'+dueMin;
    const rem={id:id||uid(),type:'reminder',category:document.getElementById('f-category').value||'personal',title,body:document.getElementById('f-body').value.trim(),tags,due:dueStr,repeat:document.getElementById('f-repeat').value,sent:ex?ex.sent||false:false,created:ex?ex.created:now,updated:now,attachments:ex?ex.attachments||[]:[]};
    if(id)DATA.reminders=DATA.reminders.map(r=>r.id===id?rem:r);else DATA.reminders.push(rem);
  }
  const lbl=document.getElementById('autosave-lbl');
  if(lbl){lbl.classList.add('show');setTimeout(()=>lbl.classList.remove('show'),2500);}
  closeModal();renderAll();
  await saveToGitHub();
  toast('Saved ✓','success');
}

async function deleteItem(id){
  if(!confirm('Delete this item?'))return;
  DATA.notes=(DATA.notes||[]).filter(n=>n.id!==id);
  DATA.reminders=(DATA.reminders||[]).filter(r=>r.id!==id);
  renderAll();
  await saveToGitHub();
}

const uid=()=>Math.random().toString(36).slice(2,10);

/* -- STAT CARD FILTER ---------------------------- */
function statFilter(type, btn){
  document.querySelectorAll('.stat-card').forEach(c=>c.classList.remove('active'));
  btn.classList.add('active');

  const remSec       = document.getElementById('rem-section');
  const notesSec     = document.getElementById('notes-section');
  const remHdr       = document.getElementById('rem-sec-header');
  const remCatFil    = document.getElementById('rem-cat-filter');
  const notesHdr     = document.getElementById('notes-sec-header');
  const notesCatFil  = document.getElementById('notes-cat-filter');

  const showRem   = (type==='all'||type==='reminder'||type==='pending');
  const showNotes = (type==='all'||type==='note');

  if(remSec)      remSec.style.display      = showRem   ? '' : 'none';
  if(remHdr)      remHdr.style.display      = showRem   ? '' : 'none';
  if(remCatFil)   remCatFil.style.display   = showRem   ? 'flex' : 'none';
  if(notesSec)    notesSec.style.display    = showNotes ? '' : 'none';
  if(notesHdr)    notesHdr.style.display    = showNotes ? '' : 'none';
  if(notesCatFil) notesCatFil.style.display = showNotes ? 'flex' : 'none';

  // pending = anything not sent (includes overdue)
  if(type==='pending'){
    document.querySelectorAll('[data-type="reminder"]').forEach(el=>{
      el.style.display = !el.classList.contains('sent') ? '' : 'none';
    });
  } else {
    document.querySelectorAll('[data-type="reminder"]').forEach(el=>{
      el.style.display = '';
    });
  }
}

/* -- FILTER/SEARCH ------------------------------- */
function filterCards(type, btn){
  // update nav highlight
  document.querySelectorAll('.nav-item').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');

  // reset stat card highlights
  document.querySelectorAll('.stat-card').forEach(c=>c.classList.remove('active'));

  const remSec      = document.getElementById('rem-section');
  const notesSec    = document.getElementById('notes-section');
  const remHdr      = document.getElementById('rem-sec-header');
  const remCatFil   = document.getElementById('rem-cat-filter');
  const notesHdr    = document.getElementById('notes-sec-header');
  const notesCatFil = document.getElementById('notes-cat-filter');

  function showRem(v){
    if(remSec)      remSec.style.display      = v ? '' : 'none';
    if(remHdr)      remHdr.style.display      = v ? '' : 'none';
    if(remCatFil)   remCatFil.style.display   = v ? 'flex' : 'none';
  }
  function showNotes(v){
    if(notesSec)    notesSec.style.display    = v ? '' : 'none';
    if(notesHdr)    notesHdr.style.display    = v ? '' : 'none';
    if(notesCatFil) notesCatFil.style.display = v ? 'flex' : 'none';
  }

  if(type==='all'){
    showRem(true); showNotes(true);
    document.querySelectorAll('.ncard,.lrow').forEach(c=>c.style.display='');
    return;
  }

  if(type==='note'){
    showRem(false); showNotes(true);
    document.querySelectorAll('.ncard,.lrow').forEach(c=>c.style.display='');
    return;
  }

  if(type==='reminder'){
    showRem(true); showNotes(false);
    document.querySelectorAll('.ncard,.lrow').forEach(c=>c.style.display='');
    return;
  }

  // pending / overdue / sent - show reminders section only, filter by class
  showRem(true); showNotes(false);

  document.querySelectorAll('[data-type="reminder"]').forEach(c=>{
    let show = false;
    if(type==='pending')       show = !c.classList.contains('sent'); // pending+overdue
    else if(type==='overdue')  show = c.classList.contains('overdue');
    else if(type==='sent')     show = c.classList.contains('sent');
    else show = c.classList.contains(type);
    c.style.display = show ? '' : 'none';
  });

  // show empty state if nothing visible
  const anyVisible = [...document.querySelectorAll('[data-type="reminder"]')]
    .some(c=>c.style.display!=='none');
  if(!anyVisible){
    // inject empty msg if not already there
    ['reminders-grid','reminders-list'].forEach(id=>{
      const el=document.getElementById(id);
      if(el && !el.querySelector('.filter-empty')){
        const d=document.createElement('div');
        d.className='empty-state filter-empty';
        d.innerHTML='<div class="ei">🔍</div><p>Nothing here</p>';
        el.appendChild(d);
      }
    });
  } else {
    document.querySelectorAll('.filter-empty').forEach(e=>e.remove());
  }
}

function searchCards(q){
  const lq=q.toLowerCase();
  document.querySelectorAll('.ncard,.lrow').forEach(c=>{
    c.style.display=c.innerText.toLowerCase().includes(lq)?'':'none';
  });
}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeModal();closeSettings();}});

/* -- TOAST --------------------------------------- */
function toast(msg,type='success'){
  const t=document.getElementById('toast');
  t.textContent=msg;t.className='show '+type;
  setTimeout(()=>{t.className='';},3000);
}

/* -- MOBILE SIDEBAR ------------------------------ */
function openSidebar(){
  document.querySelector('aside').classList.add('open');
  document.getElementById('sidebar-overlay').classList.add('open');
}
function closeSidebar(){
  document.querySelector('aside').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('open');
}
// close sidebar when any nav item clicked on mobile
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('.nav-item').forEach(btn=>{
    btn.addEventListener('click',()=>{
      if(window.innerWidth<=640) closeSidebar();
    });
  });
});

/* -- PAGE SWITCHER ------------------------------- */
function showPage(page, btn){
  const pages = ['dashboard','sticky','journal','routine','tasknotes','finance'];
  const displayMap = {dashboard:'',sticky:'flex',journal:'flex',routine:'flex',tasknotes:'flex',finance:'flex'};
  pages.forEach(p=>{
    const el=document.getElementById('page-'+p);
    if(el){
      const showing = p===page;
      el.style.display = showing ? (displayMap[p]||'') : 'none';
      if(showing){
        el.classList.remove('page-entering');
        void el.offsetWidth; // force reflow
        el.classList.add('page-entering');
      }
    }
  });

  // 6. Icons in title
  const titles = {
    dashboard:'📋 Dashboard',
    sticky:'📌 Sticky Notes',
    journal:'📈 Trading Journal',
    routine:'🔁 Routine',
    tasknotes:'✍️ Task Notes',
    finance:'💰 Finance Tracker'
  };
  document.getElementById('page-title').textContent = titles[page]||'📋 Dashboard';

  // 5. Context-aware actions
  ['dashboard','sticky','journal','routine','tasknotes','finance'].forEach(p=>{
    const el=document.getElementById('ctx-'+p);
    if(el) el.style.display=p===page?'flex':'none';
  });
  // legacy search-wrap compat
  const sw=document.getElementById('topbar-search-wrap');
  if(sw) sw.style.display='flex';

  document.querySelectorAll('.nav-item').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');

  if(page==='dashboard'){
    const remSec      = document.getElementById('rem-section');
    const notesSec    = document.getElementById('notes-section');
    const remHdr      = document.getElementById('rem-sec-header');
    const remCatFil   = document.getElementById('rem-cat-filter');
    const notesHdr    = document.getElementById('notes-sec-header');
    const notesCatFil = document.getElementById('notes-cat-filter');
    if(remSec)      remSec.style.display      = '';
    if(remHdr)      remHdr.style.display      = '';
    if(remCatFil)   remCatFil.style.display   = 'flex';
    if(notesSec)    notesSec.style.display    = '';
    if(notesHdr)    notesHdr.style.display    = '';
    if(notesCatFil) notesCatFil.style.display = 'flex';
    document.querySelectorAll('.ncard,.lrow').forEach(c=>c.style.display='');
    document.querySelectorAll('.filter-empty').forEach(e=>e.remove());
    document.querySelectorAll('.stat-card').forEach(c=>c.classList.remove('active'));
  }
  if(page==='journal') renderJournal();
  if(page==='routine') showRoutineView('today');
  if(page==='finance') renderFinance();
  else { const fab=document.getElementById('fin-fab'); if(fab) fab.classList.remove('visible'); }
}

/* -- STICKY NOTES PAGE --------------------------- */
const SP_COLORS = [
  {id:'yellow',  bg:'#fde68a', label:'Yellow'},
  {id:'orange',  bg:'#fb923c', label:'Orange'},
  {id:'pink',    bg:'#f472b6', label:'Pink'},
  {id:'green',   bg:'#86efac', label:'Green'},
  {id:'blue',    bg:'#60a5fa', label:'Blue'},
  {id:'purple',  bg:'#c084fc', label:'Purple'},
  {id:'red',     bg:'#f87171', label:'Red'},
  {id:'teal',    bg:'#2dd4bf', label:'Teal'},
  {id:'white',   bg:'#f8fafc', label:'White'},
  {id:'sky',     bg:'#38bdf8', label:'Sky'},
  {id:'lime',    bg:'#a3e635', label:'Lime'},
  {id:'amber',   bg:'#fbbf24', label:'Amber'},
];
let activeSPColor = 'yellow';
let STICKIES = [];
let ARCHIVED = [];
let _spFilter = 'all';

function initSticky(){
  const wrap = document.getElementById('sp-colors');
  wrap.innerHTML = SP_COLORS.map(c=>`
    <div class="sp-dot${c.id===activeSPColor?' active':''}"
      style="background:${c.bg}"
      title="${c.label}"
      onclick="pickSPColor('${c.id}')"
      id="spdot-${c.id}">
    </div>`).join('');
  // build color filter chips
  const cf = document.getElementById('sp-color-filters');
  if(cf) cf.innerHTML = SP_COLORS.map(c=>`
    <div class="sp-filter-chip" id="spf-${c.id}" onclick="spSetFilter('${c.id}',this)" style="gap:5px">
      <span class="sp-filter-dot" style="background:${c.bg}"></span>${c.label}
    </div>`).join('');
  try{
    STICKIES  = JSON.parse(localStorage.getItem('mynotes_stickies')||'[]');
    ARCHIVED  = JSON.parse(localStorage.getItem('mynotes_stickies_archive')||'[]');
  }catch{ STICKIES=[]; ARCHIVED=[]; }
  renderStickyBoard();
  renderArchiveGrid();
}

/* 1. color picker */
function pickSPColor(id){
  activeSPColor=id;
  document.querySelectorAll('.sp-dot').forEach(d=>d.classList.remove('active'));
  const el=document.getElementById('spdot-'+id);
  if(el) el.classList.add('active');
}

/* 2. filter */
function spSetFilter(f, btn){
  _spFilter=f;
  document.querySelectorAll('.sp-filter-chip').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  renderStickyBoard();
}

function addSticky(){
  const colorObj = SP_COLORS.find(c=>c.id===activeSPColor)||SP_COLORS[0];
  const now = new Date().toISOString().slice(0,16).replace('T',' ');
  const s = {
    id: Math.random().toString(36).slice(2,10),
    text: '',
    bg: colorObj.bg,
    colorId: colorObj.id,
    created: now,
    updated: now,
    pinned: false,
    tags: []
  };
  STICKIES.unshift(s);
  saveStickies();
  renderStickyBoard();
  setTimeout(()=>{
    const el=document.getElementById('stext-'+s.id);
    if(el){ el.focus(); placeCursorAtEnd(el); }
  }, 50);
}

/* 7. animated delete */
function deleteSticky(id){
  if(!confirm('Delete this sticky?')) return;
  const card = document.getElementById('scard-'+id);
  if(card){
    card.classList.add('removing');
    setTimeout(()=>{
      STICKIES=STICKIES.filter(s=>s.id!==id);
      saveStickies(); renderStickyBoard();
    }, 200);
  } else {
    STICKIES=STICKIES.filter(s=>s.id!==id);
    saveStickies(); renderStickyBoard();
  }
}

/* 6. archive */
function archiveSticky(id){
  const s = STICKIES.find(s=>s.id===id);
  if(!s) return;
  const card = document.getElementById('scard-'+id);
  if(card){ card.classList.add('removing'); }
  setTimeout(()=>{
    STICKIES = STICKIES.filter(x=>x.id!==id);
    ARCHIVED.unshift({...s, archivedAt: new Date().toISOString().slice(0,10)});
    saveStickies();
    renderStickyBoard();
    renderArchiveGrid();
  }, 200);
}

function restoreSticky(id){
  const s = ARCHIVED.find(a=>a.id===id);
  if(!s) return;
  ARCHIVED = ARCHIVED.filter(a=>a.id!==id);
  delete s.archivedAt;
  STICKIES.unshift(s);
  saveStickies();
  renderStickyBoard();
  renderArchiveGrid();
  toast('Sticky restored','success');
}

function toggleArchivePanel(){
  const panel = document.getElementById('sp-archive-panel');
  if(panel) panel.classList.toggle('open');
}

function renderArchiveGrid(){
  const grid = document.getElementById('sp-archive-grid');
  if(!grid) return;
  localStorage.setItem('mynotes_stickies_archive', JSON.stringify(ARCHIVED));
  if(!ARCHIVED.length){
    grid.innerHTML='<span style="font-size:12px;color:var(--muted)">No archived stickies</span>';
    return;
  }
  grid.innerHTML = ARCHIVED.map(s=>`
    <div style="background:${s.bg};border-radius:8px;padding:10px 12px;min-width:150px;max-width:200px;opacity:.75;position:relative">
      <div style="font-size:10px;color:rgba(0,0,0,.4);margin-bottom:4px">📦 Archived ${s.archivedAt||''}</div>
      <div style="font-size:12px;color:rgba(0,0,0,.75);line-height:1.4;max-height:60px;overflow:hidden">${escHtml(s.text||'(empty)')}</div>
      <div style="display:flex;gap:5px;margin-top:8px">
        <button onclick="restoreSticky('${s.id}')" style="font-size:10px;background:rgba(0,0,0,.12);border:none;border-radius:5px;padding:2px 8px;cursor:pointer;color:rgba(0,0,0,.6);font-weight:600">↩ Restore</button>
        <button onclick="permDeleteArchived('${s.id}')" style="font-size:10px;background:rgba(180,0,0,.12);border:none;border-radius:5px;padding:2px 8px;cursor:pointer;color:rgba(100,0,0,.7);font-weight:600">✕</button>
      </div>
    </div>`).join('');
}

function permDeleteArchived(id){
  if(!confirm('Permanently delete?')) return;
  ARCHIVED = ARCHIVED.filter(a=>a.id!==id);
  renderArchiveGrid();
}

function saveStickyText(id, el){
  const s=STICKIES.find(s=>s.id===id);
  if(s){
    s.text=el.innerText;
    s.updated=new Date().toISOString().slice(0,16).replace('T',' ');
    const dateEl=document.getElementById('sdate-'+id);
    if(dateEl) dateEl.innerHTML=stickyDateHtml(s);
    saveStickies();
  }
}

function saveStickyTag(id, input){
  const val=input.value.trim().replace(/,/g,'');
  if(!val) return;
  const s=STICKIES.find(s=>s.id===id);
  if(!s) return;
  s.tags=s.tags||[];
  if(!s.tags.includes(val)) s.tags.push(val);
  input.value='';
  saveStickies();
  renderStickyBoard();
}

function removeStickyTag(id, tag){
  const s=STICKIES.find(s=>s.id===id);
  if(s){ s.tags=(s.tags||[]).filter(t=>t!==tag); saveStickies(); renderStickyBoard(); }
}

function saveStickySize(id, card){
  const s=STICKIES.find(s=>s.id===id);
  if(!s) return;
  const w=card.style.width; const h=card.style.height;
  if(w) s.width=w; if(h) s.height=h;
  saveStickies();
}

function changeStickyColor(id, newColor, colorId){
  const s=STICKIES.find(s=>s.id===id);
  if(s){ s.bg=newColor; s.colorId=colorId||s.colorId; saveStickies(); renderStickyBoard(); }
}

/* 3. pin */
function toggleStickyPin(id){
  const s=STICKIES.find(s=>s.id===id);
  if(!s) return;
  s.pinned=!s.pinned;
  saveStickies(); renderStickyBoard();
}

function saveStickies(){
  localStorage.setItem('mynotes_stickies',JSON.stringify(STICKIES));
  const el=document.getElementById('nav-sticky-count');
  if(el) el.textContent=STICKIES.length;
  const cnt=document.getElementById('sp-count');
  if(cnt) cnt.textContent=STICKIES.length+' stick'+(STICKIES.length===1?'y':'ies');
}

function placeCursorAtEnd(el){
  const r=document.createRange(),s=window.getSelection();
  r.selectNodeContents(el);r.collapse(false);
  s.removeAllRanges();s.addRange(r);
}

function escHtml(s){
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

/* 5. timestamps helper */
function stickyDateHtml(s){
  let html=`<span>📅 ${s.created?s.created.slice(0,10):''}</span>`;
  if(s.updated&&s.updated!==s.created) html+=`<span style="margin-left:6px;opacity:.7">✏️ ${s.updated.slice(0,10)}</span>`;
  return html;
}

function renderStickyBoard(){
  const board=document.getElementById('sp-board');
  const empty=document.getElementById('sp-empty');
  if(!board) return;
  board.querySelectorAll('.sticky-card').forEach(el=>el.remove());

  // filter
  let visible = [...STICKIES];
  if(_spFilter==='pinned') visible=visible.filter(s=>s.pinned);
  else if(_spFilter!=='all') visible=visible.filter(s=>s.colorId===_spFilter);
  // 3. pinned first
  visible.sort((a,b)=>(b.pinned?1:0)-(a.pinned?1:0));

  if(!visible.length){
    if(empty) empty.style.display='flex';
    saveStickies();
    return;
  }
  if(empty) empty.style.display='none';
  saveStickies();

  visible.forEach(s=>{
    const card=document.createElement('div');
    card.className='sticky-card';
    card.style.background=s.bg;
    card.id='scard-'+s.id;
    card.style.width  = s.width  || '220px';
    card.style.height = s.height || '170px';

    const tagHtml=(s.tags||[]).map(t=>`
      <span class="sticky-tag">#${escHtml(t)}<span onclick="removeStickyTag('${s.id}','${escHtml(t)}')"
        style="margin-left:3px;cursor:pointer;opacity:.6">×</span></span>`).join('');

    card.innerHTML=`
      ${s.pinned?'<div class="sticky-pinned-badge">📌 PINNED</div>':''}
      <div class="sticky-card-header">
        <span class="sticky-card-date" id="sdate-${s.id}">${stickyDateHtml(s)}</span>
        <div style="display:flex;gap:4px">
          <button class="sticky-pin-btn${s.pinned?' pinned':''}" onclick="toggleStickyPin('${s.id}')" title="${s.pinned?'Unpin':'Pin to top'}">${s.pinned?'📌':'📌'}</button>
          <button class="sticky-archive-btn" onclick="archiveSticky('${s.id}')" title="Archive">🗂</button>
          <button class="sticky-card-del" onclick="deleteSticky('${s.id}')">✕</button>
        </div>
      </div>
      <div class="sticky-card-body"
        id="stext-${s.id}"
        contenteditable="true"
        onblur="saveStickyText('${s.id}',this)"
      >${escHtml(s.text)}</div>
      <div class="sticky-tags">${tagHtml}<input class="sticky-tag-input" placeholder="+ tag"
        onkeydown="if(event.key==='Enter'||event.key===','){saveStickyTag('${s.id}',this);event.preventDefault()}"
        onblur="if(this.value.trim())saveStickyTag('${s.id}',this)"></div>
      <div class="sticky-card-footer">
        <div style="display:flex;gap:4px;flex-wrap:wrap;align-items:center">
          ${SP_COLORS.map(c=>`<div onclick="changeStickyColor('${s.id}','${c.bg}','${c.id}')"
            title="${c.label}"
            style="width:13px;height:13px;border-radius:4px;background:${c.bg};cursor:pointer;
            border:2px solid ${s.bg===c.bg?'rgba(0,0,0,.55)':'transparent'};
            flex-shrink:0;transition:transform .12s"
            onmouseover="this.style.transform='scale(1.35)'"
            onmouseout="this.style.transform='scale(1)'">
          </div>`).join('')}
        </div>
      </div>
      <div class="sticky-resize-handle" id="srh-${s.id}" title="Drag to resize">
        <svg viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg">
          <line x1="10" y1="2" x2="2" y2="10" stroke="rgba(0,0,0,.55)" stroke-width="1.8" stroke-linecap="round"/>
          <line x1="10" y1="6" x2="6" y2="10" stroke="rgba(0,0,0,.55)" stroke-width="1.8" stroke-linecap="round"/>
          <line x1="10" y1="10" x2="10" y2="10" stroke="rgba(0,0,0,.55)" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      </div>`;

    board.insertBefore(card, empty||null);

    const handle = card.querySelector('.sticky-resize-handle');
    let startX, startY, startW, startH;

    function onDown(e){
      e.preventDefault(); e.stopPropagation();
      const touch = e.touches ? e.touches[0] : e;
      startX=touch.clientX; startY=touch.clientY;
      startW=card.offsetWidth; startH=card.offsetHeight;
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup',   onUp);
      document.addEventListener('touchmove', onMove, {passive:false});
      document.addEventListener('touchend',  onUp);
    }

    function onMove(e){
      e.preventDefault();
      const touch = e.touches ? e.touches[0] : e;
      const newW = Math.max(190, startW + (touch.clientX - startX));
      const newH = Math.max(140, startH + (touch.clientY - startY));
      card.style.width  = newW + 'px';
      card.style.height = newH + 'px';
    }

    function onUp(){
      const st = STICKIES.find(x=>x.id===s.id);
      if(st){ st.width=card.style.width; st.height=card.style.height; saveStickies(); }
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup',   onUp);
      document.removeEventListener('touchmove', onMove);
      document.removeEventListener('touchend',  onUp);
    }

    handle.addEventListener('mousedown',  onDown);
    handle.addEventListener('touchstart', onDown, {passive:false});
  });
}

/* -- LIVE CLOCK ---------------------------------- */
function startClock(){
  function tick(){
    const now = new Date();
    const fmtTime = tz => now.toLocaleTimeString('en-US',{
      timeZone:tz, hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:true
    });
    const fmtDate = tz => now.toLocaleDateString('en-US',{
      timeZone:tz, weekday:'short', month:'short', day:'numeric'
    });
    document.getElementById('clk-ist-time').textContent = fmtTime('Asia/Kolkata');
    document.getElementById('clk-cst-time').textContent = fmtTime('America/Chicago');
    document.getElementById('clk-ist-date').textContent = fmtDate('Asia/Kolkata');
    document.getElementById('clk-cst-date').textContent = fmtDate('America/Chicago');
  }
  tick();
  setInterval(tick, 1000);
}

/* -- TRADING JOURNAL ----------------------------- */
let TRADES = [];

function loadTrades(){
  // Trades are loaded from DATA (notes.json via GitHub) - see loadFromGitHub
  TRADES = DATA.trades || [];
  updateJournalCount();
}

function updateJournalCount(){
  const el = document.getElementById('nav-journal-count');
  if(el) el.textContent = TRADES.length;
}

async function saveTrades(){
  // Save trades into DATA.trades and push to GitHub
  DATA.trades = TRADES;
  updateJournalCount();
  await saveToGitHub();
}

function uid_trade(){ return 'T'+Date.now().toString(36)+Math.random().toString(36).slice(2,5); }

function calcPnL(trade){
  if(trade.instrument === 'options' && trade.legs?.length){
    const pnls = trade.legs.map(l=>calcLegPnL(l)).filter(v=>v!==null);
    if(!pnls.length) return null;
    return pnls.reduce((a,b)=>a+b, 0);
  }
  if(!trade.exit || !trade.entry || !trade.qty) return null;
  const diff = trade.type==='BUY'
    ? (parseFloat(trade.exit) - parseFloat(trade.entry))
    : (parseFloat(trade.entry) - parseFloat(trade.exit));
  return diff * parseFloat(trade.qty);
}

function fmtPnL(v){
  if(v===null) return '-';
  const s = v>=0 ? '+' : '';
  return s+'₹'+Math.abs(v).toLocaleString('en-IN',{maximumFractionDigits:2});
}

function getFilteredTrades(){
  const month  = document.getElementById('tj-filter-month')?.value  || 'all';
  const status = document.getElementById('tj-filter-status')?.value || 'all';
  return TRADES.filter(t=>{
    if(month !== 'all'){
      const d = new Date(t.date);
      if(d.getMonth() !== parseInt(month)) return false;
    }
    if(status !== 'all' && t.status !== status) return false;
    return true;
  });
}

function renderJournal(){
  const trades = getFilteredTrades();
  const tbody  = document.getElementById('tj-tbody');
  const empty  = document.getElementById('tj-empty');
  const stats  = document.getElementById('tj-stats');
  if(!tbody) return;

  // compute stats
  const wins   = trades.filter(t=>t.status==='win').length;
  const losses = trades.filter(t=>t.status==='loss').length;
  const open   = trades.filter(t=>t.status==='open').length;
  const pnls   = trades.map(t=>calcPnL(t)).filter(v=>v!==null);
  const netPnL = pnls.reduce((a,b)=>a+b, 0);
  const winRate= trades.length ? Math.round((wins/trades.length)*100) : 0;

  stats.innerHTML = `
    <div class="tj-stat">
      <div class="tj-stat-num b">${trades.length}</div>
      <div class="tj-stat-lbl">Total Trades</div>
    </div>
    <div class="tj-stat">
      <div class="tj-stat-num ${winRate>=50?'g':'r'}">${winRate}%</div>
      <div class="tj-stat-lbl">Win Rate</div>
    </div>
    <div class="tj-stat">
      <div class="tj-stat-num ${netPnL>=0?'g':'r'}">${fmtPnL(netPnL)}</div>
      <div class="tj-stat-lbl">Net P&L</div>
    </div>
    <div class="tj-stat">
      <div class="tj-stat-num g">${wins}</div>
      <div class="tj-stat-lbl">Wins</div>
    </div>
    <div class="tj-stat">
      <div class="tj-stat-num r">${losses}</div>
      <div class="tj-stat-lbl">Losses</div>
    </div>`;

  if(!trades.length){
    tbody.innerHTML='';
    empty.style.display='flex';
    return;
  }
  empty.style.display='none';

  const sorted = [...trades].sort((a,b)=>new Date(b.date)-new Date(a.date));
  tbody.innerHTML = sorted.map(t=>{
    const pnl = calcPnL(t);
    const pnlHtml = pnl===null ? '<span style="color:#9ca3af">-</span>'
      : `<span class="${pnl>=0?'tj-pnl-g':'tj-pnl-r'}">${fmtPnL(pnl)}</span>`;
    const isOpt = t.instrument === 'options';
    const instBadge = isOpt
      ? `<span style="font-size:9px;background:#f3e8ff;color:#7c3aed;border-radius:4px;padding:2px 6px;font-weight:700;margin-left:4px">OPT</span>`
      : t.instrument === 'futures'
        ? `<span style="font-size:9px;background:#fef9c3;color:#a16207;border-radius:4px;padding:2px 6px;font-weight:700;margin-left:4px">FUT</span>`
        : '';
    const typeHtml = isOpt
      ? `<span style="font-size:11px;font-weight:700;color:#7c3aed">${(t.legs||[]).length} leg${(t.legs||[]).length!==1?'s':''}</span>`
      : t.type==='BUY'
        ? `<span class="tj-type-buy">▲ BUY</span>`
        : `<span class="tj-type-sell">▼ SELL</span>`;
    const entryHtml = isOpt
      ? `<span style="color:#9ca3af;font-size:12px">${(t.legs||[]).map(l=>`${l.action} ${l.optType}`).join(', ')}</span>`
      : `₹${parseFloat(t.entry||0).toLocaleString('en-IN')}`;
    const exitHtml = isOpt
      ? `<span style="color:#9ca3af">-</span>`
      : (t.exit ? '₹'+parseFloat(t.exit).toLocaleString('en-IN') : '-');
    const badge = `<span class="tj-badge ${t.status}">${
      t.status==='win'?'✅ Win':t.status==='loss'?'❌ Loss':'⏳ Open'
    }</span>`;
    return `<tr onclick="openTradeModal('${t.id}')">
      <td style="color:#6b7280;font-size:12px;white-space:nowrap">${t.date||'-'}</td>
      <td><span class="tj-symbol">${esc(t.symbol)}</span>${instBadge}</td>
      <td>${typeHtml}</td>
      <td style="font-weight:600">${entryHtml}</td>
      <td style="color:#6b7280">${exitHtml}</td>
      <td style="color:#6b7280">${isOpt ? '-' : (t.qty||'-')}</td>
      <td>${pnlHtml}</td>
      <td>${badge}</td>
      <td><span class="tj-notes-cell" title="${esc(t.notes||'')}">${esc(t.notes||'-')}</span></td>
      <td onclick="event.stopPropagation()" style="white-space:nowrap">
        <button class="tj-act-btn" onclick="openTradeModal('${t.id}')">Edit</button>
        <button class="tj-act-btn del" onclick="deleteTrade('${t.id}')">Delete</button>
      </td>
    </tr>`;
  }).join('');
}

/* ── INSTRUMENT TOGGLE ── */
function onInstrumentChange(){
  const inst = document.getElementById('tj-instrument').value;
  const isOpt = inst === 'options';
  document.getElementById('tj-eq-section').style.display  = isOpt ? 'none' : '';
  document.getElementById('tj-opt-section').style.display = isOpt ? '' : 'none';
  document.getElementById('tj-pnl-preview').style.display = 'none';
  if(isOpt && document.getElementById('tj-legs-container').children.length === 0) addLeg();
  else if(!isOpt) updatePnLPreview();
}

/* ── LEG BUILDER ── */
let _legCounter = 0;
function addLeg(){
  _legCounter++;
  const legId = 'leg_'+_legCounter;
  const wrap = document.createElement('div');
  wrap.id = legId;
  wrap.style.cssText = 'background:var(--sidebar);border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin-bottom:10px;position:relative';
  wrap.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
      <span style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--accent)">Leg ${_legCounter}</span>
      <button onclick="removeLeg('${legId}')" style="background:none;border:none;cursor:pointer;font-size:14px;color:#dc2626;line-height:1">✕</button>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:10px">
      <div class="frow" style="margin:0"><label>CE / PE</label>
        <select class="leg-opttype" data-leg="${legId}" onchange="updateLegsPreview()">
          <option value="CE">📈 CE (Call)</option>
          <option value="PE">📉 PE (Put)</option>
        </select>
      </div>
      <div class="frow" style="margin:0"><label>Strike</label>
        <input class="leg-strike" data-leg="${legId}" type="number" placeholder="e.g. 22000" oninput="updateLegsPreview()">
      </div>
      <div class="frow" style="margin:0"><label>Expiry</label>
        <input class="leg-expiry" data-leg="${legId}" type="text" placeholder="e.g. 27Mar">
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px">
      <div class="frow" style="margin:0"><label>Action</label>
        <select class="leg-action" data-leg="${legId}" onchange="updateLegsPreview()">
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
      </div>
      <div class="frow" style="margin:0"><label>Qty (lots)</label>
        <input class="leg-qty" data-leg="${legId}" type="number" placeholder="1" oninput="updateLegsPreview()">
      </div>
      <div class="frow" style="margin:0"><label>Entry ₹</label>
        <input class="leg-entry" data-leg="${legId}" type="number" step="0.01" placeholder="0.00" oninput="updateLegsPreview()">
      </div>
      <div class="frow" style="margin:0"><label>Exit ₹</label>
        <input class="leg-exit" data-leg="${legId}" type="number" step="0.01" placeholder="0.00" oninput="updateLegsPreview()">
      </div>
    </div>`;
  document.getElementById('tj-legs-container').appendChild(wrap);
  updateLegsPreview();
}

function removeLeg(legId){
  const el = document.getElementById(legId);
  if(el) el.remove();
  updateLegsPreview();
}

function getLegData(){
  const legs = [];
  document.querySelectorAll('#tj-legs-container > div').forEach(wrap=>{
    const legId = wrap.id;
    legs.push({
      legId,
      optType: wrap.querySelector('.leg-opttype')?.value || 'CE',
      strike:  wrap.querySelector('.leg-strike')?.value  || '',
      expiry:  wrap.querySelector('.leg-expiry')?.value  || '',
      action:  wrap.querySelector('.leg-action')?.value  || 'BUY',
      qty:     parseFloat(wrap.querySelector('.leg-qty')?.value)  || 0,
      entry:   parseFloat(wrap.querySelector('.leg-entry')?.value) || 0,
      exit:    parseFloat(wrap.querySelector('.leg-exit')?.value)  || 0,
    });
  });
  return legs;
}

function calcLegPnL(leg){
  if(!leg.entry || !leg.exit || !leg.qty) return null;
  const diff = leg.action === 'BUY' ? (leg.exit - leg.entry) : (leg.entry - leg.exit);
  return diff * leg.qty;
}

function updateLegsPreview(){
  const legs = getLegData();
  const pnlBox   = document.getElementById('tj-legs-pnl');
  const rowsEl   = document.getElementById('tj-legs-pnl-rows');
  const totalEl  = document.getElementById('tj-legs-total');
  const hasData  = legs.some(l=>l.entry && l.exit && l.qty);
  if(!hasData){ pnlBox.style.display='none'; return; }
  pnlBox.style.display='block';
  let total = 0;
  let html = '';
  legs.forEach((leg,i)=>{
    const pnl = calcLegPnL(leg);
    if(pnl !== null){
      total += pnl;
      const label = `${leg.action} ${leg.optType}${leg.strike ? ' '+leg.strike : ''} Leg ${i+1}`;
      const color = pnl >= 0 ? '#059669' : '#dc2626';
      html += `<div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0;color:#374151">
        <span>${label}</span>
        <span style="font-weight:700;color:${color}">${fmtPnL(pnl)}</span>
      </div>`;
    }
  });
  rowsEl.innerHTML = html;
  totalEl.textContent = fmtPnL(total);
  totalEl.style.color = total >= 0 ? '#059669' : '#dc2626';
}

function populateLegInputs(legs){
  const container = document.getElementById('tj-legs-container');
  container.innerHTML = '';
  _legCounter = 0;
  legs.forEach(leg=>{
    addLeg();
    const wrap = container.lastElementChild;
    if(wrap){
      wrap.querySelector('.leg-opttype').value = leg.optType || 'CE';
      wrap.querySelector('.leg-strike').value  = leg.strike  || '';
      wrap.querySelector('.leg-expiry').value  = leg.expiry  || '';
      wrap.querySelector('.leg-action').value  = leg.action  || 'BUY';
      wrap.querySelector('.leg-qty').value     = leg.qty     || '';
      wrap.querySelector('.leg-entry').value   = leg.entry   || '';
      wrap.querySelector('.leg-exit').value    = leg.exit    || '';
    }
  });
  updateLegsPreview();
}

/* ── OPEN / CLOSE MODAL ── */
function openTradeModal(id){
  const existing = id ? TRADES.find(t=>t.id===id) : null;
  document.getElementById('trade-modal-heading').textContent = existing ? 'Edit Trade' : 'Log New Trade';
  document.getElementById('trade-edit-id').value = existing ? existing.id : '';
  document.getElementById('tj-symbol').value     = existing?.symbol     || '';
  document.getElementById('tj-date').value       = existing?.date       || new Date().toISOString().slice(0,10);
  document.getElementById('tj-instrument').value = existing?.instrument || 'equity';
  document.getElementById('tj-status').value     = existing?.status     || 'open';
  document.getElementById('tj-notes').value      = existing?.notes      || '';

  const isOpt = (existing?.instrument === 'options');
  document.getElementById('tj-eq-section').style.display  = isOpt ? 'none' : '';
  document.getElementById('tj-opt-section').style.display = isOpt ? '' : 'none';

  if(isOpt){
    const legs = existing?.legs || [];
    if(legs.length) populateLegInputs(legs);
    else { document.getElementById('tj-legs-container').innerHTML=''; _legCounter=0; addLeg(); }
  } else {
    document.getElementById('tj-type').value   = existing?.type   || 'BUY';
    document.getElementById('tj-qty').value    = existing?.qty    || '';
    document.getElementById('tj-entry').value  = existing?.entry  || '';
    document.getElementById('tj-exit').value   = existing?.exit   || '';
    document.getElementById('tj-sl').value     = existing?.sl     || '';
    document.getElementById('tj-target').value = existing?.target || '';
    updatePnLPreview();
  }
  document.getElementById('trade-modal-overlay').classList.add('open');
}
function closeTradeModal(){ document.getElementById('trade-modal-overlay').classList.remove('open'); }

function updatePnLPreview(){
  const entry = parseFloat(document.getElementById('tj-entry').value);
  const exit  = parseFloat(document.getElementById('tj-exit').value);
  const qty   = parseFloat(document.getElementById('tj-qty').value);
  const type  = document.getElementById('tj-type').value;
  const prev  = document.getElementById('tj-pnl-preview');
  const val   = document.getElementById('tj-pnl-val');
  if(entry && exit && qty){
    const pnl = type==='BUY' ? (exit-entry)*qty : (entry-exit)*qty;
    prev.style.display='flex';
    val.textContent = fmtPnL(pnl);
    val.style.color = pnl>=0 ? '#059669' : '#dc2626';
  } else {
    prev.style.display='none';
  }
}

function initJournalListeners(){
  ['tj-entry','tj-exit','tj-qty','tj-type'].forEach(id=>{
    const el=document.getElementById(id);
    if(el) el.addEventListener('input', updatePnLPreview);
  });
}

/* ── SAVE TRADE ── */
function saveTrade(){
  const symbol = document.getElementById('tj-symbol').value.trim().toUpperCase();
  if(!symbol){ toast('Symbol is required','error'); return; }
  const instrument = document.getElementById('tj-instrument').value;
  const id = document.getElementById('trade-edit-id').value;
  let trade;

  if(instrument === 'options'){
    const legs = getLegData();
    if(!legs.length){ toast('Add at least one option leg','error'); return; }
    trade = {
      id:         id || uid_trade(),
      symbol,
      instrument: 'options',
      date:       document.getElementById('tj-date').value,
      legs,
      status:     document.getElementById('tj-status').value,
      notes:      document.getElementById('tj-notes').value.trim(),
    };
  } else {
    const entry = document.getElementById('tj-entry').value;
    if(!entry){ toast('Entry price is required','error'); return; }
    trade = {
      id:         id || uid_trade(),
      symbol,
      instrument,
      date:       document.getElementById('tj-date').value,
      type:       document.getElementById('tj-type').value,
      qty:        document.getElementById('tj-qty').value,
      entry,
      exit:       document.getElementById('tj-exit').value,
      sl:         document.getElementById('tj-sl').value,
      target:     document.getElementById('tj-target').value,
      status:     document.getElementById('tj-status').value,
      notes:      document.getElementById('tj-notes').value.trim(),
    };
  }

  if(id){ TRADES = TRADES.map(t=>t.id===id ? trade : t); }
  else  { TRADES.push(trade); }

  saveTrades();
  renderJournal();
  closeTradeModal();
  toast('Trade saved ✓','success');
}

function deleteTrade(id){
  if(!confirm('Delete this trade?')) return;
  TRADES = TRADES.filter(t=>t.id!==id);
  saveTrades();
  renderJournal();
  toast('Trade deleted','success');
}

/* ── TASK & ACTION NOTES ─────────────────────────── */
/* ── TASK & ACTION NOTES ─────────────────────────── */
let TASKNOTES = [];
let _tanFilter    = 'all';
let _tanCatFilter = 'all';
let _tanSort      = 'date-desc';

function uid_tan(){ return 'TN'+Date.now().toString(36)+Math.random().toString(36).slice(2,5); }

function updateTaskNotesCount(){
  const open = TASKNOTES.filter(n=>!n.done).length;
  const el = document.getElementById('nav-tasknotes-count');
  if(el) el.textContent = TASKNOTES.length;
  const hdr = document.getElementById('tan-hdr-count');
  if(hdr) hdr.textContent = TASKNOTES.length + ' note' + (TASKNOTES.length!==1?'s':'') + (open?' · '+open+' open':'');
}

async function saveTaskNotes(){
  DATA.tasknotes = TASKNOTES;
  updateTaskNotesCount();
  await saveToGitHub();
}

function tanSetFilter(f, btn){
  _tanFilter = f;
  document.querySelectorAll('#tan-f-all,#tan-f-open,#tan-f-done,#tan-f-high,#tan-f-medium,#tan-f-low')
    .forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  renderTaskNotes();
}

function tanSetCat(cat, btn){
  _tanCatFilter = cat;
  document.querySelectorAll('#tan-fc-all,#tan-fc-personal,#tan-fc-official')
    .forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  renderTaskNotes();
}

function addTaskNote(){
  const input = document.getElementById('tan-quick-input');
  const text  = input.value.trim();
  if(!text){ toast('Write something first','error'); return; }
  const cat = document.getElementById('tan-quick-cat')?.value || 'personal';
  const note = {
    id:       uid_tan(),
    text,
    category: cat,
    priority: 'medium',
    tags:     [],
    done:     false,
    date:     new Date().toISOString().slice(0,10),
    created:  new Date().toISOString(),
  };
  TASKNOTES.unshift(note);
  input.value = '';
  input.style.height = '';
  saveTaskNotes();
  renderTaskNotes();
  toast('Note added \u2713','success');
}

/* 2. fade-out then toggle done */
function toggleTanDone(id){
  const n = TASKNOTES.find(n=>n.id===id);
  if(!n) return;
  n.done = !n.done;
  if(n.done){
    const el = document.getElementById('tan-item-'+id);
    if(el){
      el.classList.add('fading-out');
      setTimeout(()=>{ saveTaskNotes(); renderTaskNotes(); }, 260);
      return;
    }
  }
  saveTaskNotes(); renderTaskNotes();
}

function deleteTanNote(id){
  if(!confirm('Delete this note?')) return;
  const el = document.getElementById('tan-item-'+id);
  if(el){ el.classList.add('fading-out'); setTimeout(()=>{ TASKNOTES=TASKNOTES.filter(n=>n.id!==id); saveTaskNotes(); renderTaskNotes(); },260); }
  else  { TASKNOTES=TASKNOTES.filter(n=>n.id!==id); saveTaskNotes(); renderTaskNotes(); }
  toast('Note deleted','success');
}

/* 7. Quick actions */
function tanDuplicate(id){
  const n = TASKNOTES.find(n=>n.id===id);
  if(!n) return;
  const copy = {...n, id:uid_tan(), created:new Date().toISOString(), done:false};
  TASKNOTES.unshift(copy);
  closeTanDropdown();
  saveTaskNotes(); renderTaskNotes();
  toast('Duplicated \u2713','success');
}

let _openDropdown = null;
function toggleTanDropdown(id, evt){
  evt.stopPropagation();
  const dd = document.getElementById('tan-dd-'+id);
  if(!dd) return;
  if(_openDropdown && _openDropdown!==dd){ _openDropdown.classList.remove('open'); }
  dd.classList.toggle('open');
  _openDropdown = dd.classList.contains('open') ? dd : null;
}
function closeTanDropdown(){
  if(_openDropdown){ _openDropdown.classList.remove('open'); _openDropdown=null; }
}
document.addEventListener('click', ()=>closeTanDropdown());

function saveTanEdit(id){
  const n = TASKNOTES.find(n=>n.id===id);
  if(!n) return;
  const textEl = document.getElementById('tan-edit-text-'+id);
  const prioEl = document.getElementById('tan-edit-prio-'+id);
  const tagEl  = document.getElementById('tan-edit-tag-'+id);
  const catEl  = document.getElementById('tan-edit-cat-'+id);
  if(textEl) n.text     = textEl.value.trim() || n.text;
  if(prioEl) n.priority = prioEl.value;
  if(catEl)  n.category = catEl.value;
  // 5. parse tags from comma-separated input into array
  if(tagEl){
    const raw = tagEl.value.trim();
    n.tags = raw ? raw.split(',').map(t=>t.trim()).filter(Boolean) : [];
  }
  saveTaskNotes(); renderTaskNotes();
  toast('Saved \u2713','success');
}

function renderTaskNotes(){
  const list = document.getElementById('tan-list');
  if(!list) return;
  const search = (document.getElementById('tan-search')?.value||'').toLowerCase();
  const sort   = document.getElementById('tan-sort')?.value || 'date-desc';
  _tanSort = sort;
  let items = [...TASKNOTES];

  // category filter
  if(_tanCatFilter==='personal') items = items.filter(n=>(n.category||'personal')==='personal');
  if(_tanCatFilter==='official') items = items.filter(n=>n.category==='official');

  // status / priority filter
  if(_tanFilter==='open')   items = items.filter(n=>!n.done);
  if(_tanFilter==='done')   items = items.filter(n=>n.done);
  if(_tanFilter==='high')   items = items.filter(n=>n.priority==='high');
  if(_tanFilter==='medium') items = items.filter(n=>n.priority==='medium');
  if(_tanFilter==='low')    items = items.filter(n=>n.priority==='low');
  if(search) items = items.filter(n=>{
    const tags = Array.isArray(n.tags) ? n.tags.join(' ') : (n.tags||'');
    return n.text.toLowerCase().includes(search) || tags.toLowerCase().includes(search);
  });

  // 6. sort
  const prioOrder = {high:0,medium:1,low:2};
  if(sort==='date-desc') items.sort((a,b)=>new Date(b.created)-new Date(a.created));
  else if(sort==='date-asc') items.sort((a,b)=>new Date(a.created)-new Date(b.created));
  else if(sort==='priority') items.sort((a,b)=>(prioOrder[a.priority||'medium']||1)-(prioOrder[b.priority||'medium']||1));
  else if(sort==='category') items.sort((a,b)=>(a.category||'personal').localeCompare(b.category||'personal'));
  else if(sort==='status') items.sort((a,b)=>(a.done?1:0)-(b.done?1:0));

  updateTaskNotesCount();

  if(!items.length){
    list.innerHTML = `<div class="tan-empty">
      <div class="tan-empty-icon">✍️</div>
      <div style="font-size:14px;font-weight:600;color:var(--text2)">No notes here</div>
      <div style="font-size:13px">Try a different filter or add a new note above.</div>
    </div>`;
    return;
  }

  // 3. split into open and done sections
  const open = items.filter(n=>!n.done);
  const done = items.filter(n=>n.done);

  const fmtDate = iso => {
    if(!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'});
  };

  function renderItem(n){
    const cat      = n.category || 'personal';
    const catLabel = cat==='official' ? '💼 Official' : '👤 Personal';
    const prio     = n.priority || 'medium';
    const prioLabels = {high:'🔴 High', medium:'🟡 Med', low:'🟢 Low'};
    const doneCls  = n.done ? ' done' : '';
    // 5. tags as chips
    const tagArr   = Array.isArray(n.tags) ? n.tags : (n.tags ? [n.tags] : []);
    const tagHtml  = tagArr.map(t=>`<span class="tan-tag-chip">#${esc(t)}</span>`).join('');

    return `<div class="tan-item" id="tan-item-${n.id}" style="display:flex;flex-direction:row">
      <div class="tan-item-strip ${prio}"></div>
      <div class="tan-item-inner">
        <div class="tan-item-top">
          <input type="checkbox" class="tan-done-cb" ${n.done?'checked':''} onchange="toggleTanDone('${n.id}')">
          <span class="tan-item-priority ${prio}">${prioLabels[prio]}</span>
          <div class="tan-item-text${doneCls}">${esc(n.text)}</div>
          <div class="tan-item-actions">
            <button class="tan-act" onclick="tanToggleEdit('${n.id}')">Edit</button>
            <div style="position:relative">
              <button class="tan-dot-btn" onclick="toggleTanDropdown('${n.id}',event)" title="More">⋯</button>
              <div class="tan-dropdown" id="tan-dd-${n.id}">
                <div class="tan-dd-item" onclick="tanDuplicate('${n.id}')">📋 Duplicate</div>
                <div class="tan-dd-item" onclick="tanToggleEdit('${n.id}');closeTanDropdown()">✏️ Edit</div>
                <div class="tan-dd-item danger" onclick="deleteTanNote('${n.id}')">🗑 Delete</div>
              </div>
            </div>
          </div>
        </div>
        <div class="tan-item-meta">
          <span class="tan-cat-badge ${cat}">${catLabel}</span>
          <span class="tan-date-badge">📅 ${fmtDate(n.date)}</span>
          ${tagHtml}
          <span style="font-size:11px;color:var(--muted)">${n.done?'✅ Done':'⏳ Open'}</span>
        </div>
        <div class="tan-edit-area" id="tan-edit-${n.id}">
          <textarea class="tan-edit-textarea" id="tan-edit-text-${n.id}" rows="3">${esc(n.text)}</textarea>
          <div class="tan-edit-row">
            <select class="tan-cat-sel" id="tan-edit-cat-${n.id}" style="padding:5px 10px;font-size:12px">
              <option value="personal" ${cat==='personal'?'selected':''}>👤 Personal</option>
              <option value="official" ${cat==='official'?'selected':''}>💼 Official</option>
            </select>
            <select class="tan-priority-sel" id="tan-edit-prio-${n.id}">
              <option value="high"   ${prio==='high'  ?'selected':''}>🔴 High</option>
              <option value="medium" ${prio==='medium'?'selected':''}>🟡 Medium</option>
              <option value="low"    ${prio==='low'   ?'selected':''}>🟢 Low</option>
            </select>
            <input class="tan-tag-input" id="tan-edit-tag-${n.id}"
              placeholder="Tags (comma separated)"
              value="${esc(tagArr.join(', '))}">
            <button class="tan-save-btn" onclick="saveTanEdit('${n.id}')">Save</button>
          </div>
        </div>
      </div>
    </div>`;
  }

  function sectionHtml(title, arr, key){
    if(!arr.length) return '';
    return `<div>
      <div class="tan-section-hdr" onclick="tanToggleSection('${key}')">
        <span class="tan-section-chevron" id="tan-chev-${key}">▼</span>
        <span class="tan-section-title">${title}</span>
        <span class="tan-section-count">${arr.length}</span>
      </div>
      <div class="tan-section-body" id="tan-sec-${key}">
        ${arr.map(renderItem).join('')}
      </div>
    </div>`;
  }

  list.innerHTML = sectionHtml('Open Tasks', open, 'open') + sectionHtml('Completed', done, 'done');
}

function tanToggleSection(key){
  const body = document.getElementById('tan-sec-'+key);
  const chev = document.getElementById('tan-chev-'+key);
  if(!body) return;
  body.classList.toggle('collapsed');
  if(chev) chev.classList.toggle('collapsed');
}

function tanToggleEdit(id){
  const el   = document.getElementById('tan-edit-'+id);
  const item = document.getElementById('tan-item-'+id);
  if(!el) return;
  const isOpen = el.classList.contains('open');
  el.classList.toggle('open', !isOpen);
  if(item) item.classList.toggle('editing', !isOpen);
}

/* ── FINANCE TRACKER ─────────────────────────────── */
let FINANCE = [];
let _finFilter     = 'all';
let _finPersonFilter = 'all';

function uid_fin(){ return 'FN'+Date.now().toString(36)+Math.random().toString(36).slice(2,5); }

function finRupee(v){
  return '₹'+Math.abs(v).toLocaleString('en-IN',{maximumFractionDigits:2});
}

function updateFinanceCount(){
  const pending = FINANCE.filter(e=>finStatus(e)!=='settled').length;
  const el = document.getElementById('nav-finance-count');
  if(el) el.textContent = pending || FINANCE.length;
}

/* derive status — only principal repayments count toward settlement */
function finStatus(e){
  const principalPaid=(e.repayments||[])
    .filter(r=>r.repayType==='principal'||r.repayType==='both'||!r.repayType)
    .reduce((s,r)=>s+r.amount,0);
  if(e.status==='settled') return 'settled';
  if(principalPaid>=e.amount) return 'settled';
  if(principalPaid>0) return 'partial';
  if(e.duedate&&new Date(e.duedate)<new Date()) return 'overdue';
  return 'pending';
}

function finRemaining(e){
  const principalPaid=(e.repayments||[])
    .filter(r=>r.repayType==='principal'||r.repayType==='both'||!r.repayType)
    .reduce((s,r)=>s+r.amount,0);
  return Math.max(0,e.amount-principalPaid);
}

function finTotalInterestPaid(e){
  return (e.repayments||[])
    .filter(r=>r.repayType==='interest'||r.repayType==='both')
    .reduce((s,r)=>s+r.amount,0);
}

async function saveFinance(){
  DATA.finance=FINANCE;
  updateFinanceCount();
  await saveToGitHub();
}

let _finView = 'card';
let _finGroupBy = false;

function finSetView(v){
  _finView = v;
  const list = document.getElementById('fin-list');
  if(list){ list.className = 'fin-list fin-view-'+v; }
  document.getElementById('fin-vcard').classList.toggle('active', v==='card');
  document.getElementById('fin-vlist').classList.toggle('active', v==='list');
  renderFinance();
}

function finToggleGroup(btn){
  _finGroupBy = !_finGroupBy;
  btn.classList.toggle('active', _finGroupBy);
  renderFinance();
}

function finToggleTimeline(btn){
  const panel = document.getElementById('fin-timeline-panel');
  if(!panel) return;
  const isOpen = panel.classList.toggle('open');
  btn.classList.toggle('active', isOpen);
  if(isOpen) renderFinanceTimeline();
}

function renderFinanceTimeline(){
  const rows = document.getElementById('fin-tl-rows');
  if(!rows) return;
  const today = new Date(); today.setHours(0,0,0,0);
  const withDue = FINANCE
    .filter(e=>e.duedate && finStatus(e)!=='settled')
    .sort((a,b)=>new Date(a.duedate)-new Date(b.duedate));
  if(!withDue.length){
    rows.innerHTML='<div style="font-size:12px;color:var(--muted)">No upcoming due dates</div>';
    return;
  }
  const fmtD=iso=>{const d=new Date(iso);return d.toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'});};
  rows.innerHTML = withDue.map(e=>{
    const due=new Date(e.duedate);due.setHours(0,0,0,0);
    const diff=Math.round((due-today)/(86400000));
    let dotCls='ok', label='';
    if(diff<0){dotCls='overdue';label=`🔴 Overdue by ${Math.abs(diff)}d`;}
    else if(diff===0){dotCls='today';label='🟡 Due today';}
    else if(diff<=7){dotCls='soon';label=`🟡 ${diff}d left`;}
    else{label=`✅ ${diff}d left`;}
    const amtCls=e.type==='gave'?'gave':'borrowed';
    return `<div class="fin-tl-row">
      <div class="fin-tl-dot ${dotCls}"></div>
      <div class="fin-tl-date">${fmtD(e.duedate)}</div>
      <div class="fin-tl-person">${esc(e.person)}${e.notes?` · <span style="color:var(--muted)">${esc(e.notes.slice(0,30))}</span>`:''}</div>
      <div class="fin-tl-amt ${amtCls}">${finRupee(finRemaining(e))}</div>
      <div style="font-size:11px;white-space:nowrap">${label}</div>
    </div>`;
  }).join('');
}

/* 8. Settled section toggle */
function finToggleSettled(key){
  const body=document.getElementById('fin-settled-body-'+key);
  const chev=document.getElementById('fin-settled-chev-'+key);
  if(!body) return;
  body.classList.toggle('collapsed');
  if(chev) chev.classList.toggle('collapsed');
}

function finSetFilter(f,btn){
  _finFilter=f;
  document.querySelectorAll('#fin-f-all,#fin-f-gave,#fin-f-borrowed,#fin-f-pending,#fin-f-partial,#fin-f-overdue,#fin-f-settled')
    .forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  renderFinance();
}

function finSetPerson(name){
  _finPersonFilter=_finPersonFilter===name?'all':name;
  renderFinance();
}

function openFinModal(id){
  const ex=id?FINANCE.find(e=>e.id===id):null;
  document.getElementById('fin-modal-title').textContent=ex?'Edit Entry':'New Entry';
  document.getElementById('fin-edit-id').value    =ex?ex.id:'';
  document.getElementById('fin-type').value       =ex?.type      ||'gave';
  document.getElementById('fin-person').value     =ex?.person    ||'';
  document.getElementById('fin-amount').value     =ex?.amount    ||'';
  document.getElementById('fin-paymethod').value  =ex?.paymethod ||'cash';
  document.getElementById('fin-interest').value   =ex?.interestRate||'';
  document.getElementById('fin-date').value       =ex?.date      ||new Date().toISOString().slice(0,10);
  document.getElementById('fin-duedate').value    =ex?.duedate   ||'';
  document.getElementById('fin-notes').value      =ex?.notes     ||'';
  document.getElementById('fin-modal-overlay').classList.add('open');
}
function closeFinModal(){document.getElementById('fin-modal-overlay').classList.remove('open');}

function saveFinEntry(){
  const person=document.getElementById('fin-person').value.trim();
  if(!person){toast('Person name is required','error');return;}
  const amount=parseFloat(document.getElementById('fin-amount').value);
  if(!amount||amount<=0){toast('Enter a valid amount','error');return;}
  const id=document.getElementById('fin-edit-id').value;
  const existing=id?FINANCE.find(e=>e.id===id):null;
  const entry={
    id:          id||uid_fin(),
    type:        document.getElementById('fin-type').value,
    person,
    amount,
    paymethod:   document.getElementById('fin-paymethod').value,
    interestRate:parseFloat(document.getElementById('fin-interest').value)||0,
    date:        document.getElementById('fin-date').value,
    duedate:     document.getElementById('fin-duedate').value,
    notes:       document.getElementById('fin-notes').value.trim(),
    repayments:  existing?(existing.repayments||[]):[],
    created:     existing?existing.created:new Date().toISOString(),
  };
  if(id){FINANCE=FINANCE.map(e=>e.id===id?entry:e);}
  else  {FINANCE.unshift(entry);}
  closeFinModal();
  saveFinance();
  renderFinance();
  toast('Entry saved \u2713','success');
}

function deleteFinEntry(id){
  if(!confirm('Delete this entry?')) return;
  FINANCE=FINANCE.filter(e=>e.id!==id);
  saveFinance();renderFinance();
  toast('Entry deleted','success');
}

function markFinSettled(id){
  const e=FINANCE.find(e=>e.id===id);
  if(!e) return;
  e.status='settled';
  const rem=finRemaining(e);
  if(rem>0) e.repayments.push({amount:rem,repayType:'principal',paymethod:'cash',note:'Settled',date:new Date().toISOString().slice(0,10)});
  saveFinance();renderFinance();
  toast('Marked as settled \u2713','success');
}

function deleteRepayment(entryId,idx){
  if(!confirm('Remove this payment?')) return;
  const e=FINANCE.find(e=>e.id===entryId);
  if(!e) return;
  e.repayments.splice(idx,1);
  saveFinance();renderFinance();
  toast('Payment removed','success');
}

function addRepayment(id){
  const amtEl   =document.getElementById('fin-repay-amt-'+id);
  const noteEl  =document.getElementById('fin-repay-note-'+id);
  const dateEl  =document.getElementById('fin-repay-date-'+id);
  const typeEl  =document.getElementById('fin-repay-type-'+id);
  const methodEl=document.getElementById('fin-repay-method-'+id);
  const amt=parseFloat(amtEl?.value);
  if(!amt||amt<=0){toast('Enter a valid amount','error');return;}
  const e=FINANCE.find(e=>e.id===id);
  if(!e) return;
  e.repayments=e.repayments||[];
  e.repayments.push({
    amount:    amt,
    repayType: typeEl?.value   ||'principal',
    paymethod: methodEl?.value ||'cash',
    note:      noteEl?.value.trim()||'',
    date:      dateEl?.value||new Date().toISOString().slice(0,10),
  });
  saveFinance();renderFinance();
  toast('Payment recorded \u2713','success');
}

function toggleFinHistory(id){
  const el =document.getElementById('fin-history-body-'+id);
  const btn=document.getElementById('fin-history-toggle-'+id);
  if(!el) return;
  const hidden=el.style.display==='none';
  el.style.display=hidden?'':'none';
  if(btn) btn.textContent=hidden?'\u25b2 Hide':'\u25bc History';
}

function toggleFinRepay(id){
  const el=document.getElementById('fin-addrepay-'+id);
  if(el) el.style.display=el.style.display==='none'?'':'none';
}

function toggleFinExpand(id, evt){
  if(evt) evt.stopPropagation();
  const el = document.getElementById('fin-item-'+id);
  if(!el) return;
  const isOpen = el.classList.contains('open');
  el.classList.toggle('open', !isOpen);
  el.style.display = isOpen ? 'none' : '';
  // card view parent
  const card = document.getElementById('fin-card-'+id);
  if(card) card.classList.toggle('expanded', !isOpen);
}

function renderFinance(){
  const list = document.getElementById('fin-list');
  if(!list) return;
  const search = (document.getElementById('fin-search')?.value||'').toLowerCase();

  const personMap={};
  FINANCE.forEach(e=>{
    const p=e.person;
    if(!personMap[p]) personMap[p]={gave:0,borrowed:0};
    const rem=finRemaining(e);
    if(e.type==='gave') personMap[p].gave+=rem;
    else                personMap[p].borrowed+=rem;
  });

  const chips=document.getElementById('fin-person-chips');
  if(chips){
    if(!Object.keys(personMap).length){
      chips.innerHTML='<span style="font-size:12px;color:var(--muted)">No entries yet</span>';
    } else {
      chips.innerHTML=Object.entries(personMap).map(([name,bal])=>{
        const net=bal.gave-bal.borrowed;
        const balLabel=net>0?`+${finRupee(net)}`:net<0?`-${finRupee(Math.abs(net))}`:'✅ Settled';
        const balCls=net>0?'pos':net<0?'neg':'pos';
        const active=_finPersonFilter===name?' active':'';
        return `<div class="fin-person-chip${active}" onclick="finSetPerson('${esc(name)}')">
          <span class="fin-person-name">${esc(name)}</span>
          <span class="fin-person-bal ${balCls}">${balLabel}</span>
        </div>`;
      }).join('');
    }
  }

  const totalGave    =FINANCE.filter(e=>e.type==='gave').reduce((s,e)=>s+finRemaining(e),0);
  const totalBorrowed=FINANCE.filter(e=>e.type==='borrowed').reduce((s,e)=>s+finRemaining(e),0);
  const net=totalGave-totalBorrowed;
  const gaveCount=FINANCE.filter(e=>e.type==='gave'&&finStatus(e)!=='settled').length;
  const borCount =FINANCE.filter(e=>e.type==='borrowed'&&finStatus(e)!=='settled').length;
  const sg=document.getElementById('fin-sum-gave');
  const sb=document.getElementById('fin-sum-borrow');
  const sn=document.getElementById('fin-sum-net');
  if(sg) sg.textContent=finRupee(totalGave);
  if(sb) sb.textContent=finRupee(totalBorrowed);
  if(sn){sn.textContent=(net>=0?'+':'-')+finRupee(Math.abs(net));sn.className='fin-sum-val '+(net>=0?'net-pos':'net-neg');}
  const sgs=document.getElementById('fin-sum-gave-sub');
  const sbs=document.getElementById('fin-sum-borrow-sub');
  const sns=document.getElementById('fin-sum-net-sub');
  if(sgs) sgs.textContent=gaveCount+' pending';
  if(sbs) sbs.textContent=borCount+' pending';
  if(sns) sns.textContent=net>=0?'Overall you are ahead':'Overall you owe more';

  let items=[...FINANCE];
  if(_finPersonFilter!=='all') items=items.filter(e=>e.person===_finPersonFilter);
  if(_finFilter==='gave')      items=items.filter(e=>e.type==='gave');
  if(_finFilter==='borrowed')  items=items.filter(e=>e.type==='borrowed');
  if(_finFilter==='pending')   items=items.filter(e=>finStatus(e)==='pending');
  if(_finFilter==='partial')   items=items.filter(e=>finStatus(e)==='partial');
  if(_finFilter==='overdue')   items=items.filter(e=>finStatus(e)==='overdue');
  if(_finFilter==='settled')   items=items.filter(e=>finStatus(e)==='settled');
  if(search) items=items.filter(e=>e.person.toLowerCase().includes(search)||(e.notes||'').toLowerCase().includes(search));

  // 5. Sort
  const sort = document.getElementById('fin-sort')?.value || 'date-desc';
  if(sort==='date-desc') items.sort((a,b)=>new Date(b.created)-new Date(a.created));
  else if(sort==='date-asc') items.sort((a,b)=>new Date(a.created)-new Date(b.created));
  else if(sort==='amount-desc') items.sort((a,b)=>b.amount-a.amount);
  else if(sort==='amount-asc')  items.sort((a,b)=>a.amount-b.amount);
  else if(sort==='person') items.sort((a,b)=>a.person.localeCompare(b.person));
  else if(sort==='duedate') items.sort((a,b)=>{
    if(!a.duedate) return 1; if(!b.duedate) return -1;
    return new Date(a.duedate)-new Date(b.duedate);
  });
  else if(sort==='status'){
    const ord={overdue:0,pending:1,partial:2,settled:3};
    items.sort((a,b)=>(ord[finStatus(a)]||1)-(ord[finStatus(b)]||1));
  }

  // show FAB when on finance page
  const fab=document.getElementById('fin-fab');
  if(fab) fab.classList.add('visible');

  updateFinanceCount();

  if(!items.length){
    const grid=document.getElementById('fin-card-grid');
    const lbox=document.getElementById('fin-listbox');
    const empty=`<div class="fin-empty">
      <div style="font-size:40px;opacity:.4">💰</div>
      <div style="font-size:14px;font-weight:600;color:var(--text2)">No entries found</div>
      <div style="font-size:13px">Click <strong>+ New Entry</strong> to get started.</div>
    </div>`;
    if(grid) grid.innerHTML=empty;
    if(lbox) lbox.innerHTML='';
    return;
  }

  const fmtD=iso=>{if(!iso)return'';const d=new Date(iso);return d.toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'});};
  const today=new Date();today.setHours(0,0,0,0);
  const payLabel={'cash':'💵 Cash','credit_card':'💳 Card','bank':'🏦 Bank','upi':'📱 UPI'};
  const rtypeLabel={'principal':'Principal','interest':'Interest','both':'Principal+Interest'};

  const cardGrid = document.getElementById('fin-card-grid');
  const listBox  = document.getElementById('fin-listbox');

  const rendered = items.map(e=>{
    const st=finStatus(e);
    const rem=finRemaining(e);
    const paid=e.amount-rem;
    const intPaid=finTotalInterestPaid(e);
    const pct=e.amount>0?Math.round((paid/e.amount)*100):0;
    const isGave=e.type==='gave';
    const amtCls=st==='settled'?'settled':isGave?'gave':'borrowed';
    const pmLabel=payLabel[e.paymethod||'cash'];

    // due badge
    let dueBadge='';
    if(e.duedate&&st!=='settled'){
      const due=new Date(e.duedate);due.setHours(0,0,0,0);
      const diff=Math.round((due-today)/(1000*60*60*24));
      const dueCls=diff<0?'over':diff<=7?'warn':'ok';
      const dueText=diff<0?`Overdue ${Math.abs(diff)}d`:diff===0?'Due today':`${diff}d left`;
      dueBadge=`<span class="fin-due-badge ${dueCls}">📅 ${dueText}</span>`;
    }
    const stBadge=`<span class="fin-status-badge ${st}">${
      st==='settled'?'✅ Settled':st==='partial'?'🔵 Partial':st==='overdue'?'🔴 Overdue':'⏳ Pending'
    }</span>`;
    const interestBadge=e.interestRate>0
      ?`<span style="font-size:10px;background:#fef3c7;color:#92400e;border-radius:4px;padding:1px 6px;font-weight:700">📊 ${e.interestRate}%</span>`:'';
    const pmBadge=`<span class="fin-pay-badge ${e.paymethod||'cash'}" style="font-size:10px">${pmLabel}</span>`;
    const progressBar=pct>0&&st!=='settled'
      ?`<div class="fin-progress" style="margin-top:5px"><div class="fin-progress-fill" style="width:${pct}%"></div></div>`:'';

    // shared expand section
    const repays=e.repayments||[];
    const historyRows=repays.map((r,i)=>{
      const rtype=r.repayType||'principal';
      const rmethod=r.paymethod||'cash';
      return `<div class="fin-repay-row">
        <span class="fin-repay-amt">${finRupee(r.amount)}</span>
        <span class="fin-rtype-badge ${rtype}">${rtypeLabel[rtype]}</span>
        <span class="fin-pay-badge ${rmethod}" style="font-size:10px">${payLabel[rmethod]||rmethod}</span>
        <span class="fin-repay-note">${esc(r.note||'—')}</span>
        <span style="font-size:11px;color:var(--muted);white-space:nowrap;margin-left:auto">${fmtD(r.date)}</span>
        <button onclick="event.stopPropagation();deleteRepayment('${e.id}',${i})"
          style="background:none;border:none;cursor:pointer;color:#dc2626;font-size:11px;padding:0 4px">✕</button>
      </div>`;
    }).join('');
    const historySummary=repays.length
      ?`${repays.length} payment${repays.length!==1?'s':''}${intPaid>0?' · Interest: '+finRupee(intPaid):''}`
      :'No payments yet';
    const settleBtn=st!=='settled'?`<button class="fin-act settle" onclick="event.stopPropagation();markFinSettled('${e.id}')">✅ Settle All</button>`:'';
    const editBtn=`<button class="fin-act" onclick="event.stopPropagation();openFinModal('${e.id}')">Edit</button>`;
    const delBtn=`<button class="fin-act del" onclick="event.stopPropagation();deleteFinEntry('${e.id}')">Delete</button>`;
    const repayBtn=st!=='settled'?`<button class="fin-act" onclick="event.stopPropagation();toggleFinRepay('${e.id}')">+ Payment</button>`:'';
    const histBtn=repays.length?`<button id="fin-history-toggle-${e.id}" class="fin-act" style="padding:2px 8px;font-size:10px" onclick="event.stopPropagation();toggleFinHistory('${e.id}')">▼ History</button>`:'';
    const expandBody=`
      <div id="fin-item-expand-${e.id}">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
          <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)">Payment History</span>
          <span style="display:flex;align-items:center;gap:6px">
            <span style="font-size:11px;color:var(--muted)">${historySummary}</span>
            ${histBtn}
          </span>
        </div>
        <div id="fin-history-body-${e.id}" style="display:none">${historyRows}</div>
        <div class="fin-item-actions" style="margin-top:8px">${editBtn}${settleBtn}${repayBtn}${delBtn}</div>
        <div id="fin-addrepay-${e.id}" style="display:none;margin-top:10px;padding-top:10px;border-top:1px dashed var(--border)">
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:8px">Record Payment</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
            <input class="fin-repay-input" id="fin-repay-amt-${e.id}" type="number" step="0.01" placeholder="Amount ₹" style="width:110px" onclick="event.stopPropagation()">
            <select class="fin-repay-input" id="fin-repay-type-${e.id}" style="width:155px" onclick="event.stopPropagation()">
              <option value="principal">💰 Principal</option>
              <option value="interest">📊 Interest Only</option>
              <option value="both">💰+📊 Both</option>
            </select>
            <select class="fin-repay-input" id="fin-repay-method-${e.id}" style="width:120px" onclick="event.stopPropagation()">
              <option value="cash">💵 Cash</option>
              <option value="credit_card">💳 Card</option>
              <option value="bank">🏦 Bank</option>
              <option value="upi">📱 UPI</option>
            </select>
            <input class="fin-repay-input" id="fin-repay-date-${e.id}" type="date" style="width:130px" value="${new Date().toISOString().slice(0,10)}" onclick="event.stopPropagation()">
            <input class="fin-repay-input" id="fin-repay-note-${e.id}" placeholder="Note (optional)" style="flex:1;min-width:80px" onclick="event.stopPropagation()">
            <button class="fin-add-repay-btn" onclick="event.stopPropagation();addRepayment('${e.id}')">Add</button>
          </div>
        </div>
      </div>`;

    // ── CARD view ──
    const typeLabel=isGave?'💚 I Gave':'❤️ I Borrowed';
    const overdueCardCls=st==='overdue'?' overdue-card':'';
    const cardHtml=`<div class="fin-card ${amtCls}${overdueCardCls}" id="fin-card-${e.id}" onclick="toggleFinExpand('${e.id}',event)">
      <div class="fin-card-eyebrow">
        <span class="fin-card-type">${typeLabel}</span>
        ${stBadge}
      </div>
      <div class="fin-card-person">${esc(e.person)}</div>
      <div class="fin-card-amount ${amtCls}">${finRupee(e.amount)}</div>
      ${e.notes?`<div class="fin-card-note">${esc(e.notes)}</div>`:''}
      <div class="fin-card-tags">
        ${pmBadge}${interestBadge}${dueBadge}
        ${rem<e.amount&&st!=='settled'?`<span class="fin-date-badge" style="font-size:10px">Rem: ${finRupee(rem)}</span>`:''}
      </div>
      ${progressBar}
      <div class="fin-card-meta">
        <span class="fin-card-date">${fmtD(e.date)}</span>
        <div class="fin-card-btns">
          <button class="cbtn" onclick="event.stopPropagation();openFinModal('${e.id}')">Edit</button>
          ${st!=='settled'?`<button class="cbtn" onclick="event.stopPropagation();toggleFinRepay('${e.id}')">+ Payment</button>`:''}
          <button class="cbtn del" onclick="event.stopPropagation();deleteFinEntry('${e.id}')">Delete</button>
        </div>
      </div>
      <div class="fin-item-expand" id="fin-item-${e.id}">${expandBody}</div>
    </div>`;

    // ── LIST row ──
    const rowHtml=`<div class="fin-lrow" id="fin-lrow-${e.id}" onclick="toggleFinExpand('${e.id}',event)">
      <div class="fin-lrow-accent ${amtCls}"></div>
      <div class="fin-lrow-main">
        <div class="fin-lrow-person">${esc(e.person)}</div>
        ${e.notes?`<div class="fin-lrow-note">${esc(e.notes)}</div>`:''}
      </div>
      <div style="display:flex;gap:4px;align-items:center;flex-wrap:wrap">
        ${stBadge}${pmBadge}${interestBadge}${dueBadge}
      </div>
      <div class="fin-lrow-right">
        <span class="fin-lrow-amt ${amtCls}">${finRupee(e.amount)}</span>
        <span style="font-size:10px;color:var(--muted)">${fmtD(e.date)}</span>
        <button class="cbtn" onclick="event.stopPropagation();openFinModal('${e.id}')">Edit</button>
        ${st!=='settled'?`<button class="cbtn" onclick="event.stopPropagation();toggleFinRepay('${e.id}')">+ Payment</button>`:''}
        <button class="cbtn del" onclick="event.stopPropagation();deleteFinEntry('${e.id}')">Delete</button>
      </div>
    </div>
    <div id="fin-item-${e.id}" class="fin-item-expand" style="padding:10px 14px;background:var(--bg);border-bottom:1px solid var(--border)">${expandBody}</div>`;

    return {cardHtml, rowHtml};
  });

  if(cardGrid){
    if(_finGroupBy){
      // 2. Group by person
      const groups={};
      rendered.forEach((r,i)=>{
        const p=items[i].person;
        if(!groups[p]) groups[p]=[];
        groups[p].push({r,e:items[i]});
      });
      const active = items.filter(e=>finStatus(e)!=='settled');
      const settled = items.filter(e=>finStatus(e)==='settled');

      let html='';
      Object.entries(groups).forEach(([person,entries])=>{
        const pendingAmt = entries.filter(({e})=>finStatus(e)!=='settled').reduce((s,{e})=>s+finRemaining(e),0);
        const net = entries.reduce(({e:en})=>en.type==='gave'?finRemaining(en):-finRemaining(en),0);
        const gKey='g'+person.replace(/\W/g,'');
        const balCls=pendingAmt>0?'pos':'pos';
        html+=`<div class="fin-group-hdr" onclick="document.getElementById('fgb-${gKey}').classList.toggle('collapsed');this.querySelector('.fin-group-chevron').classList.toggle('collapsed')">
          <span class="fin-group-chevron">▼</span>
          <span class="fin-group-name">${esc(person)}</span>
          <span class="fin-group-bal ${balCls}">${pendingAmt>0?finRupee(pendingAmt)+' pending':'✅ Settled'}</span>
          <span class="fin-group-count">${entries.length}</span>
        </div>
        <div class="fin-group-body fin-grid" id="fgb-${gKey}">
          ${entries.map(({r})=>r.cardHtml).join('')}
        </div>`;
      });
      cardGrid.innerHTML=html;
    } else {
      // 8. Separate active and settled sections
      const activeItems   = rendered.filter((_,i)=>finStatus(items[i])!=='settled');
      const settledItems  = rendered.filter((_,i)=>finStatus(items[i])==='settled');
      let html = activeItems.map(r=>r.cardHtml).join('');
      if(settledItems.length){
        html+=`<div class="fin-settled-section" style="grid-column:1/-1">
          <div class="fin-settled-hdr" onclick="finToggleSettled('main')">
            <span class="fin-group-chevron" id="fin-settled-chev-main">▼</span>
            <span style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)">Settled (${settledItems.length})</span>
          </div>
          <div class="fin-group-body fin-grid fin-settled-body" id="fin-settled-body-main">
            ${settledItems.map(r=>r.cardHtml).join('')}
          </div>
        </div>`;
      }
      cardGrid.innerHTML=html;
    }
  }
  if(listBox)  listBox.innerHTML  = rendered.map(r=>r.rowHtml).join('');
}
let ROUTINE_LOGS = [];
const RT_COLORS = {blue:'#3b5bdb',green:'#059669',purple:'#7c3aed',yellow:'#d97706',red:'#dc2626'};

function todayStr(){
  return new Date().toISOString().slice(0,10);
}
function todayDayName(){
  return new Date().toLocaleDateString('en-US',{weekday:'short'}); // Mon,Tue...
}

function loadRoutines(){
  ROUTINES     = DATA.routines      || [];
  ROUTINE_LOGS = DATA.routine_logs  || [];
  updateRoutineCount();
}

function updateRoutineCount(){
  const el = document.getElementById('nav-routine-count');
  if(el){
    const total = ROUTINES.reduce((a,r)=>a+(r.tasks||[]).length,0);
    el.textContent = total;
  }
}

async function saveRoutines(){
  DATA.routines     = ROUTINES;
  DATA.routine_logs = ROUTINE_LOGS;
  updateRoutineCount();
  await saveToGitHub();
}

/* -- TASK VISIBILITY ------------------------ */
function isTaskForToday(task){
  if(task.frequency === 'daily') return true;
  if(task.frequency === 'weekly'){
    const today = todayDayName(); // e.g. "Fri"
    return (task.days||[]).includes(today);
  }
  return false;
}

function isTaskDoneToday(taskId){
  const today = todayStr();
  return ROUTINE_LOGS.some(l=>l.date===today && l.task_id===taskId && l.done);
}

function getWeekCount(taskId){
  // how many days in the last 7 days was this task done
  const now = new Date();
  let count = 0;
  for(let i=0;i<7;i++){
    const d = new Date(now);
    d.setDate(d.getDate()-i);
    const ds = d.toISOString().slice(0,10);
    if(ROUTINE_LOGS.some(l=>l.date===ds && l.task_id===taskId && l.done)) count++;
  }
  return count;
}

/* -- TODAY'S CHECKLIST ---------------------- */
function renderTodayChecklist(){
  const today = todayStr();
  const label = document.getElementById('rt-today-label');
  if(label){
    const fmt = new Date().toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric',year:'numeric'});
    label.textContent = 'Today · '+fmt;
  }

  let totalToday=0, doneToday=0;
  const container = document.getElementById('rt-checklist');
  if(!container) return;

  // If no GitHub token yet, show setup message
  const cfg = getConfig();
  if(!cfg.token){
    container.innerHTML=`<div style="text-align:center;padding:60px 20px;color:#8898c0">
      <div style="font-size:40px;opacity:.3">🔗</div>
      <p style="font-size:15px;font-weight:700;color:#1a2040;margin-top:12px">Connect GitHub first</p>
      <p style="font-size:13px;margin-top:6px">Click <strong>⚙️ Settings</strong> in the sidebar to connect your GitHub account</p>
    </div>`;
    updateProgress(0,0);
    return;
  }

  if(!ROUTINES || !ROUTINES.length){
    container.innerHTML=`<div style="text-align:center;padding:60px 20px;color:#8898c0">
      <div style="font-size:48px;opacity:.25">🔁</div>
      <p style="font-size:16px;font-weight:700;color:#1a2040;margin-top:12px">No routines set up yet</p>
      <p style="font-size:13px;color:#8898c0;margin-top:6px">Click <strong>⚙️ Manage Routines</strong> above to create your first routine</p>
      <button class="btn" style="margin-top:16px" onclick="showRoutineView('manage')">⚙️ Set Up Routines</button>
    </div>`;
    updateProgress(0,0);
    return;
  }

  let html = '';
  ROUTINES.forEach(group=>{
    const todayTasks = (group.tasks||[]).filter(isTaskForToday);
    if(!todayTasks.length) return;
    const doneTasks = todayTasks.filter(t=>isTaskDoneToday(t.id));
    totalToday += todayTasks.length;
    doneToday  += doneTasks.length;

    const colorClass = 'c-'+(group.color||'blue');
    const pct = todayTasks.length ? Math.round((doneTasks.length/todayTasks.length)*100) : 0;

    html += `<div class="rt-group ${colorClass}" id="rtg-${group.id}">
      <div class="rt-group-header" onclick="toggleGroup('${group.id}')">
        <span class="rt-group-icon">${group.icon||'🔁'}</span>
        <span class="rt-group-name">${esc(group.name)}</span>
        <span class="rt-group-progress">${doneTasks.length}/${todayTasks.length} · ${pct}%</span>
        <span class="rt-group-toggle" id="rtgt-${group.id}">▼</span>
      </div>
      <div class="rt-tasks" id="rttasks-${group.id}">`;

    todayTasks.forEach(task=>{
      const done = isTaskDoneToday(task.id);
      const wc   = getWeekCount(task.id);
      const freq = task.frequency==='weekly'
        ? `📅 ${(task.days||[]).join(',')}` : '🔁 Daily';
      html += `<div class="rt-task-row${done?' done':''}" onclick="toggleTask('${task.id}','${group.id}')">
        <div class="rt-checkbox">${done?'✓':''}</div>
        <div class="rt-task-info">
          <div class="rt-task-name">${esc(task.name)}</div>
          <div class="rt-task-meta">
            ${task.time?`<span class="rt-task-time">⏰ ${task.time}</span>`:''}
            <span class="rt-task-freq">${freq}</span>
          </div>
        </div>
        <span class="rt-week-count">${wc}/7 this week</span>
      </div>`;
    });

    html += `</div></div>`;
  });

  container.innerHTML = html || `<div style="text-align:center;padding:40px;color:#8898c0;font-size:13px">
    No tasks scheduled for today</div>`;
  updateProgress(doneToday, totalToday);
}

function updateProgress(done, total){
  const pct = total ? Math.round((done/total)*100) : 0;
  const fill = document.getElementById('rt-progress-fill');
  const label = document.getElementById('rt-progress-pct');
  if(fill)  fill.style.width = pct+'%';
  if(fill)  fill.style.background = pct===100 ? '#059669' : '#3b5bdb';
  if(label) label.textContent = pct===100 ? '🎉 All done!' : `${done}/${total} done today`;
  if(label) label.style.color = pct===100 ? '#059669' : '#3b5bdb';
}

function toggleGroup(groupId){
  const tasks = document.getElementById('rttasks-'+groupId);
  const icon  = document.getElementById('rtgt-'+groupId);
  if(!tasks) return;
  const hidden = tasks.style.display==='none';
  tasks.style.display = hidden ? '' : 'none';
  if(icon) icon.textContent = hidden ? '▼' : '▶';
}

async function toggleTask(taskId, groupId){
  const today = todayStr();
  const idx = ROUTINE_LOGS.findIndex(l=>l.date===today && l.task_id===taskId);
  if(idx>=0){
    ROUTINE_LOGS[idx].done = !ROUTINE_LOGS[idx].done;
  } else {
    ROUTINE_LOGS.push({date:today, task_id:taskId, done:true});
  }
  // trim old logs (keep last 30 days)
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate()-30);
  ROUTINE_LOGS = ROUTINE_LOGS.filter(l=>new Date(l.date)>=cutoff);
  renderTodayChecklist();
  await saveRoutines();
}

/* -- MANAGE VIEW ---------------------------- */
function renderManageView(){
  const container = document.getElementById('rt-groups-list');
  if(!container) return;
  if(!ROUTINES.length){
    container.innerHTML=`<div style="text-align:center;padding:48px;color:#8898c0;font-size:13px">
      No routines yet. Click <strong>+ New Routine</strong> to get started.</div>`;
    return;
  }
  container.innerHTML = ROUTINES.map(group=>`
    <div class="rt-manage-group">
      <div class="rt-manage-group-header">
        <span style="font-size:18px">${group.icon||'🔁'}</span>
        <span class="rt-manage-group-name">${esc(group.name)}</span>
        <button class="rt-mg-btn" onclick="openRoutineGroupModal('${group.id}')">Edit</button>
        <button class="rt-mg-btn del" onclick="deleteRoutineGroup('${group.id}')">Delete</button>
      </div>
      <div class="rt-manage-tasks">
        ${(group.tasks||[]).map(t=>`
        <div class="rt-manage-task-row">
          <div class="rt-mtr-info">
            <div class="rt-mtr-name">${esc(t.name)}</div>
            <div class="rt-mtr-meta">${t.frequency==='weekly'?'📅 '+((t.days||[]).join(', ')):'🔁 Daily'}${t.time?' · ⏰ '+t.time:''}</div>
          </div>
          <button class="rt-mg-btn" onclick="openRoutineTaskModal('${group.id}','${t.id}')">Edit</button>
          <button class="rt-mg-btn del" onclick="deleteRoutineTask('${group.id}','${t.id}')">Remove</button>
        </div>`).join('')}
      </div>
      <div class="rt-add-task-row">
        <button class="rt-add-task-btn" onclick="openRoutineTaskModal('${group.id}')">+ Add task to ${esc(group.name)}</button>
      </div>
    </div>`).join('');
}

function showRoutineView(view){
  document.getElementById('rt-today-view').style.display  = view==='today'   ? '' : 'none';
  document.getElementById('rt-manage-view').style.display = view==='manage'  ? '' : 'none';
  document.getElementById('rt-back-btn').style.display    = view==='manage'  ? ''  : 'none';
  if(view==='today')  renderTodayChecklist();
  if(view==='manage') renderManageView();
}

/* -- GROUP MODAL ---------------------------- */
let _editGroupId = null;
function openRoutineGroupModal(groupId){
  _editGroupId = groupId||null;
  const existing = groupId ? ROUTINES.find(r=>r.id===groupId) : null;
  document.getElementById('rt-group-modal-title').textContent = existing ? 'Edit Routine' : 'New Routine';
  document.getElementById('rt-group-edit-id').value = groupId||'';
  document.getElementById('rt-group-name').value   = existing?.name  || '';
  document.getElementById('rt-group-color').value  = existing?.color || 'blue';
  document.getElementById('rt-group-icon').value   = existing?.icon  || '🌅';
  document.querySelectorAll('.rt-icon-opt').forEach(el=>{
    el.classList.toggle('selected', el.textContent===(existing?.icon||'🌅'));
  });
  document.getElementById('rt-group-modal').classList.add('open');
}
function closeRoutineGroupModal(){ document.getElementById('rt-group-modal').classList.remove('open'); }

function selectIcon(el, icon){
  document.querySelectorAll('.rt-icon-opt').forEach(e=>e.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById('rt-group-icon').value = icon;
}

async function saveRoutineGroup(){
  const name = document.getElementById('rt-group-name').value.trim();
  if(!name){ toast('Routine name required','error'); return; }
  const id  = document.getElementById('rt-group-edit-id').value;
  const grp = {
    id:    id || 'rt'+Date.now().toString(36),
    name,
    icon:  document.getElementById('rt-group-icon').value || '🌅',
    color: document.getElementById('rt-group-color').value || 'blue',
    tasks: id ? (ROUTINES.find(r=>r.id===id)?.tasks||[]) : []
  };
  if(id){ ROUTINES = ROUTINES.map(r=>r.id===id?grp:r); }
  else  { ROUTINES.push(grp); }
  closeRoutineGroupModal();
  renderManageView();
  await saveRoutines();
  toast('Routine saved ✓','success');
}

async function deleteRoutineGroup(id){
  if(!confirm('Delete this routine and all its tasks?')) return;
  ROUTINES = ROUTINES.filter(r=>r.id!==id);
  renderManageView();
  await saveRoutines();
  toast('Routine deleted','success');
}

/* -- TASK MODAL ----------------------------- */
function openRoutineTaskModal(groupId, taskId){
  const group    = ROUTINES.find(r=>r.id===groupId);
  const existing = taskId ? (group?.tasks||[]).find(t=>t.id===taskId) : null;
  document.getElementById('rt-task-modal-title').textContent = existing ? 'Edit Task' : 'Add Task';
  document.getElementById('rt-task-edit-id').value   = taskId  || '';
  document.getElementById('rt-task-group-id').value  = groupId || '';
  document.getElementById('rt-task-name').value      = existing?.name  || '';
  document.getElementById('rt-task-time').value      = existing?.time  || '';
  document.getElementById('rt-task-freq').value      = existing?.frequency || 'daily';
  // reset day selections
  document.querySelectorAll('.rt-day-opt').forEach(el=>{
    el.classList.toggle('selected', (existing?.days||[]).includes(el.dataset.day));
  });
  toggleWeekdays();
  document.getElementById('rt-task-modal').classList.add('open');
}
function closeRoutineTaskModal(){ document.getElementById('rt-task-modal').classList.remove('open'); }

function toggleWeekdays(){
  const freq = document.getElementById('rt-task-freq').value;
  document.getElementById('rt-weekdays-row').style.display = freq==='weekly' ? '' : 'none';
}

// day picker toggle
document.addEventListener('click', e=>{
  if(e.target.classList.contains('rt-day-opt')){
    e.target.classList.toggle('selected');
  }
});

async function saveRoutineTask(){
  const name = document.getElementById('rt-task-name').value.trim();
  if(!name){ toast('Task name required','error'); return; }
  const groupId  = document.getElementById('rt-task-group-id').value;
  const taskId   = document.getElementById('rt-task-edit-id').value;
  const freq     = document.getElementById('rt-task-freq').value;
  const selDays  = [...document.querySelectorAll('.rt-day-opt.selected')].map(e=>e.dataset.day);
  const task = {
    id:        taskId || 'tk'+Date.now().toString(36),
    name,
    time:      document.getElementById('rt-task-time').value,
    frequency: freq,
    days:      freq==='weekly' ? selDays : []
  };
  const group = ROUTINES.find(r=>r.id===groupId);
  if(!group){ toast('Routine not found','error'); return; }
  if(taskId){ group.tasks = group.tasks.map(t=>t.id===taskId?task:t); }
  else      { group.tasks = [...(group.tasks||[]), task]; }
  closeRoutineTaskModal();
  renderManageView();
  await saveRoutines();
  toast('Task saved ✓','success');
}

async function deleteRoutineTask(groupId, taskId){
  if(!confirm('Remove this task?')) return;
  const group = ROUTINES.find(r=>r.id===groupId);
  if(group) group.tasks = group.tasks.filter(t=>t.id!==taskId);
  renderManageView();
  await saveRoutines();
  toast('Task removed','success');
}

/* -- INIT ---------------------------------------- */
window.addEventListener('DOMContentLoaded',()=>{
  const savedTheme=localStorage.getItem('mynotes_theme')||'cream';
  applyTheme(savedTheme);

  // restore saved view preferences
  ['rem','notes'].forEach(sec=>{
    const saved=localStorage.getItem('view_'+sec)||'card';
    setView(sec, saved);
  });

  initSticky();
  initJournalListeners();
  startClock();
  // Auto-refresh SHA every 30 min to prevent stale conflicts
  setInterval(()=>{ if(getConfig().token) refreshSHA(); }, 30*60*1000);

  const c=getConfig();
  if(!c.token){openSettings();renderAll();}
  else loadFromGitHub();
});
</script>
</body>
</html>"""

def main():
    hour_opts = ''.join(f'<option value="{i:02d}">{i:02d}</option>' for i in range(24))
    min_opts  = ''.join(f'<option value="{i:02d}">{i:02d}</option>' for i in range(60))
    html = HTML.replace('HOUR_OPTIONS_PLACEHOLDER', hour_opts)
    html = html.replace('MIN_OPTIONS_PLACEHOLDER',  min_opts)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML generated → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
