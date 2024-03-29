import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, redirect

from plan_ilan.apps.web_site.decorators import unauthenticated_user, authenticated_user
from plan_ilan.apps.web_site.filters import CourseInstanceFilter, TeacherInstanceFilter
from plan_ilan.apps.web_site.forms import CreateAccountForm, CreateDjangoUserForm
from plan_ilan.apps.web_site.models import *
from plan_ilan.apps.web_site.serializers import CourseSearchSerializer, TeacherSearchSerializer


def about_page(request):
    return render(request, 'plan_ilan/about.html')


def search(request):
    if request.method == 'GET':
        if request.is_ajax():
            if request.GET.get('type', '') == 'c':
                chosen_dict = get_course_details(request.GET.get('code', ''))
            else:
                chosen_dict = get_teacher_details(request.GET.get('code', ''))
            return JsonResponse(chosen_dict, safe=False)
        # COURSE SEARCH ENGINE
        lessons = Lesson.objects.all()
        lesson_filter = CourseInstanceFilter(request.GET, queryset=lessons)
        lessons = lesson_filter.qs
        lessons_pk = list(map(lambda lesson: lesson.pk, lessons))
        courses = Course.objects.filter(lessons__pk__in=lessons_pk).distinct()
        # TEACHER SEARCH ENGINE
        teachers = Teacher.objects.all()
        teacher_filter = TeacherInstanceFilter(request.GET, queryset=teachers)
        teachers = teacher_filter.qs
        departments = Department.objects.all()
        context = {'lesson_filter': lesson_filter, 'lessons': lessons, 'courses': courses,
                   'teacher_filter': teacher_filter, 'teachers': teachers, 'departments': departments}
        return render(request, 'plan_ilan/search.html', context)
    return render(request, 'plan_ilan/search.html')


def get_teacher_details(code):
    chosen_teacher = Teacher.objects.filter(id=code).first()
    teacher_details = TeacherSearchSerializer(chosen_teacher)
    return teacher_details.data


def get_course_details(code):
    chosen_course = Course.objects.filter(code=code).first()
    course_details = CourseSearchSerializer(chosen_course)
    return course_details.data


def home(request):
    if request.method == 'GET':

        context = show_best_teacher_courses()
        return render(request, 'plan_ilan/home.html', context)
    elif request.method == 'POST':
        if request.POST.get('load_likes', '') and request.user.is_authenticated:
            all_likes = Like.objects.filter(user=Account.objects.get(user=request.user))
            json_likes_list = serializers.serialize("json", all_likes)
            return JsonResponse({'json_likes_list': json_likes_list}, safe=False)
        elif request.POST.get('action', '') == 'edit':
            update_review_and_rating(request)
        elif request.POST.get('PostID', ''):
            return JsonResponse(add_or_remove_like(request), safe=False)
        elif request.POST.get('Rating_object_ID', ''):
            save_comment_and_rating(request)
        context = show_best_teacher_courses()
        return render(request, 'plan_ilan/home.html', context)
    return render(request, 'plan_ilan/home.html')


def update_review_and_rating(request):
    user = Account.objects.get(user=request.user)
    value = int(request.POST.get('rate_number', '0'))
    headline = request.POST.get('headline', '')
    comment_body = request.POST.get('comment_body', '')
    review_object = Review.objects.filter(id=request.POST.get('Rating_object_ID', ''))
    if not review_object.exists():
        pass
    review_object = review_object.first()
    review_object.edit(headline, comment_body, save=True)
    ref_instance = review_object.teacher if isinstance(review_object, TeacherReview) else review_object.course
    rating_obj = Rating.create(user=user, value=value, ref_instance=ref_instance)


def add_or_remove_like(request):
    if request.POST.get('type', '') == 'course':
        post_obj = CourseReview.objects.get(id=request.POST.get('PostID', ''))
    else:
        post_obj = TeacherReview.objects.get(id=request.POST.get('PostID', ''))
    if request.POST.get('to_add', '') == '1':
        post_obj.like_review(Account.objects.get(user=request.user))
    else:
        post_obj.remove_like(Account.objects.get(user=request.user))
    post_obj.save()
    return {'amount_likes': post_obj.amount_of_likes}


def show_best_teacher_courses():
    # TEACHER BEST RATINGS VIEW
    teacher_best_rating = TeacherRating.objects.all().order_by('-value')[:5]
    teachers_id = [t.teacher_id for t in teacher_best_rating]
    teachers_obj = Teacher.objects.filter(pk__in=teachers_id)
    # COURSES BEST RATING VIEW
    courses_best_rating = CourseRating.objects.all().order_by('-value')[:5]
    courses_id = [c.course_id for c in courses_best_rating]
    courses_obj = Course.objects.filter(pk__in=courses_id)
    # LATEST COMMENTS
    teacher_comments = TeacherReview.objects.all().order_by('date_modified')[:5]
    course_comments = CourseReview.objects.all().order_by('date_modified')[:5]
    teacher_rating = TeacherRating.objects.filter(teacher__pk__in=teachers_id)
    course_rating = CourseRating.objects.filter(course__pk__in=courses_id)
    return {'teachers': teachers_obj, 'courses': courses_obj,
            'teacher_comments': teacher_comments, 'course_comments': course_comments, 'teacher_rating': teacher_rating,
            'course_rating': course_rating}


def save_comment_and_rating(request):
    user = Account.objects.get(user=request.user)
    value = int(request.POST.get('rate_number', ''))
    headline = request.POST.get('headline', '')
    comment_body = request.POST.get('comment_body', '')
    if request.POST.get('type', '') == 'course':
        course_rated = Course.objects.get(code=request.POST.get('Rating_object_ID', ''))
        rating_obj = CourseRating.create(user, value, course_rated)
        review_object = CourseReview.objects.create(course=course_rated, author=user, headline=headline,
                                                    text=comment_body)
    else:
        teacher_rated = Teacher.objects.get(id=request.POST.get('Rating_object_ID', ''))
        rating_obj = TeacherRating.create(user, value, teacher_rated)
        review_object = TeacherReview.objects.create(teacher=teacher_rated, author=user, headline=headline,
                                                     text=comment_body)
    rating_obj.save()
    review_object.save()


def delete_comment(request):
    query_rev = Review.objects.filter(id=request.POST.get('id', ''))
    if query_rev.exists():
        rev = query_rev.get()
        if isinstance(rev, CourseReview):
            query_rate = CourseRating.objects.filter(course=rev)
        else:
            query_rate = TeacherRating.objects.filter(teacher=rev)
        if query_rate.exists():
            rate = query_rate.get()
            rate.delete()
        rev.delete()


@unauthenticated_user
def register(request):
    if request.method == 'POST':
        django_user_form = CreateDjangoUserForm(request.POST)
        account_form = CreateAccountForm(request.POST)
        if django_user_form.is_valid() and account_form.is_valid():
            user = django_user_form.save()
            account = account_form.save(commit=False)
            account.user = user
            account.save()
            # messages.success(request, 'ההרשמה נקלטה בהצלחה')
            login(request, user)
            return redirect('home')
        else:
            context = {'form': django_user_form, 'account_form': account_form}
            return render(request, 'plan_ilan/register.html', context)
    django_user_form = CreateDjangoUserForm()
    account_form = CreateAccountForm()
    context = {'form': django_user_form, 'account_form': account_form}
    return render(request, 'plan_ilan/register.html', context)


@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_ = authenticate(request, username=username, password=password)
        if user_ is not None:
            login(request, user_)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')
    return render(request, 'plan_ilan/login.html')


def logout_user(request):
    logout(request)
    return redirect('home')
