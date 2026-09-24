---
name: agent-activity-log
version: 1.0.0
description: Keep a live, timestamped activity log as a published artifact while a coordinator agent works unattended, with a clear "needs you" section the user can trust at a glance. Use for long or unattended runs, scheduled sessions, or whenever the user says "while I'm away", "keep going without me", "keep a log", "log what you do", "status page" or "progress page". Not for a task that fits in one reply.
---

# Agent activity log

A coordinator agent keeps one published artifact page per session or task. The page tells the user, at a glance, what state things are in, what needs them, and what happened when. It is republished on every meaningful event, so the user can open the link at any time and trust it.

Three qualities are the point of this skill: **timestamps on everything**, **an explicit split between what needs the user and what doesn't**, and **brevity**.

## When to use

- The user starts a long or unattended task ("I'm heading out", "keep going while I'm away", "keep a log", "log what you do").
- You are coordinating subagents, deploys, pull requests or a service fix that will outlast the user's attention.
- A session started by a scheduled task, where nobody is watching live.
- Not for a quick one-off answer. If the whole task fits in one reply, skip the log.

## Lifecycle

1. **Start.** Before the first real action:
   - Read the clock (see Timestamps below).
   - Load the `artifact-design` skill once if the harness offers it. The template below already follows its contract.
   - Write the page from the template to the session scratchpad directory (or a temporary directory if there is none) as `<project>-log-<YYYYMMDD-HHMM>.html`, and publish it with the Artifact tool with `icon: "log"` and a one sentence `description`.
   - Give the user the link once, in one line. Text between tool calls may never reach them, so if the harness has a tool for messaging the user directly (a `SendUserMessage` or `PushNotification` tool, for example, loaded through ToolSearch if it is deferred), use it. Otherwise put the link in your next reply.
2. **Update on every meaningful event.** Republish with the **same file path** so the URL stays the same. Omit `icon` on republish. If several events land within a couple of minutes, write them as separate rows but republish once. The log must never slow the work it describes.
3. **Finish.** Final republish: set the "Last updated" line to "Finished HH:MM", make sure every open ask is in the asks list, and fill the footer. Tell the user in one or two sentences what state things are in and how many asks are waiting. In an unattended or scheduled run, send that through the direct messaging tool too.

One page per session or task. A new stretch of work gets a new page, not an append to an old one.

### What counts as a meaningful event

Log it: a decision, a merge, a pull request opened or changing state, a deploy or rollout, a run started or stopped, a hypothesis confirmed or disproved, a blocker, a subagent finishing, anything the user authorised being used, anything that now needs the user.

Don't log it: routine reads, searches, retries that changed nothing, intermediate thinking. If a row would say "Still checking", it is not an event.

### Who writes

Only the coordinator writes the log. Subagents report back to the coordinator, which condenses their results into rows. Never let two agents republish the same page.

## Timestamps

- Use the user's local time zone. Take it from what you already know: project instructions, system context, or something the user has said. If you don't know it and the user is still around, ask once at the start. Otherwise use UTC and say so in the eyebrow.
- Sandboxes usually run on UTC, so always set the zone explicitly: `TZ=<zone> date '+%Y-%m-%d %H:%M'` at the start, `TZ=<zone> date '+%H:%M'` before each update. Never estimate a time, and never reuse an earlier one.
- Format `HH:MM`, 24 hour clock. The date lives once, in the eyebrow.
- For events you infer rather than observe, mark the uncertainty: `≤10:04`, `~09:30`.
- Update "Last updated HH:MM" on every republish.
- Timeline is chronological, oldest first. "What I need from you" at the top is the "now" view, so the timeline can read like a story.

## Page structure

Always in this order. Sections marked optional are left out entirely when empty, never shown with placeholder text. "What I need from you" is always present.

