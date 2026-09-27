'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/apiClient';
import { getAccessToken } from '@/lib/auth';
import type { Category, Drama, DramaDetail, Episode } from '@/types';
import styles from './page.module.css';

type Tab = 'dramas' | 'categories' | 'episodes';

interface DramaForm {
  title: string;
  description: string;
  cover_url: string;
  category_id: string;
  release_year: string;
  episode_count: string;
  is_completed: boolean;
}

const EMPTY_FORM: DramaForm = {
  title: '',
  description: '',
  cover_url: '',
  category_id: '',
  release_year: '',
  episode_count: '',
  is_completed: false,
};

function toForm(d: Drama): DramaForm {
  return {
    title: d.title ?? '',
    description: d.description ?? '',
    cover_url: d.cover_url ?? '',
    category_id: d.category_id != null ? String(d.category_id) : '',
    release_year: d.release_year != null ? String(d.release_year) : '',
    episode_count: d.episode_count != null ? String(d.episode_count) : '',
    is_completed: Boolean(d.is_completed),
  };
}

/** 將表單轉成 API payload：空字串轉 null（允許清空欄位） */
function formToPayload(f: DramaForm) {
  const numOrNull = (s: string) => (s.trim() === '' ? null : Number(s));
  return {
    title: f.title.trim(),
    description: f.description.trim() || null,
    cover_url: f.cover_url.trim() || null,
    category_id: f.category_id.trim() === '' ? null : Number(f.category_id),
    release_year: numOrNull(f.release_year),
    episode_count: numOrNull(f.episode_count),
    is_completed: f.is_completed,
  };
}

function errMsg(e: unknown): string {
  if (e && typeof e === 'object' && 'message' in e) {
    return String((e as { message: unknown }).message);
  }
  return '未知錯誤';
}

interface EpisodeForm {
  episode_number: string;
  title: string;
  video_url: string;
  duration: string;
  description: string;
}

const EMPTY_EP_FORM: EpisodeForm = {
  episode_number: '',
  title: '',
  video_url: '',
  duration: '',
  description: '',
};

