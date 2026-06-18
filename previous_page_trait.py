from flask import session, request


def init_app(app):
    """Register a before_request hook to track current and previous pages.

    Usage: call `init_app(app)` after creating your Flask `app` object.
    It stores `session['current_page']` and `session['previous_page']`.
    """

    @app.before_request
    def _track_pages():
        try:
            # Only track GET requests (avoid storing form posts, API calls, etc.)
            if request.method != 'GET':
                return

            # Don't track static assets or missing endpoints
            endpoint = request.endpoint
            if not endpoint or endpoint == 'static':
                return

            # Move current -> previous, then set new current
            current = session.get('current_page')
            if current:
                session['previous_page'] = current
            session['current_page'] = request.path
        except RuntimeError:
            # If called outside request context, ignore
            return


def get_previous(default='/'):
    """Return the previously visited path, falling back to `default`.

    This reads from `session['previous_page']` if available.
    """
    return session.get('previous_page') or default
