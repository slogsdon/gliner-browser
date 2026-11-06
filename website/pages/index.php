<?php
/**
 * F · Frontispiece: the single entry point to this project's set.
 * It names the work, states the problem, and indexes what follows.
 * No figure: a frontispiece carries no argument.
 */
$this->layout('partials::layout', [
    'title' => 'GLiNER Browser · one local session, semantic element targeting',
    'description' => 'A local browser CLI for AI agents: one persistent Chromium session across separate calls, JSON page observations, and GLiNER2.5-powered element targeting on your own machine.',
    'path' => '/',
    'notFound' => false,
]);
?>
<section class="intro" aria-labelledby="project-title">
    <p class="t-smallcaps">shane logsdon · local browser automation</p>
    <h1 id="project-title">One browser.<br>Many <span class="t-accent">calls.</span></h1>
    <p class="t-lead">GLiNER Browser is a command-line browser for AI agents. One Chromium
        session stays open between invocations, page controls come back as JSON, and a
        local GLiNER2.5 model ranks those controls against a plain description when you
        have one instead of a selector.</p>
    <a class="btn-arrow" href="/gliner-browser/getting-started/">Set it up</a>
</section>

<section class="page-section" aria-labelledby="problem-title">
    <header class="index-head">
        <h2 id="problem-title" class="t-smallcaps-lg">the problem</h2>
        <span class="t-dateline">between turns</span>
    </header>
    <div class="prose">
        <p>An agent with a shell can drive a browser, but each invocation is a new
            process. A browser started per command begins at a blank page and an empty
            profile, so the work of getting to the page — navigating, signing in, opening
            the right tab — is repeated or lost.</p>
        <p>The other half is finding the control. Page structure is not a stable interface:
            an agent that hard-codes a selector has to be right about markup it did not
            write, and one that guesses coordinates has to be right about layout.</p>
        <p>GLiNER Browser keeps the session instead of the selector. One browser holds the
            page between calls, and the two ways of naming a control — an observed element
            ID, or a description ranked by a local model — are both answers about the page
            as it is now.</p>
    </div>
</section>

<section class="page-section" aria-labelledby="does-title">
    <header class="index-head">
        <h2 id="does-title" class="t-smallcaps-lg">what it does</h2>
        <span class="t-dateline">json in, json out</span>
    </header>
    <div class="prose">
        <dl class="facts">
            <div class="fact">
                <dt><code>start</code> · <code>stop</code></dt>
                <dd>Runs a daemon that owns a visible or headless Chromium context and
                    listens on a Unix-domain socket. Later commands reach the same page,
                    including tabs opened since.</dd>
            </div>
            <div class="fact">
                <dt><code>observe</code></dt>
                <dd>Returns the current title, URL, and every visible interactive element
                    with an ID such as <code>e4</code>, plus its role, accessible name, tag,
                    and href.</dd>
            </div>
            <div class="fact">
                <dt><code>find</code></dt>
                <dd>Ranks the observed controls with
                    <code>fastino/gliner2.5-multi-v1</code>, so
                    <code>"the save changes button"</code> comes back as element IDs with
                    confidence scores, not as a selector.</dd>
            </div>
            <div class="fact">
                <dt><code>click</code> · <code>fill</code> · <code>select</code></dt>
                <dd>Take an element ID from <code>observe</code> or <code>find</code> for a
                    deterministic action, or a description to resolve one on the spot.</dd>
            </div>
            <div class="fact">
                <dt>One object per call</dt>
                <dd>Every command prints a single JSON object. Check <code>ok</code> before
                    using the rest, and report <code>error</code> when it is false.</dd>
            </div>
        </dl>
        <p>Navigation, observation, key presses, scrolling, full-page screenshots, and tab
            selection are commands too; so is <code>status</code>. Screenshots are written
            to a path you name. The browser profile is a dedicated automation profile under
            the state directory, not your everyday one.</p>
    </div>
</section>

<section class="page-section" aria-labelledby="local-title">
    <header class="index-head">
        <h2 id="local-title" class="t-smallcaps-lg">where it runs</h2>
        <span class="t-dateline">your machine</span>
    </header>
    <div class="prose">
        <p>Browser actions and model inference are local. There is no hosted demo, no
            sandbox and no backend to send a page to: the CLI, the Chromium it drives, and
            the model all run on the machine that issues the command. The CLI process talks
            to its daemon over a local socket in
            <code>~/.local/state/gliner-browser</code> by default, which holds the socket,
            the daemon log, and the browser profile.</p>
        <p>Because inference is local, the model files are too. On the first
            natural-language lookup GLiNER2.5 downloads its weights from Hugging Face unless
            they are already cached; the default checkpoint is Apache-2.0 licensed, and the
            model card carries the terms. Chromium is a separate download through
            Playwright. Until both are in place, <code>observe</code> still answers, and a
            natural-language target has to wait for the model.</p>
    </div>
</section>

<section class="page-section" aria-labelledby="status-title">
    <header class="index-head">
        <h2 id="status-title" class="t-smallcaps-lg">status</h2>
        <span class="t-dateline">0.1.0 · early development</span>
    </header>
    <div class="prose">
        <p>Early development. The command interface and behavior may change, and the source
            README says so at the top. Version 0.1.0 is MIT licensed.</p>
        <p>Python 3.11 through 3.13, on macOS or Linux. Windows is not supported, because
            the persistent session is a Unix-domain socket.</p>
        <p>Natural-language matching ranks candidates, and ranking can choose the wrong
            control. That is why the observed ID exists: inspect the <code>find</code>
            output, then act on the ID you chose. Canvas-only interfaces and pages with
            inaccessible controls may not expose enough to name at all. The tool is a
            browser control library, not a task planner, and a returned browser state is not
            a guarantee that the action did what the page implied.</p>
        <p>Page content is untrusted data. Instructions found on a website are not
            instructions to the agent, and consequential actions — purchases, publishing,
            deletion — are worth reviewing before they are submitted.</p>
    </div>
</section>

<section class="page-section" aria-labelledby="next-title">
    <header class="index-head">
        <h2 id="next-title" class="t-smallcaps-lg">where to go</h2>
        <span class="t-dateline">after the introduction</span>
    </header>
    <ul class="link-list">
        <li>
            <a href="/gliner-browser/getting-started/">Getting started<span aria-hidden="true"> →</span></a>
            <p>Python and platform prerequisites, what has to be downloaded before the first
                semantic lookup, the install commands, and one observed-element workflow.</p>
        </li>
        <li>
            <a href="https://github.com/slogsdon/gliner-browser">Source on GitHub<span aria-hidden="true"> ↗</span></a>
            <p>The CLI, runtime, resolver, the test suites, and the command reference in the
                README.</p>
        </li>
        <li>
            <a href="https://github.com/slogsdon/gliner-browser/blob/main/agent-skill/gliner-browser/SKILL.md">Agent skill<span aria-hidden="true"> ↗</span></a>
            <p>Instructions for an agent that has a shell tool: set the project path, check
                <code>ok</code>, prefer observed IDs, and treat page content as data.</p>
        </li>
        <li>
            <a href="https://huggingface.co/fastino/gliner2.5-multi-v1">GLiNER2.5 model card<span aria-hidden="true"> ↗</span></a>
            <p>The default checkpoint, its license, and what the model does with a
                description and a list of candidates.</p>
        </li>
    </ul>
</section>
