from flask import flash, redirect, Blueprint, url_for, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime
from app import mongo
from app.reviewsBP.forms import AddReviewForm, EditReviewForm


reviewsBP = Blueprint("reviewsBP", __name__)


@reviewsBP.route("/perfume/review/<id>", methods=["POST"])
@login_required
def review_perfume(id):
    form = AddReviewForm()
    perfume = mongo.db.perfumes.find_one({"_id": ObjectId(id)})
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
        return redirect(url_for("perfumesBP.perfume", id=perfume["_id"]))
    return redirect(url_for("perfumesBP.perfume", id=perfume["_id"]))


@reviewsBP.route("/perfume/review", methods=["POST"])
@login_required
def delete_review():
    review_id = request.form.get("review_id")
    perfume_id = request.form.get("perfume_id")
    mongo.db.perfumes.update_one(
        {"_id": ObjectId(perfume_id)},
        {"$pull": {"reviews": {"_id": ObjectId(review_id)}}},
    )
    flash("Your review has been deleted!", "success")
    return redirect(url_for("perfumesBP.perfume", id=perfume_id))


@reviewsBP.route("/review", methods=["GET", "POST"])
@login_required
def edit_review():
    form = EditReviewForm()
    review_id = request.form.get("review_id")
    perfume_id = request.form.get("perfume_id")
    review = mongo.db.perfumes.find_one(ObjectId(perfume_id))
    if form.validate_on_submit():
        mongo.db.perfumes.update(
            {"_id": ObjectId(perfume_id), "reviews._id": ObjectId(review_id)},
            {
                "$set": {
                    "reviews.$.review_content": form.review.data,
                    "reviews.$.date_reviewed": datetime.utcnow(),
                }
            },
        )
        flash("Your review has been updated!", "success")
        return redirect(url_for("perfumesBP.perfume", id=perfume_id))
    elif request.method == "GET":
        form.review.data = review[{"_id": ObjectId(review_id)}]
    return redirect(url_for("perfumesBP.perfume", id=perfume_id))
