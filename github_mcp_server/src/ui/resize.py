from __future__ import annotations

import asyncio


async def run_resize_watcher(app, on_first_loop, on_resize):
    """Асинхронный вотчер ресайза: один раз инициализирует и вызывает on_resize по изменению размеров."""
    # capture initial size
    s = app.output.get_size()
    last_cols, last_rows = s.columns, s.rows
    if on_first_loop:
        on_first_loop(last_cols, last_rows)
    while True:
        await asyncio.sleep(0.2)
        size = app.output.get_size()
        if size.columns != last_cols or size.rows != last_rows:
            last_cols, last_rows = size.columns, size.rows
            on_resize(last_cols, last_rows)


__all__ = ["run_resize_watcher"]


