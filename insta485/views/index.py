"""
Insta485 index (main) view.

URLs include:
/
/u/<user_url_slug>/
/u/<user_url_slug>/followers/
/u/<user_url_slug>/following/
/p/<postid_slug>
/explore/
/accounts/login/
/accounts/create/
/accounts/delete/
/accounts/edit/
/accounts/password/
"""
import os
import shutil
import tempfile
import uuid
import hashlib
from operator import itemgetter
import flask
import arrow
import insta485
from insta485.model import get_db


def delete_post(delete_postid):
    """Delete a post."""
    sql_delete_post = "delete from posts where postid = \'"
    sql_delete_post += delete_postid + '\''
    get_db().cursor().execute(sql_delete_post)


def delete_comment(commentid):
    """Delete a comment."""
    sql_delete_comment = "delete from comments where commentid = "
    sql_delete_comment += commentid
    get_db().cursor().execute(sql_delete_comment)


def like_post(owner, post_id):
    """Like a post."""
    sql_insert_like = "insert into likes(owner,postid) values(\'"
    sql_insert_like += owner + "\',"
    sql_insert_like += post_id + ")"
    get_db().cursor().execute(sql_insert_like)


def add_comment(text, logname, postid):
    """Add a comment."""
    sql_insert_comment = "insert into comments(owner,"
    sql_insert_comment += "postid,text) values (\'" + logname
    sql_insert_comment += "\'," + postid + ",\'" + text + "\')"
    get_db().cursor().execute(sql_insert_comment)


def unlike_post(logname, postid):
    """Unlike a post."""
    sql_delete_like = "delete from likes where owner = \'"
    sql_delete_like += logname + "\' and postid = "
    sql_delete_like += postid
    get_db().cursor().execute(sql_delete_like)


@insta485.app.route('/p/<postid_slug>/', methods=['GET', 'POST'])
def show_post(postid_slug):
    """Display post detail page."""
    # check to see if user is logged in
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    # if user wants to delete the post or a comment
    context = {}
    if flask.request.method == 'POST':
        if 'delete' in flask.request.form:
            delete_post(flask.request.form['postid'])
            return flask.redirect('/')
        if 'uncomment' in flask.request.form:
            delete_comment(flask.request.form['commentid'])
        if 'like' in flask.request.form:
            like_post(flask.session['username'], postid_slug)
        elif 'unlike' in flask.request.form:
            unlike_post(flask.session['username'], postid_slug)
        if 'comment' in flask.request.form:
            add_comment(flask.request.form['text'],
                        flask.session['username'], postid_slug)

    sql_get_post = "select * from posts where postid = \'" + postid_slug + '\''
    correct_post = get_db().cursor().execute(sql_get_post).fetchall()

    if not correct_post:
        flask.redirect('/')

    correct_post = correct_post[0]

    context['logname'] = flask.session['username']
    context['img_url'] = correct_post['filename']
    print(arrow.get(correct_post['created']))
    context['timestamp'] = arrow.get(correct_post['created']).humanize()
    context['owner'] = correct_post['owner']
    context['postid'] = postid_slug

    # do i need to add logic for liking own post?
    get_likes = "select count (*) from likes where postid =" + str(postid_slug)
    context['likes'] = int(str(get_db().cursor().execute(get_likes)
                               .fetchall())[15:-2])
    does_like = "select count(*) from likes where owner = \'"
    does_like += flask.session['username'] + '\''
    does_like += " and postid = " + str(postid_slug)
    likes = get_db().cursor().execute(does_like).fetchall()
    likes = int(likes[0]['count(*)'])

    if likes != 0:
        context['logname_likes_post'] = False
    else:
        context['logname_likes_post'] = True

    # need owner image url
    get_post_owner = "select filename from users where username = \'"
    get_post_owner += correct_post['owner'] + '\''
    post_owner_img = get_db().cursor().execute(get_post_owner).fetchall()[0]
    context['owner_img_url'] = post_owner_img['filename']

    # need to get post comments
    get_comments = "select * from comments where postid = \'"
    get_comments += str(postid_slug) + '\''
    comments = get_db().cursor().execute(get_comments).fetchall()
    context['comments'] = comments

    return flask.render_template("post.html", **context)


