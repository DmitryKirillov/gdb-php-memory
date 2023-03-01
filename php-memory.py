class PhpMemoryPage:

    def __init__(self, page_type, has_changed, is_highlighted):
        self.page_type = page_type
        self.has_changed = has_changed
        self.is_highlighted = is_highlighted


class PhpMemoryWindow:
    PAGE_FREE = 0
    PAGE_INIT = 1
    PAGE_SMALL = 2
    PAGE_LARGE = 4

    # See zend_alloc.c
    ZEND_MM_IS_LRUN = 0x40000000
    ZEND_MM_IS_SRUN = 0x80000000
    ZEND_MM_LRUN_PAGES_MASK = 0x000003ff
    ZEND_MM_SRUN_BIN_NUM_MASK = 0x0000001f

    # See zend_alloc_sizes.h
    PAGES_PER_BIN = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 3, 1, 1, 5, 3, 2, 2, 5, 3, 7, 4, 5, 3]

    def __init__(self, tui_window):
        self._chunk_map = [0] * 512
        self._chunk_free_map = [0] * 8
        self._memory_map = [None] * 512
        for i in range(512):
            self._memory_map[i] = PhpMemoryPage(self.PAGE_FREE, False, False)
        self._memory_map[0] = PhpMemoryPage(self.PAGE_INIT, False, False)

        self._tui_window = tui_window
        self._tui_window.title = 'PHP Memory Map'

        self._update_map()
        self._render()

        self._before_prompt_listener = lambda: self._before_prompt()
        gdb.events.before_prompt.connect(self._before_prompt_listener)

    def _before_prompt(self):
        self._update_map()
        self._render()

    def _update_map(self):
        if (not self._is_program_running()):
            return

        heap = gdb.parse_and_eval("zend_mm_get_heap()")
        chunk = heap['main_chunk']

        for i in range(512):
            self._chunk_map[i] = int(chunk['map'][i])
        for i in range(8):
            self._chunk_free_map[i] = int(chunk['free_map'][i])

        self._memory_map_has_changed = False
        i = 1  # We always start at index 1 (page 0 contains chunk metadata)
        while (i < 512):
            page = self._chunk_map[i]
            count = 1
            if (page == 0):  # ZEND_MM_IS_FRUN
                self._update_pages(i, count, self.PAGE_FREE)
            elif ((page & self.ZEND_MM_IS_LRUN) and (page & self.ZEND_MM_IS_SRUN)):  # ZEND_MM_IS_NRUN
                # todo Consider using a dedicated page type
                bin_num = page & self.ZEND_MM_SRUN_BIN_NUM_MASK
                count = self.PAGES_PER_BIN[bin_num]
                self._update_pages(i, count, self.PAGE_SMALL)
            elif (page & self.ZEND_MM_IS_SRUN):  # ZEND_MM_IS_SRUN
                self._update_pages(i, count, self.PAGE_SMALL)
            elif (page & self.ZEND_MM_IS_LRUN):  # ZEND_MM_IS_LRUN
                count = (page & self.ZEND_MM_LRUN_PAGES_MASK)
                self._update_pages(i, count, self.PAGE_LARGE)
            i += count

        if (self._memory_map_has_changed):
            for current_page in self._memory_map:
                current_page.is_highlighted = current_page.has_changed

    def _update_pages(self, i, count, page_type):
        max_i = i + count
        while (i < max_i):
            # PHP sometimes reports small pages that are not listed
            # in the heap->free_map.
            # We ignore these pages for now.
            current_page_type = page_type
            free_map_i = i // 64
            free_map_j = i % 64
            free_map_segment = self._chunk_free_map[free_map_i]
            bit_is_set = free_map_segment & (1 << free_map_j)
            if ((not bit_is_set) and (page_type != self.PAGE_FREE)):
                current_page_type = self.PAGE_FREE
            # todo Investigate this bug
            elif (bit_is_set and (page_type == self.PAGE_FREE)):
                current_page_type = self.PAGE_LARGE

            current_page = self._memory_map[i]
            if (current_page.page_type != current_page_type):
                self._memory_map_has_changed = True
                current_page.page_type = current_page_type
                current_page.has_changed = True
            else:
                current_page.has_changed = False
            i += 1

    def _render(self):
        self._tui_window.erase()

        if (not self._is_program_running()):
            self._tui_window.write('The program is not being run.')
            return

        for i in range(8):
            s = ''
            for j in range(64):
                ch = ''
                current_page = self._memory_map[i * 64 + j]
                if (current_page.page_type == self.PAGE_FREE):
                    if (current_page.is_highlighted):
                        ch += '\x1b[33;m'
                    ch += '░'
                    if (current_page.is_highlighted):
                        ch += '\x1b[m'
                elif (current_page.page_type == self.PAGE_INIT):
                    ch += '◙'
                elif (current_page.page_type == self.PAGE_SMALL):
                    if (current_page.is_highlighted):
                        ch += '\x1b[33;m'
                    else:
                        ch += '\x1b[37;m'
                    ch += '◘'
                    ch += '\x1b[m'
                elif (current_page.page_type == self.PAGE_LARGE):
                    if (current_page.is_highlighted):
                        ch += '\x1b[93;1m'
                    else:
                        ch += '\x1b[37;1m'
                    ch += '◘'
                    ch += '\x1b[m'
                s += ch
            s += '\n'
            self._tui_window.write(s)

    def _is_program_running(self):
        return len(gdb.selected_inferior().threads()) and gdb.selected_inferior().threads()[0].is_valid()

    def close(self):
        gdb.events.before_prompt.disconnect(self._before_prompt_listener)


gdb.register_window_type('php_memory', PhpMemoryWindow)

gdb.execute('tui new-layout php_memory php_memory 1 cmd 1 status 0')
