from flask import render_template
from flask import request, redirect, url_for, session
from flask import Flask
from flask import current_app as app
from application.models import *
from application.database import db
from PIL import Image

app.secret_key = b'75346835168465124521'

#defining the path to the static folder
app_path = os.path.abspath(os.path.dirname(__file__))
path = app_path.replace(r'\application', '')
static_path = path + '\static'

@app.route('/', methods=['GET','POST'])
def login():
    #behaviour following submit - check password, user
    if request.method == 'POST':
        #parsing arguments and getting user
        user_name = request.form.get("USER_NAME")
        password = request.form.get("PASSWORD")
        user = db.session.query(USER).filter(USER.USER_NAME == user_name).first()

        #checking if user exists
        try: #if try works, such a user exists
            Donkey = user.USER_NAME
            del Donkey
        except:
            return render_template('login.html', message = 'Either you username is wrong, or no such user exists. Please try again')

        #checking password validity
        if user.PASSWORD == password:
            session['username'] = user_name
            return redirect(url_for('feed', USER_ID=user.USER_ID))
        else:
            return render_template('login.html', message = 'Either your password or your username is wrong. <br> Please try again')

        #just rendering it
    return render_template('login.html')


@app.route('/feed/<USER_ID>', methods = ['GET'])
def feed(USER_ID):
    #checking if logged in user is trying to access
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    #checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    #getting the list of users they follow
    followed = db.session.query(FOLLOWER_FOLLOWING).filter(FOLLOWER_FOLLOWING.FOLLOWER_ID == USER_ID).order_by(FOLLOWER_FOLLOWING.FOLLOWED_ID.desc()).all()

    # now query posts, don't bother with order yet
    posts = []
    for follow in followed:
        follow_post = POST.query.filter(POST.AUTHOR.any(USER_ID = follow.FOLLOWED_ID)).order_by(POST.POST_ID.desc())
        posts.append(follow_post)

    #return posts
    return render_template('feed.html', POSTS = posts, USER = user)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':

        #getting data from html form & database
        user_name = request.form.get('USER_NAME')
        password = request.form.get('PASSWORD')
        password_confirmation = request.form.get('PASSWORD_CONFIRMATION')
        all_users_sql = db.session.query(USER.USER_NAME).all()

        # checking username uniqueness
        # taking sql object and making it a list
        user_names_list = []
        for name in all_users_sql:
            user_names_list.append(name.USER_NAME)
        #actually checking lack of uniqueness
        if user_names_list.count(user_name) > 0:
            return render_template('signup.html', message = 'Pls select a unique username')

        #checking password match
        if password != password_confirmation:
            return render_template('signup.html', message = 'Pls type your password consistently')

        #adding the user to the database, opening their profile
        new_user = USER(USER_NAME=user_name, PASSWORD = password, POST_COUNT = 0, FOLLOWER_COUNT = 0)
        db.session.add(new_user)
        db.session.commit()

        #addition complete, setting them as the user & opening their profile
        user = db.session.query(USER).filter(USER.USER_NAME == user_name).first()
        new_user_id = user.USER_ID
        session['username'] = user.USER_NAME
        return redirect(url_for("profile", USER_ID = new_user_id, VIEWED_ID = new_user_id))

    return render_template('signup.html')

@app.route('/profile/<USER_ID>', methods = ['GET'])
def profile(USER_ID):
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')
    #getting the data needed for the profile - no. of followers, no. of following, no. of posts, no. of likes, no. of dislikes

    #finding no. of posts
    post_no = POST.query.filter(POST.AUTHOR.any(USER_ID = USER_ID)).count()

    #getting all posts
    posts = POST.query.filter(POST.AUTHOR.any(USER_NAME = user.USER_NAME)).all()

    #finding no. of followers
    follower_no = FOLLOWER_FOLLOWING.query.filter(FOLLOWER_FOLLOWING.FOLLOWED_ID == USER_ID).count()

    #finding no. of followed
    followed_no = FOLLOWER_FOLLOWING.query.filter(FOLLOWER_FOLLOWING.FOLLOWER_ID == USER_ID).count()

    return render_template('profile.html', POST_NO=post_no, FOLLOWER_NO=follower_no, FOLLOWED_NO=followed_no, USER = user, POSTS= posts)

