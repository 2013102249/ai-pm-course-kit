# -*- coding: utf-8 -*-
import json, subprocess, time, re, os
APP = 'B82TblDIWa3L68suZu9cQ0dwnzf'
ROOT = '/Users/qingzou/WorkBuddy/2026-10-21-18-40-10/output/course-kit'
STATE = ROOT + '/_exports/forms_state.json'
PROG = ROOT + '/_exports/fix_v3_progress.json'
def run(args, data=None, tries=4):
    out = ''
    for _ in range(tries):
        cmd = ['lark-cli'] + args + ['--as','user','--format','json']
        if data is not None: cmd += ['--data', data]
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = (r.stdout or '').strip() or (r.stderr or '').strip()
        if out.startswith('{'):
            try:
                j = json.loads(out)
                if j.get('ok'): return j
                if j.get('error',{}).get('type') in ('network','transport','unknown'): time.sleep(1.5); continue
                return j
            except Exception: pass
        time.sleep(1.5)
    return {'ok': False, 'raw': out[:200]}
recs = json.load(open(ROOT + '/_exports/分层习题数据.json'))
by_day = {}
for r in recs: by_day.setdefault(r['day'], []).append(r)
def extract_special(path, day):
    txt = open(path, encoding='utf-8-sig').read()
    lines = txt.splitlines(); out = []; qno = 0; i = 0
    while i < len(lines):
        m = re.match(r'^###\s*(?:标准\s*)?(\d+)[.、]?\s*·?\s*(.+)', lines[i])
        if m:
            title = m.group(2).strip(); buf = {}; j = i + 1
            while j < len(lines) and not lines[j].startswith('###'):
                tm = re.match(r'^\|\s*(达标线|达标口径|验收要求|核验方式|未达标补救)\s*\|', lines[j].strip())
                if tm:
                    cells = [c.strip() for c in lines[j].strip().strip('|').split('|')]
                    buf[cells[0]] = cells[1] if len(cells) > 1 else ''
                j += 1
            if buf.get('达标线') or buf.get('验收要求') or buf.get('达标口径'):
                qno += 1
                out.append(dict(day=day, layer='验收清单', qtype='验收自查', qno=qno, stem=title, options='', desc='',
                                answer=buf.get('达标线') or buf.get('验收要求') or buf.get('达标口径') or '',
                                rubric='；'.join(f'{k}：{v}' for k, v in buf.items() if k in ('核验方式','未达标补救')),
                                score='', kaodian='当日产出验收'))
            i = j; continue
        i += 1
    return out
for day, p in [('W3D5','W3-物料/W3D5-原型评审I/06-分层习题.md'),('W4D5','W4-物料/W4D5-PRD评审大会/06-分层习题.md'),('W7D1','W7-物料/W7D1-行业纵深/06-分层习题.md')]:
    sp = extract_special(os.path.join(ROOT, p), day)
    if sp: by_day[day] = sp
state = {s['day']: s for s in json.load(open(STATE))}
prog = {}
if os.path.exists(PROG):
    try: prog = json.load(open(PROG))
    except Exception: prog = {}
DAYS = sorted(state.keys(), key=lambda d: (int(d[1]), d[3]))
def field_name(r):
    sc = f"（{r['score']}分）" if str(r.get('score','')).strip() else ''
    nm = f"Q{r['qno']}{sc} {r['stem']}".replace('\n', ' ').strip()
    return nm[:88]
def opt_labels(r):
    opts = r.get('options','') or ''
    lines = [x.strip() for x in opts.split('\n') if x.strip()]
    out = []
    for l in lines:
        m = re.match(r'^([A-G])[.、]\s*(.+)$', l)
        if m: out.append({'name': f"{m.group(1)}. {m.group(2)}"})
    return out
