"""Pure Python calculations and state for WaterBuddy. No web dependencies."""
from datetime import date, timedelta
import math

AGE_GOALS = {"Children 4-8": 1200, "Young people 9-13": 1700,
             "Teens and adults 14-64": 2250, "Older adults 65+": 1800}
TIPS = ["Keep a reusable bottle where you can see it.",
        "Try having water with meals.", "Log the amount you actually drank.",
        "Spread drinks through the day; there is no need to catch up quickly.",
        "A smaller glass can make logging easier."]

def progress(total, goal):
    if not math.isfinite(goal) or goal <= 0 or total < 0 or not math.isfinite(total):
        raise ValueError("Total must be non-negative and goal must be positive.")
    return {"total": total, "remaining": max(0, goal-total),
            "percent": total/goal*100, "fill": min(1.0, total/goal)}

def milestone(percent):
    if percent >= 100: return "complete", "Goal complete! Enjoy your achievement. No extra points for more water."
    if percent >= 75: return "cheer", "75% reached! Your buddy is cheering you on."
    if percent >= 50: return "wave", "Halfway there! Your buddy gives you a wave."
    if percent > 0: return "smile", "A good start. Keep logging at your own pace."
    return "ready", "Ready when you are. Log your first drink."

def new_model(day):
    return {"age": "Teens and adults 14-64", "goal": 2250,
            "day": day, "days": {day: {"goal":2250, "logs":[]}}}

def ensure_day(model, day):
    """Use real calendar dates. A new day never invents a completed day."""
    changed = day != model["day"]
    model["day"] = day
    model["days"].setdefault(day, {"goal":model["goal"], "logs":[]})
    model["days"][day]["goal"] = model["goal"]
    return changed

def current(model):
    row=model["days"][model["day"]]
    return progress(sum(x["ml"] for x in row["logs"]), row["goal"])

def add_water(model, amount, time, source="Quick log"):
    if isinstance(amount, bool) or not isinstance(amount, (int,float)) or not math.isfinite(amount):
        raise ValueError("Enter a valid amount.")
    if amount <= 0 or amount > 2000 or amount != int(amount):
        raise ValueError("Enter a whole amount from 1 to 2000 ml.")
    model["days"][model["day"]]["logs"].append({"ml":int(amount), "time":time, "source":source})

def undo(model):
    logs=model["days"][model["day"]]["logs"]
    if logs: logs.pop()

def reset_today(model):
    model["days"][model["day"]]["logs"].clear()

def container_amount(size, fraction):
    if size <= 0 or fraction not in (0.25,0.5,0.75,1.0):
        raise ValueError("Choose a valid container and fraction.")
    return int(math.floor(size*fraction+0.5))

def day_total(row): return sum(x["ml"] for x in row["logs"])

def day_points(row):
    pct=day_total(row)/row["goal"]
    return min(100, int(pct*100)) + (25 if pct >= 1 else 0)

def statistics(model):
    completed=sorted(date.fromisoformat(k) for k,v in model["days"].items()
                     if day_total(v) >= v["goal"])
    today=date.fromisoformat(model["day"])
    cursor=today if today in completed else today-timedelta(days=1)
    streak=0
    done=set(completed)
    while cursor in done:
        streak+=1; cursor-=timedelta(days=1)
    best=run=0; previous=None
    for d in completed:
        run=run+1 if previous and d-previous==timedelta(days=1) else 1
        best=max(best,run); previous=d
    return {"streak":streak,"best":best,
            "points":sum(day_points(v) for v in model["days"].values())}

def weekly(model):
    today=date.fromisoformat(model["day"])
    result=[]
    for offset in range(6,-1,-1):
        key=(today-timedelta(days=offset)).isoformat()
        row=model["days"].get(key)
        result.append({"Date":key,"Intake ml":day_total(row) if row else 0,
                       "Goal ml":row["goal"] if row else None,
                       "Status":("Complete" if day_total(row)>=row["goal"] else "In progress") if row else "No record"})
    return result
