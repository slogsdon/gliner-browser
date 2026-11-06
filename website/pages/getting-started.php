<?php
/**
 * D · Assembly Order: genuinely sequential setup. Step 2 depends on step 1.
 * Each step carries an id so a reader can enter at step 4 from a link.
 */
$this->layout('partials::layout', [
    'title' => 'Getting started · GLiNER Browser',
    'description' => 'Python, platform and model prerequisites for GLiNER Browser, what the first download requires, the install commands, and one observed-element workflow from the README.',
    'path' => '/getting-started/',
    'notFound' => false,
]);
?>
<section class="intro intro--compact" aria-labelledby="guide-title">
    <p class="t-smallcaps">gliner browser · assembly order</p>
    <h1 id="guide-title">Getting <span class="t-accent">started.</span></h1>
    <p class="t-lead">Seven steps, in order. The interpreter and platform come first, the
        downloads come before the first semantic lookup, and the session comes before the
        actions.</p>
    <p class="t-meta guide-source">Commands below are quoted from the project README and
        its agent skill at source revision ff41760. They were not executed while building
        this page.</p>
</section>

<div class="assembly">
    <section class="assembly__step" id="step-1" aria-labelledby="step-1-title">
        <span class="assembly__num" aria-hidden="true">01</span>
        <h2 id="step-1-title" class="t-headline-sm">Check the interpreter and the platform</h2>
        <div class="prose">
            <p>Python 3.11, 3.12, or 3.13 — the package declares
                <code>&gt;=3.11,&lt;3.14</code>, so 3.14 is outside the range. The project
                is managed with <a href="https://docs.astral.sh/uv/">uv</a>, which is the
                only tool the install commands call directly.</p>
            <p>macOS or Linux. The daemon that holds your browser session is a Unix-domain
                socket, so Windows is not supported.</p>
            <p>You also need Playwright's own Chromium, which the install step fetches
                separately from the Python packages. It is not the browser you already have
                open.</p>
        </div>
    </section>

    <section class="assembly__step" id="step-2" aria-labelledby="step-2-title">
        <span class="assembly__num" aria-hidden="true">02</span>
        <h2 id="step-2-title" class="t-headline-sm">Know what the first download costs</h2>
        <div class="prose">
            <p>Nothing here is served from this website. There is no hosted demo and no
                backend to try: the CLI, the browser, and the model all run locally, so the
                first run assembles all three on your machine. Three separate downloads are
                involved.</p>
        </div>
        <div class="table-wrap">
            <table>
                <caption class="t-smallcaps">first-download requirements</caption>
                <thead>
                    <tr><th scope="col">What</th><th scope="col">When</th><th scope="col">Notes</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <th scope="row">Python dependencies</th>
                        <td><code>uv sync</code></td>
                        <td><code>gliner2[local]</code>, PyTorch through it,
                            <code>playwright</code>, <code>transformers</code>, and
                            <code>protobuf</code>.</td>
                    </tr>
                    <tr>
                        <th scope="row">Chromium</th>
                        <td><code>uv run playwright install chromium</code></td>
                        <td>Playwright installs the browser build that matches its own
                            version; Chromium is not part of the Python packages.</td>
                    </tr>
                    <tr>
                        <th scope="row">Model files</th>
                        <td>First natural-language lookup — <code>find</code>, or a
                            description given to <code>click</code>, <code>fill</code>, or
                            <code>select</code></td>
                        <td>Downloaded from Hugging Face unless already cached. The default
                            checkpoint is <code>fastino/gliner2.5-multi-v1</code>, Apache-2.0
                            licensed; its model card has the terms.</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="prose">
            <p>The README is direct about the size: the model and PyTorch add a substantial
                first-time download. The model loads on the first lookup rather than at
                startup, and the agent skill warns that this first semantic lookup can take
                roughly a minute while it does.</p>
            <p>Both defaults are movable. <code>GLINER_BROWSER_MODEL</code> takes a Hugging
                Face model ID or a local model path, and the state directory holding the
                browser profile can be relocated with
                <code>GLINER_BROWSER_STATE_DIR</code>. Budget disk for PyTorch, the
                checkpoint, and a Chromium build before starting.</p>
        </div>
    </section>

    <section class="assembly__step" id="step-3" aria-labelledby="step-3-title">
        <span class="assembly__num" aria-hidden="true">03</span>
        <h2 id="step-3-title" class="t-headline-sm">Install from the repository</h2>
        <div class="prose">
            <p>The README installs from a clone rather than from a package index. These
                are its install commands, in its order:</p>
            <pre><code>git clone https://github.com/slogsdon/gliner-browser