@insta485.app.route('/explore/', methods=['GET', 'POST'])
def show_explore():
    """Display /explore route."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')
    # get all the users but the current one
    logname = flask.session['username']
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        sql_insert_follow = "insert into following(username1,username2) valu"
        sql_insert_follow += 'es(\'' + logname + "\', \'" + username + "\')"
        get_db().cursor().execute(sql_insert_follow)
    sql_get_users = "select * from users where username != \'"
    sql_get_users += flask.session['username'] + '\''
    users = get_db().cursor().execute(sql_get_users).fetchall()
    not_following = []
    # if logged in user is not following the user add to not_following list

    for user in users:
        sql_get_following = "select count(*) from following where username1 = "
        sql_get_following += '\'' + flask.session['username'] + "\' and "
        sql_get_following += 'username2 = \'' + user['username'] + '\''
        following = get_db().cursor().execute(sql_get_following).fetchall()
        count = int(following[0]['count(*)'])
        if count == 0:
            not_following.append(user)
    context = {'logname': flask.session['username'],
               'not_following': not_following}
    return flask.render_template("explore.html", **context)


@insta485.app.route('/', methods=['GET', 'POST'])
def show_index():
    """Display / route."""
    if 'username' in flask.session:
        logname = flask.session['username']
        if flask.request.method == 'POST':
            postid = flask.request.form['postid']
            if 'like' in flask.request.form:
                like_post(logname, postid)
            elif 'unlike' in flask.request.form:
                unlike_post(logname, postid)
            if 'comment' in flask.request.form:
                add_comment(flask.request.form['text'], logname, postid)

        get_query = "select * from posts where owner = \'"
        get_query += logname + "\'"
        posts = get_db().cursor().execute(get_query).fetchall()

        get_query = "select * from following where username1 = \'"
        get_query += flask.session['username'] + '\''
        following = get_db().cursor().execute(get_query).fetchall()
        # Looks at users followed by the logged in user and adds their posts
        for follow in following:
            get_query = "select * from posts where owner = \'"
            get_query += follow['username2'] + '\''
            post = get_db().cursor().execute(get_query).fetchall()
            posts += post
        # This loop adds the number of likes as an item in the dictionary
        # for each post in posts
        for post in posts:
            get_query = "select filename from users where username = \'"
            get_query += post['owner'] + '\''
            post_owner_img = get_db().cursor().execute(
                get_query).fetchall()[0]
            post['owner_img_url'] = post_owner_img['filename']

            get_query = "select * from comments where postid = \'"
            get_query += str(post['postid']) + '\''
            comments = get_db().cursor().execute(get_query).fetchall()
            post['comments'] = comments

            get_query = "select count (*) from likes where postid ="
            get_query += str(post["postid"])

            # if string is not shortened it prints out part of the query
            # We conver to int so that like v likes works correctly
            post['likes'] = int(str(get_db().cursor().execute(get_query)
                                    .fetchall())[15:-2])
            # get weather owner likes this post or not
            does_like = "select count(*) from likes where owner = \'"
            does_like += flask.session['username'] + '\''
            does_like += " and postid = " + str(post["postid"])
            likes = get_db().cursor().execute(does_like).fetchall()
            likes = int(likes[0]['count(*)'])
            if likes != 0:
                post['logname_likes_post'] = False
            else:
                post['logname_likes_post'] = True
            post['timestamp'] = arrow.get(post['created']).humanize()
        # sort by most recent
        posts.sort(key=itemgetter('created'), reverse=True)
        context = {'logname': flask.session['username'], 'posts': posts}
        return flask.render_template("index.html", **context)
    return flask.redirect('/accounts/login/')


def sha256sum(filename):
    """Return sha256 hash of file content, similar to UNIX sha256sum."""
    content = open(filename, 'rb').read()
    sha256_obj = hashlib.sha256(content)
    return sha256_obj.hexdigest()


@insta485.app.route('/accounts/create/', methods=['GET', 'POST'])
def show_create():
    """Display account creation page."""
    if 'username' in flask.session:
        return flask.redirect('/accounts/edit/')
    if flask.request.method == 'POST':
        # Save POST request's file object to a temp file
        dummy, temp_filename = tempfile.mkstemp()
        file = flask.request.files["file"]
        file.save(temp_filename)

        # Compute filename
        hash_txt = sha256sum(temp_filename)
        dummy, suffix = os.path.splitext(file.filename)
        hash_filename_basename = hash_txt + suffix
        hash_filename = os.path.join(
            insta485.app.config["UPLOAD_FOLDER"],
            hash_filename_basename
        )

        # Move temp file to permanent location
        shutil.move(temp_filename, hash_filename)
        insta485.app.logger.debug("Saved %s", hash_filename_basename)

        # need to get correct hash for password
        password = flask.request.form['password']
        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        create_account = "insert into users(username,fullname,email,filename,"
        create_account += "password) values(\'"
        create_account += flask.request.form['username'] + "\',\'"
        create_account += flask.request.form['fullname'] + "\',\'"
        create_account += flask.request.form['email'] + "\',\'"
        create_account += hash_filename_basename
        create_account += "\',\'" + password_db_string + "\')"
        get_db().cursor().execute(create_account)

        return flask.redirect(flask.url_for('show_index'))

    return flask.render_template('create.html')


@insta485.app.route('/accounts/logout/')
def logout():
    """Logout user."""
    flask.session.clear()
    return flask.redirect('/accounts/login/')


@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def show_login():
    """Display //accounts/login/ route."""
    if 'username' in flask.session:
        return flask.redirect('/')

    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']

        # need to verify the password ....
        get_password = "select password from users where username = \'"
        get_password += username + '\''
        hashed_password = get_db().cursor().execute(
            get_password).fetchone()['password'].split('$')
        hash_obj = hashlib.new(hashed_password[0])
        password_salted = hashed_password[1] + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()

        if password_hash != hashed_password[2]:
            flask.abort(403)

        flask.session['username'] = username
        return flask.redirect(flask.url_for('show_index'))

    return flask.render_template("login.html")