@app.route('/profile_viewed/<USER_ID>/<VIEWED_ID>', methods = ['GET'])
def profile_viewed(USER_ID, VIEWED_ID):
    # getting user and viewed user
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    viewed = db.session.query(USER).filter(USER.USER_ID == VIEWED_ID).first()

        # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    # getting the data needed for the profile - no. of followers, no. of following, no. of posts, no. of likes, no. of dislikes

    # finding no. of posts
    post_no = POST.query.filter(POST.AUTHOR.any(USER_ID=VIEWED_ID)).count()

    # getting all posts
    posts = POST.query.filter(POST.AUTHOR.any(USER_ID=VIEWED_ID))

    # finding no. of followers
    follower_no = FOLLOWER_FOLLOWING.query.filter(FOLLOWER_FOLLOWING.FOLLOWED_ID == USER_ID).count()

    # finding no. of followed
    followed_no = FOLLOWER_FOLLOWING.query.filter(FOLLOWER_FOLLOWING.FOLLOWER_ID == USER_ID).count()

    return render_template('profile_viewed.html', POST_NO=post_no, FOLLOWER_NO=follower_no, FOLLOWED_NO=followed_no, USER=user, VIEWED= viewed, POSTS = posts)


@app.route('/search_users/<USER_ID>', methods = ['GET'])
def search_users(USER_ID):
    # checking if logged in user is trying to access
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    #quering database (easy peasy)
    all_users = db.session.query(USER).order_by(USER.USER_NAME).all()

    return render_template('search_users.html', ALL_USERS=all_users, USER =user)

@app.route('/post/<USER_ID>/<POST_ID>', methods = ['GET'])
def post(USER_ID, POST_ID):
    #standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    #getting the post, getting the comments, we already have the user
    post = POST.query.filter(POST.POST_ID == POST_ID).first()
    comments = db.session.query(COMMENTS).filter(COMMENTS.POST_ID == post.POST_ID)

    #checking if the author's viewing or a user's viewing
    author = db.session.query(USER).filter(POST_USER.POST_ID == post.POST_ID).filter(POST_USER.USER_ID == user.USER_ID).first()
    try:
        dummy = author.USER_NAME #if the try works it means the author's viewing his post
        del dummy
        return render_template('post_author.html', POST=post, COMMENTS=comments, USER=user)
    except : #if we hit the except clause it means viewer was not creator
        return redirect(url_for('post_viewed', USER_ID = USER_ID, POST_ID = POST_ID))

@app.route('/post_viewed/<USER_ID>/<POST_ID>')
def post_viewed(USER_ID, POST_ID):
    #standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')
        # later this'll redirect to the you are not logged in html page which will have a url to the login page

    #getting the post, getting the comments, we already have the user
    post = POST.query.filter(POST.POST_ID == POST_ID).first()
    comments = db.session.query(COMMENTS).filter(COMMENTS.POST_ID == post.POST_ID)
    viewed = [author for author in post.AUTHOR]
    #getting the author

    return render_template('post_viewed.html', USER = user, POST = post, COMMENTS = comments, VIEWED =viewed)



