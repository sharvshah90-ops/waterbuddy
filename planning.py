"""Daily schedule and safe backup validation, independent of Streamlit."""
import json
from datetime import date
from hydration import AGE_GOALS

def plan_slots(start, end, interval, busy):
    if not 0 <= start < end <= 24 or interval not in (15,30,60,90,120,180):
        raise ValueError('Choose an end time later than the start time.')
    return [m for m in range(start*60,end*60,interval) if m//60 not in busy]

def reminder_due(enabled, hour, start, end, busy, remaining, elapsed, interval, stamp, snooze):
    return bool(enabled and start<=hour<end and hour not in busy and remaining>0
                and elapsed>=interval*60 and stamp>=snooze)

def restore_backup(raw, today):
    if len(raw)>2_000_000: raise ValueError('Backup is too large.')
    try: m=json.loads(raw)
    except (ValueError,UnicodeError): raise ValueError('This is not a readable JSON backup.')
    if not isinstance(m,dict) or m.get('age') not in AGE_GOALS: raise ValueError('Unknown age group.')
    def goal(g): return type(g) is int and 250<=g<=5000
    if not goal(m.get('goal')) or not isinstance(m.get('days'),dict) or len(m['days'])>366:
        raise ValueError('Invalid goal or history. Maximum 366 recorded days.')
    clean={}
    for day,row in m['days'].items():
        try: d=date.fromisoformat(day)
        except (TypeError,ValueError): raise ValueError('Invalid record date.')
        if d>date.fromisoformat(today) or not isinstance(row,dict) or not goal(row.get('goal')):
            raise ValueError('Invalid or future record.')
        logs=row.get('logs')
        if not isinstance(logs,list) or len(logs)>500: raise ValueError('Invalid drink log.')
        checked=[]
        for x in logs:
            if not isinstance(x,dict) or type(x.get('ml')) is not int or not 1<=x['ml']<=2000:
                raise ValueError('Invalid drink amount.')
            if not isinstance(x.get('time'),str) or not isinstance(x.get('source'),str):
                raise ValueError('Invalid drink details.')
            checked.append({'ml':x['ml'],'time':x['time'][:16],'source':x['source'][:80]})
        clean[day]={'goal':row['goal'],'logs':checked}
    return {'age':m['age'],'goal':m['goal'],'day':today,'days':clean}
