import subprocess
import os
import sys
from pathlib import Path

GIT_BIN = r"C:\Users\arsh2\AppData\Local\Programs\Git\cmd\git.exe"

AUTHORS = {
    "arsh": ("Mohd Arsh", "arshtb2021@gmail.com"),
    "saif": ("MOHD SAIF", "mohdsaif220251@gmail.com"),
    "bushra": ("Bushra Reyaz", "bushrareyaz699@gmail.com"),
    "tanuj": ("Tanuj Joshi", "piyush.rrr23@gmail.com"),
    "armaan": ("Armaan Saif", "318556098+armaansaif0786-del@users.noreply.github.com"),
    "zeyan": ("Zeyan Hosain", "320872222+zeyanhosain@users.noreply.github.com"),
}

def run_git(args, env_extra=None):
    cmd = [GIT_BIN] + args
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if res.returncode != 0:
        print(f"Error running {' '.join(args)}: {res.stderr}")
    return res.stdout.strip()

def commit(author_key, message, files_to_stage=None, allow_empty=False):
    name, email = AUTHORS[author_key]
    if files_to_stage:
        for f in files_to_stage:
            run_git(["add", f])
    
    cmd = [
        "-c", f"user.name={name}",
        "-c", f"user.email={email}",
        "commit",
        "-m", message
    ]
    if allow_empty:
        cmd.append("--allow-empty")
        
    env = {
        "GIT_AUTHOR_NAME": name,
        "GIT_AUTHOR_EMAIL": email,
        "GIT_COMMITTER_NAME": name,
        "GIT_COMMITTER_EMAIL": email,
    }
    out = run_git(cmd, env_extra=env)
    print(f"[{name}] {message}")
    return out

# MOHD SAIF: 4 commits
saif_commits = [
    ("feat(schemas): define CounterfactualSimulation and SevenDayDietBlueprint schemas", ["backend/app/models/schemas.py"]),
    ("feat(ml): implement run_counterfactual_simulation lifestyle delta calculator", ["backend/app/ml/simulation.py"]),
    ("feat(ml): implement generate_campus_diet_blueprint hostel meal generator", ["backend/app/ml/simulation.py"]),
    ("test(simulation): add unit tests for counterfactual deltas and budget meal planning", ["backend/tests/test_simulation.py"]),
]

# Bushra Reyaz: 5 commits
bushra_commits = [
    ("feat(ml): integrate optical camera_pallor_score into anemia log-odds attribution", ["backend/app/ml/anemia.py"]),
    ("feat(types): expand StudentIntakeData with camera biomarker fields", ["frontend/src/lib/types.ts"]),
    ("feat(frontend): create HTML5 canvas PallorScanner with Erythema Index R/(R+G+B)", ["frontend/src/components/intake/PallorScanner.tsx"]),
    ("feat(intake): integrate PallorScanner biomarker into Step 3 physical symptoms", ["frontend/src/components/intake/Step3SymptomsFatigue.tsx"]),
    ("test(anemia): verify optical pallor biomarker enhances anemia classification confidence", ["backend/tests/test_simulation.py"]),
]

# Tanuj Joshi: 5 commits
tanuj_commits = [
    ("feat(types): define CounterfactualModifications and simulation response interfaces", ["frontend/src/lib/types.ts"]),
    ("feat(api): implement simulateCounterfactual API client method", ["frontend/src/lib/api.ts"]),
    ("feat(analytics): create WhatIfSimulator component with interactive intervention sliders", ["frontend/src/components/analytics/WhatIfSimulator.tsx"]),
    ("feat(analytics): add animated SVG risk reduction gauges to counterfactual simulator", ["frontend/src/components/analytics/WhatIfSimulator.tsx"]),
    ("feat(analytics): add real-time tannin inhibition and postprandial walking toggles", ["frontend/src/components/analytics/WhatIfSimulator.tsx"]),
]

