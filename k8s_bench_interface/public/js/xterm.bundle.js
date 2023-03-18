import { Terminal } from 'xterm';
import { AttachAddon } from 'xterm-addon-attach';
import { FitAddon } from 'xterm-addon-fit';
import copy from 'copy-to-clipboard';

window.Terminal = Terminal;
window.AttachAddon = AttachAddon;
window.FitAddon = FitAddon;
window.copyToClipBoard = copy;