1. **Header.** Eyebrow `project · environment · D Mon YYYY`, a plain title that says what the page is, "Last updated HH:MM", and a strip of **status pills** (3 to 6). Each pill is one current fact: `ok` green, `warn` amber, `bad` red. Pills describe the state now, so rewrite them as things change rather than adding more.
2. **Read this first** (optional, `.callout`). Only when something is broken, risky, or surprising. At most three short paragraphs, each opening with a bold sentence that stands on its own. Red edge for broken, amber (`warn-edge`) for risk. Remove it once the situation is resolved and say so in the timeline.
3. **What I need from you** (always). A numbered list, most urgent first. Each item starts with a bold imperative and a link ("**Merge repo #85** to bring the service back."), then at most two sentences on what it does and how to check it worked. When nothing is waiting, write one line: "Nothing needs you right now." When the user does an ask, remove it here and add a timeline row ("You merge #85.").
4. **Timeline.** One row per event: `<time>` and one or two sentences. Rows for bad events get `class="bad-row"`. Past about 20 rows, move the oldest into a `<details>` block titled "Earlier (HH:MM to HH:MM)" at the top of the log so the recent part stays visible.
5. **Changes** (optional). A table of pull requests, deploys or other changes: link, state pill, one line of what. State pills: `ok` for merged or done, `warn` for draft or open, add "· needs you" to the pill when it is also an ask. Mark anything you merged yourself as "merged by me".
6. **Footer.** One or two sentences on authority: what you did on your own under rules the user gave you, and that everything else is a pull request, a draft or a note for them.

## Writing rules

- **Write in the user's language.** The page is for them, so use the language they write to you in.
- **Brevity first.** A row is one or two sentences. An ask is three at most. If a detail matters, link to it (pull request, run, log) instead of pasting it.
- **State facts, then consequence.** "First 502 from `api` behind the reverse proxy." not "It seems there may be some issues".
- **Own mistakes in place.** Never delete or rewrite a past row that turned out wrong. Add a new row that corrects it ("The errors predate the deploy. My 10:48 attribution was wrong.").
- **Separate attention from information.** Anything the user must act on goes in the asks list, even if it is also in the timeline. Nothing in the timeline or table should require action they could miss.
- **Punctuate with commas and full stops, not dashes.** Hyphens only inside compound words.
- Use `<code>` for identifiers, commands and endpoints. Link pull requests as `repo #N`, whichever forge hosts them.
- Never claim an action you didn't take or authority you weren't given.

## Editing the page

Keep the source file and edit it in place with the Edit tool. Don't regenerate the whole page each time: it costs tokens and risks silently dropping earlier rows.

- New timeline row: insert before `<!--MORE_LOG-->`.
- New change row: insert before `<!--MORE_CHANGES-->`.
- Update the "Last updated" line and the pills on every edit.
- Then republish with the same `file_path`.

If the user leaves comments on the artifact, read them with `ArtifactComments` (load it through ToolSearch if it is deferred), act on them, and log that as an event.

## Template

The Artifact tool wraps the file in the document skeleton (doctype, `head` with charset and viewport, `body`), so the file has none of those tags. Replace the CAPITALISED placeholders and the project name in the `<title>`.