@insta485.app.route('/u/<user_url_slug>/', methods=['GET', 'POST'])
def show_userpage(user_url_slug):
    """Display /u/<user_url_slug>/."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')
    # logname = flask.session['username']
    if flask.request.method == 'POST':
        if 'unfollow' in flask.request.form:
            sql_query = "delete from following where username1 = \'"
            sql_query += flask.session['username'] + '\''
            sql_query += "and username2 = \'" + user_url_slug + "\'"
            print(sql_query)
            get_db().cursor().execute(sql_query)
        elif 'follow' in flask.request.form:
            # to do!! fix me!!!
            # need to insert correct timestamp!!
            sql_query = "INSERT INTO following(username1,username2) "
            sql_query += "VALUES(\'" + flask.session['username']
            sql_query += "\', \'" + user_url_slug
            sql_query += "\')"
            print(sql_query)
            get_db().cursor().execute(sql_query)
        elif 'create_post' in flask.request.form:
            # Save POST request's file object to a temp file
            dummy, temp_filename = tempfile.mkstemp()
            file = flask.request.files["file"]
            file.save(temp_filename)

            # Compute filename
            dummy, suffix = os.path.splitext(file.filename)
            hash_filename_basename = sha256sum(temp_filename) + suffix
            hash_filename = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                hash_filename_basename
            )
            # Move temp file to permanent location
            shutil.move(temp_filename, hash_filename)
            insta485.app.logger.debug("Saved %s", hash_filename_basename)

            sql_query = "INSERT INTO posts(filename,owner) VALUES(\'"
            sql_query += hash_filename_basename + "\', \'"
            sql_query += flask.session['username'] + "\')"
            get_db().cursor().execute(sql_query)

    # get fullname
    sql_query = "select * from users where username = \'" + user_url_slug
    sql_query += '\''
    name = get_db().cursor().execute(sql_query).fetchall()[0]['fullname']

    # get if logname follows username
    sql_query = "select count(*) from following where username1"
    sql_query += ' = \'' + flask.session['username'] + "\' and username2 = \'"
    sql_query += user_url_slug + '\''
    following = get_db().cursor().execute(sql_query).fetchall()
    logname_follows_username = True
    if int(following[0]['count(*)']) == 0:
        logname_follows_username = False

    # get all posts by user
    sql_query = "select * from posts where owner = \'" + user_url_slug + '\''
    posts = get_db().cursor().execute(sql_query).fetchall()
    total_posts = len(posts)

    # get total number of following
    sql_query = "select count(*) from following where username1 = \'"
    sql_query += user_url_slug + '\''
    following = get_db().cursor().execute(
        sql_query).fetchall()[0]['count(*)']
    # get total number of followers
    sql_query = "select count(*) from following where username2 = \'"
    sql_query += user_url_slug + '\''
    followers = get_db().cursor().execute(
        sql_query).fetchall()[0]['count(*)']

    context = {'logname': flask.session['username'], 'username': user_url_slug,
               'logname_follows_username': logname_follows_username,
               'posts': posts, 'total_posts': total_posts,
               'followers': followers, 'following': following,
               'fullname': name}

    return flask.render_template("user.html", **context)


@insta485.app.route('/u/<user_url_slug>/following/', methods=['GET', 'POST'])
def show_user_following(user_url_slug):
    """Display users following user_url_slug."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    logname = flask.session['username']
    if flask.request.method == 'POST':
        print(flask.request.form)
        username = flask.request.form['username']
        if 'follow' in flask.request.form:
            sql_insert_following = "insert into following(username1,username2)"
            sql_insert_following += " values(\'" + logname + "\',\'" + username
            sql_insert_following += "\')"
            get_db().cursor().execute(sql_insert_following)
        if 'unfollow' in flask.request.form:
            sql_delete_following = "delete from following where username1 = \'"
            sql_delete_following += logname + "\' and username2 = \'"
            sql_delete_following += username + "\'"
            get_db().cursor().execute(sql_delete_following)
    sql_get_following = "select * from following where username1 = \'"
    sql_get_following += user_url_slug + "\'"
    sql_get_users = "select * from users"
    users = get_db().cursor().execute(sql_get_users).fetchall()
    followers = get_db().cursor().execute(sql_get_following).fetchall()
    for follower in followers:
        sql_logname_follows = "select count(*) from following where username1 "
        sql_logname_follows += "= \'" + logname + '\'' + " and username2 = \'"
        sql_logname_follows += follower['username2'] + '\''
        follows = get_db().cursor().execute(sql_logname_follows).fetchall()
        if int(follows[0]['count(*)']) == 0:
            follower['logname_follows_username'] = False
        else:
            follower['logname_follows_username'] = True
    context = {'logname': flask.session['username'], 'following': followers,
               'user_slug': user_url_slug, 'users': users}
    return flask.render_template("following.html", **context)


