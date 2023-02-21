frappe.pages['exec-terminal'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Terminal',
		single_column: true
	});
	$(`<div class="terminal"></div>`).appendTo(page.main);
	frappe.require("xterm.bundle.js", ()=> {
		const term = new Terminal();
		term.open(document.getElementsByClassName('terminal'));
		term.write('Hello from \x1B[1;3;31mxterm.js\x1B[0m $ ');
	});
}