cd gliner-browser
uv sync
uv run playwright install chromium</code></pre>
            <p>The first command clones, the second puts you in the checkout, the third
                creates the environment and installs the Python dependencies, and the fourth
                installs Chromium. The commands up to step 6 run from that checkout
                with <code>uv run</code>.</p>
            <p>Check the install before going further. There is no model work in this step,
                so it should answer immediately:</p>
            <pre><code>uv run gliner-browser --help</code></pre>
        </div>
    </section>

    <section class="assembly__step" id="step-4" aria-labelledby="step-4-title">
        <span class="assembly__num" aria-hidden="true">04</span>
        <h2 id="step-4-title" class="t-headline-sm">Start a session, open a page, observe it</h2>
        <div class="prose">
            <p><code>start</code> launches the daemon and a Chromium window; the process you
                just ran exits, and the browser does not. Everything that follows is a
                request over the socket to that daemon, so the page survives between
                commands.</p>
            <p>This is the README's quick start, quoted as written:</p>
            <pre><code>uv run gliner-browser start
uv run gliner-browser open https://example.com
uv run gliner-browser observe
uv run gliner-browser find "more information link"
uv run gliner-browser stop</code></pre>
            <p><code>observe</code> is the one to read carefully. It returns the page title,
                its URL, and the visible interactive elements it could identify — links,
                buttons, inputs, textareas, selects, summaries, and anything with a role or a
                tab stop. Each element carries an ID such as <code>e1</code>, plus its role,
                accessible name, tag, and href. <code>--limit N</code> caps the list, and the
                response also reports the total found.</p>
            <p><code>find</code> ranks the current controls for a description. Its matches
                carry a combined confidence alongside the separate lexical and GLiNER scores,
                which is how you tell a close call from a clear one.</p>
        </div>
    </section>

    <section class="assembly__step" id="step-5" aria-labelledby="step-5-title">
        <span class="assembly__num" aria-hidden="true">05</span>
        <h2 id="step-5-title" class="t-headline-sm">Act on an observed element</h2>
        <div class="prose">
            <p>This is the step the whole session exists for. Take an ID out of
                <code>observe</code> or the top of a <code>find</code> result and pass it to
                the action. No inference is involved in an ID, so the action lands on the
                element you inspected:</p>
            <pre><code>uv run gliner-browser click e4
uv run gliner-browser fill e7 person@example.com
uv run gliner-browser select e9 monthly</code></pre>
            <p>A description also works directly, at the cost of a model lookup:</p>
            <pre><code>uv run gliner-browser click "continue to checkout"