@insta485.app.route('/u/<user_url_slug>/followers/', methods=['GET', 'POST'])
def show_user_followers(user_url_slug):
    """Display users that user_url_slug follows."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    logname = flask.session['username']
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        if 'follow' in flask.request.form:
            sql_insert_following = "insert into following(username1,username2)"
            sql_insert_following += " values(\'" + logname + "\',\'" + username
            sql_insert_following += "\')"
            get_db().cursor().execute(sql_insert_following)
        if 'unfollow' in flask.request.form:
            sql_delete_following = "delete from following where username1 = \'"
            sql_delete_following += logname + "\' and username2 = \'"
            sql_delete_following += username + "\'"
            get_db().cursor().execute(sql_delete_following)
    sql_get_following = "select * from following where username2 = \'"
    sql_get_following += user_url_slug + "\'"
    sql_get_users = "select * from users"
    followers = get_db().cursor().execute(sql_get_following).fetchall()
    for follower in followers:
        sql_logname_follows = "select count(*) from following where username1"
        sql_logname_follows += " = \'" + logname + '\'' + " and username2 = \'"
        sql_logname_follows += follower['username1'] + '\''
        follows = get_db().cursor().execute(sql_logname_follows).fetchall()
        if int(follows[0]['count(*)']) == 0:
            follower['logname_follows_username'] = False
        else:
            follower['logname_follows_username'] = True
    users = get_db().cursor().execute(sql_get_users).fetchall()
    context = {'logname': flask.session['username'],
               'followers': followers,
               'user_slug': user_url_slug, 'users': users}

    return flask.render_template("followers.html", **context)


@insta485.app.route('/accounts/edit/', methods=['GET', 'POST'])
def show_edit():
    """Display edit page."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    context = {}
    sql_profile_info = "select * from users where username = \'"
    sql_profile_info += flask.session['username'] + '\''
    profile_info = get_db().cursor().execute(sql_profile_info).fetchone()

    context['logname'] = flask.session['username']
    context['filename'] = profile_info['filename']
    context['fullname'] = profile_info['fullname']
    context['email'] = profile_info['email']

    if flask.request.method == 'POST':
        # NEED TO ADD LOGIC FOR IF NO FILE CHOSEN
        # Save POST request's file object to a temp file
        dummy, temp_filename = tempfile.mkstemp()
        new_file = ''
        if 'file' in flask.request.files:
            file = flask.request.files["file"]
            file.save(temp_filename)
            # Compute filename
            hash_txt = sha256sum(temp_filename)
            dummy, suffix = os.path.splitext(file.filename)
            hash_filename_basename = hash_txt + suffix
            hash_filename = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                hash_filename_basename
            )
            # Move temp file to permanent location
            shutil.move(temp_filename, hash_filename)
            insta485.app.logger.debug("Saved %s", hash_filename_basename)

            new_file = hash_filename_basename
            update_query = "update users set filename = \'" + new_file
            update_query += "\' where username = \'" + context['logname']
            update_query += "\'"
            get_db().cursor().execute(update_query)
        new_name = flask.request.form['fullname']
        new_email = flask.request.form['email']
        update_query = "update users set fullname = \'" + new_name
        update_query += "\' where username = \'" + context['logname'] + "\'"
        get_db().cursor().execute(update_query)
        update_query = "update users set email = \'" + new_email
        update_query += "\' where username = \'" + context['logname'] + "\'"
        get_db().cursor().execute(update_query)

        context['filename'] = new_file
        context['fullname'] = new_name
        context['email'] = new_email

        return flask.render_template("edit.html", **context)
    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/password/', methods=['GET', 'POST'])
