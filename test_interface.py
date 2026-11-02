import sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from streamlit.testing.v1 import AppTest
at=AppTest.from_file(str(Path(__file__).resolve().parent / 'app.py'),default_timeout=30).run()
count=0
def check(label):
 global count
 assert not at.exception,[e.message for e in at.exception]
 count+=1;print('PASS',label,flush=True)
def btn(name):return next(b for b in at.button if b.label==name)
def num(name):return next(n for n in at.number_input if n.label==name)
def nav(name):next(r for r in at.radio if r.label=='Explore').set_value(name).run()
check('First visit shows setup instead of dashboard')
assert not at.radio
next(s for s in at.selectbox if s.label=='Age group').select('Children 4-8').run()
assert num('My daily goal (ml)').value==1200
check('Setup age changes suggested goal')
num('My daily goal (ml)').set_value(1000).run()
btn('Continue').click().run();num('Day starts at').set_value(9).run();num('Day ends at').set_value(8).run()
btn('Continue').click().run();assert at.error
check('Setup rejects invalid day')
num('Day ends at').set_value(21).run();at.multiselect[0].set_value([10,11]).run()
btn('Continue').click().run();btn('Back').click().run()
assert num('Day starts at').value==9
check('Back preserves routine')
btn('Continue').click().run();btn('Start tracking').click().run()
assert at.session_state.model['goal']==1000
assert not any(s.label=='Age group' for s in at.selectbox)
check('Home hides profile controls and keeps chosen goal')
btn('+250 ml').click().run();btn('+250 ml').click().run()
assert 'wave' in ' '.join(m.value for m in at.markdown)
check('Halfway feedback after setup')
nav('Settings');assert num('My daily goal (ml)').value==1000
assert num('Day starts at').value==9
check('Settings retains setup preferences')
num('My daily goal (ml)').set_value(2000).run();nav('Home')
assert at.session_state.model['goal']==2000
assert at.session_state.model['days'][at.session_state.model['day']]['logs'][0]['ml']==250
check('Settings changes goal without deleting water')
btn('+500 ml').click().run();btn('Undo last log').click().run()
check('Quick logging and undo')
btn('New Day / Reset').click().run();btn('Cancel reset').click().run()
assert len(at.session_state.model['days'][at.session_state.model['day']]['logs'])==2
check('Cancel reset preserves records')
btn('New Day / Reset').click().run();btn('Yes, clear today').click().run()
assert not at.session_state.model['days'][at.session_state.model['day']]['logs']
check('Confirm reset clears today')
num('Custom amount (ml)').set_value(175);btn('Add custom amount').click().run()
assert at.session_state.model['days'][at.session_state.model['day']]['logs'][-1]['ml']==175
check('Custom logging')
nav('Plan');assert any('A plan' in h.value for h in at.subheader)
check('Plan available with persisted routine')
nav('Progress');check('Progress and exports')
nav('Rewards');check('Rewards')
nav('About');check('About')
nav('Settings');check('Settings after every page')
assert num('Day starts at').value==9
next(s for s in at.selectbox if s.label=='Age group').select('Teens and adults 14-64').run()
assert at.session_state.model['goal']==2250
check('Settings age selection updates preset')
# Make a due reminder at local noon regardless of host clock.
offset=float(12-datetime.now(timezone.utc).hour)
num('Local UTC offset (hours)').set_value(offset).run()
at.multiselect[0].set_value([]).run()
next(c for c in at.checkbox if c.label=='Show in-app reminders').check().run()
at.session_state.last_log=datetime.now(timezone.utc).timestamp()-7200
nav('Home');assert any('Your buddy is here' in x.value for x in at.info)
check('Reminder respects Settings preferences')
btn('Snooze for 15 minutes').click().run()
assert not any('Your buddy is here' in x.value for x in at.info)
check('Snooze after reorganising controls')
print(f'{count} interface checks passed',flush=True)

