from pathlib import Path

root = Path("build-src/TermuxWorkspace/app/src/main/java/dev/jita/workspace")

def edit(name, fn):
    p = root / name
    s = p.read_text(encoding="utf-8")
    out = fn(s)
    if out == s:
        raise RuntimeError("No changes applied to " + name)
    p.write_text(out, encoding="utf-8")
    print("Patched", p)

def models(s):
    old = '"w_ubuntu", "ubuntu-go"'
    if old not in s:
        raise RuntimeError("Ubuntu launcher mapping not found")
    return s.replace(old, '"w_ubuntu", "ubuntu-work"', 1)

def terminal(s):
    out = []
    found_status = found_launch = False
    for line in s.splitlines(keepends=True):
        if 'setStatus("Connesso · ' in line:
            line = '                    setStatus("Connesso · " + store.startupCommand(workspace).trim())\n'
            found_status = True
        if 'val launch = "tmux new-session -A -s ' in line:
            line = (
                '                    // Run the user\'s original Termux command. Do not nest tmux.\n'
                '                    // bash -ic sources the original Termux ~/.bashrc.\n'
                '                    val launcher = store.startupCommand(workspace).trim()\n'
                '                    val launch = if (launcher.isEmpty()) "\\n" else "bash -ic " + shQuote(launcher) + "\\n"\n'
            )
            found_launch = True
        out.append(line)
    if not (found_status and found_launch):
        raise RuntimeError("Terminal startup spans not found")
    return "".join(out)

def screens(s):
    if 'controller.runCommand(command)' not in s:
        raise RuntimeError("Launcher button not found")
    s = s.replace('            controller.runCommand(command)\n', '', 1)
    s = s.replace('}) { Text("Esegui") }', '}) { Text("Salva") }', 1)
    s = s.replace(
        'Il comando viene inviato alla stessa sessione tmux. Nessun nuovo ambiente Linux.',
        'Questo comando Termux viene avviato automaticamente alla prossima apertura. Usa quello originale, senza tmux aggiuntivi.',
        1
    )
    out = []
    found = False
    for line in s.splitlines(keepends=True):
        if 'Text("SESSION / ' in line:
            line = '                Text("LAUNCHER / " + store.startupCommand(space).uppercase(), color = SoftText,\n'
            found = True
        out.append(line)
    if not found:
        raise RuntimeError("Session label not found")
    return "".join(out)

edit("WorkspaceModels.kt", models)
edit("TerminalController.kt", terminal)
edit("Screens.kt", screens)
print("Original Termux launchers enabled")
