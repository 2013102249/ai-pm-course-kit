# -*- coding: utf-8 -*-
import json, subprocess, time, re, os
APP = 'B82TblDIWa3L68suZu9cQ0dwnzf'
ROOT = '/Users/qingzou/WorkBuddy/2026-10-21-18-40-10/output/course-kit'
def run(args, tries=3):
    for _ in range(tries):
        r = subprocess.run(['lark-cli'] + args + ['--as','user','--format','json'], capture_output=True, text=True)
        out = (r.stdout or r.stderr).strip()
        if out.startswith('{'):
            try: return json.loads(out)
            except Exception: pass
        time.sleep(1.2)
    return {'ok': False}
state = json.load(open(ROOT + '/_exports/forms_state.json'))
smap = {s['day']: s for s in state}
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
                out.append(dict(day=day, layer='验收清单', qtype='验收自查', qno=qno, stem=title, options='',
                                desc='', answer=buf.get('达标线') or buf.get('验收要求') or buf.get('达标口径') or '',
                                rubric='；'.join(f'{k}：{v}' for k, v in buf.items() if k in ('核验方式','未达标补救')),
                                score='', kaodian='当日产出验收'))
            i = j; continue
        i += 1
    return out
for day, p in [('W3D5','W3-物料/W3D5-原型评审I/06-分层习题.md'),('W4D5','W4-物料/W4D5-PRD评审大会/06-分层习题.md'),('W7D1','W7-物料/W7D1-行业纵深/06-分层习题.md')]:
    sp = extract_special(ROOT + '/' + p, day)
    if sp: by_day[day] = sp
TARGET = ['W3D5','W4D5','W6D2','W6D4','W6D5','W7D1','W8D4','W7D4','W5D5','W8D5']
for day in TARGET:
    st = smap[day]; tid, fid = st['table_id'], st['form_id']
    qs = sorted(by_day.get(day, []), key=lambda x: x['qno'])
    if not qs: print(day, '无数据'); continue
    fl = run(['base','+field-list','--base-token',APP,'--table-id',tid])
    fs = (fl.get('data') or {}).get('fields') or []
    id2q = {}
    for f in fs:
        m = re.match(r'Q(\d+)', str(f.get('name','')))
        if m: id2q[f.get('id')] = int(m.group(1))
    newnames = {}
    for r in qs:
        if r['qno'] not in id2q.values(): continue
        fq_id = next(k for k, v in id2q.items() if v == r['qno'])
        std = (r.get('answer') or '').replace('\n', ' ').strip()
        nm = f"Q{r['qno']} {r['stem']}"
        if std: nm += f"｜达标口径：{std[:44]}"
        nm = nm[:92]
        spec = {'name': nm, 'type': 'select', 'options': [{'name':'已达标'},{'name':'未达标'}]}
        u = run(['base','+field-update','--base-token',APP,'--table-id',tid,'--field-id',fq_id,'--json', json.dumps(spec, ensure_ascii=False),'--yes'])
        if not u.get('ok'): print(day, '字段更新失败', json.dumps(u, ensure_ascii=False)[:120])
        newnames[r['qno']] = nm
        time.sleep(0.3)
    fq = run(['base','+form-questions-list','--base-token',APP,'--table-id',tid,'--form-id',fid])
    qlist = (fq.get('data') or {}).get('questions') or []
    pay = []
    for q in qlist:
        fq_id = q.get('id')
        if fq_id in id2q:
            r = next(x for x in qs if x['qno'] == id2q[fq_id])
            nm = newnames.get(r['qno']) or f"Q{r['qno']} {r['stem']}"
            rub = (r.get('rubric') or '').replace('\n',' ')
            desc = f"核验与补救：{rub}"[:400] if rub else '按当日验收清单逐项核验'
            pay.append({'id': fq_id, 'title': nm[:460], 'description': desc, 'required': False})
        elif str(q.get('title','')).startswith('学员姓名'):
            pay.append({'id': fq_id, 'title': '学员姓名', 'description': '请填写真实姓名，便于讲师批改反馈', 'required': True})
    pay.sort(key=lambda x: 0 if x['title'].startswith('学员姓名') else int(re.match(r'Q(\d+)', x['title']).group(1)))
    for i in range(0, len(pay), 10):
        u = run(['base','+form-questions-update','--base-token',APP,'--table-id',tid,'--form-id',fid,'--questions', json.dumps(pay[i:i+10], ensure_ascii=False)])
        if not u.get('ok'): print(day, '题目覆写失败', json.dumps(u, ensure_ascii=False)[:120])
        time.sleep(0.4)
    vl = run(['base','+view-list','--base-token',APP,'--table-id',tid])
    grid_v = next((v['id'] for v in (vl.get('data') or {}).get('views') or [] if v.get('type')=='grid'), None)
    og = ['学员姓名'] + [newnames[r['qno']] for r in qs if r['qno'] in newnames] + ['提交时间']
    of = ['学员姓名'] + [newnames[r['qno']] for r in qs if r['qno'] in newnames]
    if grid_v:
        run(['base','+view-set-visible-fields','--base-token',APP,'--table-id',tid,'--view-id',grid_v,'--json', json.dumps({'visible_fields': og}, ensure_ascii=False)]); time.sleep(0.35)
    run(['base','+view-set-visible-fields','--base-token',APP,'--table-id',tid,'--view-id',fid,'--json', json.dumps({'visible_fields': of}, ensure_ascii=False)]); time.sleep(0.35)
    print(f'{day} 验收日补齐 ({len(qs)} 项)', flush=True)
json.dump(state, open(ROOT + '/_exports/forms_state.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('done', flush=True)
