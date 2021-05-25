from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .decorators import unauthenticated_user, authenticated_user
from .filters import *
from .forms import CreateAccountForm, CreateDjangoUserForm
from .models import *


def search(request):
    if request.method == 'GET':
        if request.is_ajax():
            courses_dict = get_details(request.GET.get('code', ''))
            return JsonResponse(courses_dict, safe=False)
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


def get_details(code):
    chosen_course = Course.objects.filter(code=code)
    json_chosen_course = serializers.serialize("json", chosen_course)
    lessons = Lesson.objects.filter(course__pk=code)
    lessons_pk = list(map(lambda lesson: lesson.pk, lessons))
    teacher_list = Teacher.objects.filter(lessons__pk__in=lessons_pk).distinct()
    json_teacher_details = serializers.serialize("json", teacher_list)
    types = LessonType.objects.filter(lessons__pk__in=lessons_pk).distinct()
    exams = Exam.objects.filter(courses__pk=code)
    json_exams_details = serializers.serialize("json", exams)
    json_types_details = serializers.serialize("json", types)
    lesson_times_list = LessonTime.objects.filter(lessons__pk__in=lessons_pk).distinct()
    json_times_details = serializers.serialize("json", lesson_times_list)
    course_details = {'chosen_course': json_chosen_course, 'exams': json_exams_details, 'lesson_times': json_times_details,
                      'lesson_types': json_types_details, 'staff': json_teacher_details}
    return course_details


def home(request):
    context = show_best_teacher_courses()
    if request.method == 'GET':
        if request.is_ajax() and request.user.is_authenticated:
            all_likes = Like.objects.filter(user=Account.objects.get(user=request.user))
            json_likes_list = serializers.serialize("json", all_likes)
            return JsonResponse({'json_likes_list': json_likes_list}, safe=False)
        return render(request, 'plan_ilan/home.html', context)
    elif request.method == 'POST':
        if request.POST.get('PostID', ''):
            if request.POST.get('type', '') == 'course':
                course_post = CourseReview.objects.get(id=request.POST.get('PostID', ''))
                if request.POST.get('to_add', '') == '1':
                    course_post.like_review(Account.objects.get(user=request.user))
                else:
                    course_post.remove_like(Account.objects.get(user=request.user))
                course_post.save()
            else:
                teacher_post = TeacherReview.objects.get(id=request.POST.get('PostID', ''))
                teacher_post.like_review(request.user)
                teacher_post.save()
        elif request.POST.get('Rating_object_ID', ''):
            save_comment_and_rating(request)
        return render(request, 'plan_ilan/home.html', context)
    return render(request, 'plan_ilan/home.html')


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
    return {'teachers': teachers_obj, 'courses': courses_obj,
            'teacher_comments': teacher_comments, 'course_comments': course_comments}


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
        review_object = CourseReview.objects.create(teacher=teacher_rated, author=user, headline=headline,
                                                    text=comment_body)
    rating_obj.save()
    review_object.save()


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


@authenticated_user
def time_table(request):
    if request.method == 'GET':
        lessons_list = Lesson.objects.all()
        lesson_filter = CourseInstanceFilter(request.GET, queryset=lessons_list)
        lessons_list = lesson_filter.qs
        context = {'lesson_filter': lesson_filter}
        if request.is_ajax():
            lessons_pk = list(map(lambda lesson: lesson.pk, lessons_list))
            course_list = Course.objects.filter(lessons__pk__in=lessons_pk).distinct()
            teacher_list = Teacher.objects.filter(lessons__pk__in=lessons_pk).distinct()
            session_list = LessonTime.objects.filter(lessons__pk__in=lessons_pk)
            json_session_list = serializers.serialize("json", session_list)
            json_teacher_list = serializers.serialize("json", teacher_list)
            json_course_list = serializers.serialize("json", course_list)
            json_lesson_list = serializers.serialize("json", lessons_list)
            context = {'json_lesson_list': json_lesson_list,
                       'json_course_list': json_course_list,
                       'json_teacher_list': json_teacher_list,
                       'json_session_list': json_session_list}
            return JsonResponse(context, safe=False)
        return render(request, 'timetable_generator/timetable.html', context)
    return render(request, 'timetable_generator/timetable.html')
