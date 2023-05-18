from cmath import log
from genericpath import isfile
import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import logging

from .models import Follow, User, Post


def index(request):
    paginator = Paginator(Post.objects.all().order_by('-datetime'), 10)
    logging.info(f'COUNT: {paginator.count}')
    logging.info(f'NUMBER OF PAGES: {paginator.num_pages}')

    return render(request, "network/index.html", {
        "posts": paginator.page(1).object_list,
        "has_previous": False,
        "current_page": 1,
        "has_next": True,
        "page_range": paginator.page_range
    })


# Paginator for posts, enables loading of 10 posts on each page
def load_page(request, page_number):
    paginator = Paginator(Post.objects.all().order_by('-datetime'), 10)

    # Prevent loading of the page that doesn't exist, redirect to index if it happens
    if (page_number <= paginator.num_pages and page_number > 0):
        page = paginator.page(page_number)

        return render(request, "network/index.html", {
            "posts": page.object_list,
            "has_previous": page.has_previous,
            "current_page": page_number,
            "has_next": page.has_next,
            "page_range": paginator.page_range
        })
    
    else:
        return HttpResponseRedirect(reverse('index'))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def post(request):
    if request.method == "POST":
        user = User.objects.get(pk=int(request.POST["user_id"]))
        content = request.POST["content"]

    logging.info(f'USER: {user}')
    logging.info(f'CONTENT: {content}')

    try:
        post = Post.objects.create(content=content, poster=user)
        post.save()
    except IntegrityError:
        return render(request, 'network/index.html', {
            'message': 'Post already exists'
        })
    
    return HttpResponseRedirect(reverse('index'))


@csrf_exempt
@login_required
def like(request):
    # Update likes count
    if request.method == "PUT":
        data = json.loads(request.body)

        if data.get("post_id") is not None:
            post_id = int(data["post_id"])

        # Query for requested post
        try:
            user = request.user
            post = Post.objects.get(pk=post_id)

            logging.info(f'POST ID: {post_id}')
            logging.info(f'USER: {user}')
            logging.info(f'POST: {post}')
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        if (request.user == post.poster):
            return JsonResponse({"error": "Post authors can't like their own post."}, status=403)
        else:
            # Check if the user has already liked the post
            likers = post.likers.filter(pk=user.id)

            # If not liked, add their like to post
            if not likers:
                post.likers.add(user)
            # Else remove their like
            else:
                post.likers.remove(user)
            
            return JsonResponse({"likes": post.likers.count()})
    
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


@csrf_exempt
@login_required
def edit(request, post_id):
    # Edit post content
    if request.method == "PUT":
        # Find an associated post
        try:
            post = Post.objects.get(pk=post_id)
            logging.info(f'POST: {post}')
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        # Secure this route to prevent other users apart from the author to edit post content
        if (request.user != post.poster):
            return JsonResponse({"error": "Only post authors can edit post content."}, status=403)
        else:
            data = json.loads(request.body)

            if data.get("content") is not None:
                logging.info(f'CONTENT: {data["content"]}')
                post.content = data["content"]
                post.save()
                return HttpResponse(status=204)
    
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)
            

# Used to render users profile pages
def profile(request, user_id):
    user = User.objects.get(pk=int(user_id))

    if user is not None:
        # Find out number of users who are following given user
        followers_count = Follow.objects.filter(following=user).count()
        # Find out number of users this given user is following
        followings_count = Follow.objects.filter(follower=user).count()
        # All user's posts, in reverse chronological order
        posts_reversed = Post.objects.filter(poster=user).order_by('-datetime')
        # Check if the logged in user follows post author
        isFollower = Follow.objects.filter(following=user, follower=request.user).exists() if request.user.is_authenticated else False

        logging.info(f"USER: {user}")
        logging.info(f"FOLLOWERS COUNT: {followers_count}")
        logging.info(f"FOLLOWINGS COUNT: {followings_count}")
        logging.info(f"POSTS: {posts_reversed}")
        logging.info(f"FOLLOWING? {isFollower}")

        return render(request, "network/profile.html", {
            "author": user,
            "followers": followers_count,
            "followings": followings_count,
            "posts": posts_reversed,
            "isFollower": isFollower
        })

    else:
        return render(request, "network/profile.html", {
            "message": "Invalid user ID"
        })


@csrf_exempt
@login_required
# Used to let one user follow another
def follow(request):
    if request.method == "POST":
        data = json.loads(request.body)

        if data.get("user_id") is not None:
            user_id = int(data["user_id"])
            user = User.objects.get(pk=int(user_id))

            if user is not None:
                # Prevent users from following themselves
                if (request.user == user):
                    return JsonResponse({"error": "Users can't follow themselves."}, status=403)
                else:
                    follow = Follow.objects.filter(following=user, follower=request.user)

                    logging.info(f"FOLLOWER: {request.user}")
                    logging.info(f"FOLLOWING: {user}")
                    logging.info(f"FOLLOW: {follow}")

                    if not follow.exists():
                        follow = Follow.objects.create(follower=request.user, following=user)
                        follow.save()

                        return JsonResponse({"followers": Follow.objects.filter(following=user).count()})
            else:
                return render(request, "network/profile.html", {
                    "message": "User doesn't exist"
                })
    else:
        return JsonResponse({"error": "POST request required."}, status=400)


@csrf_exempt
@login_required
# Used to let one user follow another
def unfollow(request):
    if request.method == "DELETE":
        data = json.loads(request.body)

        if data.get("user_id") is not None:
            user_id = int(data["user_id"])
            user = User.objects.get(pk=int(user_id))

            if user is not None:
                # Prevent users from unfollowing themselves
                if (request.user == user):
                    return JsonResponse({"error": "Users can't unfollow themselves."}, status=403)
                else:
                    follow = Follow.objects.filter(following=user, follower=request.user)

                    logging.info(f"FOLLOWER: {request.user}")
                    logging.info(f"FOLLOWING: {user}")
                    logging.info(f"FOLLOW: {follow}")

                    if follow.exists():
                        follow = Follow.objects.get(follower=request.user, following=user)
                        follow.delete()

                        return JsonResponse({"followers": Follow.objects.filter(following=user).count()})
            else:
                return render(request, "network/profile.html", {
                    "message": "User doesn't exist"
                })
    else:
        return JsonResponse({"error": "POST request required."}, status=400)


@login_required
# Let's user see all posts made by users they follow
def following(request, page_number):
    # Find the users that this given user has followed. Generate the list containing followed users
    followings = [follow.following for follow in Follow.objects.filter(follower=request.user)]
    # Filter out posts to leave out only ones made by followed users
    posts = Post.objects.filter(poster__in=followings)
    # Limit to only 10 posts per page
    paginator = Paginator(posts, 10)

    logging.info(f"FOLLOWINGS: {followings}")
    logging.info(f"FOLLOWINGS: {posts}")
    logging.info(f'COUNT: {paginator.count}')
    logging.info(f'NUMBER OF PAGES: {paginator.num_pages}')

    if (page_number <= paginator.num_pages and page_number > 0):
        page = paginator.page(page_number)

        return render(request, "network/following.html", {
            "posts": page.object_list,
            "has_previous": page.has_previous,
            "current_page": page_number,
            "has_next": page.has_next,
            "page_range": paginator.page_range
        })

    else:
        return HttpResponseRedirect(reverse("following", args=(1,)))
