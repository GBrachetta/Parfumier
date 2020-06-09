"""Imports from Flask, the database and needed forms"""
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
    """Route used to create a review

    After defining all objects to be passed to the template (including
    the cursor with the aggregated perfume) the method updates the array
    of objects in the perfumes collection with the corresponding review.
    It records who posted the review (including a link to their avatar),
    the date of the review and the content with the html produced by
    CKEditor from the text area field.
    The id of the review is created using ObjectId with the current
    creation moment, assigning a virtually unique id to each review.
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
        title="Perfume"
    )


@reviews.route("/perfume/review", methods=["POST"])
@login_required
def delete_review():
    """Deletes a particular review

    This simply deletes a review based on the combination of
    the id from both the perfume and the review itself.
    As this comes from a modal, that information is passed
    through the hidden inputs in the modal, from the main
    corresponding template.
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
    """Edits an existing review

    Similar to the previous method, this one also collects the necessary
    identificators from the hidden fields containing the ids passed from
    the main template.
    It then simply updates the existing review.
    A JavaScript function pre-populates the form displaying the current
    contents of the review to be modified.
    """

    form = EditReviewForm()
    review_id = request.form.get("review_id")
    perfume_id = request.form.get("perfume_id")
    if form.validate_on_submit():
        mongo.db.perfumes.update(
            {"_id": ObjectId(perfume_id), "reviews._id": ObjectId(review_id)},
            {"$set": {"reviews.$.review_content": form.edit_review.data, }},
        )
        flash("Your review has been updated!", "success")
        return redirect(url_for("perfumes.perfume", perfume_id=perfume_id))
    # form.review.data = review[{"_id": ObjectId(review_id)}]
    flash("Your review has not been changed", "danger")
    return redirect(url_for("perfumes.perfume", perfume_id=perfume_id))
