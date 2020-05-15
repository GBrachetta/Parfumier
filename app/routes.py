import os
import logging
from flask import render_template, redirect, flash, url_for, request
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, mongo
from app.models import User
from app.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    RequestResetForm,
    ResetPasswordForm,
    CreatePerfumeForm,
    CreateTypeForm,
    EditTypeForm,
    EditPerfumeForm,
    AddReviewForm,
)
from app.utils import save_avatar, send_reset_email, save_picture
from datetime import datetime
from bson.objectid import ObjectId

logging.basicConfig(
    level=logging.DEBUG,
    filename="app.log",
    filemode="w",
    format="%(asctime)s %(name)s - %(filename)s :: %(lineno)d - %(levelname)s - %(message)s\n",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@app.route("/")
def index():
    """
    DESCRIPTION
    """
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and User.check_password(user["password"], form.password.data):
            user_obj = User(
                user["username"],
                user["first_name"],
                user["last_name"],
                user["email"],
                user["_id"],
                user["is_admin"],
                user["avatar"],
            )
            login_user(user_obj, remember=form.remember.data)
            next_page = request.args.get("next")
            flash("You have logged in!", "info")
            return (
                redirect(next_page) if next_page else redirect(url_for("index"))
            )
        else:
            flash("Please check your credentials", "warning")
    return render_template("login.html", title="Login", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    users = mongo.db.users
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        users.insert(
            {
                "username": form.username.data,
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data,
                "password": hashed_password,
                "is_admin": False,
                "avatar": "default.png",
            }
        )
        user = mongo.db.users.find_one({"email": form.email.data})
        user_obj = User(
            user["username"],
            user["first_name"],
            user["last_name"],
            user["email"],
            user["_id"],
            user["is_admin"],
            user["avatar"],
        )
        login_user(user_obj)
        flash(
            f"Account created for {form.username.data}. You are now logged in.",
            "info",
        )
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    """
    DESCRIPTION
    """
    form = UpdateAccountForm()
    updated_user = {
        "username": form.username.data,
        "first_name": form.first_name.data,
        "last_name": form.last_name.data,
        "email": form.email.data,
    }
    if form.validate_on_submit():
        if form.avatar.data:
            avatar = save_avatar(form.avatar.data)
            old_value = mongo.db.users.find_one(
                {"username": current_user.username}
            )
            avatar = {"$set": {"avatar": avatar}}
            mongo.db.users.update_one(old_value, avatar)
            if current_user.avatar != "default.png":
                os.remove(
                    os.path.join(
                        app.root_path,
                        "static/images/avatars",
                        current_user.avatar,
                    )
                )
        mongo.db.users.update_one(
            {"username": current_user.username}, {"$set": updated_user}
        )
        user = mongo.db.users.find_one({"email": form.email.data})
        user_obj = User(
            user["username"],
            user["first_name"],
            user["last_name"],
            user["email"],
            user["_id"],
            user["is_admin"],
            user["avatar"],
        )
        login_user(user_obj)
        flash("You have updated your information", "info")
        return redirect(url_for("index"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.avatar.data = current_user.avatar
    avatar = url_for("static", filename=f"images/avatars/{current_user.avatar}")
    return render_template(
        "account.html", title="Account", form=form, avatar=avatar
    )


@app.route("/logout")
@login_required
def logout():
    """
    DESCRIPTION
    """
    logout_user()
    flash("We hope to see you back soon again!", "warning")
    return redirect(url_for("index"))


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        send_reset_email(user)
        flash("An email has been sent to reset your password", "success")
        return redirect(url_for("login"))
    return render_template(
        "reset_request.html", title="Reset Password", form=form
    )


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        mongo.db.users.update_one(
            {"email": user["email"]}, {"$set": {"password": hashed_password}}
        )
        user = mongo.db.users.find_one({"password": hashed_password})
        user_obj = User(
            user["username"],
            user["first_name"],
            user["last_name"],
            user["email"],
            user["_id"],
            user["is_admin"],
            user["avatar"],
        )
        login_user(user_obj)
        flash("Your password has been updated. You are now logged in.", "info")
        return redirect(url_for("login"))
    return render_template(
        "reset_token.html", title="Reset Password", form=form
    )


@app.route("/delete_user", methods=["GET", "POST"])
@login_required
def delete_user():
    """
    DESCRIPTION
    """
    mongo.db.users.remove({"username": current_user.username})
    logout_user()
    flash("You have deleted your account", "success")
    return redirect(url_for("index"))


# ! PERFUMES
@app.route("/perfume/new", methods=["GET", "POST"])
@login_required
def new_perfume():
    if current_user.is_admin:
        form = CreatePerfumeForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture = save_picture(form.picture.data)
                mongo.db.perfumes.insert(
                    {
                        "author": current_user.username,
                        "brand": form.brand.data,
                        "name": form.name.data,
                        "perfume_type": form.perfume_type.data,
                        "description": form.description.data,
                        "date_updated": datetime.utcnow(),
                        "public": form.public.data,
                        "picture": picture,
                    }
                )
            else:
                mongo.db.perfumes.insert(
                    {
                        "author": current_user.username,
                        "brand": form.brand.data,
                        "name": form.name.data,
                        "perfume_type": form.perfume_type.data,
                        "description": form.description.data,
                        "date_updated": datetime.utcnow(),
                        "public": form.public.data,
                        "picture": "generic.png",
                    }
                )

            flash("You added a new perfume!", "info")
            return redirect(url_for("perfumes"))
    else:
        flash("You need to be an administrator to enter data.", "danger")
        return redirect(url_for("index"))
    return render_template(
        "new_perfume.html",
        title="New Perfume",
        form=form,
        types=mongo.db.types.find().sort("type_name"),
    )


@app.route("/perfumes")
def perfumes():
    """sumary_line
    With a solution found on my question on Stack Overflow:
    https://stackoverflow.com/questions/61732985/inner-join-like-with-mongodb-in-flask-jinja
    Keyword arguments:
    argument -- description
    Return: return_description
    """

    cur = mongo.db.perfumes.aggregate(
        [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "author",
                    "foreignField": "username",
                    "as": "creator",
                }
            },
            {"$unwind": "$creator"},
            {
                "$project": {
                    "_id": "$_id",
                    "perfumeName": "$name",
                    "perfumeBrand": "$brand",
                    "perfumeDescription": "$description",
                    "date_updated": "$date_updated",
                    "perfumePicture": "$picture",
                    "isPublic": "$public",
                    "perfumeType": "$perfume_type",
                    "username": "$creator.username",
                    "firstName": "$creator.first_name",
                    "lastName": "$creator.last_name",
                    "profilePicture": "$creator.avatar",
                }
            },
            {"$sort": {"perfumeName": 1}},
        ]
    )
    return render_template("perfumes.html", title="Perfumes", perfumes=cur)


@app.route("/perfume/<id>", methods=["POST", "GET"])
def perfume(id):
    perfume = mongo.db.perfumes.find_one({"_id": ObjectId(id)})
    # reviews = mongo.db.perfumes.review.find_one({"_id": ObjectId(id)})  # TEST
    form = AddReviewForm()
    cur = mongo.db.perfumes.aggregate(
        [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "author",
                    "foreignField": "username",
                    "as": "creator",
                }
            },
            {"$unwind": "$creator"},
            {
                "$project": {
                    "_id": "$_id",
                    "perfumeName": "$name",
                    "perfumeBrand": "$brand",
                    "perfumeDescription": "$description",
                    "date_updated": "$date_updated",
                    "perfumePicture": "$picture",
                    "isPublic": "$public",
                    "perfumeType": "$perfume_type",
                    "username": "$creator.username",
                    "firstName": "$creator.first_name",
                    "lastName": "$creator.last_name",
                    "profilePicture": "$creator.avatar",
                }
            },
            {"$match": {"_id": ObjectId(id)}},
        ]
    )
    return render_template(
        "perfume.html",
        title="Perfumes",
        cursor=cur,
        perfume=perfume,
        form=form,
    )