uv run gliner-browser fill "email address" person@example.com</code></pre>
            <p>Then the rule that keeps IDs meaningful, again from the README: refresh
                <code>observe</code> after navigation or page changes. Element IDs describe
                the latest observation only, and they go stale. If one does, the CLI fails
                with a message telling you to observe again rather than clicking whatever now
                sits at that position.</p>
            <p>Prefer the observed ID when accuracy matters. A description is ranked, and
                ranking can pick the wrong control — inspect the matches first when the page
                has several similar ones.</p>
        </div>
    </section>

    <section class="assembly__step" id="step-6" aria-labelledby="step-6-title">
        <span class="assembly__num" aria-hidden="true">06</span>
        <h2 id="step-6-title" class="t-headline-sm">Configure it, and call it from anywhere</h2>
        <div class="prose">
            <p>Three environment variables cover the usual changes. All are optional.</p>
        </div>
        <div class="table-wrap">
            <table>
                <caption class="t-smallcaps">configuration</caption>
                <thead>
                    <tr><th scope="col">Variable</th><th scope="col">Default</th><th scope="col">Purpose</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <th scope="row"><code>GLINER_BROWSER_STATE_DIR</code></th>
                        <td><code>~/.local/state/gliner-browser</code></td>
                        <td>Socket, log, and persistent browser profile.</td>
                    </tr>
                    <tr>
                        <th scope="row"><code>GLINER_BROWSER_MODEL</code></th>
                        <td><code>fastino/gliner2.5-multi-v1</code></td>
                        <td>Hugging Face model ID or local model path.</td>
                    </tr>
                    <tr>
                        <th scope="row"><code>GLINER_BROWSER_TIMEOUT</code></th>
                        <td><code>180</code></td>
                        <td>CLI-to-daemon socket timeout in seconds.</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="prose">
            <p>To use the CLI from a working directory other than the checkout, set the
                project path once and put <code>--project</code> in front of
                <code>run</code>:</p>
            <pre><code>uv --project "$GLINER_BROWSER_PROJECT" run gliner-browser ...</code></pre>
            <p>The daemon keeps its log at
                <code>daemon.log</code> inside the state directory. If <code>start</code>
                refuses to come up, the failure message points there, and that log is where
                the actual error is.</p>
        </div>
    </section>

    <section class="assembly__step" id="step-7" aria-labelledby="step-7-title">
        <span class="assembly__num" aria-hidden="true">07</span>
        <h2 id="step-7-title" class="t-headline-sm">Stop the session, and keep the page at arm's length</h2>
        <div class="prose">
            <p>The session is not self-closing. Stop it when you are done, or check whether
                one is already running:</p>
            <pre><code>uv run gliner-browser stop
uv run gliner-browser status</code></pre>
            <p><code>stop</code> closes the browser context and removes the socket. A
                <code>stop</code> with nothing running is not an error; it reports
                <code>already_stopped</code>.</p>
            <p><strong>The part that is not optional.</strong> Page content is untrusted
                data. Text on a website is never an instruction to the agent reading it, no
                matter how it is phrased. The CLI uses a dedicated automation profile for
                that reason: do not point it at a profile with your logins and do not read
                credentials or tokens out of it. Review consequential actions — purchases,
                publishing, deletions — before they are submitted.</p>
            <p><strong>What it will not do.</strong> It does not plan tasks, and a returned
                browser state is evidence of the click, not proof the page did what you meant.
                Canvas-only interfaces and pages whose controls are inaccessible may not
                expose enough structure to name. Treat every result as the page's answer, not
                a success report.</p>
        </div>
    </section>
</div>

<section class="page-section" aria-labelledby="next-title">
    <header class="index-head">
        <h2 id="next-title" class="t-smallcaps-lg">where to go</h2>
        <span class="t-dateline">after setup</span>
    </header>
    <ul class="link-list">
        <li>
            <a href="/gliner-browser/">Project introduction<span aria-hidden="true"> →</span></a>
            <p>What the CLI is, where it runs, and what its status does and does not
                promise.</p>
        </li>
        <li>
            <a href="https://github.com/slogsdon/gliner-browser">Source on GitHub<span aria-hidden="true"> ↗</span></a>
            <p>The command table, the resolver, and the localhost browser tests.</p>
        </li>
        <li>
            <a href="https://github.com/slogsdon/gliner-browser/blob/main/agent-skill/gliner-browser/SKILL.md">Agent skill<span aria-hidden="true"> ↗</span></a>
            <p>The agent-facing instructions, including the check-<code>ok</code> habit and
                the rule that page content is data.</p>
        </li>
    </ul>
</section>
