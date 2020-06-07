# Parfumier <!-- omit in toc -->

> An app that allows users to create a profile, edit it, add their profile image and interact with a database with perfumes.

![Mockup](wireframes/images/mockup.png)

## Table of Contents <!-- omit in toc -->

- [Introduction](#introduction)
- [UX](#ux)
  - [Who is this website for](#who-is-this-website-for)
  - [Who are the primary target groups](#who-are-the-primary-target-groups)
  - [What is it that they (the users) want to achieve](#what-is-it-that-they-the-users-want-to-achieve)
  - [How is my project the best way to help them achieve those things](#how-is-my-project-the-best-way-to-help-them-achieve-those-things)
  - [How do users achieve each of the following goals](#how-do-users-achieve-each-of-the-following-goals)
- [Project Goals](#project-goals)
  - [User Goals](#user-goals)
  - [Visitor Goals](#visitor-goals)
- [User Stories](#user-stories)
- [Design Choices](#design-choices)
  - [Buttons](#buttons)
  - [Colors](#colors)
- [Wireframes](#wireframes)
- [Features](#features)
  - [Existing Features](#existing-features)
    - [Login](#login)
    - [Account managment](#account-managment)
    - [Perfumes](#perfumes)
    - [Admins](#admins)
    - [Perfume Photos](#perfume-photos)
    - [Default photos](#default-photos)
  - [Future Goals](#future-goals)
- [Information Architecture](#information-architecture)
  - [Database Choice](#database-choice)
  - [Data Storage](#data-storage)
- [Technologies Used](#technologies-used)
  - [MongoDB](#mongodb)
  - [Python](#python)
  - [JavaScript](#javascript)
  - [HTML](#html)
  - [CSS](#css)
  - [Cloudinary](#cloudinary)
- [Testing](#testing)
- [Issues found and status](#issues-found-and-status)
  - [Custom Validator for types](#custom-validator-for-types)
  - [Aggregation](#aggregation)
  - [Onerror default to picture](#onerror-default-to-picture)
  - [Images](#images)
  - [filters](#filters)
    - [Search](#search)
    - [CKEdit](#ckedit)
    - [Quote all testing as noted in external doc](#quote-all-testing-as-noted-in-external-doc)
  - [Deployment](#deployment)
    - [Heroku](#heroku)
    - [Variables](#variables)
  - [Credits](#credits)
    - [Content](#content)
    - [Media](#media)
    - [Code](#code)
    - [Acknowledgements](#acknowledgements)
- [Disclaimer](#disclaimer)

---

## Introduction

The current app is my third submission for my studies at Code Institue and it was inspired by my love for fragrances.

## UX

### Who is this website for

This website is intended for all pefume lovers, people curious about perfumes, or people wishing to exchange comments, reviews and experiences around perfumes.

### Who are the primary target groups

### What is it that they (the users) want to achieve

### How is my project the best way to help them achieve those things

### How do users achieve each of the following goals

## Project Goals

### User Goals

### Visitor Goals

## User Stories

> As a user, I would like to ______________"

- Find information about perfumes.
- Be able to see what the bottle looks like.
- Be able to search for a particular perfume.
- Be able to filter perfumes by type.
- Learn more about types of perfumes.
- Be able to read reviews on a perfume.
- Be able to write my own review on a perfume.
- Be able to create an account and modify it.
- Be able to upload an avatar or photo of my choice, and preview it before I do so.
- Be able to change that photo at any point.
- See my photo next to my reviews on perfumes.
- Be able to create a new password in case I forgot my current one.
- Be able to edit or delete my reviews on a perfume.
- Be able to delete my account.

> As an administrator, I would like to do all of the above, plus ______________"

- Be able to create, modify and delete perfumes.
- Be able to upload a photo of the perfume, and to change it.
- Be able to preview the photo I'm about to upload.
- Be able to create, modify and delete types of perfumes.

## Design Choices

### Buttons

I chose to have well rounded buttons.

### Colors

The colors chosen for the app are all soft shades of pastel colors allowing users to make a visual connection with the world of perfumes: flowers, herbs, spices and woods.

![Color Palette](wireframes/images/palette.png)

## Wireframes

- [Login Page](wireframes/login.png)
- [Account Page](wireframes/account.png)
- [Register Page](wireframes/register.png)
- [All Perfumes](wireframes/perfumes.png)
- [Individual Perfume](wireframes/perfume.png)
- [All Types](wireframes/types.png)
- [Individual Type](wireframes/type.png)
- [About](wireframes/about.png)

## Features

### Existing Features

#### Login

Users can create an account and log in.
This gives registered users the possibility to add reviews to perfumes, edit them and delete them.

#### Account managment

- Users can edit their account and change their information.
- Users can upload a picture or avatar which will represent their interaction with the app. The picture can also be changed at any point.
- Users have the possibility to delete their account.
- Users can request a password reset in case they forget their password.

#### Perfumes

- Admins are able to create, edit and delete perfumes.
- Admins can upload and change a picture for the above perfumes.
- All users and not registered visitors can browse and search the full database and access all perfumes and reviews.

#### Admins

- Admins have access to functionalities reserved only to them, such as
  - Creating a perfume.
  - Deleting a perfume.

#### Perfume Photos

#### Default photos

### Future Goals

## Information Architecture

### Database Choice

For this project we were instructed to use MongoDB as our database.

MongoDB is a non-relational database but I still decided to have three different collections and find ways to combine data from them by using aggregation, such as in the colde below:

``` python
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
```

### Data Storage

## Technologies Used

### MongoDB

### Python

### JavaScript

### HTML

### CSS

### Cloudinary

The app originally saved media files to the file system, but that caused some issues:

- The local and remote file systems are different spaces, so pictures uploaded while on development didn't exist remotely (and vice-versa).
- Heroku's file system is ephemeral, meaning that it is rebuilt on each deployment. That causes that all pictures uploaded at a certain point get destroyed on subsequent deploys, making the media file practically unmanageable.

With this in mind I decided considered saving photos to a cloud-based solution reachable both locally and remotely.
The options I considered were Imgur and Cloudinary, and chose the latter due to its set of features and ease of use and setup.

## Testing

## Issues found and status

During the project I met several challenges, as this was my first experience with both Python and MongoDB (or any database for that matter).
Some of them are summarised below.

### Custom Validator for types

While

### Aggregation

### Onerror default to picture

If for some reason outside my control a remote image weren't found for a user or a perfume, I decided to put in place the following method in the templates to ensure at least that the visitor wouldn't see a broken image icon.

### Images

### filters

#### Search

I userd the following to index my collections and allow users to perform searches on the indexed fields:

```python
@perfumes.route("/search")
def search():
    types = mongo.db.types.find().sort("type_name")
    mongo.db.perfumes.create_index(
        [("name", "text"), ("brand", "text"), ("perfume_type", "text")]
    ) # This creates the indexes for the three mentioned fields, allowing users to search the collection
    db_query = request.args["db_query"]
    # If no text is entered, returns all the perfumes.
    if db_query == "":
        return redirect(url_for("perfumes.all_perfumes"))
    # I then use the aggregate method to render the search results including
    # the necessary fields from other collections, such as the avatar,
    # and sort that aggregate by name.
    results = mongo.db.perfumes.aggregate(
        [
            {"$match": {"$text": {"$search": db_query}}},
            {
                "$lookup": {...}
            },
            {"$unwind": "$creator"},
            {
                "$project": {...}
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
```

#### CKEdit

This was my choice in order to give admins and users the possibility to enter text in Rich Text Format.

#### Quote all testing as noted in external doc

### Deployment

#### Heroku

#### Variables

### Credits

#### Content

#### Media

The media (pictures) contained in this app has been borrowed from [Fragrantica](https://www.fragrantica.com/) without any comercial intention.

#### Code

Code was entirely written by the author for the present app, albeit on ocassions inspired by freely available tutorials, instructional documentation and open source examples.
On such instances, the sources have been mentioned in the code where it corresponds.
Notable sources of information, inspiration and source to sort problems are:

- [Stack Overflow](https://stackoverflow.com/)
- [W3Schools](https://www.w3schools.com/)

#### Acknowledgements

I would like to specially thank the help of:

- [Roko Buljan](https://github.com/rokobuljan), for his help and input.
- [Simen Daehlin](https://github.com/Eventyret), my mentor for this project.

## Disclaimer

This app and its deployment are for instructional purposes only, not intended comercially in any way and its eventual copyright infringments involuntary.