@app.route("/perfumes/<id>", methods=["POST"])
@login_required
def delete_perfume(id):
    if current_user.is_admin:
        mongo.db.perfumes.delete_one({"_id": ObjectId(id)})
        flash("You deleted this perfume", "success")
        return redirect(url_for("perfumes"))
    flash("Not allowed", "warning")
    return redirect(url_for("perfumes"))


@app.route("/perfume/edit/<id>", methods=["POST", "GET"])
@login_required
def edit_perfume(id):
    form = EditPerfumeForm()
    perfume = mongo.db.perfumes.find_one({"_id": ObjectId(id)})
    if current_user.is_admin:
        if form.validate_on_submit():
            if form.picture.data:
                picture = save_picture(form.picture.data)
                new_value = {
                    "$set": {
                        "brand": form.brand.data,
                        "name": form.name.data,
                        "perfume_type": form.perfume_type.data,
                        "description": form.description.data,
                        "date_updated": datetime.utcnow(),
                        "public": form.public.data,
                        "picture": picture,
                    }
                }
                mongo.db.perfumes.update_one(perfume, new_value)
                flash("You updated the perfume", "info")
                return redirect(url_for("perfume", id=perfume["_id"]))
            else:
                new_value = {
                    "$set": {
                        "brand": form.brand.data,
                        "name": form.name.data,
                        "perfume_type": form.perfume_type.data,
                        "description": form.description.data,
                        "date_updated": datetime.utcnow(),
                        "public": form.public.data,
                    }
                }
                mongo.db.perfumes.update_one(perfume, new_value)
                flash("You updated the perfume", "info")
                return redirect(url_for("perfume", id=perfume["_id"]))
        elif request.method == "GET":
            form.brand.data = perfume["brand"]
            form.name.data = perfume["name"]
            form.perfume_type.data = perfume["perfume_type"]
            form.description.data = perfume["description"]
            form.public.data = perfume["public"]
    return render_template(
        "edit_perfume.html",
        title="Edit Perfume",
        form=form,
        types=mongo.db.types.find().sort("type_name"),
    )


