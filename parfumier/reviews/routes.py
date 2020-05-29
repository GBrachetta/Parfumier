"""sumary_line"""
from datetime import datetime
from flask import flash, redirect, Blueprint, url_for, request, render_template
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from parfumier import mongo
from parfumier.reviews.forms import AddReviewForm, EditReviewForm


reviews = Blueprint("reviews", __name__)


@reviews.route("/perfume/review/<perfume_id>", methods=["POST", "GET"])
@login_required
def review_perfume(perfume_id):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    form = AddReviewForm()
    form_edit = EditReviewForm()
    perfume = mongo.db.perfumes.find_one({"_id": ObjectId(perfume_id)})
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
    if form.validate_on_submit():
        review_id = ObjectId.from_datetime(datetime.utcnow())
        mongo.db.perfumes.update(
            {"_id": perfume["_id"]},
            {
                "$push": {
                    "reviews": {
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
        return redirect(url_for("perfumes.perfume", perfume_id=perfume["_id"]))
    return render_template(
        "pages/perfume.html",
        perfume=perfume,
        add_review_form=form,
        edit_review_form=form_edit,
        cursor=cur,
    )


@reviews.route("/perfume/review", methods=["POST"])
@login_required
def delete_review():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    review_id = request.form.get("review_id")
    perfume_id = request.form.get("perfume_id")
    mongo.db.perfumes.update_one(
        {"_id": ObjectId(perfume_id)},
        {"$pull": {"reviews": {"_id": ObjectId(review_id)}}},
    )
    flash("Your review has been deleted!", "success")
    return redirect(url_for("perfumes.perfume", perfume_id=perfume_id))


@reviews.route("/review", methods=["GET", "POST"])
@login_required
def edit_review():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    form = EditReviewForm()
    review_id = request.form.get("review_id")
    print(review_id)
    perfume_id = request.form.get("perfume_id")
    # review = mongo.db.perfumes.find_one(ObjectId(perfume_id))
    if form.validate_on_submit():
        mongo.db.perfumes.update(
            {"_id": ObjectId(perfume_id), "reviews._id": ObjectId(review_id)},
            {
                "$set": {
                    "reviews.$.review_content": form.edit_review.data,
                    # "reviews.$.date_reviewed": datetime.utcnow(),
                }
            },
        )
        flash("Your review has been updated!", "success")
        return redirect(url_for("perfumes.perfume", perfume_id=perfume_id))
    # form.review.data = review[{"_id": ObjectId(review_id)}]
    return redirect(url_for("perfumes.perfume", perfume_id=perfume_id))
