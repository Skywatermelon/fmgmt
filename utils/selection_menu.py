import curses

class SelectionMenu:
    def __init__(self, items_dict, key_name="full name"):
        if key_name not in items_dict:
            raise ValueError(f"Key '{key_name}' not found in the provided dictionary.")
        self.items = items_dict[key_name]
        self.selected_items = set()
        self.highlighted_index = 0

    def display_menu(self, stdscr, multi_select=False):
        curses.curs_set(0)
        stdscr.clear()
        while True:
            stdscr.clear()
            self.print_menu(stdscr, multi_select)
            key = stdscr.getch()

            if key == curses.KEY_UP and self.highlighted_index > 0:
                self.highlighted_index -= 1
            elif key == curses.KEY_DOWN and self.highlighted_index < len(self.items) - 1:
                self.highlighted_index += 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                if not multi_select:
                    return { "selected": self.items[self.highlighted_index] }
            elif key == ord(' '):
                if multi_select:
                    current_item = self.items[self.highlighted_index]
                    if current_item in self.selected_items:
                        self.selected_items.remove(current_item)
                    else:
                        self.selected_items.add(current_item)
            elif key == 27:  # ESC key to exit
                break

            stdscr.refresh()

        return {"selected": list(self.selected_items)}

    def print_menu(self, stdscr, multi_select):
        for idx, item in enumerate(self.items):
            if idx == self.highlighted_index:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(idx, 0, f"> {item}")
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(idx, 0, f"  {item}")

        if multi_select:
            stdscr.addstr(len(self.items) + 2, 0, f"Selected: {', '.join(self.selected_items)}")
        stdscr.addstr(len(self.items) + 4, 0, "Press ENTER to confirm or ESC to exit.")