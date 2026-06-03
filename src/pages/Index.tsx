import { useState } from "react";
import Icon from "@/components/ui/icon";

const APPLY_URL = "https://functions.poehali.dev/459af168-6b2e-4396-89ba-5a63b80d9bd8";
const APPLICATIONS_URL = "https://functions.poehali.dev/9dd1f61b-eb31-4510-bb6d-f17cc8ca27c0";
const DECIDE_URL = "https://functions.poehali.dev/dbca4200-dfc2-4bc5-b24b-1a84c0fb17ba";

type Tab = "about" | "rules" | "socials" | "apply" | "admin";

interface Application {
  id: number;
  nickname: string;
  email: string;
  status: string;
  created_at: string;
}

const RULES = [
  "Запрещены читы, моды дающие преимущество и любой вид гриферства.",
  "Уважай других игроков — оскорбления и токсичность недопустимы.",
  "Не строй базы ближе 500 блоков от чужих построек без разрешения.",
  "Запрещена торговля за реальные деньги между игроками.",
  "Дюпы и баги движка — под запретом. О найденных сообщай администрации.",
  "Реклама других серверов и ресурсов запрещена.",
  "Администрация вправе выдать бан без объяснений при грубом нарушении.",
];

function BgDecor() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      <div className="absolute -top-32 -left-32 w-[600px] h-[600px] rounded-full bg-blue-200/40 blur-3xl" />
      <div className="absolute top-1/3 -right-24 w-[400px] h-[400px] rounded-full bg-yellow-200/35 blur-3xl" />
      <div className="absolute bottom-0 left-1/3 w-[500px] h-[300px] rounded-full bg-blue-100/50 blur-2xl" />
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%231a4d8f' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />
    </div>
  );
}

