const INVITE_URL   = "https://discord.com/oauth2/authorize?client_id=1536795505911398593";
const BOT_ICON_URL = document.body.dataset.iconUrl || "templates/icon.png";

const MEASURES = ["minutes", "hours", "days"];
const COMMANDS = [
  { name: "ping",     cat: "utility",    desc: "shows the bot ping", params: [] },
  { name: "lock",     cat: "channels",   desc: "locks the chat where the command was used", params: [] },
  { name: "unlock",   cat: "channels",   desc: "unlocks the chat where the command was used", params: [] },
  { name: "ban",      cat: "moderation", desc: "ban a user", params: [{ n: "user" }, { n: "reason" }] },
  { name: "unban",    cat: "moderation", desc: "unban a user", params: [{ n: "user" }, { n: "reason" }] },
  { name: "ban_list", cat: "moderation", desc: "see the list of users banned", params: [] },
  { name: "timeout",  cat: "moderation", desc: "set a timeout for a user (max 28 days)",
    params: [{ n: "user" }, { n: "time" }, { n: "time_measurement", choices: MEASURES }, { n: "reason" }] },
  { name: "embed",    cat: "web", desc: "generates a link where the user can customize and create an embed", params: [],
    note: "Sends you a private link, valid for 60 minutes." },
  { name: "ticket",   cat: "web", desc: "generates a link where the user can customize and create a ticket system", params: [],
    note: "Sends you a private link, valid for 60 minutes." },
];

function botIcon() {
  const img = document.createElement("img");
  img.className = "icon"; img.alt = ""; img.src = BOT_ICON_URL;
  img.onerror = () => { const s = document.createElement("span"); s.className = "logo-mark"; img.replaceWith(s); };
  return img;
}
document.querySelectorAll("[data-bot-icon]").forEach(el => el.replaceWith(botIcon()));
document.querySelectorAll("[data-invite]").forEach(a => a.href = INVITE_URL);

const list = document.getElementById("cmdList");
COMMANDS.forEach(c => {
  const li = document.createElement("li");
  li.className = "cmd"; li.dataset.cat = c.cat;
  const params = c.params.map(p =>
    `<span class="cmd-param">${p.n}${p.choices ? `<i>${p.choices.join(" / ")}</i>` : ""}</span>`).join("");
  li.innerHTML = `<div class="cmd-line"><span class="cmd-name">/${c.name}</span>${params}</div>
    <p class="cmd-desc">${c.desc}</p>${c.note ? `<p class="cmd-note">${c.note}</p>` : ""}`;
  list.appendChild(li);
});
document.querySelectorAll(".chip").forEach(chip => chip.addEventListener("click", () => {
  document.querySelectorAll(".chip").forEach(c => {
    c.classList.toggle("active", c === chip); c.setAttribute("aria-selected", c === chip);
  });
  const f = chip.dataset.filter;
  list.querySelectorAll(".cmd").forEach(li => li.hidden = !(f === "all" || li.dataset.cat === f));
}));

const MEMBERS = [
  { n: "Luccadark", c: "#C8FF00" }, { n: "n4nja", c: "#ffffff" }, { n: "DarkBot", c: "#8a8a8a" },
];
const SCENES = [
  { cmd: "lock", reply: "the chat was <b>locked</b>,<br>you can use <b>/unlock</b> to unlock it." },
  { cmd: "ban", values: { user: "@n4nja", reason: "spam" },
    reply: "The User @n4nja was banned by reason <b>'spam'</b>,<br>if you want to unban him, use the command <b>/unban</b>" },
  { cmd: "timeout", values: { user: "@n4nja", time: "10", time_measurement: "minutes", reason: "flood" },
    reply: "The User @n4nja suffered a timeout of <b>10 minutes</b> by reason <b>'flood'</b>" },
  { cmd: "ping", reply: "🏓 pong! <b>42ms</b>" },
];

const $ = id => document.getElementById(id);
const chat = $("chat"), typed = $("typed"), chip = $("cmdChip"), paramsEl = $("params"), popup = $("popup");
const fast = matchMedia("(prefers-reduced-motion: reduce)").matches;
const wait = ms => new Promise(r => setTimeout(r, fast ? ms / 4 : ms));

function showPopup(title, rows, selIndex) {
  popup.innerHTML = `<h4>${title}</h4>` + rows.map((r, i) =>
    `<div class="opt${i === selIndex ? " sel" : ""}">${r}</div>`).join("");
  popup.hidden = false;
}
const hidePopup = () => popup.hidden = true;

async function typeInto(el, text, speed = 70) {
  for (const ch of text) { el.textContent += ch; await wait(speed); }
}

async function play(s) {
  const def = COMMANDS.find(c => c.name === s.cmd);
  typed.textContent = "/";
  const stub = s.cmd.slice(0, 2);
  for (const ch of stub) {
    typed.textContent += ch; await wait(120);
    const m = COMMANDS.filter(c => c.name.startsWith(typed.textContent.slice(1)) && c.cat !== "web");
    const idx = Math.max(0, m.findIndex(c => c.name === s.cmd));
    showPopup("Commands", m.map(c => `<b>/${c.name}</b><small>${c.desc.slice(0, 28)}</small>`), idx);
  }
  await wait(700); hidePopup();
  typed.textContent = ""; chip.textContent = "/" + s.cmd; chip.hidden = false;
  paramsEl.innerHTML = def.params.map(p => `<span class="param" data-p="${p.n}"><b>${p.n}</b><span class="pv"></span></span>`).join("");
  await wait(600);
  for (const p of def.params) {
    const box = paramsEl.querySelector(`[data-p="${p.n}"]`), pv = box.querySelector(".pv");
    box.classList.add("on"); await wait(350);
    if (p.n === "user") {
      showPopup("Members", MEMBERS.map(m => `<span class="dot" style="background:${m.c}">${m.n[0]}</span>${m.n}`), 0);
      await wait(600); showPopup("Members", MEMBERS.map(m => `<span class="dot" style="background:${m.c}">${m.n[0]}</span>${m.n}`), 1);
      await wait(800); hidePopup();
    } else if (p.choices) {
      showPopup(p.n, p.choices.map(x => x), 0); await wait(600);
      showPopup(p.n, p.choices.map(x => x), p.choices.indexOf(s.values[p.n])); await wait(700); hidePopup();
    }
    if (p.n === "user" || p.choices) pv.textContent = s.values[p.n];
    else await typeInto(pv, s.values[p.n]);
    box.classList.remove("on"); await wait(250);
  }
  await wait(500);
  chip.hidden = true; paramsEl.innerHTML = ""; typed.textContent = "";
  const d = document.createElement("div");
  d.className = "msg";
  d.innerHTML = `<div class="av" data-av></div><div><span class="who">DarkBot<em>BOT</em></span>
    <span class="used">Luccadark used /${s.cmd}</span><span class="what">${s.reply}</span>
    <span class="only">Only you can see this</span></div>`;
  d.querySelector("[data-av]").appendChild(botIcon());
  chat.replaceChildren(d);
  await wait(3200);
}

(async function loop() { for (let i = 0; ; i++) await play(SCENES[i % SCENES.length]); })();