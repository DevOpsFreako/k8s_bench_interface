/* global frappe, $, Terminal, AttachAddon, FitAddon, copyToClipBoard */

frappe.pages['exec-terminal'].on_page_load = async wrapper => {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Terminal',
    single_column: true,
  });
  await configure(page);
};

const configure = async page => {
  const query = new URL(window.location.href).searchParams;
  const namespace = query.get('namespace');
  const name = query.get('name');
  const command = query.get('command') || 'sh';

  if (!name) {
    throw new Error('name required');
  }

  if (!namespace) {
    throw new Error('namespace required');
  }

  const { message } = await frappe.call({
    method: 'k8s_bench_interface.endpoints.get_pod_exec_info',
  });
  $('<div id="terminal"></div>').appendTo(page.main);
  const wsUrl =
    message.terminal_socket_endpoint +
    `/ws/${namespace}/${name}?command=${command}&token=` +
    message.token;

  const term = new Terminal({ cursorBlink: true, convertEol: true });
  const socket = new WebSocket(wsUrl);
  const attachAddon = new AttachAddon(socket);
  term.loadAddon(attachAddon);
  const fitAddon = new FitAddon();
  term.loadAddon(fitAddon);
  fitAddon.fit();
  term.reset();
  term.open(document.getElementById('terminal'));

  socket.onopen = () => socket.send('hostname\r');
  socket.onclose = event => {
    term.writeln('');
    term.writeln('  \u001b[31m[!] Lost connection');
  };

  document.addEventListener('keydown', zEvent => {
    if (zEvent.ctrlKey && zEvent.shiftKey && zEvent.key === 'C') {
      zEvent.preventDefault();
      copyToClipBoard(term.getSelection());
    }
  });

  window.onresize = () => {
    fitAddon.fit();
  };
};
