# -*- coding: utf-8 -*-
import json, subprocess, time, re
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
                                rubric='', score='', kaodian='当日产出验收'))
            i = j; continue
        i += 1
    return out
for day, p in [('W3D5','W3-物料/W3D5-原型评审I/06-分层习题.md'),('W4D5','W4-物料/W4D5-PRD评审大会/06-分层习题.md'),('W7D1','W7-物料/W7D1-行业纵深/06-分层习题.md')]:
    sp = extract_special(ROOT + '/' + p, day)
    if sp: by_day[day] = sp
order_ok = share_ok = stem_ok = 0
bad = []
for st in sorted(state, key=lambda x: (int(x['day'][1]), x['day'][3])):
    day, tid, fid = st['day'], st['table_id'], st['form_id']
    qs = sorted(by_day.get(day, []), key=lambda x: x['qno'])
    expect = [r['qno'] for r in qs]
    # 1) 分享放开（一次只传一个字段）
    u = run(['base','+form-share-update','--base-token',APP,'--table-id',tid,'--form-id',fid,'--access-scope','anyone'])
    sg = run(['base','+form-share-get','--base-token',APP,'--table-id',tid,'--form-id',fid])
    sd = sg.get('data') or {}
    so = sd.get('access_scope') == 'anyone' and bool(sd.get('share_url'))
    share_ok += so
    if sd.get('share_url'): st['url'] = sd['share_url']
    # 2) 顺序核对（按真实题号）
    vl = run(['base','+view-list','--base-token',APP,'--table-id',tid])
    grid_seq = form_seq = None
    for v in (vl.get('data') or {}).get('views') or []:
        gv = run(['base','+view-get-visible-fields','--base-token',APP,'--table-id',tid,'--view-id',v['id']])
        vf = (gv.get('data') or {}).get('visible_fields') or []
        seq = [int(m.group(1)) for x in vf if (m := re.match(r'^Q(\d+)', str(x)))]
        if v.get('type') == 'grid': grid_seq = seq
        elif v.get('type') == 'form': form_seq = seq
    ok_ord = (grid_seq == expect) and (form_seq == expect)
    order_ok += ok_ord
    # 3) 题干核对
    fl = run(['base','+field-list','--base-token',APP,'--table-id',tid])
    fs = (fl.get('data') or {}).get('fields') or []
    stems = sum(1 for f in fs if re.match(r'^Q\d+', str(f.get('name',''))) and len(str(f.get('name',''))) > 12)
    s_ok = stems >= len(expect)
    stem_ok += s_ok
    if not (so and ok_ord and s_ok):
        bad.append((day, f'share={so} order={ok_ord} stem={s_ok} expect={expect} grid={grid_seq} form={form_seq}'))
    print(f'{day}: share={so} order={ok_ord} stem={s_ok} ({stems}/{len(expect)})', flush=True)
    time.sleep(0.3)
json.dump(list(state.values()), open(ROOT + '/_exports/forms_state.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\n分享 anyone: {share_ok}/40 | 顺序正确: {order_ok}/40 | 题干完整: {stem_ok}/40', flush=True)
print('异常:', bad if bad else '无', flush=True)