def show_password():
    """Check password."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    if flask.request.method == 'POST':
        if 'update_password' in flask.request.form:

            old_password = flask.request.form['password']
            new_password1 = flask.request.form['new_password1']
            new_password2 = flask.request.form['new_password2']

            # check that old_password is correct
            get_password = "select password from users where username = \'"
            get_password += flask.session['username'] + '\''

            get_db().cursor().execute(get_password)
            hashed_password = get_db().cursor().fetchone()[
                'password'].split('$')

            hash_obj = hashlib.new(hashed_password[0])
            password_salted = hashed_password[1] + old_password
            hash_obj.update(password_salted.encode('utf-8'))
            password_hash = hash_obj.hexdigest()

            if password_hash != hashed_password[2]:
                flask.abort(403)

            if new_password1 != new_password2:
                flask.abort(401)

            # need to hash new_password and put into database
            algorithm = 'sha512'
            salt = uuid.uuid4().hex
            hash_obj = hashlib.new(algorithm)
            password_salted = salt + new_password1
            hash_obj.update(password_salted.encode('utf-8'))
            password_hash = hash_obj.hexdigest()
            password_db_string = "$".join([algorithm, salt, password_hash])

            update_query = "update users set password = \'"
            update_query += password_db_string + "\' where username = \'"
            update_query += flask.session['username'] + "\'"
            get_db().cursor().execute(update_query)

            return flask.redirect('/accounts/edit/')

    return flask.render_template("password.html")


@insta485.app.route('/accounts/delete/', methods=['GET', 'POST'])
def show_delete():
    """Delete page."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    context = {}
    context['logname'] = flask.session['username']

    if flask.request.method == 'POST':
        if 'delete' in flask.request.form:

            # first delete the profile piture
            delete_propic = "select filename from users where username = \'"
            delete_propic += context['logname'] + '\''
            propic_file = get_db().cursor().execute(
                delete_propic).fetchone()['filename']
            hash_filename = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                propic_file
            )
            os.remove(hash_filename)

            # then delete all the post pictuers
            delete_posts = "select filename from posts where owner = \'"
            delete_posts += context['logname'] + '\''
            post_files = [post['filename'] for post in get_db(
            ).cursor().execute(delete_posts).fetchall()]

            for post in post_files:
                hash_filename = os.path.join(
                    insta485.app.config["UPLOAD_FOLDER"],
                    post
                )
                os.remove(hash_filename)

            sql_delete_account = "delete from users where username = \'"
            sql_delete_account += context['logname'] + '\''
            get_db().cursor().execute(sql_delete_account)
            flask.session.clear()
            return flask.redirect('/accounts/create/')

    return flask.render_template("delete.html", **context)


@insta485.app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Return filename."""
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename)
