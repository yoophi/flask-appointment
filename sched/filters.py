def do_datetime(dt, format=None):
    if dt is None:
        return ''
    if format is None:
        # 1. Left-strip leading 0 in hour display
        # 2. Use 'am'/'pm' (lower case) instead of 'AM'/'PM'
        formatted_date = dt.strftime('%Y-%m-%d - %A')
        formatted_time = dt.strftime('%I:%M%p').lstrip('0').lower()
        formatted = '%s at %s' % (formatted_date, formatted_time)
    else:
        formatted = dt.strftime(format)
    return formatted

def init_app(app):
    app.jinja_env.filters['datetime'] = do_datetime