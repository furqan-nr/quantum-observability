#!/usr/bin/env python3
"""Definitively classify PR #14998 (VF2PostLayout, uncoupled qubit, strict_direction=True).

Builds (or reuses) the fix and parent, runs the fix's exact regression PassManager on each (both
seeds), and decides the channel:
  parent RAISES                                    -> compilation_failure (VISIBLE)  -> 19/68 (28%)
  parent OK, wrong final_index_layout, output
    equivalent modulo global phase + permutation   -> contract_metadata  (INVISIBLE) -> 20/68 (29%)
  parent OK, output NOT equivalent                  -> output_semantic    (VISIBLE)  -> stays visible
Run from repo root:  python scripts/verify_14998.py
"""
import json, os, subprocess, sys
from pathlib import Path
from itertools import permutations
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "src"))
from source_validate_mining import build_event

FIX    = "2d73e5d93c842d0c8fc253e6f97ca0c927474141"
PARENT = "3226fde99f65d6c3c2c6b66f86217f58bab7a8cb"

SNIPPET = r'''
import json, numpy as np
res = {"seeds": {}}
for seed in (-1, 12):
    r = {}
    try:
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import CXGate, XGate
        from qiskit.transpiler import PassManager, Target, InstructionProperties, passes
        from qiskit.quantum_info import Operator
        qc = QuantumCircuit(3); qc.x(0); qc.cx(1, 2)
        bad = InstructionProperties(error=1e-1); good = InstructionProperties(error=1e-5)
        target = Target()
        target.add_instruction(XGate(),  {(0,): bad, (1,): good, (2,): good})
        target.add_instruction(CXGate(), {(0, 1): good, (1, 2): bad})
        pm = PassManager([passes.TrivialLayout(target), passes.ApplyLayout(),
                          passes.VF2PostLayout(target, seed=seed, strict_direction=True),
                          passes.ApplyLayout()])
        out = pm.run(qc)
        r["crashed"] = False
        try: r["final_index_layout"] = list(out.layout.final_index_layout())
        except Exception as e: r["final_index_layout"] = "err:" + repr(e)
        uq = Operator(qc).data; uo = Operator(out).data
        r["u_qc_re"] = uq.real.round(6).tolist(); r["u_qc_im"] = uq.imag.round(6).tolist()
        r["u_out_re"] = uo.real.round(6).tolist(); r["u_out_im"] = uo.imag.round(6).tolist()
    except Exception as e:
        r = {"crashed": True, "error_type": type(e).__name__, "error": str(e)[:400]}
    res["seeds"][str(seed)] = r
print("RESULT_JSON:" + json.dumps(res))
'''

def ensure_build(sha, eid):
    venv = ROOT / "environment" / "_builds" / eid / "venv"
    py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if py.exists():
        print(f"reusing existing build {eid}"); return py
    return build_event(sha, eid)

def run(py):
    p = subprocess.run([str(py), "-c", SNIPPET], capture_output=True, text=True)
    for line in (p.stdout or "").splitlines():
        if line.startswith("RESULT_JSON:"):
            return json.loads(line[len("RESULT_JSON:"):])
    return {"error": "no result; stderr=" + (p.stderr or "")[-400:]}

def perm_matrix(perm, nq=3):
    dim = 2 ** nq; M = np.zeros((dim, dim))
    for i in range(dim):
        bits = [(i >> b) & 1 for b in range(nq)]
        j = sum(bits[perm[b]] << b for b in range(nq)); M[j, i] = 1
    return M

def equiv_mod_phase_perm(d, nq=3):
    U = np.array(d["u_out_re"]) + 1j * np.array(d["u_out_im"])
    V = np.array(d["u_qc_re"])  + 1j * np.array(d["u_qc_im"])
    for perm in permutations(range(nq)):
        P = perm_matrix(perm, nq); W = P @ V @ P.conj().T
        M = U.conj().T @ W; ph = M[0, 0]
        if abs(abs(ph) - 1) < 1e-6 and np.allclose(M, ph * np.eye(M.shape[0]), atol=1e-5):
            return True
    return False

def classify(fix, bug):
    out = []
    for seed in ("-1", "12"):
        f = fix["seeds"][seed]; b = bug["seeds"][seed]
        if b.get("crashed"):
            out.append(f"seed {seed}: parent RAISES ({b.get('error_type')}: {b.get('error','')[:120]}) "
                       f"-> compilation_failure (VISIBLE)")
        elif f.get("crashed"):
            out.append(f"seed {seed}: FIX crashed ({f.get('error_type')}) -> investigate")
        else:
            same = f.get("final_index_layout") == b.get("final_index_layout")
            blind = equiv_mod_phase_perm(b)
            if not same and blind:
                out.append(f"seed {seed}: parent layout {b.get('final_index_layout')} vs fix "
                           f"{f.get('final_index_layout')}; output EQUIVALENT mod phase+perm "
                           f"-> contract_metadata (INVISIBLE)")
            elif not blind:
                out.append(f"seed {seed}: parent output NOT equivalent -> output_semantic (VISIBLE)")
            else:
                out.append(f"seed {seed}: same layout {b.get('final_index_layout')} + output across "
                           f"builds -> fault not reproduced at this seed")
    return out

def main():
    fpy = ensure_build(FIX, "sv-14998-fix"); ppy = ensure_build(PARENT, "sv-14998-bug")
    if not fpy or not ppy:
        print("build failed (need Rust toolchain)"); return 1
    fix = run(fpy); bug = run(ppy)
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "verify_14998.json").write_text(json.dumps({"fix": fix, "parent": bug}, indent=2, default=str))
    print("=" * 66)
    if "error" in fix or "error" in bug:
        print("worker error:\n  fix:", fix.get("error"), "\n  parent:", bug.get("error")); return 1
    print(f"fix    final_index_layout: seed-1={fix['seeds']['-1'].get('final_index_layout')}  "
          f"seed12={fix['seeds']['12'].get('final_index_layout')}")
    print(f"parent final_index_layout: seed-1={bug['seeds']['-1'].get('final_index_layout')}  "
          f"seed12={bug['seeds']['12'].get('final_index_layout')}")
    for v in classify(fix, bug): print(v)
    print("wrote results/verify_14998.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
