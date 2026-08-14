const URL = window.SUPABASE_URL,
  KEY = window.SUPABASE_ANON_KEY;
let media = [];
const $ = id => document.getElementById(id);

function show(id) {
  document.querySelectorAll(".screen").forEach(x => x.classList.remove("active"));
  $(id).classList.add("active");
}

function configured() {
  return URL && KEY && !URL.includes("COLE_A_") && !KEY.includes("COLE_A_");
}

function font(n) {
  $("message").style.fontSize = n + "px";
}

function code() {
  let s = "",
    c = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  for (let i = 0; i < 6; i++) s += c[Math.floor(Math.random() * c.length)];
  return s;
}

async function api(path, opt = {}) {
  const url = URL + "/rest/v1/" + path;
  console.log("🔗 Requisição para:", url);
  const r = await fetch(url, {
    ...opt,
    headers: {
      apikey: KEY,
      Authorization: "Bearer " + KEY,
      "Content-Type": "application/json",
      ...(opt.headers || {})
    }
  });

  const text = await r.text();
  console.log("📡 Status:", r.status);
  console.log("📄 Resposta (texto):", text);

  if (!r.ok) {
    throw new Error("HTTP " + r.status + ": " + text);
  }

  if (r.status === 204) return null;
  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch (e) {
    console.warn("⚠️ Resposta não é JSON:", text);
    return text;
  }
}

$("photos").onchange = async e => {
  media = [];
  for (const f of e.target.files) {
    if (f.size > 3e6) continue;
    media.push(await new Promise((ok, no) => {
      const r = new FileReader();
      r.onload = () => ok(r.result);
      r.onerror = no;
      r.readAsDataURL(f);
    }));
  }
  $("preview").innerHTML = media.map(x => "<img src='" + x + "'>").join("");
};

async function createLetter() {
  const st = $("createStatus");
  st.textContent = "";
  if (!configured()) {
    st.textContent = "Falta configurar o Supabase no config.js.";
    return;
  }
  const msg = $("message").value.trim();
  if (!msg) {
    st.textContent = "Escreva a carta primeiro.";
    return;
  }
  try {
    let c = code(),
      q = await api("letters?select=id&code=eq." + c);
    while (Array.isArray(q) && q.length) {
      c = code();
      q = await api("letters?select=id&code=eq." + c);
    }
    const body = JSON.stringify({ code: c, message: msg, media });
    console.log("📤 Enviando:", body);
    await api("letters", {
      method: "POST",
      body: body
    });
    $("code").textContent = c;
    show("created");
  } catch (e) {
    console.error("❌ Erro:", e);
    st.textContent = "Erro: " + e.message;
  }
}

async function openLetter() {
  const st = $("receiveStatus");
  st.textContent = "";
  if (!configured()) {
    st.textContent = "Falta configurar o Supabase no config.js.";
    return;
  }
  const c = $("codeInput").value.trim().toUpperCase();
  if (!c) {
    st.textContent = "Digite o código.";
    return;
  }
  try {
    const rows = await api("letters?select=message,media&code=eq." + encodeURIComponent(c) + "&limit=1");
    if (!rows || (Array.isArray(rows) && rows.length === 0)) {
      st.textContent = "Carta não encontrada.";
      return;
    }
    const first = Array.isArray(rows) ? rows[0] : rows;
    $("finalMessage").textContent = first.message;
    const medias = first.media || [];
    $("finalMedia").innerHTML = medias.map(x => "<img src='" + x + "'>").join("");
    show("letter");
  } catch (e) {
    console.error(e);
    st.textContent = "Erro ao buscar a carta: " + e.message;
  }
}

async function copyCode() {
  try {
    await navigator.clipboard.writeText($("code").textContent);
  } catch (e) {}
}
