"""
eXuCoDeR Music Bot - Inline Query Handler
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

from pyrogram import types

from anony import app, yt


@app.on_inline_query()
async def inline_query(_, query: types.InlineQuery):
    """Handle inline queries for music search."""
    q = query.query.strip()
    if not q:
        return await query.answer(
            results=[],
            switch_pm_text="Search music...",
            switch_pm_parameter="help",
        )

    # Search YouTube
    results = []
    try:
        from py_yt import VideosSearch
        search = VideosSearch(q, limit=5)
        search_results = await search.next()

        if search_results and search_results.get("result"):
            for i, video in enumerate(search_results["result"][:5]):
                results.append(
                    types.InlineQueryResultArticle(
                        title=video.get("title", "Unknown"),
                        description=f"{video.get('duration', 'N/A')} | "
                                   f"{video.get('channel', {}).get('name', 'Unknown')}",
                        input_message_content=types.InputTextMessageContent(
                            message_text=f"/play {video.get('link', '')}"
                        ),
                        thumb_url=video.get("thumbnails", [{}])[-1].get("url", ""),
                        id=f"yt_{video.get('id', i)}",
                    )
                )
    except Exception:
        pass

    if not results:
        results.append(
            types.InlineQueryResultArticle(
                title="No results found",
                description="Try a different query",
                input_message_content=types.InputTextMessageContent(
                    message_text="No results found."
                ),
                id="no_results",
            )
        )

    await query.answer(results, cache_time=10)
