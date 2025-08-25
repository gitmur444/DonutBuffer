import curses

from .agent_injector import AgentInjector


class CursesUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.injector = AgentInjector()
        self.input_lines: list[str] = [""]
        self.running = True
        self.out_win = None
        self.in_win = None
        self._init_layout()
        self.out_yx = [1, 2]  # cursor in output pane

    def _init_layout(self):
        self.stdscr.clear()
        self.stdscr.nodelay(False)
        self.stdscr.keypad(True)
        curses.curs_set(1)
        h, w = self.stdscr.getmaxyx()
        out_h = max(3, h - 7)
        self.out_win = curses.newwin(out_h, w, 0, 0)
        self.in_win = curses.newwin(5, w, out_h + 1, 0)
        # Borders
        self.out_win.border()
        try:
            self.out_win.addstr(0, 2, " Output ")
        except curses.error:
            pass
        self.out_win.noutrefresh()
        self._render_input()
        curses.doupdate()

    def _render_input(self):
        self.in_win.clear()
        self.in_win.border()
        title = " Prompt (Enter=send, Ctrl+J=newline, Ctrl+C=exit) "
        try:
            self.in_win.addstr(0, 2, title)
        except curses.error:
            pass
        # Placeholder if empty
        lines = self.input_lines if any(self.input_lines) else ["→ Plan, search, build anything"]
        y = 1
        for line in lines:
            try:
                self.in_win.addstr(y, 2, line)
            except curses.error:
                pass
            y += 1
        self.in_win.noutrefresh()

    def append_chunk(self, text: str):
        # Write chunk to output pane without clearing
        try:
            self.out_win.addstr(text)
        except curses.error:
            pass
        self.out_win.noutrefresh()
        curses.doupdate()

    def newline_output(self):
        self.append_chunk("\n")

    def read_loop(self):
        self._init_layout()
        while self.running:
            ch = self.stdscr.get_wch()
            if ch == curses.KEY_RESIZE:
                self._init_layout()
                continue
            if isinstance(ch, str):
                if ch == "\n":  # Enter -> send
                    prompt = "\n".join(self.input_lines).strip()
                    if prompt:
                        # Draw a small box of the prompt into output
                        w = self.out_win.getmaxyx()[1]
                        edge = min(len(prompt), max(10, w - 6))
                        top = "┌" + "─" * edge + "┐\n"
                        mid = "│ " + prompt[: edge - 2] + " │\n"
                        bot = "└" + "─" * edge + "┘\n"
                        self.append_chunk(top + mid + bot)
                        self._send_prompt(prompt)
                    self.input_lines = [""]
                    self._render_input()
                    curses.doupdate()
                elif ch == "\x0a":  # Ctrl+J -> newline
                    self.input_lines.append("")
                    self._render_input()
                    curses.doupdate()
                elif ch == "\x03":  # Ctrl+C
                    self.running = False
                    break
                elif ch == "\x7f":  # Backspace
                    if self.input_lines and self.input_lines[-1]:
                        self.input_lines[-1] = self.input_lines[-1][:-1]
                    elif len(self.input_lines) > 1:
                        self.input_lines.pop()
                    self._render_input()
                    curses.doupdate()
                else:
                    self.input_lines[-1] += ch
                    self._render_input()
                    curses.doupdate()
            else:
                pass

    def _send_prompt(self, prompt: str):
        def on_user(_t: str):
            pass

        def on_chunk(t: str):
            self.append_chunk(t)

        def on_result(_t: str):
            self.newline_output()

        self.injector.stream_with_callbacks(
            prompt, on_user=on_user, on_chunk=on_chunk, on_result=on_result
        )


def run_curses():
    curses.wrapper(lambda stdscr: CursesUI(stdscr).read_loop())


