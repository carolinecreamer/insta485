"""REST API for likes."""
import flask
import insta485
from insta485.model import get_db


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/',
                    methods=["GET", "POST", "DELETE"])
def get_likes(postid_url_slug):
    """Return likes on postid.
    Example:
    {
      "logname_likes_this": 1,
      "likes_count": 3,
      "postid": 1,
      "url": "/api/v1/p/1/likes/"
    }
    """

    if "username" not in flask.session:
        flask.abort(403)

    # User
    logname = flask.session["username"]
    context = {}

    # url
    context["url"] = flask.request.path

    # Post
    postid = postid_url_slug
    context["postid"] = postid

    # Did this user like this post?
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT EXISTS( "
        "  SELECT 1 FROM likes "
        "    WHERE postid = ? "
        "    AND owner = ? "
        "    LIMIT 1"
        ") AS logname_likes_this ",
        (postid, logname)
    )
    logname_likes_this = cur.fetchone()
    context.update(logname_likes_this)

    # Likes
    cur = connection.execute(
        "SELECT COUNT(*) AS likes_count FROM likes WHERE postid = ? ",
        (postid,)
    )
    likes_count = cur.fetchone()
    context.update(likes_count)

    # Unlike post
    if flask.request.method == 'DELETE':
        if logname_likes_this['logname_likes_this'] == 1:
            sql_delete_like = "delete from likes where owner = \'"
            sql_delete_like += logname + "\' and postid = "
            sql_delete_like += str(postid)
            get_db().cursor().execute(sql_delete_like)
        return flask.jsonify(), 204

    # Add like
    if flask.request.method == 'POST':
        # Check if user already likes post
        # If so return 409 conflict
        if logname_likes_this['logname_likes_this'] == 1:
            return flask.jsonify({'logname': logname, 'message': "Conflict",
                                  'postid': postid, 'status_code': 409}), 409
        # Insert like into database
        sql_insert_like = "insert into likes(owner,postid) values(\'"
        sql_insert_like += logname + "\',"
        sql_insert_like += str(postid) + ")"
        get_db().cursor().execute(sql_insert_like)

        # If like was succesfully inserted and return 201 if it worked
        cur = connection.execute(
            "SELECT EXISTS( "
            "  SELECT 1 FROM likes "
            "    WHERE postid = ? "
            "    AND owner = ? "
            "    LIMIT 1"
            ") AS logname_likes_this ",
            (postid, logname)
        )
        logname_likes_this = cur.fetchone()
        # if(logname_likes_this):
        return 201
        # Otherwise return error
    return flask.jsonify(**context)
