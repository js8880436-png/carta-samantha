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
  const r = await fetch(URL + "/rest/v1/" + path, {
    ...opt,
    headers: {
      apikey: KEY,
      Authorization: "Bearer " + KEY,
      "Content-Type": "application/json",
      ...(opt.headers || {})
    }
  });
  if (!r.ok) throw Error(await r.text());
  return r.status === 204 ? null : r.json();
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
    while (q.length) {
      c = code();
      q = await api("letters?select=id&code=eq." + c);
    }
    await api("letters", {
      method: "POST",
      body: JSON.stringify({ code: c, message: msg, media })
    });
    $("code").textContent = c;
    show("created");
  } catch (e) {
    console.error(e);
    st.textContent = "Erro: " + e.message;  // ← ALTERAÇÃO AQUI
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
    if (!rows.length) {
      st.textContent = "Carta não encontrada.";
      return;
    }
    $("finalMessage").textContent = rows[0].message;
    $("finalMedia").innerHTML = (rows[0].media || []).map(x => "<img src='" + x + "'>").join("");
    show("letter");
  } catch (e) {
    console.error(e);
    st.textContent = "Erro ao buscar a carta.";
  }
}

async function copyCode() {
  try {
    await navigator.clipboard.writeText($("code").textContent);
  } catch (e) {}
}