```html
<title>PROJECT Activity Log</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
  :root {
    --ground:#f3f5f7; --surface:#fff; --ink:#1a2330; --muted:#586676; --rule:#d9e0e7; --code:#e9eef3; --accent:#1d6a86;
    --ok:#17803f; --ok-bg:#e2f3e8; --warn:#93650a; --warn-bg:#f8eed4; --bad:#b8322a; --bad-bg:#f9e3e0;
    --sans:"Source Sans 3",-apple-system,"Segoe UI",Roboto,sans-serif; --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
  }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
    color-scheme:dark; --ground:#0f141a; --surface:#161d25; --ink:#e3e8ee; --muted:#93a0ae; --rule:#27313c; --code:#1d2630; --accent:#6fb6d2;
    --ok:#5ccf85; --ok-bg:#15301f; --warn:#e3b64b; --warn-bg:#33290f; --bad:#f08075; --bad-bg:#3a1c1a; } }
  :root[data-theme="dark"] {
    color-scheme:dark; --ground:#0f141a; --surface:#161d25; --ink:#e3e8ee; --muted:#93a0ae; --rule:#27313c; --code:#1d2630; --accent:#6fb6d2;
    --ok:#5ccf85; --ok-bg:#15301f; --warn:#e3b64b; --warn-bg:#33290f; --bad:#f08075; --bad-bg:#3a1c1a; }
  body { background:var(--ground); color:var(--ink); font:16px/1.6 var(--sans); margin:0; padding-inline:20px; padding-block:36px 64px; }
  main { max-width:800px; margin:0 auto; display:grid; gap:36px; }
  h1,h2 { margin:0; line-height:1.25; text-wrap:balance; } h1 { font-size:1.85rem; } h2 { font-size:1.2rem; }
  p { margin:0; max-width:68ch; } a { color:var(--accent); text-underline-offset:2px; }
  code { font-family:var(--mono); font-size:.84em; background:var(--code); padding:1px 5px; border-radius:4px; overflow-wrap:anywhere; }
  section, header { display:grid; gap:12px; }
  .eyebrow { font-family:var(--mono); font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
  .updated { color:var(--muted); font-size:.92rem; }
  .strip { display:flex; flex-wrap:wrap; gap:8px; }
  .pill { font-family:var(--mono); font-size:.76rem; font-weight:600; padding:3px 10px; border-radius:999px; white-space:nowrap; }
  .ok { color:var(--ok); background:var(--ok-bg); } .warn { color:var(--warn); background:var(--warn-bg); } .bad { color:var(--bad); background:var(--bad-bg); }
  .callout { border-left:4px solid var(--bad); background:var(--surface); padding:16px 18px; border-radius:0 6px 6px 0; }
  .callout.warn-edge { border-left-color:var(--warn); }
  ol.asks { margin:0; padding-left:22px; display:grid; gap:10px; }
  .log { display:grid; border:1px solid var(--rule); border-radius:6px; background:var(--surface); overflow:hidden; }
  .log > div { display:grid; grid-template-columns:5.2rem 1fr; gap:14px; padding:10px 14px; }
  .log > div + div, .log > details + div { border-top:1px solid var(--rule); }
  .log details { padding:10px 14px; } .log summary { cursor:pointer; color:var(--muted); }
  .log time { font-family:var(--mono); font-size:.85rem; color:var(--muted); font-variant-numeric:tabular-nums; }
  .log .bad-row time { color:var(--bad); font-weight:600; }
  .table-wrap { overflow-x:auto; border:1px solid var(--rule); border-radius:6px; background:var(--surface); }
  table { border-collapse:collapse; width:100%; font-size:.94rem; }
  th,td { text-align:left; vertical-align:top; padding:10px 14px; }
  th { font-family:var(--mono); font-size:.7rem; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); border-bottom:1px solid var(--rule); }
  tr + tr td { border-top:1px solid var(--rule); } td:first-child { white-space:nowrap; }
  footer { color:var(--muted); font-size:.86rem; border-top:1px solid var(--rule); padding-top:14px; }
  @media (max-width:560px) { body { padding-inline:16px; padding-block:24px 48px; } h1 { font-size:1.5rem; } .log > div { grid-template-columns:1fr; gap:2px; } }
</style>

<main>
  <header>
    <span class="eyebrow">PROJECT · ENV · D Mon YYYY</span>
    <h1>PLAIN TITLE OF WHAT THIS RUN IS</h1>
    <p class="updated">Last updated HH:MM</p>
    <div class="strip" aria-label="Current state">
      <span class="pill ok">FACT</span>
      <span class="pill warn">FACT</span>
    </div>
  </header>

  <!-- Optional. Remove when nothing is broken or surprising. -->
  <section class="callout" aria-labelledby="now">
    <h2 id="now">Read this first</h2>
    <p><b>ONE SENTENCE THAT STANDS ALONE.</b> One or two sentences of context.</p>
  </section>

  <section aria-labelledby="asks">
    <h2 id="asks">What I need from you</h2>
    <ol class="asks">
      <li><b>VERB <a href="URL">repo #N</a></b> to OUTCOME. How to check it worked.</li>
    </ol>
    <!-- When empty: <p>Nothing needs you right now.</p> -->
  </section>

  <section aria-labelledby="log">
    <h2 id="log">Timeline (local time)</h2>
    <div class="log">
      <div><time>HH:MM</time><span>Started. GOAL IN ONE SENTENCE.</span></div>
      <!--MORE_LOG-->
    </div>
  </section>

  <!-- Optional. -->
  <section aria-labelledby="changes">
    <h2 id="changes">Changes</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>Change</th><th>State</th><th>What</th></tr></thead>
      <tbody>
        <!--MORE_CHANGES-->
      </tbody>
    </table></div>
  </section>

  <footer>Kept by Claude while you were away. I only did WHAT YOU AUTHORISED on my own. Everything else is a pull request or a note for you.</footer>
</main>
```
