"""REST API FOR posts."""
import flask
import insta485
from insta485.model import get_db
from insta485.api.errors import InvalidUsage, handle_invalid_usage


@insta485.app.route('/api/v1/p/', methods=["GET"])
def get_posts():
    """Get Top 10 posts."""
    if "username" not in flask.session:
        raise InvalidUsage("Forbidden", status_code=403)

    context = {}
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)

    logname = flask.session["username"]
    connection = get_db()
    cur = connection.execute(
        "SELECT DISTINCT posts.postid from posts"
        " LEFT JOIN following ON posts.owner = following.username2 "
        " WHERE following.username1 = ? OR posts.owner = ?"
        "ORDER BY posts.postid DESC "
        "LIMIT ? OFFSET ?",
        (logname, logname, size, page*size)
    )
    results = cur.fetchall()
    total = connection.execute(
        "SELECT DISTINCT posts.postid from posts"
        " LEFT JOIN following ON posts.owner = following.username2 "
        " WHERE following.username1 = ? OR posts.owner = ?",
        (logname, logname)).fetchall()

    for post in results:
        post["url"] = "/api/v1/p/" + str(post["postid"])
    context["url"] = flask.request.path
    next_page = page + 1
    if size * page + size < len(total):
        context["next"] = "/api/v1/p/?size={}&page={}".format(size, next_page)
    else:
        context["next"] = ""
    context["results"] = results
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/', methods=["GET"])
def get_post_metadata(postid_url_slug):
    """Get post metadata."""
    if "username" not in flask.session:
        raise InvalidUsage("Forbidden", status_code=403)

    context = {}
    postid = postid_url_slug

    # Check if postid is out of range
    cur = get_db().execute("SELECT COUNT(*) FROM posts WHERE 1=1")
    # It returns a list of strings so we need to chop it into a comparable num
    total_posts = int(str(cur.fetchall()[0])[13:-1])
    if postid > total_posts:
        raise InvalidUsage('Not Found', status_code=404)

    posts = get_db().execute(
        "SELECT posts.created as age, posts.filename as img_url, "
        " posts.owner as owner, users.filename as owner_img_url "
        " FROM posts "
        "LEFT JOIN users ON users.username = posts.owner "
        "WHERE postid = " + str(postid)
        ).fetchone()
    context = posts
    context["post_show_url"] = "/p/" + str(postid) + "/"
    context["img_url"] = "/uploads/" + context["img_url"]
    context["owner_img_url"] = "/uploads/" + context["owner_img_url"]
    context["owner_show_url"] = "/u/" + context["owner"] + "/"
    context["url"] = flask.request.path
    return flask.jsonify(**context)


@insta485.app.route('/api/v1', methods=["GET"])
def get_links():
    """Return links."""
    return flask.jsonify(**{"posts": "/api/v1/p/", "url": "/api/v1/"})