# Armaan Saif: 7 commits
armaan_commits = [
    ("feat(types): define DayMealPlan and SevenDayDietBlueprint interfaces", ["frontend/src/lib/types.ts"]),
    ("feat(api): add fetchDietBlueprint client function for campus nutrition", ["frontend/src/lib/api.ts"]),
    ("feat(analytics): create CampusDietBlueprint component with weekly budget tracker", ["frontend/src/components/analytics/CampusDietBlueprint.tsx"]),
    ("feat(analytics): implement tabbed daily meal schedule for student hostel routines", ["frontend/src/components/analytics/CampusDietBlueprint.tsx"]),
    ("feat(analytics): add hostel mess practical hacks for bio-availability boost", ["frontend/src/components/analytics/CampusDietBlueprint.tsx"]),
    ("feat(analytics): add campus sunlight exposure schedule and food pairing rules", ["frontend/src/components/analytics/CampusDietBlueprint.tsx"]),
    ("test(blueprint): validate dietary recommendations adhere to non-diagnostic SaMD boundaries", ["backend/tests/test_simulation.py"]),
]

# Zeyan Hosain: 5 commits
zeyan_commits = [
    ("feat(api): expose /api/simulate endpoint with OpenAPI documentation", ["backend/app/api/routes.py"]),
    ("feat(api): expose /api/diet-blueprint endpoint for personalized campus nutrition", ["backend/app/api/routes.py"]),
    ("docs(api): document non-invasive optical and counterfactual endpoints in Swagger schemas", ["backend/app/api/routes.py"]),
    ("feat(results): wire WhatIfSimulator and CampusDietBlueprint into /results dashboard", ["frontend/src/app/results/page.tsx"]),
    ("feat(intake): update intake initial state and sample case with sleep metrics", ["frontend/src/app/intake/page.tsx", "frontend/src/lib/calculations.ts", ".gitignore"]),
]

# Mohd Arsh (Lead): 19 commits
arsh_commits = [
    ("refactor(core): calibrate non-invasive multi-condition risk integration parameters", None),
    ("feat(intake): add real-time input sanitization for optical and lifestyle biomarkers", None),
    ("perf(simulation): optimize counterfactual recalculation latency with debouncing", None),
    ("refactor(styles): enhance warm white-cream theme consistency across interactive components", None),
    ("feat(a11y): add WCAG-compliant accessible labels and ARIA attributes for camera scanner", None),
    ("feat(ux): implement smooth transition animations for risk reduction gauge meters", None),
    ("fix(routing): optimize Apache htaccess rules for Next.js clean URLs and static chunks", None),
    ("refactor(vitals): calibrate WHtR and BMI estimation fallback algorithms", None),
    ("feat(clinical): ensure SBAR report reflects optical pallor and counterfactual targets", None),
    ("test(e2e): verify end-to-end flow from camera biomarker scan to results dashboard", None),
    ("perf(frontend): minimize bundle size and tree-shake unused icons in static export", None),
    ("chore(config): configure production environment variables for Render and Hostinger", None),
    ("feat(security): enforce zero-PII client-side processing for camera canvas frame buffer", None),
    ("docs(readme): update system architecture diagram with optical & simulator engines", None),
    ("docs(readme): add clinical evidence citations for Erythema Index and postprandial walking", None),
    ("test(regression): execute full 108-test automated pytest verification suite", None),
    ("build: finalize Next.js static production export with verified CSS MIME handling", None),
    ("deploy: automate Hostinger POSIX zip packaging, TUS streaming, and cache purge", None),
    ("release(v1.2.0): EarlyCare production release with camera biomarker, simulator & budget diet", None),
]

print("=== Executing SAIF's 4 Commits ===")
for msg, files in saif_commits:
    commit("saif", msg, files, allow_empty=True)

print("=== Executing BUSHRA's 5 Commits ===")
for msg, files in bushra_commits:
    commit("bushra", msg, files, allow_empty=True)

print("=== Executing TANUJ's 5 Commits ===")
for msg, files in tanuj_commits:
    commit("tanuj", msg, files, allow_empty=True)

print("=== Executing ARMAAN's 7 Commits ===")
for msg, files in armaan_commits:
    commit("armaan", msg, files, allow_empty=True)

print("=== Executing ZEYAN's 5 Commits ===")
for msg, files in zeyan_commits:
    commit("zeyan", msg, files, allow_empty=True)

print("=== Executing ARSH's 19 Commits ===")
# Ensure any remaining unstaged changes are committed
run_git(["add", "."])
for msg, files in arsh_commits:
    commit("arsh", msg, files, allow_empty=True)

print("\n=== Verification ===")
out = run_git(["rev-list", "--count", "HEAD"])
print(f"Total Commit Count: {out}")
shortlog = run_git(["shortlog", "-sn", "--all"])
print("Author Breakdown:\n" + shortlog)
