"""REST API for likes."""
import flask
import insta485


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/', methods=["GET"])
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

    return flask.jsonify(**context)