for day in DAYS:
    if prog.get(day): continue
    st = state[day]; tid = st['table_id']; fid = st['form_id']
    qs = sorted(by_day[day], key=lambda x: x['qno'])
    fl = run(['base','+field-list','--base-token',APP,'--table-id',tid])
    fields = (fl.get('data') or {}).get('fields') or []
    id2name = {f.get('id'): f.get('name') for f in fields}
    id2q = {}
    for f in fields:
        m = re.match(r'Q(\d+)', str(f.get('name','')))
        if m: id2q[f.get('id')] = int(m.group(1))
    # 1) 字段改名 + 选项写全文
    newnames = {}
    for r in qs:
        if r['qno'] not in id2q.values(): continue
        fid_q = next(k for k, v in id2q.items() if v == r['qno'])
        nm = field_name(r)
        spec = {'name': nm, 'type': 'select' if (r['qtype']=='选择题' or r['layer']=='验收清单') else 'text'}
        if r['qtype'] == '选择题':
            ol = opt_labels(r)
            spec['options'] = ol or [{'name': x} for x in list('ABCD')]
        elif r['layer'] == '验收清单':
            spec['options'] = [{'name':'已达标'},{'name':'未达标'}]
        u = run(['base','+field-update','--base-token',APP,'--table-id',tid,'--field-id',fid_q,'--json', json.dumps(spec, ensure_ascii=False),'--yes'])
        if not u.get('ok'):
            print(f'{day} 字段 {r["qno"]} 更新失败: {json.dumps(u, ensure_ascii=False)[:120]}', flush=True)
        newnames[r['qno']] = nm
        time.sleep(0.25)
    # 2) 表单题目：title=新字段名（带题干），description=选项/补充
    fq = run(['base','+form-questions-list','--base-token',APP,'--table-id',tid,'--form-id',fid])
    qlist = (fq.get('data') or {}).get('questions') or []
    pay = []
    for q in qlist:
        fid_q = q.get('id')
        if fid_q in id2q:
            r = next(x for x in qs if x['qno'] == id2q[fid_q])
            nm = newnames.get(r['qno']) or field_name(r)
            desc = (r.get('options') or r.get('desc') or '')[:480]
            pay.append({'id': fid_q, 'title': nm[:460], 'description': desc, 'required': False})
        elif str(q.get('title','')).startswith('学员姓名'):
            pay.append({'id': fid_q, 'title': '学员姓名', 'description': '请填写真实姓名，便于讲师批改反馈', 'required': True})
    pay.sort(key=lambda x: 0 if x['title'].startswith('学员姓名') else int(re.match(r'Q(\d+)', x['title']).group(1)))
    for i in range(0, len(pay), 10):
        u = run(['base','+form-questions-update','--base-token',APP,'--table-id',tid,'--form-id',fid,'--questions', json.dumps(pay[i:i+10], ensure_ascii=False)])
        if not u.get('ok'): print(f'{day} 题目覆写失败', flush=True)
        time.sleep(0.4)
    # 3) 视图排序
    vl = run(['base','+view-list','--base-token',APP,'--table-id',tid])
    views = (vl.get('data') or {}).get('views') or []
    grid_v = next((v['id'] for v in views if v.get('type') == 'grid'), None)
    ordered_grid = ['学员姓名'] + [newnames[r['qno']] for r in qs if r['qno'] in newnames] + ['提交时间']
    ordered_form = ['学员姓名'] + [newnames[r['qno']] for r in qs if r['qno'] in newnames]
    if grid_v:
        run(['base','+view-set-visible-fields','--base-token',APP,'--table-id',tid,'--view-id',grid_v,
             '--json', json.dumps({'visible_fields': ordered_grid}, ensure_ascii=False)]); time.sleep(0.4)
    run(['base','+view-set-visible-fields','--base-token',APP,'--table-id',tid,'--view-id',fid,
         '--json', json.dumps({'visible_fields': ordered_form}, ensure_ascii=False)]); time.sleep(0.4)
    # 4) 分享放开（任何人可填）
    run(['base','+form-share-update','--base-token',APP,'--table-id',tid,'--form-id',fid,
         '--access-scope','anyone','--enabled']); time.sleep(0.4)
    sg = run(['base','+form-share-get','--base-token',APP,'--table-id',tid,'--form-id',fid])
    surl = ((sg.get('data') or {}).get('share_url')) or ''
    st['url'] = surl; st['grid_view_id'] = grid_v
    state[day] = st
    prog[day] = True
    json.dump(list(state.values()), open(STATE,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(prog, open(PROG,'w'), ensure_ascii=False)
    print(f'{day} OK ({len(qs)} 题) 累计 {len(prog)}/40', flush=True)
print('修复完成:', len(prog), '/40', flush=True)
