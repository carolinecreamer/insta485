"""REST API for comments."""
import flask
import insta485
from insta485.api.errors import InvalidUsage, handle_invalid_usage


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/comments/',
                    methods=["GET", "POST"])
def get_comments(postid_url_slug):
    """Return comments for post."""
    if "username" not in flask.session:
        raise InvalidUsage("Forbidden", status_code=403)

    logname = flask.session["username"]
    connection = insta485.model.get_db()

    if flask.request.method == 'POST':
        post_text = flask.json.loads(flask.request.data)['text']
        sql_query = "insert into comments(owner,postid,text) values(\'"
        sql_query += logname + "\',"
        sql_query += str(postid_url_slug) + ", \'"
        sql_query += post_text + "\')"
        cur = connection.execute(sql_query)

        sql_query = "select commentid, owner, owner as owner_show_url, {0} as postid, text from comments where rowid = last_insert_rowid()".format(postid_url_slug)
        cur = connection.execute(sql_query)
        comment = cur.fetchone()
        comment['owner_show_url'] = '/u/' + comment['owner_show_url'] + '/'
        return flask.jsonify(**comment), 201

    context = {}
    context["url"] = flask.request.path
    sql_query = "select commentid, owner, owner as owner_show_url, {0} as postid, text from comments where postid = {0}".format(postid_url_slug)
    cur = connection.execute(sql_query)
    comments = cur.fetchall()
    for c in comments:
        c['owner_show_url'] = '/u/' + c['owner_show_url'] + '/'
    context["comments"] = comments

    return flask.jsonify(**context)
