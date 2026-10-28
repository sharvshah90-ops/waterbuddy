import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from streamlit.testing.v1 import AppTest

at=AppTest.from_file(str(Path(__file__).resolve().parent / 'app.py'),default_timeout=30).run()
def clean(step):
 assert not at.exception, (step,[e.message for e in at.exception])
 print('PASS',step)
def button(label): return next(b for b in at.button if b.label==label)
def number(label): return next(b for b in at.number_input if b.label==label)
clean('Initial page renders')
button('+250 ml').click().run();clean('Quick logging')
assert at.session_state.model['days'][at.session_state.model['day']]['logs'][0]['ml']==250
number('My daily goal (ml)').set_value(1000).run();clean('Custom goal recalculates')
button('+250 ml').click().run();assert 'wave' in ' '.join(m.value for m in at.markdown);clean('50 percent mascot')
button('+250 ml').click().run();assert 'cheer' in ' '.join(m.value for m in at.markdown);clean('75 percent mascot')
button('+250 ml').click().run();assert len(at.success)>0;clean('100 percent completion')
button('Undo last log').click().run();clean('Undo')
button('New Day / Reset').click().run();assert len(at.warning)>0
button('Cancel reset').click().run();assert len(at.session_state.model['days'][at.session_state.model['day']]['logs'])==3;clean('Cancel reset preserves logs')
button('New Day / Reset').click().run();button('Yes, clear today').click().run()
assert len(at.session_state.model['days'][at.session_state.model['day']]['logs'])==0;clean('Confirm reset clears logs')
next(s for s in at.selectbox if s.label=='Age group').select('Children 4-8').run()
assert at.session_state.model['goal']==1200;clean('Age selection suggests goal')
number('Custom amount (ml)').set_value(175);button('Add custom amount').click().run()
assert at.session_state.model['days'][at.session_state.model['day']]['logs'][-1]['ml']==175;clean('Custom logging')
next(s for s in at.selectbox if s.label=='Container').select('Bottle').run()
next(s for s in at.selectbox if s.label=='Amount drunk').select('1/2').run()
button('Log 500 ml').click().run();clean('Container logging')
next(r for r in at.radio if r.label=='Explore').set_value('Progress').run();clean('Progress page and exports')
next(r for r in at.radio if r.label=='Explore').set_value('Rewards').run();clean('Rewards page')
next(r for r in at.radio if r.label=='Explore').set_value('About').run();clean('About page and sources')
from datetime import datetime, timezone
next(r for r in at.radio if r.label=='Explore').set_value('Home').run()
utc_hour=datetime.now(timezone.utc).hour
day_offset=12-utc_hour
number('Local UTC offset (hours)').set_value(float(day_offset)).run()
at.session_state.last_log=datetime.now(timezone.utc).timestamp()-7200
next(c for c in at.checkbox if c.label=='Show in-app reminders').check().run()
assert any('Your buddy is here' in i.value for i in at.info);clean('Due reminder appears while Home is active')
button('Snooze for 15 minutes').click().run()
assert not any('Your buddy is here' in i.value for i in at.info);clean('Snooze hides reminder')
night_offset=23-utc_hour
if night_offset>14: night_offset-=24
at.session_state.snooze=0
number('Local UTC offset (hours)').set_value(float(night_offset)).run()
assert not any('Your buddy is here' in i.value for i in at.info);clean('Quiet hours suppress reminder')
number('Local UTC offset (hours)').set_value(float(day_offset)).run()
number('My daily goal (ml)').set_value(250).run()
button('+250 ml').click().run()
at.session_state.last_log=datetime.now(timezone.utc).timestamp()-7200
at.run()
assert not any('Your buddy is here' in i.value for i in at.info);clean('Completed goal suppresses reminder')
next(r for r in at.radio if r.label=='Explore').set_value('Rewards').run()
next(s for s in at.selectbox if s.label=="Choose your buddy's celebration").select('Party hat').run()
assert any('celebration accessory' in s.value for s in at.success);clean('Completion unlocks cosmetic reward')
print('INTERFACE CHECKS PASSED')





