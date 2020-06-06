"""sumary_line"""
from flask import Blueprint, redirect, url_for, render_template, flash
from flask_login import current_user, login_required
from bson.objectid import ObjectId
from parfumier import mongo
from parfumier.types.forms import CreateTypeForm, EditTypeForm


types = Blueprint("types", __name__)


@types.route("/type/new", methods=["POST", "GET"])
@login_required
def new_type():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

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
            return redirect(url_for("types.all_types"))
    else:
        flash("You need to be an administrator.", "danger")
        return redirect(url_for("main.index"))
    return render_template("pages/new_type.html", title="New Type", form=form)


@types.route("/types")
def all_types():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    the_types = mongo.db.types.find().sort("type_name")
    return render_template("pages/types.html", types=the_types, title="Types")


@types.route("/type/<type_id>")
def show_type(type_id):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    one_type = mongo.db.types.find_one({"_id": ObjectId(type_id)})
    return render_template(
        "pages/type.html", type=one_type, title=one_type["type_name"]
    )


@types.route("/type/<type_id>", methods=["POST"])
@login_required
def delete_type(type_id):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
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
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
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
        "pages/edit_type.html",
        title="Edit Type",
        form=form,
        current_type=current_type,
    )
