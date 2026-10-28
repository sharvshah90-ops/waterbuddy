"""WaterBuddy FA2. Run with: python -m streamlit run app.py"""
from datetime import datetime, timezone, timedelta
import csv
import io
import json
import base64
import streamlit as st
from hydration import (AGE_GOALS,TIPS,new_model,ensure_day,current,add_water,
                       undo,reset_today,container_amount,milestone,statistics,weekly,day_points)

st.set_page_config(page_title="WaterBuddy",page_icon="💧",layout="wide")
st.markdown("""<style>
.stApp {background:#f4fafb;color:#173c48}
.block-container {max-width:1120px;padding-top:4rem;padding-bottom:2rem}
h1,h2,h3 {color:#123d49!important;letter-spacing:-.035em}
[data-testid="stMetric"] {background:white;border:1px solid #d8e9ed;border-radius:16px;padding:14px}
[data-testid="stSidebar"] {background:#eaf5f6}
.stButton>button {border-radius:12px;min-height:46px;font-weight:600}
.stButton>button[kind="primary"] {background:#087e8b;border:0;color:white}
.eyebrow {font-size:12px;font-weight:700;letter-spacing:.14em;color:#26737c}
.buddy {display:flex;align-items:center;justify-content:center;gap:28px;flex-wrap:wrap;
background:white;border:1px solid #d8e9ed;border-radius:24px;padding:24px;margin:12px 0}
.buddy p {margin:4px 0;color:#406671}.buddy strong {font-size:38px;color:#123d49}
</style>""",unsafe_allow_html=True)

def now():
    return datetime.now(timezone(timedelta(hours=st.session_state.get("utc_offset",5.5))))

if "model" not in st.session_state:
    st.session_state.model=new_model(now().date().isoformat())
    st.session_state.age=st.session_state.model["age"]
    st.session_state.goal=st.session_state.model["goal"]
    st.session_state.last_log=datetime.now(timezone.utc).timestamp()
    st.session_state.snooze=0
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

with st.sidebar:
    st.markdown("### 💧 WaterBuddy")
    st.caption("Your daily hydration companion")
    st.selectbox("Age group",list(AGE_GOALS),key="age",on_change=age_changed)
    st.caption("Suggested starting goal: {:,} ml".format(AGE_GOALS[model["age"]]))
    st.number_input("My daily goal (ml)",min_value=250,max_value=5000,step=50,key="goal",on_change=goal_changed)
    st.caption("Classroom presets are editable logging goals, not medical prescriptions. Ask a parent or clinician if you need help choosing a goal.")
    with st.expander("My containers"):
        st.number_input("Glass size (ml)",100,1000,300,25,key="glass")
        st.number_input("Bottle size (ml)",250,2000,1000,50,key="bottle")
    with st.expander("Reminders and clock"):
        st.checkbox("Show in-app reminders",key="reminders")
        st.selectbox("Reminder interval (minutes)",[60,120,180],key="interval")
        st.caption("Quiet hours: 22:00 to 07:00. Reminders work only while Home is open and connected; no background notifications.")
        st.number_input("Local UTC offset (hours)",-12.0,14.0,5.5,0.5,key="utc_offset")
        st.caption("Default: India UTC +5:30. Changing the clock can change the recorded date.")
    st.caption("No account needed. Records stay in this Streamlit session on the server. A disconnected or restarted session may lose them. Download a backup below.")

st.markdown('<div class="eyebrow">DAILY WATER TRACKER</div>',unsafe_allow_html=True)
st.title("WaterBuddy")
st.write("Log your drinks and see how you are doing today.")
nav=st.radio("Explore",["Home","Progress","Rewards","About"],horizontal=True,label_visibility="collapsed")
p=current(model); stats=statistics(model)

def mascot_svg(state,fill):
    mouth={"ready":"M64 101 Q80 106 96 101","smile":"M63 99 Q80 119 97 99",
           "wave":"M60 97 Q80 124 100 97","cheer":"M60 96 Q80 128 100 96",
           "complete":"M59 95 Q80 130 101 95"}[state]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="168" height="178" viewBox="0 0 160 170" role="img" aria-label="Water drop buddy {state}">
    <path d="M80 9 C70 37 24 63 24 103 A56 56 0 0 0 136 103 C136 63 90 37 80 9Z" fill="#35bfd1" stroke="#087e8b" stroke-width="4"/>
    <ellipse cx="58" cy="83" rx="5" ry="7" fill="#123d49"/><ellipse cx="102" cy="83" rx="5" ry="7" fill="#123d49"/>
    <ellipse cx="47" cy="99" rx="9" ry="5" fill="#a4e6ec"/><ellipse cx="113" cy="99" rx="9" ry="5" fill="#a4e6ec"/>
    <path d="{mouth}" fill="none" stroke="#123d49" stroke-width="4" stroke-linecap="round"/>
    <path d="M23 115 Q8 110 12 {75 if state in ('wave','cheer','complete') else 126}" fill="none" stroke="#087e8b" stroke-width="5" stroke-linecap="round"/>
    <path d="M137 115 Q152 110 148 {75 if state in ('cheer','complete') else 126}" fill="none" stroke="#087e8b" stroke-width="5" stroke-linecap="round"/></svg>'''

if nav=="Home":
    st.caption(now().strftime("%A %d %B %Y")+" · Log only what you drank")
    a,b,c=st.columns(3)
    a.metric("Water logged",f'{p["total"]:,} ml')
    b.metric("Still to go",f'{p["remaining"]:,} ml')
    c.metric("My daily goal",f'{model["goal"]:,} ml')
    state,message=milestone(p["percent"])
    svg=base64.b64encode(mascot_svg(state,p["fill"]).encode()).decode()
    st.markdown(f'<div class="buddy"><img width="168" alt="Water drop buddy {state}" src="data:image/svg+xml;base64,{svg}"><div><p>YOUR DAILY WATER BATTERY</p><strong>{p["percent"]:.1f}%</strong><p>{p["total"]:,} / {model["goal"]:,} ml</p></div></div>',unsafe_allow_html=True)
    st.progress(p["fill"],text=message)
    st.caption(f'Suggested starting goal: {AGE_GOALS[model["age"]]:,} ml · Your intake is {p["total"]/AGE_GOALS[model["age"]]*100:.1f}% of that starting goal. Your selected goal is {model["goal"]:,} ml.')
    if p["percent"]>=100: st.success("Daily goal complete. Rewards are capped; more drinking is not a challenge.")
    st.subheader("Log water")
    x,y=st.columns([1,2])
    x.button("+250 ml",type="primary",use_container_width=True,on_click=log,args=(250,"Quick log"))
    with y:
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
        if (st.session_state.get("reminders") and 7<=now().hour<22 and current(model)["remaining"]>0
            and elapsed>=st.session_state.get("interval",60)*60 and stamp>=st.session_state.snooze):
            st.info(f"Your buddy is here: {current(model)['remaining']:,} ml remains toward your chosen goal. Drink at a comfortable pace.")
            if st.button("Snooze for 15 minutes"):
                st.session_state.snooze=stamp+900; st.rerun()
    reminder_panel()
    st.caption("Tip of the day: "+TIPS[now().date().toordinal()%len(TIPS)])

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
    st.caption("Backups preserve a readable record. This version does not restore backups into the app.")

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
    st.caption("FA1 storyboard and FA2 app share the same four sections, controls, formulas, reward rules and reset behavior.")

