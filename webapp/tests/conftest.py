# =============================================================================
# conftest.py — Shared Fixtures for ALL test files
# =============================================================================
import pytest
import os
import json
import datetime
from django.contrib.auth.models import User

# Module-level list — each test appends its result here as it finishes
_results = []

# =============================================================================
# FIXTURE — save_response_html
# =============================================================================
# pytest does NOT take screenshots — it has no real browser, nothing to photograph.
#
# BUT we can save the actual HTML that Django returned during a test.
# This is the text equivalent of a screenshot — you can open the saved .html
# file in a browser and see EXACTLY what the page looked like at that moment.
#
# HOW TO USE IN A TEST:
#
#   def test_login_page_loads(self, client, save_response_html):
#       response = client.get(reverse('loginpage'))
#       save_response_html(response, 'login_page_GET')   ← call it with the response
#       assert response.status_code == 200
#
# This saves: test-results/html-snapshots/login_page_GET.html
# Open that file in any browser to see the exact HTML Django rendered.
#
# WHEN IS THIS USEFUL?
#   - When a test FAILS and you want to see what the page actually looked like
#   - When you want to verify the right content appeared on the page visually
#   - As a record of what each page looked like when tests passed
# =============================================================================
@pytest.fixture
def save_response_html():
    """
    Fixture that returns a helper function.
    Call it inside a test to save a response's HTML to test-results/html-snapshots/.
    Open the saved file in any browser to see what the page looked like.
    """
    folder = os.path.join('test-results', 'html-snapshots')
    os.makedirs(folder, exist_ok=True)

    def _save(response, name):
        """
        response = the Django test response object (from client.get or client.post)
        name     = a descriptive filename (no extension needed)

        Example:
            save_response_html(response, 'login_page_empty_form')
            → saves to test-results/html-snapshots/login_page_empty_form.html
        """
        # Get the HTML content from the response
        # response.content is raw bytes — decode to a string
        html_content = response.content.decode('utf-8', errors='replace')

        # Build the full file path
        filename = f"{name}.html"
        filepath = os.path.join(folder, filename)

        # Write the HTML file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Also print the path so it shows in the terminal
        print(f"\n  [HTML SNAPSHOT] saved → {filepath}")

    return _save


# =============================================================================
# HOOK 1 — pytest_runtest_makereport
# =============================================================================
# Called automatically by pytest after every single test phase.
# Phases: setup → call (the actual test body) → teardown
# We only care about 'call' — that is when the real test ran.
# We store the result in _results so the report can use it later.
# =============================================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call':
        parts  = item.nodeid.replace('\\', '/').split('::')
        module = parts[0].replace('webapp/tests/', '')
        cls    = parts[1] if len(parts) > 2 else '-'
        fn     = parts[-1]
        _results.append({
            'module':   module,
            'cls':      cls,
            'fn':       fn,
            'status':   'passed' if rep.passed else ('failed' if rep.failed else 'skipped'),
            'duration': round(rep.duration, 3),
            'longrepr': str(rep.longrepr) if rep.failed else '',
        })


# =============================================================================
# HOOK 2 — pytest_sessionfinish
# =============================================================================
# Called once after ALL tests have finished.
# We read _results here and build the full HTML report.
# =============================================================================
def pytest_sessionfinish(session, exitstatus):
    """Generate a modern dark-theme HTML report with Chart.js charts."""
    os.makedirs('test-results', exist_ok=True)

    n_passed = sum(1 for r in _results if r['status'] == 'passed')
    n_failed = sum(1 for r in _results if r['status'] == 'failed')
    n_skip   = sum(1 for r in _results if r['status'] == 'skipped')
    total    = len(_results)
    pass_pct = round((n_passed / total * 100) if total > 0 else 0, 1)

    # ── Table rows ──────────────────────────────────────────────────────
    rows_html = ''
    for r in _results:
        st = r['status']
        if st == 'passed':
            badge = '<span class="badge badge-pass">PASSED</span>'
        elif st == 'failed':
            badge = '<span class="badge badge-fail">FAILED</span>'
        else:
            badge = '<span class="badge badge-skip">SKIPPED</span>'

        detail = ''
        if r['longrepr']:
            esc = (r['longrepr']
                   .replace('&', '&amp;').replace('<', '&lt;')
                   .replace('>', '&gt;').replace('"', '&quot;'))
            detail = f'<tr class="detail-row"><td colspan="5"><pre class="traceback">{esc}</pre></td></tr>'

        rows_html += f'''
        <tr class="row-{st}" onclick="toggleDetail(this)">
          <td>{r["module"]}</td>
          <td><span class="cls-tag">{r["cls"]}</span></td>
          <td class="fn-name">{r["fn"]}</td>
          <td>{badge}</td>
          <td>{r["duration"]}s</td>
        </tr>{detail}'''

    # ── Bar chart grouped by class ───────────────────────────────────────
    groups = {}
    for r in _results:
        g = r['cls']
        if g not in groups:
            groups[g] = {'passed': 0, 'failed': 0}
        groups[g][r['status']] = groups[g].get(r['status'], 0) + 1

    bar_labels = json.dumps(list(groups.keys()))
    bar_pass   = json.dumps([groups[g].get('passed', 0) for g in groups])
    bar_fail   = json.dumps([groups[g].get('failed', 0) for g in groups])
    now        = datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')

    # ── HTML ─────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Test Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{{--pass:#22c55e;--fail:#ef4444;--skip:#f59e0b;--bg:#0f172a;--card:#1e293b;--border:#334155;--text:#e2e8f0;--muted:#94a3b8;--accent:#6366f1;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);padding:2rem;}}
