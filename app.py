"""WaterBuddy FA2. Run with: python -m streamlit run app.py"""
from datetime import datetime, timezone, timedelta
import csv
import io
import json
import base64
import math
import struct
import wave
from planning import plan_slots, reminder_due, restore_backup
import streamlit as st
from hydration import (AGE_GOALS,TIPS,new_model,ensure_day,current,add_water,
                       undo,reset_today,container_amount,milestone,statistics,weekly,day_points)

def alarm_wav():
    out=io.BytesIO()
    with wave.open(out,'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b''.join(struct.pack('<h',int(6500*math.sin(2*math.pi*660*i/16000)*(1-i/8000))) for i in range(8000)))
    return out.getvalue()

st.set_page_config(page_title="WaterBuddy",page_icon="💧",layout="wide")
st.markdown("""<style>
:root{--ink:#153c35;--teal:#12695a;--mint:#d9f2e7;--lavender:#eae4fa}
.stApp{background:#f5f6f0;color:var(--ink)}
.block-container{max-width:1180px;padding-top:3.5rem;padding-bottom:3rem}
h1,h2,h3{color:var(--ink)!important;letter-spacing:-.045em}
h1{font-size:3.1rem!important;font-weight:800!important}
h3{font-size:1.35rem!important}
[data-testid="stSidebar"]{background:#e9efe6;border-right:1px solid #dce4d7}
[data-testid="stSidebar"] h3{font-size:1.6rem!important}
[data-testid="stMetric"]{background:#fff;border:1px solid #e2e7dc;border-radius:20px;padding:20px 22px;box-shadow:0 6px 20px #123d4904}
[data-testid="stMetricValue"]{color:var(--ink)!important;font-weight:650;font-size:1.9rem}
[data-testid="stMetricLabel"]{color:#567166!important;font-size:.8rem}
.stButton>button,.stDownloadButton>button{border-radius:14px;min-height:48px;border:1px solid #d4dfd1;font-weight:650;background:#fff;color:var(--ink);transition:transform .15s,box-shadow .15s}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#12695a;transform:translateY(-1px);box-shadow:0 4px 12px #12695a12}
.stButton>button[kind="primary"]{background:#12695a;color:white;border:1px solid #12695a}
[data-testid="stRadio"]>div[role="radiogroup"]{gap:6px;background:#e7ece2;padding:6px;border-radius:17px;width:fit-content;margin-bottom:16px}
[data-testid="stRadio"] label{padding:8px 20px!important;margin:0!important;border-radius:12px;color:#52685b!important;font-weight:600}
[data-testid="stRadio"] label:has(input:checked){background:#fff;box-shadow:0 2px 8px #19392b12;color:#153c35!important}
[data-testid="stRadio"] label>div:first-child{display:none}
[data-testid="stExpander"]{border:1px solid #d9e2d3;border-radius:16px;background:#ffffff70}
[data-testid="stForm"]{background:#fff;border:1px solid #e2e7dc;border-radius:18px}
[data-testid="stProgressBar"] [role="progressbar"]{border-radius:10px}
.eyebrow{font-size:11px;font-weight:750;letter-spacing:.17em;color:#62826b;margin-bottom:5px}
.buddy{display:flex;align-items:center;justify-content:space-between;gap:24px;background:linear-gradient(125deg,#d9f2e7,#e4f1df 60%,#ede8fb);border-radius:28px;padding:32px 40px;margin:10px 0 20px;overflow:hidden}
.buddy .hero-label{font-size:11px;font-weight:750;letter-spacing:.14em;color:#527968;margin:0 0 12px}
.buddy strong{font-size:68px;line-height:1.05;color:#153c35;letter-spacing:-.06em}
.buddy p{color:#456b59;margin:10px 0;font-size:14px}
.buddy .hero-title{font-size:23px;font-weight:700;color:#153c35;letter-spacing:-.035em}
.ring{width:170px;height:170px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.ring-inner{width:148px;height:148px;background:#edf8ea;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:inset 0 0 30px #ffffff90}
.ring img{width:116px;filter:drop-shadow(0 9px 7px #12695a18)}
.status-strip{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0 6px}
.status-pill{background:#eee9fa;border-radius:30px;padding:7px 14px;color:#665580;font-size:12px;font-weight:600}
@media(max-width:700px){.block-container{padding:3rem 1rem 2rem}.buddy{padding:24px;gap:14px;flex-wrap:wrap}.buddy strong{font-size:52px}.ring{width:145px;height:145px}.ring-inner{width:125px;height:125px}.ring img{width:100px}h1{font-size:2.4rem!important}[data-testid="stRadio"] label{padding:7px 10px!important}}
@media(prefers-reduced-motion:reduce){.stButton>button{transition:none}}
[data-testid="stSidebar"] [data-testid="stRadio"]>div[role="radiogroup"]{width:100%;background:transparent;padding:0;gap:6px}
[data-testid="stSidebar"] [data-testid="stRadio"] label{width:100%;padding:11px 18px!important}
</style>""",unsafe_allow_html=True)

def now():
    return datetime.now(timezone(timedelta(hours=st.session_state.get("utc_offset",5.5))))

if "model" not in st.session_state:
    st.session_state.model=new_model(now().date().isoformat())
    st.session_state.age=st.session_state.model["age"]
    st.session_state.goal=st.session_state.model["goal"]
    st.session_state.last_log=datetime.now(timezone.utc).timestamp()
    st.session_state.snooze=0
if "pending_profile" in st.session_state:
    st.session_state.age,st.session_state.goal=st.session_state.pop("pending_profile")
model=st.session_state.model
ensure_day(model,now().date().isoformat())

def age_changed():
    model["age"]=st.session_state.age
    st.session_state.goal=AGE_GOALS[model["age"]]
    goal_changed()

def goal_changed():
    model["goal"]=int(st.session_state.goal)
    model["days"][model["day"]]["goal"]=model["goal"]

def log(amount,source):
    ensure_day(model,now().date().isoformat())
    add_water(model,amount,now().strftime("%H:%M:%S"),source)
    st.session_state.last_log=datetime.now(timezone.utc).timestamp()
    st.session_state.snooze=0

# Keep preferences when their widgets are not displayed on the current page.
for setting in ("age","goal","glass","bottle","reminders","interval","sound_alarm","day_start","day_end","busy_hours","utc_offset"):
    if setting in st.session_state:
        st.session_state[setting]=st.session_state[setting]

def profile_settings():
    st.selectbox("Age group",list(AGE_GOALS),key="age",on_change=age_changed)
    st.caption("Suggested starting goal: {:,} ml".format(AGE_GOALS[model["age"]]))
    st.number_input("My daily goal (ml)",min_value=250,max_value=5000,step=50,key="goal",on_change=goal_changed)
    with st.expander("About your goal"):
        st.caption("These are editable classroom logging goals, not medical prescriptions. Ask a parent or clinician if you need help choosing one.")

def container_settings():
    with st.expander("My containers"):
        st.number_input("Glass size (ml)",100,1000,300,25,key="glass")
        st.number_input("Bottle size (ml)",250,2000,1000,50,key="bottle")

def routine_settings():
    st.checkbox("Show in-app reminders",key="reminders")
    st.selectbox("Reminder interval (minutes)",[15,30,60,90,120,180],index=2,key="interval")
    st.checkbox("Sound alarm when due",key="sound_alarm")
    st.caption("Tap play below once to test your sound. Your browser may block automatic audio. Keep Home open and connected for alarms; closed-tab alarms are not supported.")
    st.audio(alarm_wav(),format="audio/wav")
    st.number_input("Day starts at",0,22,7,key="day_start")
    st.number_input("Day ends at",1,24,22,key="day_end")
    st.multiselect("Busy hours to skip",list(range(24)),format_func=lambda h:f"{h:02d}:00–{h+1:02d}:00",key="busy_hours")
    st.caption("Reminders pause outside your selected day and during busy hours. See your schedule on Plan; edit it here in Settings.")
    st.number_input("Local UTC offset (hours)",-12.0,14.0,5.5,0.5,key="utc_offset")
    st.caption("Default: India UTC +5:30. Changing the clock can change the recorded date.")

if not st.session_state.get("setup_done",False):
    step=st.session_state.get("setup_step",0)
    st.markdown('<div class="eyebrow">WELCOME TO WATERBUDDY</div>',unsafe_allow_html=True)
    st.title("Let's make it yours.")
    st.write("A quick setup, then your daily dashboard is ready.")
    st.progress((step+1)/3,text=f"Step {step+1} of 3 · "+["Your goal","Your routine","Ready to start"][step])
    if step==0:
        st.subheader("Choose your starting goal")
        profile_settings()
        st.caption("You can change these details later in Settings.")
    elif step==1:
        st.subheader("Make space in your day")
        routine_settings()
    else:
        st.subheader("Your setup at a glance")
        st.write(f"Age group: {model['age']}")
        st.write(f"Daily logging goal: {model['goal']:,} ml")
        st.write(f"Day: {st.session_state.get('day_start',7):02d}:00 to {st.session_state.get('day_end',22):02d}:00")
        st.write(f"Reminder spacing: {st.session_state.get('interval',60)} minutes")
        st.caption("Optional alarms work while Home is open and connected. No account is needed; download a backup to keep your records.")
    back,forward=st.columns(2)
    if step>0 and back.button("Back",use_container_width=True):
        st.session_state.setup_step=step-1; st.rerun()
    if forward.button("Start tracking" if step==2 else "Continue",type="primary",use_container_width=True):
        if step==1 and st.session_state.get('day_start',7)>=st.session_state.get('day_end',22):
            st.error("Choose an end time later than your start time.")
        elif step<2:
            st.session_state.setup_step=step+1; st.rerun()
        else:
            st.session_state.setup_done=True; st.rerun()
    st.stop()

with st.sidebar:
    st.markdown("### 💧 WaterBuddy")
    st.caption("A little progress, every day.")
    nav=st.radio("Explore",["Home","Plan","Progress","Rewards","Settings","About"],label_visibility="collapsed")
    st.divider()
    st.caption(f"YOUR DAILY GOAL · {model['goal']:,} ml")
    st.caption("Change your goal, routine or reminders in Settings.")
    st.caption("Records are stored in this session. Download a backup in Progress to keep them.")

st.markdown('<div class="eyebrow">DAILY WATER TRACKER</div>',unsafe_allow_html=True)
st.title("WaterBuddy")
st.caption("Your water. Your routine. One easy place to keep track.")
p=current(model); stats=statistics(model)
start=st.session_state.get("day_start",7); end=st.session_state.get("day_end",22)
busy=st.session_state.get("busy_hours",[])
try: slots=plan_slots(start,end,st.session_state.get("interval",60),busy)
except ValueError:
    slots=[]; st.warning("Your day must end later than it starts. Fix the times in Settings to enable your plan.")

def mascot_svg(state,fill):
    mouth={"ready":"M64 101 Q80 106 96 101","smile":"M63 99 Q80 119 97 99",
           "wave":"M60 97 Q80 124 100 97","cheer":"M60 96 Q80 128 100 96",
           "complete":"M59 95 Q80 130 101 95"}[state]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="168" height="178" viewBox="0 0 160 170" role="img" aria-label="Water drop buddy {state}">
    <path d="M80 9 C70 37 24 63 24 103 A56 56 0 0 0 136 103 C136 63 90 37 80 9Z" fill="#62c8a7" stroke="#25866c" stroke-width="4"/>
    <ellipse cx="58" cy="83" rx="5" ry="7" fill="#123d49"/><ellipse cx="102" cy="83" rx="5" ry="7" fill="#123d49"/>
    <ellipse cx="47" cy="99" rx="9" ry="5" fill="#c8f4df"/><ellipse cx="113" cy="99" rx="9" ry="5" fill="#c8f4df"/>
    <path d="{mouth}" fill="none" stroke="#123d49" stroke-width="4" stroke-linecap="round"/>
    <path d="M23 115 Q8 110 12 {75 if state in ('wave','cheer','complete') else 126}" fill="none" stroke="#087e8b" stroke-width="5" stroke-linecap="round"/>
    <path d="M137 115 Q152 110 148 {75 if state in ('cheer','complete') else 126}" fill="none" stroke="#087e8b" stroke-width="5" stroke-linecap="round"/></svg>'''

if nav=="Home":
    st.caption(now().strftime("%A %d %B %Y")+" · Log only what you drank")
    state,message=milestone(p["percent"])
    svg=base64.b64encode(mascot_svg(state,p["fill"]).encode()).decode()
    st.markdown(f'<div class="buddy"><div><p class="hero-label">YOUR DAILY HYDRATION</p><div class="hero-title">Every little sip counts.</div><strong>{p["percent"]:.0f}<span style="font-size:32px">%</span></strong><p>{p["total"]:,} of {model["goal"]:,} ml logged today</p></div><div class="ring" style="background:conic-gradient(#25866c {p["fill"]*360:.1f}deg,#c5ddcd 0deg)"><div class="ring-inner"><img alt="Water drop buddy {state}" src="data:image/svg+xml;base64,{svg}"></div></div></div>',unsafe_allow_html=True)
    st.subheader("Log water")
    q1,q2,q3=st.columns(3)
    q1.button("+100 ml",use_container_width=True,on_click=log,args=(100,"Small glass"))
    q3.button("+500 ml",use_container_width=True,on_click=log,args=(500,"Bottle"))
    q2.button("+250 ml",type="primary",use_container_width=True,on_click=log,args=(250,"Quick log"))
    a,b,c=st.columns(3)
    a.metric("Water logged",f'{p["total"]:,} ml')
    b.metric("Still to go",f'{p["remaining"]:,} ml')
    c.metric("My daily goal",f'{model["goal"]:,} ml')
    st.progress(p["fill"],text=message)
    st.caption(f'Suggested starting goal: {AGE_GOALS[model["age"]]:,} ml · Your intake is {p["total"]/AGE_GOALS[model["age"]]*100:.1f}% of that starting goal. Your selected goal is {model["goal"]:,} ml.')
    if p["percent"]>=100: st.success("Daily goal complete. Rewards are capped; more drinking is not a challenge.")
    st.markdown(f'<div class="status-strip"><span class="status-pill">{stats["streak"]} day streak</span><span class="status-pill">{stats["points"]} AquaPoints</span><span class="status-pill">Your own pace</span></div>',unsafe_allow_html=True)
    with st.expander("Add a custom amount"):
        with st.form("custom",clear_on_submit=False):
            amount=st.number_input("Custom amount (ml)",1,2000,250,1)
            if st.form_submit_button("Add custom amount"):
                log(amount,"Custom"); st.rerun()
    with st.expander("Log from my glass or bottle"):
        cx,cy=st.columns(2)
        container=cx.selectbox("Container",["Glass","Bottle"])
        fraction=cy.selectbox("Amount drunk",["1/4","1/2","3/4","Full"])
        f={"1/4":.25,"1/2":.5,"3/4":.75,"Full":1.0}[fraction]
        size=st.session_state.get(container.lower(),300 if container=="Glass" else 1000)
        value=container_amount(size,f)
        st.caption(f"{size} ml × {fraction} = {value} ml (rounded to nearest ml)")
        st.button(f"Log {value} ml",on_click=log,args=(value,f"{fraction} {container.lower()}"))
    u,r=st.columns(2)
    u.button("Undo last log",disabled=not model["days"][model["day"]]["logs"],on_click=undo,args=(model,),use_container_width=True)
    if r.button("New Day / Reset",use_container_width=True): st.session_state.confirm_reset=True
    if st.session_state.get("confirm_reset"):
        st.warning("Clear today's water logs and today's earned points? Earlier dates and your settings will stay. Resetting does not create another calendar day.")
        yes,no=st.columns(2)
        if yes.button("Yes, clear today"):
            reset_today(model); st.session_state.confirm_reset=False; st.session_state.last_log=datetime.now(timezone.utc).timestamp(); st.rerun()
        if no.button("Cancel reset"):
            st.session_state.confirm_reset=False; st.rerun()
    next_mark=next((m for m in (25,50,75,100) if p["percent"]<m),None)
    if next_mark:
        st.info(f"Mini mission: reach {next_mark}% at your own pace. {max(0,round(model['goal']*next_mark/100-p['total'])):,} ml to that checkpoint.")
    else: st.info("All four checkpoints reached today. Your buddy is celebrating!")
    @st.fragment(run_every="60s")
    def reminder_panel():
        if ensure_day(model,now().date().isoformat()): st.rerun(scope="app")
        stamp=datetime.now(timezone.utc).timestamp()
        elapsed=stamp-st.session_state.last_log
        if reminder_due(st.session_state.get("reminders"),now().hour,start,end,busy,current(model)["remaining"],elapsed,st.session_state.get("interval",60),stamp,st.session_state.snooze):
            st.info(f"Your buddy is here: {current(model)['remaining']:,} ml remains toward your chosen goal. Drink at a comfortable pace.")
            if st.session_state.get("sound_alarm") and stamp-st.session_state.get("last_alarm",0)>=st.session_state.get("interval",60)*60:
                st.audio(alarm_wav(),format="audio/wav",autoplay=True)
                st.session_state.last_alarm=stamp
            if st.button("Snooze for 15 minutes"):
                st.session_state.snooze=stamp+900; st.rerun()
    reminder_panel()
    st.caption("Tip of the day: "+TIPS[now().date().toordinal()%len(TIPS)])

elif nav=="Settings":
    st.subheader("Your settings")
    st.write("Adjust your details here. Changes save for this session and your logged drinks stay intact.")
    with st.expander("Profile and daily goal",expanded=True): profile_settings()
    with st.expander("Routine and reminders"): routine_settings()
    container_settings()
    st.caption("Your preferences stay in this session. Water backups restore water records; schedule preferences are kept separately.")

elif nav=="Plan":
    st.subheader("A plan that fits your day")
    st.write("Set your waking hours, reminder spacing and busy hours in Settings. The plan leaves out lessons, work or travel hours you want to keep quiet.")
    st.caption("This is a rule-based schedule from your choices, not an AI health assessment. It never increases your chosen goal.")
    if slots:
        minute=now().hour*60+now().minute
        upcoming=[m for m in slots if m>minute]
        a,b,c=st.columns(3)
        a.metric("Planned check-ins",len(slots))
        b.metric("Next planned check-in",f"{upcoming[0]//60:02d}:{upcoming[0]%60:02d}" if upcoming else "Tomorrow")
        c.metric("Busy hours skipped",len(set(busy)&set(range(start,end))))
        elapsed_slots=sum(m<=minute for m in slots)
        expected=round(model['goal']*elapsed_slots/len(slots))
        st.progress(min(1,elapsed_slots/len(slots)),text="Your planned day")
        st.write(f"Schedule guide: about {expected:,} ml by this point, compared with {p['total']:,} ml logged. This is a flexible planning guide, not an instruction to catch up quickly.")
        st.dataframe([{"Time":f"{m//60:02d}:{m%60:02d}","Check-in":"Earlier" if m<=minute else "Upcoming"} for m in slots],hide_index=True,use_container_width=True)
        st.caption("These are planned check-ins, not proof that water was drunk. Live reminders depend on time since your last log, snooze and whether Home is open; they may occur after the scheduled slot.")
        st.download_button("Download my plan",json.dumps({"start":start,"end":end,"busy_hours":busy,"interval":st.session_state.get("interval",60),"check_ins":[f"{m//60:02d}:{m%60:02d}" for m in slots]},indent=2),"waterbuddy_plan.json","application/json")
    else: st.info("No available check-ins. Adjust your day times or remove some busy hours.")

elif nav=="Progress":
    st.subheader("Your last seven calendar days")
    rows=weekly(model)
    st.bar_chart({"Date":[r["Date"] for r in rows],"Water logged (ml)":[r["Intake ml"] for r in rows]},x="Date",y="Water logged (ml)",color="#087e8b")
    recorded=[r for r in rows if r["Goal ml"] is not None]
    a,b,c=st.columns(3)
    a.metric("Completed days",f'{sum(r["Status"]=="Complete" for r in rows)} / 7')
    b.metric("Average on recorded days",f'{sum(r["Intake ml"] for r in recorded)/len(recorded):.0f} ml')
    c.metric("Best calendar streak",f'{stats["best"]} days')
    st.caption("No record means no saved session data for that date; it is not proof that you drank zero. Averages use recorded days only.")
    st.dataframe(rows,use_container_width=True,hide_index=True)
    st.subheader("Today's drink log")
    logs=model["days"][model["day"]]["logs"]
    if logs: st.dataframe(logs,use_container_width=True,hide_index=True)
    else: st.info("Your first drink will appear here.")
    out=io.StringIO(); writer=csv.DictWriter(out,fieldnames=["Date","Intake ml","Goal ml","Status"]); writer.writeheader(); writer.writerows(rows)
    st.download_button("Download weekly CSV",out.getvalue(),"waterbuddy_week.csv","text/csv")
    st.download_button("Download session backup",json.dumps(model,indent=2),"waterbuddy_backup.json","application/json")
    st.subheader("Restore a saved backup")
    st.caption("Restore replaces this session's water records. Download a backup first if you want to keep them. Schedule preferences stay as they are.")
    uploaded=st.file_uploader("WaterBuddy JSON backup",type=["json"])
    approved=st.checkbox("Replace my current water records with this backup")
    if st.button("Restore backup",disabled=not uploaded or not approved):
        try:
            restored=restore_backup(uploaded.getvalue(),now().date().isoformat())
            st.session_state.model=restored
            st.session_state.pending_profile=(restored['age'],restored['goal'])
            st.rerun()
        except ValueError as e: st.error(str(e))
    st.subheader("Session summary")
    st.write(f"{p['total']:,} ml today across {len(logs)} drinks. {stats['streak']} day current streak and {stats['best']} day best streak.")

elif nav=="Rewards":
    st.subheader("Your progress and badges")
    a,b,c=st.columns(3)
    a.metric("AquaPoints this session",stats["points"])
    b.metric("Current calendar streak",f'{stats["streak"]} days')
    c.metric("Points today",f'{day_points(model["days"][model["day"]])} / 125')
    st.write("Earn one point per whole percent of your goal, up to 100 points, plus 25 on completion. Points come from current records, so undo, reset and goal changes recalculate them.")
    for mark,title in [(50,"Halfway Hero"),(75,"Steady Sipper"),(100,"Hydration Hero")]:
        st.write(("🏅 " if p["percent"]>=mark else "🔒 ")+title+f" · {mark}% of today's goal")
    if p["percent"]>=100:
        accessory=st.selectbox("Choose your buddy's celebration",["Golden star","Party hat","Flower crown"])
        st.success({"Golden star":"⭐","Party hat":"🎉","Flower crown":"🌸"}[accessory]+" Your buddy earned a celebration accessory today!")
    st.caption("Streaks use consecutive real dates with a completed saved goal. No sample streaks, points or history are preloaded.")

else:
    st.subheader("About WaterBuddy")
    st.write("WaterBuddy is a Python learning project. Its age presets are illustrative starting goals carried forward from the storyboard: 1,200 / 1,700 / 2,250 / 1,800 ml. They are not universal health standards or personalised drinking-water prescriptions.")
    st.write("EFSA reference values describe TOTAL water from food and all drinks: 1,600 ml for ages 4-8; 1,900 ml for girls and 2,100 ml for boys aged 9-13; and 2,000 ml for females and 2,500 ml for males aged 14 and over, including older adults. This app records only the water you log. Do not treat a shortfall against a total-water reference as an instruction to drink that much plain water.")
    st.write("Needs vary with activity, climate and health. Follow individual medical advice, including any fluid restriction. Children should choose a suitable goal with an adult. Spread drinks through the day.")
    st.markdown("[EFSA reference values](https://www.efsa.europa.eu/sites/default/files/2017_09_DRVs_summary_report.pdf) · [CDC water guidance](https://www.cdc.gov/healthy-weight-growth/water-healthy-drinks/)")
    st.write("Built with Streamlit widgets and session_state. A Python-drawn SVG drop replaces desktop Turtle animation so the same mascot reactions work in a browser on Streamlit Cloud.")
    st.caption("FA1 storyboard and FA2 app share the same six sections, controls, formulas, reward rules and reset behavior.")