export default function AdminPage() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>('dramas');
  const [checking, setChecking] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  // 劇集
  const [dramas, setDramas] = useState<Drama[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [search, setSearch] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState<DramaForm>(EMPTY_FORM);

  // 分類
  const [newCatName, setNewCatName] = useState('');
  const [newCatSlug, setNewCatSlug] = useState('');

  // 集數
  const [episodeDramaId, setEpisodeDramaId] = useState<number | null>(null);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [episodeDramaDetail, setEpisodeDramaDetail] = useState<DramaDetail | null>(null);
  const [creatingEp, setCreatingEp] = useState(false);
  const [editingEpId, setEditingEpId] = useState<number | null>(null);
  const [epForm, setEpForm] = useState<EpisodeForm>(EMPTY_EP_FORM);
  const [loadingEp, setLoadingEp] = useState(false);

  // 權限檢查：無 token → 去登入；非 admin → 顯示無權限
  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace('/login');
      return;
    }
    apiClient<{ is_admin?: boolean }>('/auth/me')
      .then((me) => {
        setIsAdmin(Boolean(me.is_admin));
        setChecking(false);
      })
      .catch((e: { message?: string }) => {
        setAuthError(errMsg(e));
        setChecking(false);
      });
  }, [router]);

  const loadData = useCallback(async () => {
    setBusy(true);
    setMsg(null);
    try {
      const [d, c] = await Promise.all([
        apiClient<Drama[]>('/cms/dramas'),
        apiClient<Category[]>('/categories', { auth: false }),
      ]);
      setDramas(d ?? []);
      setCategories(c ?? []);
    } catch (e) {
      setMsg(`載入失敗：${errMsg(e)}`);
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    if (isAdmin) loadData();
  }, [isAdmin, loadData]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return dramas;
    return dramas.filter(
      (d) =>
        d.title.toLowerCase().includes(q) ||
        (d.category?.name ?? '').toLowerCase().includes(q),
    );
  }, [dramas, search]);

  // ---------- Drama CRUD ----------
  const startCreate = () => {
    setCreating(true);
    setEditingId(null);
    setForm(EMPTY_FORM);
  };

  const startEdit = (d: Drama) => {
    setCreating(false);
    setEditingId(d.id);
    setForm(toForm(d));
  };

  const submitDrama = async () => {
    if (!form.title.trim()) {
      setMsg('劇名不能空白');
      return;
    }
    setBusy(true);
    setMsg(null);
    try {
      if (creating) {
        await apiClient('/cms/dramas', { method: 'POST', body: formToPayload(form) });
        setMsg('已新增劇集');
      } else if (editingId != null) {
        await apiClient(`/cms/dramas/${editingId}`, { method: 'PUT', body: formToPayload(form) });
        setMsg('已更新劇集');
      }
      setCreating(false);
      setEditingId(null);
      await loadData();
    } catch (e) {
      setMsg(`儲存失敗：${errMsg(e)}`);
    } finally {
      setBusy(false);
    }
  };

  const deleteDrama = async (d: Drama) => {
    if (!window.confirm(`確定刪除「${d.title}」？此操作不可還原。`)) return;
    setBusy(true);
    setMsg(null);
    try {
      await apiClient(`/cms/dramas/${d.id}`, { method: 'DELETE' });
      setMsg(`已刪除「${d.title}」`);
      await loadData();
    } catch (e) {
      setMsg(`刪除失敗：${errMsg(e)}`);
    } finally {
      setBusy(false);
    }
  };

  // ---------- Category CRUD ----------
  const createCategory = async () => {
    if (!newCatName.trim() || !newCatSlug.trim()) {
      setMsg('分類名稱同 slug 都要填');
      return;
    }
    setBusy(true);
    setMsg(null);
    try {
      await apiClient('/cms/categories', {
        method: 'POST',
        body: { name: newCatName.trim(), slug: newCatSlug.trim().toLowerCase() },
      });
      setNewCatName('');
      setNewCatSlug('');
      setMsg('已新增分類');
      await loadData();
    } catch (e) {
      setMsg(`新增分類失敗：${errMsg(e)}`);
    } finally {
      setBusy(false);
    }
  };

  const renameCategory = async (c: Category, name: string) => {
    setBusy(true);
    setMsg(null);
    try {
      await apiClient(`/cms/categories/${c.id}`, {
        method: 'PUT',
        body: { name, slug: c.slug },
      });
      setMsg('已更新分類');
      await loadData();
    } catch (e) {
      setMsg(`更新分類失敗：${errMsg(e)}`);
    } finally {
      setBusy(false);
    }
  };

  const deleteCategory = async (c: Category) => {
    if (!window.confirm(`確定刪除分類「${c.name}」？`)) return;
    setBusy(true);
    setMsg(null);
    try {
      await apiClient(`/cms/categories/${c.id}`, { method: 'DELETE' });
      setMsg(`已刪除分類「${c.name}」`);
      await loadData();
    } catch (e) {
      setMsg(`刪除分類失敗：${errMsg(e)}`);
    } finally {
      setBusy(false);
    }
  };

  // ---------- Episode CRUD ----------
  const loadEpisodes = useCallback(async (dramaId: number) => {
    setLoadingEp(true);
    setMsg(null);
    try {
      const detail = await apiClient<DramaDetail>(`/dramas/${dramaId}`, { auth: false });
      setEpisodeDramaDetail(detail);
      setEpisodes(detail.episodes ?? []);
    } catch (e) {
      setMsg(`載入集數失敗：${errMsg(e)}`);
      setEpisodes([]);
    } finally {
      setLoadingEp(false);
    }
  }, []);

  // 揀咗劇集或者入到集數 tab 時載入
  useEffect(() => {
    if (tab !== 'episodes') return;
    if (episodeDramaId == null) {
      if (dramas.length > 0) setEpisodeDramaId(dramas[0].id);
      return;
    }
    loadEpisodes(episodeDramaId);
  }, [tab, episodeDramaId, dramas, loadEpisodes]);

  const startCreateEp = () => {
    setCreatingEp(true);
    setEditingEpId(null);
    setEpForm({ ...EMPTY_EP_FORM, episode_number: String(episodes.length + 1) });
  };

  const startEditEp = (ep: Episode) => {
    setCreatingEp(false);
    setEditingEpId(ep.id);
    setEpForm({
      episode_number: String(ep.episode_number),
      title: ep.title,
      video_url: ep.video_url ?? '',
      duration: ep.duration != null ? String(ep.duration) : '',
      description: ep.description ?? '',
    });
  };

  const submitEpisode = async () => {
    if (episodeDramaId == null) {
      setMsg('請先揀一部劇集');
      return;
    }
    if (!epForm.episode_number.trim() || !epForm.title.trim() || !epForm.video_url.trim()) {
      setMsg('集數編號、標題同影片 URL 都要填');
      return;
    }
    const numOrNull = (s: string) => (s.trim() === '' ? null : Number(s));
    const base = {
      episode_number: Number(epForm.episode_number),
      title: epForm.title.trim(),
      video_url: epForm.video_url.trim(),
      duration: numOrNull(epForm.duration),
      description: epForm.description.trim() || null,
    };
    setBusy(true);
    setMsg(null);
    try {
      if (creatingEp) {
        await apiClient('/cms/episodes', { method: 'POST', body: { ...base, drama_id: episodeDramaId } });
        setMsg('已新增集數');
      } else if (editingEpId != null) {
        await apiClient(`/cms/episodes/${editingEpId}`, { method: 'PUT', body: base });
        setMsg('已更新集數');
      }
      setCreatingEp(false);
      setEditingEpId(null);
      await loadEpisodes(episodeDramaId);
    } catch (e) {
      setMsg(`儲存失敗：${errMsg(e)}`);
    } finally {
      setBusy(false);
    }
  };

  const deleteEpisode = async (ep: Episode) => {
    if (!window.confirm(`確定刪除第 ${ep.episode_number} 集「${ep.title}」？`)) return;
    setBusy(true);
    setMsg(null);
    try {
      await apiClient(`/cms/episodes/${ep.id}`, { method: 'DELETE' });
      setMsg(`已刪除第 ${ep.episode_number} 集`);
      if (episodeDramaId != null) await loadEpisodes(episodeDramaId);
    } catch (e) {
      setMsg(`刪除失敗：${errMsg(e)}`);
    } finally {
      setBusy(false);
    }
  };

  // ---------- Render ----------
  if (checking) {
    return (
      <main className={styles.wrap}>
        <div className={styles.centerMsg}>驗證權限中…</div>
      </main>
    );
  }

  if (!isAdmin) {
    return (
      <main className={styles.wrap}>
        <div className={styles.centerMsg}>
          <h1 className={styles.deniedTitle}>無管理員權限</h1>
          <p>{authError ?? '此帳號冇權限進入 CMS，請用管理員帳號登入。'}</p>
        </div>
      </main>
    );
  }

  const setField = (key: keyof DramaForm, value: string | boolean) =>
    setForm((f) => ({ ...f, [key]: value }));

  return (
    <main className={styles.wrap}>
      <header className={styles.header}>
        <h1 className={styles.title}>內容管理後台</h1>
        <nav className={styles.tabs}>
          <button
            type="button"
            className={`${styles.tab} ${tab === 'dramas' ? styles.tabActive : ''}`}
            onClick={() => setTab('dramas')}
          >
            劇集管理（{dramas.length}）
          </button>
          <button
            type="button"
            className={`${styles.tab} ${tab === 'categories' ? styles.tabActive : ''}`}
            onClick={() => setTab('categories')}
          >
            分類管理（{categories.length}）
          </button>
          <button
            type="button"
            className={`${styles.tab} ${tab === 'episodes' ? styles.tabActive : ''}`}
            onClick={() => setTab('episodes')}
          >
            集數管理
          </button>
        </nav>
      </header>

      {msg && <div className={styles.msg}>{msg}</div>}

      {tab === 'dramas' && (
        <section>
          <div className={styles.toolbar}>
            <input
              type="search"
              className={styles.input}
              placeholder="搜尋劇名／分類…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <button type="button" className={styles.primaryBtn} onClick={startCreate}>
              ＋ 新增劇集
            </button>
          </div>

          {(creating || editingId != null) && (
            <div className={styles.formCard}>
              <h2 className={styles.formTitle}>{creating ? '新增劇集' : '編輯劇集'}</h2>
              <div className={styles.formGrid}>
                <label className={styles.field}>
                  <span>劇名 *</span>
                  <input
                    className={styles.input}
                    value={form.title}
                    onChange={(e) => setField('title', e.target.value)}
                  />
                </label>
                <label className={styles.field}>
                  <span>封面 URL</span>
                  <input
                    className={styles.input}
                    value={form.cover_url}
                    onChange={(e) => setField('cover_url', e.target.value)}
                    placeholder="https://…"
                  />
                </label>
                <label className={styles.field}>
                  <span>分類</span>
                  <select
                    className={styles.input}
                    value={form.category_id}
                    onChange={(e) => setField('category_id', e.target.value)}
                  >
                    <option value="">（未分類）</option>
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label className={styles.field}>
                  <span>集數</span>
                  <input
                    className={styles.input}
                    inputMode="numeric"
                    value={form.episode_count}
                    onChange={(e) => setField('episode_count', e.target.value.replace(/\D/g, ''))}
                    placeholder="如 24"
                  />
                </label>
                <label className={styles.field}>
                  <span>年份</span>
                  <input
                    className={styles.input}
                    inputMode="numeric"
                    value={form.release_year}
                    onChange={(e) => setField('release_year', e.target.value.replace(/\D/g, ''))}
                    placeholder="如 2026"
                  />
                </label>
                <label className={styles.checkField}>
                  <input
                    type="checkbox"
                    checked={form.is_completed}
                    onChange={(e) => setField('is_completed', e.target.checked)}
                  />
                  <span>已完結</span>
                </label>
                <label className={styles.fieldWide}>
                  <span>簡介</span>
                  <textarea
                    className={styles.input}
                    rows={3}
                    value={form.description}
                    onChange={(e) => setField('description', e.target.value)}
                  />
                </label>
              </div>
              <div className={styles.formActions}>
                <button type="button" className={styles.primaryBtn} disabled={busy} onClick={submitDrama}>
                  {busy ? '儲存中…' : '儲存'}
                </button>
                <button
                  type="button"
                  className={styles.ghostBtn}
                  onClick={() => {
                    setCreating(false);
                    setEditingId(null);
                  }}
                >
                  取消
                </button>
              </div>
            </div>
          )}

          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>封面</th>
                  <th>劇名</th>
                  <th>分類</th>
                  <th>集數</th>
                  <th>狀態</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((d) => (
                  <tr key={d.id}>
                    <td>
                      {d.cover_url ? (
                        <img
                          className={styles.thumb}
                          src={d.cover_url}
                          alt=""
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.opacity = '0.25';
                          }}
                        />
                      ) : (
                        <div className={styles.thumbPlaceholder} />
                      )}
                    </td>
                    <td className={styles.cellTitle}>{d.title}</td>
                    <td>{d.category?.name ?? '—'}</td>
                    <td>{d.episode_count ?? '—'}</td>
                    <td>
                      <span className={`${styles.badge} ${d.is_completed ? styles.badgeDone : styles.badgeOngoing}`}>
                        {d.is_completed ? '完結' : '連載'}
                      </span>
                    </td>
                    <td>
                      <button type="button" className={styles.smallBtn} onClick={() => startEdit(d)}>
                        編輯
                      </button>
                      <button type="button" className={`${styles.smallBtn} ${styles.dangerBtn}`} onClick={() => deleteDrama(d)}>
                        刪除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filtered.length === 0 && (
              <div className={styles.empty}>搵唔到劇集（或清空咗搜尋字）</div>
            )}
          </div>
        </section>
      )}

      {tab === 'categories' && (
        <section>
          <div className={styles.toolbar}>
            <input
              className={styles.input}
              placeholder="新分類名稱"
              value={newCatName}
              onChange={(e) => setNewCatName(e.target.value)}
            />
            <input
              className={styles.input}
              placeholder="slug（小寫英文，如 wuxia）"
              value={newCatSlug}
              onChange={(e) => setNewCatSlug(e.target.value)}
            />
            <button type="button" className={styles.primaryBtn} disabled={busy} onClick={createCategory}>
              新增分類
            </button>
          </div>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>名稱</th>
                  <th>Slug</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {categories.map((c) => (
                  <CategoryRow key={c.id} category={c} onRename={renameCategory} onDelete={deleteCategory} busy={busy} />
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {tab === 'episodes' && (
        <section>
          <div className={styles.toolbar}>
            <select
              className={styles.input}
              value={episodeDramaId ?? ''}
              onChange={(e) => {
                const v = e.target.value;
                setEpisodeDramaId(v ? Number(v) : null);
                setCreatingEp(false);
                setEditingEpId(null);
              }}
            >
              <option value="">選擇劇集…</option>
              {dramas.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title}
                </option>
              ))}
            </select>
            <button
              type="button"
              className={styles.primaryBtn}
              disabled={episodeDramaId == null}
              onClick={startCreateEp}
            >
              ＋ 新增集數
            </button>
          </div>

          {loadingEp && <div className={styles.centerMsg}>載入集數中…</div>}

          {(creatingEp || editingEpId != null) && episodeDramaId != null && (
            <div className={styles.formCard}>
              <h2 className={styles.formTitle}>
                {creatingEp ? '新增集數' : `編輯集數 · ${episodeDramaDetail?.title ?? `劇集 #${episodeDramaId}`}`}
              </h2>
              <div className={styles.formGrid}>
                <label className={styles.field}>
                  <span>集數編號 *</span>
                  <input
                    className={styles.input}
                    inputMode="numeric"
                    value={epForm.episode_number}
                    onChange={(e) => setEpForm((f) => ({ ...f, episode_number: e.target.value.replace(/\D/g, '') }))}
                  />
                </label>
                <label className={styles.field}>
                  <span>標題 *</span>
                  <input
                    className={styles.input}
                    value={epForm.title}
                    onChange={(e) => setEpForm((f) => ({ ...f, title: e.target.value }))}
                  />
                </label>
                <label className={styles.field}>
                  <span>影片 URL *</span>
                  <input
                    className={styles.input}
                    value={epForm.video_url}
                    onChange={(e) => setEpForm((f) => ({ ...f, video_url: e.target.value }))}
                    placeholder="https://…"
                  />
                </label>
                <label className={styles.field}>
                  <span>時長（秒）</span>
                  <input
                    className={styles.input}
                    inputMode="numeric"
                    value={epForm.duration}
                    onChange={(e) => setEpForm((f) => ({ ...f, duration: e.target.value.replace(/\D/g, '') }))}
                    placeholder="如 120"
                  />
                </label>
                <label className={styles.fieldWide}>
                  <span>簡介</span>
                  <textarea
                    className={styles.input}
                    rows={2}
                    value={epForm.description}
                    onChange={(e) => setEpForm((f) => ({ ...f, description: e.target.value }))}
                  />
                </label>
              </div>
              <div className={styles.formActions}>
                <button type="button" className={styles.primaryBtn} disabled={busy} onClick={submitEpisode}>
                  {busy ? '儲存中…' : '儲存'}
                </button>
                <button
                  type="button"
                  className={styles.ghostBtn}
                  onClick={() => {
                    setCreatingEp(false);
                    setEditingEpId(null);
                  }}
                >
                  取消
                </button>
              </div>
            </div>
          )}

          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>集數</th>
                  <th>標題</th>
                  <th>影片 URL</th>
                  <th>時長</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {episodes.map((ep) => (
                  <tr key={ep.id}>
                    <td>{ep.episode_number}</td>
                    <td className={styles.cellTitle}>{ep.title}</td>
                    <td
                      style={{
                        maxWidth: 260,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {ep.video_url ?? '—'}
                    </td>
                    <td>{ep.duration != null ? `${ep.duration}s` : '—'}</td>
                    <td>
                      <button type="button" className={styles.smallBtn} onClick={() => startEditEp(ep)}>
                        編輯
                      </button>
                      <button
                        type="button"
                        className={`${styles.smallBtn} ${styles.dangerBtn}`}
                        onClick={() => deleteEpisode(ep)}
                      >
                        刪除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {episodes.length === 0 && !loadingEp && (
              <div className={styles.empty}>呢部劇未有集數（或未揀劇集）</div>
            )}
          </div>
        </section>
      )}
    </main>
  );
}

function CategoryRow({
  category,
  onRename,
  onDelete,
  busy,
}: {
  category: Category;
  onRename: (c: Category, name: string) => void;
  onDelete: (c: Category) => void;
  busy: boolean;
}) {
  const [name, setName] = useState(category.name);
  return (
    <tr>
      <td>{category.id}</td>
      <td>
        <input className={styles.input} value={name} onChange={(e) => setName(e.target.value)} />
      </td>
      <td className={styles.cellSlug}>{category.slug}</td>
      <td>
        <button type="button" className={styles.smallBtn} disabled={busy} onClick={() => onRename(category, name.trim() || category.name)}>
          儲存
        </button>
        <button type="button" className={`${styles.smallBtn} ${styles.dangerBtn}`} disabled={busy} onClick={() => onDelete(category)}>
          刪除
        </button>
      </td>
    </tr>
  );
}
