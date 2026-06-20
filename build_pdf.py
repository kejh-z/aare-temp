# -*- coding: utf-8 -*-
"""Builds a nicely formatted PDF of the Aare Temperature project description."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, ListFlowable, ListItem, KeepTogether,
)

# ---- Palette (Aare blues) ----
DARK = colors.HexColor("#1a5276")
MID = colors.HexColor("#2e86c1")
LIGHT = colors.HexColor("#eaf2f8")
GREY = colors.HexColor("#666666")
LIGHTGREY = colors.HexColor("#999999")
RULE = colors.HexColor("#d5dbdb")

OUTPUT = "Aare-Temperature-Project.pdf"
TITLE = "Aare Temperature Daily Email"
SUBTITLE = "Project Description & Technical Documentation"

styles = getSampleStyleSheet()

body = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="Helvetica",
    fontSize=10, leading=15, textColor=colors.HexColor("#222222"),
    spaceAfter=6, alignment=TA_LEFT,
)
h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=16, leading=20, textColor=DARK, spaceBefore=18, spaceAfter=8,
)
h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=12.5, leading=16, textColor=MID, spaceBefore=12, spaceAfter=5,
)
bullet = ParagraphStyle(
    "Bullet", parent=body, leftIndent=4, spaceAfter=3,
)
code = ParagraphStyle(
    "Code", parent=body, fontName="Courier", fontSize=8.5, leading=12,
    textColor=colors.HexColor("#1b2631"), backColor=colors.HexColor("#f4f6f7"),
    borderPadding=8, spaceBefore=4, spaceAfter=8, leftIndent=2, rightIndent=2,
)
cell = ParagraphStyle("Cell", parent=body, fontSize=9, leading=12, spaceAfter=0)
cellb = ParagraphStyle("CellB", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)


def hr():
    return HRFlowable(width="100%", thickness=0.75, color=RULE,
                      spaceBefore=4, spaceAfter=10)


def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(t, bullet), value="•", leftIndent=14) for t in items],
        bulletType="bullet", start="•", leftIndent=12,
    )


def make_table(rows, col_widths, header=True):
    data = []
    for i, row in enumerate(rows):
        style = cellb if (header and i == 0) else cell
        data.append([Paragraph(str(c), style) for c in row])
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    ts = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]
    if header:
        ts += [
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, DARK),
        ]
    t.setStyle(TableStyle(ts))
    return t


# ---- Header / footer ----
def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Footer rule + text
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 15 * mm, w - 20 * mm, 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(LIGHTGREY)
    canvas.drawString(20 * mm, 10 * mm, "Aare Temperature Daily Email")
    canvas.drawRightString(w - 20 * mm, 10 * mm, "Page %d" % doc.page)
    canvas.restoreState()


def cover(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Top blue band
    canvas.setFillColor(DARK)
    canvas.rect(0, h - 95 * mm, w, 95 * mm, fill=1, stroke=0)
    canvas.setFillColor(MID)
    canvas.rect(0, h - 97 * mm, w, 2 * mm, fill=1, stroke=0)
    # Big temperature motif
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 64)
    canvas.drawCentredString(w / 2, h - 62 * mm, u"°C")
    canvas.setFont("Helvetica-Bold", 26)
    canvas.drawCentredString(w / 2, h - 78 * mm, TITLE)
    canvas.setFont("Helvetica", 13)
    canvas.drawCentredString(w / 2, h - 88 * mm, SUBTITLE)
    # Footer text
    canvas.setFillColor(LIGHTGREY)
    canvas.setFont("Helvetica", 9)
    canvas.drawCentredString(w / 2, 18 * mm,
                             "github.com/kejh-z/aare-temp  -  Data: aaremarzili.ch via aare.guru")
    canvas.restoreState()


def build():
    doc = BaseDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=22 * mm, bottomMargin=22 * mm,
        title=TITLE, author="kejh-z",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="main")
    cover_frame = Frame(doc.leftMargin, doc.bottomMargin,
                        doc.width, doc.height - 80 * mm, id="cover")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=cover),
        PageTemplate(id="main", frames=[frame], onPage=header_footer),
    ])

    S = []  # story
    from reportlab.platypus import NextPageTemplate, PageBreak

    # Cover summary box (sits below the blue band)
    S.append(Spacer(1, 6 * mm))
    intro = ("An automation that checks the daily peak water temperature of the "
             "river Aare in Bern (the Marzili swimming spot) and emails a "
             "formatted daily report to a list of recipients every day at "
             "<b>18:00 Zurich time</b> &mdash; chosen because it falls after the "
             "warmest part of the day, so the reported peak reflects the true "
             "daily maximum. The whole system runs in the cloud; no personal "
             "computer needs to be switched on.")
    S.append(Paragraph(intro, ParagraphStyle(
        "Intro", parent=body, fontSize=11, leading=17)))
    S.append(Spacer(1, 4 * mm))
    S.append(make_table([
        ["Property", "Value"],
        ["Recipients", "kevin@holden.ch, jessica@holden.ch, brigitte.lendl@bluewin.ch"],
        ["From address", "aare@holden.ch (verified holden.ch domain)"],
        ["Schedule", "Daily at 18:00 Europe/Zurich"],
        ["Repository", "github.com/kejh-z/aare-temp (branch: main)"],
    ], [38 * mm, doc.width - 38 * mm]))

    S.append(NextPageTemplate("main"))
    S.append(PageBreak())

    # 1. What the email contains
    S.append(Paragraph("1. What the Email Contains", h1)); S.append(hr())
    S.append(bullets([
        "<b>Peak water temperature</b> reached that day, and the time it occurred",
        "<b>Current water temperature</b> at the moment the report is generated",
        "<b>Flow rate</b> of the river (m&sup3;/s)",
        "<b>Number of measurements</b> taken that day",
        "A friendly <b>swim verdict</b> based on the peak temperature",
    ]))
    S.append(Spacer(1, 3))
    S.append(Paragraph("Swim verdict thresholds:", h2))
    S.append(make_table([
        ["Peak temperature", "Verdict"],
        ["&ge; 20 &deg;C", "Perfect for swimming!"],
        ["&ge; 18 &deg;C", "Warm enough for a swim."],
        ["&ge; 16 &deg;C", "A bit fresh, but doable."],
        ["&lt; 16 &deg;C", "Too cold for most swimmers."],
    ], [50 * mm, doc.width - 50 * mm]))
    S.append(Spacer(1, 4))
    S.append(Paragraph("The email is delivered as styled HTML: a blue temperature "
                       "card, a stats table, and a data-source footer.", body))

    # 2. Data source
    S.append(Paragraph("2. Data Source", h1)); S.append(hr())
    S.append(Paragraph("Website: <b>aaremarzili.ch</b> (redirects to aaremarzili.info)", body))
    S.append(Paragraph("Data API:", body))
    S.append(Paragraph("https://aareguru.existenz.ch/v2018/current?app=aare-temp&amp;version=1.0.0", code))
    S.append(Paragraph(
        "The aaremarzili site loads its data dynamically, so instead of scraping "
        "the page we use the public <b>aare.guru API</b> &mdash; the same "
        "underlying data source for Aare conditions in Bern. The API returns "
        "JSON containing:", body))
    S.append(bullets([
        "<font face='Courier'>aare.temperature</font> &mdash; current water temperature",
        "<font face='Courier'>aare.flow</font> &mdash; current flow rate",
        "<font face='Courier'>aarepast[]</font> &mdash; ~48 hours of historical readings "
        "(Unix timestamp + temperature, 10-minute intervals)",
    ]))
    S.append(Paragraph(
        "The app filters <font face='Courier'>aarepast[]</font> to readings from "
        "the current day (Zurich time), then finds the maximum temperature and "
        "the time it occurred.", body))

    # 3. Architecture
    S.append(Paragraph("3. How It Runs (Architecture)", h1)); S.append(hr())
    S.append(Paragraph("Scheduling and execution are split across three services:", body))
    S.append(Spacer(1, 2))
    S.append(make_table([
        ["Stage", "Service", "Role"],
        ["1. Scheduler", "cron-job.org", "Fires daily at 18:00 Zurich; sends an authenticated POST to the GitHub API to trigger the workflow."],
        ["2. Compute", "GitHub Actions", "Runs an inline Node.js script: fetches Aare data, computes the peak, builds the email, calls Resend."],
        ["3. Delivery", "Resend", "Sends the HTML email from aare@holden.ch to the recipients."],
    ], [26 * mm, 32 * mm, doc.width - 58 * mm]))
    S.append(Spacer(1, 5))
    S.append(Paragraph("Trigger request sent by cron-job.org:", h2))
    S.append(Paragraph(
        "POST https://api.github.com/repos/kejh-z/aare-temp/<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;actions/workflows/daily-email.yml/dispatches<br/>"
        "Authorization: Bearer &lt;GitHub personal access token&gt;<br/>"
        "Accept: application/vnd.github+json<br/>"
        "Content-Type: application/json<br/>"
        "Body: {&quot;ref&quot;:&quot;main&quot;}", code))
    S.append(Paragraph("Why this combination?", h2))
    S.append(bullets([
        "<b>GitHub's built-in cron was unreliable</b> &mdash; scheduled runs on "
        "inactive repos were delayed by hours or skipped. The <font face='Courier'>schedule:</font> "
        "trigger was removed and replaced with cron-job.org firing a "
        "<font face='Courier'>workflow_dispatch</font> event on time.",
        "<b>GitHub Actions</b> provides free, always-on compute, so no personal PC is needed.",
        "<b>Resend</b> handles deliverability and lets us send from a custom domain.",
    ]))

    # 4. Reliability
    S.append(Paragraph("4. Reliability: IP Blocking &amp; Self-Healing Retry", h1)); S.append(hr())
    S.append(Paragraph(
        "The aare.guru server (existenz.ch) runs <b>Imunify360 bot-protection</b>, "
        "which blocks a large share of cloud / datacenter IP addresses with the "
        "response <font face='Courier'>{\"message\":\"Access denied by Imunify360 "
        "bot-protection...\"}</font>. GitHub Actions runners use such IPs, and each "
        "run gets <b>one IP for its whole lifetime</b>. In practice roughly 40% of "
        "runs land on a blocked IP &mdash; the cause of the intermittent failures.", body))
    S.append(Paragraph(
        "Because every request inside a run shares that one IP, retrying <i>within</i> "
        "a run (or sleeping and retrying) cannot escape a block. The fix is to retry "
        "as <b>separate runs</b>, each getting a fresh runner and therefore a fresh IP:", body))
    S.append(bullets([
        "A run fetches the data (3 quick attempts, ~10 s, to absorb genuine transient "
        "blips) and sends the email. On success it finishes.",
        "On failure, a second step (<font face='Courier'>if: failure()</font>) waits "
        "90 s and uses the <font face='Courier'>GH_PAT</font> secret to dispatch a "
        "brand-new run with an incremented <font face='Courier'>attempt</font> counter.",
        "This repeats until a run succeeds or the cap of <b>6 attempts</b> is reached. "
        "The chain stops the instant one run succeeds, so recipients never get a duplicate.",
    ]))
    S.append(Paragraph(
        "With ~60% success per IP, six independent attempts give roughly <b>99.6%</b> "
        "reliability, and on a bad-IP day the email still typically arrives within a "
        "few minutes. GitHub's built-in token deliberately cannot trigger a "
        "<font face='Courier'>workflow_dispatch</font> (anti-recursion), which is why a "
        "separate <font face='Courier'>GH_PAT</font> token secret is required. A browser "
        "User-Agent is also sent, though the dominant factor is the IP, not the user-agent. "
        "Local runs via <font face='Courier'>index.js</font> use a residential IP that is "
        "not blocked, so they need no retry logic.", body))

    # 5. Repository contents
    S.append(Paragraph("5. Repository Contents", h1)); S.append(hr())
    S.append(make_table([
        ["File", "Purpose"],
        ["<font face='Courier'>.github/workflows/<br/>daily-email.yml</font>",
         "<b>The live production code.</b> Self-contained GitHub Actions workflow with an inline Node.js script (no dependencies, no checkout). Runs each day."],
        ["<font face='Courier'>index.js</font>",
         "Standalone Node.js version of the same logic for local testing. Uses the resend npm package and a .env file. Supports a --dry-run flag."],
        ["<font face='Courier'>package.json</font>",
         "Declares the resend dependency and npm start / npm test scripts."],
        ["<font face='Courier'>.env.example</font>",
         "Template showing the expected RESEND_API_KEY variable."],
        ["<font face='Courier'>.env</font>",
         "(Not committed) Holds the real Resend API key for local runs."],
        ["<font face='Courier'>.gitignore</font>",
         "Excludes node_modules/ and .env from git."],
        ["<font face='Courier'>setup-task.bat</font>",
         "Legacy Windows Task Scheduler helper (superseded by the cloud setup)."],
        ["<font face='Courier'>PROJECT.md</font>",
         "Markdown source of this documentation."],
    ], [42 * mm, doc.width - 42 * mm]))
    S.append(Spacer(1, 5))
    S.append(Paragraph("Two copies of the logic &mdash; why?", h2))
    S.append(Paragraph(
        "The workflow contains an <b>inline</b> copy made self-contained (Node's "
        "built-in <font face='Courier'>fetch</font> + the Resend REST API directly) "
        "because the GitHub organisation restricts external Actions like "
        "<font face='Courier'>actions/checkout</font>, and a private repo could not "
        "be cloned without auth. <font face='Courier'>index.js</font> is the "
        "cleaner original kept for local testing. The two are functionally "
        "equivalent &mdash; if you change recipients or design, update <b>both</b> "
        "(the workflow is what runs in production).", body))

    # 6. Making changes
    S.append(Paragraph("6. Key Processes &amp; Making Changes", h1)); S.append(hr())
    S.append(Paragraph("Change recipients", h2))
    S.append(Paragraph("Edit the <font face='Courier'>RECIPIENTS</font> array in "
                       "<b>both</b> the workflow and index.js, then commit and push.", body))
    S.append(Paragraph("Change the send time", h2))
    S.append(Paragraph("Adjust the schedule in cron-job.org (not in the repo). "
                       "Keep the timezone set to Europe/Zurich.", body))
    S.append(Paragraph("Test manually", h2))
    S.append(bullets([
        "<b>From GitHub:</b> Actions tab &rarr; \"Daily Aare Temperature Email\" &rarr; \"Run workflow\".",
        "<b>From cron-job.org:</b> use the \"Test run\" button.",
        "<b>Locally:</b> <font face='Courier'>npm test</font> (dry run) or "
        "<font face='Courier'>npm start</font> (sends a real email); requires a valid .env.",
    ]))
    S.append(Paragraph("Rotate the API key", h2))
    S.append(Paragraph("Create a new key in Resend, then update the "
                       "<font face='Courier'>AARE_TEMP</font> secret at "
                       "github.com/kejh-z/aare-temp/settings/secrets/actions.", body))

    # 7. Git usage
    S.append(Paragraph("7. Git Usage", h1)); S.append(hr())
    S.append(bullets([
        "Git was initialised locally and pushed to GitHub (github.com/kejh-z/aare-temp).",
        "Default branch renamed from <font face='Courier'>master</font> to "
        "<font face='Courier'>main</font> (GitHub expects main; the Actions UI "
        "was not surfacing the workflow under master).",
        "Each change (adding recipients, switching domains, fixing the workflow) "
        "was a small, separate commit with a descriptive message.",
        "Secrets are never committed &mdash; .env is git-ignored and the "
        "production key lives only as a GitHub Actions secret.",
    ]))

    # 8. Accounts
    S.append(Paragraph("8. Accounts &amp; Credentials", h1)); S.append(hr())
    S.append(make_table([
        ["Service", "Purpose", "Notes"],
        ["GitHub (kejh-z)", "Hosts the repo and runs the workflow", "Repo: aare-temp"],
        ["Resend", "Sends the emails", "holden.ch verified; key stored as the AARE_TEMP secret"],
        ["cron-job.org", "Triggers the workflow at 18:00", "Uses a GitHub personal access token (classic, repo scope)"],
    ], [30 * mm, 50 * mm, doc.width - 80 * mm]))
    S.append(Spacer(1, 5))
    S.append(Paragraph("GitHub repository secrets:", h2))
    S.append(make_table([
        ["Secret", "Purpose"],
        ["AARE_TEMP", "The Resend API key, used to send the email."],
        ["GH_PAT", "A GitHub token (classic, repo scope) used to re-dispatch a fresh run on failure. Can be the same token value cron-job.org uses."],
    ], [34 * mm, doc.width - 34 * mm]))

    # 9. Gotchas
    S.append(Paragraph("9. Known Considerations &amp; Gotchas", h1)); S.append(hr())
    S.append(bullets([
        "<b>The data provider blocks cloud IPs (Imunify360)</b> &mdash; the single "
        "biggest source of failures. Handled by the self-healing retry (section 4): "
        "fresh runs on new IPs. Retrying within one run is useless, since its IP is fixed.",
        "<b>Re-dispatch needs the GH_PAT secret</b> &mdash; without it the workflow can "
        "only try once per trigger (the failure step logs that the secret is missing). "
        "GitHub's built-in token cannot start a new run.",
        "<b>cron-job.org header formatting matters</b> &mdash; the Authorization "
        "value must be exactly <font face='Courier'>Bearer &lt;token&gt;</font>. A "
        "truncated token caused a 401 during setup.",
        "<b>GitHub cron is unreliable</b> &mdash; intentionally not used; a "
        "duplicate email at ~22:16 was a late-firing GitHub cron run before its "
        "<font face='Courier'>schedule:</font> trigger was removed.",
        "<b>Resend free tier</b> originally only allowed sending to the account "
        "owner until the holden.ch domain was verified. Now any recipient works.",
        "If emails land in <b>spam</b>, sending separate emails per recipient "
        "(instead of one with all three in the To field) can improve "
        "deliverability &mdash; easy to switch on if needed.",
    ]))

    doc.build(S)
    print("Wrote", OUTPUT)


if __name__ == "__main__":
    build()