function Header({ active, onTab }: { active: Tab; onTab: (t: Tab) => void }) {
  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: "about",   label: "О сервере",    icon: "Server" },
    { id: "rules",   label: "Правила",      icon: "ScrollText" },
    { id: "socials", label: "Соц. сети",    icon: "Share2" },
    { id: "apply",   label: "Подать заявку",icon: "Send" },
  ];

  return (
    <header className="sticky top-0 z-40 glass border-b border-white/60 shadow-sm">
      <div className="max-w-5xl mx-auto px-4 py-3 flex flex-col sm:flex-row items-center gap-3 sm:gap-0 justify-between">
        <button
          onClick={() => onTab("about")}
          className="flex items-center gap-2 group"
        >
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center shadow">
            <span className="text-white font-montserrat font-black text-lg leading-none">S</span>
          </div>
          <span className="font-montserrat font-black text-xl text-blue-800 tracking-tight">Spirit</span>
        </button>

        <nav className="flex gap-1 flex-wrap justify-center">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => onTab(t.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-montserrat font-600 transition-all duration-200
                ${active === t.id
                  ? "bg-blue-600 text-white shadow"
                  : "text-blue-900 hover:bg-blue-100"
                }`}
            >
              <Icon name={t.icon} size={14} />
              {t.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
}

function AboutTab({ onTab }: { onTab: (t: Tab) => void }) {
  const stats = [
    { icon: "Lock", label: "Тип", value: "Приватный" },
    { icon: "Layers", label: "Версия", value: "1.21.1" },
    { icon: "Map", label: "Размер карты", value: "6 000 × 6 000" },
    { icon: "Users", label: "Сообщество", value: "Дружелюбное" },
  ];

  return (
    <div className="animate-fade-in">
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 bg-yellow-100 text-yellow-800 px-4 py-1.5 rounded-full text-sm font-montserrat font-600 mb-5 border border-yellow-200">
          <Icon name="Star" size={14} />
          Приватный сервер
        </div>
        <h1 className="font-montserrat font-black text-5xl sm:text-6xl text-blue-900 mb-4 leading-tight">
          Добро пожаловать<br />
          <span className="text-blue-500">на Spirit</span>
        </h1>
        <p className="text-blue-700/70 text-lg max-w-xl mx-auto font-golos leading-relaxed">
          Уютный приватный сервер для тех, кто ценит спокойную игру,
          честное сообщество и атмосферу настоящего выживания.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
        {stats.map((s, i) => (
          <div
            key={s.label}
            className={`glass rounded-2xl p-5 text-center animate-fade-in delay-${(i + 1) * 100}`}
          >
            <div className="w-10 h-10 rounded-xl bg-blue-600/10 flex items-center justify-center mx-auto mb-3">
              <Icon name={s.icon} size={20} className="text-blue-600" />
            </div>
            <p className="text-xs text-blue-500 font-montserrat font-600 uppercase tracking-wider mb-1">{s.label}</p>
            <p className="font-montserrat font-800 text-blue-900 text-sm">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="glass rounded-2xl p-7 text-center animate-fade-in delay-500">
        <p className="font-montserrat font-700 text-blue-900 text-lg mb-2">Хочешь попасть на сервер?</p>
        <p className="text-blue-600/70 mb-5 font-golos">Подай заявку — мы рассматриваем каждого игрока индивидуально.</p>
        <button
          onClick={() => onTab("apply")}
          className="spirit-btn-primary shadow-md"
        >
          <Icon name="Send" size={16} />
          Подать заявку
        </button>
      </div>
    </div>
  );
}

function RulesTab() {
  return (
    <div className="animate-fade-in">
      <div className="text-center mb-10">
        <h2 className="font-montserrat font-black text-4xl text-blue-900 mb-3">Правила сервера</h2>
        <p className="text-blue-600/70 font-golos">Соблюдение правил обязательно для всех игроков</p>
      </div>

      <div className="space-y-3 max-w-2xl mx-auto">
        {RULES.map((rule, i) => (
          <div
            key={i}
            className={`glass rounded-xl p-5 flex gap-4 items-start animate-fade-in`}
            style={{ animationDelay: `${i * 0.07}s` }}
          >
            <div className="w-8 h-8 rounded-lg bg-yellow-400 flex items-center justify-center shrink-0 shadow-sm">
              <span className="font-montserrat font-black text-sm text-yellow-900">{i + 1}</span>
            </div>
            <p className="text-blue-900 font-golos leading-relaxed">{rule}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 glass rounded-2xl p-5 text-center max-w-2xl mx-auto border border-yellow-200/60 bg-yellow-50/40">
        <Icon name="AlertTriangle" size={20} className="text-yellow-600 mx-auto mb-2" />
        <p className="text-yellow-800 font-golos text-sm">
          Незнание правил не освобождает от ответственности. При нарушении — бан без предупреждения.
        </p>
      </div>
    </div>
  );
}

function SocialsTab() {
  const socials = [
    {
      icon: "Send",
      label: "Telegram",
      handle: "@fqylov",
      desc: "Написать администратору напрямую",
      href: "https://t.me/fqylov",
      color: "bg-blue-500",
    },
    {
      icon: "MessageSquare",
      label: "Discord",
      handle: "discord.gg/J5fcGEEM",
      desc: "Наш сервер Discord — чат, новости, события",
      href: "https://discord.gg/J5fcGEEM",
      color: "bg-indigo-500",
    },
  ];

  return (
    <div className="animate-fade-in">
      <div className="text-center mb-10">
        <h2 className="font-montserrat font-black text-4xl text-blue-900 mb-3">Наши соц. сети</h2>
        <p className="text-blue-600/70 font-golos">Следи за новостями и общайся с сообществом</p>
      </div>

      <div className="grid sm:grid-cols-2 gap-5 max-w-2xl mx-auto">
        {socials.map((s, i) => (
          <a
            key={s.label}
            href={s.href}
            target="_blank"
            rel="noopener noreferrer"
            className={`glass rounded-2xl p-7 flex flex-col items-center text-center gap-4 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 animate-fade-in delay-${(i + 1) * 100}`}
          >
            <div className={`w-14 h-14 rounded-2xl ${s.color} flex items-center justify-center shadow-md`}>
              <Icon name={s.icon} size={28} className="text-white" />
            </div>
            <div>
              <p className="font-montserrat font-800 text-blue-900 text-xl mb-1">{s.label}</p>
              <p className="font-montserrat font-600 text-blue-500 text-sm mb-2">{s.handle}</p>
              <p className="text-blue-700/60 font-golos text-sm">{s.desc}</p>
            </div>
            <div className="flex items-center gap-1.5 text-blue-500 font-montserrat font-600 text-sm">
              Перейти <Icon name="ArrowRight" size={14} />
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

function ApplyTab() {
  const [nickname, setNickname] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!nickname.trim() || !email.trim()) {
      setError("Заполните все поля");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(APPLY_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nickname: nickname.trim(), email: email.trim() }),
      });
      const data = await res.json();
      const parsed = typeof data === "string" ? JSON.parse(data) : data;
      if (parsed.ok) {
        setDone(true);
      } else {
        setError(parsed.error || "Ошибка при отправке");
      }
    } catch {
      setError("Ошибка сети. Попробуй ещё раз.");
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <div className="animate-scale-in flex flex-col items-center text-center py-16">
        <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mb-6 shadow">
          <Icon name="CheckCircle" size={40} className="text-green-500" />
        </div>
        <h2 className="font-montserrat font-black text-3xl text-blue-900 mb-3">Заявка отправлена!</h2>
        <p className="text-blue-600/70 font-golos max-w-sm">
          Мы получили твою заявку и скоро рассмотрим её. Ответ придёт на указанную почту.
        </p>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="text-center mb-10">
        <h2 className="font-montserrat font-black text-4xl text-blue-900 mb-3">Подать заявку</h2>
        <p className="text-blue-600/70 font-golos">Заполни форму — мы рассмотрим и ответим на почту</p>
      </div>

      <form onSubmit={handleSubmit} className="glass rounded-2xl p-8 max-w-md mx-auto flex flex-col gap-5">
        <div>
          <label className="block font-montserrat font-600 text-blue-900 text-sm mb-2">
            Никнейм в Minecraft
          </label>
          <div className="relative">
            <Icon name="Gamepad2" size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-blue-400" />
            <input
              type="text"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              placeholder="YourNickname"
              className="w-full pl-9 pr-4 py-3 rounded-xl border border-blue-200 bg-white/70 focus:outline-none focus:ring-2 focus:ring-blue-400 font-golos text-blue-900 placeholder:text-blue-300 transition"
            />
          </div>
        </div>

        <div>
          <label className="block font-montserrat font-600 text-blue-900 text-sm mb-2">
            Почта Gmail
          </label>
          <div className="relative">
            <Icon name="Mail" size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-blue-400" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@gmail.com"
              className="w-full pl-9 pr-4 py-3 rounded-xl border border-blue-200 bg-white/70 focus:outline-none focus:ring-2 focus:ring-blue-400 font-golos text-blue-900 placeholder:text-blue-300 transition"
            />
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-red-700 text-sm font-golos">
            <Icon name="AlertCircle" size={16} />
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="spirit-btn-primary w-full justify-center text-base shadow disabled:opacity-60"
        >
          {loading ? (
            <><Icon name="Loader2" size={18} className="animate-spin" /> Отправляем...</>
          ) : (
            <><Icon name="Send" size={16} /> Отправить заявку</>
          )}
        </button>

        <p className="text-center text-xs text-blue-400 font-golos">
          После подачи заявки ожидай письмо на указанную почту
        </p>
      </form>
    </div>
  );
}

function AdminTab() {
  const [password, setPassword] = useState("");
  const [authed, setAuthed] = useState(false);
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(false);
  const [deciding, setDeciding] = useState<number | null>(null);
  const [decided, setDecided] = useState<Record<number, string>>({});

  const ADMIN_PASS = "spirit2024admin";

  async function loadApps() {
    setLoading(true);
    try {
      const res = await fetch(APPLICATIONS_URL);
      const data = await res.json();
      const parsed = typeof data === "string" ? JSON.parse(data) : data;
      setApps(parsed.applications || []);
    } finally {
      setLoading(false);
    }
  }

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (password === ADMIN_PASS) {
      setAuthed(true);
      loadApps();
    } else {
      alert("Неверный пароль");
    }
  }

  async function decide(id: number, decision: "accept" | "reject") {
    setDeciding(id);
    try {
      await fetch(DECIDE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, decision }),
      });
      setDecided((prev) => ({ ...prev, [id]: decision }));
    } finally {
      setDeciding(null);
    }
  }

  if (!authed) {
    return (
      <div className="animate-fade-in">
        <div className="text-center mb-10">
          <h2 className="font-montserrat font-black text-4xl text-blue-900 mb-3">Панель администратора</h2>
          <p className="text-blue-600/70 font-golos">Только для администраторов сервера</p>
        </div>
        <form onSubmit={handleLogin} className="glass rounded-2xl p-8 max-w-sm mx-auto flex flex-col gap-4">
          <div className="relative">
            <Icon name="Lock" size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-blue-400" />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Пароль администратора"
              className="w-full pl-9 pr-4 py-3 rounded-xl border border-blue-200 bg-white/70 focus:outline-none focus:ring-2 focus:ring-blue-400 font-golos text-blue-900 placeholder:text-blue-300"
            />
          </div>
          <button type="submit" className="spirit-btn-primary w-full justify-center">
            <Icon name="LogIn" size={16} /> Войти
          </button>
        </form>
      </div>
    );
  }

  const pending = apps.filter((a) => a.status === "pending" && !decided[a.id]);
  const processed = apps.filter((a) => a.status !== "pending" || decided[a.id]);

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <h2 className="font-montserrat font-black text-3xl text-blue-900">Заявки</h2>
        <button onClick={loadApps} className="flex items-center gap-2 text-sm text-blue-500 hover:text-blue-700 font-montserrat font-600">
          <Icon name="RefreshCw" size={14} /> Обновить
        </button>
      </div>

      {loading && (
        <div className="flex justify-center py-12">
          <Icon name="Loader2" size={28} className="text-blue-400 animate-spin" />
        </div>
      )}

      {!loading && pending.length === 0 && (
        <div className="glass rounded-2xl p-10 text-center mb-6">
          <Icon name="Inbox" size={32} className="text-blue-300 mx-auto mb-3" />
          <p className="text-blue-400 font-golos">Новых заявок нет</p>
        </div>
      )}

      {pending.length > 0 && (
        <div className="space-y-4 mb-8">
          <p className="font-montserrat font-700 text-blue-700 text-sm uppercase tracking-wider">На рассмотрении ({pending.length})</p>
          {pending.map((app) => (
            <div key={app.id} className="glass rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-montserrat font-800 text-blue-900 text-lg">{app.nickname}</span>
                  <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full font-montserrat font-600">#{app.id}</span>
                </div>
                <p className="text-blue-500 font-golos text-sm">{app.email}</p>
              </div>
              <div className="flex gap-2 shrink-0">
                <button
                  onClick={() => decide(app.id, "accept")}
                  disabled={deciding === app.id}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-green-500 text-white font-montserrat font-700 text-sm hover:bg-green-600 transition disabled:opacity-60"
                >
                  {deciding === app.id ? <Icon name="Loader2" size={14} className="animate-spin" /> : <Icon name="Check" size={14} />}
                  Принять
                </button>
                <button
                  onClick={() => decide(app.id, "reject")}
                  disabled={deciding === app.id}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-red-500 text-white font-montserrat font-700 text-sm hover:bg-red-600 transition disabled:opacity-60"
                >
                  <Icon name="X" size={14} />
                  Отказать
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {processed.length > 0 && (
        <div className="space-y-3">
          <p className="font-montserrat font-700 text-blue-400 text-sm uppercase tracking-wider">Обработанные</p>
          {processed.map((app) => {
            const finalStatus = decided[app.id] || app.status;
            return (
              <div key={app.id} className="glass rounded-xl p-4 flex items-center gap-4 opacity-70">
                <div className="flex-1">
                  <span className="font-montserrat font-700 text-blue-800">{app.nickname}</span>
                  <span className="text-blue-400 font-golos text-sm ml-2">{app.email}</span>
                </div>
                <span className={`text-xs px-3 py-1 rounded-full font-montserrat font-700
                  ${finalStatus === "accept" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
                  {finalStatus === "accept" ? "Принят" : "Отклонён"}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function Index() {
  const [tab, setTab] = useState<Tab>("about");

  return (
    <div className="min-h-screen">
      <BgDecor />
      <Header active={tab} onTab={setTab} />

      <main className="max-w-5xl mx-auto px-4 py-12">
        {tab === "about"   && <AboutTab onTab={setTab} />}
        {tab === "rules"   && <RulesTab />}
        {tab === "socials" && <SocialsTab />}
        {tab === "apply"   && <ApplyTab />}
        {tab === "admin"   && <AdminTab />}
      </main>

      <footer className="text-center py-6 text-blue-300 text-xs font-golos">
        © 2024 Spirit Server · Minecraft 1.21.1
        <button
          onClick={() => setTab("admin")}
          className="ml-3 text-blue-200/40 hover:text-blue-300 transition text-xs"
        >
          Admin
        </button>
      </footer>
    </div>
  );
}