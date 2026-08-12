const CODE="JAPONESA", K={m:"carta_message",f:"carta_font",s:"carta_sealed",media:"carta_media"};const $=id=>document.getElementById(id);
function show(id){document.querySelectorAll(".screen").forEach(x=>x.classList.remove("active"));$(id).classList.add("active")}
function save(){localStorage.setItem(K.m,$("message").value);localStorage.setItem(K.f,$("message").style.fontSize||"24px")}
function render(){let g=$("mediaGrid");g.innerHTML="";let a=[];try{a=JSON.parse(localStorage.getItem(K.media)||"[]")}catch{}a.forEach(x=>{let e=document.createElement(x.type.startsWith("video/")?"video":"img");e.src=x.data;if(e.tagName==="VIDEO"){e.controls=true;e.playsInline=true}g.appendChild(e)})}
$("message").value=localStorage.getItem(K.m)||"";$("message").style.fontSize=localStorage.getItem(K.f)||"24px";
document.querySelectorAll("[data-size]").forEach(b=>b.onclick=()=>{$("message").style.fontSize=b.dataset.size+"px";localStorage.setItem(K.f,b.dataset.size+"px")});
$("message").oninput=save;$("galleryBtn").onclick=()=>{render();show("gallery")};$("backCreator").onclick=()=>show("creator");
$("chooseMedia").onclick=()=>$("mediaInput").click();
$("mediaInput").onchange=async e=>{let a=[];try{a=JSON.parse(localStorage.getItem(K.media)||"[]")}catch{}for(const f of e.target.files){if(!/^(image|video)\//.test(f.type))continue;if(f.size>6*1024*1024){alert("Arquivo muito grande: "+f.name);continue}let d=await new Promise((ok,no)=>{let r=new FileReader();r.onload=()=>ok(r.result);r.onerror=no;r.readAsDataURL(f)});a.push({name:f.name,type:f.type,data:d})}try{localStorage.setItem(K.media,JSON.stringify(a));render()}catch{alert("Sem espaço no armazenamento local. Use arquivos menores.")}e.target.value=""};
$("sealBtn").onclick=()=>{if(!$("message").value.trim()){$("creatorStatus").textContent="Escreva a carta antes de selá-la.";return}save();localStorage.setItem(K.s,"1");show("sealed")};
$("continueBtn").onclick=()=>show("code");
$("openBtn").onclick=()=>{if($("codeInput").value.trim().toUpperCase()!==CODE){$("codeStatus").textContent="Código incorreto.";return}$("finalMessage").textContent=localStorage.getItem(K.m)||"";show("letter")};
$("letterGalleryBtn").onclick=()=>{render();show("gallery")};