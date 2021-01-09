import sys
import random
from collections import defaultdict
from typing import List
from optimized_course import OptimizedCourse
import pickle


def main(db_name: str, collection_name: str, courses_code_list: List[str]):
    configure_logging('logging', 'optimization')
    client = DataAccessService(db_name, collection_name)
    courses_list = client.get_courses_by_code_list(courses_code_list)
    optimized_courses_list = make_optimized_courses(courses_list)
    print_courses_list(optimized_courses_list)
    with open('courses_data.pickle', 'wb') as binary_file:
        pickle.dump(optimized_courses_list, binary_file, protocol=pickle.HIGHEST_PROTOCOL)


def print_courses_list(optimized_courses_list):
    i = 1
    for course in optimized_courses_list:
        for time in course.times:
            print(f'{i}. קורס {course.id}, דירוג: {course.rank},' +
                  f' יום: {day_number_to_char(time.day)}, שעות: {time.start_str}-{time.end_str}')
            i += 1


def day_number_to_char(n: int) -> str:
    if not 1 <= n <= 6:
        return 'Not a valid day'
    return DAYS[n - 1]


def make_optimized_courses(courses_list: List[Course]) -> List[OptimizedCourse]:
    course_codes = set([course.code for course in courses_list])
    course_teachers = set([course.teacher_name for course in courses_list])
    random.seed(3)
    rankings = defaultdict(lambda: 0)
    for k in course_codes | course_teachers:
        rankings[k] += random.randint(0, 4)
    optimized_courses_list = []
    for course in courses_list:
        times_list = []
        for time in course.class_times:
            times_list.append(LessonTime(time.day.num_of_day, time.start_time, time.end_time))
        opt_course = OptimizedCourse(code=course.code, group=course.group_code, teacher=course.teacher_name,
                                     times=times_list)
        opt_course.rank = rankings[opt_course.code] + rankings[opt_course.teacher]
        optimized_courses_list.append(opt_course)
    optimized_courses_list.sort(key=lambda course: course.code)
    return optimized_courses_list


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    DAYS = 'א ב ג ד ה ו'.split()
    if len(sys.argv) < 4:
        with open(sys.argv[1], 'rb') as binary_file:
            courses_list = pickle.load(binary_file)
        # print_courses_list(courses_list)
        courses_by_days = cut_by_day(courses_list)
        overlaps_day1 = find_overlap(courses_by_days[0])
        for lap in overlaps_day1:
            first = lap[0]
            second = lap[1]
            print("{0} - {1}   xxx   {2} - {3}".format(first.times[0].start, first.times[0].end, second.times[0].start,
                                                     second.times[0].end))
            if first.id == second.id:
                print("X")
            else:
                print("{0} ----- {1}".format(first.id, second.id))
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3].split(','))
