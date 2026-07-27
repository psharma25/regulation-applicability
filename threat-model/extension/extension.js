const vscode = require('vscode');
const path = require('path');

let panel = null;
let watcher = null;
const cfg = () => vscode.workspace.getConfiguration('askg');
const root = () => (vscode.workspace.workspaceFolders || [])[0];
const enc = new TextEncoder(), dec = new TextDecoder();

function uriFor(rel) {
  const r = root();
  if (!r) return null;
  return vscode.Uri.joinPath(r.uri, ...rel.split('/'));
}

async function readWorkspaceTree() {
  const excl = '{' + cfg().get('excludeGlobs').join(',') + '}';
  const files = await vscode.workspace.findFiles('**/*', excl, cfg().get('maxFiles'));
  const base = root().uri.path;
  return files.map(f => f.path.startsWith(base) ? f.path.slice(base.length + 1) : path.basename(f.path));
}

async function readModel() {
  const u = uriFor(cfg().get('modelPath'));
  if (!u) return null;
  try { return JSON.parse(dec.decode(await vscode.workspace.fs.readFile(u))); }
  catch (e) { return null; }
}

async function writeModel(project) {
  const u = uriFor(cfg().get('modelPath'));
  if (!u) return;
  await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(u, '..'));
  await vscode.workspace.fs.writeFile(u, enc.encode(JSON.stringify(project, null, 2)));
}

function post(msg) { if (panel) panel.webview.postMessage(msg); }

async function openPanel(context) {
  if (panel) { panel.reveal(vscode.ViewColumn.One); return panel; }
  panel = vscode.window.createWebviewPanel('askg', 'AI Security Knowledge Graph', vscode.ViewColumn.One, {
    enableScripts: true, retainContextWhenHidden: true,
    localResourceRoots: [vscode.Uri.joinPath(context.extensionUri, 'media')]
  });
  const html = dec.decode(await vscode.workspace.fs.readFile(vscode.Uri.joinPath(context.extensionUri, 'media', 'index.html')));
  panel.webview.html = html;
  panel.onDidDispose(() => { panel = null; });

  panel.webview.onDidReceiveMessage(async msg => {
    if (msg.type === 'ready') {
      const m = await readModel();
      if (m) post({ type: 'model', project: m });
    } else if (msg.type === 'requestTree') {
      const paths = await readWorkspaceTree();
      post({ type: 'tree', paths, name: root() ? path.basename(root().uri.fsPath) : 'Workspace' });
    } else if (msg.type === 'saveModel') {
      await writeModel(msg.project);
      vscode.window.setStatusBarMessage('Threat model written to ' + cfg().get('modelPath'), 3000);
    } else if (msg.type === 'log') {
      console.log('[askg]', msg.text);
    }
  });
  return panel;
}

function startWatcher(context) {
  const r = root(); if (!r) return;
  const folder = cfg().get('intakeFolder');
  const pattern = new vscode.RelativePattern(r, folder + '/**/*.{sarif,json,csv,xml}');
  watcher = vscode.workspace.createFileSystemWatcher(pattern);
  const send = async uri => {
    if (!panel) await openPanel(context);
    const text = dec.decode(await vscode.workspace.fs.readFile(uri));
    post({ type: 'intake', name: path.basename(uri.fsPath), payload: text });
    vscode.window.showInformationMessage('Sent ' + path.basename(uri.fsPath) + ' to the security agents.');
  };
  watcher.onDidCreate(send);
  watcher.onDidChange(send);
  context.subscriptions.push(watcher);
}

function activate(context) {
  const reg = (id, fn) => context.subscriptions.push(vscode.commands.registerCommand(id, fn));

  reg('askg.open', async () => {
    await openPanel(context);
    post({ type: 'requestTree' });
  });
  reg('askg.sync', async () => {
    await openPanel(context);
    post({ type: 'tree', paths: await readWorkspaceTree(), name: path.basename(root().uri.fsPath) });
  });
  reg('askg.agents', async () => { await openPanel(context); post({ type: 'command', command: 'runAgents' }); });
  reg('askg.clean', async () => { await openPanel(context); post({ type: 'command', command: 'clean' }); });
  reg('askg.export', async () => { await openPanel(context); post({ type: 'command', command: 'export' }); });
  reg('askg.framework', async () => {
    const pick = await vscode.window.showQuickPick(
      [{ label: 'STRIDE', id: 'stride' }, { label: 'MITRE ATLAS', id: 'atlas' },
       { label: 'MITRE ATT&CK', id: 'attack' }, { label: 'ATT&CK for ICS', id: 'ics' }],
      { placeHolder: 'Which framework should run over the model?' });
    if (!pick) return;
    await openPanel(context);
    post({ type: 'command', command: 'framework', framework: pick.id });
  });
  reg('askg.ingest', async uri => {
    const target = uri || (await vscode.window.showOpenDialog({ canSelectMany: false }))?.[0];
    if (!target) return;
    await openPanel(context);
    const text = dec.decode(await vscode.workspace.fs.readFile(target));
    post({ type: 'intake', name: path.basename(target.fsPath), payload: text });
  });

  startWatcher(context);
  if (cfg().get('openOnStartup')) vscode.commands.executeCommand('askg.open');
}
function deactivate() { if (watcher) watcher.dispose(); }
module.exports = { activate, deactivate };