.header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid var(--border);}}
.header h1{{font-size:1.8rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.meta{{color:var(--muted);font-size:.85rem;text-align:right;line-height:1.7;}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:1rem;margin-bottom:2rem;}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.25rem 1.5rem;position:relative;overflow:hidden;}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;}}
.card-total::before{{background:var(--accent);}}
.card-pass::before{{background:var(--pass);}}
.card-fail::before{{background:var(--fail);}}
.card-skip::before{{background:var(--skip);}}
.card-pct::before{{background:linear-gradient(90deg,var(--pass),var(--accent));}}
.card-label{{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.5rem;}}
.card-value{{font-size:2rem;font-weight:700;}}
.card-total .card-value{{color:#e2e8f0;}}
.card-pass  .card-value{{color:var(--pass);}}
.card-fail  .card-value{{color:var(--fail);}}
.card-skip  .card-value{{color:var(--skip);}}
.card-pct   .card-value{{font-size:1.6rem;background:linear-gradient(90deg,var(--pass),var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.prog-bar{{height:8px;background:var(--border);border-radius:99px;overflow:hidden;margin:.5rem 0;}}
.prog-fill{{height:100%;background:linear-gradient(90deg,var(--pass),var(--accent));border-radius:99px;}}
.prog-label{{display:flex;justify-content:space-between;font-size:.78rem;color:var(--muted);}}
.charts{{display:grid;grid-template-columns:260px 1fr;gap:1.5rem;margin:2rem 0;}}
.chart-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.5rem;}}
.chart-card h2{{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:1rem;}}
.table-wrap{{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;}}
.tbl-hdr{{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.5rem;border-bottom:1px solid var(--border);}}
.tbl-hdr h2{{font-size:1rem;font-weight:600;}}
input.search{{background:var(--bg);border:1px solid var(--border);border-radius:8px;color:var(--text);padding:.4rem .75rem;font-size:.85rem;width:220px;outline:none;}}
input.search:focus{{border-color:var(--accent);}}
table{{width:100%;border-collapse:collapse;}}
thead tr{{background:#0f172a;}}
th{{padding:.75rem 1rem;text-align:left;font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);border-bottom:1px solid var(--border);}}
td{{padding:.75rem 1rem;font-size:.85rem;border-bottom:1px solid var(--border);vertical-align:middle;}}
.row-passed:hover{{background:rgba(34,197,94,.06);cursor:pointer;}}
.row-failed:hover{{background:rgba(239,68,68,.08);cursor:pointer;}}
.row-skipped:hover{{background:rgba(245,158,11,.06);cursor:pointer;}}
.detail-row td{{background:#0f172a;padding:0;}}
pre.traceback{{background:#1e293b;border-left:3px solid var(--fail);color:#fca5a5;font-size:.78rem;padding:1rem;white-space:pre-wrap;word-break:break-word;max-height:300px;overflow-y:auto;}}
.fn-name{{font-family:'Cascadia Code','Fira Code',monospace;color:#c4b5fd;}}
.cls-tag{{background:rgba(99,102,241,.15);color:#818cf8;border-radius:6px;padding:2px 8px;font-size:.75rem;font-family:monospace;white-space:nowrap;}}
.badge{{display:inline-block;padding:3px 10px;border-radius:99px;font-size:.72rem;font-weight:700;letter-spacing:.04em;}}
.badge-pass{{background:rgba(34,197,94,.15);color:#4ade80;}}
.badge-fail{{background:rgba(239,68,68,.15);color:#f87171;}}
.badge-skip{{background:rgba(245,158,11,.15);color:#fbbf24;}}
.footer{{margin-top:2rem;text-align:center;font-size:.75rem;color:var(--muted);}}
@media(max-width:768px){{.charts{{grid-template-columns:1fr;}}body{{padding:1rem;}}}}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div>
    <h1>&#129514; Test Report</h1>
    <div style="color:var(--muted);font-size:.85rem;margin-top:4px;">webProject &mdash; Django Test Suite</div>
  </div>
  <div class="meta">
    <div>&#128197; {now}</div>
    <div>Python 3.12 &middot; Django 5.2.8 &middot; pytest 9.0.2</div>
  </div>
</div>

<!-- SUMMARY CARDS -->
<div class="cards">
  <div class="card card-total"><div class="card-label">Total Tests</div><div class="card-value">{total}</div></div>
  <div class="card card-pass"> <div class="card-label">Passed</div>     <div class="card-value">{n_passed}</div></div>
  <div class="card card-fail"> <div class="card-label">Failed</div>     <div class="card-value">{n_failed}</div></div>
  <div class="card card-skip"> <div class="card-label">Skipped</div>    <div class="card-value">{n_skip}</div></div>
  <div class="card card-pct">  <div class="card-label">Pass Rate</div>  <div class="card-value">{pass_pct}%</div></div>
</div>

<!-- PROGRESS BAR -->
<div class="prog-bar"><div class="prog-fill" style="width:{pass_pct}%"></div></div>
<div class="prog-label"><span>0%</span><span style="color:var(--pass);font-weight:600;">{pass_pct}% passing</span><span>100%</span></div>

<!-- CHARTS -->
<div class="charts">
  <div class="chart-card">
    <h2>&#127849; Pass / Fail Breakdown</h2>
    <div style="position:relative;height:220px;"><canvas id="donut"></canvas></div>
  </div>
  <div class="chart-card">
    <h2>&#128202; Tests per Class</h2>
    <div style="position:relative;height:220px;"><canvas id="bar"></canvas></div>
  </div>
</div>

<!-- RESULTS TABLE -->
<div class="table-wrap">
  <div class="tbl-hdr">
    <h2>&#128203; All Test Results</h2>
    <input class="search" id="q" type="text" placeholder="&#128269; Search tests..." oninput="filter()"/>
  </div>
  <table id="tbl">
    <thead><tr><th>File</th><th>Class</th><th>Test Name</th><th>Status</th><th>Duration</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>

<div class="footer">Auto-generated by pytest &middot; {now} &middot; webProject</div>

<script>
new Chart(document.getElementById('donut'),{{
  type:'doughnut',
  data:{{labels:['Passed','Failed','Skipped'],datasets:[{{data:[{n_passed},{n_failed},{n_skip}],backgroundColor:['#22c55e','#ef4444','#f59e0b'],borderColor:'#1e293b',borderWidth:3,hoverOffset:8}}]}},
  options:{{responsive:true,maintainAspectRatio:false,cutout:'65%',plugins:{{legend:{{position:'bottom',labels:{{color:'#94a3b8',padding:16,font:{{size:12}}}}}},tooltip:{{callbacks:{{label:c=>` ${{c.label}}: ${{c.raw}} test${{c.raw!==1?'s':''}}`}}}}}}}}
}});
new Chart(document.getElementById('bar'),{{
  type:'bar',
  data:{{
    labels:{bar_labels},
    datasets:[
      {{label:'Passed',data:{bar_pass},backgroundColor:'rgba(34,197,94,.75)',borderColor:'#22c55e',borderWidth:1,borderRadius:6}},
      {{label:'Failed', data:{bar_fail},backgroundColor:'rgba(239,68,68,.75)',borderColor:'#ef4444',borderWidth:1,borderRadius:6}}
    ]
  }},
  options:{{
    responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{labels:{{color:'#94a3b8',font:{{size:12}}}}}}}},
    scales:{{
      x:{{ticks:{{color:'#94a3b8',font:{{size:11}}}},grid:{{color:'rgba(51,65,85,.4)'}}}},
      y:{{ticks:{{color:'#94a3b8',stepSize:1}},grid:{{color:'rgba(51,65,85,.4)'}},beginAtZero:true}}
    }}
  }}
}});
function filter(){{
  const q=document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('#tbl tbody tr:not(.detail-row)').forEach(r=>{{
    r.style.display=r.textContent.toLowerCase().includes(q)?'':'none';
  }});
}}
function toggleDetail(row){{
  const n=row.nextElementSibling;
  if(n&&n.classList.contains('detail-row'))
    n.style.display=n.style.display==='none'?'':'none';
}}
document.querySelectorAll('.detail-row').forEach(r=>r.style.display='none');
</script>
</body>
</html>"""

    out = os.path.join('test-results', 'custom_report.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)


# =============================================================================
# FIXTURES
# =============================================================================
@pytest.fixture(scope='function')
def test_user(db):
    """
    Creates a basic test user.
    Available to ALL test files automatically.
    """
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='StrongPass123!'
    )


@pytest.fixture
def admin_user(db):
    """
    Creates a superuser (admin).
    Useful for testing admin-only views.
    """
    return User.objects.create_superuser(
        username='adminuser',
        email='admin@example.com',
        password='AdminPass123!'
    )


@pytest.fixture
def logged_in_client(client, test_user):
    """
    A client that is ALREADY logged in as test_user.
    Use this for any view protected by @login_required.
    """
    client.force_login(test_user)
    return client
