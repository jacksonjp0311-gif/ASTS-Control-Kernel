import json
import os
from datetime import datetime
from typing import Dict, Any

from metrics.drift.drift import reset_baseline
from engine.recovery.plateau import push_and_check

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "state")
RECOVERY_STATE_FILE = os.path.join(STATE_DIR, "recovery_state.json")

DEFAULTS = {
    "warn": 0.006,
    "crit": 0.010,
    "recover": 0.0115,
    "reset": 0.0125,
    "cooldown_steps": 5,
    "max_backoff_steps": 3,
    "plateau_window": 6,
    "plateau_eps": 0.00015,
    "warn_streak_to_recover": 6,
    "crit_streak_to_reset": 3,
    "max_resets_per_100": 3,
    "enable_autonomous_reset": True,
    "verbose_recovery": True
}

def _clamp01(x):
    try: x=float(x)
    except: return 0.0
    return max(0,min(1,x))

def _load_json(p):
    if not os.path.exists(p): return None
    with open(p,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def _save_json(p,obj):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,"w",encoding="utf-8") as f:
        json.dump(obj,f,indent=2,sort_keys=True)

def load_thresholds(root_dir):
    tpath=os.path.join(root_dir,"state","thresholds.json")
    merged=dict(DEFAULTS)
    try:
        d=_load_json(tpath)
        if isinstance(d,dict):
            for k in merged:
                if k in d: merged[k]=d[k]
    except: pass
    for k in ["warn","crit","recover","reset"]:
        merged[k]=_clamp01(merged.get(k,DEFAULTS[k]))
    return merged

def _load_state():
    s=_load_json(RECOVERY_STATE_FILE)
    if not isinstance(s,dict):
        return {"k":0,"last_reset_k":-10**9,"backoff":0,"warn_streak":0,"crit_streak":0,"reset_events":[]}
    return s

def _save_state(s):
    _save_json(RECOVERY_STATE_FILE,s)

def decide(theta:Dict[str,Any],root_dir:str)->Dict[str,Any]:
    th=load_thresholds(root_dir)
    s=_load_state()
    s["k"]=int(s.get("k",0))+1

    drift_slow=0.0
    d=theta.get("drift",{})
    if isinstance(d,dict):
        drift_slow=float(d.get("slow",0.0))

    mode="ok"
    if drift_slow>=th["reset"]: mode="reset"
    elif drift_slow>=th["recover"]: mode="recover"
    elif drift_slow>=th["crit"]: mode="crit"
    elif drift_slow>=th["warn"]: mode="warn"

    if mode=="warn":
        s["warn_streak"]=s.get("warn_streak",0)+1
        s["crit_streak"]=0
    elif mode in ("crit","recover","reset"):
        s["crit_streak"]=s.get("crit_streak",0)+1
        s["warn_streak"]=0
    else:
        s["warn_streak"]=0
        s["crit_streak"]=0

    plateau=push_and_check(drift_slow,window=th["plateau_window"],eps=th["plateau_eps"])

    actions=[]
    backoff=0

    can_reset=(s["k"]-s.get("last_reset_k",-10**9))>=th["cooldown_steps"]

    # ---- PLATEAU OVERRIDE (SAFE) ----
    if plateau.get("plateau") and s.get("crit_streak",0)>=3:
        can_reset=True

    if mode=="reset" and can_reset:
        actions.append("reset_baseline")
        s["last_reset_k"]=s["k"]
        s["backoff"]=0
    elif mode in ("recover","crit","warn"):
        if mode in ("recover","crit"):
            s["backoff"]=min(s.get("backoff",0)+1,th["max_backoff_steps"])
        backoff=s.get("backoff",0)

        if mode=="recover":
            actions+=["tighten_constraints","request_validation"]
        elif mode=="crit":
            actions+=["tighten_constraints","request_validation"]
        elif mode=="warn":
            actions+=["mark_uncertainty_high"]

    _save_state(s)

    return {
        "mode":mode,
        "actions":actions,
        "backoff_steps":backoff,
        "plateau":plateau,
        "timestamp":datetime.utcnow().isoformat()+"Z"
    }

def apply(decision,theta,root_dir):
    if "reset_baseline" in decision.get("actions",[]):
        try: reset_baseline(theta.get("metrics",{}))
        except: pass
    return decision

