"""
No database models are required.

Background removal happens entirely in the visitor's browser, so the server
never stores images, tasks, or history. Recent uploads and processing stats are
kept client-side in ``localStorage``. This module is intentionally left empty
and exists only to satisfy Django's app layout.
"""
