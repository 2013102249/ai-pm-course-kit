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
MD = {}
for p in glob.glob(ROOT + '/W*-物料/*/06-分层习题.md') + [ROOT + '/01-样课日-W3D3-RAG/06-分层习题.md']:
    dm = re.match(r'(?:01-样课日-)?(W\dD\d)', os.path.basename(os.path.dirname(p)))
    if dm: MD[dm.group(1)] = p
def has_options(day, qno):
    p = MD.get(day)
    if not p: return 0
    lines = open(p, encoding='utf-8-sig').read().splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(r'^\*\*' + str(qno) + r'[.、]', ln): start = i; break
    if start is None: return 0
    cnt = set()
    for ln in lines[start+1:]:
        if re.match(r'^\*\*\d+[.、]', ln) or ln.startswith('## ') or ln.strip() == '---': break
        for m in re.finditer(r'([A-G])[.．、\)）]\s*', ln): cnt.add(m.group(1))
    return len(cnt)
recs = json.load(open(ROOT + '/_exports/分层习题数据.json'))
by_day = {}
for r in recs: by_day.setdefault(r['day'], []).append(r)
state = json.load(open(ROOT + '/_exports/forms_state.json'))
fixed = []
for st in sorted(state, key=lambda x: (int(x['day'][1]), x['day'][3])):
    day, tid, fid = st['day'], st['table_id'], st['form_id']
    qs = {r['qno']: r for r in by_day.get(day, [])}
    fl = run(['base','+field-list','--base-token',APP,'--table-id',tid])
    fs = (fl.get('data') or {}).get('fields') or []
    id2q = {}
    for f in fs:
        m = re.match(r'^Q(\d+)', str(f.get('name','')))
        if m: id2q[f.get('id')] = int(m.group(1))
    pay = []
    changed = False
    for f in fs:
        fq_id = f.get('id')
        if fq_id not in id2q: continue
        qno = id2q[fq_id]
        opts = f.get('options') or []
        bare = bool(opts) and all(len(str(o.get('name',''))) <= 2 for o in opts)
        src = qs.get(qno)
        if bare and has_options(day, qno) < 3:
            u = run(['base','+field-update','--base-token',APP,'--table-id',tid,'--field-id',fq_id,
                     '--json', json.dumps({'name': f.get('name'), 'type': 'text'}, ensure_ascii=False),'--yes'])
            if u.get('ok'):
                fixed.append(f'{day} Q{qno}'); changed = True
            else:
                print(day, 'Q%s 转文本失败' % qno, json.dumps(u, ensure_ascii=False)[:110], flush=True)
            time.sleep(0.3)
        if src:
            desc = (src.get('desc') or '').strip()
            if not desc and src.get('qtype') != '选择题':
                desc = '按《06-分层习题》题干要求作答；参考答案与评分要点见习题总库。'
            pay.append({'id': fq_id, 'title': str(f.get('name',''))[:460], 'description': desc[:480], 'required': False})
    fq = run(['base','+form-questions-list','--base-token',APP,'--table-id',tid,'--form-id',fid])
    qlist = (fq.get('data') or {}).get('questions') or []
    for q in qlist:
        fq_id = q.get('id')
        if fq_id in id2q:
            src = qs.get(id2q[fq_id])
            if not src: continue
            desc = (src.get('desc') or '').strip() or (src.get('options') or '').strip() or '按《06-分层习题》题干要求作答；参考答案与评分要点见习题总库。'
            pay = [x for x in pay if x['id'] != fq_id]
            pay.append({'id': fq_id, 'title': str(q.get('title',''))[:460], 'description': desc[:480], 'required': False})
        elif str(q.get('title','')).startswith('学员姓名'):
            pay = [x for x in pay if x['id'] != fq_id]
            pay.append({'id': fq_id, 'title': '学员姓名', 'description': '请填写真实姓名，便于讲师批改反馈', 'required': True})
    pay.sort(key=lambda x: 0 if x['title'].startswith('学员姓名') else int(re.match(r'Q(\d+)', x['title']).group(1)))
    if pay:
        for i in range(0, len(pay), 10):
            run(['base','+form-questions-update','--base-token',APP,'--table-id',tid,'--form-id',fid,'--questions', json.dumps(pay[i:i+10], ensure_ascii=False)])
            time.sleep(0.35)
    if changed: print(f'{day} 纠正非选择题', flush=True)
print('转文本字段:', len(fixed), fixed, flush=True)
