"""Imports all Flask components, database object and forms"""
from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from bson.objectid import ObjectId
from parfumier import mongo
from parfumier.types.forms import CreateTypeForm, EditTypeForm
from flask_paginate import Pagination, get_page_parameter


types = Blueprint("types", __name__)


@types.route("/type/new", methods=["POST", "GET"])
@login_required
def new_type():
    """Creates a new Perfume Type

    User has to be an admin in order to create a perfume type.
    The route simply creates a new document with the information
    passed in the form in case the form validates.
    """

    if current_user.is_admin:
        form = CreateTypeForm()
        if form.validate_on_submit():
            if form.type_picture.data:
                picture_uploaded = upload(form.type_picture.data)
                type_picture, options = cloudinary_url(
                    picture_uploaded["public_id"],
                    format="jpg",
                    crop="fill",
                    width=250,
                    height=250,
                    opacity=20,
                )
                picture_link = type_picture.replace("http", "https")
                mongo.db.types.insert(
                    {
                        "type_name": form.type_name.data,
                        "description": form.description.data,
                        "type_picture": picture_link,
                        "author": current_user.username,
                    }
                )
            else:
                mongo.db.types.insert(
                    {
                        "type_name": form.type_name.data,
                        "description": form.description.data,
                        "type_picture": (
                            "https://res.cloudinary.com/gbrachetta/"
                            "image/upload/c_scale,o_20,w_293/"
                            "v1578262574/sample.jpg"
                        ),
                        "author": current_user.username,
                    }
                )
            flash("You added a new type!", "info")
            return redirect(url_for("types.all_types"))
    else:
        flash("You need to be an administrator.", "danger")
        return redirect(url_for("main.index"))
    return render_template(
        "pages/perfume-and-type.html",
        title="New Type",
        form=form,
        new_type=True,
        heading="New Type",
    )


@types.route("/types")
def all_types():
    """Displays all types

    This route simply displays all existing types.
    It uses aggregation in order to allow for pagination.
    """
    page = request.args.get(get_page_parameter(), type=int, default=1)
    total_types = mongo.db.types.find().count()
    page_count = 8
    the_types = mongo.db.types.aggregate(
        [
            {
                "$lookup": {
                    "from": "types",
                    "localField": "type_name",
                    "foreignField": "perfume_type",
                    "as": "type",
                }
            },
            {"$unwind": "$type_name"},
            {
                "$project": {
                    "_id": "$_id",
                    "typeName": "$type_name",
                    "picture": "$type_picture",
                }
            },
            {"$sort": {"typeName": 1}},
            {"$skip": (page - 1) * page_count},
            {"$limit": page_count},
        ]
    )
    pagination = Pagination(
        per_page=8,
        page=page,
        total=total_types,
        record_name="types",
        bs_version=4,
        outer_window=2,
        alignment="center",
        display_msg="Displaying <b>{start} - {end}</b>\
        {record_name} of <b>{total}</b>",
    )
    return render_template(
        "pages/types.html",
        types=the_types,
        title="Types",
        pagination=pagination,
    )


@types.route("/type/<type_id>")
def show_type(type_id):
    """Displays one type only

    This route displays the type selected using the unique ObjectId.
    """

    one_type = mongo.db.types.find_one({"_id": ObjectId(type_id)})
    return render_template(
        "pages/type.html", type=one_type, title=one_type["type_name"]
    )


@types.route("/type/<type_id>", methods=["POST"])
@login_required
def delete_type(type_id):
    """Deletes a perfume type

    This route simply deletes a perfume type matched by its id.
    It's only available to admins.
    """

    if current_user.is_admin:
        mongo.db.types.delete_one({"_id": ObjectId(type_id)})
        flash("You deleted this type", "success")
        return redirect(url_for("types.all_types"))
    flash("Not allowed", "warning")
    return redirect(url_for("types.all_types"))


@types.route("/type/edit/<type_id>", methods=["POST", "GET"])
@login_required
def edit_type(type_id):
    """Allows editing a Perfume Type

    This route finds a type by its id, assigns the current name to the hidden
    field (used to check against to avoid a false validation error) and updates
    the current data from its corresponding document in the database.
    """

    form = EditTypeForm()
    current_type = mongo.db.types.find_one({"_id": ObjectId(type_id)})
    current_type_name = mongo.db.types.find_one(
        {"_id": ObjectId(type_id)}, {"_id": 0, "type_name": 1}
    )
    form.origin_type_name.data = current_type_name["type_name"]
    current_type_value = mongo.db.types.find_one({"_id": ObjectId(type_id)})
    if current_user.is_admin:
        if form.validate_on_submit():
            if form.type_picture.data:
                picture_uploaded = upload(form.type_picture.data)
                type_picture, options = cloudinary_url(
                    picture_uploaded["public_id"],
                    format="jpg",
                    crop="fill",
                    width=250,
                    height=250,
                    opacity=20,
                )
                picture_link = type_picture.replace("http", "https")
                new_value = {
                    "$set": {
                        "type_name": form.type_name.data,
                        "description": form.description.data,
                        "type_picture": picture_link,
                    }
                }
                mongo.db.types.update_one(current_type_value, new_value)
                flash("Type has been updated", "info")
                return redirect(
                    url_for(
                        "types.show_type", type_id=current_type_value["_id"]
                    )
                )
            else:
                new_value = {
                    "$set": {
                        "type_name": form.type_name.data,
                        "description": form.description.data,
                    }
                }
            mongo.db.types.update_one(current_type_value, new_value)
            flash("Type has been updated", "info")
            return redirect(
                url_for("types.show_type", type_id=current_type_value["_id"])
            )
        form.type_name.data = current_type_value["type_name"]
        form.description.data = current_type_value["description"]
    return render_template(
        "pages/perfume-and-type.html",
        title="Edit Type",
        form=form,
        current_type=current_type,
        edit_type=True,
        heading="Edit Type",
    )