@app.route("/perfume/review/<id>", methods=["POST", "GET"])
@login_required
def review_perfume(id):
    form = AddReviewForm()
    perfume = mongo.db.perfumes.find_one({"_id": ObjectId(id)})
    if form.validate_on_submit():
        # ! don't delete from
        # mongo.db.reviews.insert(
        #     {
        #         "review_author": current_user.username,
        #         "review": form.review.data,
        #         "review_date": datetime.utcnow(),
        #         "review_avatar": current_user.avatar,
        #     }
        # )
        # ! don't delete to
        # review = mongo.db.reviews.find_one()
        # print(mongo.db.reviews.find().limit(1).sort("$natural", -1))
        # ! don't delete from
        # my_review = mongo.db.reviews.find().sort("_id", -1).limit(1)[0]["_id"]
        # mongo.db.perfumes.update(
        #     {"_id": perfume["_id"]}, {"$push": {"review": my_review}}
        # )
        # ! don't delete to
        review_id = ObjectId.from_datetime(datetime.utcnow())
        mongo.db.perfumes.update(
            {"_id": perfume["_id"]},
            {
                "$push": {
                    "review": {
                        "_id": review_id,
                        "review_content": form.review.data,
                        "reviewer": current_user.username,
                        "date_reviewed": datetime.utcnow(),
                        "reviewer_picture": current_user.avatar,
                    }
                }
            },
        )
        flash("Your review has been received", "success")
        return redirect(url_for("perfume", id=perfume["_id"]))
    return redirect(url_for("perfume", id=perfume["_id"]))


# ! Types
@app.route("/type/new", methods=["GET", "POST"])
@login_required
def new_type():
    if current_user.is_admin:
        form = CreateTypeForm()
        if form.validate_on_submit():
            mongo.db.types.insert(
                {
                    "type_name": form.type_name.data,
                    "description": form.description.data,
                    "author": current_user.username,
                }
            )
            flash("You added a new type!", "info")
            return redirect(url_for("types"))
    else:
        flash("You need to be an administrator.", "danger")
        return redirect(url_for("index"))
    return render_template("new_type.html", title="New Type", form=form)


@app.route("/types")
def types():
    types = mongo.db.types.find().sort("type_name")
    return render_template("types.html", types=types)


@app.route("/type/<id>")
def type(id):
    type = mongo.db.types.find_one({"_id": ObjectId(id)})
    return render_template("type.html", type=type)


@app.route("/type/<id>", methods=["POST"])
@login_required
def delete_type(id):
    if current_user.is_admin:
        mongo.db.types.delete_one({"_id": ObjectId(id)})
        flash("You deleted this type", "success")
        return redirect(url_for("types"))
    flash("Not allowed", "warning")
    return redirect(url_for("types"))


@app.route("/type/edit/<id>", methods=["POST", "GET"])
@login_required
def edit_type(id):
    form = EditTypeForm()
    type = mongo.db.types.find_one({"_id": ObjectId(id)})
    if current_user.is_admin:
        if form.validate_on_submit():
            new_value = {
                "$set": {
                    "type_name": form.type_name.data,
                    "description": form.description.data,
                }
            }
            mongo.db.types.update_one(type, new_value)
            flash("Type has been updated", "info")
            return redirect(url_for("type", id=type["_id"]))
        elif request.method == "GET":
            form.type_name.data = type["type_name"]
            form.description.data = type["description"]
    return render_template("edit_type.html", title="Edit Type", form=form)


@app.route("/delete_review/<id>/<perfume_id>")
@login_required
def delete_review(id, perfume_id):
    """With help from:

    Keyword arguments:
    argument -- description
    Return: return_description
    """
    mongo.db.perfumes.update_one(
        {"_id": ObjectId(perfume_id)},
        {"$pull": {"review": {"_id": ObjectId(id)}}},
    )
    flash("Your review has been deleted!", "success")
    return redirect(url_for("perfume", id=perfume_id))


@app.route("/edit_review/<id>/<perfume_id>", methods=["GET", "POST"])
@login_required
def edit_review(id, perfume_id):

    mongo.db.perfumes.update_one(
        {"_id": ObjectId(perfume_id)},
        {"$pull": {"review": {"_id": ObjectId(id)}}},
    )
    flash("Your review has been updated!", "success")
    return redirect(url_for("perfume", id=perfume_id))
