from flask import Flask, render_template, request
from build_all_tables import FilesDropped, db_session
from datetime import timedelta
from sqlalchemy import *
from config import AUTO_ARCHIVE_MIN_DURATION
app = Flask(__name__)


'''Web app returns a web page with assets according to filter criteria'''


def query_filter(state):
    if state['type'] == 'Archived':  # get archived assets
        db_result = db_session.query(FilesDropped).filter(
            FilesDropped.date_archived.isnot(None),
            FilesDropped.date_removed.is_(None),
            FilesDropped.duration >= AUTO_ARCHIVE_MIN_DURATION.total_seconds(),  # only list things this service handles
            or_(FilesDropped.display_name.contains(state['text']),  # are they looking for something specific?
                FilesDropped.mob_id.contains(state['text']),
                FilesDropped.file_path.contains(state['text'])))
    elif request.form['state'] == 'Dropped':  # the system is aware of the asset but has taken no action
        db_result = db_session.query(FilesDropped).filter(
            FilesDropped.date_archived.isnot(None),
            FilesDropped.date_removed.is_(None),
            FilesDropped.duration >= AUTO_ARCHIVE_MIN_DURATION.total_seconds(),
            or_(FilesDropped.display_name.contains(state['text']),
                FilesDropped.mob_id.contains(state['text']),
                FilesDropped.file_path.contains(state['text'])))
    else:  # blank or unknown category just sort by length and search term
        db_result = db_session.query(FilesDropped).filter(
            FilesDropped.date_removed.isnot(None),
            FilesDropped.duration >= AUTO_ARCHIVE_MIN_DURATION.total_seconds(),
            or_(FilesDropped.display_name.contains(state['text']),
                FilesDropped.mob_id.contains(state['text']),
                FilesDropped.file_path.contains(state['text'])))

    if state['column'] == 'MOB ID':
        if state['order'] == 'A':
            db_result = db_result.order_by(FilesDropped.mob_id)
        else:
            db_result = db_result.order_by(FilesDropped.mob_id.desc())
    elif state['column'] == 'Display Name':
        if state['order'] == 'A':
            db_result = db_result.order_by(FilesDropped.display_name)
        else:
            db_result = db_result.order_by(FilesDropped.display_name.desc())
    elif state['column'] == 'Duration':
        if state['order'] == 'A':
            db_result = db_result.order_by(FilesDropped.duration)
        else:
            db_result = db_result.order_by(FilesDropped.duration.desc())
    elif state['column'] == 'Creation Date':
        if state['order'] == 'A':
            db_result = db_result.order_by(FilesDropped.date_created)
        else:
            db_result = db_result.order_by(FilesDropped.date_created.desc())
    elif state['column'] == 'Modified Date':
        if state['order'] == 'A':
            db_result = db_result.order_by(FilesDropped.date_modified)
        else:
            db_result = db_result.order_by(FilesDropped.date_modified.desc())
    elif state['column'] == 'Archived Date':
        if state['order'] == 'A':
            db_result = db_result.order_by(FilesDropped.date_archived)
        else:
            db_result = db_result.order_by(FilesDropped.date_archived.desc())
    else:
        if state['order'] == 'A':
            db_result = db_result.order_by(FilesDropped.date_removed)
        else:
            db_result = db_result.order_by(FilesDropped.date_removed.desc())

    return db_result.limit(state['limit']).all()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        state = {
            'type': 'Archived',
            'column': 'MOB ID',
            'order': 'A',
            'text': '',
            'limit': 100
        }

    else:
        state = {
            'type': request.form['state'],
            'column': request.form['sort_col'],
            'order': request.form['sort_order'],
            'text': request.form['search_request'],
            'limit': int(request.form['query_limit'])
        }

    db_result = query_filter(state)

    results = []
    for result in db_result:  # make a list for the template
        results.append(
            {
                'MOB ID': result.mob_id,
                'Duration': timedelta(seconds=result.duration),  # make this some sort of human readable format
                'Display Name': result.display_name,
                'Creation Date': result.date_created,
                'Modified Date': result.date_modified,
                'Archived Date': result.date_archived,
                'Removed Date': result.date_removed
            }
        )
    return render_template('home.html', assets=results, nav_state=state)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
