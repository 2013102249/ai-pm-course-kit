# -*- coding: utf-8 -*-
import json, subprocess, time, re, os, glob
APP = 'B82TblDIWa3L68suZu9cQ0dwnzf'
ROOT = '/Users/qingzou/WorkBuddy/2026-10-21-18-40-10/output/course-kit'
def run(args, tries=3):
    for _ in range(tries):
        r = subprocess.run(['lark-cli'] + args + ['--as','user','--format','json'], capture_output=True, text=True)
        out = (r.stdout or '').strip()
        if out.startswith('{'):
            try: return json.loads(out)
            except Exception: pass
        time.sleep(1.2)
    return {'ok': False}
# ---------- md 原文抽取选项（支持行内多选项） ----------
MD = {}
for p in glob.glob(ROOT + '/W*-物料/*/06-分层习题.md') + [ROOT + '/01-样课日-W3D3-RAG/06-分层习题.md']:
    day = os.path.basename(os.path.dirname(p))
    dm = re.match(r'(?:01-样课日-)?(W\dD\d)', day)
    if dm: MD[dm.group(1)] = p
def extract_options(day, qno):
    p = MD.get(day)
    if not p: return []
    lines = open(p, encoding='utf-8-sig').read().splitlines()
    start = None
    for i, ln in enumerate(lines):
        m = re.match(r'^\*\*' + str(qno) + r'[.、]\s*(.+?)\*\*\s*$', ln)
        if m: start = i; break
    if start is None: return []
    body = []
    for ln in lines[start+1:]:
        if re.match(r'^\*\*\d+[.、]', ln) or ln.startswith('## ') or ln.strip() == '---': break
        body.append(ln)
    opts = []
    for ln in body:
        marks = list(re.finditer(r'([A-G])[.．、\)）]\s*', ln))
        if len(marks) >= 2:
            for k, m in enumerate(marks):
                end = marks[k+1].start() if k+1 < len(marks) else len(ln)
                txt = ln[m.end():end].strip()
                if txt: opts.append((m.group(1), txt))
        elif len(marks) == 1:
            m = marks[0]
            txt = ln[m.end():].strip()
            if txt: opts.append((m.group(1), txt))
    seen = set(); out = []
    for L, t in opts:
        if L in seen: continue
        seen.add(L); out.append((L, t))
    return out
# ---------- 主流程 ----------
recs = json.load(open(ROOT + '/_exports/分层习题数据.json'))
by_day = {}
for r in recs: by_day.setdefault(r['day'], []).append(r)
state = json.load(open(ROOT + '/_exports/forms_state.json'))
smap = {s['day']: s for s in state}
updated_fields = 0; updated_days = []
for st in sorted(state, key=lambda x: (int(x['day'][1]), x['day'][3])):
    day, tid, fid = st['day'], st['table_id'], st['form_id']
    qs = sorted(by_day.get(day, []), key=lambda x: x['qno'])
    choice = [r for r in qs if r['qtype'] == '选择题']
    if not choice: continue
    fl = run(['base','+field-list','--base-token',APP,'--table-id',tid])
    fs = (fl.get('data') or {}).get('fields') or []
    id2q = {}
    for f in fs:
        m = re.match(r'^Q(\d+)', str(f.get('name','')))
        if m: id2q[f.get('id')] = int(m.group(1))
    plan = {}
    for r in choice:
        opts = extract_options(day, r['qno'])
        if len(opts) < 3: continue
        fq_id = next((k for k, v in id2q.items() if v == r['qno']), None)
        if not fq_id: continue
        labels = [{'name': f"{L}. {t}"} for L, t in opts]
        cur = next((f for f in fs if f.get('id') == fq_id), {})
        cur_labels = [str(o.get('name')) for o in (cur.get('options') or [])]
        if cur_labels != [x['name'] for x in labels]:
            u = run(['base','+field-update','--base-token',APP,'--table-id',tid,'--field-id',fq_id,
                     '--json', json.dumps({'name': cur.get('name'), 'type': 'select', 'options': labels}, ensure_ascii=False),'--yes'])
            if u.get('ok'): updated_fields += 1
            else: print(day, 'Q%s 选项更新失败' % r['qno'], json.dumps(u, ensure_ascii=False)[:120], flush=True)
            time.sleep(0.25)
        plan[r['qno']] = '\n'.join(f"{L}. {t}" for L, t in opts)
    # 表单题目描述同步选项全文
    fq = run(['base','+form-questions-list','--base-token',APP,'--table-id',tid,'--form-id',fid])
    qlist = (fq.get('data') or {}).get('questions') or []
    pay = []
    for q in qlist:
        fq_id = q.get('id')
        if fq_id in id2q:
            r = next((x for x in qs if x['qno'] == id2q[fq_id]), None)
            if not r: continue
            desc = plan.get(r['qno']) or (r.get('options') or r.get('desc') or '')
            pay.append({'id': fq_id, 'title': str(q.get('title',''))[:460], 'description': desc[:480], 'required': False})
        elif str(q.get('title','')).startswith('学员姓名'):
            pay.append({'id': fq_id, 'title': '学员姓名', 'description': '请填写真实姓名，便于讲师批改反馈', 'required': True})
    pay.sort(key=lambda x: 0 if x['title'].startswith('学员姓名') else int(re.match(r'Q(\d+)', x['title']).group(1)))
    if pay:
        for i in range(0, len(pay), 10):
            run(['base','+form-questions-update','--base-token',APP,'--table-id',tid,'--form-id',fid,'--questions', json.dumps(pay[i:i+10], ensure_ascii=False)])
            time.sleep(0.35)
    updated_days.append(day)
    print(f'{day}: 选项同步完成（更新字段 {updated_fields} 累计）', flush=True)
print(f'选项字段更新 {updated_fields} 个，覆盖 {len(updated_days)} 天', flush=True)