@app.route('/create_post/<USER_ID>', methods = ['GET', 'POST'])
def create_post(USER_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    if request.method == 'POST':
        #parsing arguments
        post_title = request.form.get("POST_TITLE")
        post_content = request.form.get("POST_CONTENT")

        #adding post
        #getting latest post_id
        latest_post = db.session.query(sqlite_sequence).filter(sqlite_sequence.name == 'POST').first()
        post_id = int(latest_post.seq) + 1

        #adding new post to posts table
        new_post = POST(POST_ID = post_id, POST_TITLE = post_title, POST_CONTENT = post_content, POST_LIKES = 0, POST_DISLIKES = 0)
        db.session.add(new_post)

        #assembling and adding new post_user entry
        post_user = POST_USER(POST_ID = post_id, USER_ID=user.USER_ID)
        db.session.add(post_user)

        #updating user's post count
        user.POST_COUNT += 1
        db.session.add(user)

        #image block
        try:
            post_image = request.files['POST_IMAGE']
            # processing image
            img = Image.open(post_image)
            #saving the image
            img.save(f"{static_path}\POST_IMAGE{post_id}.png")
        except:
            pass

        db.session.commit()
        return redirect(url_for('all_posts',USER_ID = user.USER_ID))
    #end of all that
    return render_template('create_post.html', USER = user)

@app.route('/edit_post/<USER_ID>/<POST_ID>', methods = ['GET', 'POST'])
def edit_post(USER_ID, POST_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    # getting the old post
    post = db.session.query(POST).filter(POST.POST_ID == POST_ID).first()

   #getting the new data and updating the post
    if request.method == 'POST':
        #parsing arguments
        post_title = request.form.get("POST_TITLE")
        post_content = request.form.get("POST_CONTENT")

        #modifying og post
        post.POST_TITLE = post_title
        post.POST_CONTENT = post_content

        #updating db
        db.session.add(post)

        #updating the image
        try:
            post_image = request.files['POST_IMAGE']
            # processing image
            img = Image.open(post_image)
            # saving the image
            img.save(f"{static_path}\POST_IMAGE{post.POST_ID}.png")
        except:
            pass
        db.session.commit()
        return redirect(url_for('post', USER_ID = USER_ID, POST_ID=POST_ID))

    #rendering template with all the data
    return render_template('edit_post.html', POST= post, USER = user)

@app.route('/all_posts/<USER_ID>')
def all_posts(USER_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    #GETTING THEIR POSTS
    posts = POST.query.filter(POST.AUTHOR.any(USER_NAME = user.USER_NAME)).all()

    return render_template('all_posts.html', POSTS = posts, USER = user)

@app.route('/delete_post/<USER_ID>/<POST_ID>', methods = ['GET', 'POST'])
def delete_post(USER_ID,POST_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    # getting the post
    post = db.session.query(POST).filter(POST.POST_ID == POST_ID).first()

    # getting the post_user
    post_user = db.session.query(POST_USER).filter(POST_USER.POST_ID == POST_ID).filter(POST_USER.USER_ID == USER_ID).first()

    #forbidding someone from deleting another's post
    try:
        user_id = post_user.USER_ID
        del user_id
    except:
        return render_template('misc_error.html', USER = user)

    # getting the like_dislikes of that post
    like_dislikes = db.session.query(LIKE_DISLIKE).filter(LIKE_DISLIKE.POST_ID==post.POST_ID).all()

    #getting the comments of that post
    comments = db.session.query(COMMENTS).filter(COMMENTS.POST_ID == post.POST_ID).all()

    if request.method == 'POST':
        #GETTING WHAT THEY SAID
        radio = request.form.get("CONFIRMATION")
        if radio == "Y":
            #changing post count
            user.POST_COUNT -= 1
            db.session.add(user)

            #deleting like_dislike
            for like_dislike in like_dislikes:
                db.session.delete(like_dislike)

            #deleting comments
            for comment in comments:
                db.session.delete(comment)

            #deleting post_user
            db.session.delete(post_user)

            # deleting post
            db.session.delete(post)

            # deleting image from static
            try:
                os.remove(f"{static_path}\POST_IMAGE{post.POST_ID}.png")
            except:
                pass

            db.session.commit()
        return redirect(url_for('all_posts', USER_ID = USER_ID))

    return render_template('delete_post.html',POST=post, USER=user)


@app.route('/all_posts_viewed/<USER_ID>/<VIEWED_ID>')
def all_posts_viewed(USER_ID, VIEWED_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    viewed = db.session.query(USER).filter(USER.USER_ID == VIEWED_ID).first()
    # GETTING THEIR POSTS
    posts = POST.query.filter(POST.AUTHOR.any(USER_NAME=viewed.USER_NAME)).all()

    return render_template('all_posts_viewed.html', POSTS=posts, USER=user,VIEWED=viewed)

@app.route('/followers/<USER_ID>', methods = ['GET'])
def followers(USER_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')
    
    # rudimentary form of querying
    # first get follower's ids
    follower_ids = FOLLOWER_FOLLOWING.query.filter(FOLLOWER_FOLLOWING.FOLLOWED_ID == user.USER_ID).all()
    # put em in a list
    followers = []
    for follower in follower_ids:
        userx = db.session.query(USER).filter(USER.USER_ID == follower.FOLLOWER_ID).first()
        followers.append(userx)

    return render_template('followers.html', FOLLOWERS = followers, USER=user)

@app.route('/followed/<USER_ID>')
def followed(USER_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

# rudimentary form of querying
    # first get follower's ids
    followed_ids = FOLLOWER_FOLLOWING.query.filter(FOLLOWER_FOLLOWING.FOLLOWER_ID == user.USER_ID).all()

    # getting data for all the users who follow & putting those users in a list
    followed = []
    for followed_single in followed_ids:
        userx = db.session.query(USER).filter(USER.USER_ID == followed_single.FOLLOWED_ID).first()
        followed.append(userx)

    return render_template('followed.html', FOLLOWED=followed, USER=user)

@app.route('/change_followers/<USER_ID>/<VIEWED_ID>', methods = ['GET', 'POST'])
def change_followers(USER_ID, VIEWED_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    #getting the viewed relation
    viewed = db.session.query(USER).filter(USER.USER_ID == VIEWED_ID).first()

    #checking if they're trying to follow themselves
    if user.USER_ID == viewed.USER_ID:
        return render_template('misc_error.html',USER = user)

    #getting existing relns between the 2
    follower = db.session.query(FOLLOWER_FOLLOWING).filter(FOLLOWER_FOLLOWING.FOLLOWER_ID == USER_ID).filter(FOLLOWER_FOLLOWING.FOLLOWED_ID == VIEWED_ID)
    followed = db.session.query(FOLLOWER_FOLLOWING).filter(FOLLOWER_FOLLOWING.FOLLOWER_ID == VIEWED_ID).filter(FOLLOWER_FOLLOWING.FOLLOWED_ID == USER_ID)

    if request.method == 'POST':
        #code to follow
        if request.form.get('FOLLOW') == 'Y':
            #updating follower_following
            user_follow_view = FOLLOWER_FOLLOWING(FOLLOWER_ID = user.USER_ID, FOLLOWED_ID = viewed.USER_ID)
            db.session.add(user_follow_view)
            #updating viewed follower count
            viewed.FOLLOWER_COUNT += 1
            db.session.add(viewed)
        #code to unfollow
        if request.form.get('UNFOLLOW') == 'Y':
            #updating follower_following
            user_unfollow_view = db.session.query(FOLLOWER_FOLLOWING).filter(FOLLOWER_FOLLOWING.FOLLOWER_ID == USER_ID).filter(FOLLOWER_FOLLOWING.FOLLOWED_ID == VIEWED_ID).first()
            db.session.delete(user_unfollow_view)
            #updating viewed
            viewed.FOLLOWER_COUNT -= 1
        #code to block
        if request.form.get('BLOCK') == 'Y':
            #removing view as user's follower
            user_block_view = db.session.query(FOLLOWER_FOLLOWING).filter(FOLLOWER_FOLLOWING.FOLLOWER_ID == VIEWED_ID).filter(FOLLOWER_FOLLOWING.FOLLOWED_ID == USER_ID).first()
            db.session.delete(user_block_view)
            #reducing user's follower count
            user.FOLLOWER_COUNT -= 1
            db.session.commit()
            return redirect(url_for('followers', USER_ID = user.USER_ID))
        db.session.commit()
        return redirect(url_for('followed', USER_ID = user.USER_ID))

    return render_template('change_followers.html', USER = user, VIEWED = viewed, FOLLOWER = follower, FOLLOWED = followed)

@app.route('/post_like/<USER_ID>/<POST_ID>')
def post_like(USER_ID, POST_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    #getting the post
    post = db.session.query(POST).filter(POST.POST_ID == POST_ID).first()

    # checking if you've already liked/disliked it
    like_dislike_check = db.session.query(LIKE_DISLIKE).filter(LIKE_DISLIKE.USER_ID == user.USER_ID).filter(LIKE_DISLIKE.POST_ID == post.POST_ID).all()
    if len(like_dislike_check) > 0:
        like_dislike_single = like_dislike_check[0]
        if like_dislike_single.LIKE_DISLIKE == 1: #if you already liked it, cant do it again
            return render_template('already_liked_disliked.html', LIKE_DISLIKE=like_dislike_single, POST=post, USER=user)
        post.POST_DISLIKES -= 1 #if you disliked it, let's undo that
        db.session.delete(like_dislike_single)

    #  upping the post's  likes
    post.POST_LIKES += 1

    #updating like_dislike table
    like_dislike = LIKE_DISLIKE(POST_ID=post.POST_ID, USER_ID=user.USER_ID, LIKE_DISLIKE=1)

    #updating databases
    db.session.add(post)
    db.session.add(like_dislike)
    db.session.commit()
    return redirect(url_for('post_viewed', USER_ID=user.USER_ID, POST_ID=post.POST_ID))


@app.route('/post_dislike/<USER_ID>/<POST_ID>')
def post_dislike(USER_ID, POST_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    # retreiving the post, upping its dislikes
    post = db.session.query(POST).filter(POST.POST_ID == POST_ID).first()


    # checking if you've already liked/disliked it
    like_dislike_check = db.session.query(LIKE_DISLIKE).filter(LIKE_DISLIKE.USER_ID == user.USER_ID).filter(
        LIKE_DISLIKE.POST_ID == post.POST_ID).all()
    if len(like_dislike_check) > 0:
        like_dislike_single = like_dislike_check[0]
        if like_dislike_single.LIKE_DISLIKE == 0:  # if you already disliked it, cant do it again
            return render_template('already_liked_disliked.html', LIKE_DISLIKE=like_dislike_single, POST=post, USER=user)
        post.POST_LIKES -= 1  # if you liked it, let's undo that
        db.session.delete(like_dislike_single)

    #retreiving the table, upping its dislikes
    post.POST_DISLIKES += 1

    # updating like_dislike table
    like_dislike = LIKE_DISLIKE(POST_ID=post.POST_ID, USER_ID=user.USER_ID, LIKE_DISLIKE=0)

    # updating databases
    db.session.add(post)
    db.session.add(like_dislike)
    db.session.commit()
    return redirect(url_for('post_viewed', USER_ID=user.USER_ID, POST_ID=post.POST_ID))

@app.route('/add_comment/<USER_ID>/<POST_ID>', methods = ['GET', 'POST'])
def add_comment(USER_ID, POST_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    #getting the post
    post = db.session.query(POST).filter(POST.POST_ID == POST_ID).first()

    if request.method == 'POST':
        #making the comment
        comment_content = request.form.get('COMMENT_CONTENT')
        comments = COMMENTS(COMMENT_CONTENT = comment_content, POST_ID =post.POST_ID, USER_NAME = user.USER_NAME)

        #putting the comment in a database
        db.session.add(comments)
        db.session.commit()

        #final redicrect
        return redirect(url_for('post', USER_ID = user.USER_ID, POST_ID = post.POST_ID))
    return render_template('add_comment.html',USER=user,POST =post)

@app.route('/delete_comment/<USER_ID>/<POST_ID>/<COMMENT_ID>')
def delete_comment(USER_ID, POST_ID, COMMENT_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    # getting the post
    post = db.session.query(POST).filter(POST.POST_ID == POST_ID).first()

    #getting the comment
    comments = db.session.query(COMMENTS).filter(COMMENTS.COMMENT_ID == COMMENT_ID).first()

    #nuking it
    db.session.delete(comments)
    db.session.commit()

    #redirect
    return redirect(url_for('post', USER_ID=user.USER_ID, POST_ID=post.POST_ID))

@app.route('/logout/<USER_ID>', methods = ['GET','POST'])
def logout(USER_ID):
    # standard logged in or not check
    user = db.session.query(USER).filter(USER.USER_ID == USER_ID).first()
    # checking if user exists
    try:
        name = user.USER_NAME
        del name
    except:
        return render_template('not_logged_in.html')
    # checking if they're logged in
    if session['username'] != user.USER_NAME:
        return render_template('not_logged_in.html')

    if request.method == 'POST':
        session['username'] = ''
        return redirect(url_for('login'))

    #load the form
    return render_template('logout.html', USER = user)