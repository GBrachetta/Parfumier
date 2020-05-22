"""sumary_line"""
from datetime import datetime
import math
from flask import render_template, redirect, flash, url_for, request, Blueprint
from flask_login import login_required, current_user
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from bson.objectid import ObjectId
from parfumier.perfumes.forms import CreatePerfumeForm, EditPerfumeForm
from parfumier.reviews.forms import AddReviewForm
from parfumier import mongo

perfumes = Blueprint("perfumes", __name__)


@perfumes.route("/perfumes")
def all_perfumes():
    """sumary_line
    With a solution found on my question on Stack Overflow:
    https://stackoverflow.com/questions/61732985/inner-join-like-with-mongodb-in-flask-jinja
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    types = mongo.db.types.find().sort("type_name")
    # Pagination
    page_count = 8
    page = int(request.args.get("page", 1))
    total_perfumes = mongo.db.perfumes.count()
    total_pages = range(1, int(math.ceil(total_perfumes / page_count)) + 1)
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
            {"$skip": (page - 1) * page_count},
            {"$limit": page_count},
        ]
    )
    return render_template(
        "pages/perfumes.html",
        title="Perfumes",
        perfumes=cur,
        types=types,
        page=page,
        total_pages=total_pages,
    )


@perfumes.route("/perfume/new", methods=["GET", "POST"])
@login_required
def new_perfume():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    if current_user.is_admin:
        form = CreatePerfumeForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_uploaded = upload(form.picture.data)
                picture, options = cloudinary_url(
                    picture_uploaded["public_id"],
                    format="jpg",
                    crop="fill",
                    width=225,
                    height=300,
                )
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
                        "picture": ("https://res.cloudinary.com/gbrachetta/"
                                    "image/upload/v1590013198/generic.jpg"),
                    }
                )

            flash("You added a new perfume!", "info")
            return redirect(url_for("perfumes.all_perfumes"))
    else:
        flash("You need to be an administrator to enter data.", "danger")
        return redirect(url_for("main.index"))
    return render_template(
        "pages/new_perfume.html",
        title="New Perfume",
        form=form,
        types=mongo.db.types.find().sort("type_name"),
    )


@perfumes.route("/perfume/<id>", methods=["GET"])
def perfume(id):
    perfume = mongo.db.perfumes.find_one({"_id": ObjectId(id)})
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
        "pages/perfume.html",
        title="Perfumes",
        cursor=cur,
        perfume=perfume,
        form=form,
    )


@perfumes.route("/perfume/<id>/delete", methods=["POST", "GET"])
@login_required
def delete_perfume(id):
    if current_user.is_admin:
        mongo.db.perfumes.delete_one({"_id": ObjectId(id)})
        flash("You deleted this perfume", "success")
        return redirect(url_for("perfumes.all_perfumes"))
    flash("Not allowed", "warning")
    return redirect(url_for("perfumes.all_perfumes"))


@perfumes.route("/perfume/edit/<id>", methods=["POST", "GET"])
@login_required
def edit_perfume(id):
    form = EditPerfumeForm()
    perfume = mongo.db.perfumes.find_one({"_id": ObjectId(id)})
    if current_user.is_admin:
        if form.validate_on_submit():
            if form.picture.data:
                picture_uploaded = upload(form.picture.data)
                # "options" is a needed parameter in order for cloudinary to
                # format the thumbnail server-side
                picture, options = cloudinary_url(
                    picture_uploaded["public_id"],
                    format="jpg",
                    crop="fill",
                    width=225,
                    height=300,
                )
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
                return redirect(url_for("perfumes.perfume", id=perfume["_id"]))
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
            return redirect(url_for("perfumes.perfume", id=perfume["_id"]))
        form.brand.data = perfume["brand"]
        form.name.data = perfume["name"]
        form.perfume_type.data = perfume["perfume_type"]
        form.description.data = perfume["description"]
        form.public.data = perfume["public"]
    return render_template(
        "pages/edit_perfume.html",
        title="Edit Perfume",
        form=form,
        types=mongo.db.types.find().sort("type_name"),
    )


@perfumes.route("/search")
def search():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    types = mongo.db.types.find().sort("type_name")
    mongo.db.perfumes.create_index(
        [("name", "text"), ("brand", "text"), ("perfume_type", "text")]
    )
    db_query = request.args["db_query"]
    if db_query == "":
        return redirect(url_for("perfumes.all_perfumes"))
    results = mongo.db.perfumes.aggregate(
        [
            {"$match": {"$text": {"$search": db_query}}},
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
    return render_template(
        "pages/perfumes.html",
        perfumes=results,
        types=types,
        title="Perfumes",
    )


@perfumes.route("/filters")
def filters():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    types = mongo.db.types.find().sort("type_name")
    mongo.db.types.create_index([("type_name", "text")])
    filter_query = request.args["filter_query"]
    if filter_query == "":
        return redirect(url_for("perfumes.all_perfumes"))
    results = mongo.db.perfumes.aggregate(
        [
            {"$match": {"$text": {"$search": filter_query}}},
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
    return render_template(
        "pages/perfumes.html",
        perfumes=results,
        types=types,
        title="Perfumes",
    )
