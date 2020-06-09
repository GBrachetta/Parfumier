"""Besides the flask imports, math was imported to deal with
pagination, datetime to stamp current creation date, cloudinary_url
and upload to deal with uploading images and ObjectId to find and deal
with objects by their id.
"""
from datetime import datetime
import math
from flask import render_template, redirect, flash, url_for, request, Blueprint
from flask_login import login_required, current_user
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from bson.objectid import ObjectId
from parfumier.perfumes.forms import CreatePerfumeForm, EditPerfumeForm
from parfumier.reviews.forms import AddReviewForm, EditReviewForm
from parfumier import mongo

perfumes = Blueprint("perfumes", __name__)


@perfumes.route("/perfumes")
def all_perfumes():
    """Displays all pefumes

    With a solution found on my question on Stack Overflow:
    https://stackoverflow.com/questions/61732985/inner-join-like-with-mongodb-in-flask-jinja
    Adds pagination (8 items per page) and uses aggregation to
    combine multiple collections.
    Returns a cursor with the said aggregation amongst pagination objects
    and the types collection ordered by name.
    """
    types = mongo.db.types.find().sort("type_name")
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
    """Creates a new perfume (only admins)

    Uses Cloudinary to upload images. The variable 'options' throws a
    warning but it's necessary to specify Cloudinary's settings.
    In case a picture isn't chosen, the function defaults to a
    pre-chosen generic photo present in Cloudinary.
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
                picture_link = picture.replace("http", "https")
                mongo.db.perfumes.insert(
                    {
                        "author": current_user.username,
                        "brand": form.brand.data,
                        "name": form.name.data,
                        "perfume_type": form.perfume_type.data,
                        "description": form.description.data,
                        "date_updated": datetime.utcnow(),
                        "public": form.public.data,
                        "picture": picture_link,
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
                        "picture": (
                            "https://res.cloudinary.com/gbrachetta/"
                            "image/upload/v1590013198/generic.jpg"
                        ),
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


@perfumes.route("/perfume/<perfume_id>", methods=["GET"])
def perfume(perfume_id):
    """Returns an individual perfume

    Uses aggregation to combine perfumes and types in order
    to display details about a particular perfume.
    Includes the review form in order to allow for reviews
    to be placed over those individual perfumes.
    """

    current_perfume = mongo.db.perfumes.find_one({"_id": ObjectId(perfume_id)})
    add_review_form = AddReviewForm()
    edit_review_form = EditReviewForm()
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
            {"$match": {"_id": ObjectId(perfume_id)}},
        ]
    )
    return render_template(
        "pages/perfume.html",
        title=current_perfume["name"],
        cursor=cur,
        perfume=current_perfume,
        add_review_form=add_review_form,
        edit_review_form=edit_review_form,
    )


@perfumes.route("/perfume/<perfume_id>/delete", methods=["POST", "GET"])
@login_required
def delete_perfume(perfume_id):
    """Deletes a perfume

    Simply deletes one perfume found through its ObjectId.
    """

    if current_user.is_admin:
        mongo.db.perfumes.delete_one({"_id": ObjectId(perfume_id)})
        flash("You deleted this perfume", "success")
        return redirect(url_for("perfumes.all_perfumes"))
    flash("Not allowed", "warning")
    return redirect(url_for("perfumes.all_perfumes"))


@perfumes.route("/perfume/edit/<perfume_id>", methods=["POST", "GET"])
@login_required
def edit_perfume(perfume_id):
    """Edits an existing perfume

    If the user is an admin and the form validates, checks if there is a
    picture to be uploaded, in which case it uses the cloudinary import
    with its options to format and resize it.
    The function also replaces the http protocol rendered by cloudinary
    with https to serve them securely.
    It then updates the existing record. This existing record populates
    the form with its current values.
    """

    form = EditPerfumeForm()
    current_perfume = mongo.db.perfumes.find_one({"_id": ObjectId(perfume_id)})
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
                picture_link = picture.replace("http", "https")
                new_value = {
                    "$set": {
                        "brand": form.brand.data,
                        "name": form.name.data,
                        "perfume_type": form.perfume_type.data,
                        "description": form.description.data,
                        "date_updated": datetime.utcnow(),
                        "public": form.public.data,
                        "picture": picture_link,
                    }
                }
                mongo.db.perfumes.update_one(current_perfume, new_value)
                flash("You updated the perfume", "info")
                return redirect(
                    url_for(
                        "perfumes.perfume", perfume_id=current_perfume["_id"]
                    )
                )
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
            mongo.db.perfumes.update_one(current_perfume, new_value)
            flash("You updated the perfume", "info")
            return redirect(
                url_for("perfumes.perfume", perfume_id=current_perfume["_id"])
            )
        form.brand.data = current_perfume["brand"]
        form.name.data = current_perfume["name"]
        form.perfume_type.data = current_perfume["perfume_type"]
        form.description.data = current_perfume["description"]
        form.public.data = current_perfume["public"]
    return render_template(
        "pages/edit_perfume.html",
        title="Edit Perfume",
        form=form,
        current_perfume=current_perfume,
        types=mongo.db.types.find().sort("type_name"),
    )


@perfumes.route("/search")
def search():
    """Allows to search by determined fields

    Creates an index over the collection on the 'name', 'brand'
    and 'type' fields to allow searching through those.
    This command indexes the remote Mongodb database.
    It returns all the perfumes if nothing has been entered
    in the search form.
    It returns the 'results' cursor, sorted alphabetically.
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
        "pages/perfumes.html", perfumes=results, types=types, title="Perfumes",
    )


@perfumes.route("/filters")
def filters():
    """Allows to query the db by type

    Similar to the previous function, but this indexes by type only.
    In combination with its JavaScritp function checkSelected(), it
    triggers the query without further interaction from the user
    such as pressing a submit button.
    It also contains a shortcut to create a new type if the proper
    option is selected.
    As in most perfumes and types routes, this one uses aggregation.
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
        "pages/perfumes.html", perfumes=results, types=types, title="Perfumes",
    )
